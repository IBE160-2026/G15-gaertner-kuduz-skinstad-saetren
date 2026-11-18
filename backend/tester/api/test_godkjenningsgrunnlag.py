"""GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id} (story 3.1, FR12).

Godkjenningsflaten henter Vakten og én Gyldig kandidat herfra. Endepunktet er
lesende. Testene bruker Kandidater som er gyldige også etter story 2.4: Jonas
Bakke (6) og Mette Solberg (5) for #4127 (OP-13). Testen for utelukkede er ikke
bundet til en regel: den sammenligner med svaret fra `/kandidater`.
"""

from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event, select, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import OSLO, AnsattRad, Base, GodkjenningRad, VaktRad
from adaptere.lagring.preferansetolkning import lagre_resultat
from adaptere.lagring.testdata import ANSATTE, MANGLER_BEMANNING, fyll_testdata
from domene.porter.rangering import TolketPreferanse
from domene.regelmotor.vurdering import REGLER
from tester.api.test_kandidater import RANGERT_FELT, forleng_ingrids_første_vakt_i_uka
from tester.api.test_innlogging import COOKIE_NAVN, engine, feilsvar, klient, logg_inn  # noqa: F401

NAVN = {ansatt_id: navn for ansatt_id, navn, *_ in ANSATTE}
KOMPETANSE = {ansatt_id: kompetanse for ansatt_id, _, _, _, _, kompetanse, _ in ANSATTE}
JONAS, METTE, THOMAS, INGRID = 6, 5, 3, 4
SILJE = MANGLER_BEMANNING[4127][0]

# Jonas er nr. 1 for #4127 uten lagrede tolkninger (AV-07, FAKTORER_4127/UTEN_TOLKNING_4127
# i test_rangering.py). Story 4.5 bruker det samme svaret som `topprangert` for Mette,
# som er nr. 2 (test_jonas_på_4127_har_nøyaktig_dette_svaret under).
JONAS_SOM_TOPPRANGERT = {
    "id": JONAS, "navn": "Jonas Bakke", "kompetansenivå": KOMPETANSE[JONAS]["dag"],
    "kostnad": {"total": 2960, "ordinære_timer": 8, "overtidstimer": 0, "ordinær_sats": 370, "overtidssats": 555},
    "minutter_i_uka": 960,  # 16 t i uke 39
    "timebelastning_prosent": 100 * 16 / 36, "hoy_belastning": False,
    "ulempebelastning": {
        "dagtimer": 67, "kveldstimer": 4, "helgetimer": 15, "natttimer": 2,
        "poeng": 40, "score": 100 * (1 - 40 / 300),
    },
    "stilling": "Sykepleier", "ansiennitet": 3, "plass": 1, "totalscore": 3335 / 42,
    "faktorpoeng": {"kostnad": 1780 / 21, "timebelastning": 100, "ulempe": 260 / 3},
    "preferansepoeng": 50, "tolkestatus": "venter_paa_tolkning", "preferansekategori": None,
}


def sti(vaktnummer: int, ansatt_id: int | str) -> str:
    return f"/api/vakter/{vaktnummer}/kandidater/{ansatt_id}"


def gyldige_ider(klient: TestClient, vaktnummer: int) -> set[int]:
    respons = klient.get(f"/api/vakter/{vaktnummer}/kandidater")
    assert respons.status_code == 200
    return {k["id"] for k in respons.json()["kandidater"]}


def øyeblikksbilde(engine: Engine) -> dict[str, list[tuple]]:
    """Alle rader i alle tabeller, også `vakt`, som tupler."""
    with lag_sessionmaker(engine)() as session:
        return {
            tabell.name: [tuple(rad) for rad in session.execute(select(tabell).order_by(*tabell.primary_key.columns))]
            for tabell in Base.metadata.sorted_tables
        }


def assert_ikke_funnet(respons) -> None:  # type: ignore[no-untyped-def]
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())
    for navn in NAVN.values():
        assert navn not in respons.text


# --- Gyldig kandidat -------------------------------------------------------------


