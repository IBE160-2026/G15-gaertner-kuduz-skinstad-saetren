"""Bakgrunnstolkning av preferansetekster og bruken i Rangeringen (story 5.1, FR-10, P-05).

`tolk_ventende` kalles direkte og synkront. Lifespan-testene viser at
`with TestClient(lag_app(ki=...))` starter tråden, og at `ki=None` aldri gjør det.
Ingen test bruker nettverk, nøkkel eller faktisk venting.
"""

import importlib
import logging
import threading
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select, update

from adaptere.api.main import TOLKETRÅD, ki_fra_miljo, lag_app, tolk_ventende
from adaptere.api.sesjon import STANDARD_MINUTTER
from adaptere.ki.openrouter import HttpSvar, OpenRouterKiAdapter, Tolkefeil
from adaptere.lagring.database import lag_engine, lag_sessionmaker
from adaptere.lagring.kandidatgrunnlag import grunnlagsmerke
from adaptere.lagring.modeller import AnsattRad, BrukerRad
from adaptere.lagring.testdata import FASIT, PREFERANSER
from domene.porter.rangering import TolketPreferanse
from domene.regelmotor.rangering import PREFERANSEPOENG
from tester.api.test_innlogging import NOKKEL, engine, feilsvar, klient, logg_inn  # noqa: F401
from tester.api.test_kandidater import RANGERING_4127_UTEN_TOLKNING, hent
from tester.ki.test_openrouter import FalskKlokke, FalskTransport, innhold, status
from tester.regelmotor.test_rangering import TOLKET_4127

KATEGORI_VED_POENG = {poeng: kategori for kategori, poeng in PREFERANSEPOENG.items()}
FASITKATEGORI = {tekst: KATEGORI_VED_POENG[poeng] for tekst, poeng in PREFERANSER.values()}
JONAS = 6
MODELL = "falsk/fasit"


class FasitKi:
    """Svarer etter fasiten i PRD §4.5 og teller kallene."""

    def __init__(self, før: Callable[[str], None] | None = None) -> None:
        self.tekster: list[str] = []
        self.før = før

    def tolk(self, tekst: str) -> TolketPreferanse | Tolkefeil:
        self.tekster.append(tekst)
        if self.før:
            self.før(tekst)
        return TolketPreferanse(FASITKATEGORI[tekst], "Begrunnelse fra falsk adapter.", MODELL)


class FeilKi:
    def __init__(self, feiltype: str = "5xx") -> None:
        self.feiltype = feiltype
        self.antall = 0

    def tolk(self, tekst: str) -> Tolkefeil:
        self.antall += 1
        return Tolkefeil(self.feiltype)  # type: ignore[arg-type]


def kandidater(klient: TestClient) -> list[dict]:
    return hent(klient, 4127)["kandidater"]


def bruker_id(engine: Engine) -> int:
    with lag_sessionmaker(engine)() as session:
        return session.scalars(select(BrukerRad.id)).one()


# --- Rangeringen med lagrede tolkninger -------------------------------------------


def test_tolkede_preferanser_gir_fasiten(klient: TestClient, engine: Engine) -> None:
    assert [(k["navn"], k["totalscore"]) for k in kandidater(klient)] == RANGERING_4127_UTEN_TOLKNING
    ki = FasitKi()
    tolk_ventende(lag_sessionmaker(engine), ki)
    # Én tolkning per Ansatt med tekst, også når teksten er lik (19 tekster, 15 unike).
    assert len(ki.tekster) == 19
    assert len(set(ki.tekster)) == 15

    svar = kandidater(klient)
    fasit = FASIT[4127]["rangering"]
    assert [k["navn"] for k in svar] == [r["navn"] for r in fasit]
    # FASIT er summert for hånd i `float` og kan avvike i siste bit fra den eksakte
    # brøken (samme presedens som `tester/regelmotor/test_rangering.py`).
    assert [k["totalscore"] for k in svar] == pytest.approx([r["totalscore"] for r in fasit], abs=1e-12)
    assert [k["totalscore"] for k in svar] == [float(t) for _, t in TOLKET_4127]
    assert [round(k["totalscore"], 2) for k in svar] == [85.65, 78.65, 59.0, 37.0]
    assert [k["preferansepoeng"] for k in svar] == [r["preferansepoeng"] for r in fasit] == [75, 75, 0, 100]
    assert [k["preferansekategori"] for k in svar] == [
        "positiv_ved_behov", "positiv_ved_behov", "vil_unnga", "onsker_flere"]
    assert {k["tolkestatus"] for k in svar} == {"tolket"}


