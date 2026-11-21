"""Avveining gjennom den beskyttede ruten og ekte adapter med falsk transport."""

import json
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, update

from adaptere.api.main import lag_app
from adaptere.ki.openrouter import HttpSvar, Nettverksfeil, OpenRouterKiAdapter
from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import AnsattRad
from tester.api.test_innlogging import engine, logg_inn  # noqa: F401
from tester.ki.test_openrouter import FalskKlokke, FalskTransport, adapter, innhold, status
from tester.regelmotor.test_rangering import DATAGRENSE, HISTORIKKSTART, VAKT, kandidat


LISTE = "/api/vakter/4127/kandidater"


def test_referanse_følger_plassen_også_ved_eksakt_lik_totalscore(engine, monkeypatch):
    from adaptere.api import main

    hent = main.hent_kandidatgrunnlag

    def like_kandidater(*args):
        return replace(hent(*args), vakt=replace(VAKT, vaktnummer=4127),
                       ansatte=(kandidat(2), kandidat(1)), datagrense=DATAGRENSE, historikkstart=HISTORIKKSTART)

    monkeypatch.setattr(main, "hent_kandidatgrunnlag", like_kandidater)
    par = []

    def transport(_url, kropp, _headere, _timeout):
        data = json.loads(json.loads(kropp)["messages"][1]["content"])
        lik_total = next(p for p in data["tillatte"] if p.get("faktor") == "total" and p["retning"] == "lik")
        par.append((lik_total["kandidat_id"], lik_total["referanse_id"]))
        myk = next(p for p in data["tillatte"] if p.get("faktor") == "preferanse")
        return HttpSvar(200, {}, innhold({"paastander": [lik_total, myk]}))

    klient = TestClient(lag_app(engine=engine, ki=OpenRouterKiAdapter("test", transport=transport)))
    logg_inn(klient)
    for id in (1, 2):
        assert klient.get(f"{LISTE}/{id}/avveining").json()["status"] == "ok"
    assert par == [(1, 2), (2, 1)]


def test_én_lesing_per_grunnlagstabell_og_riktig_referanse_for_hver_rad(engine):
    sendte = []

    def transport(url, kropp, headere, timeout):
        forespørsel = json.loads(kropp)
        tillatte = json.loads(forespørsel["messages"][1]["content"])["tillatte"]
        sammenligning = next(p for p in tillatte if p.get("faktor") == "ulempe" and "referanse_id" in p)
        sendte.append((sammenligning["kandidat_id"], sammenligning["referanse_id"]))
        return HttpSvar(200, {}, innhold({"paastander": [sammenligning]}))

    klient = TestClient(lag_app(engine=engine, ki=OpenRouterKiAdapter("test", transport=transport)))
    assert klient.get(f"{LISTE}/6/avveining").status_code == 401
    logg_inn(klient)
    tabeller = []

    def spor(_conn, _cursor, sql, *_):
        for tabell in ("ansatt", "turnus", "vakt"):
            if f"FROM {tabell} " in sql:
                tabeller.append(tabell)

    event.listen(engine, "before_cursor_execute", spor)
    try:
        assert klient.get("/api/vakter/987654/kandidater").status_code == 404
        assert tabeller == []
        liste = klient.get(LISTE).json()
    finally:
        event.remove(engine, "before_cursor_execute", spor)
    assert sorted(tabeller) == ["ansatt", "turnus", "vakt"]
    rader = liste["kandidater"]
    for r in rader:
        grunnlag = klient.get(f"{LISTE}/{r['id']}").json()
        assert grunnlag["grunnlagsmerke"] == r["grunnlagsmerke"]
    utenfor = liste["utelukkelser"]["utelukkede"][0]["id"]
    svar = [klient.get(f"{LISTE}/{id}/avveining") for id in (utenfor, 987654)]
    assert [s.status_code for s in svar] == [404, 404] and svar[0].json() == svar[1].json()
    assert not sendte
    for i, r in enumerate(rader):
        svar = klient.get(f"{LISTE}/{r['id']}/avveining").json()
        assert svar["status"] == "ok" and svar["ki_kilde"] == "live"
        assert svar["modell"] == "openai/gpt-6-luna" and svar["grunnlagsmerke"] == r["grunnlagsmerke"]
        assert (svar["vaktnummer"], svar["kandidat_id"]) == (4127, r["id"])
        ref = rader[1 if i == 0 else 0]
        assert ref["navn"] in svar["paastander"][0]
        assert sendte[-1] == (r["id"], ref["id"])


def test_modellfeil_beholder_merke_fra_før_kallet_og_sperrer_ingen_skriving(engine):
    def transport(*_):
        with lag_sessionmaker(engine).begin() as økt:
            økt.execute(update(AnsattRad).where(AnsattRad.id == 6).values(navn="Oppdatert navn"))
        return HttpSvar(200, {}, innhold({"paastander": [{"navn": "Ubekreftet"}]}))

    klient = TestClient(lag_app(engine=engine, ki=OpenRouterKiAdapter("test", transport=transport)))
    logg_inn(klient)
    valgt = f"{LISTE}/6"
    merke = klient.get(valgt).json()["grunnlagsmerke"]
    svar = klient.get(f"{valgt}/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", "grunnlagsmerke": merke, "vaktnummer": 4127, "kandidat_id": 6}
    assert klient.get(valgt).json()["grunnlagsmerke"] != merke


