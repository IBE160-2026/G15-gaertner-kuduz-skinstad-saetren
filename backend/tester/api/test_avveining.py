"""Avveining gjennom den beskyttede ruten og ekte adapter med falsk transport."""

import json
import logging
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, update

from adaptere.api.main import lag_app
from adaptere.ki.demo import KONTRAKTSVERSJON, DemoKiAdapter
from adaptere.ki.openrouter import HttpSvar, Nettverksfeil, OpenRouterKiAdapter
from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import AnsattRad
from tester.api.test_innlogging import RIKTIG, engine, logg_inn  # noqa: F401
from tester.ki.test_openrouter import FalskKlokke, FalskTransport, adapter, innhold, sertifikatfeil, status
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


def test_direkte_sertifikatfeil_logger_årsaken_uten_feiltekst(engine, caplog):
    # Samme årsak i loggen som fra `urllib_transport` (769b3fb), også når feilen kommer rett fra transporten.
    klokke, transport = FalskKlokke(), FalskTransport([sertifikatfeil()])
    klient = TestClient(lag_app(engine=engine, ki=adapter(klokke, transport)))
    logg_inn(klient)
    with caplog.at_level(logging.WARNING, logger="adaptere.ki.openrouter"):
        assert klient.get(f"{LISTE}/6/avveining").json()["status"] == "avveining_feilet"
    advarsler = [r.getMessage() for r in caplog.records if r.name == "adaptere.ki.openrouter"]
    # Retro 5, T3: `forklar` legger til én oppsummeringslinje med feiltypen.
    assert advarsler == ["Nettverksfeil mot OpenRouter: SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED"] * 4 + [
        "Avveining for kandidat 6 ga reservetekst (nettverk)."]
    assert "Bearer hemmelig" not in caplog.text


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


# --- story 5.7: `ki_kilde` fra en ekte `DemoKiAdapter`, gjennom den ekte ruten -----


def test_demo_med_levert_innhold_og_endret_referanse(engine) -> None:
    """Samme ID og retning hos referansen, men ny vaktkostnad, skal gi mal (AD-6)."""
    app = lag_app(engine=engine, ki=DemoKiAdapter())
    with TestClient(app) as klient:
        app.state.tolketråd.join(10)
        assert not app.state.tolketråd.is_alive()
        innlogging = klient.post("/api/innlogging", json=RIKTIG)
        assert innlogging.json()["demomodus"] is True
        assert klient.get("/api/meg").json()["demomodus"] is True
        rader = klient.get(LISTE).json()["kandidater"]
        assert [r["id"] for r in rader] == [6, 5, 3, 4]
        for rad in rader:
            svar = klient.get(f"{LISTE}/{rad['id']}/avveining").json()
            assert svar["ki_kilde"] == "forhandsgenerert" and svar["generert"]
            assert svar["paastander"]

        with lag_sessionmaker(engine).begin() as økt:
            økt.get(AnsattRad, 5).timelønn += 1
        etter = klient.get(LISTE).json()["kandidater"]
        assert [r["id"] for r in etter] == [6, 5, 3, 4]
        assert etter[0]["totalscore"] == rader[0]["totalscore"]
        assert etter[1]["totalscore"] != rader[1]["totalscore"]
        svar = klient.get(f"{LISTE}/6/avveining").json()
        assert svar["ki_kilde"] == "mal" and svar["paastander"]
        assert "generert" not in svar


def test_demo_adapter_rapporterer_mal_kilde_i_http_svaret_uten_oppslag(engine, tmp_path: Path) -> None:
    """Ingen treff i datafilen gir `ki_kilde: "mal"` i HTTP-svaret, aldri `avveining_feilet`
    så lenge kandidaten har minst én myk faktor-påstand."""
    datafil = tmp_path / "demoinnhold.json"
    datafil.write_text(json.dumps({
        "kontraktsversjon": KONTRAKTSVERSJON, "modell": "openai/gpt-6-luna", "generert": "2026-11-22",
        "kommando": "python scripts/generer_demoinnhold.py --live", "preferanser": {}, "avveininger": {},
    }, ensure_ascii=False), encoding="utf-8")

    klient = TestClient(lag_app(engine=engine, ki=DemoKiAdapter(datafil)))
    logg_inn(klient)
    svar = klient.get(f"{LISTE}/4/avveining").json()
    assert svar["status"] == "ok"
    assert svar["ki_kilde"] == "mal"
    assert svar["paastander"]


