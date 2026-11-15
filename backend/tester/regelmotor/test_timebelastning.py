"""Timebelastning og terskelen for høy belastning (story 4.2, FR8, P-04/K-02)."""

from datetime import timedelta

import pytest

from domene.regelmotor.timebelastning import HØY_BELASTNING_GRENSE, NORMALUKE, timebelastning


def hm(timer: int, minutter: int = 0, sekunder: int = 0) -> timedelta:
    return timedelta(hours=timer, minutes=minutter, seconds=sekunder)


def test_grensen_er_eksakt_1944_minutter() -> None:
    assert HØY_BELASTNING_GRENSE == timedelta(minutes=1944)
    assert NORMALUKE == timedelta(hours=36)


@pytest.mark.parametrize(
    "tid,prosent,høy",
    [
        (hm(0), 0.0, False),
        (hm(32), 100 * 32 / 36, False),  # Ingrid i #4127: 88,9 %
        (hm(32, 23), 100 * 1943 / 2160, False),
        (hm(32, 23, 59), None, False),
        (hm(32, 24), 90.0, True),
        (hm(32, 25), None, True),
        (hm(36), 100.0, True),
        (hm(40), 100 * 40 / 36, True),
    ],
)
def test_matrisen(tid: timedelta, prosent: float | None, høy: bool) -> None:
    svar = timebelastning(tid)
    assert svar.høy is høy
    if prosent is not None:
        assert svar.prosent == pytest.approx(prosent)


def test_ingrid_er_88_9_prosent() -> None:
    assert round(timebelastning(hm(32)).prosent, 1) == 88.9


def test_32_24_er_nøyaktig_90_prosent() -> None:
    assert timebelastning(hm(32, 24)).prosent == pytest.approx(90.0)


def test_40_timer_kuttes_ikke_i_backend() -> None:
    assert round(timebelastning(hm(40)).prosent, 1) == 111.1


def test_ett_sekund_under_og_på_grensen() -> None:
    assert not timebelastning(HØY_BELASTNING_GRENSE - timedelta(seconds=1)).høy
    assert timebelastning(HØY_BELASTNING_GRENSE).høy


def test_gjentatt_kjøring_gir_identisk_resultat() -> None:
    for tid in (hm(0), hm(32, 23, 59), hm(32, 24), hm(40)):
        assert timebelastning(tid) == timebelastning(tid)
