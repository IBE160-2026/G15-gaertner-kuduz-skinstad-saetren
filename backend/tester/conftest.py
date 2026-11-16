"""Felles for alle backendtester."""

import os

import pytest

KI_VARIABLER = ("OPENROUTER_API_KEY", "KI_MODUS", "OPENROUTER_MODEL")

# Kjøres før testmodulene samles inn. `tester/test_helse.py` importerer
# `adaptere.api.main`, som bygger modulobjektet `app` med `ki_fra_miljo()`. Uten
# dette ville en nøkkel i terminalen gitt `app` en ekte `OpenRouterKiAdapter`.
for _navn in KI_VARIABLER:
    os.environ.pop(_navn, None)


@pytest.fixture(autouse=True)
def uten_ki_miljo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ingen test skal kunne bruke en ekte nøkkel eller modus fra terminalen (story 5.1)."""
    for navn in KI_VARIABLER:
        monkeypatch.delenv(navn, raising=False)