@pytest.mark.parametrize("ansatt_id", [JONAS, METTE])
def test_gyldig_kandidat_gir_vakt_og_kandidat(klient: TestClient, ansatt_id: int) -> None:
    logg_inn(klient)
    respons = klient.get(sti(4127, ansatt_id))

    assert respons.status_code == 200
    svar = respons.json()
    assert set(svar) == {"status", "vakt", "kandidat", "topprangert", "grunnlagsmerke"}
    assert len(svar["grunnlagsmerke"]) == 64
    assert svar["status"] == "ok"
    # Vakten og Kandidaten er de samme som i listen (story 4.4), som nå har de samme
    # feltene som godkjenningsgrunnlagets kandidat (story 4.5: begge er RangertKandidatUt).
    assert svar["vakt"] == klient.get("/api/vakter/4127").json()
    liste = klient.get("/api/vakter/4127/kandidater").json()["kandidater"]
    (fra_listen,) = [k for k in liste if k["id"] == ansatt_id]
    assert svar["kandidat"] == {felt: fra_listen[felt] for felt in svar["kandidat"]}
    assert svar["kandidat"]["navn"] == NAVN[ansatt_id]
    # Topprangert er nøyaktig nr. 1 fra samme liste, eller None når valgt selv er nr. 1.
    if fra_listen["plass"] == 1:
        assert svar["topprangert"] is None
    else:
        (topp,) = [k for k in liste if k["plass"] == 1]
        assert svar["topprangert"] == topp


def test_jonas_på_4127_har_nøyaktig_dette_svaret(klient: TestClient) -> None:
    logg_inn(klient)
    svar = klient.get(sti(4127, JONAS)).json()
    assert len(svar.pop("grunnlagsmerke")) == 64
    assert svar == {
        "status": "ok",
        "vakt": {
            "avdeling": "Kirurgisk sengepost",
            "vaktnummer": 4127,
            "vakttype": "dag",
            "start": "2026-09-27T07:00:00+02:00",
            "slutt": "2026-09-27T15:00:00+02:00",
            "minstenivå": 3,
        },
        "kandidat": JONAS_SOM_TOPPRANGERT,
        "topprangert": None,
    }


def test_mette_på_4127_har_nøyaktig_dette_svaret_med_jonas_som_topprangert(klient: TestClient) -> None:
    """Mette er nr. 2 (72,40) bak Jonas (79,40), uten lagrede tolkninger (AV-07, P-05).

    Ulempefordelingen (kveld/helg/natt) er ikke egen fasit i dokumentasjonen; bare
    poeng og score (begge kjente fasittall) kontrolleres eksplisitt, og resten av
    fordelingsdelen gjenbrukes uendret fra selve svaret for å låse alle andre felt.
    """
    logg_inn(klient)
    svar = klient.get(sti(4127, METTE)).json()
    assert len(svar.pop("grunnlagsmerke")) == 64
    ulempe = svar["kandidat"]["ulempebelastning"]
    assert (ulempe["poeng"], ulempe["score"]) == (180, 40)
    assert svar == {
        "status": "ok",
        "vakt": {
            "avdeling": "Kirurgisk sengepost",
            "vaktnummer": 4127,
            "vakttype": "dag",
            "start": "2026-09-27T07:00:00+02:00",
            "slutt": "2026-09-27T15:00:00+02:00",
            "minstenivå": 3,
        },
        "kandidat": {
            "id": METTE, "navn": "Mette Solberg", "kompetansenivå": KOMPETANSE[METTE]["dag"],
            "kostnad": {"total": 2960, "ordinære_timer": 8, "overtidstimer": 0, "ordinær_sats": 370, "overtidssats": 555},
            "minutter_i_uka": 960,  # 16 t i uke 39
            "timebelastning_prosent": 100 * 16 / 36, "hoy_belastning": False,
            "ulempebelastning": ulempe,
            "stilling": "Sykepleier", "ansiennitet": 9, "plass": 2, "totalscore": 3041 / 42,
            "faktorpoeng": {"kostnad": 1780 / 21, "timebelastning": 100, "ulempe": 40},
            "preferansepoeng": 50, "tolkestatus": "venter_paa_tolkning", "preferansekategori": None,
        },
        "topprangert": JONAS_SOM_TOPPRANGERT,
    }


