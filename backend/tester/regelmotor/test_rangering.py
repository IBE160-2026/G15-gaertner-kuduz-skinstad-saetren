"""Rangering av Gyldige kandidater (story 4.4, FR9, PRD §4.4).

Fasitene er regnet for hånd fra formelen (KS-02), ikke kopiert fra programmet
(AV-07). Brøkene står i kommentarene. Testene sammenligner med `float(Fraction(...))`,
som er den korrekt avrundede verdien av den eksakte brøken.

Kandidatene i de syntetiske testene har bare dagtimer på hverdager i uka Vakten
starter i, så ulempen er 0 p (Ulempescore 100), og ingen kostnad har overtid.
"""

import random
import re
from dataclasses import replace
from datetime import datetime, timedelta
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Engine, select

from adaptere.lagring.database import lag_sessionmaker
from adaptere.lagring.kandidatgrunnlag import hent_kandidatgrunnlag
from adaptere.lagring.modeller import BrukerRad
from adaptere.lagring.testdata import FASIT
from domene.porter.rangering import TolketPreferanse, Tolkestatus
from domene.regelmotor.rangering import (
    PREFERANSEPOENG,
    STANDARD_PARAMETERE,
    Rangeringsparametere,
    minmaks,
    ranger,
    totalscore,
)
from domene.regelmotor.kostnad import beregn_kostnad
from domene.regelmotor.timebelastning import timebelastning
from domene.regelmotor.timer_i_uka import timer_i_startuka
from domene.regelmotor.vurdering import vurder_kandidater
from domene.typer import Datafeil, Kandidat, Kandidatvurdering, Tidsrom, Ulempebelastning, Vakt
from tester.api.test_innlogging import engine  # noqa: F401


def tolket(kategori: str) -> TolketPreferanse:
    return TolketPreferanse(kategori, "Testbegrunnelse.", "test/modell")


OSLO = ZoneInfo("Europe/Oslo")
BACKEND = Path(__file__).resolve().parents[2]

# Torsdag 05.11.2026 07–15. Uka er mandag 02.11 til mandag 09.11.
VAKT = Vakt(1, "dag", datetime(2026, 11, 5, 7, tzinfo=OSLO), datetime(2026, 11, 5, 15, tzinfo=OSLO), 3, None)
HISTORIKKSTART = datetime(2026, 9, 1, tzinfo=OSLO)
DATAGRENSE = datetime(2026, 12, 1, tzinfo=OSLO)
TEKST = "Hvis dere mangler folk, stiller jeg gjerne på en ekstravakt."


def kandidat(
    id_: int, *, lønn: int = 300, timer: int = 0, nivå: int = 3, preferanse: str | None = TEKST,
) -> Kandidat:
    """`timer` dagtimer i uka: inntil 11 t mandag fra 07:00, resten tirsdag fra 07:00."""
    vakter = []
    if timer:
        mandag = datetime(2026, 11, 2, 7, tzinfo=OSLO)
        vakter.append(Tidsrom(mandag, mandag + timedelta(hours=min(timer, 11))))
    if timer > 11:
        tirsdag = datetime(2026, 11, 3, 7, tzinfo=OSLO)
        vakter.append(Tidsrom(tirsdag, tirsdag + timedelta(hours=timer - 11)))
    return Kandidat(id_, f"Ansatt {id_}", {"dag": nivå}, tuple(vakter), timelønn=lønn, preferanse=preferanse)


def vurder(*kandidater: Kandidat, vakt: Vakt = VAKT) -> Kandidatvurdering:
    vurdering = vurder_kandidater(vakt, kandidater, DATAGRENSE, HISTORIKKSTART)
    assert not isinstance(vurdering, Datafeil), vurdering
    assert not vurdering.utelukkede
    return vurdering


def plasser(rangert) -> list[int]:  # type: ignore[no-untyped-def]
    return [r.id for r in rangert]


# --- Fasiten for #4127 (AV-07, AV-12) --------------------------------------------


