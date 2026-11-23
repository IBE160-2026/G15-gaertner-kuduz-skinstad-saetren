"""Terminalvisning av appens loggmeldinger (spec-loggoppsett-backend).

Uten oppsett viser Python bare WARNING og høyere fra `adaptere.*`, så INFO-fremdriften
fra `tolk_ventende` ble aldri vist under uvicorn.
"""

import io
import logging
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from adaptere.api.main import TERMINALMERKE, vis_applogg_i_terminalen
from tester.api.test_innlogging import BACKEND

APPLOGGER = logging.getLogger("adaptere")


def terminalhandlere() -> list[logging.Handler]:
    return [h for h in APPLOGGER.handlers if getattr(h, TERMINALMERKE, False)]


@pytest.fixture
def strøm() -> Iterator[io.StringIO]:
    """Erstatter handleren fra modulimporten med én som skriver til en StringIO."""
    nivå = APPLOGGER.level
    gamle = terminalhandlere()
    for h in gamle:
        APPLOGGER.removeHandler(h)
    buffer = io.StringIO()
    try:
        yield buffer
    finally:
        for h in terminalhandlere():
            APPLOGGER.removeHandler(h)
        for h in gamle:
            APPLOGGER.addHandler(h)
        APPLOGGER.setLevel(nivå)


def test_modulimporten_har_gitt_appen_én_terminalhandler() -> None:
    assert len(terminalhandlere()) == 1
    assert APPLOGGER.propagate is True


def test_handleren_fra_modulimporten_skriver_til_ekte_stderr(tmp_path: Path) -> None:
    miljo = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "KI_MODUS")}
    miljo |= {"TURNUSHJELPEREN_DB": str(tmp_path / "logg.db"), "PYTHONUTF8": "1"}
    resultat = subprocess.run(
        [sys.executable, "-c", "import adaptere.api.main, logging; logging.getLogger('adaptere.api.main').info('x')"],
        cwd=BACKEND, env=miljo, capture_output=True, text=True, encoding="utf-8",
    )
    assert resultat.returncode == 0, resultat.stderr
    assert "INFO:     x\n" in resultat.stderr


def test_info_fra_tolkningen_vises_med_uvicorns_prefiks(strøm: io.StringIO) -> None:
    vis_applogg_i_terminalen(strøm)
    logging.getLogger("adaptere.api.main").info("Preferansetolkning: %d tekster venter.", 19)
    assert strøm.getvalue() == "INFO:     Preferansetolkning: 19 tekster venter.\n"


def test_advarsel_vises_én_gang_med_nivåprefiks(strøm: io.StringIO) -> None:
    vis_applogg_i_terminalen(strøm)
    logging.getLogger("adaptere.ki.openrouter").warning("Nettverksfeil mot OpenRouter: %s", "URLError")
    assert strøm.getvalue() == "WARNING:     Nettverksfeil mot OpenRouter: URLError\n"


def test_gjentatt_oppsett_gir_én_handler_og_én_linje(strøm: io.StringIO) -> None:
    første = vis_applogg_i_terminalen(strøm)
    andre = vis_applogg_i_terminalen(io.StringIO())
    assert andre is første
    assert len(terminalhandlere()) == 1
    logging.getLogger("adaptere.api.main").info("tolket")
    assert strøm.getvalue().count("tolket") == 1


def test_rotloggeren_og_uvicorn_røres_ikke(strøm: io.StringIO) -> None:
    rot = logging.getLogger()
    uvicorn = logging.getLogger("uvicorn")
    før = (list(rot.handlers), rot.level, list(uvicorn.handlers), uvicorn.level)
    vis_applogg_i_terminalen(strøm)
    assert (list(rot.handlers), rot.level, list(uvicorn.handlers), uvicorn.level) == før


def test_debug_vises_ikke(strøm: io.StringIO) -> None:
    vis_applogg_i_terminalen(strøm)
    logging.getLogger("adaptere.api.main").debug("detalj")
    assert strøm.getvalue() == ""


def test_caplog_fanger_fortsatt_info(strøm: io.StringIO, caplog: pytest.LogCaptureFixture) -> None:
    vis_applogg_i_terminalen(strøm)
    with caplog.at_level(logging.INFO, logger="adaptere.api.main"):
        logging.getLogger("adaptere.api.main").info("Preferansetolkning for ansatt %s: tolket.", 7)
    assert "ansatt 7: tolket" in caplog.text
    assert "ansatt 7: tolket" in strøm.getvalue()
