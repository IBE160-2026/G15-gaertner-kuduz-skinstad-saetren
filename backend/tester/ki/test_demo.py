"""`DemoKiAdapter`: samme porter som live, uten nettverk (AD-6, story 5.7).

Ingen test her bruker nettverk, nøkkel eller den ekte, forhåndsgenererte
`demoinnhold.json` som skipes med appen: alle datafiler er skrevet lokalt i
testen, slik at testene er uavhengige av hva `scripts/generer_demoinnhold.py`
har produsert når de kjøres.
"""

import json
import logging
import threading
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from adaptere.ki.avveining import tillatte_påstander, valider
from adaptere.forklaringsgrunnlag import KONTRAKTSVERSJON, forklaringsnøkkel
from adaptere.ki.demo import DemoKiAdapter
from adaptere.ki.openrouter import Tolkefeil
from domene.porter.rangering import TolketPreferanse
from tester.ki.test_avveining import egen, mot
from tester.regelmotor.test_rangering import VAKT, kandidat, vurder
from domene.regelmotor.rangering import ranger

MODELL = "openai/gpt-6-luna"
TEKST = "Jeg ønsker flere vakter denne uken."


def skriv(tmp_path: Path, **felt) -> Path:
    sti = tmp_path / "demoinnhold.json"
    data = {"kontraktsversjon": KONTRAKTSVERSJON, "modell": MODELL, "generert": "2026-11-22",
            "kommando": "python scripts/generer_demoinnhold.py --live", "preferanser": {}, "avveininger": {}}
    data.update(felt)
    sti.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return sti


def kandidater():
    return ranger(vurder(kandidat(1, lønn=300), kandidat(2, lønn=400)), VAKT)


# --- Preferansetolkning (AC2) -------------------------------------------------------


def test_kjent_tekst_gir_lagret_kategori(tmp_path: Path) -> None:
    sti = skriv(tmp_path, preferanser={TEKST: {
        "kategori": "onsker_flere", "begrunnelse": "Ønsker flere vakter.", "modell": MODELL}})
    ki = DemoKiAdapter(sti)
    resultat = ki.tolk(TEKST)
    assert resultat == TolketPreferanse("onsker_flere", "Ønsker flere vakter.", MODELL)


def test_ukjent_tekst_gir_tolkefeil_ubrukelig(tmp_path: Path) -> None:
    ki = DemoKiAdapter(skriv(tmp_path))
    assert ki.tolk("En tekst uten forhåndsgenerert treff.") == Tolkefeil("ubrukelig")


@pytest.mark.parametrize("oppføring", [
    {"kategori": "onsker_flere", "begrunnelse": "", "modell": MODELL},
    {"kategori": "onsker_flere", "begrunnelse": "x", "modell": ""},
    {"kategori": 123, "begrunnelse": "x", "modell": MODELL},
    # Gyldig streng, men ikke en kjent kategori i PREFERANSEPOENG -- f.eks. en
    # skrivefeil i demoinnhold.json. Samme kontroll som OpenRouterKiAdapters les_svar().
    {"kategori": "onsker_flere_skrivefeil", "begrunnelse": "x", "modell": MODELL},
    {"begrunnelse": "x", "modell": MODELL},
    "fritekst",
], ids=["tom-begrunnelse", "tom-modell", "ikke-streng-kategori", "ukjent-kategori", "mangler-kategori", "fritekst"])
def test_ugyldig_lagret_preferanse_gir_tolkefeil(tmp_path: Path, oppføring: object) -> None:
    ki = DemoKiAdapter(skriv(tmp_path, preferanser={TEKST: oppføring}))
    assert ki.tolk(TEKST) == Tolkefeil("ubrukelig")


# --- Avveining: forhåndsgenerert, mal og ingen myk faktor (AC3, AC4, AC5) -----------


def test_forhandsgenerert_svar_som_bestaar_kontroll_brukes(tmp_path: Path) -> None:
    en, to = kandidater()
    gyldig = mot("kostnad", "høyere")
    sti = skriv(tmp_path, avveininger={"testnøkkel": {"paastander": [gyldig]}})
    ki = DemoKiAdapter(sti)
    svar = ki.forklar_med_oppslag(en, to, "testnøkkel")
    assert svar == valider({"paastander": [gyldig]}, tillatte_påstander(en, to))
    assert svar is not None
    assert ki.siste_kilde == "forhandsgenerert"


def test_forhandsgenerert_svar_som_ikke_bestaar_kontroll_faller_til_mal(tmp_path: Path) -> None:
    en, to = kandidater()
    # Svaret peker på en umulig sammenligning (motsatt retning) og består aldri valider().
    ugyldig = mot("kostnad", "lavere")
    sti = skriv(tmp_path, avveininger={"testnøkkel": {"paastander": [ugyldig]}})
    ki = DemoKiAdapter(sti)
    svar = ki.forklar_med_oppslag(en, to, "testnøkkel")
    assert svar is not None and svar == ki._mal(tillatte_påstander(en, to))  # noqa: SLF001
    assert ki.siste_kilde == "mal"
    assert any(p.myk_faktor for p in tillatte_påstander(en, to) if p.tekst in svar)


@pytest.mark.parametrize("metadata", [{"modell": None}, {"modell": "  "}, {"generert": "2026-02-31"}])
def test_manglende_kildebelegg_gir_mal(tmp_path, metadata):
    en, to = kandidater()
    svar = {"paastander": [mot("kostnad", "høyere")]}
    ki = DemoKiAdapter(skriv(tmp_path, avveininger={"treff": svar}, **metadata))
    assert ki.forklar_med_oppslag(en, to, "treff")
    assert ki.siste_kilde == "mal"


