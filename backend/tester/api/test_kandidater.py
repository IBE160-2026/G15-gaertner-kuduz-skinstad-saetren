"""GET /api/vakter/{vaktnummer}/kandidater (story 2.1–2.4).

Fasiten kommer fra `testdata.FASIT` (AV-07). Med alle fire harde regler på plass
er de gyldige alle som fasiten ikke utelukker: 4 for #4127 og 0 for #4189. En tom
liste gir `status: "ingen_gyldige_kandidater"` (story 2.6, FR6); `ok` har alltid minst én Kandidat.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.kandidatgrunnlag import hent_kandidatgrunnlag


def test_kostnadsfasit_og_identisk_godkjenningsgrunnlag(klient):
    svar = hent(klient, 4127)
    forventet = {"Jonas Bakke": 2960, "Mette Solberg": 2960, "Thomas Nygård": 2800, "Ingrid Dahl": 3850}
    assert {k["navn"]: k["kostnad"]["total"] for k in svar["kandidater"]} == forventet
    ingrid = next(k for k in svar["kandidater"] if k["navn"] == "Ingrid Dahl")
    assert ingrid["kostnad"] == {"total": 3850, "ordinære_timer": 4, "overtidstimer": 4,
                                 "ordinær_sats": 385, "overtidssats": 577.5}
    for kandidat in svar["kandidater"]:
        respons = klient.get(f"/api/vakter/4127/kandidater/{kandidat['id']}")
        assert respons.status_code == 200
        assert respons.json()["kandidat"]["kostnad"] == kandidat["kostnad"]


def test_ugyldig_lønn_stopper_begge_kandidatsvar(klient, monkeypatch):
    from dataclasses import replace
    import adaptere.api.main as api

    opprinnelig = api.hent_kandidatgrunnlag

    def ugyldig(*args):
        grunnlag = opprinnelig(*args)
        ansatte = list(grunnlag.ansatte)
        indeks = next(i for i, ansatt in enumerate(ansatte) if ansatt.id == 6)
        ansatte[indeks] = replace(ansatte[indeks], timelønn=None)
        return replace(grunnlag, ansatte=tuple(ansatte))

    monkeypatch.setattr(api, "hent_kandidatgrunnlag", ugyldig)
    assert_datafeil(hent(klient, 4127))
    respons = klient.get("/api/vakter/4127/kandidater/6")
    assert respons.status_code == 200
    assert_datafeil(respons.json())
from adaptere.lagring.modeller import OSLO, AnsattRad, BrukerRad, TurnusRad, VaktRad
from adaptere.lagring.testdata import ANSATTE, FASIT, MANGLER_BEMANNING, PERIODE_SLUTT, PERIODE_START
from domene.regelmotor.rangering import ranger
from domene.regelmotor.vurdering import norsk_sorteringsnøkkel, vurder_kandidater
from domene.typer import Kandidat, Kandidatvurdering
from tester.api.test_innlogging import engine, feilsvar, klient, logg_inn  # noqa: F401

NAVN = {ansatt_id: navn for ansatt_id, navn, *_ in ANSATTE}
ID_VED_NAVN = {navn: ansatt_id for ansatt_id, navn in NAVN.items()}
# To ansatte med samme navn ville la ID_VED_NAVN peke på feil id (den sist vunnet).
assert len(ID_VED_NAVN) == len(NAVN)
KOMPETANSE = {navn: kompetanse for _, navn, _, _, _, kompetanse, _ in ANSATTE}

# FASIT bruker korte utfallsnavn; API-et svarer med regelmotorens fulle årsaksstrenger.
UTFALL_TIL_ÅRSAK = {
    "kompetanse": "kompetanse-minstekrav",
    "kolliderende": "kolliderende vakt",
    "elleve-timer": "11-timersregelen",
    "trettifem-timer": "35-timersregelen",
}
REKKEFØLGE_PER_REGEL = ["kompetanse-minstekrav", "kolliderende vakt", "11-timersregelen", "35-timersregelen"]
# `KandidatUt` (uendret, også i godkjenningsgrunnlaget) og det Rangeringen legger til (story 4.4).
KANDIDAT_FELT = {"id", "navn", "kompetansenivå", "minutter_i_uka", "timebelastning_prosent",
                 "hoy_belastning", "ulempebelastning", "kostnad"}
RANGERT_FELT = KANDIDAT_FELT | {"stilling", "ansiennitet", "plass", "totalscore", "faktorpoeng",
                                "preferansepoeng", "tolkestatus", "preferansekategori"}


def hent(klient: TestClient, nummer: int) -> dict:
    logg_inn(klient)
    respons = klient.get(f"/api/vakter/{nummer}/kandidater")
    assert respons.status_code == 200
    return respons.json()


IMPLEMENTERTE_REGLER = {"kompetanse", "kolliderende", "elleve-timer", "trettifem-timer"}


def forventet_gyldige(nummer: int) -> set[str]:
    return {navn for navn, utfall in FASIT[nummer]["utfall"].items() if utfall not in IMPLEMENTERTE_REGLER}


def forventet_utelukket(nummer: int) -> set[str]:
    return {navn for navn, utfall in FASIT[nummer]["utfall"].items() if utfall in IMPLEMENTERTE_REGLER}


def forventet_per_regel(nummer: int) -> list[dict[str, object]]:
    tellinger = dict.fromkeys(REKKEFØLGE_PER_REGEL, 0)
    for utfall in FASIT[nummer]["utfall"].values():
        if utfall in UTFALL_TIL_ÅRSAK:
            tellinger[UTFALL_TIL_ÅRSAK[utfall]] += 1
    return [{"årsak": årsak, "antall": tellinger[årsak]} for årsak in REKKEFØLGE_PER_REGEL]


def forventet_utelukkelser(nummer: int) -> dict[str, object]:
    utfall = FASIT[nummer]["utfall"]
    # Samme norske sortering som regelmotoren faktisk bruker (`vurder_kandidater`),
    # ikke Pythons vanlige strengsortering, slik at forventningen ikke kan skli
    # fra produksjonslogikken selv om de i dag gir samme rekkefølge for fasitnavnene.
    kandidater = [Kandidat(id=ID_VED_NAVN[navn], navn=navn, kompetanse={}, timelønn=300) for navn in forventet_utelukket(nummer)]
    navn_sortert = [k.navn for k in sorted(kandidater, key=norsk_sorteringsnøkkel)]
    return {
        "totalt": len(navn_sortert),
        "per_regel": forventet_per_regel(nummer),
        "utelukkede": [
            {"id": ID_VED_NAVN[navn], "navn": navn, "årsaker": [UTFALL_TIL_ÅRSAK[utfall[navn]]]}
            for navn in navn_sortert
        ],
    }


@pytest.mark.parametrize("nummer,antall", [(4127, 4), (4189, 0)])
def test_gyldige_stemmer_med_fasiten(klient: TestClient, nummer: int, antall: int) -> None:
    svar = hent(klient, nummer)

    assert set(svar) == {"status", "kandidater", "utelukkelser"}
    assert svar["status"] == ("ok" if antall else "ingen_gyldige_kandidater")
    navn = [k["navn"] for k in svar["kandidater"]]
    assert len(navn) == len(set(navn)) == antall
    assert set(navn) == forventet_gyldige(nummer)


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_bare_gyldige_sendes_nfr2(klient: TestClient, nummer: int) -> None:
    svar = hent(klient, nummer)
    utelukket = forventet_utelukket(nummer)
    satt_opp = NAVN[MANGLER_BEMANNING[nummer][0]]

    # 4127: 8 kompetanse + 7 kollisjon + 4 på 11 t + 1 på 35 t. 4189: 3 + 2 + 18 + 1.
    assert len(utelukket) == {4127: 20, 4189: 24}[nummer]

    kandidatnavn = {k["navn"] for k in svar["kandidater"]}
    utelukkede_svar = {u["navn"]: tuple(u["årsaker"]) for u in svar["utelukkelser"]["utelukkede"]}
    # To utelukkede med samme navn ville la ordboka skjule den ene stille.
    assert len(utelukkede_svar) == len(svar["utelukkelser"]["utelukkede"])

    for navn in utelukket:
        assert navn not in kandidatnavn
        forventet_årsak = UTFALL_TIL_ÅRSAK[FASIT[nummer]["utfall"][navn]]
        assert utelukkede_svar[navn] == (forventet_årsak,)

    assert satt_opp not in kandidatnavn
    assert satt_opp not in utelukkede_svar


def test_av12_fasit_fra_seed_vises_uavrundet(klient: TestClient) -> None:
    # Testdataenes uavhengige kontroll i test_testdata.py gir 40 og 180 poeng.
    svar = hent(klient, 4127)
    kandidater = {k["navn"]: k["ulempebelastning"] for k in svar["kandidater"]}
    jonas, mette = kandidater["Jonas Bakke"], kandidater["Mette Solberg"]
    assert jonas["poeng"] == 40
    assert mette["poeng"] == 180
    assert jonas["score"] == pytest.approx(86 + 2 / 3)
    assert mette["score"] == 40
    assert 0.15 * (jonas["score"] - mette["score"]) == pytest.approx(7)
    assert hent(klient, 4127)["kandidater"] == svar["kandidater"]


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_vakter_lekker_ikke_i_svaret(klient: TestClient, nummer: int) -> None:
    svar = hent(klient, nummer)

    for k in svar["kandidater"]:
        assert set(k) == RANGERT_FELT
    tekst = str(svar)
    for ord_ in ("vakter", "start", "slutt", "tildelt", "kolliderer", "2026-09"):
        assert ord_ not in tekst


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_ingen_med_kolliderende_vakt_i_fasiten_er_med(klient: TestClient, nummer: int) -> None:
    navn = {k["navn"] for k in hent(klient, nummer)["kandidater"]}
    kolliderende = {n for n, utfall in FASIT[nummer]["utfall"].items() if utfall == "kolliderende"}

    assert len(kolliderende) == {4127: 7, 4189: 2}[nummer]
    assert not navn & kolliderende


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_ingen_med_brudd_på_11_timersregelen_i_fasiten_er_med(klient: TestClient, nummer: int) -> None:
    navn = {k["navn"] for k in hent(klient, nummer)["kandidater"]}
    elleve = {n for n, utfall in FASIT[nummer]["utfall"].items() if utfall == "elleve-timer"}

    assert len(elleve) == {4127: 4, 4189: 18}[nummer]
    assert not navn & elleve


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_ingen_med_brudd_på_35_timersregelen_i_fasiten_er_med(klient: TestClient, nummer: int) -> None:
    navn = {k["navn"] for k in hent(klient, nummer)["kandidater"]}
    trettifem = {n for n, utfall in FASIT[nummer]["utfall"].items() if utfall == "trettifem-timer"}

    assert trettifem == {4127: {"Anders Strand"}, 4189: {"Line Moe"}}[nummer]
    assert not navn & trettifem


def test_4189_gir_ingen_gyldige_kandidater(klient: TestClient) -> None:
    # Alle 24 er utelukket (3/2/18/1). Fasiten er uendret (AV-07).
    svar = hent(klient, 4189)
    assert svar == {
        "status": "ingen_gyldige_kandidater",
        "kandidater": [],
        "utelukkelser": forventet_utelukkelser(4189),
    }
    assert svar["utelukkelser"]["totalt"] == 24


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_status_og_liste_følger_invariantene(klient: TestClient, nummer: int) -> None:
    svar = hent(klient, nummer)
    if svar["status"] == "ok":
        assert svar["kandidater"] != []
    else:
        assert svar["status"] == "ingen_gyldige_kandidater"
        assert svar["kandidater"] == []


def test_datafeil_blir_aldri_ingen_gyldige(klient: TestClient, engine: Engine) -> None:
    start = datetime(2026, 10, 4, 5, 1, tzinfo=OSLO)
    endre_vakt(engine, start=start, slutt=start + timedelta(hours=8))
    svar = hent(klient, 4127)
    assert svar["status"] == "datafeil"
    assert "kandidater" not in svar
    assert "utelukkelser" not in svar


@pytest.mark.parametrize("nummer,forventet", [(4127, [8, 7, 4, 1]), (4189, [3, 2, 18, 1])])
def test_per_regel_stemmer_med_fasiten(klient: TestClient, nummer: int, forventet: list[int]) -> None:
    svar = hent(klient, nummer)

    assert svar["utelukkelser"]["per_regel"] == [
        {"årsak": årsak, "antall": antall} for årsak, antall in zip(REKKEFØLGE_PER_REGEL, forventet)
    ]
    # Samme tall følger av selve fasiten (AV-07), ikke bare hardkodet to steder.
    assert svar["utelukkelser"]["per_regel"] == forventet_per_regel(nummer)
    assert svar["utelukkelser"]["totalt"] == len(forventet_utelukket(nummer))


def test_silje_er_ikke_med_på_4127_og_utelukket_på_4189(klient: TestClient) -> None:
    navn_4127 = {k["navn"] for k in hent(klient, 4127)["kandidater"]}
    navn_4189 = {k["navn"] for k in hent(klient, 4189)["kandidater"]}

    assert "Silje Amundsen" not in navn_4127  # satt opp
    assert "Silje Amundsen" not in navn_4189  # mangler nivå for natt
    assert FASIT[4189]["utfall"]["Silje Amundsen"] == "kompetanse"
    assert "Eirik Moen" not in navn_4127 | navn_4189


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_rangert_med_kompetansenivå_for_vakttypen(klient: TestClient, nummer: int) -> None:
    kandidater = hent(klient, nummer)["kandidater"]
    nøkkel = {4127: "dag", 4189: "natt"}[nummer]

    for k in kandidater:
        assert set(k) == RANGERT_FELT
        assert NAVN[k["id"]] == k["navn"]
        assert k["kompetansenivå"] == KOMPETANSE[k["navn"]][nøkkel]
        assert k["kompetansenivå"] >= 3
    # Story 4.4: sortert etter plass i Rangeringen, ikke alfabetisk som i 2.1.
    assert [k["navn"] for k in kandidater] == {
        4127: ["Jonas Bakke", "Mette Solberg", "Thomas Nygård", "Ingrid Dahl"], 4189: [],
    }[nummer]
    assert [k["plass"] for k in kandidater] == list(range(1, len(kandidater) + 1))


# --- Rangering (story 4.4) -------------------------------------------------------

# Regnet for hånd fra PRD §4.4 (KS-02), med 50 preferansepoeng for alle fordi ingen
# tolkning er lagret før epic 5 (P-05). Kostnad 2960/2960/2800/3850 gir min–maks
# over 1050 kr: Jonas og Mette 100 × 890/1050 = 1780/21, Thomas 100, Ingrid 0.
# Timer 16/16/24/32 gir 100/100/50/0. Ulempe 40/180/120/60 p gir 260/3, 40, 60, 80.
#   Jonas  = 2/5 × 1780/21 + 1/5 × 100 + 3/20 × 260/3 + 1/4 × 50 = 3335/42 ≈ 79,40
#   Mette  = 2/5 × 1780/21 + 1/5 × 100 + 3/20 × 40    + 1/4 × 50 = 3041/42 ≈ 72,40
#   Thomas = 2/5 × 100     + 1/5 × 50  + 3/20 × 60    + 1/4 × 50 = 71,5
#   Ingrid = 0             + 0         + 3/20 × 80    + 1/4 × 50 = 24,5
RANGERING_4127_UTEN_TOLKNING = [
    ("Jonas Bakke", 3335 / 42), ("Mette Solberg", 3041 / 42), ("Thomas Nygård", 71.5), ("Ingrid Dahl", 24.5),
]


def test_4127_er_rangert_med_totaler_plass_og_status(klient: TestClient) -> None:
    kandidater = hent(klient, 4127)["kandidater"]
    assert [(k["navn"], k["totalscore"]) for k in kandidater] == RANGERING_4127_UTEN_TOLKNING
    assert [round(k["totalscore"], 2) for k in kandidater] == [79.40, 72.40, 71.50, 24.50]
    assert [k["plass"] for k in kandidater] == [1, 2, 3, 4]
    # Alle fire har registrert tekst i seeden, og ingen tolkning er lagret (P-05).
    assert {k["tolkestatus"] for k in kandidater} == {"venter_paa_tolkning"}
    assert {k["preferansepoeng"] for k in kandidater} == {50}
    assert {k["preferansekategori"] for k in kandidater} == {None}
    jonas, mette, thomas, ingrid = kandidater
    assert jonas["faktorpoeng"] == {"kostnad": 1780 / 21, "timebelastning": 100, "ulempe": 260 / 3}
    assert thomas["faktorpoeng"] == {"kostnad": 100, "timebelastning": 50, "ulempe": 60}
    assert ingrid["faktorpoeng"] == {"kostnad": 0, "timebelastning": 0, "ulempe": 80}
    # AV-12: bare ulempen skiller Jonas og Mette, med nøyaktig 7,0 i forskjell.
    assert jonas["totalscore"] - mette["totalscore"] == 7.0
    # Thomas er billigst, men ikke øverst (FR9, SM-6).
    assert min(kandidater, key=lambda k: k["kostnad"]["total"])["navn"] == "Thomas Nygård"
    assert thomas["plass"] == 3
    assert (jonas["stilling"], jonas["ansiennitet"]) == ("Sykepleier", 3)


def test_rangeringen_bruker_fasiten_fra_testdataene(klient: TestClient) -> None:
    # FASIT har tolkede preferanser (75/75/0/100). Uten dem er rekkefølgen den samme.
    fasit = [r["navn"] for r in FASIT[4127]["rangering"]]
    assert [k["navn"] for k in hent(klient, 4127)["kandidater"]] == fasit


def test_svaret_stemmer_med_porten_fra_samme_database(klient: TestClient, engine: Engine) -> None:
    # `rangert_ut` regner `KandidatUt`-feltene for seg. De må stemme med `RangertKandidat`.
    svar = {k["id"]: k for k in hent(klient, 4127)["kandidater"]}
    with lag_sessionmaker(engine)() as session:
        bruker_id = session.scalars(select(BrukerRad.id)).first()
        grunnlag = hent_kandidatgrunnlag(session, bruker_id, 4127)
    assert grunnlag is not None
    vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
    assert isinstance(vurdering, Kandidatvurdering)
    rangert = ranger(vurdering, grunnlag.vakt)
    assert sorted(svar) == sorted(r.id for r in rangert)
    for r in rangert:
        k = svar[r.id]
        assert (k["plass"], k["totalscore"]) == (r.plass, r.totalscore)
        assert (k["kostnad"]["total"], k["kostnad"]["ordinære_timer"], k["kostnad"]["overtidstimer"]) == (
            r.kostnad, r.ordinære_timer, r.overtidstimer)
        assert (k["timebelastning_prosent"], k["hoy_belastning"]) == (r.timebelastning_prosent, r.høy_belastning)
        u = k["ulempebelastning"]
        assert (u["poeng"], u["kveldstimer"], u["helgetimer"], u["natttimer"]) == (
            r.ulempepoeng, r.kveldstimer, r.helgetimer, r.natttimer)
        # Med standardtaket er Ulempescoren den samme som scoren fra story 4.7.
        assert k["faktorpoeng"]["ulempe"] == pytest.approx(u["score"])


def test_kandidatfeltene_er_de_samme_som_i_godkjenningsgrunnlaget(klient: TestClient) -> None:
    # Rangeringen legger bare til felt. `KandidatUt` er uendret (story 4.4).
    for kandidat in hent(klient, 4127)["kandidater"]:
        enkelt = klient.get(f"/api/vakter/4127/kandidater/{kandidat['id']}").json()["kandidat"]
        assert set(enkelt) == KANDIDAT_FELT
        assert {felt: kandidat[felt] for felt in KANDIDAT_FELT} == enkelt


def test_samme_svar_hver_gang(klient: TestClient) -> None:
    assert hent(klient, 4127) == hent(klient, 4127)


# --- Tilgang -------------------------------------------------------------------


def test_uten_sesjon_gir_401(klient: TestClient) -> None:
    respons = klient.get("/api/vakter/4127/kandidater")
    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


@pytest.mark.parametrize("nummer", [9999, 4128, 3338, 4261, 4265])
def test_ukjent_bemannet_og_historisk_gir_404(klient: TestClient, nummer: int) -> None:
    logg_inn(klient)
    respons = klient.get(f"/api/vakter/{nummer}/kandidater")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())
    assert "kandidater" not in respons.json()


def assert_ingen_navn(tekst: str) -> None:
    for navn in NAVN.values():
        assert navn not in tekst


def test_annen_turnus_gir_404(klient: TestClient, engine: Engine) -> None:
    with lag_sessionmaker(engine).begin() as session:
        annen = TurnusRad(
            avdeling="Annen avdeling", periode_start=PERIODE_START,
            periode_slutt=PERIODE_SLUTT, sist_oppdatert=PERIODE_START,
        )
        session.add(annen)
        session.flush()
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(turnus_id=annen.id))
    logg_inn(klient)
    respons = klient.get("/api/vakter/4127/kandidater")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())
    assert_ingen_navn(respons.text)


@pytest.mark.parametrize("start,synlig", [
    (PERIODE_START, True), (PERIODE_SLUTT, False), (PERIODE_START - timedelta(minutes=1), False),
])
def test_halvapen_periode_ved_grensene(klient: TestClient, engine: Engine, start: datetime, synlig: bool) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(start=start, slutt=start + timedelta(hours=8)))
    logg_inn(klient)
    respons = klient.get("/api/vakter/4127/kandidater")
    if synlig:
        assert respons.status_code == 200
        assert respons.json()["status"] == "ok"
    else:
        assert respons.status_code == 404
        assert feilsvar("ikke_funnet")(respons.json())
        assert_ingen_navn(respons.text)


# --- Kandidatens egne vakter fra databasen ---------------------------------------


def legg_til_tildelt_vakt(engine: Engine, ansatt_id: int, start: datetime, slutt: datetime) -> None:
    """En ekstra bemannet vakt for én Ansatt, i samme turnus som #4127."""
    with lag_sessionmaker(engine).begin() as session:
        turnus_id = session.scalars(select(VaktRad.turnus_id).where(VaktRad.vaktnummer == 4127)).one()
        session.add(VaktRad(
            turnus_id=turnus_id, vaktnummer=99001, vakttype="natt", start=start, slutt=slutt,
            minstenivå=1, tildelt_ansatt_id=ansatt_id, mangler_bemanning=False,
        ))