@pytest.mark.parametrize("ekstra,høy", [(23, False), (24, True)])
def test_timebelastning_i_godkjenningsgrunnlaget_følger_32_24_grensen(
    klient: TestClient, engine: Engine, ekstra: int, høy: bool
) -> None:
    """Samme grense som i kandidatlisten (story 4.2, P-04), via godkjenningsgrunnlaget."""
    INGRID = 4
    forleng_ingrids_første_vakt_i_uka(engine, ekstra)
    logg_inn(klient)
    kandidat = klient.get(sti(4127, INGRID)).json()["kandidat"]

    assert kandidat["hoy_belastning"] is høy
    assert kandidat["timebelastning_prosent"] == pytest.approx(100 * (1920 + ekstra) / 2160)


def test_timebelastning_i_godkjenningsgrunnlaget_bevarer_sekunder(klient: TestClient, engine: Engine) -> None:
    forleng_ingrids_første_vakt_i_uka(engine, 23, 59)
    logg_inn(klient)
    kandidat = klient.get(sti(4127, 4)).json()["kandidat"]
    assert kandidat["minutter_i_uka"] == 32 * 60 + 23
    assert kandidat["hoy_belastning"] is False
    assert kandidat["timebelastning_prosent"] == pytest.approx(100 * (32 * 3600 + 23 * 60 + 59) / (36 * 3600))


@pytest.mark.parametrize("vaktnummer", [4127, 4189])
def test_alle_i_listen_gir_200_og_alle_andre_404(klient: TestClient, vaktnummer: int) -> None:
    # Regeluavhengig (OP-13): fasiten er det `/kandidater` svarer, uansett hvor
    # mange regler som er på plass. Listen for #4189 kan være tom (0 etter 2.4),
    # og da skal alle Ansatte gi 404.
    logg_inn(klient)
    gyldige = gyldige_ider(klient, vaktnummer)
    if vaktnummer == 4127:
        assert gyldige
    assert MANGLER_BEMANNING[vaktnummer][0] not in gyldige

    for ansatt_id in sorted(NAVN):
        respons = klient.get(sti(vaktnummer, ansatt_id))
        if ansatt_id in gyldige:
            assert respons.status_code == 200, ansatt_id
            assert respons.json()["kandidat"]["id"] == ansatt_id
        else:
            assert_ikke_funnet(respons)


def test_utelukket_ukjent_og_satt_opp_gir_samme_svar(klient: TestClient) -> None:
    # Svaret sier ikke om personen finnes, eller hvilken regel som slår inn (NFR2).
    logg_inn(klient)
    gyldige = gyldige_ider(klient, 4127)
    utelukket = min(set(NAVN) - gyldige - {SILJE})
    svar = [klient.get(sti(4127, ansatt_id)) for ansatt_id in (utelukket, SILJE, 999, 0, -1)]

    for respons in svar:
        assert_ikke_funnet(respons)
    assert len({respons.text for respons in svar}) == 1


def test_svaret_for_gyldig_nevner_ingen_utelukket(klient: TestClient) -> None:
    logg_inn(klient)
    respons = klient.get(sti(4127, METTE))
    # Mette er ikke topprangert (plass 2), så dette svaret inneholder også
    # Jonas' tall i `topprangert` — teksten under dekker begge.
    assert respons.json()["topprangert"] is not None
    tekst = respons.text

    for ansatt_id, navn in NAVN.items():
        if ansatt_id not in (METTE, JONAS):
            assert navn not in tekst
    for ord_ in (*(regel.årsak for regel in REGLER), "utelukket", "satt_opp"):
        assert ord_ not in tekst


def test_kandidaten_har_bare_kontraktsfeltene(klient: TestClient) -> None:
    logg_inn(klient)
    jonas = klient.get(sti(4127, JONAS)).json()
    assert set(jonas["kandidat"]) == RANGERT_FELT
    assert jonas["topprangert"] is None
    assert set(jonas["vakt"]) == {"avdeling", "vaktnummer", "vakttype", "start", "slutt", "minstenivå"}

    mette = klient.get(sti(4127, METTE)).json()
    assert set(mette["kandidat"]) == RANGERT_FELT
    assert set(mette["topprangert"]) == RANGERT_FELT


def test_topprangert_er_none_bare_for_plass_1(klient: TestClient) -> None:
    logg_inn(klient)
    liste = klient.get("/api/vakter/4127/kandidater").json()["kandidater"]
    (nummer_1,) = [k for k in liste if k["plass"] == 1]

    for kandidat in liste:
        svar = klient.get(sti(4127, kandidat["id"])).json()
        if kandidat["plass"] == 1:
            assert svar["topprangert"] is None
        else:
            assert svar["topprangert"] == nummer_1
            # Ikke en kopi av valgt: Mette og de andre har ikke Jonas' id.
            assert svar["topprangert"]["id"] != svar["kandidat"]["id"]