def test_endret_vakt_eller_grunndata_gir_mal_selv_med_samme_rangering(tmp_path):
    en, to = kandidater()
    ansatt = kandidat(en.id)
    nøkkel = forklaringsnøkkel(VAKT, ansatt, en, to)
    svar = {"paastander": [mot("kostnad", "høyere")]}
    ki = DemoKiAdapter(skriv(tmp_path, avveininger={nøkkel: svar}))
    for vakt, grunnlag in [
        (replace(VAKT, vaktnummer=VAKT.vaktnummer + 1), ansatt),
        (VAKT, replace(ansatt, kompetanse={**ansatt.kompetanse, "natt": 4})),
    ]:
        assert ki.forklar_med_oppslag(en, to, forklaringsnøkkel(vakt, grunnlag, en, to))
        assert ki.siste_kilde == "mal"


def test_intet_oppslag_gir_mal(tmp_path: Path) -> None:
    en, to = kandidater()
    ki = DemoKiAdapter(skriv(tmp_path))
    svar = ki.forklar_med_oppslag(en, to, "testnøkkel")
    assert svar is not None and ki.siste_kilde == "mal"
    tillatte = tillatte_påstander(en, to)
    assert set(svar) <= {p.tekst for p in tillatte}
    assert any(p.myk_faktor for p in tillatte if p.tekst in svar)
    # `_mal()` skal alltid lede med regelpåstanden (hvorfor kandidaten kan ta vakten),
    # ikke bare den myke faktoren.
    (regelpåstand,) = (p.tekst for p in tillatte if p.felt.get("type") == "regler")
    assert svar[0] == regelpåstand


def test_ingen_myk_faktor_gir_none_uavhengig_av_lagret_svar(tmp_path: Path) -> None:
    en, _ = kandidater()
    lik = Fraction(50)
    en = replace(en, eksakte_poeng=type(en.eksakte_poeng)(lik, lik, lik, lik, lik))
    # Et lagret svar finnes, men skal aldri brukes uten en myk faktor i det hele tatt.
    sti = skriv(tmp_path, avveininger={"uten-referanse": {"paastander": [egen()]}})
    ki = DemoKiAdapter(sti)
    assert ki.forklar_med_oppslag(en, None, "uten-referanse") is None
    assert ki.siste_kilde is None


# --- Kontraktsversjon og manglende/ugyldig datafil (P-06: ingen foreldet visning) ---


def test_feil_kontraktsversjon_gir_tom_data_med_advarsel(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    sti = skriv(tmp_path, kontraktsversjon=KONTRAKTSVERSJON + 1,
                preferanser={TEKST: {"kategori": "onsker_flere", "begrunnelse": "x", "modell": MODELL}})
    with caplog.at_level(logging.WARNING):
        ki = DemoKiAdapter(sti)
    assert ki.tolk(TEKST) == Tolkefeil("ubrukelig")
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_manglende_datafil_gir_tom_data_med_advarsel(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        ki = DemoKiAdapter(tmp_path / "finnes-ikke.json")
    assert ki.tolk(TEKST) == Tolkefeil("ubrukelig")
    assert ki.modell == ""
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_ugyldig_json_gir_tom_data_med_advarsel(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    sti = tmp_path / "demoinnhold.json"
    sti.write_text("{ikke json", encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        ki = DemoKiAdapter(sti)
    assert ki.tolk(TEKST) == Tolkefeil("ubrukelig")
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_to_adaptere_mot_manglende_datafil_deler_ikke_samme_dict(tmp_path: Path) -> None:
    """To instanser som begge feiler ved lesing, skal aldri aliasere samme mutable dict."""
    manglende = tmp_path / "finnes-ikke.json"
    ki1, ki2 = DemoKiAdapter(manglende), DemoKiAdapter(manglende)
    assert ki1._preferanser is not ki2._preferanser  # noqa: SLF001
    assert ki1._avveininger is not ki2._avveininger  # noqa: SLF001
    ki1._preferanser[TEKST] = {"kategori": "onsker_flere", "begrunnelse": "x", "modell": MODELL}  # noqa: SLF001
    assert ki2._preferanser == {}  # noqa: SLF001
    assert ki2.tolk(TEKST) == Tolkefeil("ubrukelig")


# --- `siste_kilde` er per tråd, ikke delt tilstand (samtidige avveiningskall) -------


def test_siste_kilde_er_isolert_per_trad(tmp_path: Path) -> None:
    en, to = kandidater()
    gyldig = mot("kostnad", "høyere")
    sti = skriv(tmp_path, avveininger={"testnøkkel": {"paastander": [gyldig]}})
    ki = DemoKiAdapter(sti)
    start = threading.Barrier(2)
    resultater: dict[str, object] = {}

    def forhandsgenerert() -> None:
        start.wait(5)
        ki.forklar_med_oppslag(en, to, "testnøkkel")
        resultater["forhandsgenerert"] = ki.siste_kilde

    def mal() -> None:
        start.wait(5)
        ki.forklar_med_oppslag(en, None, "uten-referanse")  # samme kandidat, annen referanse -> annen nøkkel -> intet oppslag -> mal
        resultater["mal"] = ki.siste_kilde

    t1, t2 = threading.Thread(target=forhandsgenerert), threading.Thread(target=mal)
    t1.start(); t2.start()
    t1.join(5); t2.join(5)
    assert not t1.is_alive() and not t2.is_alive()
    assert resultater == {"forhandsgenerert": "forhandsgenerert", "mal": "mal"}
