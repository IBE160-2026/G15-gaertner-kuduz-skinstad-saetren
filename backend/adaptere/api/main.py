"""Oppstartslaget i adaptere/api. Komposisjon av adaptere skjer her (AD-2).

`lag_app` bygger appen, slik at testene kan gi den egen nøkkel, utløpstid og
database. `app` er appen uvicorn starter, med tilfeldig nøkkel, utløpstid fra
miljøet og databasen fra `lag_engine()`.
"""

import secrets
from collections.abc import Iterator
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictStr
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from adaptere.api import sesjon
from adaptere.lagring.brukere import hent_innlogget, hent_passord_kilde, verifiser_innlogging
from adaptere.lagring.database import lag_engine, lag_sessionmaker

# Feilform etter AD-4. `melding` er fast per kode og gjentar aldri det som ble
# sendt inn. Frontend viser egen tekst etter `kode`.
MELDINGER: dict[str, str] = {
    "feil_innlogging": "Feil brukernavn eller passord.",
    "mangler_sesjon": "Ingen gyldig sesjon.",
    "ugyldig_foresporsel": "Forespørselen har feil form.",
    "ikke_funnet": "Fant ikke ressursen.",
    "metode_ikke_tillatt": "Metoden er ikke tillatt for denne ressursen.",
    "intern_feil": "Uventet feil på serveren.",
    "ukjent_feil": "Forespørselen kunne ikke behandles.",
}
RUTEKODER = {404: "ikke_funnet", 405: "metode_ikke_tillatt"}


def feil(status: int, kode: str, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"kode": kode, "melding": MELDINGER[kode]},
        headers=headers,
    )


class InnloggingInn(BaseModel):
    brukernavn: StrictStr = Field(max_length=50)  # som kolonnen i `bruker`
    passord: StrictStr = Field(max_length=256)


class InnloggetUt(BaseModel):
    navn: str
    avdeling: str


class InnloggingsinfoUt(BaseModel):
    passord_kilde: Literal["tilfeldig", "personlig"] | None


def lag_app(
    nokkel: bytes | None = None,
    minutter: int | None = None,
    engine: Engine | None = None,
) -> FastAPI:
    nokkel = nokkel or secrets.token_bytes(32)
    minutter = sesjon.les_minutter(None if minutter is None else str(minutter))
    engine = engine or lag_engine()
    okter = lag_sessionmaker(engine)

    def databaseokt() -> Iterator[Session]:
        with okter() as okt:
            yield okt

    Okt = Annotated[Session, Depends(databaseokt)]

    app = FastAPI(title="Turnushjelperen")

    @app.exception_handler(RequestValidationError)
    async def valideringsfeil(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        # Detaljene fra Pydantic inneholder det som ble sendt inn, også passordet.
        return feil(422, "ugyldig_foresporsel")

    @app.exception_handler(StarletteHTTPException)
    async def rutefeil(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return feil(exc.status_code, RUTEKODER.get(exc.status_code, "ukjent_feil"), exc.headers)

    @app.exception_handler(Exception)
    async def uventet_feil(_request: Request, _exc: Exception) -> JSONResponse:
        # Starlette sender svaret og løfter unntaket videre, så det havner i loggen.
        return feil(500, "intern_feil")

    @app.get("/api/helse")
    def helse() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/innlogging", response_model=InnloggetUt)
    def innlogging(inn: InnloggingInn, respons: Response, okt: Okt) -> InnloggetUt | JSONResponse:
        bruker = verifiser_innlogging(okt, inn.brukernavn, inn.passord)
        if bruker is None:
            return feil(401, "feil_innlogging")
        sesjon.sett_cookie(respons, sesjon.lag_token(bruker.id, nokkel, minutter), minutter)
        return InnloggetUt(navn=bruker.navn, avdeling=bruker.avdeling)

    @app.get("/api/meg", response_model=InnloggetUt)
    def meg(request: Request, okt: Okt) -> InnloggetUt | JSONResponse:
        token = sesjon.les_cookie(request)
        bruker_id = sesjon.les_token(token, nokkel) if token else None
        bruker = hent_innlogget(okt, bruker_id) if bruker_id is not None else None
        if bruker is None:
            return feil(401, "mangler_sesjon")
        return InnloggetUt(navn=bruker.navn, avdeling=bruker.avdeling)

    @app.get("/api/innloggingsinfo")
    def innloggingsinfo(okt: Okt) -> InnloggingsinfoUt:
        return InnloggingsinfoUt(passord_kilde=hent_passord_kilde(okt))

    return app


app = lag_app()