def gyldig_på_4127() -> tuple[int, str]:
    navn = sorted(forventet_gyldige(4127))[0]
    (ansatt_id,) = [i for i, n in NAVN.items() if n == navn]
    return ansatt_id, navn


def test_egen_vakt_før_periodestart_som_overlapper_utelukker(klient: TestClient, engine: Engine) -> None:
    # Kandidatens vakter hentes uavhengig av periode. En vakt som starter før
    # periodestart og overlapper en Vakt ved periodestart, skal utelukke.
    endre_vakt(engine, start=PERIODE_START, slutt=PERIODE_START + timedelta(hours=8))
    # Den første som er gyldig på det nye tidspunktet. Fasiten for #4127 gjelder
    # ikke her: med 35-timersregelen er Ingrid ikke gyldig mandag 21.09 00–08.
    kandidat = hent(klient, 4127)["kandidater"][0]
    ansatt_id, navn = kandidat["id"], kandidat["navn"]

    legg_til_tildelt_vakt(engine, ansatt_id, PERIODE_START - timedelta(hours=2), PERIODE_START + timedelta(hours=1))
    assert navn not in {k["navn"] for k in hent(klient, 4127)["kandidater"]}


# --- Datafeil (P-08) med endret testdatabase -----------------------------------


def endre_vakt(engine: Engine, **verdier: object) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(**verdier))


