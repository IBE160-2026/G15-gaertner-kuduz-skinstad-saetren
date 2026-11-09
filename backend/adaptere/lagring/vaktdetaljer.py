"""Les én ubemannet vakt i den innloggede brukerens visningsperiode."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptere.lagring.modeller import BrukerRad, TurnusRad, VaktRad


@dataclass(frozen=True)
class Vaktdetaljer:
    avdeling: str
    vaktnummer: int
    vakttype: str
    start: datetime
    slutt: datetime
    minstenivå: int


def hent_vaktdetaljer(session: Session, bruker_id: int, vaktnummer: int) -> Vaktdetaljer | None:
    """Returner None også ved annen turnus, bemanning og utenfor perioden."""
    rad = session.execute(
        select(VaktRad, TurnusRad.avdeling)
        .join(TurnusRad, VaktRad.turnus_id == TurnusRad.id)
        .join(BrukerRad, BrukerRad.turnus_id == TurnusRad.id)
        .where(
            BrukerRad.id == bruker_id,
            VaktRad.vaktnummer == vaktnummer,
            VaktRad.mangler_bemanning.is_(True),
            VaktRad.start >= TurnusRad.periode_start,
            VaktRad.start < TurnusRad.periode_slutt,
        )
    ).one_or_none()
    if rad is None:
        return None
    vakt, avdeling = rad
    return Vaktdetaljer(
        avdeling=avdeling,
        vaktnummer=vakt.vaktnummer,
        vakttype=vakt.vakttype,
        start=vakt.start,
        slutt=vakt.slutt,
        minstenivå=vakt.minstenivå,
    )
