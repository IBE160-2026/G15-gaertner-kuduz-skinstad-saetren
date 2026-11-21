"""Faktakontroll for live og forhåndsgenererte påstander (P-06, P-07)."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from fractions import Fraction

import pytest

from adaptere.ki.avveining import faktorretninger, tillatte_påstander, valider
from adaptere.ki import openrouter
from adaptere.ki.begrenser import Begrenser, TidsbudsjettOpbrukt
from adaptere.ki.openrouter import HttpSvar, OpenRouterKiAdapter
from domene.regelmotor.rangering import Rangeringsparametere, ranger
from tester.ki.test_openrouter import FalskKlokke, FalskTransport, adapter, innhold, ok, status
from tester.regelmotor.test_rangering import VAKT, kandidat, vurder


def egen(faktor="kostnad", retning="opp"):
    return {"type": "egen", "kandidat_id": 1, "faktor": faktor, "retning": retning}


def mot(faktor, retning):
    return {"type": "sammenligning", "kandidat_id": 1, "referanse_id": 2, "faktor": faktor, "retning": retning}


def kontroller(valgt, ref, *felt):
    return valider({"paastander": list(felt)}, tillatte_påstander(valgt, ref))


def kandidater():
    return ranger(vurder(kandidat(1, lønn=300), kandidat(2, lønn=400)), VAKT)


def test_billigere_vakt_har_høyere_kostnadspoeng():
    en, to = kandidater()
    assert en.kostnad < to.kostnad
    (tekst,) = kontroller(en, to, mot("kostnad", "høyere"))
    assert tekst.startswith("Kostnadspoengene") and to.navn in tekst
    assert not kontroller(en, to, mot("kostnad", "lavere"))
    assert en.ulempescore == 100 and en.ulempepoeng == 0
    assert kontroller(en, to, egen("ulempe", "opp"))
    assert not kontroller(en, to, egen("ulempepoeng", "opp"))


def test_60_mot_80_trekker_ned():
    en, _ = kandidater()
    en = replace(en, eksakte_poeng=replace(en.eksakte_poeng, kostnad=Fraction(60), total=Fraction(80)))
    assert kontroller(en, None, egen(retning="ned"))
    assert not kontroller(en, None, egen())
    en = replace(en, eksakte_poeng=replace(en.eksakte_poeng, kostnad=Fraction("62.25")))
    (tekst,) = kontroller(en, None, egen(retning="ned"))
    assert "(62,3)" in tekst and "(80,0) før avrunding" in tekst


def test_ingen_retning_for_nullvekt_eller_likhet():
    p = Rangeringsparametere(kostnadsvekt=0, timebelastningsvekt=1, ulempevekt=0, preferansevekt=0)
    en, to = ranger(vurder(kandidat(1, lønn=300), kandidat(2, lønn=400)), VAKT, parametere=p)
    assert en.eksakte_poeng.kostnad != en.eksakte_poeng.total
    assert faktorretninger(en) == {}
    assert not kontroller(en, None, egen())
    assert not kontroller(en, None, egen(retning="ned"))
    assert not kontroller(en, to, mot("kostnad", "høyere"))
    assert kontroller(en, to, mot("kostnad", "høyere"), mot("timebelastning", "lik"))


@pytest.mark.parametrize("feil", [
    egen("kostnad", "ned"), egen("kompetanse"), {**egen(), "navn": "Ansatt 1"}, {**egen(), "beløp": 2400},
    {**egen(), "kandidat_id": True}, {**egen(), "kandidat_id": 2}, {**egen(), "type": "overstyr"},
    {**mot("ulempe", "lik"), "referanse_id": 3}, {}, "fritekst",
])
def test_én_feil_forkaster_hele_svaret(feil):
    en, to = kandidater()
    assert not kontroller(en, to, egen(), feil)


def test_én_gyldig_eller_bare_hard_regel_og_total():
    en, to = kandidater()
    regler = {"type": "regler", "kandidat_id": en.id}
    assert kontroller(en, None, regler, egen())
    assert not kontroller(en, None, egen(), mot("ulempe", "lik"))
    assert not kontroller(en, to, regler, mot("total", "høyere"))
    lik = Fraction(50)
    en = replace(en, eksakte_poeng=type(en.eksakte_poeng)(lik, lik, lik, lik, lik))
    transport = FalskTransport([])
    assert adapter(FalskKlokke(), transport).forklar(en, None) is None
    assert not transport.kall


@pytest.mark.parametrize("forskjell", [Fraction(1, 1000), Fraction(1, 10**20)])
def test_lik_krever_eksakt_likhet_selv_ved_samme_visning_eller_float(forskjell):
    en, to = kandidater()
    assert kontroller(en, to, mot("preferanse", "lik"))
    to = replace(to, eksakte_poeng=replace(to.eksakte_poeng, preferanse=en.eksakte_poeng.preferanse + forskjell))
    assert not kontroller(en, to, mot("preferanse", "lik"))
    assert kontroller(en, to, mot("preferanse", "lavere"))


def test_første_live_kall_starter_budsjettet_etter_delt_begrenser():
    klokke = FalskKlokke()
    transport = FalskTransport([ok()] * 18 + [status(429), HttpSvar(200, {}, innhold({"paastander": [egen()]}))])
    ki = adapter(klokke, transport)
    for _ in range(18):
        ki.tolk("Fiktiv tekst")
    en, to = kandidater()
    assert ki.forklar(en, to)
    assert klokke.søvn == [60, 60]
    assert [k.tidsavbrudd for k in transport.kall[-2:]] == [45, 30]


def test_svar_etter_livefristen_forkastes():
    klokke = FalskKlokke()

    def for_sent(_):
        klokke.nå += 91
        return HttpSvar(200, {}, innhold({"paastander": [egen()]}))

    assert adapter(klokke, FalskTransport([for_sent])).forklar(*kandidater()) is None


def test_avveining_venter_på_ledig_plass_før_første_kall():
    i_kø = threading.Event()
    begrenser = Begrenser(per_minutt=18, samtidige=1)
    transport = FalskTransport([HttpSvar(200, {}, innhold({"paastander": [egen()]}))])
    ki = OpenRouterKiAdapter("test", begrenser=begrenser, transport=transport)
    par = kandidater()

    def åpne_panel():
        i_kø.set()
        return ki.forklar(*par)

    with ThreadPoolExecutor(max_workers=1) as tråder:
        with begrenser.plass(None):
            svar = tråder.submit(åpne_panel)
            assert i_kø.wait(2)
            with pytest.raises(TimeoutError):
                svar.result(timeout=0.05)
            assert not transport.kall
        assert svar.result(timeout=2)
    assert len(transport.kall) == 1


def test_hengende_transport_beholder_plassen_når_avveiningen_har_returnert(monkeypatch):
    monkeypatch.setattr(openrouter, "TIDSBUDSJETT_S", 0.2)
    startet = threading.Event()
    slipp_transport = threading.Event()

    def treg_transport(_):
        startet.set()
        assert slipp_transport.wait(5)
        return status(503)

    begrenser = Begrenser(per_minutt=18, samtidige=1)
    transport = FalskTransport([treg_transport])
    ki = OpenRouterKiAdapter("test", begrenser=begrenser, transport=transport)
    with ThreadPoolExecutor(max_workers=1) as tråder:
        svar = tråder.submit(ki.forklar, *kandidater())
        try:
            assert startet.wait(2)
            assert svar.result(timeout=2) is None
            with pytest.raises(TidsbudsjettOpbrukt), begrenser.plass(time.monotonic()):
                pytest.fail("Transporten skal fortsatt eie plassen")
        finally:
            slipp_transport.set()
    with begrenser.plass(time.monotonic() + 2):
        assert len(transport.kall) == 1


@pytest.mark.parametrize("modelltekst", [
    '{"paastander":[{"type":"egen","kandidat_id":2,"kandidat_id":1,"faktor":"kostnad","retning":"opp"}]}',
    '{"paastander":[{"type":"egen","kandidat_id":1,"faktor":"kostnad","retning":"ned","retning":"opp"}]}',
    '{"paastander":[],"paastander":[{"type":"egen","kandidat_id":1,"faktor":"kostnad","retning":"opp"}]}',
])
def test_rått_modellsvar_med_gjentatte_felt_forkastes(modelltekst):
    transport = FalskTransport([HttpSvar(200, {}, innhold(modelltekst))])
    assert adapter(FalskKlokke(), transport).forklar(*kandidater()) is None
    assert len(transport.kall) == 1


def test_avveiningskallet_sender_lukket_skjema_for_alle_tre_påstandstyper():
    transport = FalskTransport([HttpSvar(200, {}, innhold({"paastander": [egen()]}))])
    assert adapter(FalskKlokke(), transport).forklar(*kandidater())
    (kall,) = transport.kall
    format = kall.kropp["response_format"]
    assert format["type"] == "json_schema"
    kontrakt = format["json_schema"]
    assert kontrakt["name"] == "avveining" and kontrakt["strict"] is True

    rot = kontrakt["schema"]
    assert rot["type"] == "object" and rot["additionalProperties"] is False
    assert rot["required"] == ["paastander"] and set(rot["properties"]) == {"paastander"}
    liste = rot["properties"]["paastander"]
    assert liste["type"] == "array"
    typer = {}
    for variant in liste["items"]["anyOf"]:
        assert variant["type"] == "object" and variant["additionalProperties"] is False
        felt = variant["properties"]
        assert set(variant["required"]) == set(felt)
        assert felt["kandidat_id"] == {"type": "integer"}
        assert felt["type"]["type"] == "string"
        (navn,) = felt["type"]["enum"]
        typer[navn] = felt
    assert set(typer) == {"regler", "egen", "sammenligning"}
    assert set(typer["regler"]) == {"type", "kandidat_id"}
    assert set(typer["egen"]) == {"type", "kandidat_id", "faktor", "retning"}
    assert set(typer["sammenligning"]) == {"type", "kandidat_id", "referanse_id", "faktor", "retning"}
    assert typer["sammenligning"]["referanse_id"] == {"type": "integer"}
    faktorer = {"kostnad", "timebelastning", "ulempe", "preferanse"}
    for navn, tillatte_faktorer, retninger in [
        ("egen", faktorer, {"opp", "ned"}),
        ("sammenligning", faktorer | {"total"}, {"høyere", "lavere", "lik"}),
    ]:
        assert typer[navn]["faktor"]["type"] == typer[navn]["retning"]["type"] == "string"
        assert set(typer[navn]["faktor"]["enum"]) == tillatte_faktorer
        assert set(typer[navn]["retning"]["enum"]) == retninger
