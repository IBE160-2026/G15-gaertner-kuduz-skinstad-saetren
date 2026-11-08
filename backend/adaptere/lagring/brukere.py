"""Passordhash og oppslag av turnusansvarlig (story 1.3).

Hashing og brukeroppslag skjer bare her (AD-3). API-et sender passordet videre
til `verifiser_innlogging` og lagrer aldri en hash selv.

Hashformat: `scrypt$<n>$<r>$<p>$<salt-hex>$<hash-hex>`. Parametrene står i
hashen, slik at de kan endres senere uten å ugyldiggjøre gamle hasher.
"""

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptere.lagring.modeller import BrukerRad, TurnusRad

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16
HASH_BYTES = 32


@dataclass(frozen=True)
class Innlogget:
    id: int
    navn: str
    avdeling: str


def _scrypt(passord: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        passord.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=HASH_BYTES
    )


def hash_passord(passord: str) -> str:
    """Hasher passordet med scrypt og et tilfeldig salt."""
    salt = secrets.token_bytes(SALT_BYTES)
    hashet = _scrypt(passord, salt, SCRYPT_N, SCRYPT_R, SCRYPT_P)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${hashet.hex()}"


def _stemmer(passord: str, lagret: str) -> bool:
    try:
        metode, n, r, p, salt_hex, hash_hex = lagret.split("$")
        if metode != "scrypt":
            return False
        salt, forventet = bytes.fromhex(salt_hex), bytes.fromhex(hash_hex)
        beregnet = _scrypt(passord, salt, int(n), int(r), int(p))
    except ValueError:
        return False
    return hmac.compare_digest(beregnet, forventet)


# Ukjent bruker sjekkes mot denne, slik at feil brukernavn tar omtrent like lang
# tid som feil passord. Passordet bak er tilfeldig og finnes bare i minnet.
_DUMMY_HASH = hash_passord(secrets.token_urlsafe(16))


def verifiser_innlogging(session: Session, brukernavn: str, passord: str) -> Innlogget | None:
    """Brukeren når brukernavn og passord stemmer, ellers `None`.

    Feil brukernavn og feil passord gir samme svar. Passordet hashes i begge
    tilfeller.
    """
    rad = session.execute(
        select(BrukerRad, TurnusRad.avdeling)
        .join(TurnusRad, BrukerRad.turnus_id == TurnusRad.id)
        .where(BrukerRad.brukernavn == brukernavn)
    ).first()
    if rad is None:
        _stemmer(passord, _DUMMY_HASH)
        return None
    bruker, avdeling = rad
    if not _stemmer(passord, bruker.passord_hash):
        return None
    return Innlogget(id=bruker.id, navn=bruker.navn, avdeling=avdeling)


def hent_innlogget(session: Session, bruker_id: int) -> Innlogget | None:
    """Brukeren med denne ID-en, eller `None` hvis den ikke finnes lenger."""
    rad = session.execute(
        select(BrukerRad.id, BrukerRad.navn, TurnusRad.avdeling)
        .join(TurnusRad, BrukerRad.turnus_id == TurnusRad.id)
        .where(BrukerRad.id == bruker_id)
    ).first()
    if rad is None:
        return None
    return Innlogget(id=rad.id, navn=rad.navn, avdeling=rad.avdeling)


def hent_passord_kilde(session: Session) -> str | None:
    """`"tilfeldig"` eller `"personlig"` for turnusansvarlig, `None` uten bruker."""
    return session.scalar(
        select(BrukerRad.passord_kilde).order_by(BrukerRad.id).limit(1)
    )
