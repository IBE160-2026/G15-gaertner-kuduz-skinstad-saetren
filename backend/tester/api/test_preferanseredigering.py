"""Redigering av preferansetekst på kandidatflaten (story 5.9, P-10B, P-09).

`PUT /api/vakter/{nr}/kandidater/{id}/preferanse` lagrer ny tekst, øker
`preferanseversjon`, nullstiller tolkningen og tolker den nye teksten med samme
lås og regler som «Prøv igjen» (AV-19). Testene dekker hver rad i matrisen i
`spec-5-9-redigere-preferansetekst.md`. Ingen test bruker nettverk eller nøkkel.
"""

import threading
import time
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select, update

import adaptere.api.main as main
from adaptere.api.main import lag_app, tolk_ventende
from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.modeller import AnsattRad, BrukerRad, TurnusRad, VaktRad
from adaptere.lagring.preferansetolkning import lagre_tekst
from adaptere.lagring.testdata import PERIODE_SLUTT, PERIODE_START, PREFERANSER
from tester.api.test_godkjenningsgrunnlag import øyeblikksbilde
from tester.api.test_innlogging import NOKKEL, engine, feilsvar, klient, logg_inn  # noqa: F401
from tester.api.test_kandidater import hent
from tester.api.test_preferansetolkning import JONAS, MODELL, FasitKi, FeilKi

STI = f"/api/vakter/4127/kandidater/{JONAS}/preferanse"
GODKJENNING = f"/api/vakter/4127/kandidater/{JONAS}"
A = PREFERANSER[4][0]  # Jonas' tekst i testdataene, 75 poeng
B = PREFERANSER[13][0]  # 0 poeng
C = PREFERANSER[1][0]  # 100 poeng


def app_klient(engine: Engine, ki: object | None = None) -> TestClient:
    klient = TestClient(lag_app(nokkel=NOKKEL, engine=engine, ki=ki), raise_server_exceptions=False)  # type: ignore[arg-type]
    logg_inn(klient)
    return klient


def jonas(klient: TestClient) -> dict:
    return next(k for k in hent(klient, 4127)["kandidater"] if k["id"] == JONAS)


def jonas_rad(engine: Engine) -> AnsattRad:
    with lag_sessionmaker(engine)() as session:
        rad = session.get(AnsattRad, JONAS)
        assert rad is not None
        session.expunge(rad)
        return rad


def vent_til(betingelse: Callable[[], bool]) -> None:
    frist = time.monotonic() + 10
    while not betingelse():
        assert time.monotonic() < frist, "tidsavbrudd i testen"
        time.sleep(0.01)


def i_tråd(klient: TestClient, tekst: str, svar: list) -> threading.Thread:
    tråd = threading.Thread(target=lambda: svar.append(klient.put(STI, json={"tekst": tekst})))
    tråd.start()
    return tråd


# --- Matrisen ---------------------------------------------------------------------


def test_ny_tekst_tolkes_og_gir_ny_rangering(engine: Engine) -> None:
    ki = FasitKi()
    klient = app_klient(engine, ki)
    før = hent(klient, 4127)["kandidater"]
    assert før[0]["id"] == JONAS and før[0]["preferansetekst"] == A

    svar = klient.put(STI, json={"tekst": f"  {B}  "})
    assert svar.status_code == 200 and svar.json() == {"status": "tolket"}
    assert ki.tekster == [B]
    rad = jonas_rad(engine)
    assert (rad.preferanse, rad.preferanseversjon, rad.tolket_kategori, rad.tolket_modell) == (
        B, 1, "vil_unnga", MODELL)
    etter = jonas(klient)
    assert (etter["preferansetekst"], etter["tolkestatus"], etter["preferansepoeng"]) == (B, "tolket", 0)
    assert etter["totalscore"] < før[0]["totalscore"]
    # Rangeringen leser bare lagrede tolkninger (NFR1).
    assert ki.tekster == [B]


def test_ki_feiler_endelig_gir_feilet_og_kan_prøves_igjen(engine: Engine) -> None:
    ki = FeilKi("5xx")
    klient = app_klient(engine, ki)
    svar = klient.put(STI, json={"tekst": B})
    assert svar.status_code == 200 and svar.json() == {"status": "feilet"}
    etter = jonas(klient)
    assert (etter["tolkestatus"], etter["preferansepoeng"], etter["preferansetekst"]) == (
        "kunne_ikke_tolkes", 50, B)
    # «Prøv igjen» godtar den lagrede feilen for den nye teksten.
    assert klient.post(STI).json() == {"status": "feilet"}
    assert ki.antall == 2


