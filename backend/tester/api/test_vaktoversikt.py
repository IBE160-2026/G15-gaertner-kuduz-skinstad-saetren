"""Tester for GET /api/vaktoversikt (story 1.5).

Fixturene `engine` og `klient` og `logg_inn` gjenbrukes fra testene for
innlogging, så appen bygges mot en database i `tmp_path`.
"""

from datetime import datetime, timedelta

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import Engine, update

from adaptere.api.sesjon import COOKIE_NAVN
from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import OSLO, VaktRad
from adaptere.lagring.testdata import (
    ANSATTE, HISTORIKK, PERIODE, PERIODE_SLUTT, PERIODE_START, SIST_OPPDATERT, TURNUS_ID,
)
from tester.api.test_innlogging import engine, feilsvar, klient, logg_inn  # noqa: F401

STI = "/api/vaktoversikt"


def hent(klient: TestClient) -> dict:
    logg_inn(klient)
    respons = klient.get(STI)
    assert respons.status_code == 200
    return respons.json()


def tid(tekst: str) -> datetime:
    return datetime.fromisoformat(tekst)


def test_uten_sesjon_gir_401_og_ingen_data(klient: TestClient) -> None:
    respons = klient.get(STI)

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_ugyldig_token_gir_401(klient: TestClient) -> None:
    respons = klient.get(STI, headers={"Cookie": f"{COOKIE_NAVN}=tull"})

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_hoder_og_fotnotegrunnlag(klient: TestClient) -> None:
    svar = hent(klient)

    assert set(svar) == {
        "avdeling", "periode_start", "periode_slutt", "sist_oppdatert",
        "antall_ansatte", "krever_handling", "bemannet",
    }
    assert svar["avdeling"] == "Kirurgisk sengepost"
    assert svar["periode_start"] == "2026-09-21T00:00:00+02:00"
    assert svar["periode_slutt"] == "2026-10-05T00:00:00+02:00"
    assert svar["sist_oppdatert"] == "2026-09-27T06:20:00+02:00"
    assert tid(svar["sist_oppdatert"]) == SIST_OPPDATERT
    assert svar["antall_ansatte"] == len(ANSATTE) == 25


def test_krever_handling_har_de_to_vaktene_med_meldingen(klient: TestClient) -> None:
    svar = hent(klient)

    assert svar["krever_handling"] == [
        {
            "vaktnummer": 4127,
            "vakttype": "dag",
            "start": "2026-09-27T07:00:00+02:00",
            "slutt": "2026-09-27T15:00:00+02:00",
            "satt_opp": "Silje Amundsen",
            "meldt_fra": "2026-09-27T06:14:00+02:00",
            "grunn": "sykemeldt",
        },
        {
            "vaktnummer": 4189,
            "vakttype": "natt",
            "start": "2026-09-28T23:00:00+02:00",
            "slutt": "2026-09-29T07:00:00+02:00",
            "satt_opp": "Eirik Moen",
            "meldt_fra": "2026-09-26T21:40:00+02:00",
            "grunn": "sykemeldt",
        },
    ]


def test_bemannet_har_164_vakter_med_ansatt(klient: TestClient) -> None:
    svar = hent(klient)
    bemannet = svar["bemannet"]

    assert len(bemannet) == 164 == len(PERIODE) - 2
    nummer = {v["vaktnummer"] for v in bemannet}
    assert not nummer & {4127, 4189}
    rad = next(v for v in bemannet if v["vaktnummer"] == 4128)
    assert rad == {
        "vaktnummer": 4128,
        "vakttype": "kveld",
        "start": "2026-09-27T15:00:00+02:00",
        "slutt": "2026-09-27T23:00:00+02:00",
        "ansatt": {"navn": "Per Halvorsen", "stilling": "Sykepleier", "ansiennitet": 4},
    }
    for vakt in bemannet:
        assert set(vakt["ansatt"]) == {"navn", "stilling", "ansiennitet"}


def test_sortert_etter_start_og_deretter_vaktnummer(klient: TestClient) -> None:
    svar = hent(klient)

    for liste in (svar["krever_handling"], svar["bemannet"]):
        nokler = [(tid(v["start"]), v["vaktnummer"]) for v in liste]
        assert nokler == sorted(nokler)
    # Flere vakter starter samtidig, så vaktnummeret avgjør innenfor samme start.
    starter = [v["start"] for v in svar["bemannet"]]
    assert len(set(starter)) < len(starter)