def assert_datafeil(svar: dict) -> None:
    assert svar == {
        "status": "datafeil",
        "kode": "mangler_turnusgrunnlag",
        "datagrense": "2026-10-05T00:00:00+02:00",
    }


# Fra story 2.3 må vinduet `[start − 11 t, slutt + 11 t)` ligge innenfor
# datadekningen (P-08, A5). En Vakt som slutter 04.10 kl. 13:00, når akkurat
# datagrensen 05.10 kl. 00:00. Fra story 2.4 må også de berørte kalenderukene
# ligge innenfor. Uka 28.09–05.10 slutter nøyaktig på datagrensen.


def test_vindu_som_slutter_ved_datagrensen_vurderes(klient: TestClient, engine: Engine) -> None:
    start = datetime(2026, 10, 4, 5, 0, tzinfo=OSLO)
    endre_vakt(engine, start=start, slutt=start + timedelta(hours=8))
    assert hent(klient, 4127)["status"] == "ok"


def test_vindu_som_slutter_etter_datagrensen_gir_datafeil(
    klient: TestClient, engine: Engine, caplog: pytest.LogCaptureFixture,
) -> None:
    start = datetime(2026, 10, 4, 5, 1, tzinfo=OSLO)
    endre_vakt(engine, start=start, slutt=start + timedelta(hours=8))
    with caplog.at_level("WARNING", logger="adaptere.api.main"):
        assert_datafeil(hent(klient, 4127))
    # Grunnen logges for feilsøking, men sendes ikke i svaret.
    assert "Datafeil for vakt 4127" in caplog.text
    assert "datagrensen" in caplog.text


