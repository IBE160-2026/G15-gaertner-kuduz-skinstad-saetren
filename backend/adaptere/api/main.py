"""Oppstartslaget i adaptere/api. Komposisjon av adaptere skjer her (AD-2).

`lag_app` bygger appen, slik at testene kan gi den egen nøkkel, utløpstid,
database og KI-adapter. `app` er appen uvicorn starter, med tilfeldig nøkkel,
utløpstid fra miljøet, databasen fra `lag_engine()` og KI-adapteren fra
`ki_fra_miljo()`. Bare `app` leser KI-konfigurasjonen fra miljøet.
"""

from _thread import LockType
import logging
import os
import secrets
import sys
import threading
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal, TextIO

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictStr
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException as StarletteHTTPException

from adaptere.api import sesjon
from adaptere.ki.avveining import Retning, faktorretninger
from adaptere.ki.openrouter import STANDARD_MODELL, Forklarer, OpenRouterKiAdapter, Tolker, leverandør
from adaptere.lagring.brukere import hent_innlogget, hent_passord_kilde, verifiser_innlogging
from adaptere.lagring.database import lag_engine, lag_sessionmaker
from adaptere.lagring.kandidatgrunnlag import hent_kandidatgrunnlag, kandidatmerke
from adaptere.lagring.godkjenninger import lagre_godkjenning
from adaptere.lagring.modeller import OSLO, AnsattRad
from adaptere.lagring.preferansetolkning import lagre_resultat, ventende_tekster, les_tolkning, tilstandsmerke
from adaptere.lagring.vaktdetaljer import hent_vaktdetaljer
from adaptere.lagring.vaktoversikt import hent_vaktoversikt
from domene.porter.rangering import RangertKandidat, TolketPreferanse
from domene.porter.utelukkelse import UtelukkelsesOppsummering
from domene.regelmotor.kostnad import beregn_kostnad
from domene.regelmotor.rangering import ranger
from domene.regelmotor.timebelastning import timebelastning
from domene.regelmotor.timer_i_uka import minutter_i_uka, timer_i_startuka
from domene.regelmotor.vurdering import lag_utelukkelsesoppsummering, vurder_kandidater
from domene.typer import Datafeil, Godkjenning, Kandidat, Kandidatvurdering, Ulempebelastning, Vakt

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
    "endret_grunnlag": "Beslutningsgrunnlaget er endret.",
    "ugyldig_kandidat": "Kandidaten kan ikke godkjennes for denne vakten.",
    "ki_utilgjengelig": "Preferansetolkning er ikke tilgjengelig.",
    "tolkning_paagar": "Preferansen tolkes allerede.",
    "ikke_feilet": "Preferansen har ikke en gyldig feilstatus.",
    "allerede_bemannet": "Vakten er allerede bemannet.",
}
RUTEKODER = {404: "ikke_funnet", 405: "metode_ikke_tillatt"}

logger = logging.getLogger(__name__)

TERMINALFORMAT = "%(levelname)s:     %(message)s"  # INFO-linjene ser ut som uvicorns egne
TERMINALMERKE = "_turnushjelperen_terminal"


class _Terminalhandler(logging.StreamHandler):  # type: ignore[type-arg]
    """StreamHandler som slår opp `sys.stderr` ved hver post når ingen strøm er gitt.

    Da skriver den til gjeldende stderr også når pytest bytter den ut etter at
    modulen er importert, slik `logging.lastResort` gjør.
    """

    def __init__(self, strøm: TextIO | None = None) -> None:
        super().__init__(strøm)
        self._strøm = strøm

    @property  # type: ignore[override]
    def stream(self) -> TextIO:
        return self._strøm if self._strøm is not None else sys.stderr

    @stream.setter
    def stream(self, verdi: TextIO | None) -> None:
        self._strøm = verdi