# --- Retro 5, T3: feilvern i ruten og ruten uten forklaringsport (R5, R6) -------------


class BareTolker:
    """Ren `Tolker` uten `forklar` og `modell`, slik et oppsett uten forklaringsport ser ut."""

    def tolk(self, tekst):
        raise AssertionError("Avveiningsruten skal ikke tolke")


class KastendeForklarer:
    modell = "test/modell"

    def tolk(self, tekst):
        raise AssertionError("Avveiningsruten skal ikke tolke")

    def forklar(self, kandidat, referanse):
        raise RuntimeError("uventet feil i forklaringsporten")


def _identitet(klient: TestClient, ansatt_id: int = 6) -> dict:
    merke = klient.get(f"{LISTE}/{ansatt_id}").json()["grunnlagsmerke"]
    return {"vaktnummer": 4127, "kandidat_id": ansatt_id, "grunnlagsmerke": merke}


@pytest.mark.parametrize("ki", [None, BareTolker()], ids=["uten-ki", "bare-tolker"])
def test_uten_forklaringsport_gir_kandidatbundet_reservesvar(engine, caplog, ki):
    klient = TestClient(lag_app(engine=engine, ki=ki))
    logg_inn(klient)
    with caplog.at_level(logging.ERROR, logger="adaptere.api.main"):
        svar = klient.get(f"{LISTE}/6/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", **_identitet(klient)}
    # Ingen forklaringsport er et kjent oppsett, ikke en uventet feil som feilvernet fanger.
    assert [r for r in caplog.records if r.levelno >= logging.ERROR] == []


def _kast(*_args, **_kwargs):
    raise RuntimeError("uventet feil i forklaringsnøkkelen")


@pytest.mark.parametrize("oppsett", ["forklar", "forklaringsnøkkel"])
def test_uventet_unntak_i_ki_delen_gir_reservesvar_og_én_feillinje(engine, monkeypatch, caplog, tmp_path, oppsett):
    from adaptere.api import main

    if oppsett == "forklar":
        ki = KastendeForklarer()
    else:
        # Demoadapteren er den eneste som får en oppslagsnøkkel.
        monkeypatch.setattr(main, "forklaringsnøkkel", _kast)
        ki = DemoKiAdapter(tmp_path / "mangler.json")
    klient = TestClient(lag_app(engine=engine, ki=ki), raise_server_exceptions=False)
    logg_inn(klient)
    identitet = _identitet(klient)
    with caplog.at_level(logging.ERROR, logger="adaptere.api.main"):
        svar = klient.get(f"{LISTE}/6/avveining")
    assert svar.status_code == 200
    assert svar.json() == {"status": "avveining_feilet", **identitet}
    feil = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert [(r.name, r.getMessage()) for r in feil] == [
        ("adaptere.api.main", "Avveining for vakt 4127 og kandidat 6 feilet uventet.")]
    assert feil[0].exc_info is not None


def test_demo_uten_datafil_gir_mal_med_tom_modell(engine, tmp_path: Path) -> None:
    """`demo.py` gir `modell = ""` når datafilen mangler. Frontend godtar `mal` uten modell."""
    klient = TestClient(lag_app(engine=engine, ki=DemoKiAdapter(tmp_path / "mangler.json")))
    logg_inn(klient)
    svar = klient.get(f"{LISTE}/6/avveining").json()
    assert {k: svar[k] for k in ("status", "ki_kilde", "modell")} == {"status": "ok", "ki_kilde": "mal", "modell": ""}
    assert "generert" not in svar
    assert svar["paastander"]