def test_uke_som_slutter_ved_datagrensen_vurderes(klient: TestClient) -> None:
    # #4189 (mandag 28.09 23–07) berører uka [28.09, 05.10), som slutter på datagrensen.
    assert hent(klient, 4189)["status"] == "ingen_gyldige_kandidater"


def test_uke_som_slutter_etter_datagrensen_gir_datafeil(
    klient: TestClient, engine: Engine, caplog: pytest.LogCaptureFixture,
) -> None:
    # Datagrensen flyttes til lørdag 03.10. #4189 har 11-timersvinduet til 29.09
    # kl. 18:00, men uka går til 05.10, så grunnlaget dekker ikke hele uka.
    grense = datetime(2026, 10, 3, 0, 0, tzinfo=OSLO)
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(TurnusRad).values(periode_slutt=grense))
    with caplog.at_level("WARNING", logger="adaptere.api.main"):
        svar = hent(klient, 4189)
    assert svar == {"status": "datafeil", "kode": "mangler_turnusgrunnlag", "datagrense": "2026-10-03T00:00:00+02:00"}
    assert "datagrensen" in caplog.text


def test_start_ikke_før_slutt_gir_datafeil(klient: TestClient, engine: Engine) -> None:
    start = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)
    endre_vakt(engine, slutt=start)
    assert_datafeil(hent(klient, 4127))


