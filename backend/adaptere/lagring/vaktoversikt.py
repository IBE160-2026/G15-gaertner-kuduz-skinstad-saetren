"""Vaktoversikten for turnusen til den innloggede brukeren (story 1.5).

Bare lesing. Bare Vakter som starter i `[periode_start, periode_slutt)` tas med
(AV-03), så historikken før perioden kommer aldri med. Sorteringen er etter
start og deretter vaktnummer.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from adaptere.lagring.modeller import AnsattRad, BrukerRad, TurnusRad, VaktRad


@dataclass(frozen=True)
class BemannetAnsatt:
    navn: str
    stilling: str
    ansiennitet: int


@dataclass(frozen=True)
class VaktSomManglerBemanning:
    vaktnummer: int
    vakttype: str
    start: datetime
    slutt: datetime
    satt_opp: str | None
    meldt_fra: datetime | None
    grunn: str | None


@dataclass(frozen=True)
class BemannetVakt:
    vaktnummer: int
    vakttype: str
    start: datetime
    slutt: datetime
    ansatt: BemannetAnsatt


@dataclass(frozen=True)
class Vaktoversikt:
    avdeling: str
    periode_start: datetime
    periode_slutt: datetime
    sist_oppdatert: datetime
    # Alle rader i `ansatt`. Ansatte er ikke knyttet til avdeling, og v1 har én
    # avdeling. Kjent begrensning.
    antall_ansatte: int
    krever_handling: list[VaktSomManglerBemanning]
    bemannet: list[BemannetVakt]


def hent_vaktoversikt(session: Session, bruker_id: int) -> Vaktoversikt | None:
    """Oversikten for turnusen til brukeren, eller `None` uten bruker."""
    turnus = session.scalar(
        select(TurnusRad)
        .join(BrukerRad, BrukerRad.turnus_id == TurnusRad.id)
        .where(BrukerRad.id == bruker_id)
    )
    if turnus is None:
        return None

    vakter = session.scalars(
        select(VaktRad)
        .options(joinedload(VaktRad.tildelt_ansatt), joinedload(VaktRad.satt_opp_ansatt))
        .where(
            VaktRad.turnus_id == turnus.id,
            # OsloTid lagrer UTC-tekst, så sammenligningen følger tidslinjen.
            VaktRad.start >= turnus.periode_start,
            VaktRad.start < turnus.periode_slutt,
        )
        .order_by(VaktRad.start, VaktRad.vaktnummer)
    ).all()

    krever_handling: list[VaktSomManglerBemanning] = []
    bemannet: list[BemannetVakt] = []
    for vakt in vakter:
        if vakt.mangler_bemanning:
            krever_handling.append(
                VaktSomManglerBemanning(
                    vaktnummer=vakt.vaktnummer,
                    vakttype=vakt.vakttype,
                    start=vakt.start,
                    slutt=vakt.slutt,
                    satt_opp=vakt.satt_opp_ansatt.navn if vakt.satt_opp_ansatt else None,
                    meldt_fra=vakt.meldt_fra,
                    grunn=vakt.meldt_fra_grunn,
                )
            )
        else:
            ansatt = vakt.tildelt_ansatt
            assert ansatt is not None  # CHECK-regelen i `vakt` sikrer dette.
            bemannet.append(
                BemannetVakt(
                    vaktnummer=vakt.vaktnummer,
                    vakttype=vakt.vakttype,
                    start=vakt.start,
                    slutt=vakt.slutt,
                    ansatt=BemannetAnsatt(
                        navn=ansatt.navn,
                        stilling=ansatt.stilling,
                        ansiennitet=ansatt.ansiennitet,
                    ),
                )
            )

    return Vaktoversikt(
        avdeling=turnus.avdeling,
        periode_start=turnus.periode_start,
        periode_slutt=turnus.periode_slutt,
        sist_oppdatert=turnus.sist_oppdatert,
        antall_ansatte=session.scalar(select(func.count()).select_from(AnsattRad)) or 0,
        krever_handling=krever_handling,
        bemannet=bemannet,
    )
