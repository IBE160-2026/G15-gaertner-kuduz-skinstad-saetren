"""GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id} (story 3.1, FR12).

Godkjenningsflaten henter Vakten og én Gyldig kandidat herfra. Endepunktet er
lesende. Testene bruker Kandidater som er gyldige også etter story 2.4: Jonas
Bakke (6) og Mette Solberg (5) for #4127 (OP-13). Testen for utelukkede er ikke
bundet til en regel: den sammenligner med svaret fra `/kandidater`.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import OSLO, Base, VaktRad
from adaptere.lagring.testdata import ANSATTE, MANGLER_BEMANNING
from domene.regelmotor.vurdering import REGLER
from tester.api.test_innlogging import engine, feilsvar, klient, logg_inn  # noqa: F401

NAVN = {ansatt_id: navn for ansatt_id, navn, *_ in ANSATTE}
KOMPETANSE = {ansatt_id: kompetanse for ansatt_id, _, _, _, _, kompetanse, _ in ANSATTE}
JONAS, METTE = 6, 5
SILJE = MANGLER_BEMANNING[4127][0]


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
    assert set(svar) == {"status", "vakt", "kandidat"}
    assert svar["status"] == "ok"
    # Vakten er den samme som vaktdetaljene gir, og Kandidaten den samme som i listen.
    assert svar["vakt"] == klient.get("/api/vakter/4127").json()
    (fra_listen,) = [k for k in klient.get("/api/vakter/4127/kandidater").json()["kandidater"] if k["id"] == ansatt_id]
    assert svar["kandidat"] == fra_listen
    assert svar["kandidat"]["navn"] == NAVN[ansatt_id]


def test_jonas_på_4127_har_nøyaktig_dette_svaret(klient: TestClient) -> None:
    logg_inn(klient)
    assert klient.get(sti(4127, JONAS)).json() == {
        "status": "ok",
        "vakt": {
            "avdeling": "Kirurgisk sengepost",
            "vaktnummer": 4127,
            "vakttype": "dag",
            "start": "2026-09-27T07:00:00+02:00",
            "slutt": "2026-09-27T15:00:00+02:00",
            "minstenivå": 3,
        },
        "kandidat": {"id": JONAS, "navn": "Jonas Bakke", "kompetansenivå": KOMPETANSE[JONAS]["dag"]},
    }


@pytest.mark.parametrize("vaktnummer", [4127, 4189])
def test_alle_i_listen_gir_200_og_alle_andre_404(klient: TestClient, vaktnummer: int) -> None:
    # Regeluavhengig (OP-13): fasiten er det `/kandidater` svarer, uansett hvor
    # mange regler som er på plass.
    logg_inn(klient)
    gyldige = gyldige_ider(klient, vaktnummer)
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
    tekst = klient.get(sti(4127, METTE)).text

    for ansatt_id, navn in NAVN.items():
        if ansatt_id != METTE:
            assert navn not in tekst
    for ord_ in (*(regel.årsak for regel in REGLER), "utelukket", "satt_opp"):
        assert ord_ not in tekst


def test_kandidaten_har_bare_id_navn_og_nivå(klient: TestClient) -> None:
    logg_inn(klient)
    svar = klient.get(sti(4127, JONAS)).json()
    assert set(svar["kandidat"]) == {"id", "navn", "kompetansenivå"}
    assert set(svar["vakt"]) == {"avdeling", "vaktnummer", "vakttype", "start", "slutt", "minstenivå"}


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


@pytest.mark.parametrize("metode", ["POST", "PUT", "PATCH", "DELETE"])
def test_ingen_skrivende_metode(klient: TestClient, engine: Engine, metode: str) -> None:
    # Godkjenningen skrives først i story 3.2.
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