def test_tildelt_vakt_med_start_ikke_før_slutt_gir_datafeil(klient: TestClient, engine: Engine) -> None:
    # Ugyldig historikk hos en Kandidat er ikke fri tid (P-08). Vakten ligger
    # samtidig med #4127, så den er relevant for regelen uansett avgrensning.
    ansatt_id, _ = gyldig_på_4127()
    start = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)
    legg_til_tildelt_vakt(engine, ansatt_id, start, start)
    assert_datafeil(hent(klient, 4127))


@pytest.mark.parametrize("start,vakttype", [
    (datetime(2026, 10, 4, 7, 0, tzinfo=OSLO), "dag"),
    (datetime(2026, 10, 4, 15, 0, tzinfo=OSLO), "kveld"),
    (datetime(2026, 10, 4, 23, 0, tzinfo=OSLO), "natt"),
])
def test_vakter_04_10_gir_datafeil(klient: TestClient, engine: Engine, start: datetime, vakttype: str) -> None:
    # Som #4261–#4265: hvilen etter kan ikke kontrolleres, så P-08 krever datafeil.
    endre_vakt(engine, vakttype=vakttype, start=start, slutt=start + timedelta(hours=8))
    assert_datafeil(hent(klient, 4127))


def test_tildelt_vakt_med_start_ikke_før_slutt_langt_unna_ignoreres(klient: TestClient, engine: Engine) -> None:
    # Vedtak A5 (PR #14): ugyldig historikk utenfor vinduet rundt #4127 kan ikke
    # påvirke noen regel og gir ikke datafeil.
    ansatt_id, navn = gyldig_på_4127()
    uke_35 = datetime(2026, 8, 26, 7, 0, tzinfo=OSLO)
    legg_til_tildelt_vakt(engine, ansatt_id, uke_35, uke_35)
    svar = hent(klient, 4127)
    assert svar["status"] == "ok"
    assert navn in {k["navn"] for k in svar["kandidater"]}


