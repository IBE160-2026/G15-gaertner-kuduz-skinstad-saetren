"""Timebelastning og høy belastning (FR8, P-04/K-02, story 4.2).

Timebelastning er timer i uka Vakten starter i (`timer_i_startuka`, story 4.1)
som prosent av en normaluke på 36 t. «Høy belastning» begynner ved minst 32,4 t,
altså 0,90 × 36 t = 1944 minutter. Sammenligningen er eksakt mellom to
`timedelta` mot uavrundet tid, så 32:23:59 er under og 32:24:00 er på grensen.
Grensen er bare en visuell indikator uten rangeringspoeng og ikke en hard regel.
Ren Python uten KI (NFR1).
"""

from dataclasses import dataclass
from datetime import timedelta

NORMALUKE = timedelta(hours=36)
# 36 t × 90 % i heltallsminutter, ikke flyttall (0.9 * 36 gir 32.400000000000006).
HØY_BELASTNING_GRENSE = timedelta(minutes=36 * 60 * 9 // 10)


@dataclass(frozen=True)
class Timebelastning:
    prosent: float  # Uavrundet og ikke kuttet: 40 t gir 111,1.
    høy: bool


def timebelastning(timer_i_uka: timedelta) -> Timebelastning:
    """Prosent av 36 t og om Kandidaten er på eller over 32,4 t. Deterministisk."""
    return Timebelastning(
        prosent=100 * (timer_i_uka / NORMALUKE),
        høy=timer_i_uka >= HØY_BELASTNING_GRENSE,
    )
