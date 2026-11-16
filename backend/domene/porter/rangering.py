"""Portene for Rangeringen: `TolketPreferanse` inn og `RangertKandidat` ut (story 4.4, AD-1).

Bare datatyper, uten logikk, som `utelukkelse.py` (story 2.5). Arkitekturen sier
Pydantic, men domenet holder seg til frosne dataklasser etter presedensen fra 2.5,
og `adaptere/api` gjør dem om til Pydantic-svar. Avviket står i KI-loggen for 4.4.

`RangertKandidat` konstrueres bare av `domene/regelmotor/rangering.py` (AD-1), og
bare for Gyldige kandidater (NFR2). `TolketPreferanse` lages ny bare av
`adaptere/ki` og leses tilbake av `adaptere/lagring`, som validerer den lagrede
verdien (story 5.1). Ren Python, ingen import fra `adaptere`.
"""

from dataclasses import dataclass
from enum import StrEnum


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
    Pydantic (presedensen fra 2.5 og 4.4). Svaret valideres i `adaptere/ki`, og en
    lagret verdi valideres ved lesing i `adaptere/lagring`.
    """

    kategori: str
    begrunnelse: str
    modell: str


@dataclass(frozen=True)
class RangertKandidat:
    """Én Gyldig kandidat med beregnede fakta, faktorpoeng og plass.

    Alle tall er `float`. Sorteringen bruker de eksakte `Fraction`-verdiene, og de
    gjøres om til `float` først her. To totaler som er like som `float` i porten,
    kan derfor være ulike `Fraction`-er. Det motsatte kan ikke skje: like
    `Fraction`-er gir like `float`. Rekkefølgen står i `plass` (1 er øverst). Bruk
    `plass`, ikke en sammenligning av `totalscore`, for å finne rekkefølgen.

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