def test_historikkstart_er_periodestart_minus_672_timer(engine: Engine) -> None:
    with lag_sessionmaker(engine)() as session:
        bruker_id = session.scalars(select(BrukerRad.id)).first()
        grunnlag = hent_kandidatgrunnlag(session, bruker_id, 4127)
    assert grunnlag is not None
    assert grunnlag.historikkstart == datetime(2026, 8, 24, 0, 0, tzinfo=OSLO)
    assert grunnlag.historikkstart == PERIODE_START.astimezone(UTC) - timedelta(hours=672)
    assert grunnlag.datagrense == PERIODE_SLUTT


def test_historikkstart_regnes_i_faktisk_tid_over_vårskiftet(engine: Engine) -> None:
    # 672 faktiske timer før 13.04 00:00 CEST krysser vårskiftet 29.03 og havner
    # 15.03 kl. 23:00 CET. På veggklokka ville det blitt 16.03 kl. 00:00.
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(TurnusRad).values(periode_start=datetime(2026, 4, 13, tzinfo=OSLO)))
    with lag_sessionmaker(engine)() as session:
        bruker_id = session.scalars(select(BrukerRad.id)).first()
        grunnlag = hent_kandidatgrunnlag(session, bruker_id, 4127)
    assert grunnlag is not None
    assert grunnlag.historikkstart == datetime(2026, 3, 15, 23, 0, tzinfo=OSLO)


