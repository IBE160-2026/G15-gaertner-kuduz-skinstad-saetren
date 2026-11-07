"""Tester for innlogging, sesjon og feilform i API-et (story 1.3).

Hver test bygger appen med `lag_app` mot en database i `tmp_path`, så ingen test
rører `backend/turnushjelperen.db`.
"""

import os
import secrets
import subprocess
import sys
import warnings
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, delete, update

from adaptere.api.main import lag_app
from adaptere.api.sesjon import (
    COOKIE_NAVN,
    MINUTTER_VARIABEL,
    STANDARD_MINUTTER,
    UgyldigUtlopstid,
    lag_token,
    les_minutter,
    les_token,
)
from adaptere.lagring.database import lag_engine, lag_sessionmaker, opprett_skjema
from adaptere.lagring.modeller import BrukerRad
from adaptere.lagring.testdata import fyll_testdata, legg_til_turnusansvarlig

BACKEND = Path(__file__).resolve().parents[2]
PASSORD = "riktig-hest-batteri"
NOKKEL = b"n" * 32
KARI = {"navn": "Kari Vestby", "avdeling": "Kirurgisk sengepost"}
RIKTIG = {"brukernavn": "kari.vestby", "passord": PASSORD}


def feilsvar(kode: str) -> Callable[[dict], bool]:
    return lambda svar: set(svar) == {"kode", "melding"} and svar["kode"] == kode


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = lag_engine(tmp_path / "api.db")
    opprett_skjema(engine)
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
        legg_til_turnusansvarlig(session, PASSORD, "tilfeldig")
    yield engine
    engine.dispose()


@pytest.fixture
def klient(engine: Engine) -> TestClient:
    return TestClient(
        lag_app(nokkel=NOKKEL, minutter=STANDARD_MINUTTER, engine=engine),
        raise_server_exceptions=False,
    )


def logg_inn(klient: TestClient) -> str:
    respons = klient.post("/api/innlogging", json=RIKTIG)
    assert respons.status_code == 200
    return respons.cookies[COOKIE_NAVN]


def meg_med(klient: TestClient, token: str):  # type: ignore[no-untyped-def]
    klient.cookies.clear()
    return klient.get("/api/meg", headers={"Cookie": f"{COOKIE_NAVN}={token}"})


# --- POST /api/innlogging ----------------------------------------------------


def test_riktig_innlogging_gir_navn_og_avdeling_og_ingen_token_i_kroppen(klient: TestClient) -> None:
    respons = klient.post("/api/innlogging", json=RIKTIG)

    assert respons.status_code == 200
    assert respons.json() == KARI
    token = respons.cookies[COOKIE_NAVN]
    assert token
    assert token not in respons.text
    assert PASSORD not in respons.text


def test_cookieattributtene(klient: TestClient) -> None:
    respons = klient.post("/api/innlogging", json=RIKTIG)

    (cookie,) = respons.headers.get_list("set-cookie")
    deler = [d.strip() for d in cookie.split(";")]
    attributter = {d.split("=", 1)[0].lower(): (d.split("=", 1) + [""])[1] for d in deler[1:]}
    assert deler[0].startswith(f"{COOKIE_NAVN}=")
    assert "httponly" in attributter
    assert attributter["samesite"].lower() == "strict"
    assert attributter["path"] == "/api"
    assert attributter["max-age"] == str(STANDARD_MINUTTER * 60)
    assert "secure" not in attributter


def test_max_age_folger_utlopstiden(engine: Engine) -> None:
    klient = TestClient(lag_app(nokkel=NOKKEL, minutter=30, engine=engine))
    respons = klient.post("/api/innlogging", json=RIKTIG)
    assert "Max-Age=1800" in respons.headers["set-cookie"]
    innhold = jwt.decode(respons.cookies[COOKIE_NAVN], NOKKEL, algorithms=["HS256"])
    assert innhold["exp"] - innhold["iat"] == 1800