def test_lagret_gyldig_tolkning_gir_ingen_nye_kall(engine: Engine) -> None:
    okter = lag_sessionmaker(engine)
    tolk_ventende(okter, FasitKi())
    igjen = FasitKi()
    tolk_ventende(okter, igjen)
    assert igjen.tekster == []


def test_feil_gir_kunne_ikke_tolkes_og_prøves_ved_neste_oppstart(klient: TestClient, engine: Engine) -> None:
    okter = lag_sessionmaker(engine)
    feil = FeilKi("nettverk")
    tolk_ventende(okter, feil)
    assert feil.antall == 19
    svar = kandidater(klient)
    assert {k["tolkestatus"] for k in svar} == {"kunne_ikke_tolkes"}
    assert {k["preferansepoeng"] for k in svar} == {50}
    assert {k["preferansekategori"] for k in svar} == {None}
    # Ingen KI-feil utelukker en Kandidat: samme fire, samme rekkefølge som uten tolkning.
    assert [(k["navn"], k["totalscore"]) for k in svar] == RANGERING_4127_UTEN_TOLKNING
    with okter() as session:
        assert {r.tolkefeil for r in session.scalars(select(AnsattRad)) if r.preferanse} == {"nettverk"}

    ny = FasitKi()
    tolk_ventende(okter, ny)
    assert len(ny.tekster) == 19
    assert {k["tolkestatus"] for k in kandidater(klient)} == {"tolket"}


def test_tekst_endret_under_kallet_lagrer_ingenting(klient: TestClient, engine: Engine) -> None:
    okter = lag_sessionmaker(engine)
    jonas_tekst = PREFERANSER[4][0]
    endret = []

    def endre_jonas(tekst: str) -> None:
        if tekst == jonas_tekst and not endret:
            with okter.begin() as session:
                session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(preferanse="Ny tekst."))
            endret.append(True)

    tolk_ventende(okter, FasitKi(før=endre_jonas))
    with okter() as session:
        jonas = session.get(AnsattRad, JONAS)
        assert jonas is not None
        assert (jonas.tolket_kategori, jonas.tolket_teksthash, jonas.tolkefeil, jonas.tolkeformat) == (
            None, None, None, None)
    statuser = {k["navn"]: k["tolkestatus"] for k in kandidater(klient)}
    assert statuser["Jonas Bakke"] == "venter_paa_tolkning"
    assert statuser["Mette Solberg"] == "tolket"


def test_ugyldig_lagret_tolkning_venter_og_tolkes_på_nytt(klient: TestClient, engine: Engine) -> None:
    okter = lag_sessionmaker(engine)
    tolk_ventende(okter, FasitKi())
    with okter.begin() as session:
        session.execute(update(AnsattRad).where(AnsattRad.id == JONAS).values(tolkeformat=2))
        session.execute(update(AnsattRad).where(AnsattRad.id == 5).values(tolket_kategori="uklar"))
    statuser = {k["id"]: k["tolkestatus"] for k in kandidater(klient)}
    assert statuser[JONAS] == statuser[5] == "venter_paa_tolkning"
    ny = FasitKi()
    tolk_ventende(okter, ny)
    assert sorted(ny.tekster) == sorted([PREFERANSER[4][0], PREFERANSER[5][0]])
    assert {k["tolkestatus"] for k in kandidater(klient)} == {"tolket"}


def test_uventet_unntak_for_én_tekst_stopper_ikke_de_andre(engine: Engine, caplog: pytest.LogCaptureFixture) -> None:
    okter = lag_sessionmaker(engine)
    jonas_tekst = PREFERANSER[4][0]

    def krasj(tekst: str) -> None:
        if tekst == jonas_tekst:
            raise RuntimeError("feil i adapteren")

    ki = FasitKi(før=krasj)
    tolk_ventende(okter, ki)
    assert len(ki.tekster) == 19
    with okter() as session:
        med_tekst = {r.id for r in session.scalars(select(AnsattRad)) if r.preferanse}
        tolkede = {r.id for r in session.scalars(select(AnsattRad)) if r.tolket_kategori}
    # Bare Jonas har tekst nr. 4.
    assert tolkede == med_tekst - {JONAS}
    assert "feilet uventet" in caplog.text