def test_periodegrensen_er_halvapen(klient: TestClient) -> None:
    svar = hent(klient)
    nummer = {v["vaktnummer"] for v in svar["bemannet"] + svar["krever_handling"]}

    # Natt 20.09 23:00–21.09 07:00 starter før perioden (AV-03).
    assert 3338 not in nummer
    assert 3339 not in nummer
    # Natt 04.10 23:00–05.10 07:00 starter i perioden.
    assert 4265 in nummer
    rad = next(v for v in svar["bemannet"] if v["vaktnummer"] == 4265)
    assert rad["start"] == "2026-10-04T23:00:00+02:00"
    assert rad["slutt"] == "2026-10-05T07:00:00+02:00"


def test_historikken_vises_ikke(klient: TestClient) -> None:
    svar = hent(klient)
    alle = svar["bemannet"] + svar["krever_handling"]
    start = tid(svar["periode_start"])
    slutt = tid(svar["periode_slutt"])

    assert not any(3000 <= v["vaktnummer"] <= 3999 for v in alle)
    assert not {v["vaktnummer"] for v in alle} & {rad[0] for rad in HISTORIKK}
    assert all(start <= tid(v["start"]) < slutt for v in alle)
    assert len(alle) == len(PERIODE) == 166


def test_ingen_mangler_bemanning_gir_tom_liste(engine: Engine, klient: TestClient) -> None:
    # Bare i testens egen database. CHECK-regelen krever at vakten har en
    # tildelt ansatt når den ikke mangler bemanning.
    with lag_sessionmaker(engine).begin() as session:
        session.execute(
            update(VaktRad)
            .where(VaktRad.vaktnummer.in_([4127, 4189]))
            .values(
                tildelt_ansatt_id=ANSATTE[0][0],
                mangler_bemanning=False,
                satt_opp_ansatt_id=None,
                meldt_fra=None,
                meldt_fra_grunn=None,
            )
        )

    svar = hent(klient)

    assert svar["krever_handling"] == []
    assert len(svar["bemannet"]) == 166
    assert {4127, 4189} <= {v["vaktnummer"] for v in svar["bemannet"]}


def test_tidene_har_offset_og_er_i_oslo(klient: TestClient) -> None:
    svar = hent(klient)
    verdier = [svar["periode_start"], svar["periode_slutt"], svar["sist_oppdatert"]]
    for vakt in svar["bemannet"]:
        verdier += [vakt["start"], vakt["slutt"]]
    for vakt in svar["krever_handling"]:
        verdier += [vakt["start"], vakt["slutt"], vakt["meldt_fra"]]

    assert len(verdier) == 3 + 2 * 164 + 3 * 2
    for tekst in verdier:
        verdi = tid(tekst)
        assert verdi.utcoffset() is not None
        assert verdi.utcoffset() == verdi.astimezone(OSLO).utcoffset()


def test_periodegrensen_ved_de_eksakte_kantene(engine: Engine, klient: TestClient) -> None:
    # Bare i testens egen database: én vakt som starter nøyaktig ved
    # periode_start (med) og én nøyaktig ved periode_slutt (ikke med).
    with lag_sessionmaker(engine).begin() as session:
        for nummer, start in ((9001, PERIODE_START), (9002, PERIODE_SLUTT)):
            session.add(
                VaktRad(
                    turnus_id=TURNUS_ID, vaktnummer=nummer, vakttype="natt",
                    start=start, slutt=start + timedelta(hours=7), minstenivå=1,
                    tildelt_ansatt_id=ANSATTE[0][0], mangler_bemanning=False,
                )
            )

    svar = hent(klient)
    nummer = [v["vaktnummer"] for v in svar["bemannet"]]

    assert 9001 in nummer
    assert 9002 not in nummer
    assert nummer[0] == 9001  # starter først i perioden


def test_rute_uten_oversikt_gir_401_og_sletter_cookie(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    logg_inn(klient)
    monkeypatch.setattr("adaptere.api.main.hent_vaktoversikt", lambda _okt, _id: None)

    respons = klient.get(STI)

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())
    assert "Max-Age=0" in respons.headers["set-cookie"]