@pytest.mark.parametrize(("utfall", "venting"), [
    (status(402), []),
    (status(403), []),
    (HttpSvar(200, {}, b""), []),
    (HttpSvar(200, {}, innhold({"paastander": []})), []),
    (status(503), [2, 4, 8]),
    (Nettverksfeil("ingen forbindelse"), [2, 4, 8]),
    (ConnectionResetError("forbindelsen ble brutt"), [2, 4, 8]),
    (TimeoutError("lesingen tok for lang tid"), [2, 4, 8]),
], ids=["402", "403", "tom-kropp", "ubrukelig", "5xx", "nettverk", "brutt-forbindelse", "transporttidsavbrudd"])
def test_livefeil_gir_kandidatbundet_reservesvar_innen_fristen(engine, utfall, venting):
    klokke, transport = FalskKlokke(), FalskTransport([utfall])
    klient = TestClient(lag_app(engine=engine, ki=adapter(klokke, transport)))
    logg_inn(klient)
    valgt = f"{LISTE}/6"
    merke = klient.get(valgt).json()["grunnlagsmerke"]
    start = klokke()
    svar = klient.get(f"{valgt}/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", "vaktnummer": 4127, "kandidat_id": 6, "grunnlagsmerke": merke}
    assert klokke.søvn == venting
    assert len(transport.kall) == len(venting) + 1
    assert klokke() - start <= 90


def test_transporttidsavbrudd_bruker_opp_de_90_sekundene(engine):
    klokke = FalskKlokke()

    def utløp(tidsavbrudd):
        klokke.nå += tidsavbrudd
        raise TimeoutError("lesingen tok for lang tid")

    transport = FalskTransport([utløp])
    klient = TestClient(lag_app(engine=engine, ki=adapter(klokke, transport)))
    logg_inn(klient)
    valgt = f"{LISTE}/6"
    merke = klient.get(valgt).json()["grunnlagsmerke"]
    start = klokke()
    svar = klient.get(f"{valgt}/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", "vaktnummer": 4127, "kandidat_id": 6, "grunnlagsmerke": merke}
    assert [k.tidsavbrudd for k in transport.kall] == [45, 43]
    assert klokke.søvn == [2]
    assert klokke() - start == 90


@pytest.mark.parametrize("sekunder", [70, 90, 91])
def test_resetfristen_avgjør_om_nytt_liveforsøk_kan_gjøres(engine, sekunder):
    klokke = FalskKlokke()
    reset = str(int((klokke.vegg() + sekunder) * 1000))
    påstand = {"type": "egen", "kandidat_id": 6, "faktor": "kostnad", "retning": "opp"}
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), HttpSvar(200, {}, innhold({"paastander": [påstand]}))])
    klient = TestClient(lag_app(engine=engine, ki=adapter(klokke, transport)))
    logg_inn(klient)
    valgt = f"{LISTE}/6"
    identitet = {"vaktnummer": 4127, "kandidat_id": 6, "grunnlagsmerke": klient.get(valgt).json()["grunnlagsmerke"]}
    start = klokke()
    svar = klient.get(f"{valgt}/avveining")
    assert svar.status_code == 200
    assert klokke() - start <= 90
    if sekunder == 70:
        assert svar.json() == {**identitet, "status": "ok", "ki_kilde": "live", "modell": "openai/gpt-6-luna",
                               "paastander": ["Kostnadspoengene (84,8) trekker opp sammenholdt med egen totalscore (79,4) før avrunding."]}
        assert klokke.søvn == [70]
        assert [k.tidsavbrudd for k in transport.kall] == [45, 20]
    else:
        assert svar.json() == {**identitet, "status": "avveining_feilet"}
        assert klokke.søvn == []
        assert len(transport.kall) == 1


def test_utelukket_navn_forkaster_hele_forklaringen_og_valgt_kandidat_kan_godkjennes(engine):
    def transport(_url, kropp, _headere, _timeout):
        data = json.loads(json.loads(kropp)["messages"][1]["content"])
        gyldig = next(p for p in data["tillatte"] if p.get("faktor") == "kostnad")
        påstander = [gyldig]
        if gyldig["kandidat_id"] == valgt["id"]:
            påstander.append({**gyldig, "navn": utelukket})
        return HttpSvar(200, {}, innhold({"paastander": påstander}))

    klient = TestClient(lag_app(engine=engine, ki=OpenRouterKiAdapter("test", transport=transport)))
    logg_inn(klient)
    liste = klient.get(LISTE).json()
    valgt, annen = liste["kandidater"][:2]
    utelukket = liste["utelukkelser"]["utelukkede"][0]["navn"]
    sti = f"{LISTE}/{valgt['id']}"
    svar = klient.get(f"{sti}/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", "vaktnummer": 4127,
                           "kandidat_id": valgt["id"], "grunnlagsmerke": valgt["grunnlagsmerke"]}
    assert utelukket not in svar.text
    annen_forklaring = klient.get(f"{LISTE}/{annen['id']}/avveining").json()
    assert (annen_forklaring["kandidat_id"], annen_forklaring["ki_kilde"]) == (annen["id"], "live")
    assert annen_forklaring["paastander"]
    assert klient.post(sti, json={"grunnlagsmerke": valgt["grunnlagsmerke"]}).json() == {"status": "godkjent"}