@pytest.mark.parametrize("tekst", ["   ", ""])
def test_tom_tekst_gir_ingen_registrert(engine: Engine, tekst: str) -> None:
    ki = FasitKi()
    klient = app_klient(engine, ki)
    svar = klient.put(STI, json={"tekst": tekst})
    assert svar.status_code == 200 and svar.json() == {"status": "ingen"}
    assert (jonas_rad(engine).preferanse, jonas_rad(engine).preferanseversjon) == (None, 1)
    etter = jonas(klient)
    assert (etter["tolkestatus"], etter["preferansetekst"]) == ("ingen_registrert", None)
    assert ki.tekster == []


@pytest.mark.parametrize("tekst", [A, f" {A}\n"])
def test_uendret_tekst_endrer_ingenting(engine: Engine, tekst: str) -> None:
    tolk_ventende(lag_sessionmaker(engine), FasitKi())
    ki = FasitKi()
    klient = app_klient(engine, ki)
    før = øyeblikksbilde(engine)
    svar = klient.put(STI, json={"tekst": tekst})
    assert svar.status_code == 200 and svar.json() == {"status": "uendret"}
    assert øyeblikksbilde(engine) == før
    assert ki.tekster == []


@pytest.mark.parametrize("kropp", [
    {"tekst": "x" * 501}, {"tekst": 123}, {"tekst": None}, {}, {"tekst": ["a"]},
], ids=["for-lang", "tall", "null", "mangler", "liste"])
def test_ugyldig_kropp_gir_422_og_endrer_ingenting(engine: Engine, kropp: dict) -> None:
    ki = FasitKi()
    klient = app_klient(engine, ki)
    før = øyeblikksbilde(engine)
    svar = klient.put(STI, json=kropp)
    assert svar.status_code == 422
    assert feilsvar("ugyldig_foresporsel")(svar.json())
    assert øyeblikksbilde(engine) == før
    assert ki.tekster == []


def test_500_tegn_er_tillatt(engine: Engine) -> None:
    klient = app_klient(engine)
    assert klient.put(STI, json={"tekst": "x" * 500}).json() == {"status": "venter"}
    assert jonas_rad(engine).preferanse == "x" * 500


def test_uten_sesjon_gir_401_og_endrer_ingenting(engine: Engine) -> None:
    ki = FasitKi()
    klient = TestClient(lag_app(nokkel=NOKKEL, engine=engine, ki=ki))  # type: ignore[arg-type]
    før = øyeblikksbilde(engine)
    svar = klient.put(STI, json={"tekst": B})
    assert svar.status_code == 401
    assert feilsvar("mangler_sesjon")(svar.json())
    assert øyeblikksbilde(engine) == før
    assert ki.tekster == []


def test_utelukket_eller_ukjent_ansatt_gir_404_og_endrer_ingenting(engine: Engine) -> None:
    ki = FasitKi()
    klient = app_klient(engine, ki)
    utelukket = hent(klient, 4127)["utelukkelser"]["utelukkede"][0]["id"]
    før = øyeblikksbilde(engine)
    for sti in (f"/api/vakter/4127/kandidater/{utelukket}/preferanse",
                "/api/vakter/4127/kandidater/999999/preferanse",
                f"/api/vakter/999999/kandidater/{JONAS}/preferanse"):
        svar = klient.put(sti, json={"tekst": B})
        assert svar.status_code == 404, sti
        assert feilsvar("ikke_funnet")(svar.json())
    assert øyeblikksbilde(engine) == før
    assert ki.tekster == []


def test_annen_brukers_vakt_gir_404_og_endrer_ingenting(engine: Engine) -> None:
    okter = lag_sessionmaker(engine)
    with okter.begin() as session:
        annen = TurnusRad(avdeling="Annen avdeling", periode_start=PERIODE_START,
                          periode_slutt=PERIODE_SLUTT, sist_oppdatert=PERIODE_START)
        session.add(annen)
        session.flush()
        opprinnelig = session.scalars(select(BrukerRad)).one()
        session.add(BrukerRad(brukernavn="annen", navn="Annen bruker", passord_hash=opprinnelig.passord_hash,
                              passord_kilde=opprinnelig.passord_kilde, turnus_id=annen.id))
        session.execute(update(VaktRad).where(VaktRad.vaktnummer == 4127).values(turnus_id=annen.id))
    ki = FasitKi()
    klient = app_klient(engine, ki)
    før = øyeblikksbilde(engine)
    svar = klient.put(STI, json={"tekst": B})
    assert svar.status_code == 404
    assert øyeblikksbilde(engine) == før
    assert ki.tekster == []


