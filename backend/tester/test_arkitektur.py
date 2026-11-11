"""Arkitekturgrensen: domenekjernen importerer aldri adaptere (AD-1, AD-2).

Kjører import-linter-kontrakten i `pyproject.toml`. Testen feiler både når
kontrakten brytes og når den ikke kan kjøres, for eksempel fordi konfigurasjonen
mangler eller en modul i kontrakten ikke finnes.
"""

from pathlib import Path

from importlinter.cli import lint_imports

BACKEND = Path(__file__).resolve().parents[1]


def test_domenet_importerer_ikke_adaptere(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # import-linter finner pakkene fra arbeidsmappen.
    monkeypatch.chdir(BACKEND)
    assert lint_imports(config_filename=str(BACKEND / "pyproject.toml"), no_cache=True) == 0