@pytest.mark.parametrize("verdi", [0, 5, "3"])
def test_ugyldig_kompetanseverdi_gir_datafeil(klient: TestClient, engine: Engine, verdi: object) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == 3).values(kompetanse={"dag": verdi, "natt": 3}))
    assert_datafeil(hent(klient, 4127))


def test_minutter_i_startuka_ingrid_32_timer_og_alle_har_feltet(klient: TestClient) -> None:
    kandidater = hent(klient, 4127)["kandidater"]
    minutter = {k["navn"]: k["minutter_i_uka"] for k in kandidater}
    assert minutter["Ingrid Dahl"] == 1920  # 32 t, fasit AV-07
    assert all(isinstance(m, int) and m >= 0 for m in minutter.values())
    assert hent(klient, 4127)["kandidater"] == kandidater


def forleng_ingrids_første_vakt_i_uka(engine: Engine, minutter: int, sekunder: int = 0) -> None:
    """Gjør Ingrids 32:00 i uke 39 til 32:00 + `minutter`, uten å flytte starten."""
    uke_start, uke_slutt = datetime(2026, 9, 21, tzinfo=OSLO), datetime(2026, 9, 28, tzinfo=OSLO)
    with lag_sessionmaker(engine).begin() as session:
        rad = session.scalars(
            select(VaktRad)
            .where(VaktRad.tildelt_ansatt_id == 4, VaktRad.start >= uke_start, VaktRad.start < uke_slutt)
            .order_by(VaktRad.start)
        ).first()
        assert rad is not None
        rad.slutt = rad.slutt + timedelta(minutes=minutter, seconds=sekunder)


