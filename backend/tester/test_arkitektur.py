"""Arkitekturgrensen og kodestilen i backend.

Kjører import-linter-kontrakten i `pyproject.toml`: domenekjernen importerer aldri
adaptere (AD-1, AD-2). Testen feiler både når kontrakten brytes og når den ikke kan
kjøres, for eksempel fordi konfigurasjonen mangler eller en modul i kontrakten ikke
finnes.

Kjører også ruff med reglene i `[tool.ruff]`, slik at linteren går i hver
`pytest`-kjøring, lokalt og i CI, uten et eget steg.
"""

import subprocess
import sys
from pathlib import Path

from importlinter.cli import lint_imports

BACKEND = Path(__file__).resolve().parents[1]


def test_domenet_importerer_ikke_adaptere(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # import-linter finner pakkene fra arbeidsmappen.
    monkeypatch.chdir(BACKEND)
    assert lint_imports(config_filename=str(BACKEND / "pyproject.toml"), no_cache=True) == 0


def test_ruff_finner_ingen_feil() -> None:
    resultat = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache", "--output-format", "concise", "."],
        cwd=BACKEND, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
