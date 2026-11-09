"""Tilgang og periodegrenser for GET /api/vakter/{vaktnummer}."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, update

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import TurnusRad, VaktRad
from adaptere.lagring.testdata import ANSATTE, PERIODE_START, PERIODE_SLUTT
from tester.api.test_innlogging import engine, feilsvar, klient, logg_inn  # noqa: F401


@pytest.mark.parametrize("nummer,forventet", [
    (4127, {"vakttype": "dag", "start": "2026-09-27T07:00:00+02:00", "slutt": "2026-09-27T15:00:00+02:00", "minstenivå": 3}),
    (4189, {"vakttype": "natt", "start": "2026-09-28T23:00:00+02:00", "slutt": "2026-09-29T07:00:00+02:00", "minstenivå": 3}),
])
def test_ubemannet_vakt_i_egen_turnus(klient: TestClient, nummer: int, forventet: dict) -> None:
    logg_inn(klient)
    respons = klient.get(f"/api/vakter/{nummer}")
    assert respons.status_code == 200
    assert respons.json() == {"avdeling": "Kirurgisk sengepost", "vaktnummer": nummer, **forventet}
    assert "kandidat" not in respons.text.lower()


@pytest.mark.parametrize("nummer", [4128, 3338, 999999])
def test_bemannet_historisk_og_ukjent_gir_samme_404(klient: TestClient, nummer: int) -> None:
    logg_inn(klient)
    respons = klient.get(f"/api/vakter/{nummer}")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())
    assert "vaktnummer" not in respons.text


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
    respons = klient.get("/api/vakter/4127")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())


@pytest.mark.parametrize("start,synlig", [(PERIODE_START, True), (PERIODE_SLUTT, False), (PERIODE_START - timedelta(minutes=1), False)])
def test_halvapen_periode_ved_grensene(klient: TestClient, engine: Engine, start, synlig: bool) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(start=start, slutt=start + timedelta(hours=8)))
    logg_inn(klient)
    respons = klient.get("/api/vakter/4127")
    assert respons.status_code == (200 if synlig else 404)


def test_uten_sesjon_gir_401(klient: TestClient) -> None:
    respons = klient.get("/api/vakter/4127")
    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_bemannet_status_avviser_tidligere_gyldig_vakt(klient: TestClient, engine: Engine) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(
            tildelt_ansatt_id=ANSATTE[0][0], mangler_bemanning=False,
            satt_opp_ansatt_id=None, meldt_fra=None, meldt_fra_grunn=None,
        ))
    logg_inn(klient)
    respons = klient.get("/api/vakter/4127")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())