def seed_4127(engine: Engine) -> tuple[Kandidatvurdering, Vakt]:
    with lag_sessionmaker(engine)() as session:
        bruker_id = session.scalars(select(BrukerRad.id)).first()
        grunnlag = hent_kandidatgrunnlag(session, bruker_id, 4127)
    assert grunnlag is not None
    vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
    assert isinstance(vurdering, Kandidatvurdering)
    return vurdering, grunnlag.vakt


# Seeden (story 1.2): kostnad Jonas og Mette 2960, Thomas 2800, Ingrid 3850 kr.
# Min–maks over 1050 kr: Jonas og Mette 100 × 890/1050 = 1780/21, Thomas 100, Ingrid 0.
# Timer 16/16/24/32 over 16 t: 100/100/50/0. Ulempe 40/180/120/60 p mot tak 300:
# 260/3, 40, 60 og 80.
FAKTORER_4127 = {
    "Jonas Bakke": (Fraction(1780, 21), Fraction(100), Fraction(260, 3)),
    "Mette Solberg": (Fraction(1780, 21), Fraction(100), Fraction(40)),
    "Thomas Nygård": (Fraction(100), Fraction(50), Fraction(60)),
    "Ingrid Dahl": (Fraction(0), Fraction(0), Fraction(80)),
}
# Tolket: 2/5 × 1780/21 + 1/5 × 100 + 3/20 × 260/3 + 1/4 × 75 = 712/21 + 20 + 13 + 75/4 = 7195/84.
# Mette: 712/21 + 20 + 6 + 75/4 = 6607/84. Thomas: 40 + 10 + 9 + 0 = 59. Ingrid: 0 + 0 + 12 + 25 = 37.
TOLKET_4127 = [
    ("Jonas Bakke", Fraction(7195, 84)), ("Mette Solberg", Fraction(6607, 84)),
    ("Thomas Nygård", Fraction(59)), ("Ingrid Dahl", Fraction(37)),
]
# 50 for alle: Jonas 712/21 + 20 + 13 + 25/2 = 3335/42, Mette 712/21 + 20 + 6 + 25/2 = 3041/42,
# Thomas 40 + 10 + 9 + 25/2 = 143/2, Ingrid 12 + 25/2 = 49/2.
UTEN_TOLKNING_4127 = [
    ("Jonas Bakke", Fraction(3335, 42)), ("Mette Solberg", Fraction(3041, 42)),
    ("Thomas Nygård", Fraction(143, 2)), ("Ingrid Dahl", Fraction(49, 2)),
]
# Kategoriene for seedtekstene nr. 4, 5, 13 og 1 (PRD §4.5).
TOLKEDE_4127 = {
    6: tolket("positiv_ved_behov"),  # Jonas
    5: tolket("positiv_ved_behov"),  # Mette
    3: tolket("vil_unnga"),  # Thomas
    4: tolket("onsker_flere"),  # Ingrid
}


def test_fasit_4127_med_tolkede_preferanser(engine: Engine) -> None:  # noqa: F811
    vurdering, vakt = seed_4127(engine)
    rangert = ranger(vurdering, vakt, TOLKEDE_4127)

    assert [(r.navn, r.totalscore) for r in rangert] == [(n, float(t)) for n, t in TOLKET_4127]
    assert [round(r.totalscore, 2) for r in rangert] == [85.65, 78.65, 59.0, 37.0]
    # Samme rekkefølge og totaler som `testdata.FASIT` fra story 1.2.
    fasit = FASIT[4127]["rangering"]
    assert [r.navn for r in rangert] == [f["navn"] for f in fasit]
    assert [r.totalscore for r in rangert] == pytest.approx([f["totalscore"] for f in fasit], abs=1e-12)
    assert [r.preferansepoeng for r in rangert] == [f["preferansepoeng"] for f in fasit]
    assert [r.plass for r in rangert] == [1, 2, 3, 4]
    assert {r.tolkestatus for r in rangert} == {Tolkestatus.TOLKET}
    assert [r.tolket_preferanse for r in rangert] == [TOLKEDE_4127[r.id] for r in rangert]
    for r in rangert:
        assert (r.kostnadspoeng, r.timebelastningspoeng, r.ulempescore) == tuple(map(float, FAKTORER_4127[r.navn]))


