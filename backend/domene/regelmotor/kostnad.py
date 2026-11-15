"""Deterministisk merkostnad per kandidat (P-01–P-03)."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from domene.regelmotor.timer_i_uka import arbeidstid_i_uke
from domene.regelmotor.trettifem_timer import berørte_uker
from domene.typer import Kandidat, Tidsrom, Vakt

GRENSE = timedelta(hours=36)
MIKROSEKUNDER_PER_TIME = Decimal(3_600_000_000)


@dataclass(frozen=True)
class Kostnad:
    total: Decimal
    ordinære_timer: Decimal
    overtidstimer: Decimal
    ordinær_sats: Decimal
    overtidssats: Decimal


def _timer(tid: timedelta) -> Decimal:
    mikrosekunder = (tid.days * 86400 + tid.seconds) * 1_000_000 + tid.microseconds
    return Decimal(mikrosekunder) / MIKROSEKUNDER_PER_TIME


def beregn_kostnad(kandidat: Kandidat, vakt: Vakt) -> Kostnad:
    """Krever vurdert grunnlag; eksisterende og ny arbeidstid regnes som union."""
    ordinær = overtid = timedelta(0)
    for uke in berørte_uker(vakt):
        før = arbeidstid_i_uke(kandidat.vakter, uke)
        etter = arbeidstid_i_uke(kandidat.vakter + (Tidsrom(vakt.start, vakt.slutt),), uke)
        ordinær += min(etter, GRENSE) - min(før, GRENSE)
        overtid += max(etter - GRENSE, timedelta(0)) - max(før - GRENSE, timedelta(0))
    sats = Decimal(str(kandidat.timelønn))
    ord_timer, overt_timer = _timer(ordinær), _timer(overtid)
    overt_sats = sats * Decimal("1.5")
    return Kostnad(ord_timer * sats + overt_timer * overt_sats, ord_timer, overt_timer, sats, overt_sats)