def vis_applogg_i_terminalen(strøm: TextIO | None = None) -> logging.Handler:
    """Gir loggeren `adaptere` én terminalhandler på INFO, slik at fremdriften synes.

    Uten oppsett viser Python bare WARNING og høyere fra appens loggere. Rotloggeren
    og uvicorns loggere røres ikke, og `propagate` forblir `True`, så pytests
    `caplog` fanger postene som før. Handleren er merket, så gjentatte kall, også
    etter `importlib.reload`, legger ikke til en ny. `strøm` er for testene; uten
    den skrives det til gjeldende `sys.stderr`.
    """
    applogger = logging.getLogger("adaptere")
    applogger.setLevel(logging.INFO)
    for handler in applogger.handlers:
        if getattr(handler, TERMINALMERKE, False):
            return handler
    handler = _Terminalhandler(strøm)
    setattr(handler, TERMINALMERKE, True)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(TERMINALFORMAT))
    applogger.addHandler(handler)
    return handler


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


Vakttype = Literal["dag", "mellom", "kveld", "natt"]


class AnsattUt(BaseModel):
    navn: str
    stilling: str
    ansiennitet: int


class ManglerBemanningUt(BaseModel):
    vaktnummer: int
    vakttype: Vakttype
    start: datetime
    slutt: datetime
    satt_opp: str | None
    meldt_fra: datetime | None
    grunn: str | None


class BemannetUt(BaseModel):
    vaktnummer: int
    vakttype: Vakttype
    start: datetime
    slutt: datetime
    ansatt: AnsattUt


class VaktoversiktUt(BaseModel):
    """Bare data. Tekst og formatering lages i frontend (story 1.5).

    Tidspunktene er i Europe/Oslo og sendes som ISO 8601 med offset.
    """

    avdeling: str
    periode_start: datetime
    periode_slutt: datetime
    sist_oppdatert: datetime
    antall_ansatte: int
    krever_handling: list[ManglerBemanningUt]
    bemannet: list[BemannetUt]


class VaktdetaljerUt(BaseModel):
    avdeling: str
    vaktnummer: int
    vakttype: Vakttype
    start: datetime
    slutt: datetime
    minstenivå: int


class UlempebelastningUt(BaseModel):
    dagtimer: float
    kveldstimer: float
    helgetimer: float
    natttimer: float
    poeng: float
    score: float


class KostnadUt(BaseModel):
    total: float
    ordinære_timer: float
    overtidstimer: float
    ordinær_sats: float
    overtidssats: float


class KandidatUt(BaseModel):
    id: int
    navn: str
    # Nivået for Vaktens vakttype, 1–4. Vises som tag (UX-DR11).
    kompetansenivå: int
    # Hele minutter i uka Vakten starter i, uten Vakten selv (FR8, P-02, story 4.1).
    minutter_i_uka: int
    # Prosent av 36 t (uavrundet, ikke kuttet) og om uavrundet tid er minst 32,4 t (story 4.2, P-04).
    timebelastning_prosent: float
    hoy_belastning: bool
    ulempebelastning: UlempebelastningUt
    kostnad: KostnadUt


Tolkestatus = Literal["tolket", "venter_paa_tolkning", "kunne_ikke_tolkes", "ingen_registrert"]


class FaktorpoengUt(BaseModel):
    """Faktorpoengene 0–100, uavrundet (K-03). Preferansen står i `preferansepoeng`."""

    kostnad: float
    timebelastning: float
    ulempe: float


class RangertKandidatUt(KandidatUt):
    """En Gyldig kandidat i Rangeringen (story 4.4, FR9): `KandidatUt` med plass og poeng.

    Lages bare fra `RangertKandidat` fra regelmotoren. `totalscore` og poengene er
    uavrundet, og frontend avrunder ved visning. `preferansekategori` er satt bare
    når `tolkestatus` er `tolket`.
    """

    stilling: str
    ansiennitet: int
    plass: int
    totalscore: float
    faktorpoeng: FaktorpoengUt
    preferansepoeng: float
    tolkestatus: Tolkestatus
    preferansekategori: str | None
    grunnlagsmerke: str
    faktorretninger: dict[str, Retning]


def belastning(kandidat: Kandidat, vakt: Vakt) -> dict[str, float | bool]:
    """Feltene for timebelastning, regnet fra uavrundet tid (story 4.2)."""
    b = timebelastning(timer_i_startuka(kandidat, vakt))
    return {"timebelastning_prosent": b.prosent, "hoy_belastning": b.høy}