def test_fasit_4127_uten_tolkning_gir_50_og_venter(engine: Engine) -> None:  # noqa: F811
    vurdering, vakt = seed_4127(engine)
    rangert = ranger(vurdering, vakt)

    assert [(r.navn, r.totalscore) for r in rangert] == [(n, float(t)) for n, t in UTEN_TOLKNING_4127]
    assert [round(r.totalscore, 2) for r in rangert] == [79.40, 72.40, 71.50, 24.50]
    assert {r.preferansepoeng for r in rangert} == {50.0}
    assert {r.tolkestatus for r in rangert} == {Tolkestatus.VENTER_PAA_TOLKNING}
    assert {r.tolket_preferanse for r in rangert} == {None}


@pytest.mark.parametrize("tolkede", [{}, TOLKEDE_4127])
def test_jonas_og_mette_skilles_med_nøyaktig_7_av_ulempen(engine: Engine, tolkede) -> None:  # noqa: F811
    # AV-12: 3/20 × (260/3 − 40) = 3/20 × 140/3 = 7.
    vurdering, vakt = seed_4127(engine)
    jonas, mette = ranger(vurdering, vakt, tolkede)[:2]
    assert (jonas.navn, mette.navn) == ("Jonas Bakke", "Mette Solberg")
    assert (jonas.kostnadspoeng, jonas.timebelastningspoeng, jonas.preferansepoeng) == (
        mette.kostnadspoeng, mette.timebelastningspoeng, mette.preferansepoeng)
    assert (jonas.ulempepoeng, mette.ulempepoeng) == (40, 180)
    assert jonas.totalscore - mette.totalscore == 7.0


@pytest.mark.parametrize("tolkede", [{}, TOLKEDE_4127])
def test_billigste_er_ikke_øverst(engine: Engine, tolkede) -> None:  # noqa: F811
    # FR9, SM-6: Thomas har lavest kostnad (2800 kr), men havner som nr. 3.
    vurdering, vakt = seed_4127(engine)
    rangert = ranger(vurdering, vakt, tolkede)
    billigst = min(rangert, key=lambda r: r.kostnad)
    assert billigst.navn == "Thomas Nygård"
    assert billigst.kostnadspoeng == 100
    assert billigst.plass == 3


def test_porten_bærer_fakta_for_fasiten(engine: Engine) -> None:  # noqa: F811
    vurdering, vakt = seed_4127(engine)
    ingrid = next(r for r in ranger(vurdering, vakt) if r.navn == "Ingrid Dahl")
    assert (ingrid.stilling, ingrid.ansiennitet, ingrid.kompetansenivå) == ("Sykepleier", 6, 4)
    assert (ingrid.kostnad, ingrid.ordinære_timer, ingrid.overtidstimer) == (3850, 4, 4)
    assert ingrid.kostnadstype == "inkluderer_overtid"
    assert ingrid.timer_i_uka == 32
    assert ingrid.timebelastning_prosent == pytest.approx(100 * 32 / 36)
    assert ingrid.høy_belastning is False
    assert ingrid.ulempepoeng == 60
    assert not hasattr(ingrid, "vakter")
    assert not hasattr(ingrid, "minutter_i_uka")


def test_porten_har_samme_fakta_som_beregningene_for_alle_fire(engine: Engine) -> None:  # noqa: F811
    vurdering, vakt = seed_4127(engine)
    gyldige = {k.id: k for k in vurdering.gyldige}
    rangert = ranger(vurdering, vakt)
    assert len(rangert) == 4
    for r in rangert:
        kostnad = beregn_kostnad(gyldige[r.id], vakt)
        belastning = timebelastning(timer_i_startuka(gyldige[r.id], vakt))
        ulempe = vurdering.ulempe_per_kandidat[r.id]
        assert (r.kostnad, r.ordinære_timer, r.overtidstimer) == (
            float(kostnad.total), float(kostnad.ordinære_timer), float(kostnad.overtidstimer))
        assert r.kostnadstype == ("inkluderer_overtid" if kostnad.overtidstimer > 0 else "ordinær")
        assert (r.timebelastning_prosent, r.høy_belastning) == (belastning.prosent, belastning.høy)
        assert (r.ulempepoeng, r.kveldstimer, r.helgetimer, r.natttimer) == (
            ulempe.poeng, ulempe.kveldstimer, ulempe.helgetimer, ulempe.natttimer)
    jonas = next(r for r in rangert if r.navn == "Jonas Bakke")
    assert jonas.kostnadstype == "ordinær"
    assert jonas.overtidstimer == 0


