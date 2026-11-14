"""GET /api/vakter/{vaktnummer}/kandidater (story 2.1–2.4).

Fasiten kommer fra `testdata.FASIT` (AV-07). Med alle fire harde regler på plass
er de gyldige alle som fasiten ikke utelukker: 4 for #4127 og 0 for #4189. En tom
liste gir `status: "ok"` til story 2.6 innfører `ingen_gyldige_kandidater`.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.kandidatgrunnlag import hent_kandidatgrunnlag
from adaptere.lagring.modeller import OSLO, AnsattRad, BrukerRad, TurnusRad, VaktRad
from adaptere.lagring.testdata import ANSATTE, FASIT, MANGLER_BEMANNING, PERIODE_SLUTT, PERIODE_START
from domene.regelmotor.vurdering import norsk_sorteringsnøkkel
from domene.typer import Kandidat
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
    kandidater = [Kandidat(id=ID_VED_NAVN[navn], navn=navn, kompetanse={}) for navn in forventet_utelukket(nummer)]
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
    assert svar["status"] == "ok"
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


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_vakter_lekker_ikke_i_svaret(klient: TestClient, nummer: int) -> None:
    svar = hent(klient, nummer)

    for k in svar["kandidater"]:
        assert set(k) == {"id", "navn", "kompetansenivå"}
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


def test_4189_gir_tom_liste_med_status_ok_til_story_2_6(klient: TestClient) -> None:
    # Alle 24 er utelukket. API-et er uendret til 2.6 (beslutning B).
    assert hent(klient, 4189) == {
        "status": "ok",
        "kandidater": [],
        "utelukkelser": forventet_utelukkelser(4189),
    }


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
def test_alfabetisk_med_kompetansenivå_for_vakttypen(klient: TestClient, nummer: int) -> None:
    kandidater = hent(klient, nummer)["kandidater"]
    nøkkel = {4127: "dag", 4189: "natt"}[nummer]

    for k in kandidater:
        assert set(k) == {"id", "navn", "kompetansenivå"}
        assert NAVN[k["id"]] == k["navn"]
        assert k["kompetansenivå"] == KOMPETANSE[k["navn"]][nøkkel]
        assert k["kompetansenivå"] >= 3
    navn = [k["navn"] for k in kandidater]
    # Seeden har ingen navn med æ, ø eller å først, så vanlig sortering er nok her.
    # Den norske rekkefølgen testes i domenet.
    assert navn == sorted(navn)
    assert navn == {4127: ["Ingrid Dahl", "Jonas Bakke", "Mette Solberg", "Thomas Nygård"], 4189: []}[nummer]


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
    assert hent(klient, 4189)["status"] == "ok"


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
