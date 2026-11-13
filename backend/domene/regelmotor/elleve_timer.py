"""Hard regel: 11-timersregelen, daglig hvile (FR4, AV-04, story 2.3).

En Kandidat utelukkes når hvilen før eller etter Vakten blir under 11 timer.
Hvilen før er Vaktens start minus slutten på Kandidatens forrige vakt, og hvilen
etter er starten på Kandidatens neste vakt minus Vaktens slutt. Nøyaktig 11 t er
gyldig, og en vakt som bare møter Vakten (0 t hvile), bryter regelen.

Hvilen er faktisk forløpt tid i UTC. Med samme `ZoneInfo` på begge tidene regner
Python ellers på veggklokka, og hvilen blir én time feil over sommertidsskiftene.

En egen vakt som overlapper Vakten, teller bare som kolliderende vakt (beslutning
A, Mithad 2026-11-11, OP-12). Regelen ser bare på vakter som ikke overlapper, og
nærmeste slutt før og nærmeste start etter avgjør. Det er det samme som at ingen
ikke-overlappende vakt ligger nærmere enn 11 t.
"""

from datetime import UTC, datetime, timedelta

from domene.regelmotor.kolliderende_vakt import overlapper
from domene.typer import Kandidat, Tidsrom, Vakt

ÅRSAK = "11-timersregelen"
MINSTE_HVILE = timedelta(hours=11)


def gyldig_tidsrom(egen: object) -> bool:
    """Bare tidsrom med tidssone og start før slutt kan gi en hvileperiode.

    Ugyldige vakter innenfor vinduet stopper vurderingen med datafeil før reglene
    kjøres. De som ligger utenfor, kan ikke påvirke regelen og hoppes over.
    """
    return (
        isinstance(egen, Tidsrom)
        and isinstance(egen.start, datetime) and egen.start.utcoffset() is not None
        and isinstance(egen.slutt, datetime) and egen.slutt.utcoffset() is not None
        and egen.start.astimezone(UTC) < egen.slutt.astimezone(UTC)
    )


def bryter_elleve_timer(kandidat: Kandidat, vakt: Vakt) -> bool:
    """Om hvilen før eller etter Vakten blir under 11 t.

    Forutsetning: kalles via `vurder_kandidater`, eller etter at
    `kandidatvaktdatafeil` har godkjent Kandidatens vakter i vinduet. Ugyldige
    vakter hoppes over her, så kalt direkte blir ugyldige vakter i vinduet ikke
    oppdaget (gjelder for eksempel en ny regelkontroll ved Godkjenning i Epic 3).
    """
    start, slutt = vakt.start.astimezone(UTC), vakt.slutt.astimezone(UTC)
    for egen in kandidat.vakter:
        if not gyldig_tidsrom(egen) or overlapper(egen.start, egen.slutt, vakt.start, vakt.slutt):
            continue
        egen_start, egen_slutt = egen.start.astimezone(UTC), egen.slutt.astimezone(UTC)
        if egen_slutt <= start and start - egen_slutt < MINSTE_HVILE:
            return True
        if egen_start >= slutt and egen_start - slutt < MINSTE_HVILE:
            return True
    return False


def vindu(vakt: Vakt) -> Tidsrom:
    """Vakter i `[start − 11 t, slutt + 11 t)` kan påvirke regelen. Regnet i UTC."""
    return Tidsrom(
        start=vakt.start.astimezone(UTC) - MINSTE_HVILE,
        slutt=vakt.slutt.astimezone(UTC) + MINSTE_HVILE,
    )
