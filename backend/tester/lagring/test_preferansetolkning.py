"""Lagring og lesing av preferansetolkninger på `ansatt` (story 5.1, P-05).

Lagringen validerer en lagret verdi ved lesing. Alt som ikke er en gyldig tolkning
eller en gyldig lagret feil for gjeldende tekst, gir `venter_paa_tolkning`.
"""

from collections.abc import Iterator
from hashlib import sha256
from pathlib import Path

import pytest
from sqlalchemy import Engine, select, update
from sqlalchemy.orm import Session, sessionmaker

from adaptere.lagring.database import lag_engine, lag_sessionmaker, opprett_skjema
from adaptere.lagring.modeller import AnsattRad
from adaptere.lagring.preferansetolkning import (
    TOLKEFORMAT,
    lagre_resultat,
    lagre_tekst,
    les_tolkning,
    teksthash,
    tilstandsmerke,
    tolkninger,
    ventende_tekster,
)
from adaptere.lagring.testdata import ANSATTE, PREFERANSER, fyll_testdata
from domene.porter.rangering import TolketPreferanse

JONAS = 6
TEKST_JONAS = PREFERANSER[4][0]
TOLKNING = TolketPreferanse("positiv_ved_behov", "Tar gjerne en ekstravakt ved behov.", "openai/gpt-6-luna")
TOLKNINGSKOLONNER = ("tolket_kategori", "tolket_begrunnelse", "tolket_modell", "tolket_teksthash",
                     "tolkefeil", "tolkeformat")


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = lag_engine(tmp_path / "tolkning.db")
    opprett_skjema(engine)
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
    yield engine
    engine.dispose()


@pytest.fixture
def okter(engine: Engine) -> sessionmaker[Session]:
    return lag_sessionmaker(engine)


def rad(okter: sessionmaker[Session], ansatt_id: int = JONAS) -> AnsattRad:
    with okter() as session:
        funnet = session.get(AnsattRad, ansatt_id)
        assert funnet is not None
        session.expunge(funnet)
        return funnet


def gyldig_rad(**endringer: object) -> AnsattRad:
    verdier: dict[str, object] = dict(
        id=1, preferanse=TEKST_JONAS, tolket_kategori=TOLKNING.kategori,
        tolket_begrunnelse=TOLKNING.begrunnelse, tolket_modell=TOLKNING.modell,
        tolket_teksthash=teksthash(TEKST_JONAS), tolkefeil=None, tolkeformat=TOLKEFORMAT,
    )
    verdier.update(endringer)
    return AnsattRad(**verdier)


def test_testdataene_har_tomme_tolkningskolonner(okter: sessionmaker[Session]) -> None:
    with okter() as session:
        for ansatt in session.scalars(select(AnsattRad)):
            assert all(getattr(ansatt, kolonne) is None for kolonne in TOLKNINGSKOLONNER)


def test_19_tekster_venter_etter_testdataene(okter: sessionmaker[Session]) -> None:
    with okter() as session:
        ventende = ventende_tekster(session)
    forventet = [(i, PREFERANSER[nr][0]) for i, _, _, _, _, _, nr in ANSATTE if nr is not None]
    assert ventende == forventet
    assert len(ventende) == 19
    assert len({tekst for _, tekst in ventende}) == 15


def test_hash_er_sha256_av_teksten() -> None:
    tekst = "Jeg ønsker flere vakter denne uken."
    assert teksthash(tekst) == sha256(tekst.encode("utf-8")).hexdigest()


# --- Validering ved lesing -------------------------------------------------------


def test_gyldig_lagret_tolkning_leses_tilbake() -> None:
    assert les_tolkning(gyldig_rad()) == TOLKNING


def test_gyldig_lagret_feil_gir_feilet() -> None:
    feil = gyldig_rad(tolket_kategori=None, tolket_begrunnelse=None, tolket_modell=None, tolkefeil="5xx")
    assert les_tolkning(feil) == "feilet"