def rangert_ut(rangert: RangertKandidat, kandidat: Kandidat, vakt: Vakt, ulempe: Ulempebelastning,
               merke: str) -> RangertKandidatUt:
    """`KandidatUt`-feltene, regnet som før, pluss Rangeringens plass og poeng."""
    return RangertKandidatUt(
        grunnlagsmerke=merke, faktorretninger=faktorretninger(rangert),
        id=rangert.id, navn=rangert.navn, kompetansenivå=rangert.kompetansenivå,
        minutter_i_uka=minutter_i_uka(kandidat, vakt),
        **belastning(kandidat, vakt),
        kostnad=KostnadUt.model_validate(beregn_kostnad(kandidat, vakt), from_attributes=True),
        ulempebelastning=UlempebelastningUt.model_validate(ulempe, from_attributes=True),
        stilling=rangert.stilling, ansiennitet=rangert.ansiennitet, plass=rangert.plass,
        totalscore=rangert.totalscore,
        faktorpoeng=FaktorpoengUt(
            kostnad=rangert.kostnadspoeng, timebelastning=rangert.timebelastningspoeng,
            ulempe=rangert.ulempescore,
        ),
        preferansepoeng=rangert.preferansepoeng, tolkestatus=rangert.tolkestatus.value,
        preferansekategori=rangert.tolket_preferanse.kategori if rangert.tolket_preferanse else None,
    )


class RegelAntallUt(BaseModel):
    årsak: str
    antall: int


class EkskludertKandidatUt(BaseModel):
    id: int
    navn: str
    årsaker: tuple[str, ...]


class UtelukkelsesOppsummeringUt(BaseModel):
    """Ekskludert-boksen (UX-DR15): totalt, per hard regel og hele listen."""

    totalt: int
    per_regel: tuple[RegelAntallUt, ...]
    utelukkede: tuple[EkskludertKandidatUt, ...]


class KandidaterUt(BaseModel):
    """Bare Gyldige kandidater, sortert etter plass i Rangeringen (NFR2, FR9).
    `utelukkelser` dekker resten.

    Alltid minst én Kandidat: null Gyldige gir `IngenGyldigeUt` (FR6, AD-4).
    """

    status: Literal["ok"]
    kandidater: list[RangertKandidatUt]
    utelukkelser: UtelukkelsesOppsummeringUt


class IngenGyldigeUt(BaseModel):
    """Vurderingen er fullført og alle er utelukket (FR6, P-11). `kandidater` er alltid tom.

    Ikke en feil og ikke en datafeil: datafeil har ingen liste, fordi ingen er vurdert.
    """

    status: Literal["ingen_gyldige_kandidater"]
    kandidater: list[RangertKandidatUt]
    utelukkelser: UtelukkelsesOppsummeringUt


class GodkjenningsgrunnlagUt(BaseModel):
    """Vakten og én Gyldig kandidat for godkjenningsflaten (story 3.1, FR12).

    Bare lesing. Utelukkede, ukjente og opprinnelig oppsatte Ansatte gir 404, uten at svaret sier
    hvorfor (NFR2).
    """

    status: Literal["ok"]
    vakt: VaktdetaljerUt
    kandidat: RangertKandidatUt
    topprangert: RangertKandidatUt | None
    grunnlagsmerke: str


class GodkjenningInn(BaseModel):
    grunnlagsmerke: StrictStr = Field(min_length=64, max_length=64)


class GodkjenningUt(BaseModel):
    status: Literal["godkjent"]


class DatafeilUt(BaseModel):
    """Grunnlaget mangler eller er ugyldig, så ingen Kandidat er vurdert (P-08).

    Et 200-svar, ikke en feil: vurderingen har kjørt og stoppet med vilje. Frontend
    viser egen tekst ut fra `status` og `kode` og oppgir datagrensen.
    """

    status: Literal["datafeil"]
    kode: Literal["mangler_turnusgrunnlag"]
    datagrense: datetime


class AvveiningFeiletUt(BaseModel):
    status: Literal["avveining_feilet"] = "avveining_feilet"
    vaktnummer: int
    kandidat_id: int
    grunnlagsmerke: str