def test_eneste_gyldige_kandidat_er_alltid_topprangert_selv(klient: TestClient, engine: Engine) -> None:
    """En Gyldig kandidat for vakten gir plass 1 og ingen topprangert (I/O-matrisen)."""
    with lag_sessionmaker(engine).begin() as session:
        for ansatt_id in (METTE, THOMAS, INGRID):
            session.execute(update(AnsattRad).where(AnsattRad.id == ansatt_id).values(kompetanse={"dag": 1}))
    logg_inn(klient)
    liste = klient.get("/api/vakter/4127/kandidater").json()
    assert liste["status"] == "ok"
    assert [k["navn"] for k in liste["kandidater"]] == ["Jonas Bakke"]

    svar = klient.get(sti(4127, JONAS)).json()
    assert svar["kandidat"]["plass"] == 1
    assert svar["topprangert"] is None


def test_lagret_tolkning_endrer_topprangert_uten_live_kall(klient: TestClient, engine: Engine) -> None:
    """Syntetisk eksempel (ikke en påstand om seedteksten, AV-07): Mette tolkes til
    «ønsker flere» (100 preferansepoeng), lagret direkte uten KI-kall. Jonas har
    ingen lagret tolkning og får fortsatt 50 (P-05). Det er nok til at Mette blir
    topprangert i stedet for Jonas, selv om de andre faktorene er uendret (AV-12)."""
    okter = lag_sessionmaker(engine)
    with okter() as session:
        tekst = session.get(AnsattRad, METTE).preferanse
    assert tekst
    assert lagre_resultat(okter, METTE, tekst, TolketPreferanse("onsker_flere", "Syntetisk testtekst.", "test"))
    logg_inn(klient)

    svar_jonas = klient.get(sti(4127, JONAS)).json()
    svar_mette = klient.get(sti(4127, METTE)).json()

    assert svar_mette["kandidat"]["plass"] == 1
    assert svar_mette["kandidat"]["tolkestatus"] == "tolket"
    assert svar_mette["kandidat"]["preferansekategori"] == "onsker_flere"
    assert svar_mette["topprangert"] is None

    assert svar_jonas["kandidat"]["plass"] == 2
    assert svar_jonas["kandidat"]["tolkestatus"] == "venter_paa_tolkning"
    assert svar_jonas["topprangert"] == svar_mette["kandidat"]


# --- Vakt som ikke mangler bemanning, og tilgang --------------------------------


@pytest.mark.parametrize("vaktnummer", [4128, 9999])
def test_bemannet_og_ukjent_vakt_gir_404(klient: TestClient, vaktnummer: int) -> None:
    logg_inn(klient)
    assert_ikke_funnet(klient.get(sti(vaktnummer, JONAS)))


def test_uten_sesjon_gir_401(klient: TestClient) -> None:
    respons = klient.get(sti(4127, JONAS))
    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())
    assert "Jonas" not in respons.text


@pytest.mark.parametrize("metode", ["PUT", "PATCH", "DELETE"])
def test_ingen_skrivende_metode(klient: TestClient, engine: Engine, metode: str) -> None:
    logg_inn(klient)
    før = øyeblikksbilde(engine)
    respons = klient.request(metode, sti(4127, JONAS))
    assert respons.status_code == 405
    assert feilsvar("metode_ikke_tillatt")(respons.json())
    assert øyeblikksbilde(engine) == før


def test_ansatt_id_som_ikke_er_tall_gir_422(klient: TestClient) -> None:
    logg_inn(klient)
    respons = klient.get(sti(4127, "jonas"))
    assert respons.status_code == 422
    assert feilsvar("ugyldig_foresporsel")(respons.json())


# --- Datafeil (P-08) ---------------------------------------------------------------


def flytt_4127_til_periodekanten(engine: Engine) -> None:
    # Hvilen etter kan ikke kontrolleres når slutt + 11 t passerer datagrensen.
    start = datetime(2026, 10, 4, 5, 1, tzinfo=OSLO)
    with lag_sessionmaker(engine).begin() as session:
        session.execute(
            update(VaktRad).where(VaktRad.vaktnummer == 4127).values(start=start, slutt=start + timedelta(hours=8))
        )


