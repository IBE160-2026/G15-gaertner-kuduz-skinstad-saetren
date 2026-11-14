"""Hard regel: kolliderende vakt (FR3, story 2.2).

En Kandidat utelukkes når en av de egne tildelte vaktene overlapper Vakten.
Vakter er halvåpne intervall `[start, slutt)`: `a.start < b.slutt and b.start <
a.slutt`. Vakter som bare berører hverandre, kolliderer ikke, og en vakt som
omslutter Vakten eller ligger inne i den, gjør det. Tidene sammenlignes i UTC,
altså faktisk forløpt tid, ikke kalenderdato eller veggklokke. Overlappende vakter
for ulike Ansatte er ikke et regelbrudd (AV-02), og regelen ser bare på
Kandidatens egne vakter.
"""

from datetime import UTC, datetime

from domene.typer import Kandidat, Tidsrom, Vakt

ÅRSAK = "kolliderende vakt"


def overlapper(a_start: datetime, a_slutt: datetime, b_start: datetime, b_slutt: datetime) -> bool:
    """Halvåpne intervall på faktisk tid. Alle fire tidene må ha tidssone."""
    return (
        a_start.astimezone(UTC) < b_slutt.astimezone(UTC)
        and b_start.astimezone(UTC) < a_slutt.astimezone(UTC)
    )


def bryter_kollisjon(kandidat: Kandidat, vakt: Vakt) -> bool:
    """Om en av Kandidatens egne vakter overlapper Vakten.

    Forutsetning: kalles via `vurder_kandidater`, eller etter at
    `kandidatvaktdatafeil` har godkjent Kandidatens vakter i vinduet. Ugyldige
    vakter hoppes ikke over her, slik de gjør i 11- og 35-timersregelen. Kalt
    direkte feiler en vakt som ikke er et tidsrom, en vakt uten tidssone tolkes
    i maskinens lokale tid, og en vakt med start etter slutt kan gi kollisjon
    (gjelder for eksempel en ny regelkontroll ved Godkjenning i Epic 3).
    """
    return any(overlapper(egen.start, egen.slutt, vakt.start, vakt.slutt) for egen in kandidat.vakter)


def vindu(vakt: Vakt) -> Tidsrom:
    """Bare vakter som overlapper `[start, slutt)`, kan påvirke regelen. Regnet i UTC."""
    return Tidsrom(start=vakt.start.astimezone(UTC), slutt=vakt.slutt.astimezone(UTC))