class AvveiningUt(BaseModel):
    status: Literal["ok"] = "ok"
    vaktnummer: int
    kandidat_id: int
    grunnlagsmerke: str
    ki_kilde: Literal["live"] = "live"
    modell: str
    paastander: list[str]


@dataclass
class RangertGrunnlag:
    vakt: Vakt
    avdeling: str
    vurdering: Kandidatvurdering
    rangert: tuple[RangertKandidat, ...]
    gyldige: dict[int, Kandidat]
    avtrykk: str
    bruker_id: int

    def merke(self, id: int) -> str:
        return kandidatmerke(self.avtrykk, self.bruker_id, self.vakt.vaktnummer, id)

    def rad(self, r: RangertKandidat) -> RangertKandidatUt:
        return rangert_ut(r, self.gyldige[r.id], self.vakt, self.vurdering.ulempe_per_kandidat[r.id], self.merke(r.id))


def les_rangering(okt: Session, bruker_id: int, vaktnummer: int) -> RangertGrunnlag | DatafeilUt | JSONResponse:
    okt.connection().exec_driver_sql("BEGIN")
    grunnlag = hent_kandidatgrunnlag(okt, bruker_id, vaktnummer)
    if grunnlag is None:
        return feil(404, "ikke_funnet")
    vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
    if isinstance(vurdering, Datafeil):
        logger.warning("Datafeil for vakt %s: %s", vaktnummer, "; ".join(vurdering.grunner))
        return DatafeilUt(status="datafeil", kode="mangler_turnusgrunnlag", datagrense=vurdering.datagrense)
    return RangertGrunnlag(
        grunnlag.vakt, grunnlag.avdeling, vurdering, ranger(vurdering, grunnlag.vakt, grunnlag.tolkede, grunnlag.feilede),
        {k.id: k for k in vurdering.gyldige}, grunnlag.avtrykk, bruker_id,
    )


KI_MODUSER = ("openrouter", "demo")
TOLKETRÅD = "preferansetolkning"


def ki_fra_miljo() -> Tolker | None:
    """KI-adapteren fra miljøet, eller None når preferansetolkningen er av (AD-6, story 5.1).

    `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (tom gir `openai/gpt-6-luna`) og
    `KI_MODUS` (`openrouter` | `demo`, tom gir `openrouter`). Mangler nøkkelen, er
    modus `demo` eller ukjent, eller har modellen feil form, logges én WARNING og
    ingen tolkning startes. `DemoKiAdapter` kommer i story 5.7. Brukes bare for
    modulobjektet `app`; nøkkelen logges aldri.
    """
    modus = os.environ.get("KI_MODUS", "").strip() or "openrouter"
    nøkkel = os.environ.get("OPENROUTER_API_KEY", "").strip()
    modell = os.environ.get("OPENROUTER_MODEL", "").strip() or STANDARD_MODELL
    if modus not in KI_MODUSER:
        grunn = "KI_MODUS er ukjent (gyldig: openrouter, demo)"
    elif modus == "demo":
        grunn = "KI_MODUS er demo, og demo-modus er ikke bygget ennå"
    elif not nøkkel:
        grunn = "OPENROUTER_API_KEY er ikke satt"
    elif not nøkkel.isascii() or not nøkkel.isprintable():
        # http.client gjengir headerverdien i feilmeldingen, så nøkkelen kunne havnet i loggen.
        grunn = "OPENROUTER_API_KEY har ugyldige tegn"
    else:
        try:
            leverandør(modell)
        except ValueError:
            grunn = "OPENROUTER_MODEL må ha formen <leverandør>/<modell>"
        else:
            return OpenRouterKiAdapter(nøkkel, modell)
    logger.warning("Preferansetolkning er av: %s. Se README.", grunn)
    return None