@pytest.mark.parametrize("ansatt_id", [JONAS, METTE, SILJE, 999])
def test_datafeil_gir_datafeilsvaret_uten_kandidat(
    klient: TestClient, engine: Engine, caplog: pytest.LogCaptureFixture, ansatt_id: int,
) -> None:
    # Uten vurdering er det ukjent hvem som er gyldig, så id-en avgjør ikke svaret.
    flytt_4127_til_periodekanten(engine)
    logg_inn(klient)
    with caplog.at_level("WARNING", logger="adaptere.api.main"):
        respons = klient.get(sti(4127, ansatt_id))
    assert respons.status_code == 200
    assert respons.json() == {
        "status": "datafeil",
        "kode": "mangler_turnusgrunnlag",
        "datagrense": "2026-10-05T00:00:00+02:00",
    }
    assert "Datafeil for vakt 4127" in caplog.text
    for navn in NAVN.values():
        assert navn not in respons.text


# --- Lesende (FR12) ---------------------------------------------------------------


def test_databasen_er_uendret_etter_ok_404_og_datafeil(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    før = øyeblikksbilde(engine)
    vakt_før = før["vakt"]
    assert vakt_før

    assert klient.get(sti(4127, JONAS)).status_code == 200
    assert klient.get(sti(4127, METTE)).status_code == 200
    assert klient.get(sti(4127, SILJE)).status_code == 404
    assert klient.get(sti(4127, 999)).status_code == 404
    assert klient.get(sti(4128, JONAS)).status_code == 404
    assert øyeblikksbilde(engine) == før

    flytt_4127_til_periodekanten(engine)
    etter_flytting = øyeblikksbilde(engine)
    assert klient.get(sti(4127, JONAS)).json()["status"] == "datafeil"
    assert øyeblikksbilde(engine) == etter_flytting


def test_4127_mangler_fortsatt_bemanning_etter_visning(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    for _ in range(2):
        assert klient.get(sti(4127, JONAS)).status_code == 200
    with lag_sessionmaker(engine)() as session:
        rad = session.scalars(select(VaktRad).where(VaktRad.vaktnummer == 4127)).one()
        assert rad.mangler_bemanning is True
        assert rad.tildelt_ansatt_id is None
    assert 4127 in {v["vaktnummer"] for v in klient.get("/api/vaktoversikt").json()["krever_handling"]}


def test_post_lagrer_en_godkjenning_og_bemanner_vakten(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke}).json() == {"status": "godkjent"}
    with lag_sessionmaker(engine)() as session:
        (godkjenning,) = session.scalars(select(GodkjenningRad)).all()
        vakt = session.scalar(select(VaktRad).where(VaktRad.vaktnummer == 4127))
        assert godkjenning.ansatt_id == JONAS
        assert godkjenning.vakt_id == vakt.id
        assert godkjenning.bruker_id is not None
        assert godkjenning.godkjent.utcoffset() is not None
        assert vakt.tildelt_ansatt_id == JONAS
        assert not vakt.mangler_bemanning
    oversikt = klient.get("/api/vaktoversikt").json()
    assert 4127 not in {v["vaktnummer"] for v in oversikt["krever_handling"]}
    assert next(v for v in oversikt["bemannet"] if v["vaktnummer"] == 4127)["ansatt"]["navn"] == "Jonas Bakke"
    dublett = klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke})
    assert dublett.status_code == 409
    assert feilsvar("allerede_bemannet")(dublett.json())


def test_endret_grunnlag_krever_nytt_trykk(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    gammelt = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(minstenivå=2))
    før = øyeblikksbilde(engine)
    svar = klient.post(sti(4127, JONAS), json={"grunnlagsmerke": gammelt})
    assert svar.status_code == 409
    assert feilsvar("endret_grunnlag")(svar.json())
    assert øyeblikksbilde(engine) == før
    nytt = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    assert nytt != gammelt
    assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": nytt}).status_code == 200


