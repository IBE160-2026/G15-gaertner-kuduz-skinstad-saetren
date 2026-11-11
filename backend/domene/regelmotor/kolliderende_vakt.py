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


def _har_offset(tid: object) -> bool:
    return isinstance(tid, datetime) and tid.utcoffset() is not None


def overlapper(a_start: datetime, a_slutt: datetime, b_start: datetime, b_slutt: datetime) -> bool:
    """Halvåpne intervall på faktisk tid. Alle fire tidene må ha tidssone."""
    return (
        a_start.astimezone(UTC) < b_slutt.astimezone(UTC)
        and b_start.astimezone(UTC) < a_slutt.astimezone(UTC)
    )


def bryter_kollisjon(kandidat: Kandidat, vakt: Vakt) -> bool:
    return any(overlapper(egen.start, egen.slutt, vakt.start, vakt.slutt) for egen in kandidat.vakter)


def _tidsromdatafeil(kandidat: Kandidat, indeks: int, egen: object) -> list[str]:
    ref = f"ansatt {kandidat.id}: vakt nr. {indeks + 1} i grunnlaget"
    if not isinstance(egen, Tidsrom):
        return [f"{ref} er ikke et tidsrom"]
    uten_offset = [navn for navn, tid in (("start", egen.start), ("slutt", egen.slutt)) if not _har_offset(tid)]
    if uten_offset:
        return [f"{ref}: {', '.join(uten_offset)} mangler tidssone"]
    if not egen.start.astimezone(UTC) < egen.slutt.astimezone(UTC):
        return [f"{ref}: start er ikke før slutt"]
    return []


def kollisjonsdatafeil(kandidat: Kandidat, _vakt: Vakt) -> list[str]:
    """Det regelen krever av Kandidatens vakter: tidssone og start før slutt (P-08)."""
    return [g for i, egen in enumerate(kandidat.vakter) for g in _tidsromdatafeil(kandidat, i, egen)]
