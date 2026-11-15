"""Kontroll av at grunnlagsmerket (P-09) tar stilling til hver tabell i skjemaet.

Merket hasher alle kolonner i tabellene i `GRUNNLAGSTABELLER`. En ny tabell som
påvirker visning, regler eller rangering, men som ikke er ført der, ville ellers
gi likt merke selv om beslutningsgrunnlaget er endret.
"""

from adaptere.lagring.kandidatgrunnlag import GRUNNLAGSTABELLER, UTENFOR_GRUNNLAG
from adaptere.lagring.modeller import Base


def test_hver_tabell_er_klassifisert_for_grunnlagsmerket() -> None:
    i_merket = {modell.__tablename__ for modell in GRUNNLAGSTABELLER}
    assert i_merket.isdisjoint(UTENFOR_GRUNNLAG)
    uklassifisert = set(Base.metadata.tables) - i_merket - set(UTENFOR_GRUNNLAG)
    assert not uklassifisert, (
        f"Tabellene {sorted(uklassifisert)} må føres i GRUNNLAGSTABELLER eller "
        "UTENFOR_GRUNNLAG i adaptere/lagring/kandidatgrunnlag.py (P-09)"
    )


def test_klassifiseringen_nevner_bare_tabeller_som_finnes() -> None:
    assert set(UTENFOR_GRUNNLAG) <= set(Base.metadata.tables)


def test_hver_utelatt_tabell_har_begrunnelse() -> None:
    assert all(begrunnelse.strip() for begrunnelse in UTENFOR_GRUNNLAG.values())