def test_timebelastning_ingrid_er_88_9_prosent_og_ikke_høy(klient: TestClient) -> None:
    ingrid = next(k for k in hent(klient, 4127)["kandidater"] if k["navn"] == "Ingrid Dahl")
    assert round(ingrid["timebelastning_prosent"], 1) == 88.9
    assert ingrid["hoy_belastning"] is False
    assert all(isinstance(k["hoy_belastning"], bool) for k in hent(klient, 4127)["kandidater"])
    assert hent(klient, 4127)["kandidater"] == hent(klient, 4127)["kandidater"]


@pytest.mark.parametrize("ekstra,høy", [(23, False), (24, True), (25, True)])
def test_timebelastning_grensen_32_23_og_32_24(klient: TestClient, engine: Engine, ekstra: int, høy: bool) -> None:
    forleng_ingrids_første_vakt_i_uka(engine, ekstra)
    kandidater = hent(klient, 4127)["kandidater"]
    ingrid = next(k for k in kandidater if k["navn"] == "Ingrid Dahl")
    assert ingrid["minutter_i_uka"] == 1920 + ekstra
    assert ingrid["hoy_belastning"] is høy
    assert ingrid["timebelastning_prosent"] == pytest.approx(100 * (1920 + ekstra) / 2160)


def test_timebelastning_rett_under_grensen_bevarer_sekunder(klient: TestClient, engine: Engine) -> None:
    forleng_ingrids_første_vakt_i_uka(engine, 23, 59)
    ingrid = next(k for k in hent(klient, 4127)["kandidater"] if k["navn"] == "Ingrid Dahl")
    assert ingrid["minutter_i_uka"] == 32 * 60 + 23
    assert ingrid["hoy_belastning"] is False
    assert ingrid["timebelastning_prosent"] == pytest.approx(100 * (32 * 3600 + 23 * 60 + 59) / (36 * 3600))