@pytest.mark.parametrize("endring", ["ansatt", "vakttid"])
def test_ansatt_og_vakttid_endrer_merket_uten_lagring(
    klient: TestClient, engine: Engine, endring: str,
) -> None:
    logg_inn(klient)
    gammelt = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    with lag_sessionmaker(engine).begin() as session:
        if endring == "ansatt":
            session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(navn="Jonas Oppdatert"))
        else:
            vakt = session.scalar(select(VaktRad).where(VaktRad.vaktnummer == 4127))
            session.execute(update(VaktRad).where(VaktRad.id == vakt.id).values(
                start=vakt.start + timedelta(minutes=1), slutt=vakt.slutt + timedelta(minutes=1),
            ))
    før = øyeblikksbilde(engine)
    svar = klient.post(sti(4127, JONAS), json={"grunnlagsmerke": gammelt})
    assert svar.status_code == 409
    assert feilsvar("endret_grunnlag")(svar.json())
    assert øyeblikksbilde(engine) == før
    nytt = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    assert nytt != gammelt
    assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": nytt}).status_code == 200


def test_endret_lønn_krever_nytt_trykk_og_gir_ny_kostnad(klient: TestClient, engine: Engine) -> None:
    """P-09 for kostnaden (story 4.3): en lønnsendring etter visning lagrer ingenting.

    Ingrid har 4 t ordinær tid og 4 t overtid på #4127, så både satsen og 150 %-satsen
    må følge med i det nye grunnlaget.
    """
    ingrid = 4
    logg_inn(klient)
    gammelt = klient.get(sti(4127, ingrid)).json()
    assert gammelt["kandidat"]["kostnad"]["total"] == 3850
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == ingrid).values(timelønn=400))
    før = øyeblikksbilde(engine)
    svar = klient.post(sti(4127, ingrid), json={"grunnlagsmerke": gammelt["grunnlagsmerke"]})
    assert svar.status_code == 409
    assert feilsvar("endret_grunnlag")(svar.json())
    assert øyeblikksbilde(engine) == før
    nytt = klient.get(sti(4127, ingrid)).json()
    assert nytt["grunnlagsmerke"] != gammelt["grunnlagsmerke"]
    assert nytt["kandidat"]["kostnad"] == {
        "total": 4000, "ordinære_timer": 4, "overtidstimer": 4, "ordinær_sats": 400, "overtidssats": 600,
    }
    assert klient.post(sti(4127, ingrid), json={"grunnlagsmerke": nytt["grunnlagsmerke"]}).status_code == 200


def test_merket_er_knyttet_til_valgt_kandidat(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    jonas = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    mette = klient.get(sti(4127, METTE)).json()["grunnlagsmerke"]
    assert jonas != mette
    før = øyeblikksbilde(engine)
    svar = klient.post(sti(4127, METTE), json={"grunnlagsmerke": jonas})
    assert svar.status_code == 409
    assert feilsvar("endret_grunnlag")(svar.json())
    assert øyeblikksbilde(engine) == før


def test_get_visning_og_merke_kommer_fra_samme_snapshot(
    klient: TestClient, engine: Engine, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # WAL lar den andre forbindelsen committe mens GET holder et lesesnapshot.
    with engine.connect() as forbindelse:
        forbindelse.exec_driver_sql("PRAGMA journal_mode=WAL")
    logg_inn(klient)
    gammelt = klient.get(sti(4127, JONAS)).json()
    api = import_module("adaptere.api.main")
    opprinnelig = api.hent_vaktdetaljer

    def endre_etter_grunnlag(*args):  # type: ignore[no-untyped-def]
        with lag_sessionmaker(engine).begin() as session:
            session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(navn="Jonas Nytt Navn"))
        return opprinnelig(*args)

    monkeypatch.setattr(api, "hent_vaktdetaljer", endre_etter_grunnlag)
    svar = klient.get(sti(4127, JONAS))
    assert svar.status_code == 200
    assert svar.json()["kandidat"] == gammelt["kandidat"]
    assert svar.json()["grunnlagsmerke"] == gammelt["grunnlagsmerke"]


def test_feil_etter_vaktoppdatering_ruller_tilbake_begge_endringer(
    klient: TestClient, engine: Engine,
) -> None:
    logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    før = øyeblikksbilde(engine)
    def feiler_ved_innsetting(_mapper, _connection, _rad):  # type: ignore[no-untyped-def]
        raise RuntimeError("simulert feil etter oppdatering")

    event.listen(GodkjenningRad, "before_insert", feiler_ved_innsetting)
    try:
        assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke}).status_code == 500
    finally:
        event.remove(GodkjenningRad, "before_insert", feiler_ved_innsetting)
    assert øyeblikksbilde(engine) == før


