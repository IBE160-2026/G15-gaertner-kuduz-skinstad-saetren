"""Tester for passordhash og brukeroppslag i `adaptere.lagring.brukere` (story 1.3)."""

import hashlib
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adaptere.lagring import brukere
from adaptere.lagring.brukere import (
    Innlogget,
    hash_passord,
    hent_innlogget,
    hent_passord_kilde,
    verifiser_innlogging,
)
from adaptere.lagring.database import lag_engine, lag_sessionmaker, opprett_skjema
from adaptere.lagring.modeller import BrukerRad
from adaptere.lagring.testdata import fyll_testdata, legg_til_turnusansvarlig

PASSORD = "riktig-hest-batteri"
KARI = ("Kari Vestby", "Kirurgisk sengepost")


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = lag_engine(tmp_path / "brukere.db")
    opprett_skjema(engine)
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
        legg_til_turnusansvarlig(session, PASSORD, "tilfeldig")
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with lag_sessionmaker(engine)() as session:
        yield session


@pytest.fixture
def scrypt_kall(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Teller kall til `hashlib.scrypt` mens testen kjører."""
    kall: list[int] = []
    ekte = hashlib.scrypt

    def tellende(*args, **kwargs):  # type: ignore[no-untyped-def]
        kall.append(1)
        return ekte(*args, **kwargs)

    monkeypatch.setattr(brukere.hashlib, "scrypt", tellende)
    return kall


# --- Hashing -----------------------------------------------------------------


def test_hashen_er_ikke_passordet_og_har_parametrene() -> None:
    hashet = hash_passord(PASSORD)
    assert hashet != PASSORD
    assert PASSORD not in hashet
    metode, n, r, p, salt, verdi = hashet.split("$")
    assert (metode, n, r, p) == ("scrypt", "16384", "8", "1")
    assert len(bytes.fromhex(salt)) == 16
    assert len(bytes.fromhex(verdi)) == 32


def test_samme_passord_gir_ulikt_salt_og_ulik_hash() -> None:
    a, b = hash_passord(PASSORD), hash_passord(PASSORD)
    assert a != b
    assert a.split("$")[4] != b.split("$")[4]


def test_lagret_hash_er_ikke_passordet(session: Session) -> None:
    (bruker,) = session.scalars(select(BrukerRad)).all()
    assert bruker.passord_hash.startswith("scrypt$")
    assert PASSORD not in bruker.passord_hash


# --- Innlogging --------------------------------------------------------------


def test_riktig_passord_gir_innlogget(session: Session) -> None:
    innlogget = verifiser_innlogging(session, "kari.vestby", PASSORD)
    assert isinstance(innlogget, Innlogget)
    assert (innlogget.navn, innlogget.avdeling) == KARI


@pytest.mark.parametrize(
    "brukernavn, passord",
    [
        ("kari.vestby", "feil-passord"),
        ("kari.vestby", ""),
        ("kari.vestby", PASSORD + " "),
        ("Kari.Vestby", PASSORD),
        ("ola.nordmann", PASSORD),
        ("", ""),
    ],
)
def test_feil_brukernavn_eller_passord_gir_none(session: Session, brukernavn: str, passord: str) -> None:
    assert verifiser_innlogging(session, brukernavn, passord) is None


def test_ukjent_bruker_hashes_like_mange_ganger_som_feil_passord(
    session: Session, scrypt_kall: list[int]
) -> None:
    assert verifiser_innlogging(session, "ola.nordmann", PASSORD) is None
    ukjent = len(scrypt_kall)
    scrypt_kall.clear()
    assert verifiser_innlogging(session, "kari.vestby", "feil-passord") is None
    feil_passord = len(scrypt_kall)
    assert ukjent == feil_passord == 1


def test_odelagt_hash_gir_none_og_ikke_unntak(session: Session) -> None:
    session.execute(update(BrukerRad).values(passord_hash="ikke-en-hash"))
    assert verifiser_innlogging(session, "kari.vestby", PASSORD) is None
    session.execute(update(BrukerRad).values(passord_hash="bcrypt$1$2$3$00$00"))
    assert verifiser_innlogging(session, "kari.vestby", PASSORD) is None


# --- Oppslag -----------------------------------------------------------------


def test_hent_innlogget(session: Session) -> None:
    innlogget = verifiser_innlogging(session, "kari.vestby", PASSORD)
    assert innlogget is not None
    assert hent_innlogget(session, innlogget.id) == innlogget
    assert hent_innlogget(session, innlogget.id + 1000) is None


def test_hent_passord_kilde(session: Session) -> None:
    assert hent_passord_kilde(session) == "tilfeldig"
    session.execute(update(BrukerRad).values(passord_kilde="personlig"))
    assert hent_passord_kilde(session) == "personlig"
    session.execute(delete(BrukerRad))
    assert hent_passord_kilde(session) is None


# --- Skjemaet ----------------------------------------------------------------


def test_brukernavnet_er_unikt(session: Session) -> None:
    session.add(
        BrukerRad(
            brukernavn="kari.vestby",
            navn="Duplikat",
            passord_hash=hash_passord("x"),
            passord_kilde="personlig",
            turnus_id=1,
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()


def test_ugyldig_passord_kilde_avvises(session: Session) -> None:
    session.execute(delete(BrukerRad))
    session.add(
        BrukerRad(
            brukernavn="kari.vestby",
            navn="Kari Vestby",
            passord_hash=hash_passord("x"),
            passord_kilde="klartekst",
            turnus_id=1,
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()