def test_token_like_for_utlop_godtas(klient: TestClient) -> None:
    token = logg_inn(klient)
    bruker_id = int(jwt.decode(token, NOKKEL, algorithms=["HS256"])["sub"])
    gammelt = lag_token(bruker_id, NOKKEL, 480, naa=datetime.now(UTC) - timedelta(minutes=479))

    respons = meg_med(klient, gammelt)

    assert respons.status_code == 200
    assert respons.json() == KARI


@pytest.mark.parametrize(
    "inn",
    [
        {"brukernavn": "kari.vestby", "passord": "feil-passord"},
        {"brukernavn": "ola.nordmann", "passord": PASSORD},
        {"brukernavn": "ola.nordmann", "passord": "feil-passord"},
    ],
    ids=["feil-passord", "ukjent-bruker", "begge-feil"],
)
def test_feil_innlogging_gir_samme_svar(klient: TestClient, inn: dict) -> None:
    respons = klient.post("/api/innlogging", json=inn)

    assert respons.status_code == 401
    assert feilsvar("feil_innlogging")(respons.json())
    assert "set-cookie" not in respons.headers
    assert inn["passord"] not in respons.text
    assert inn["brukernavn"] not in respons.text


def test_feil_brukernavn_og_feil_passord_gir_identisk_kropp(klient: TestClient) -> None:
    a = klient.post("/api/innlogging", json={"brukernavn": "kari.vestby", "passord": "x"})
    b = klient.post("/api/innlogging", json={"brukernavn": "ukjent", "passord": "x"})
    assert (a.status_code, a.content) == (b.status_code, b.content)


HEMMELIG = "hemmelig-passord-som-ikke-skal-lekke"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"json": {}},
        {"json": {"brukernavn": "kari.vestby"}},
        {"json": {"passord": HEMMELIG}},
        {"json": {"brukernavn": "kari.vestby", "passord": 1234567890}},
        {"json": {"brukernavn": 42, "passord": HEMMELIG}},
        {"json": {"brukernavn": "kari.vestby", "passord": None}},
        {"json": [HEMMELIG]},
        {"content": f"brukernavn=kari.vestby&passord={HEMMELIG}"},
        {"content": "{ikke json " + HEMMELIG, "headers": {"content-type": "application/json"}},
        {"json": {"brukernavn": "k" * 51, "passord": HEMMELIG}},
        {"json": {"brukernavn": "kari.vestby", "passord": HEMMELIG + "x" * (257 - len(HEMMELIG))}},
    ],
    ids=["tom", "uten-passord", "uten-brukernavn", "passord-tall", "brukernavn-tall",
         "passord-null", "liste", "skjemadata", "ugyldig-json", "brukernavn-51", "passord-257"],
)
def test_ugyldig_foresporsel_gjentar_ikke_innsendte_verdier(klient: TestClient, kwargs: dict) -> None:
    respons = klient.post("/api/innlogging", **kwargs)

    assert respons.status_code == 422
    assert feilsvar("ugyldig_foresporsel")(respons.json())
    assert HEMMELIG not in respons.text
    assert "1234567890" not in respons.text
    assert "kari.vestby" not in respons.text
    assert "k" * 51 not in respons.text


def test_lengste_tillatte_brukernavn_og_passord_gir_feil_innlogging(klient: TestClient) -> None:
    for inn in (
        {"brukernavn": "k" * 50, "passord": PASSORD},
        {"brukernavn": "kari.vestby", "passord": "p" * 256},
    ):
        respons = klient.post("/api/innlogging", json=inn)
        assert respons.status_code == 401
        assert feilsvar("feil_innlogging")(respons.json())


# --- GET /api/meg ------------------------------------------------------------


def test_gyldig_sesjon_gir_navn_og_avdeling(klient: TestClient) -> None:
    logg_inn(klient)
    respons = klient.get("/api/meg")

    assert respons.status_code == 200
    assert respons.json() == KARI