# --- Min–maks og like verdier (AV-05) --------------------------------------------


def test_én_gyldig_gir_50_for_kostnad_og_timer() -> None:
    (eneste,) = ranger(vurder(kandidat(1, lønn=350, timer=20)), VAKT)
    assert (eneste.kostnadspoeng, eneste.timebelastningspoeng) == (50, 50)
    # Ulempescoren har fast skala og er 100 uten ulempetimer.
    assert eneste.ulempescore == 100
    # 2/5 × 50 + 1/5 × 50 + 3/20 × 100 + 1/4 × 50 = 20 + 10 + 15 + 12,5.
    assert eneste.totalscore == 57.5
    assert eneste.plass == 1


def test_alle_like_gir_50_og_rekkefølge_etter_id() -> None:
    rangert = ranger(vurder(kandidat(3, timer=10), kandidat(1, timer=10), kandidat(2, timer=10)), VAKT)
    assert plasser(rangert) == [1, 2, 3]
    assert {(r.kostnadspoeng, r.timebelastningspoeng, r.totalscore) for r in rangert} == {(50, 50, 57.5)}


def test_minmaks_er_lineær_mellom_lavest_og_høyest() -> None:
    assert minmaks({1: Fraction(10), 2: Fraction(15), 3: Fraction(20)}) == {1: 100, 2: 50, 3: 0}
    assert minmaks({1: Fraction(7), 2: Fraction(7)}) == {1: 50, 2: 50}
    assert minmaks({}) == {}


def test_kostnad_og_timer_normaliseres_hver_for_seg() -> None:
    # Kostnad 2400/2440/2480 kr (lønn 300/305/310) gir 100/50/0. Timer 0/20/5 gir 100/0/75.
    rangert = {r.id: r for r in ranger(vurder(
        kandidat(1, lønn=300, timer=0), kandidat(2, lønn=305, timer=20), kandidat(3, lønn=310, timer=5),
    ), VAKT)}
    assert [(rangert[i].kostnadspoeng, rangert[i].timebelastningspoeng) for i in (1, 2, 3)] == [
        (100, 100), (50, 0), (0, 75)]
    # 1: 40 + 20 + 15 + 12,5 = 87,5. 2: 20 + 0 + 27,5 = 47,5. 3: 0 + 15 + 27,5 = 42,5.
    assert [rangert[i].totalscore for i in (1, 2, 3)] == [87.5, 47.5, 42.5]


def test_bare_kompetansen_er_ulik_gir_lik_totalscore() -> None:
    # FR2, FR9: nivå over minstekravet gir ingen poeng. Rekkefølgen følger ID uansett nivå.
    for nivåer in ((3, 4), (4, 3)):
        rangert = ranger(vurder(kandidat(2, nivå=nivåer[1]), kandidat(1, nivå=nivåer[0])), VAKT)
        assert plasser(rangert) == [1, 2]
        assert rangert[0].totalscore == rangert[1].totalscore
        assert {r.kompetansenivå for r in rangert} == {3, 4}


def test_matematisk_like_totaler_er_like_uten_toleranse() -> None:
    # Eksempelet fra referatet §11: [0, 0, 0, 300/7] mot [0, 100/7, 200/7, 100/7] gir begge 75/7.
    a = totalscore(Fraction(0), Fraction(0), Fraction(0), Fraction(300, 7))
    b = totalscore(Fraction(0), Fraction(100, 7), Fraction(200, 7), Fraction(100, 7))
    assert a == b == Fraction(75, 7)
    # Med flyttall skiller de seg i siste siffer, og ID-regelen ville ikke slått inn.
    assert 0.25 * (300 / 7) != 0.2 * (100 / 7) + 0.15 * (200 / 7) + 0.25 * (100 / 7)


