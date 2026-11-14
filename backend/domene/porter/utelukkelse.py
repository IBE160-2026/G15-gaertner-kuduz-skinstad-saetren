"""Porten `UtelukkelsesOppsummering` (story 2.5, UX-DR15).

Bare datatyper, uten logikk, slik `domene/typer.py` gjør for `Vakt` og `Kandidat`.
Konstrueres bare av `domene/regelmotor` (AD-1): `lag_utelukkelsesoppsummering` i
`domene/regelmotor/vurdering.py` bygger den fra `Kandidatvurdering.utelukkede`.
Ren Python, ingen import fra `adaptere`.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegelAntall:
    """Antall utelukkede for én hard regel, i `REGLER`-rekkefølge."""

    årsak: str
    antall: int


@dataclass(frozen=True)
class EkskludertKandidat:
    """Én utelukket Kandidat med alle årsakene, i `REGLER`-rekkefølge."""

    id: int
    navn: str
    årsaker: tuple[str, ...]


@dataclass(frozen=True)
class UtelukkelsesOppsummering:
    """Oppsummeringen som vises i Ekskludert-boksen.

    `totalt` teller hver Kandidat én gang. `per_regel` kan summere til mer enn
    `totalt`, fordi en Kandidat som bryter flere regler telles under hver av dem.
    """

    totalt: int
    per_regel: tuple[RegelAntall, ...]
    utelukkede: tuple[EkskludertKandidat, ...]