@pytest.mark.parametrize("endringer", [
    {"tolket_teksthash": teksthash("en annen tekst")},
    {"tolket_teksthash": None},
    {"tolkeformat": 2},
    {"tolkeformat": None},
    {"tolket_kategori": "uklar"},
    {"tolket_kategori": None},
    {"tolket_begrunnelse": ""},
    {"tolket_begrunnelse": "   "},
    {"tolket_begrunnelse": None},
    {"tolket_modell": ""},
    {"tolkefeil": "5xx"},  # tolkning og feil samtidig
    {"tolkefeil": ""},
], ids=lambda e: ",".join(f"{k}={v!r}" for k, v in e.items()))
def test_ugyldig_lagret_verdi_gir_venter(endringer: dict) -> None:
    assert les_tolkning(gyldig_rad(**endringer)) is None


@pytest.mark.parametrize("tekst", [None, "", "   "])
def test_uten_tekst_brukes_ingen_lagret_verdi(tekst: str | None) -> None:
    assert les_tolkning(gyldig_rad(preferanse=tekst, tolket_teksthash=teksthash(tekst or ""))) is None


def test_tolkninger_deler_i_tolkede_og_feilede() -> None:
    rader = [
        gyldig_rad(id=1),
        gyldig_rad(id=2, tolket_kategori=None, tolket_begrunnelse=None, tolket_modell=None, tolkefeil="4xx"),
        gyldig_rad(id=3, tolkeformat=2),
        gyldig_rad(id=4, preferanse=None),
    ]
    resultat = tolkninger(rader)
    assert resultat.tolkede == {1: TOLKNING}
    assert resultat.feilede == frozenset({2})


# --- Skriving --------------------------------------------------------------------


def test_lagret_tolkning(okter: sessionmaker[Session]) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    lagret = rad(okter)
    assert (lagret.tolket_kategori, lagret.tolket_begrunnelse, lagret.tolket_modell) == (
        TOLKNING.kategori, TOLKNING.begrunnelse, TOLKNING.modell)
    assert (lagret.tolket_teksthash, lagret.tolkefeil, lagret.tolkeformat) == (teksthash(TEKST_JONAS), None, 1)
    assert les_tolkning(lagret) == TOLKNING
    with okter() as session:
        assert JONAS not in {i for i, _ in ventende_tekster(session)}


def test_feil_nullstiller_tolkning_og_suksess_nullstiller_feil(okter: sessionmaker[Session]) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, "nettverk", versjon=0)
    feilet = rad(okter)
    assert (feilet.tolket_kategori, feilet.tolket_begrunnelse, feilet.tolket_modell, feilet.tolkefeil) == (
        None, None, None, "nettverk")
    assert feilet.tolket_teksthash == teksthash(TEKST_JONAS)
    assert les_tolkning(feilet) == "feilet"
    # En lagret feil prøves på nytt ved neste oppstart.
    with okter() as session:
        assert (JONAS, TEKST_JONAS) in ventende_tekster(session)
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert rad(okter).tolkefeil is None
    assert les_tolkning(rad(okter)) == TOLKNING


def test_endret_tekst_lagrer_ingenting(okter: sessionmaker[Session]) -> None:
    with okter.begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(preferanse="Ny tekst."))
    assert not lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert all(getattr(rad(okter), kolonne) is None for kolonne in TOLKNINGSKOLONNER)


def test_endret_tekst_etter_lagring_gir_venter(okter: sessionmaker[Session]) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    with okter.begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(preferanse="Ny tekst."))
    assert les_tolkning(rad(okter)) is None
    with okter() as session:
        assert (JONAS, "Ny tekst.") in ventende_tekster(session)


def test_tom_feiltype_avvises(okter: sessionmaker[Session]) -> None:
    with pytest.raises(ValueError):
        lagre_resultat(okter, JONAS, TEKST_JONAS, " ", versjon=0)


