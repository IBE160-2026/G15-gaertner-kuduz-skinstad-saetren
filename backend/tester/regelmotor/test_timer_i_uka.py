"""Timer i uka Vakten starter i (story 4.1, FR8, P-02).

Uke 39 er 21.09–28.09.2026 og uke 40 er 28.09–05.10. Grensetester for ukeskifte,
sommertid (mars og oktober) og halvåpne intervaller. Ingrids 32 t for #4127 testes
gjennom API-et i `tester/api/test_kandidater.py`.
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from domene.regelmotor.timer_i_uka import minutter_i_uka, timer_i_startuka
from domene.typer import Kandidat, Tidsrom, Vakt

OSLO = ZoneInfo("Europe/Oslo")
UKE_39 = date(2026, 9, 21)
UKE_40 = date(2026, 9, 28)


def kl(dag: date, time_: int, minutt: int = 0) -> datetime:
    return datetime.combine(dag, time(time_, minutt), tzinfo=OSLO)


def vakt(start: datetime, slutt: datetime | None = None) -> Vakt:
    return Vakt(4127, "dag", start, slutt or start + timedelta(hours=8), 1, None)


def kandidat(*egne: Tidsrom) -> Kandidat:
    return Kandidat(id=1, navn="Test", kompetanse={"dag": 4}, vakter=egne, timelønn=300)


def timer(k: Kandidat, v: Vakt) -> timedelta:
    return timer_i_startuka(k, v)


def test_uten_vakter_er_null() -> None:
    assert timer(kandidat(), vakt(kl(UKE_39 + timedelta(days=6), 7))) == timedelta(0)


def test_summerer_vakter_i_uka() -> None:
    egne = [Tidsrom(kl(UKE_39 + timedelta(days=d), 7), kl(UKE_39 + timedelta(days=d), 15)) for d in range(4)]
    assert timer(kandidat(*egne), vakt(kl(UKE_39 + timedelta(days=6), 7))) == timedelta(hours=32)


def test_natt_over_ukeskifte_startuka_er_uka_etter() -> None:
    natt = Tidsrom(kl(UKE_39 + timedelta(days=6), 23), kl(UKE_40, 7))
    assert timer(kandidat(natt), vakt(kl(UKE_40 + timedelta(days=2), 7))) == timedelta(hours=7)


def test_natt_over_ukeskifte_startuka_er_uka_før() -> None:
    natt = Tidsrom(kl(UKE_39 + timedelta(days=6), 23), kl(UKE_40, 7))
    assert timer(kandidat(natt), vakt(kl(UKE_39 + timedelta(days=2), 7))) == timedelta(hours=1)


def test_slutter_nøyaktig_mandag_null_gir_null_i_neste_uke() -> None:
    før = Tidsrom(kl(UKE_39 + timedelta(days=6), 16), kl(UKE_40, 0))
    assert timer(kandidat(før), vakt(kl(UKE_40 + timedelta(days=1), 7))) == timedelta(0)
    assert timer(kandidat(før), vakt(kl(UKE_39 + timedelta(days=1), 7))) == timedelta(hours=8)


def test_vakt_i_neste_uke_telles_ikke() -> None:
    etter = Tidsrom(kl(UKE_40, 0), kl(UKE_40, 8))
    assert timer(kandidat(etter), vakt(kl(UKE_39 + timedelta(days=1), 7))) == timedelta(0)


def test_sommertid_mars_natt_er_7_timer() -> None:
    lørdag = date(2026, 3, 28)
    natt = Tidsrom(kl(lørdag, 23), kl(lørdag + timedelta(days=1), 7))
    assert timer(kandidat(natt), vakt(kl(date(2026, 3, 24), 7))) == timedelta(hours=7)


def test_vintertid_oktober_natt_er_9_timer() -> None:
    lørdag = date(2026, 10, 24)
    natt = Tidsrom(kl(lørdag, 23), kl(lørdag + timedelta(days=1), 7))
    assert timer(kandidat(natt), vakt(kl(date(2026, 10, 20), 7))) == timedelta(hours=9)


def test_ukegrensen_ved_sommertid_er_oslo_mandag() -> None:
    # Søndag 29.03.2026 23:00 til mandag 07:00 (sommertid): 1 t før og 7 t etter mandag 00:00.
    natt = Tidsrom(kl(date(2026, 3, 29), 23), kl(date(2026, 3, 30), 7))
    assert timer(kandidat(natt), vakt(kl(date(2026, 3, 25), 7))) == timedelta(hours=1)
    assert timer(kandidat(natt), vakt(kl(date(2026, 3, 31), 7))) == timedelta(hours=7)


def test_overlappende_vakter_telles_som_union() -> None:
    a = Tidsrom(kl(UKE_39, 7), kl(UKE_39, 15))
    b = Tidsrom(kl(UKE_39, 11), kl(UKE_39, 19))
    assert timer(kandidat(a, b), vakt(kl(UKE_39 + timedelta(days=3), 7))) == timedelta(hours=12)


def test_gjentatt_kjøring_gir_samme_resultat() -> None:
    k, v = kandidat(Tidsrom(kl(UKE_39, 7), kl(UKE_39, 15))), vakt(kl(UKE_39 + timedelta(days=6), 7))
    assert timer(k, v) == timer(k, v) == timedelta(hours=8)


def test_vakten_som_starter_søndag_natt_regner_uka_den_starter_i() -> None:
    # Søndag 27.09 23:00 hører til uke 39, selv om den slutter i uke 40.
    søndag = UKE_39 + timedelta(days=6)
    natt = vakt(kl(søndag, 23), kl(søndag + timedelta(days=1), 7))
    egne = [Tidsrom(kl(UKE_39, 7), kl(UKE_39, 15)), Tidsrom(kl(UKE_40, 7), kl(UKE_40, 15))]
    assert timer(kandidat(*egne), natt) == timedelta(hours=8)


def test_vakten_som_starter_mandag_midnatt_regner_den_nye_uka() -> None:
    egne = [Tidsrom(kl(UKE_39, 7), kl(UKE_39, 15)), Tidsrom(kl(UKE_40, 7), kl(UKE_40, 15))]
    assert timer(kandidat(*egne), vakt(kl(UKE_40, 0))) == timedelta(hours=8)


def test_minutter_avrundes_ned_til_hele_minutter() -> None:
    v = vakt(kl(UKE_39, 7))
    egne = [Tidsrom(kl(UKE_40 - timedelta(days=3), 7), kl(UKE_40 - timedelta(days=3), 15) + timedelta(seconds=59))]
    assert minutter_i_uka(kandidat(*egne), v) == 480
    assert minutter_i_uka(kandidat(), v) == 0
