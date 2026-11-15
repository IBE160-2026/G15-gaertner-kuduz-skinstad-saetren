"""Deterministisk ulempebelastning fra tildelte vakter (FR-14, AV-09/11).

Alle intervaller og varigheter regnes i UTC. Kategori bestemmes med lokal tid
i Europe/Oslo; grensene faller på hele UTC-timer også ved sommertidsskifte.
"""

import math
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from domene.typer import Kandidat, Tidsrom, Ulempebelastning, Vakt

OSLO = ZoneInfo("Europe/Oslo")
MÅLEVINDU = timedelta(hours=672)
STANDARD_TAK = 300
TIME = timedelta(hours=1)


def vindu(vakt: Vakt) -> Tidsrom:
    """De 672 faktisk forløpte timene før vaktstart, halvåpent i UTC."""
    start = vakt.start.astimezone(UTC)
    return Tidsrom(start - MÅLEVINDU, start)


def _kategori(tid: datetime) -> str:
    lokal = tid.astimezone(OSLO)
    if lokal.hour >= 22 or lokal.hour < 6:
        return "natt"
    if lokal.weekday() >= 5:
        return "helg"
    if lokal.hour >= 18:
        return "kveld"
    return "dag"


def beregn_ulempebelastning(
    kandidat: Kandidat, vakt: Vakt, *, tak: float = STANDARD_TAK,
) -> Ulempebelastning:
    """Klipp historikken til målevinduet og tell hver faktisk arbeidstime én gang.

    Krever at P-08 har validert datadekning og kandidatvakter før kallet.
    `tak` er ett navngitt domeneparameter, ikke miljøkonfigurasjon.
    """
    if isinstance(tak, bool) or not isinstance(tak, (int, float)) or not math.isfinite(tak) or tak <= 0:
        raise ValueError("tak må være et positivt, endelig tall")
    måling = vindu(vakt)
    sekunder = dict.fromkeys(("dag", "kveld", "helg", "natt"), 0.0)
    intervaller = sorted(
        (max(egen.start.astimezone(UTC), måling.start), min(egen.slutt.astimezone(UTC), måling.slutt))
        for egen in kandidat.vakter
    )
    sammenslått: list[tuple[datetime, datetime]] = []
    for start, slutt in intervaller:
        if start >= slutt:
            continue
        if sammenslått and start <= sammenslått[-1][1]:
            forrige_start, forrige_slutt = sammenslått[-1]
            sammenslått[-1] = (forrige_start, max(forrige_slutt, slutt))
        else:
            sammenslått.append((start, slutt))
    for start, slutt in sammenslått:
        while start < slutt:
            neste = min(start.replace(minute=0, second=0, microsecond=0) + TIME, slutt)
            sekunder[_kategori(start)] += (neste - start).total_seconds()
            start = neste
    dag, kveld, helg, natt = (sekunder[k] / 3600 for k in ("dag", "kveld", "helg", "natt"))
    poeng = kveld + 2 * helg + 3 * natt
    return Ulempebelastning(
        dagtimer=dag, kveldstimer=kveld, helgetimer=helg, natttimer=natt,
        poeng=poeng, score=max(0.0, 100 * (1 - poeng / tak)),
    )