def test_uten_forventet_eller_versjon_avvises(okter: sessionmaker[Session]) -> None:
    """Story 5.9: versjonen sammenlignes alltid, så kallet må oppgi den."""
    with pytest.raises(ValueError):
        lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING)
    assert les_tolkning(rad(okter)) is None


# --- Redigering av teksten (story 5.9) ---------------------------------------------


def test_testdataene_har_versjon_0(okter: sessionmaker[Session]) -> None:
    with okter() as session:
        assert {a.preferanseversjon for a in session.scalars(select(AnsattRad))} == {0}


def test_ny_tekst_lagres_trimmet_øker_versjonen_og_nullstiller_tolkningen(okter: sessionmaker[Session]) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert lagre_tekst(okter, JONAS, "  Ny tekst.  ") == 1
    lagret = rad(okter)
    assert (lagret.preferanse, lagret.preferanseversjon) == ("Ny tekst.", 1)
    assert all(getattr(lagret, kolonne) is None for kolonne in TOLKNINGSKOLONNER)
    assert les_tolkning(lagret) is None
    assert lagre_tekst(okter, JONAS, "Enda en.") == 2


def test_lagret_feil_nullstilles_ved_ny_tekst(okter: sessionmaker[Session]) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, "nettverk", versjon=0)
    assert lagre_tekst(okter, JONAS, "Ny tekst.") == 1
    assert rad(okter).tolkefeil is None


@pytest.mark.parametrize("tekst", ["", "   ", "\n\t"])
def test_tom_tekst_lagres_som_none(okter: sessionmaker[Session], tekst: str) -> None:
    assert lagre_tekst(okter, JONAS, tekst) == 1
    assert rad(okter).preferanse is None
    assert lagre_tekst(okter, JONAS, "") == "uendret"


@pytest.mark.parametrize("tekst", [TEKST_JONAS, f"  {TEKST_JONAS}\n"])
def test_samme_tekst_er_en_noop(okter: sessionmaker[Session], tekst: str) -> None:
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    før = tilstandsmerke(rad(okter))
    assert lagre_tekst(okter, JONAS, tekst) == "uendret"
    assert tilstandsmerke(rad(okter)) == før
    assert les_tolkning(rad(okter)) == TOLKNING


def test_ikke_tillatt_eller_ukjent_ansatt_endrer_ingenting(okter: sessionmaker[Session]) -> None:
    sett: list[bool] = []

    def nei(_session: Session) -> bool:
        sett.append(True)
        return False

    assert lagre_tekst(okter, JONAS, "Ny tekst.", nei) == "ikke_funnet"
    assert sett == [True]
    assert lagre_tekst(okter, 999_999, "Ny tekst.") == "ikke_funnet"
    assert (rad(okter).preferanse, rad(okter).preferanseversjon) == (TEKST_JONAS, 0)


def test_svar_på_eldre_versjon_lagres_ikke(okter: sessionmaker[Session]) -> None:
    forventet = tilstandsmerke(rad(okter))
    assert lagre_tekst(okter, JONAS, "Ny tekst.") == 1
    assert not lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert not lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, forventet)
    assert all(getattr(rad(okter), kolonne) is None for kolonne in TOLKNINGSKOLONNER)


def test_a_b_a_forkaster_svaret_på_den_første_a(okter: sessionmaker[Session]) -> None:
    """Teksten er lik før og etter, men versjonen er ikke (deferred-work fra 5.1)."""
    forventet = tilstandsmerke(rad(okter))
    assert lagre_tekst(okter, JONAS, "B") == 1
    assert lagre_tekst(okter, JONAS, TEKST_JONAS) == 2
    assert rad(okter).preferanse == TEKST_JONAS
    assert not lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, forventet)
    assert not lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, versjon=0)
    assert les_tolkning(rad(okter)) is None
    assert lagre_resultat(okter, JONAS, TEKST_JONAS, TOLKNING, tilstandsmerke(rad(okter)))
    assert les_tolkning(rad(okter)) == TOLKNING
