"""Kandidatgrunnlaget for én ubemannet vakt, som domenetyper (story 2.1, AD-5).

Konverteringen fra SQLAlchemy til `domene.typer` skjer bare her. Regelmotoren får
ferdige domenetyper og vet ikke at det finnes en database.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptere.lagring.modeller import AnsattRad, TurnusRad, VaktRad
from adaptere.lagring.vaktdetaljer import finn_ubemannet_vakt
from domene.typer import Kandidat, Tidsrom, Vakt


@dataclass(frozen=True)
class Kandidatgrunnlag:
    vakt: Vakt
    ansatte: tuple[Kandidat, ...]
    # Der turnusgrunnlaget slutter: `turnus.periode_slutt` (P-08).
    datagrense: datetime
    # Der turnusgrunnlaget starter: `turnus.periode_start` − 672 faktiske timer,
    # samme vindu som ulempemålingen (AV-09, beslutning 2A i story 2.3).
    historikkstart: datetime


# 672 faktiske timer. Trekkes fra i UTC: `- timedelta` på en `ZoneInfo`-tid
# regner på veggklokka og gir feil over sommertidsskiftet.
HISTORIKK = timedelta(hours=672)


# Tabeller som kan påvirke visning, harde regler eller rangering (P-09). Alle
# kolonner tas med, så nye felt på disse tabellene dekkes automatisk. En ny
# tabell må føres her eller i UTENFOR_GRUNNLAG; testen i
# `tester/lagring/test_grunnlagsmerke.py` feiler ellers. Story 5.1 må ta stilling
# til tabellen for TolketPreferanse hvis den ikke blir kolonner på `ansatt`.
GRUNNLAGSTABELLER = (TurnusRad, AnsattRad, VaktRad)

# Tabeller som bevisst holdes utenfor merket, med begrunnelse.
UTENFOR_GRUNNLAG: dict[str, str] = {
    "bruker": "innlogging, ingen beslutningsdata",
    "godkjenning": "speiles i vakt.tildelt_ansatt_id og vakt.mangler_bemanning",
}


def grunnlagsmerke(session: Session, bruker_id: int, vaktnummer: int, ansatt_id: int) -> str:
    """Opakt merke over alle lagrede felt som kan påvirke visning eller regler.

    Merket dekker bare databasen. Konstanter i `domene/` (terskler, satser, vekter)
    endres bare ved omstart, og da lages en ny JWT-nøkkel, så alle logges ut og
    godkjenningsflaten henter et nytt merke. Gjøres JWT-nøkkelen varig over
    omstart, må en versjon for beregningene inn i merket. KI-forklaringer skal
    ikke inn: de er ikke deterministiske og bindes til merket i frontend
    (story 5.3/5.5, P-09).
    """
    rader = []
    for modell in GRUNNLAGSTABELLER:
        kolonner = tuple(modell.__table__.columns)
        rader.append([
            tuple(getattr(rad, kolonne.key) for kolonne in kolonner)
            for rad in session.scalars(select(modell).order_by(modell.id))
        ])
    data = json.dumps(
        [bruker_id, vaktnummer, ansatt_id, rader],
        sort_keys=True, default=str, ensure_ascii=False,
    ).encode("utf-8")
    return sha256(data).hexdigest()


def hent_kandidatgrunnlag(session: Session, bruker_id: int, vaktnummer: int) -> Kandidatgrunnlag | None:
    """Vakten, alle Ansatte og datadekningen, eller None når vakten ikke er synlig.

    Alle rader i `vakt` med tildelt Ansatt hentes i én spørring, uavhengig av periode,
    og legges på Kandidaten som `vakter`. Vakten som skal bemannes, har ingen tildelt
    Ansatt og er derfor aldri med.

    Alle rader i `ansatt` er med. Tabellen har ingen `turnus_id`, og v1 har én
    turnus (AV-06). Regelmotoren tar selv bort den som var satt opp.
    """
    funnet = finn_ubemannet_vakt(session, bruker_id, vaktnummer)
    if funnet is None:
        return None
    vaktrad, turnus = funnet
    ansatte = session.scalars(select(AnsattRad).order_by(AnsattRad.id)).all()
    egne: defaultdict[int, list[Tidsrom]] = defaultdict(list)
    for tildelt_id, start, slutt in session.execute(
        select(VaktRad.tildelt_ansatt_id, VaktRad.start, VaktRad.slutt)
        .where(VaktRad.tildelt_ansatt_id.is_not(None))
        .order_by(VaktRad.start, VaktRad.id)
    ):
        egne[tildelt_id].append(Tidsrom(start=start, slutt=slutt))
    return Kandidatgrunnlag(
        vakt=Vakt(
            vaktnummer=vaktrad.vaktnummer,
            vakttype=vaktrad.vakttype,
            start=vaktrad.start,
            slutt=vaktrad.slutt,
            minstenivå=vaktrad.minstenivå,
            satt_opp_ansatt_id=vaktrad.satt_opp_ansatt_id,
        ),
        ansatte=tuple(
            Kandidat(
                id=rad.id, navn=rad.navn, kompetanse=rad.kompetanse, vakter=tuple(egne[rad.id]),
                timelønn=rad.timelønn, preferanse=rad.preferanse, stilling=rad.stilling,
                ansiennitet=rad.ansiennitet,
            )
            for rad in ansatte
        ),
        datagrense=turnus.periode_slutt,
        historikkstart=turnus.periode_start.astimezone(UTC) - HISTORIKK,
    )