def test_lik_total_med_ulike_faktorer_sorteres_etter_id() -> None:
    # Lønn 300–307 kr gir 2400–2456 kr, et spenn på 56 kr. Timer 8–15 gir et spenn på 7 t.
    # Nr. 1: dyrest (kostnadspoeng 0) og 12 t (100 × 3/7 = 300/7).
    # Nr. 2: lønn 306 (100 × 8/56 = 100/7) og 14 t (100/7).
    # Med 0 preferansepoeng og Ulempescore 100: 1/5 × 300/7 = 2/5 × 100/7 + 1/5 × 100/7 = 60/7.
    vurdering = vurder(
        kandidat(1, lønn=307, timer=12, preferanse=TEKST),
        kandidat(2, lønn=306, timer=14, preferanse=TEKST),
        kandidat(10, lønn=300, timer=8), kandidat(11, lønn=307, timer=15),
    )
    tolkede = {1: tolket("vil_unnga"), 2: tolket("vil_unnga")}
    rangert = {r.id: r for r in ranger(vurdering, VAKT, tolkede)}
    én, to = rangert[1], rangert[2]
    assert (én.kostnadspoeng, én.timebelastningspoeng) == (0, float(Fraction(300, 7)))
    assert (to.kostnadspoeng, to.timebelastningspoeng) == (float(Fraction(100, 7)), float(Fraction(100, 7)))
    assert én.totalscore == to.totalscore == float(Fraction(60, 7) + 15)
    assert to.plass == én.plass + 1
    # Kontroll av testen: flyttall i samme rekkefølge ville satt nr. 2 foran nr. 1.
    flyt = [0.4 * kp + 0.2 * tp + 0.15 * 100 + 0.25 * 0
            for kp, tp in ((0.0, 100 * 3 / 7), (100 * 8 / 56, 100 * 1 / 7))]
    assert flyt[1] > flyt[0]


# --- Preferanse og tolkestatus (P-05) --------------------------------------------


@pytest.mark.parametrize(("kategori", "poeng"), [
    ("onsker_flere", 100), ("positiv_ved_behov", 75), ("noytral", 50), ("foretrekker_a_slippe", 25), ("vil_unnga", 0),
])
def test_tolket_kategori_gir_fast_poeng(kategori: str, poeng: int) -> None:
    tolkning = tolket(kategori)
    (r,) = ranger(vurder(kandidat(1)), VAKT, {1: tolkning})
    assert (r.preferansepoeng, r.tolkestatus, r.tolket_preferanse) == (poeng, Tolkestatus.TOLKET, tolkning)
    assert PREFERANSEPOENG[kategori] == poeng
    # 20 + 10 + 15 + 1/4 × poeng.
    assert r.totalscore == 45 + poeng / 4


def test_alle_fire_tolkestatuser() -> None:
    vurdering = vurder(
        kandidat(1), kandidat(2), kandidat(3), kandidat(4, preferanse=None), kandidat(5, preferanse="   "),
    )
    rangert = {r.id: r for r in ranger(vurdering, VAKT, {1: tolket("onsker_flere")}, frozenset({2}))}
    assert {i: (r.tolkestatus, r.preferansepoeng) for i, r in rangert.items()} == {
        1: (Tolkestatus.TOLKET, 100),
        2: (Tolkestatus.KUNNE_IKKE_TOLKES, 50),
        3: (Tolkestatus.VENTER_PAA_TOLKNING, 50),
        4: (Tolkestatus.INGEN_REGISTRERT, 50),
        5: (Tolkestatus.INGEN_REGISTRERT, 50),
    }
    assert [rangert[i].tolket_preferanse for i in (2, 3, 4, 5)] == [None] * 4
    # Ingen status utelukker: alle fem er rangert.
    assert sorted(rangert) == [1, 2, 3, 4, 5]


