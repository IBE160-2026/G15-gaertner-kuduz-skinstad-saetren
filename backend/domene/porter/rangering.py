"""Portene for Rangeringen: `TolketPreferanse` inn og `RangertKandidat` ut (story 4.4, AD-1).

Bare datatyper, uten logikk, som `utelukkelse.py` (story 2.5). Portene er frosne
dataklasser og ikke Pydantic-modeller (AV-18). `adaptere/api` gjør dem om til
Pydantic-svar.

`RangertKandidat` konstrueres bare av `domene/regelmotor/rangering.py` (AD-1), og
bare for Gyldige kandidater (NFR2). `TolketPreferanse` lages ny bare av
`adaptere/ki` og leses tilbake av `adaptere/lagring`, som validerer den lagrede
verdien (story 5.1). Ren Python, ingen import fra `adaptere`.
"""

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction


class Tolkestatus(StrEnum):
    """Hvor preferansepoengene kommer fra (P-05, FR-10).

    Bare `TOLKET` gir poeng etter kategori. De tre andre gir midlertidig 50 poeng.
    """

    TOLKET = "tolket"
    VENTER_PAA_TOLKNING = "venter_paa_tolkning"
    KUNNE_IKKE_TOLKES = "kunne_ikke_tolkes"
    INGEN_REGISTRERT = "ingen_registrert"


@dataclass(frozen=True)
class TolketPreferanse:
    """En vellykket tolkning av én Ansatts preferansetekst (FR-10, story 5.1).

    `kategori` er en av nøklene i `rangering.PREFERANSEPOENG`, for eksempel
    `"positiv_ved_behov"`. `begrunnelse` er modellens korte begrunnelse på bokmål,
    og `modell` er OpenRouter-modellen som tolket teksten. Frossen dataklasse, ikke
    Pydantic (AV-18). Svaret valideres i `adaptere/ki`, og en lagret verdi
    valideres ved lesing i `adaptere/lagring`.
    """

    kategori: str
    begrunnelse: str
    modell: str


@dataclass(frozen=True)
class RangertKandidat:
    """Én Gyldig kandidat med beregnede fakta, faktorpoeng og plass.

    Sorteringen og faktakontrollen bruker de eksakte brøkene i `eksakte_poeng`.
    De numeriske visningsfeltene er fortsatt `float`. To totaler som er like
    som `float`, kan være ulike brøker. Rekkefølgen står i `plass` (1 er øverst).

    Porten har ikke Kandidatens vakter eller rå minutter, bare ferdige tall.
    """

    plass: int
    id: int
    navn: str
    stilling: str
    ansiennitet: int
    kompetansenivå: int
    # Vaktkostnad (P-01–P-03). `kostnadstype` er "ordinær" eller "inkluderer_overtid".
    kostnad: float
    ordinære_timer: float
    overtidstimer: float
    kostnadstype: str
    # Timer i uka Vakten starter i, uten Vakten selv, og prosent av 36 t (FR8, P-02, P-04).
    timer_i_uka: float
    timebelastning_prosent: float
    høy_belastning: bool
    # Ulempebelastningen i målevinduet (FR-14, AV-09).
    ulempepoeng: float
    kveldstimer: float
    helgetimer: float
    natttimer: float
    # Faktorpoeng 0–100 og totalscore, uavrundet (K-03).
    kostnadspoeng: float
    timebelastningspoeng: float
    ulempescore: float
    preferansepoeng: float
    totalscore: float
    tolkestatus: Tolkestatus
    tolket_preferanse: TolketPreferanse | None
    # P-06: sammenlign alltid brøkene fra selve beregningen, også ved lik float.
    eksakte_poeng: "EksaktePoeng"
    aktive_faktorer: frozenset[str]


@dataclass(frozen=True)
class EksaktePoeng:
    kostnad: Fraction
    timebelastning: Fraction
    ulempe: Fraction
    preferanse: Fraction
    total: Fraction
