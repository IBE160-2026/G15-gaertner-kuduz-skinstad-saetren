"""Kandidatgrunnlaget for én ubemannet vakt, som domenetyper (story 2.1, AD-5).

Konverteringen fra SQLAlchemy til `domene.typer` skjer bare her. Regelmotoren får
ferdige domenetyper og vet ikke at det finnes en database.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptere.lagring.modeller import AnsattRad
from adaptere.lagring.vaktdetaljer import finn_ubemannet_vakt
from domene.typer import Kandidat, Vakt


@dataclass(frozen=True)
class Kandidatgrunnlag:
    vakt: Vakt
    ansatte: tuple[Kandidat, ...]
    # Der turnusgrunnlaget slutter: `turnus.periode_slutt` (P-08).
    datagrense: datetime


def hent_kandidatgrunnlag(session: Session, bruker_id: int, vaktnummer: int) -> Kandidatgrunnlag | None:
    """Vakten, alle Ansatte og datagrensen, eller None når vakten ikke er synlig.

    Alle rader i `ansatt` er med. Tabellen har ingen `turnus_id`, og v1 har én
    turnus (AV-06). Regelmotoren tar selv bort den som var satt opp.
    """
    funnet = finn_ubemannet_vakt(session, bruker_id, vaktnummer)
    if funnet is None:
        return None
    vaktrad, turnus = funnet
    ansatte = session.scalars(select(AnsattRad).order_by(AnsattRad.id)).all()
    return Kandidatgrunnlag(
        vakt=Vakt(
            vaktnummer=vaktrad.vaktnummer,
            vakttype=vaktrad.vakttype,
            start=vaktrad.start,
            slutt=vaktrad.slutt,
            minstenivå=vaktrad.minstenivå,
            satt_opp_ansatt_id=vaktrad.satt_opp_ansatt_id,
        ),
        ansatte=tuple(Kandidat(id=rad.id, navn=rad.navn, kompetanse=rad.kompetanse) for rad in ansatte),
        datagrense=turnus.periode_slutt,
    )