# --- Grunnlagsmerket (P-09) -------------------------------------------------------


def test_ny_tolkning_etter_visning_gir_endret_grunnlag(klient: TestClient, engine: Engine) -> None:
    """Bare sluttresultatet skrives: forsøkene underveis endrer ikke merket."""
    logg_inn(klient)
    sti = f"/api/vakter/4127/kandidater/{JONAS}"
    okter = lag_sessionmaker(engine)
    bruker = bruker_id(engine)
    klokke = FalskKlokke()
    merker_underveis: list[str] = []

    def svar(kropp: bytes) -> Callable[[float], HttpSvar]:
        def send(_tidsavbrudd: float) -> HttpSvar:
            with okter() as session:
                merker_underveis.append(grunnlagsmerke(session, bruker, 4127, JONAS))
            return HttpSvar(200, {}, kropp) if kropp else status(503)
        return send

    transport = FalskTransport([svar(b""), svar(b""), svar(innhold(
        {"kategori": "positiv_ved_behov", "begrunnelse": "Tar gjerne en ekstravakt ved behov."}))])
    ki = OpenRouterKiAdapter("test", transport=transport, klokke=klokke, sov=klokke.sov, veggklokke=klokke)
    with okter.begin() as session:
        # Bare Jonas venter, så forsøkene gjelder hans tekst.
        session.execute(update(AnsattRad).where(AnsattRad.preferanse.is_not(None), AnsattRad.id != JONAS)
                        .values(preferanse=None))
    gammelt = klient.get(sti).json()["grunnlagsmerke"]

    tolk_ventende(okter, ki)
    assert len(transport.kall) == 3
    assert merker_underveis == [gammelt] * 3
    svar_post = klient.post(sti, json={"grunnlagsmerke": gammelt})
    assert svar_post.status_code == 409
    assert feilsvar("endret_grunnlag")(svar_post.json())
    nytt = klient.get(sti).json()["grunnlagsmerke"]
    assert nytt != gammelt
    assert klient.post(sti, json={"grunnlagsmerke": nytt}).status_code == 200


# --- Oppstart (lifespan) ------------------------------------------------------------


def app_med(engine: Engine, ki: object | None = None):  # type: ignore[no-untyped-def]
    return lag_app(nokkel=NOKKEL, minutter=STANDARD_MINUTTER, engine=engine, ki=ki)  # type: ignore[arg-type]


def test_lifespan_starter_tolkningen_i_bakgrunnen(engine: Engine) -> None:
    slipp = threading.Event()
    startet = threading.Event()

    def vent(_tekst: str) -> None:
        startet.set()
        assert slipp.wait(timeout=10)

    ki = FasitKi(før=vent)
    app = app_med(engine, ki)
    with TestClient(app) as klient:
        tråd = app.state.tolketråd
        assert isinstance(tråd, threading.Thread)
        assert (tråd.name, tråd.daemon) == (TOLKETRÅD, True)
        assert startet.wait(timeout=10)
        # Appen kan brukes mens tolkningen pågår.
        assert {k["tolkestatus"] for k in kandidater(klient)} == {"venter_paa_tolkning"}
        slipp.set()
        tråd.join(timeout=10)
        assert not tråd.is_alive()
        assert {k["tolkestatus"] for k in kandidater(klient)} == {"tolket"}
    assert len(ki.tekster) == 19


def test_uten_ki_startes_ingen_tråd(engine: Engine) -> None:
    app = app_med(engine)
    with TestClient(app) as klient:
        assert klient.get("/api/helse").status_code == 200
        assert app.state.tolketråd is None
        assert TOLKETRÅD not in {t.name for t in threading.enumerate()}


def test_lag_app_med_ki_starter_ingenting_før_oppstart(engine: Engine) -> None:
    ki = FasitKi()
    app = app_med(engine, ki)
    assert app.state.tolketråd is None
    assert ki.tekster == []


# --- Konfigurasjon fra miljøet ------------------------------------------------------


def advarsler(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]