def test_uten_ki_lagres_teksten_og_venter(engine: Engine) -> None:
    klient = app_klient(engine)
    svar = klient.put(STI, json={"tekst": B})
    assert svar.status_code == 200 and svar.json() == {"status": "venter"}
    etter = jonas(klient)
    assert (etter["tolkestatus"], etter["preferansepoeng"], etter["preferansetekst"]) == (
        "venter_paa_tolkning", 50, B)


def test_gammel_tolkning_brukes_ikke_for_ny_tekst(engine: Engine) -> None:
    tolk_ventende(lag_sessionmaker(engine), FasitKi())
    klient = app_klient(engine)
    assert jonas(klient)["tolkestatus"] == "tolket"
    assert klient.put(STI, json={"tekst": B}).json() == {"status": "venter"}
    etter = jonas(klient)
    assert (etter["tolkestatus"], etter["preferansekategori"]) == ("venter_paa_tolkning", None)


def test_endring_mens_godkjenning_er_åpen_gir_endret_grunnlag(engine: Engine) -> None:
    klient = app_klient(engine)
    gammelt = klient.get(GODKJENNING).json()["grunnlagsmerke"]
    assert klient.put(STI, json={"tekst": B}).json() == {"status": "venter"}
    svar = klient.post(GODKJENNING, json={"grunnlagsmerke": gammelt})
    assert svar.status_code == 409
    assert feilsvar("endret_grunnlag")(svar.json())
    nytt = klient.get(GODKJENNING).json()["grunnlagsmerke"]
    assert nytt != gammelt
    assert klient.post(GODKJENNING, json={"grunnlagsmerke": nytt}).status_code == 200


def test_tilbake_til_samme_tekst_gir_nytt_merke(engine: Engine) -> None:
    """A–B–A gir samme tekst, men versjonen gjør merket nytt (P-09)."""
    klient = app_klient(engine)
    gammelt = klient.get(GODKJENNING).json()["grunnlagsmerke"]
    assert klient.put(STI, json={"tekst": B}).json() == {"status": "venter"}
    assert klient.put(STI, json={"tekst": A}).json() == {"status": "venter"}
    assert klient.get(GODKJENNING).json()["grunnlagsmerke"] != gammelt
    assert klient.post(GODKJENNING, json={"grunnlagsmerke": gammelt}).status_code == 409


# --- A–B–A og samtidighet ---------------------------------------------------------


def test_a_b_a_under_prøv_igjen_forkaster_det_gamle_svaret(engine: Engine) -> None:
    """Endringene skjer mens KI-kallet for A pågår (`FasitKi(før=...)`)."""
    okter = lag_sessionmaker(engine)
    tolk_ventende(okter, FeilKi())

    def a_b_a(tekst: str) -> None:
        if tekst == A and jonas_rad(engine).preferanseversjon == 0:
            assert lagre_tekst(okter, JONAS, B) == 1
            assert lagre_tekst(okter, JONAS, A) == 2

    klient = app_klient(engine, FasitKi(før=a_b_a))
    assert klient.post(STI).json() == {"status": "endret"}
    rad = jonas_rad(engine)
    assert (rad.preferanse, rad.preferanseversjon, rad.tolket_kategori, rad.tolkefeil) == (A, 2, None, None)
    assert jonas(klient)["tolkestatus"] == "venter_paa_tolkning"


def test_a_b_a_under_oppstartstolkning_forkaster_det_gamle_svaret(engine: Engine) -> None:
    okter = lag_sessionmaker(engine)

    def a_b_a(tekst: str) -> None:
        if tekst == A and jonas_rad(engine).preferanseversjon == 0:
            lagre_tekst(okter, JONAS, B)
            lagre_tekst(okter, JONAS, A)

    tolk_ventende(okter, FasitKi(før=a_b_a))
    rad = jonas_rad(engine)
    assert (rad.preferanse, rad.preferanseversjon, rad.tolket_kategori) == (A, 2, None)