def test_lagringsoperasjonen_tar_skrivelas_for_lesing(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch,
) -> None:
    logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    lagring = import_module("adaptere.lagring.godkjenninger")
    opprinnelig = lagring.hent_kandidatgrunnlag
    kontrollert = False

    def kontroller_transaksjon(session, bruker_id, vaktnummer):  # type: ignore[no-untyped-def]
        nonlocal kontrollert
        # SQLite-transaksjonen må være startet før første kandidatspørring.
        assert session.connection().connection.driver_connection.in_transaction
        kontrollert = True
        return opprinnelig(session, bruker_id, vaktnummer)

    monkeypatch.setattr(lagring, "hent_kandidatgrunnlag", kontroller_transaksjon)
    assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke}).status_code == 200
    assert kontrollert


def test_ugyldig_og_datafeil_skriver_ingenting(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    før = øyeblikksbilde(engine)
    ugyldig = klient.post(sti(4127, SILJE), json={"grunnlagsmerke": merke})
    assert ugyldig.status_code == 409
    assert feilsvar("ugyldig_kandidat")(ugyldig.json())
    assert øyeblikksbilde(engine) == før
    flytt_4127_til_periodekanten(engine)
    etter = øyeblikksbilde(engine)
    datafeil = klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke})
    assert datafeil.status_code == 200
    assert datafeil.json()["status"] == "datafeil"
    assert øyeblikksbilde(engine) == etter


def test_samtidige_post_gir_bare_en_godkjenning(klient: TestClient, engine: Engine) -> None:
    token = logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]

    def forsok() -> int:
        with TestClient(klient.app, raise_server_exceptions=False) as egen:
            return egen.post(
                sti(4127, JONAS), json={"grunnlagsmerke": merke},
                headers={"Cookie": f"{COOKIE_NAVN}={token}"},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        svar = list(pool.map(lambda _: forsok(), range(2)))
    assert sorted(svar) == [200, 409]
    with lag_sessionmaker(engine)() as session:
        assert len(session.scalars(select(GodkjenningRad)).all()) == 1


def test_ny_seeding_sletter_godkjenning_for_vakter(klient: TestClient, engine: Engine) -> None:
    logg_inn(klient)
    merke = klient.get(sti(4127, JONAS)).json()["grunnlagsmerke"]
    assert klient.post(sti(4127, JONAS), json={"grunnlagsmerke": merke}).status_code == 200
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
    with lag_sessionmaker(engine)() as session:
        assert session.scalars(select(GodkjenningRad)).all() == []
        vakt = session.scalar(select(VaktRad).where(VaktRad.vaktnummer == 4127))
        assert vakt.mangler_bemanning


def test_post_uten_sesjon_skriver_ingenting(klient: TestClient, engine: Engine) -> None:
    før = øyeblikksbilde(engine)
    svar = klient.post(sti(4127, JONAS), json={"grunnlagsmerke": "a" * 64})
    assert svar.status_code == 401
    assert feilsvar("mangler_sesjon")(svar.json())
    assert øyeblikksbilde(engine) == før


def test_andre_api_ruter_bemanner_ikke_og_lager_ingen_godkjenning(
    klient: TestClient, engine: Engine,
) -> None:
    logg_inn(klient)
    før = øyeblikksbilde(engine)
    for rute in (
        "/api/meg", "/api/vaktoversikt", "/api/vakter/4127",
        "/api/vakter/4127/kandidater", sti(4127, JONAS),
        "/api/innloggingsinfo", "/api/helse",
    ):
        assert klient.get(rute).status_code == 200
    assert klient.post("/api/utlogging").status_code == 204
    assert øyeblikksbilde(engine) == før
    with lag_sessionmaker(engine)() as session:
        assert session.scalars(select(GodkjenningRad)).all() == []
        vakt = session.scalar(select(VaktRad).where(VaktRad.vaktnummer == 4127))
        assert vakt.mangler_bemanning
        assert vakt.tildelt_ansatt_id is None