def tolk_ventende(okter: sessionmaker[Session], ki: Tolker, laaser: dict[int, LockType] | None = None, vakt: LockType | None = None) -> None:
    """Tolker alle ventende tekster én gang og lagrer sluttresultatet per tekst (story 5.1).

    Synkron. Leser listen i én kort økt og holder ingen transaksjon åpen under
    KI-kallene. Er teksten endret mens kallet pågikk, forkastes resultatet. En
    uventet feil for én tekst logges, og de andre tolkes videre.
    """
    try:
        with okter() as okt:
            ventende = [(ansatt_id, tekst, tilstandsmerke(okt.get(AnsattRad, ansatt_id)))
                        for ansatt_id, tekst in ventende_tekster(okt)]
    except Exception:
        logger.exception(
            "Preferansetolkning stoppet: kunne ikke lese ansatt-tabellen. Er databasen fra før "
            "story 5.1? Slett den og last testdata på nytt."
        )
        return
    if ventende:
        logger.info("Preferansetolkning: %d tekster venter.", len(ventende))
    laaser = laaser if laaser is not None else {}
    vakt = vakt if vakt is not None else threading.Lock()
    for ansatt_id, tekst, forventet in ventende:
        with vakt:
            laas = laaser.setdefault(ansatt_id, threading.Lock())
        if not laas.acquire(blocking=False):
            continue
        try:
            with okter() as okt:
                rad = okt.get(AnsattRad, ansatt_id)
                if rad is None or rad.preferanse != tekst or tilstandsmerke(rad) != forventet or isinstance(les_tolkning(rad), TolketPreferanse):
                    continue
            resultat = ki.tolk(tekst)
            verdi = resultat if isinstance(resultat, TolketPreferanse) else resultat.feiltype
            if not lagre_resultat(okter, ansatt_id, tekst, verdi, forventet):
                logger.info("Preferansetolkning for ansatt %s forkastet: teksten er endret.", ansatt_id)
            elif isinstance(verdi, TolketPreferanse):
                logger.info("Preferansetolkning for ansatt %s: tolket.", ansatt_id)
            else:
                logger.warning("Preferansetolkning for ansatt %s: kunne ikke tolkes (%s).", ansatt_id, verdi)
        except Exception:
            logger.exception("Preferansetolkning for ansatt %s feilet uventet.", ansatt_id)
        finally:
            laas.release()


