"""GET /api/vakter/{vaktnummer}/kandidater (story 2.1 og 2.2).

Fasiten kommer fra `testdata.FASIT` (AV-07). Med kompetanse-minstekravet og
kolliderende vakt på plass er de gyldige alle unntatt dem fasiten utelukker på
`kompetanse` eller `kolliderende`. De to andre reglene kommer i 2.3 og 2.4.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import OSLO, AnsattRad, TurnusRad, VaktRad
from adaptere.lagring.testdata import ANSATTE, FASIT, MANGLER_BEMANNING, PERIODE_SLUTT, PERIODE_START
from tester.api.test_innlogging import engine, feilsvar, klient, logg_inn  # noqa: F401

NAVN = {ansatt_id: navn for ansatt_id, navn, *_ in ANSATTE}
KOMPETANSE = {navn: kompetanse for _, navn, _, _, _, kompetanse, _ in ANSATTE}


def hent(klient: TestClient, nummer: int) -> dict:
    logg_inn(klient)
    respons = klient.get(f"/api/vakter/{nummer}/kandidater")
    assert respons.status_code == 200
    return respons.json()


IMPLEMENTERTE_REGLER = {"kompetanse", "kolliderende"}


def forventet_gyldige(nummer: int) -> set[str]:
    return {navn for navn, utfall in FASIT[nummer]["utfall"].items() if utfall not in IMPLEMENTERTE_REGLER}


def forventet_utelukket(nummer: int) -> set[str]:
    return {navn for navn, utfall in FASIT[nummer]["utfall"].items() if utfall in IMPLEMENTERTE_REGLER}


@pytest.mark.parametrize("nummer,antall", [(4127, 9), (4189, 19)])
def test_gyldige_stemmer_med_fasiten(klient: TestClient, nummer: int, antall: int) -> None:
    svar = hent(klient, nummer)

    assert set(svar) == {"status", "kandidater"}
    assert svar["status"] == "ok"
    navn = [k["navn"] for k in svar["kandidater"]]
    assert len(navn) == len(set(navn)) == antall
    assert set(navn) == forventet_gyldige(nummer)


@pytest.mark.parametrize("nummer", [4127, 4189])
def test_bare_gyldige_sendes_nfr2(klient: TestClient, nummer: int) -> None:
    logg_inn(klient)
    respons_tekst = klient.get(f"/api/vakter/{nummer}/kandidater").text
    utelukket = forventet_utelukket(nummer)
    satt_opp = NAVN[MANGLER_BEMANNING[nummer][0]]

    # 4127: 8 kompetanse + 7 kollisjon. 4189: 3 kompetanse + 2 kollisjon.
    assert len(utelukket) == {4127: 15, 4189: 5}[nummer]
    for navn in utelukket | {satt_opp}:
        assert navn not in respons_tekst
    assert "kompetanse-minstekrav" not in respons_tekst
    assert "kolliderende" not in respons_tekst


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
    # De to andre reglene er ikke på plass ennå, så de som bare brytes av dem, er med.
    assert {n for n, utfall in FASIT[nummer]["utfall"].items() if utfall in {"elleve-timer", "trettifem-timer"}} <= navn


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
    assert navn[0] == "Anders Strand"


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


def test_vakt_som_slutter_ved_datagrensen_vurderes(klient: TestClient, engine: Engine) -> None:
    start = datetime(2026, 10, 4, 16, 0, tzinfo=OSLO)
    endre_vakt(engine, vakttype="kveld", start=start, slutt=start + timedelta(hours=8))
    assert hent(klient, 4127)["status"] == "ok"


def test_vakt_som_slutter_etter_datagrensen_gir_datafeil(
    klient: TestClient, engine: Engine, caplog: pytest.LogCaptureFixture,
) -> None:
    start = datetime(2026, 10, 4, 16, 1, tzinfo=OSLO)
    endre_vakt(engine, vakttype="kveld", start=start, slutt=start + timedelta(hours=8))
    with caplog.at_level("WARNING", logger="adaptere.api.main"):
        assert_datafeil(hent(klient, 4127))
    # Grunnen logges for feilsøking, men sendes ikke i svaret.
    assert "Datafeil for vakt 4127" in caplog.text
    assert "datagrensen" in caplog.text


def test_start_ikke_før_slutt_gir_datafeil(klient: TestClient, engine: Engine) -> None:
    start = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)
    endre_vakt(engine, slutt=start)
    assert_datafeil(hent(klient, 4127))


@pytest.mark.parametrize("verdi", [0, 5, "3"])
def test_ugyldig_kompetanseverdi_gir_datafeil(klient: TestClient, engine: Engine, verdi: object) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == 3).values(kompetanse={"dag": verdi, "natt": 3}))
    assert_datafeil(hent(klient, 4127))