def test_uten_cookie_mangler_sesjon(klient: TestClient) -> None:
    respons = klient.get("/api/meg")

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def _alg_none(bruker_id: int) -> str:
    naa = datetime.now(UTC)
    return jwt.encode(
        {"sub": str(bruker_id), "iat": naa, "exp": naa + timedelta(hours=1)},
        None,
        algorithm="none",
    )


def _hs512(bruker_id: int) -> str:
    """Riktig nøkkel, men en annen algoritme enn HS256."""
    naa = datetime.now(UTC)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", jwt.warnings.InsecureKeyLengthWarning)
        return jwt.encode(
            {"sub": str(bruker_id), "iat": naa, "exp": naa + timedelta(hours=1)},
            NOKKEL,
            algorithm="HS512",
        )


@pytest.mark.parametrize(
    "lag",
    [
        lambda i: lag_token(i, NOKKEL, 480, naa=datetime.now(UTC) - timedelta(minutes=481)),
        lambda i: lag_token(i, b"a" * 32, 480),
        _alg_none,
        lambda i: jwt.encode({"sub": str(i), "iat": datetime.now(UTC)}, NOKKEL, algorithm="HS256"),
        lambda i: jwt.encode(
            {"sub": "kari", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(hours=1)},
            NOKKEL,
            algorithm="HS256",
        ),
        _hs512,
        lambda i: lag_token(i + 1000, NOKKEL, 480),
        lambda i: "ikke.et.token",
        lambda i: lag_token(i, NOKKEL, 480)[:-4] + "AAAA",
    ],
    ids=["utlopt", "feil-nokkel", "alg-none", "uten-exp", "sub-ikke-tall", "hs512",
         "bruker-finnes-ikke", "soppel", "endret-signatur"],
)
def test_ugyldig_sesjon_mangler_sesjon(klient: TestClient, lag: Callable[[int], str]) -> None:
    logg_inn(klient)
    bruker_id = int(jwt.decode(klient.cookies[COOKIE_NAVN], NOKKEL, algorithms=["HS256"])["sub"])

    respons = meg_med(klient, lag(bruker_id))

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_token_for_slettet_bruker_mangler_sesjon(klient: TestClient, engine: Engine) -> None:
    token = logg_inn(klient)
    assert meg_med(klient, token).status_code == 200
    with lag_sessionmaker(engine).begin() as session:
        session.execute(delete(BrukerRad))

    respons = meg_med(klient, token)

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_navnet_hentes_fra_databasen_og_ikke_fra_tokenet(klient: TestClient, engine: Engine) -> None:
    token = logg_inn(klient)
    innhold = jwt.decode(token, NOKKEL, algorithms=["HS256"])
    assert set(innhold) == {"sub", "iat", "exp"}
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(BrukerRad).values(navn="Kari Vestby-Nilsen"))

    assert meg_med(klient, token).json()["navn"] == "Kari Vestby-Nilsen"


def test_omstart_gir_ny_nokkel_og_logger_ut(engine: Engine) -> None:
    foer = TestClient(lag_app(minutter=STANDARD_MINUTTER, engine=engine))
    token = logg_inn(foer)
    assert meg_med(foer, token).status_code == 200

    etter = TestClient(lag_app(minutter=STANDARD_MINUTTER, engine=engine))
    respons = meg_med(etter, token)

    assert respons.status_code == 401
    assert feilsvar("mangler_sesjon")(respons.json())


def test_ny_nokkel_godtar_ikke_token_fra_en_annen() -> None:
    a, b = secrets.token_bytes(32), secrets.token_bytes(32)
    token = lag_token(1, a, 480)
    assert les_token(token, a) == 1
    assert les_token(token, b) is None


# --- GET /api/innloggingsinfo ------------------------------------------------