def test_ugyldig_kategori_følger_feilflyten() -> None:
    (r,) = ranger(vurder(kandidat(1)), VAKT, {1: tolket("uklar")})
    assert (r.tolkestatus, r.preferansepoeng, r.tolket_preferanse) == (Tolkestatus.KUNNE_IKKE_TOLKES, 50, None)


def test_lagret_tolkning_går_foran_feil_men_ikke_manglende_tekst() -> None:
    tolkning = tolket("vil_unnga")
    (med_tekst,) = ranger(vurder(kandidat(1)), VAKT, {1: tolkning}, frozenset({1}))
    assert (med_tekst.tolkestatus, med_tekst.preferansepoeng) == (Tolkestatus.TOLKET, 0)
    (uten_tekst,) = ranger(vurder(kandidat(1, preferanse=None)), VAKT, {1: tolkning})
    assert (uten_tekst.tolkestatus, uten_tekst.preferansepoeng) == (Tolkestatus.INGEN_REGISTRERT, 50)


# --- Bare Gyldige rangeres (NFR2, AD-1) ------------------------------------------


def test_utelukkede_rangeres_aldri() -> None:
    utelukket = kandidat(9, nivå=1, lønn=200)  # under minstenivå 3
    vurdering = vurder_kandidater(VAKT, [kandidat(1), utelukket, kandidat(2)], DATAGRENSE, HISTORIKKSTART)
    assert isinstance(vurdering, Kandidatvurdering)
    assert [u.kandidat.id for u in vurdering.utelukkede] == [9]
    rangert = ranger(vurdering, VAKT, {9: tolket("onsker_flere")}, frozenset({9}))
    assert plasser(rangert) == [1, 2]
    # Den utelukkede er billigst, men påvirker ikke min–maks: begge har samme kostnad og får 50.
    assert {r.kostnadspoeng for r in rangert} == {50}


def test_ingen_gyldige_gir_tom_rangering() -> None:
    vurdering = vurder_kandidater(VAKT, [kandidat(9, nivå=1)], DATAGRENSE, HISTORIKKSTART)
    assert isinstance(vurdering, Kandidatvurdering)
    assert ranger(vurdering, VAKT) == ()


def test_bare_regelmotoren_konstruerer_rangertkandidat() -> None:
    kall = re.compile(r"\bRangertKandidat\(")
    tillatt = {BACKEND / "domene" / "regelmotor" / "rangering.py"}
    funnet = [
        sti.relative_to(BACKEND).as_posix()
        for mappe in ("domene", "adaptere")
        for sti in (BACKEND / mappe).rglob("*.py")
        if sti not in tillatt and kall.search(sti.read_text(encoding="utf-8"))
    ]
    assert funnet == []


# --- Over fem gyldige (FR9, SM-3) ------------------------------------------------


def test_alle_gyldige_rangeres_og_minmaks_bruker_alle() -> None:
    # Lønn 300, 301, …, 306 kr gir 2400–2448 kr. Alle har 10 t, så timer gir 50.
    # Nr. 7 (dyrest) setter nullpunktet: nr. 2 (2408 kr) får 100 × 40/48 = 250/3, ikke
    # 100 × 24/32 = 75, som det ville blitt med min–maks over bare de fem øverste.
    vurdering = vurder(*(kandidat(i, lønn=299 + i, timer=10) for i in range(1, 8)))
    rangert = ranger(vurdering, VAKT)
    assert plasser(rangert) == [1, 2, 3, 4, 5, 6, 7]
    assert [r.plass for r in rangert] == [1, 2, 3, 4, 5, 6, 7]
    assert rangert[1].kostnadspoeng == float(Fraction(250, 3))
    assert rangert[-1].kostnadspoeng == 0


# --- Determinisme (NFR1, SM-5) ---------------------------------------------------