def test_uten_nøkkel_er_tolkningen_av_med_én_advarsel(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        assert ki_fra_miljo() is None
    assert advarsler(caplog) == ["Preferansetolkning er av: OPENROUTER_API_KEY er ikke satt. Se README."]


@pytest.mark.parametrize(("modus", "nøkkel", "del_av_melding"), [
    ("demo", "hemmelig-test", "KI_MODUS er demo"),
    ("live", "hemmelig-test", "KI_MODUS er ukjent"),
    ("OpenRouter", "hemmelig-test", "KI_MODUS er ukjent"),
    ("openrouter", "   ", "OPENROUTER_API_KEY er ikke satt"),
])
def test_tolkningen_er_av(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, modus: str, nøkkel: str, del_av_melding: str,
) -> None:
    monkeypatch.setenv("KI_MODUS", modus)
    monkeypatch.setenv("OPENROUTER_API_KEY", nøkkel)
    with caplog.at_level(logging.WARNING):
        assert ki_fra_miljo() is None
    (melding,) = advarsler(caplog)
    assert del_av_melding in melding and melding.startswith("Preferansetolkning er av:")
    assert "hemmelig-test" not in caplog.text


def test_modell_uten_leverandør_slår_av_tolkningen(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "hemmelig-test")
    monkeypatch.setenv("OPENROUTER_MODEL", "gpt-6-luna")
    with caplog.at_level(logging.WARNING):
        assert ki_fra_miljo() is None
    assert len(advarsler(caplog)) == 1


@pytest.mark.parametrize(("modus", "modell", "forventet"), [
    ("", "", "openai/gpt-6-luna"),
    ("openrouter", "  ", "openai/gpt-6-luna"),
    (" openrouter ", "anthropic/claude-haiku-5.5", "anthropic/claude-haiku-5.5"),
])
def test_med_nøkkel_brukes_openrouter(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, modus: str, modell: str, forventet: str,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "hemmelig-test")
    monkeypatch.setenv("KI_MODUS", modus)
    monkeypatch.setenv("OPENROUTER_MODEL", modell)
    with caplog.at_level(logging.WARNING):
        ki = ki_fra_miljo()
    assert isinstance(ki, OpenRouterKiAdapter)
    assert ki.modell == forventet
    assert advarsler(caplog) == []


@pytest.mark.parametrize("nøkkel", ["sk-or-\x7fabc","sk-or-æøå", "sk-or-a\tb", "sk-or-a\nb"])
def test_nøkkel_med_ugyldige_tegn_slår_av_tolkningen(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, nøkkel: str,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", nøkkel)
    with caplog.at_level(logging.WARNING):
        assert ki_fra_miljo() is None
    assert advarsler(caplog) == ["Preferansetolkning er av: OPENROUTER_API_KEY har ugyldige tegn. Se README."]
    assert nøkkel.strip() not in caplog.text


def test_modulobjektet_app_får_adapteren_fra_miljøet(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import adaptere.api.main as main

    monkeypatch.setenv("TURNUSHJELPEREN_DB", str(tmp_path / "modul.db"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "hemmelig-test")
    try:
        importlib.reload(main)
        assert isinstance(main.app.state.ki, OpenRouterKiAdapter)
        assert main.app.state.tolketråd is None
    finally:
        monkeypatch.delenv("OPENROUTER_API_KEY")
        importlib.reload(main)
    assert main.app.state.ki is None


def test_gammel_database_stopper_tolkningen_med_én_feilmelding(
    tmp_path: Path, caplog: pytest.LogCaptureFixture,
) -> None:
    gammel = lag_engine(tmp_path / "gammel.db")
    with gammel.begin() as tilkobling:
        tilkobling.exec_driver_sql("CREATE TABLE ansatt (id INTEGER PRIMARY KEY, preferanse TEXT)")
        tilkobling.exec_driver_sql("INSERT INTO ansatt VALUES (1, 'Jeg ønsker flere vakter denne uken.')")
    ki = FasitKi()
    with caplog.at_level(logging.ERROR):
        tolk_ventende(lag_sessionmaker(gammel), ki)
    gammel.dispose()
    assert ki.tekster == []
    (feil,) = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert feil.getMessage() == (
        "Preferansetolkning stoppet: kunne ikke lese ansatt-tabellen. Er databasen fra før "
        "story 5.1? Slett den og last testdata på nytt."
    )
