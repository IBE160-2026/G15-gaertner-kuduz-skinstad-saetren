"""Timer i uka Vakten starter i, per Kandidat (FR8, P-02, story 4.1).

Summen av faktisk overlapp mellom Kandidatens egne vakter og kalenderuka Vakten
starter i (mandag 00:00 til mandag 00:00, `Europe/Oslo`). Vakten som bemannes
er ikke med: den fordeles først i kostnadsberegningen (4.3). Ukegrensene kommer
fra `berørte_uker`, og tiden er faktisk forløpt tid i UTC, så uka har 167 eller
169 t ved sommertidsskifte. Intervallene er halvåpne, så en vakt som slutter
nøyaktig mandag 00:00 gir 0 t i neste uke. Overlappende vakter telles som union.
Ren Python uten KI (NFR1).
"""

from datetime import UTC, timedelta

from domene.regelmotor.elleve_timer import gyldig_tidsrom
from domene.regelmotor.trettifem_timer import berørte_uker
from domene.typer import Kandidat, Vakt


def timer_i_startuka(kandidat: Kandidat, vakt: Vakt) -> timedelta:
    """Kandidatens eksisterende arbeidstid i uka `vakt` starter i. 0 uten vakter."""
    uke = berørte_uker(vakt)[0]
    uke_start, uke_slutt = uke.start.astimezone(UTC), uke.slutt.astimezone(UTC)
    klippet = sorted(
        (max(v.start.astimezone(UTC), uke_start), min(v.slutt.astimezone(UTC), uke_slutt))
        for v in kandidat.vakter
        if gyldig_tidsrom(v) and v.start.astimezone(UTC) < uke_slutt and uke_start < v.slutt.astimezone(UTC)
    )
    sum_, dekket_til = timedelta(0), uke_start
    for start, slutt in klippet:
        start = max(start, dekket_til)
        if slutt > start:
            sum_ += slutt - start
            dekket_til = slutt
    return sum_


def minutter_i_uka(kandidat: Kandidat, vakt: Vakt) -> int:
    """Som `timer_i_startuka`, i hele minutter avrundet ned (kontrakten mot frontend)."""
    return int(timer_i_startuka(kandidat, vakt) // timedelta(minutes=1))