def test_samme_input_i_ulik_rekkefølge_gir_samme_rangering() -> None:
    kandidater = [
        kandidat(1, lønn=307, timer=12), kandidat(2, lønn=306, timer=14), kandidat(3, lønn=300, timer=8),
        kandidat(4, lønn=307, timer=15), kandidat(5, timer=10, preferanse=None), kandidat(6, nivå=4, timer=10),
    ]
    tolkede = {1: tolket("vil_unnga"), 2: tolket("vil_unnga")}
    forventet = ranger(vurder(*kandidater), VAKT, tolkede)
    tilfeldig = random.Random(4127)
    for _ in range(20):
        stokket = kandidater[:]
        tilfeldig.shuffle(stokket)
        assert ranger(vurder(*stokket), VAKT, tolkede) == forventet
        # Også når `gyldige` kommer i en annen rekkefølge enn `vurder_kandidater` gir.
        vurdering = vurder(*stokket)
        omvendt = replace(vurdering, gyldige=tuple(reversed(vurdering.gyldige)))
        assert ranger(omvendt, VAKT, tolkede) == forventet


# --- Parametere (AV-11) ----------------------------------------------------------


def test_standardparameterne_er_vedtaket() -> None:
    p = STANDARD_PARAMETERE
    assert (p.kostnadsvekt, p.timebelastningsvekt, p.ulempevekt, p.preferansevekt) == (
        Fraction(2, 5), Fraction(1, 5), Fraction(3, 20), Fraction(1, 4))
    assert p.tak == 300


def test_vektene_kan_varieres() -> None:
    # Bare kostnad: den billigste først. Bare timer: den med færrest timer først.
    vurdering = vurder(kandidat(1, lønn=310, timer=0), kandidat(2, lønn=300, timer=20))
    bare_kostnad = Rangeringsparametere(1, 0, 0, 0)
    bare_timer = Rangeringsparametere(0, 1, 0, 0)
    assert plasser(ranger(vurdering, VAKT, parametere=bare_kostnad)) == [2, 1]
    assert plasser(ranger(vurdering, VAKT, parametere=bare_timer)) == [1, 2]
    assert [r.totalscore for r in ranger(vurdering, VAKT, parametere=bare_kostnad)] == [100, 0]
    # Standardvektene: nr. 1 får 0 + 20 + 15 + 12,5 = 47,5, nr. 2 får 40 + 0 + 15 + 12,5 = 67,5.
    assert [(r.id, r.totalscore) for r in ranger(vurdering, VAKT)] == [(2, 67.5), (1, 47.5)]


def test_taket_kan_varieres(engine: Engine) -> None:  # noqa: F811
    # Jonas har 40 p. Med tak 600: 100 × (1 − 40/600) = 280/3. Over taket gir 0.
    vurdering, vakt = seed_4127(engine)
    jonas = next(r for r in ranger(vurdering, vakt, parametere=Rangeringsparametere(tak=600)) if r.id == 6)
    assert jonas.ulempescore == float(Fraction(280, 3))
    mette = next(r for r in ranger(vurdering, vakt, parametere=Rangeringsparametere(tak=100)) if r.id == 5)
    assert mette.ulempescore == 0


@pytest.mark.parametrize("vekter", [
    (0.4, 0.2, 0.15, 0.25),  # flyttall summerer ikke eksakt
    (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)),  # negativ vekt
    (Fraction(1, 2), 0, 0, 0),  # summerer ikke til 1
    (True, 0, 0, 0),
])
def test_ugyldige_vekter_avvises(vekter) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError):
        Rangeringsparametere(*vekter)


@pytest.mark.parametrize("tak", [0, -1, float("inf"), float("nan"), True, "300"])
def test_ugyldig_tak_avvises(tak) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError):
        Rangeringsparametere(tak=tak)


def test_ulempescore_regnes_fra_poeng_med_parameterens_tak() -> None:
    # 150 p mot tak 300 gir 50; samme vurdering med tak 200 gir 25.
    vurdering = vurder(kandidat(1))
    ulempe = Ulempebelastning(dagtimer=0, kveldstimer=0, helgetimer=0, natttimer=50, poeng=150, score=50)
    vurdering = replace(vurdering, ulempe_per_kandidat={1: ulempe})
    assert ranger(vurdering, VAKT)[0].ulempescore == 50
    assert ranger(vurdering, VAKT, parametere=Rangeringsparametere(tak=200))[0].ulempescore == 25