def lag_app(
    nokkel: bytes | None = None,
    minutter: int | None = None,
    engine: Engine | None = None,
    ki: Tolker | None = None,
) -> FastAPI:
    """`ki=None` starter aldri tolkning. Med `ki` tolkes ventende tekster i en
    daemon-tråd når appen starter (lifespan), og appen kan brukes imens."""
    nokkel = nokkel or secrets.token_bytes(32)
    minutter = sesjon.les_minutter(None if minutter is None else str(minutter))
    engine = engine or lag_engine()
    okter = lag_sessionmaker(engine)
    tolkelaaser: dict[int, LockType] = {}
    laasevakt = threading.Lock()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if ki is not None:
            tråd = threading.Thread(target=tolk_ventende, args=(okter, ki, tolkelaaser, laasevakt), name=TOLKETRÅD, daemon=True)
            app.state.tolketråd = tråd
            tråd.start()
        yield

    def databaseokt() -> Iterator[Session]:
        with okter() as okt:
            yield okt

    Okt = Annotated[Session, Depends(databaseokt)]

    app = FastAPI(
        title="Turnushjelperen", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan,
    )
    app.state.tolketråd = None
    app.state.ki = ki

    offentlige_ruter = {
        ("GET", "/api/helse"),
        ("POST", "/api/innlogging"),
        ("GET", "/api/innloggingsinfo"),
    }

    @app.middleware("http")
    async def krev_sesjon(request: Request, call_next):  # type: ignore[no-untyped-def]
        # Autoriser før ruting: også ukjente API-stier og feil metoder er beskyttet.
        if (request.url.path == "/api" or request.url.path.startswith("/api/")) and (request.method, request.url.path) not in offentlige_ruter:
            token = sesjon.les_cookie(request)
            bruker_id = sesjon.les_token(token, nokkel) if token else None
            with okter() as okt:
                bruker = hent_innlogget(okt, bruker_id) if bruker_id is not None else None
            if bruker is None:
                respons = feil(401, "mangler_sesjon")
                sesjon.slett_cookie(respons)
                return respons
            request.state.bruker = bruker
        return await call_next(request)

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
    def meg(request: Request) -> InnloggetUt:
        bruker = request.state.bruker
        return InnloggetUt(navn=bruker.navn, avdeling=bruker.avdeling)

    @app.get("/api/vaktoversikt", response_model=VaktoversiktUt)
    def vaktoversikt(request: Request, okt: Okt) -> VaktoversiktUt | JSONResponse:
        # Vernet har allerede sjekket at brukeren og turnusen finnes. `None` her
        # betyr at brukeren ble slettet mellom vernet og spørringen.
        oversikt = hent_vaktoversikt(okt, request.state.bruker.id)
        if oversikt is None:
            respons = feil(401, "mangler_sesjon")
            sesjon.slett_cookie(respons)
            return respons
        return VaktoversiktUt.model_validate(oversikt, from_attributes=True)

    @app.get("/api/vakter/{vaktnummer}", response_model=VaktdetaljerUt)
    def vaktdetaljer(vaktnummer: int, request: Request, okt: Okt) -> VaktdetaljerUt | JSONResponse:
        detaljer = hent_vaktdetaljer(okt, request.state.bruker.id, vaktnummer)
        if detaljer is None:
            return feil(404, "ikke_funnet")
        return VaktdetaljerUt.model_validate(detaljer, from_attributes=True)

    @app.get("/api/vakter/{vaktnummer}/kandidater", response_model=KandidaterUt | IngenGyldigeUt | DatafeilUt)
    def kandidater(
        vaktnummer: int, request: Request, okt: Okt,
    ) -> KandidaterUt | IngenGyldigeUt | DatafeilUt | JSONResponse:
        grunnlag = les_rangering(okt, request.state.bruker.id, vaktnummer)
        if not isinstance(grunnlag, RangertGrunnlag):
            return grunnlag
        oppsummering: UtelukkelsesOppsummering = lag_utelukkelsesoppsummering(grunnlag.vurdering)
        utelukkelser = UtelukkelsesOppsummeringUt.model_validate(oppsummering, from_attributes=True)
        if not grunnlag.rangert:
            return IngenGyldigeUt(status="ingen_gyldige_kandidater", kandidater=[], utelukkelser=utelukkelser)
        return KandidaterUt(status="ok", kandidater=[grunnlag.rad(r) for r in grunnlag.rangert],
                            utelukkelser=utelukkelser)

    @app.get("/api/vakter/{vaktnummer}/kandidater/{ansatt_id}/avveining",
             response_model=AvveiningUt | AvveiningFeiletUt | DatafeilUt)
    def avveining(vaktnummer: int, ansatt_id: int, request: Request):
        with okter() as okt:
            grunnlag = les_rangering(okt, request.state.bruker.id, vaktnummer)
            if not isinstance(grunnlag, RangertGrunnlag):
                return grunnlag
            valgt = next((r for r in grunnlag.rangert if r.id == ansatt_id), None)
            if valgt is None:
                return feil(404, "ikke_funnet")
            andre = (r for r in grunnlag.rangert if r.id != ansatt_id)
            referanse = next(andre, None)
            identitet = dict(vaktnummer=vaktnummer, kandidat_id=ansatt_id, grunnlagsmerke=grunnlag.merke(ansatt_id))
        # Slipp lesetransaksjonen før venting og nettverkskall.
        if isinstance(ki, Forklarer):
            paastander = ki.forklar(valgt, referanse)
            if paastander:
                return AvveiningUt(**identitet, modell=ki.modell, paastander=paastander)
        return AvveiningFeiletUt(**identitet)

    @app.post("/api/vakter/{vaktnummer}/kandidater/{ansatt_id}/preferanse", response_model=None)
    def prov_preferanse(vaktnummer: int, ansatt_id: int, request: Request) -> dict[str, str] | JSONResponse:
        # Do not disclose whether another request is running before checking access.
        with okter() as okt:
            okt.connection().exec_driver_sql("BEGIN")
            grunnlag = hent_kandidatgrunnlag(okt, request.state.bruker.id, vaktnummer)
            if grunnlag is None:
                return feil(404, "ikke_funnet")
            vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
            if isinstance(vurdering, Datafeil) or not any(k.id == ansatt_id for k in vurdering.gyldige):
                return feil(404, "ikke_funnet")
        with laasevakt:
            laas = tolkelaaser.setdefault(ansatt_id, threading.Lock())
        if not laas.acquire(blocking=False):
            return feil(409, "tolkning_paagar")
        try:
            with okter() as okt:
                okt.connection().exec_driver_sql("BEGIN")
                grunnlag = hent_kandidatgrunnlag(okt, request.state.bruker.id, vaktnummer)
                if grunnlag is None:
                    return feil(404, "ikke_funnet")
                vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
                if isinstance(vurdering, Datafeil) or not any(k.id == ansatt_id for k in vurdering.gyldige):
                    return feil(404, "ikke_funnet")
                rad = okt.get(AnsattRad, ansatt_id)
                if rad is None or les_tolkning(rad) != "feilet" or rad.preferanse is None:
                    return feil(409, "ikke_feilet")
                tekst = rad.preferanse
                forventet = tilstandsmerke(rad)
            if ki is None:
                return feil(503, "ki_utilgjengelig")
            resultat = ki.tolk(tekst)
            verdi = resultat if isinstance(resultat, TolketPreferanse) else resultat.feiltype
            lagret = lagre_resultat(okter, ansatt_id, tekst, verdi, forventet)
            return {"status": "endret" if not lagret else "tolket" if isinstance(verdi, TolketPreferanse) else "feilet"}
        finally:
            laas.release()

    @app.get(
        "/api/vakter/{vaktnummer}/kandidater/{ansatt_id}",
        response_model=GodkjenningsgrunnlagUt | DatafeilUt,
    )
    def godkjenningsgrunnlag(
        vaktnummer: int, ansatt_id: int, request: Request, okt: Okt,
    ) -> GodkjenningsgrunnlagUt | DatafeilUt | JSONResponse:
        grunnlag = les_rangering(okt, request.state.bruker.id, vaktnummer)
        if not isinstance(grunnlag, RangertGrunnlag):
            return grunnlag
        valgt = next((r for r in grunnlag.rangert if r.id == ansatt_id), None)
        if valgt is None:
            return feil(404, "ikke_funnet")
        kandidat = grunnlag.rad(valgt)
        vakt = grunnlag.vakt
        return GodkjenningsgrunnlagUt(
            status="ok", vakt=VaktdetaljerUt(avdeling=grunnlag.avdeling, vaktnummer=vakt.vaktnummer,
                                            vakttype=vakt.vakttype, start=vakt.start, slutt=vakt.slutt,
                                            minstenivå=vakt.minstenivå),
            kandidat=kandidat, topprangert=None if valgt.plass == 1 else grunnlag.rad(grunnlag.rangert[0]),
            grunnlagsmerke=kandidat.grunnlagsmerke,
        )

    @app.post("/api/vakter/{vaktnummer}/kandidater/{ansatt_id}", response_model=GodkjenningUt | DatafeilUt)
    def godkjenn(
        vaktnummer: int, ansatt_id: int, inn: GodkjenningInn, request: Request,
    ) -> GodkjenningUt | DatafeilUt | JSONResponse:
        godkjenning = Godkjenning(
            vaktnummer=vaktnummer, ansatt_id=ansatt_id,
            bruker_id=request.state.bruker.id, godkjent=datetime.now(OSLO),
        )
        utfall = lagre_godkjenning(okter, godkjenning, inn.grunnlagsmerke)
        if isinstance(utfall, Datafeil):
            logger.warning("Datafeil for vakt %s: %s", vaktnummer, "; ".join(utfall.grunner))
            return DatafeilUt(status="datafeil", kode="mangler_turnusgrunnlag", datagrense=utfall.datagrense)
        if utfall == "godkjent":
            return GodkjenningUt(status="godkjent")
        return feil(404 if utfall == "ikke_funnet" else 409, utfall)

    @app.post("/api/utlogging", status_code=204)
    def utlogging(respons: Response) -> None:
        sesjon.slett_cookie(respons)

    @app.get("/api/innloggingsinfo")
    def innloggingsinfo(okt: Okt) -> InnloggingsinfoUt:
        return InnloggingsinfoUt(passord_kilde=hent_passord_kilde(okt))

    return app


vis_applogg_i_terminalen()
app = lag_app(ki=ki_fra_miljo())
