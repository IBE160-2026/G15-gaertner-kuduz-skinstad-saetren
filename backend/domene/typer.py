"""Domenetypene for kandidatvurderingen (story 2.1).

Rene Python-typer uten rammeverk. `adaptere/lagring` konverterer radene sine hit
(AD-5), og domenet importerer aldri fra adaptere (AD-1, AD-2).

Verdiene fra lagringen valideres ikke her. Regelmotoren sjekker selv grunnlaget
og svarer med `Datafeil` når det ikke holder (P-08), så feltene er typet så vidt
som dataene faktisk kan være.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

# AV-02: dag 07–15, mellom 10–18, kveld 15–23, natt 23–07.
VAKTTYPER = ("dag", "mellom", "kveld", "natt")


@dataclass(frozen=True)
class Vakt:
    """Vakten som skal bemannes på nytt.

    `satt_opp_ansatt_id` er den som var satt opp og meldte fra. Vedkommende er
    ikke med i kandidatgrunnlaget (AV-06).
    """

    vaktnummer: int
    vakttype: str
    start: datetime
    slutt: datetime
    minstenivå: int
    satt_opp_ansatt_id: int | None


@dataclass(frozen=True)
class Kandidat:
    """En Ansatt som vurderes for Vakten.

    `kompetanse` er nivå per vakttype (`dag`, `kveld`, `natt`). Mangler nøkkelen,
    er den ansatte ikke opplært for vakttypen. Kopien er skrivebeskyttet, slik at
    en vurdering ikke kan endre grunnlaget for den neste.
    """

    id: int
    navn: str
    kompetanse: Mapping[str, object] = field(compare=False)

    def __post_init__(self) -> None:
        if isinstance(self.kompetanse, Mapping):
            object.__setattr__(self, "kompetanse", MappingProxyType(dict(self.kompetanse)))


@dataclass(frozen=True)
class Utelukket:
    """En Kandidat som bryter minst én hard regel, med alle årsakene."""

    kandidat: Kandidat
    årsaker: tuple[str, ...]


@dataclass(frozen=True)
class Kandidatvurdering:
    """Resultatet når grunnlaget er gyldig.

    Gyldige og utelukkede er adskilte typer, så en utelukket Kandidat ikke kan
    sendes videre til rangering ved en feil (SM-2). Begge er sortert alfabetisk.
    """

    gyldige: tuple[Kandidat, ...]
    utelukkede: tuple[Utelukket, ...]


@dataclass(frozen=True)
class Datafeil:
    """Grunnlaget mangler eller er ugyldig, så ingen Kandidat er vurdert (P-08).

    `datagrense` er der turnusgrunnlaget slutter. `grunner` sier hva som feilet,
    for tester og feilsøking. De sendes ikke til brukergrensesnittet.
    """

    datagrense: datetime
    grunner: tuple[str, ...]
