"""Avveining gjennom den beskyttede ruten og ekte adapter med falsk transport."""

import json
from dataclasses import replace

from fastapi.testclient import TestClient
from sqlalchemy import event, update

from adaptere.api.main import lag_app
from adaptere.ki.openrouter import HttpSvar, OpenRouterKiAdapter
from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import AnsattRad
from tester.api.test_innlogging import engine, logg_inn  # noqa: F401
from tester.ki.test_openrouter import innhold
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
