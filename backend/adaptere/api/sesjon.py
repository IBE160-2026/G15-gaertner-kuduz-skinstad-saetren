"""Sesjon som ett JWT i en httpOnly-cookie (story 1.3, AD-3, OP-10).

JWT finnes bare i `adaptere/api`. Nøkkelen lages tilfeldig ved oppstart og holdes
bare i minnet, så alle logges ut når API-et starter på nytt. Utløpstiden leses fra
`TURNUSHJELPEREN_JWT_MINUTTER`, med 480 minutter (én vakt) når den mangler.
"""

import os
import re
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Request, Response

MINUTTER_VARIABEL = "TURNUSHJELPEREN_JWT_MINUTTER"
STANDARD_MINUTTER = 480
COOKIE_NAVN = "turnushjelperen_sesjon"
COOKIE_STI = "/api"
ALGORITME = "HS256"


class UgyldigUtlopstid(ValueError):
    """`TURNUSHJELPEREN_JWT_MINUTTER` er ikke et positivt heltall."""


def les_minutter(verdi: str | None = None) -> int:
    """Utløpstiden i minutter fra argumentet eller miljøet.

    En tom eller manglende verdi gir 480. Alt annet enn et positivt heltall gir
    `UgyldigUtlopstid`, slik at API-et ikke starter med en uklar innstilling.
    """
    if verdi is None:
        verdi = os.environ.get(MINUTTER_VARIABEL)
    if not verdi:
        return STANDARD_MINUTTER
    if not re.fullmatch(r"[0-9]+", verdi) or int(verdi) <= 0:
        raise UgyldigUtlopstid(
            f"{MINUTTER_VARIABEL} må være et positivt heltall (antall minutter), "
            f"men er {verdi!r}. Fjern variabelen for å bruke {STANDARD_MINUTTER} minutter."
        )
    return int(verdi)


def lag_token(bruker_id: int, nokkel: bytes, minutter: int, naa: datetime | None = None) -> str:
    """Et signert token med bare `sub`, `iat` og `exp`. Navnet hentes fra databasen."""
    naa = naa or datetime.now(UTC)
    innhold = {
        "sub": str(bruker_id),
        "iat": naa,
        "exp": naa + timedelta(minutes=minutter),
    }
    return jwt.encode(innhold, nokkel, algorithm=ALGORITME)


def les_token(token: str, nokkel: bytes) -> int | None:
    """Bruker-ID fra et gyldig token, ellers `None`.

    Bare HS256 godtas, så `alg: none` og andre algoritmer avvises. Utløpt token,
    feil nøkkel og manglende felt gir også `None`.
    """
    try:
        innhold = jwt.decode(
            token,
            nokkel,
            algorithms=[ALGORITME],
            options={"require": ["sub", "iat", "exp"]},
        )
        return int(innhold["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None


def sett_cookie(respons: Response, token: str, minutter: int) -> None:
    # Ikke Secure, fordi utviklingsserveren går over http. Vite-proxyen gir samme
    # opphav, så SameSite=Strict holder.
    respons.set_cookie(
        key=COOKIE_NAVN,
        value=token,
        max_age=minutter * 60,
        path=COOKIE_STI,
        httponly=True,
        samesite="strict",
        secure=False,
    )


def les_cookie(request: Request) -> str | None:
    return request.cookies.get(COOKIE_NAVN) or None
