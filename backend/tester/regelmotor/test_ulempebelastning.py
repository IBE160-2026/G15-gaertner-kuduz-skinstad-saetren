"""Fasiten er regnet fra kategorigrensene i KS-03, uavhengig av koden."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor.ulempebelastning import beregn_ulempebelastning, vindu
from domene.regelmotor.vurdering import vurder_kandidater
from domene.typer import Kandidat, Kandidatvurdering, Tidsrom, Vakt

OSLO = ZoneInfo("Europe/Oslo")


def lokal(y, m, d, h, minute=0):
    return datetime(y, m, d, h, minute, tzinfo=OSLO)


def beregn(start, slutt, *, tak=300):
    vakt = Vakt(1, "dag", slutt + timedelta(days=1), slutt + timedelta(days=1, hours=8), 1, None)
    kandidat = Kandidat(1, "Test", {}, (Tidsrom(start, slutt),))
    return beregn_ulempebelastning(kandidat, vakt, tak=tak)


@pytest.mark.parametrize(("start", "slutt", "timer", "poeng"), [
    (lokal(2026, 11, 13, 7), lokal(2026, 11, 13, 15), (8, 0, 0, 0), 0),
    (lokal(2026, 11, 13, 10), lokal(2026, 11, 13, 18), (8, 0, 0, 0), 0),
    (lokal(2026, 11, 13, 15), lokal(2026, 11, 13, 23), (3, 4, 0, 1), 7),
    (lokal(2026, 11, 13, 23), lokal(2026, 11, 14, 7), (0, 0, 1, 7), 23),
    (lokal(2026, 11, 14, 7), lokal(2026, 11, 14, 15), (0, 0, 8, 0), 16),
    (lokal(2026, 11, 14, 10), lokal(2026, 11, 14, 18), (0, 0, 8, 0), 16),
    (lokal(2026, 11, 14, 15), lokal(2026, 11, 14, 23), (0, 0, 7, 1), 17),
    (lokal(2026, 11, 15, 23), lokal(2026, 11, 16, 7), (1, 0, 0, 7), 21),
    (lokal(2026, 3, 28, 23), lokal(2026, 3, 29, 7), (0, 0, 1, 6), 20),
    (lokal(2026, 10, 24, 23), lokal(2026, 10, 25, 7), (0, 0, 1, 8), 26),
    (lokal(2026, 11, 13, 17, 30), lokal(2026, 11, 13, 22, 30), (0.5, 4, 0, 0.5), 5.5),
    (lokal(2026, 11, 14, 5, 30), lokal(2026, 11, 14, 6, 30), (0, 0, 0.5, 0.5), 2.5),
])
def test_kategorier(start, slutt, timer, poeng):
    resultat = beregn(start, slutt)
    assert (resultat.dagtimer, resultat.kveldstimer, resultat.helgetimer, resultat.natttimer) == timer
    assert resultat.poeng == poeng
    assert resultat.score == 100 * (1 - poeng / 300)


@pytest.mark.parametrize(("start", "forventet_lokal_start"), [
    (lokal(2026, 4, 10, 12), lokal(2026, 3, 13, 11)),
    (lokal(2026, 11, 10, 12), lokal(2026, 10, 13, 13)),
])
def test_vindu_er_672_faktiske_timer_og_klipper_begge_grenser(start, forventet_lokal_start):
    vakt = Vakt(1, "dag", start, start + timedelta(hours=8), 1, None)
    måling = vindu(vakt)
    assert måling.slutt - måling.start == timedelta(hours=672)
    assert måling.start.astimezone(OSLO) == forventet_lokal_start
    kandidat = Kandidat(1, "Test", {}, (
        Tidsrom(måling.start - timedelta(minutes=30), måling.start + timedelta(minutes=30)),
        Tidsrom(måling.slutt - timedelta(minutes=30), måling.slutt + timedelta(minutes=30)),
        Tidsrom(måling.start - timedelta(hours=2), måling.start),
        Tidsrom(måling.slutt, måling.slutt + timedelta(hours=2)),
    ))
    resultat = beregn_ulempebelastning(kandidat, vakt)
    assert sum((resultat.dagtimer, resultat.kveldstimer, resultat.helgetimer, resultat.natttimer)) == 1
    # Begge klippede halvtimeintervaller ligger på dagtid en fredag/tirsdag.
    assert (resultat.dagtimer, resultat.kveldstimer, resultat.helgetimer, resultat.natttimer) == (1, 0, 0, 0)
    assert resultat.poeng == 0


@pytest.mark.parametrize(("time", "før", "etter", "poeng"), [
    (6, "natttimer", "dagtimer", 3 / 60),
    (18, "dagtimer", "kveldstimer", 1 / 60),
    (22, "kveldstimer", "natttimer", 4 / 60),
])
def test_hverdagsgrense_på_minuttet(time, før, etter, poeng):
    grense = lokal(2026, 11, 13, time)
    resultat = beregn(grense - timedelta(minutes=1), grense + timedelta(minutes=1))
    assert getattr(resultat, før) == pytest.approx(1 / 60)
    assert getattr(resultat, etter) == pytest.approx(1 / 60)
    assert resultat.poeng == pytest.approx(poeng)


def test_overlapp_og_duplikat_telles_en_gang():
    start, slutt = lokal(2026, 11, 13, 17), lokal(2026, 11, 13, 23)
    vakt = Vakt(1, "dag", lokal(2026, 11, 16, 7), lokal(2026, 11, 16, 15), 1, None)
    kandidat = Kandidat(1, "Test", {}, (Tidsrom(start, slutt), Tidsrom(start, slutt),
                                         Tidsrom(lokal(2026, 11, 13, 20), lokal(2026, 11, 14, 1))))
    resultat = beregn_ulempebelastning(kandidat, vakt)
    assert (resultat.dagtimer, resultat.kveldstimer, resultat.natttimer, resultat.poeng) == (1, 4, 3, 13)


def test_tomt_grunnlag_og_parameterisert_tak():
    start = lokal(2026, 11, 13, 18)
    vakt = Vakt(1, "dag", lokal(2026, 11, 16, 7), lokal(2026, 11, 16, 15), 1, None)
    tom = Kandidat(1, "Test", {})
    assert beregn_ulempebelastning(tom, vakt).score == 100
    kandidat = Kandidat(1, "Test", {}, (Tidsrom(start, start + timedelta(hours=1)),))
    assert beregn_ulempebelastning(kandidat, vakt, tak=2).score == 50
    assert beregn_ulempebelastning(kandidat, vakt, tak=1).score == 0
    assert beregn_ulempebelastning(kandidat, vakt, tak=0.5).score == 0
    for ugyldig in (0, -1, float("nan"), float("inf"), True):
        with pytest.raises(ValueError):
            beregn_ulempebelastning(kandidat, vakt, tak=ugyldig)


def test_standardtak_300_og_over_300():
    vakt = Vakt(1, "dag", lokal(2026, 11, 20, 7), lokal(2026, 11, 20, 15), 1, None)
    # Tolv vakter à åtte natttimer og én på fire: 100 × 3 = 300.
    vakter = tuple(Tidsrom(lokal(2026, 11, dag, 22), lokal(2026, 11, dag + 1, 6))
                   for dag in range(1, 13)) + (Tidsrom(lokal(2026, 11, 13, 22), lokal(2026, 11, 14, 2)),)
    ved_taket = beregn_ulempebelastning(Kandidat(1, "A", {}, vakter), vakt)
    over_taket = beregn_ulempebelastning(
        Kandidat(2, "B", {}, vakter + (Tidsrom(lokal(2026, 11, 14, 2), lokal(2026, 11, 14, 3)),)), vakt,
    )
    assert (ved_taket.natttimer, ved_taket.poeng, ved_taket.score) == (100, 300, 0)
    assert (over_taket.natttimer, over_taket.poeng, over_taket.score) == (101, 303, 0)


def test_like_poeng_er_uavhengig_av_andre_kandidater_og_gjentakelse():
    vakt = Vakt(1, "dag", lokal(2026, 11, 16, 7), lokal(2026, 11, 16, 15), 1, None)
    a = Kandidat(1, "A", {"dag": 1}, (Tidsrom(lokal(2026, 11, 13, 18), lokal(2026, 11, 13, 22)),))
    b = Kandidat(2, "B", {"dag": 1}, (Tidsrom(lokal(2026, 11, 13, 21), lokal(2026, 11, 13, 23)),))
    c = Kandidat(3, "C", {"dag": 1}, ())
    def vurder(kandidater):
        result = vurder_kandidater(vakt, kandidater, lokal(2026, 12, 1, 0), lokal(2026, 10, 1, 0))
        assert isinstance(result, Kandidatvurdering)
        return result.ulempe_per_kandidat
    alene = vurder((a, b))
    sammen = vurder((c, b, a))
    assert alene == vurder((a, b))
    assert alene[1] == sammen[1] and alene[2] == sammen[2]
    # A: 4 × 1; B: 1 × 1 + 1 × 3. Samme score, ulik fordeling.
    assert alene[1].poeng == alene[2].poeng == 4
    assert alene[1].score == alene[2].score == 100 * (1 - 4 / 300)
    assert (alene[1].kveldstimer, alene[1].natttimer) == (4, 0)
    assert (alene[2].kveldstimer, alene[2].natttimer) == (1, 1)


def test_beregner_kun_for_gyldige(monkeypatch):
    from domene.regelmotor import ulempebelastning

    vakt = Vakt(1, "dag", lokal(2026, 11, 16, 7), lokal(2026, 11, 16, 15), 1, None)
    gyldig = Kandidat(1, "A", {"dag": 1})
    utelukket = Kandidat(2, "B", {})
    kall = []
    original = ulempebelastning.beregn_ulempebelastning

    def observer(kandidat, vakt):
        kall.append(kandidat.id)
        return original(kandidat, vakt)

    monkeypatch.setattr(ulempebelastning, "beregn_ulempebelastning", observer)
    resultat = vurder_kandidater(vakt, (gyldig, utelukket), lokal(2026, 12, 1, 0), lokal(2026, 10, 1, 0))
    assert isinstance(resultat, Kandidatvurdering)
    assert [k.id for k in resultat.gyldige] == [1]
    assert [u.kandidat.id for u in resultat.utelukkede] == [2]
    assert kall == [1]