def test_a_b_a_over_http_tolker_bare_siste_a(engine: Engine) -> None:
    """Kall på A pågår («Prøv igjen»); B og så A lagres og venter på låsen. Svaret på
    den første A forkastes, B tolkes aldri, og den siste A tolkes."""
    okter = lag_sessionmaker(engine)
    tolk_ventende(okter, FeilKi())
    startet, fortsett = threading.Event(), threading.Event()

    def vent(_tekst: str) -> None:
        if not startet.is_set():
            startet.set()
            assert fortsett.wait(10)

    ki = FasitKi(før=vent)
    klient = app_klient(engine, ki)
    prøv: list = []
    b_svar: list = []
    a_svar: list = []
    tråder = [threading.Thread(target=lambda: prøv.append(klient.post(STI)))]
    tråder[0].start()
    try:
        assert startet.wait(10)
        tråder.append(i_tråd(klient, B, b_svar))
        vent_til(lambda: jonas_rad(engine).preferanseversjon == 1)
        tråder.append(i_tråd(klient, A, a_svar))
        vent_til(lambda: jonas_rad(engine).preferanseversjon == 2)
    finally:
        fortsett.set()
        for tråd in tråder:
            tråd.join(10)
    assert not any(t.is_alive() for t in tråder)
    assert prøv[0].json() == {"status": "endret"}
    assert b_svar[0].json() == {"status": "endret"}
    assert a_svar[0].json() == {"status": "tolket"}
    assert ki.tekster == [A, A]
    rad = jonas_rad(engine)
    assert (rad.preferanse, rad.preferanseversjon, rad.tolket_kategori) == (A, 2, "positiv_ved_behov")


def test_samtidig_ny_endring_forkaster_det_første_svaret(engine: Engine) -> None:
    startet, fortsett = threading.Event(), threading.Event()

    def vent(tekst: str) -> None:
        if tekst == B:
            startet.set()
            assert fortsett.wait(10)

    ki = FasitKi(før=vent)
    klient = app_klient(engine, ki)
    første: list = []
    andre: list = []
    tråder = [i_tråd(klient, B, første)]
    try:
        assert startet.wait(10)
        tråder.append(i_tråd(klient, C, andre))
        vent_til(lambda: jonas_rad(engine).preferanseversjon == 2)
    finally:
        fortsett.set()
        for tråd in tråder:
            tråd.join(10)
    assert not any(t.is_alive() for t in tråder)
    assert første[0].json() == {"status": "endret"}
    assert andre[0].json() == {"status": "tolket"}
    assert ki.tekster == [B, C]
    rad = jonas_rad(engine)
    assert (rad.preferanse, rad.tolket_kategori) == (C, "onsker_flere")


def test_låsen_blir_ikke_ledig_i_tide_gir_venter(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "LAASEVENT_S", 0.05)
    tolk_ventende(lag_sessionmaker(engine), FeilKi())
    startet, fortsett = threading.Event(), threading.Event()

    def vent(tekst: str) -> None:
        if tekst == A:
            startet.set()
            assert fortsett.wait(10)

    ki = FasitKi(før=vent)
    klient = app_klient(engine, ki)
    prøv: list = []
    tråd = threading.Thread(target=lambda: prøv.append(klient.post(STI)))
    tråd.start()
    try:
        assert startet.wait(10)
        svar = klient.put(STI, json={"tekst": B})
        assert svar.json() == {"status": "venter"}
    finally:
        fortsett.set()
        tråd.join(10)
    assert prøv[0].json() == {"status": "endret"}
    assert ki.tekster == [A]
    assert jonas(klient)["tolkestatus"] == "venter_paa_tolkning"


def test_demo_modus_tolker_ukjent_tekst_som_feilet(engine: Engine) -> None:
    """Demo-modus tillater endring; en ukjent tekst har ingen forhåndsgenerert tolkning."""
    from adaptere.ki.demo import DemoKiAdapter

    klient = app_klient(engine, DemoKiAdapter())
    assert klient.get("/api/meg").json()["demomodus"] is True
    assert klient.put(STI, json={"tekst": "En helt ny tekst som ikke finnes i demoinnholdet."}).json() == {
        "status": "feilet"}
    assert klient.put(STI, json={"tekst": B}).json() == {"status": "tolket"}
    assert jonas(klient)["preferansepoeng"] == 0