def test_innloggingsinfo_tilfeldig(klient: TestClient) -> None:
    respons = klient.get("/api/innloggingsinfo")
    assert respons.status_code == 200
    assert respons.json() == {"passord_kilde": "tilfeldig"}
    assert PASSORD not in respons.text


def test_innloggingsinfo_personlig(klient: TestClient, engine: Engine) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(update(BrukerRad).values(passord_kilde="personlig"))
    assert klient.get("/api/innloggingsinfo").json() == {"passord_kilde": "personlig"}


def test_innloggingsinfo_uten_bruker(klient: TestClient, engine: Engine) -> None:
    with lag_sessionmaker(engine).begin() as session:
        session.execute(delete(BrukerRad))
    respons = klient.get("/api/innloggingsinfo")
    assert respons.status_code == 200
    assert respons.json() == {"passord_kilde": None}


# --- Feilform for ruting og uventede feil ------------------------------------


def test_ukjent_sti_gir_ikke_funnet(klient: TestClient) -> None:
    respons = klient.get("/api/finnes-ikke")
    assert respons.status_code == 404
    assert feilsvar("ikke_funnet")(respons.json())


def test_feil_metode_gir_metode_ikke_tillatt(klient: TestClient) -> None:
    respons = klient.put("/api/innlogging", json=RIKTIG)
    assert respons.status_code == 405
    assert feilsvar("metode_ikke_tillatt")(respons.json())
    assert "POST" in respons.headers["allow"]
    assert PASSORD not in respons.text


def test_uten_testdata_gir_intern_feil(tmp_path: Path) -> None:
    # Databasen finnes, men testdatakommandoen er ikke kjørt, så `bruker` mangler.
    engine = lag_engine(tmp_path / "tom.db")
    try:
        klient = TestClient(lag_app(nokkel=NOKKEL, engine=engine), raise_server_exceptions=False)
        for respons in (
            klient.post("/api/innlogging", json=RIKTIG),
            klient.get("/api/innloggingsinfo"),
        ):
            assert respons.status_code == 500
            assert feilsvar("intern_feil")(respons.json())
            assert PASSORD not in respons.text
    finally:
        engine.dispose()


def test_helsesjekk_i_lag_app(klient: TestClient) -> None:
    assert klient.get("/api/helse").json() == {"status": "ok"}


# --- Utløpstiden -------------------------------------------------------------


@pytest.mark.parametrize("verdi, forventet", [(None, 480), ("", 480), ("30", 30), ("1", 1), ("0480", 480)])
def test_gyldig_utlopstid(monkeypatch: pytest.MonkeyPatch, verdi: str | None, forventet: int) -> None:
    if verdi is None:
        monkeypatch.delenv(MINUTTER_VARIABEL, raising=False)
    else:
        monkeypatch.setenv(MINUTTER_VARIABEL, verdi)
    assert les_minutter() == forventet


@pytest.mark.parametrize("verdi", ["abc", "0", "-5", "1.5", " 30", "30m", "+30", "000"])
def test_ugyldig_utlopstid_stopper_lag_app(
    monkeypatch: pytest.MonkeyPatch, engine: Engine, verdi: str
) -> None:
    monkeypatch.setenv(MINUTTER_VARIABEL, verdi)
    with pytest.raises(UgyldigUtlopstid, match="positivt heltall"):
        lag_app(engine=engine)


def test_api_et_starter_ikke_med_ugyldig_utlopstid(tmp_path: Path) -> None:
    miljo = {
        **os.environ,
        MINUTTER_VARIABEL: "abc",
        "TURNUSHJELPEREN_DB": str(tmp_path / "start.db"),
        "PYTHONUTF8": "1",
    }
    resultat = subprocess.run(
        [sys.executable, "-c", "import adaptere.api.main"],
        cwd=BACKEND, env=miljo, capture_output=True, text=True, encoding="utf-8",
    )
    assert resultat.returncode != 0
    assert f"{MINUTTER_VARIABEL} må være et positivt heltall" in resultat.stderr
