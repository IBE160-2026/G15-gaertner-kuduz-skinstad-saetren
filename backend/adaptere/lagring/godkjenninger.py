"""Atomisk godkjenningsoperasjon og eneste skrivevei for ny bemanning (AD-5)."""

from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from adaptere.lagring.kandidatgrunnlag import kandidatmerke, hent_kandidatgrunnlag
from adaptere.lagring.modeller import BrukerRad, GodkjenningRad, TurnusRad, VaktRad
from domene.regelmotor.vurdering import vurder_kandidater
from domene.typer import Datafeil, Godkjenning

Godkjenningsutfall = Literal["godkjent", "allerede_bemannet", "ikke_funnet", "ugyldig_kandidat", "endret_grunnlag"]


def lagre_godkjenning(
    okter: sessionmaker[Session], godkjenning: Godkjenning, vist_merke: str,
) -> Godkjenningsutfall | Datafeil:
    """Lås, les, kontroller og skriv mot én konsistent databasetilstand.

    Operasjonen eier sesjonen og transaksjonsgrensen. Retur uten commit rulles
    tilbake ved lukking; også feil etter vaktoppdateringen rulles tilbake.
    """
    with okter() as session:
        session.connection().exec_driver_sql("BEGIN IMMEDIATE")
        grunnlag = hent_kandidatgrunnlag(session, godkjenning.bruker_id, godkjenning.vaktnummer)
        if grunnlag is None:
            vakt = session.scalar(
                select(VaktRad).join(BrukerRad, BrukerRad.turnus_id == VaktRad.turnus_id)
                .where(BrukerRad.id == godkjenning.bruker_id, VaktRad.vaktnummer == godkjenning.vaktnummer)
            )
            if vakt is not None and not vakt.mangler_bemanning:
                return "allerede_bemannet"
            return "ikke_funnet"

        vurdering = vurder_kandidater(
            grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart,
        )
        if isinstance(vurdering, Datafeil):
            return vurdering
        if not any(k.id == godkjenning.ansatt_id for k in vurdering.gyldige):
            return "ugyldig_kandidat"
        if kandidatmerke(
            grunnlag.avtrykk, godkjenning.bruker_id, godkjenning.vaktnummer, godkjenning.ansatt_id,
        ) != vist_merke:
            return "endret_grunnlag"

        vakt = session.scalar(select(VaktRad).where(VaktRad.vaktnummer == godkjenning.vaktnummer))
        assert vakt is not None
        resultat = session.execute(
            update(VaktRad)
            .where(VaktRad.id == vakt.id, VaktRad.mangler_bemanning.is_(True))
            .values(mangler_bemanning=False, tildelt_ansatt_id=godkjenning.ansatt_id)
        )
        if resultat.rowcount != 1:
            return "allerede_bemannet"
        session.add(GodkjenningRad(
            vakt_id=vakt.id,
            ansatt_id=godkjenning.ansatt_id,
            bruker_id=godkjenning.bruker_id,
            godkjent=godkjenning.godkjent,
        ))
        session.execute(
            update(TurnusRad)
            .where(TurnusRad.id == vakt.turnus_id)
            .values(sist_oppdatert=godkjenning.godkjent)
        )
        session.flush()
        session.commit()
        return "godkjent"
