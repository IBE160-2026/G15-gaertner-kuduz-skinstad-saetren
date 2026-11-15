from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor.kostnad import beregn_kostnad
from domene.regelmotor.vurdering import vurder_kandidater
from domene.typer import Datafeil, Kandidat, Tidsrom, Vakt

OSLO = ZoneInfo('Europe/Oslo')


def tid(dag, time=0, minute=0, month=11):
    return datetime(2026, month, dag, time, minute, tzinfo=OSLO)


@pytest.mark.parametrize('timer,ordinær,overtid,total', [
    (28, 8, 0, 2400), (32, 4, 4, 3000), (40, 0, 8, 3600),
])
def test_uketerskel(timer, ordinær, overtid, total):
    kandidat = Kandidat(1, 'A', {}, (Tidsrom(tid(2), tid(2) + timedelta(hours=timer)),), timelønn=300)
    vakt = Vakt(1, 'dag', tid(6, 7), tid(6, 15), 1, None)
    resultat = beregn_kostnad(kandidat, vakt)
    assert (resultat.ordinære_timer, resultat.overtidstimer, resultat.total) == (ordinær, overtid, total)
    assert resultat == beregn_kostnad(kandidat, vakt)


def test_ukeskifte_og_overlapp():
    kandidat = Kandidat(1, 'A', {}, (Tidsrom(tid(2), tid(3, 12)), Tidsrom(tid(2), tid(2, 4)), Tidsrom(tid(9), tid(9, 20))), timelønn=300)
    vakt = Vakt(1, 'natt', tid(8, 23), tid(9, 7), 1, None)
    resultat = beregn_kostnad(kandidat, vakt)
    # Den andre uka overlapper de sju timene fra vakten med eksisterende arbeid.
    assert resultat.total == 450
    assert resultat.overtidstimer == 1


def test_ukeskifte_hver_uke_har_egen_grense():
    kandidat = Kandidat(1, 'A', {}, (Tidsrom(tid(2), tid(3, 12)), Tidsrom(tid(10), tid(10, 20))), timelønn=300)
    vakt = Vakt(1, 'natt', tid(8, 23), tid(9, 7), 1, None)
    resultat = beregn_kostnad(kandidat, vakt)
    assert (resultat.ordinære_timer, resultat.overtidstimer, resultat.total) == (7, 1, 2550)


@pytest.mark.parametrize('month,dag,timer', [(3, 28, 7), (10, 24, 9)])
def test_sommertid(month, dag, timer):
    kandidat = Kandidat(1, 'A', {}, timelønn=300)
    vakt = Vakt(1, 'natt', tid(dag, 23, month=month), tid(dag + 1, 7, month=month), 1, None)
    assert beregn_kostnad(kandidat, vakt).total == timer * 300


@pytest.mark.parametrize('month,dag,overtid,total', [(3, 28, 3, 2550), (10, 24, 5, 3450)])
def test_sommertid_over_grensen(month, dag, overtid, total):
    start = tid(dag - 5, month=month)
    kandidat = Kandidat(1, 'A', {}, (Tidsrom(start, start + timedelta(hours=32)),), timelønn=300)
    vakt = Vakt(1, 'natt', tid(dag, 23, month=month), tid(dag + 1, 7, month=month), 1, None)
    resultat = beregn_kostnad(kandidat, vakt)
    assert (resultat.ordinære_timer, resultat.overtidstimer, resultat.total) == (4, overtid, total)


def test_brøktime():
    kandidat = Kandidat(1, 'A', {}, timelønn=300)
    vakt = Vakt(1, 'dag', tid(6, 7), tid(6, 7, 30), 1, None)
    assert beregn_kostnad(kandidat, vakt).total == Decimal('150')


@pytest.mark.parametrize('lønn', [None, 0, -1, float('nan'), float('inf'), True, 'ugyldig', '300', 300.0, 1.5, 2**63, 10**400])
def test_ugyldig_lønn_stopper_vurdering(lønn):
    kandidat = Kandidat(1, 'A', {'dag': 1}, timelønn=lønn)
    vakt = Vakt(1, 'dag', tid(6, 7), tid(6, 15), 1, None)
    assert isinstance(vurder_kandidater(vakt, [kandidat], tid(30), tid(1, month=10)), Datafeil)


def test_største_sqlite_heltall_er_gyldig_lønn():
    kandidat = Kandidat(1, 'A', {'dag': 1}, timelønn=2**63 - 1)
    vakt = Vakt(1, 'dag', tid(6, 7), tid(6, 15), 1, None)
    assert not isinstance(vurder_kandidater(vakt, [kandidat], tid(30), tid(1, month=10)), Datafeil)
