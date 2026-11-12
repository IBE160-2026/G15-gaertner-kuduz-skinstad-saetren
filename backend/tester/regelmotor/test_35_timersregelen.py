"""35-timersregelen, ukentlig fri (story 2.4, FR5, AV-04), og vinduet for datafeil (A5).

Bare enhetsdata i domenet, uten database. Fasiten for #4127 og #4189 testes
gjennom API-et i `tester/api/test_kandidater.py`.

Alle tider i en sammenligning bruker samme `ZoneInfo`-objekt (`OSLO`). Da regner
Python på veggklokka hvis koden glemmer omregningen til UTC, og
sommertidstestene fanger det. De fanger også ukegrenser satt i UTC i stedet for
Oslo-tid.

Uke 39 (21.09–28.09.2026) og uke 40 (28.09–05.10) brukes som standard.
Hjelperen `hverdager` fyller ukedager med vakter slik at ingen annen fri i uka når 35 t,
og bare den fria testen ser på, avgjør.
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor import elleve_timer, kolliderende_vakt, kompetanse, trettifem_timer
from domene.regelmotor.trettifem_timer import ÅRSAK, berørte_uker, bryter_trettifem_timer, lengste_fri
from domene.regelmotor.vurdering import REGLER, samlet_vindu, vurder_kandidater
from domene.typer import Datafeil, Kandidat, Kandidatvurdering, Tidsrom, Vakt

OSLO = ZoneInfo("Europe/Oslo")
# Seeden: periodestart 21.09 − 672 t og periodeslutt 05.10 (beslutning 2A).
HISTORIKKSTART = datetime(2026, 8, 24, 0, 0, tzinfo=OSLO)
DATAGRENSE = datetime(2026, 10, 5, 0, 0, tzinfo=OSLO)
UKE_39 = date(2026, 9, 21)
UKE_40 = date(2026, 9, 28)
MINUTT = timedelta(minutes=1)


def kl(dag: date, time_: int, minutt: int = 0) -> datetime:
    return datetime.combine(dag, time(time_, minutt), tzinfo=OSLO)


def utc(tid: datetime) -> datetime:
    return tid.astimezone(UTC)


def rom(start: datetime, slutt: datetime) -> Tidsrom:
    return Tidsrom(start, slutt)


def vakt(start: datetime, slutt: datetime, vakttype: str = "dag") -> Vakt:
    return Vakt(vaktnummer=4127, vakttype=vakttype, start=start, slutt=slutt, minstenivå=1, satt_opp_ansatt_id=None)


def kandidat(*egne: object, id: int = 1) -> Kandidat:
    return Kandidat(id=id, navn=f"Ansatt {id:02d}", kompetanse={"dag": 4, "kveld": 4, "natt": 4}, vakter=egne)  # type: ignore[arg-type]


def hverdager(mandag: date, dager: range = range(5), fra: int = 7, til: int = 15) -> tuple[Tidsrom, ...]:
    """Vakter `fra`–`til` på ukedagene i `dager` (0 = mandag)."""
    return tuple(rom(kl(mandag + timedelta(days=d), fra), kl(mandag + timedelta(days=d), til)) for d in dager)


def vurder(v: Vakt, *kandidater: Kandidat, historikkstart: datetime = HISTORIKKSTART,
           datagrense: datetime = DATAGRENSE) -> Kandidatvurdering:
    resultat = vurder_kandidater(v, kandidater, datagrense, historikkstart)
    assert isinstance(resultat, Kandidatvurdering), resultat
    return resultat


def årsaker(v: Vakt, k: Kandidat, **kw: datetime) -> tuple[str, ...]:
    resultat = vurder(v, k, **kw)
    return resultat.utelukkede[0].årsaker if resultat.utelukkede else ()


def datafeil(v: Vakt, *kandidater: Kandidat, historikkstart: datetime = HISTORIKKSTART,
             datagrense: datetime = DATAGRENSE) -> Datafeil:
    resultat = vurder_kandidater(v, kandidater or (kandidat(),), datagrense, historikkstart)
    assert isinstance(resultat, Datafeil), resultat
    assert resultat.grunner
    assert resultat.datagrense == datagrense
    return resultat


# --- Grensen: 35:00 er gyldig, 34:59 utelukker -------------------------------------
# Mandag–fredag 07–15 og Vakten lørdag 26.09. Fria fra Vaktens slutt til mandag
# 28.09 00:00 er den lengste i uka. Hverdagsgapene er 16 t, mandag morgen 7 t.


def test_nøyaktig_35_timer_fri_til_ukeslutt_er_gyldig() -> None:
    v = vakt(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 13))
    k = kandidat(*hverdager(UKE_39))
    assert lengste_fri([*k.vakter, rom(v.start, v.slutt)], berørte_uker(v)[0]) == timedelta(hours=35)
    assert årsaker(v, k) == ()


def test_34_59_fri_til_ukeslutt_utelukker() -> None:
    v = vakt(kl(date(2026, 9, 26), 5, 1), kl(date(2026, 9, 26), 13, 1))
    k = kandidat(*hverdager(UKE_39))
    assert lengste_fri([*k.vakter, rom(v.start, v.slutt)], berørte_uker(v)[0]) == timedelta(hours=34, minutes=59)
    assert årsaker(v, k) == (ÅRSAK,)


@pytest.mark.parametrize("fri_min,brudd", [(2099, True), (2100, False), (2101, False)])
def test_fri_fra_ukestart_rundt_grensen(fri_min: int, brudd: bool) -> None:
    # Vakten først i uka, egne vakter onsdag–søndag 07–15 (gap tirsdag kveld ≥ 11 t).
    start = utc(kl(UKE_39, 0)) + timedelta(minutes=fri_min)
    v = vakt(start.astimezone(OSLO), (start + timedelta(hours=8)).astimezone(OSLO))
    k = kandidat(*hverdager(UKE_39, range(2, 7)))
    assert bryter_trettifem_timer(k, v) is brudd


@pytest.mark.parametrize("fri_min,brudd", [(2099, True), (2100, False)])
def test_fri_mellom_to_vakter_rundt_grensen(fri_min: int, brudd: bool) -> None:
    # Egne vakter mandag–tirsdag og fredag–søndag 07–15. Vakten onsdag 07–15, og
    # fria fra Vaktens slutt til neste egne vakt er den lengste i uka.
    v = vakt(kl(date(2026, 9, 23), 7), kl(date(2026, 9, 23), 15))
    neste_start = (utc(v.slutt) + timedelta(minutes=fri_min)).astimezone(OSLO)
    egne = (*hverdager(UKE_39, range(0, 2)), rom(neste_start, (utc(neste_start) + timedelta(hours=8)).astimezone(OSLO)),
            *hverdager(UKE_39, range(5, 7)))
    assert bryter_trettifem_timer(kandidat(*egne), v) is brudd


def test_ingen_egne_vakter_utelukkes_ikke() -> None:
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    assert årsaker(v, kandidat()) == ()
    assert lengste_fri([rom(v.start, v.slutt)], berørte_uker(v)[0]) == timedelta(hours=6 * 24 + 7)


def test_vakten_alene_kan_ikke_ta_bort_fria() -> None:
    # En uke med bare Vakten har alltid minst 80 t fri på én side.
    for dag in range(7):
        start = kl(UKE_39 + timedelta(days=dag), 7)
        assert not bryter_trettifem_timer(kandidat(), vakt(start, start + timedelta(hours=8)))


# --- Berørte uker og ukeskiftet ------------------------------------------------


def test_vakt_inne_i_uka_berører_én_uke() -> None:
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    assert berørte_uker(v) == [Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 0)))]


def test_vakt_som_slutter_mandag_00_berører_bare_én_uke() -> None:
    v = vakt(kl(date(2026, 9, 27), 16), kl(UKE_40, 0))
    assert berørte_uker(v) == [Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 0)))]
    assert trettifem_timer.vindu(v) == Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 0)))


def test_vakt_som_slutter_mandag_00_sjekker_ikke_neste_uke() -> None:
    # Uke 40 er fylt med kveldsvakter, så den ville gitt brudd om den ble sjekket.
    v = vakt(kl(date(2026, 9, 27), 16), kl(UKE_40, 0))
    k = kandidat(*hverdager(UKE_40, range(7), 15, 23))
    assert lengste_fri(list(k.vakter), Tidsrom(utc(kl(UKE_40, 0)), utc(kl(date(2026, 10, 5), 0)))) < timedelta(hours=35)
    assert årsaker(v, k) == ()


def test_vakt_som_starter_mandag_00_berører_bare_den_uka() -> None:
    v = vakt(kl(UKE_40, 0), kl(UKE_40, 8))
    assert berørte_uker(v) == [Tidsrom(utc(kl(UKE_40, 0)), utc(kl(date(2026, 10, 5), 0)))]


def test_nattevakt_over_ukeskiftet_berører_begge_ukene() -> None:
    v = vakt(kl(date(2026, 9, 27), 23), kl(UKE_40, 7), "natt")
    assert berørte_uker(v) == [
        Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 0))),
        Tidsrom(utc(kl(UKE_40, 0)), utc(kl(date(2026, 10, 5), 0))),
    ]


def test_krysser_ukeskiftet_med_brudd_bare_i_uka_før() -> None:
    # Uke 39: mandag–lørdag 07–15, så fria lørdag 15 – søndag 23 er 32 t. Uke 40 er tom.
    v = vakt(kl(date(2026, 9, 27), 23), kl(UKE_40, 7), "natt")
    assert årsaker(v, kandidat(*hverdager(UKE_39, range(6)))) == (ÅRSAK,)


def test_krysser_ukeskiftet_med_brudd_bare_i_uka_etter() -> None:
    # Uke 39 er tom. Uke 40: kveld tirsdag–søndag, så fria mandag 07 – tirsdag 15 er 32 t.
    v = vakt(kl(date(2026, 9, 27), 23), kl(UKE_40, 7), "natt")
    assert årsaker(v, kandidat(*hverdager(UKE_40, range(1, 7), 15, 23))) == (ÅRSAK,)


def test_fri_over_ukeskiftet_teller_bare_delen_innenfor_uka() -> None:
    # 40 t fri fra lørdag 26.09 kl. 15 til mandag 28.09 kl. 07, men bare 33 t i uke 39.
    v = vakt(kl(date(2026, 9, 26), 7), kl(date(2026, 9, 26), 15))
    k = kandidat(*hverdager(UKE_39), *hverdager(UKE_40, range(1)))
    assert utc(kl(UKE_40, 7)) - utc(v.slutt) == timedelta(hours=40)
    assert årsaker(v, k) == (ÅRSAK,)


# --- Overlapp og flere årsaker (beslutning A) --------------------------------------


def test_overlappende_vakt_telles_med_i_unionen() -> None:
    # Beslutning A (Ragnhild 2026-11-11, OP-14): som fasithjelperen. Egen vakt
    # lørdag 05–14 overlapper Vakten lørdag 05–13, og fria til mandag blir 34 t.
    v = vakt(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 13))
    k = kandidat(*hverdager(UKE_39), rom(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 14)))
    assert årsaker(v, k) == (kolliderende_vakt.ÅRSAK, ÅRSAK)


def test_vakt_som_ligger_inne_i_en_annen_forkorter_ikke_den_ytre() -> None:
    # Egen vakt lørdag 04–16 omslutter Vakten lørdag 05–13. Fria regnes fra 16:00
    # (32 t til mandag), ikke fra Vaktens slutt 13:00 (35 t).
    v = vakt(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 13))
    k = kandidat(*hverdager(UKE_39), rom(kl(date(2026, 9, 26), 4), kl(date(2026, 9, 26), 16)))
    assert lengste_fri([*k.vakter, rom(v.start, v.slutt)], berørte_uker(v)[0]) == timedelta(hours=32)
    assert årsaker(v, k) == (kolliderende_vakt.ÅRSAK, ÅRSAK)


def test_for_lavt_nivå_og_for_lite_fri_gir_begge_årsakene_i_fast_rekkefølge() -> None:
    v = Vakt(4127, "dag", kl(date(2026, 9, 26), 6), kl(date(2026, 9, 26), 14), 3, None)
    k = Kandidat(id=1, navn="Ansatt 01", kompetanse={"dag": 1}, vakter=hverdager(UKE_39))
    assert vurder(v, k).utelukkede[0].årsaker == (kompetanse.ÅRSAK, ÅRSAK)


def test_regelen_ligger_som_nummer_fire_i_regellisten() -> None:
    assert ÅRSAK == "35-timersregelen"
    assert [r.årsak for r in REGLER] == [
        "kompetanse-minstekrav", "kolliderende vakt", "11-timersregelen", "35-timersregelen",
    ]
    assert REGLER[3].bryter is trettifem_timer.bryter_trettifem_timer
    assert REGLER[3].vindu is trettifem_timer.vindu
    assert REGLER[3].vaktkrav(vakt(kl(UKE_39, 7), kl(UKE_39, 15))) == []


# --- Sommertid: ukegrenser i Oslo-tid, fri i faktisk tid ---------------------------
# Seedens dekning går 24.08–05.10, så testene sender egne grenser.
VÅR = {"historikkstart": datetime(2026, 3, 1, tzinfo=OSLO), "datagrense": datetime(2026, 4, 30, tzinfo=OSLO)}
HØST = {"historikkstart": datetime(2026, 10, 1, tzinfo=OSLO), "datagrense": datetime(2026, 11, 30, tzinfo=OSLO)}


def test_uka_med_vårskiftet_har_167_timer() -> None:
    (uke,) = berørte_uker(vakt(kl(date(2026, 3, 25), 7), kl(date(2026, 3, 25), 15)))
    assert uke == Tidsrom(utc(kl(date(2026, 3, 23), 0)), utc(kl(date(2026, 3, 30), 0)))
    assert uke.slutt - uke.start == timedelta(hours=167)


def test_uka_med_høstskiftet_har_169_timer() -> None:
    (uke,) = berørte_uker(vakt(kl(date(2026, 10, 21), 7), kl(date(2026, 10, 21), 15)))
    assert uke == Tidsrom(utc(kl(date(2026, 10, 19), 0)), utc(kl(date(2026, 10, 26), 0)))
    assert uke.slutt - uke.start == timedelta(hours=169)


def test_vårskiftet_35_timer_på_veggklokka_er_34_faktiske_og_utelukker() -> None:
    # Uke 23.–30.03.2026. Natt til 29.03 går klokka fra 02:00 til 03:00.
    # Mandag–fredag 07–15 og Vakten lørdag 28.03 05–13. Fria til mandag 00:00.
    v = vakt(kl(date(2026, 3, 28), 5), kl(date(2026, 3, 28), 13))
    ukeslutt = kl(date(2026, 3, 30), 0)
    assert ukeslutt.replace(tzinfo=None) - v.slutt.replace(tzinfo=None) == timedelta(hours=35)
    assert utc(ukeslutt) - utc(v.slutt) == timedelta(hours=34)
    assert årsaker(v, kandidat(*hverdager(date(2026, 3, 23))), **VÅR) == (ÅRSAK,)


def test_høstskiftet_34_timer_på_veggklokka_er_35_faktiske_og_er_gyldig() -> None:
    # Uke 19.–26.10.2026. Natt til 25.10 går klokka fra 03:00 til 02:00.
    # Mandag–fredag 07–15 og Vakten lørdag 24.10 06–14. Fria til mandag 00:00.
    v = vakt(kl(date(2026, 10, 24), 6), kl(date(2026, 10, 24), 14))
    ukeslutt = kl(date(2026, 10, 26), 0)
    assert ukeslutt.replace(tzinfo=None) - v.slutt.replace(tzinfo=None) == timedelta(hours=34)
    assert utc(ukeslutt) - utc(v.slutt) == timedelta(hours=35)
    assert årsaker(v, kandidat(*hverdager(date(2026, 10, 19))), **HØST) == ()


def test_høstskiftet_ett_minutt_mindre_utelukker() -> None:
    v = vakt(kl(date(2026, 10, 24), 6, 1), kl(date(2026, 10, 24), 14, 1))
    assert årsaker(v, kandidat(*hverdager(date(2026, 10, 19))), **HØST) == (ÅRSAK,)


def test_uka_etter_vårskiftet_starter_mandag_00_sommertid() -> None:
    # Mandag 30.03 00:00 CEST er 29.03 22:00 UTC. Ukegrenser i UTC ville gitt 30.03
    # 00:00 UTC, og 168 faktiske timer fra 23.03 00:00 CET ville gitt 29.03 23:00 UTC.
    (uke,) = berørte_uker(vakt(kl(date(2026, 3, 31), 7), kl(date(2026, 3, 31), 15)))
    assert uke.start == datetime(2026, 3, 29, 22, 0, tzinfo=UTC)


# --- Determinisme ---------------------------------------------------------------


def test_samme_input_gir_samme_output() -> None:
    # Vakten lørdag 05–13 gir nøyaktig 35 t fri til mandag. Id 13–24 har i tillegg
    # en egen vakt lørdag rundt kl. 14–15, så fria blir under 35 t.
    v = vakt(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 13))
    kandidater = [kandidat(*hverdager(UKE_39), id=i) for i in range(1, 13)]
    kandidater += [
        kandidat(*hverdager(UKE_39), rom(kl(date(2026, 9, 26), 14) + timedelta(minutes=i),
                                         kl(date(2026, 9, 26), 15) + timedelta(minutes=i)), id=i)
        for i in range(13, 25)
    ]
    første = vurder(v, *kandidater)
    assert [k.id for k in første.gyldige] == list(range(1, 13))
    assert [u.kandidat.id for u in første.utelukkede] == list(range(13, 25))
    for _ in range(3):
        assert vurder(v, *kandidater) == første
        assert vurder(v, *reversed(kandidater)) == første


def test_samme_input_gir_samme_output_med_gyldige_og_utelukkede() -> None:
    v = vakt(kl(date(2026, 9, 26), 5), kl(date(2026, 9, 26), 13))
    kandidater = [kandidat(*hverdager(UKE_39), id=1), kandidat(id=2),
                  kandidat(*hverdager(UKE_39), rom(kl(date(2026, 9, 26), 14), kl(date(2026, 9, 26), 15)), id=3)]
    første = vurder(v, *kandidater)
    assert [k.id for k in første.gyldige] == [1, 2]
    assert [u.kandidat.id for u in første.utelukkede] == [3]
    for _ in range(3):
        assert vurder(v, *reversed(kandidater)) == første


# --- Vinduet og datadekningen (P-08, vedtak A5) ---------------------------------


def test_vinduet_er_de_berørte_ukene() -> None:
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    assert trettifem_timer.vindu(v) == Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 0)))
    natt = vakt(kl(date(2026, 9, 27), 23), kl(UKE_40, 7), "natt")
    assert trettifem_timer.vindu(natt) == Tidsrom(utc(kl(UKE_39, 0)), utc(kl(date(2026, 10, 5), 0)))


def test_eksempelet_for_4127_og_4189() -> None:
    # #4127 søndag 27.09 07–15: [21.09 00:00, 28.09 02:00) med 11-timersvinduet.
    v4127 = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    assert samlet_vindu(v4127, REGLER) == Tidsrom(utc(kl(UKE_39, 0)), utc(kl(UKE_40, 2)))
    # #4189 mandag 28.09 23–07: uka slutter nøyaktig på datagrensen.
    v4189 = vakt(kl(UKE_40, 23), kl(date(2026, 9, 29), 7), "natt")
    assert samlet_vindu(v4189, REGLER) == Tidsrom(utc(kl(UKE_40, 0)), utc(DATAGRENSE))
    assert vurder(v4189, kandidat()).gyldige


def test_uke_som_slutter_på_datagrensen_vurderes() -> None:
    v = vakt(kl(date(2026, 9, 30), 7), kl(date(2026, 9, 30), 15))
    assert vurder(v, kandidat()).gyldige


def test_uke_som_slutter_etter_datagrensen_er_datafeil() -> None:
    # Datagrense lørdag 03.10: 11-timersvinduet slutter 01.10 02:00, men uka går til 05.10.
    v = vakt(kl(date(2026, 9, 30), 7), kl(date(2026, 9, 30), 15))
    grense = kl(date(2026, 10, 3), 0)
    assert elleve_timer.vindu(v).slutt < utc(grense)
    resultat = datafeil(v, datagrense=grense)
    assert "datagrensen" in resultat.grunner[0]


def test_uke_ett_minutt_etter_datagrensen_er_datafeil() -> None:
    v = vakt(kl(date(2026, 9, 30), 7), kl(date(2026, 9, 30), 15))
    datafeil(v, datagrense=DATAGRENSE - MINUTT)


def test_uke_som_starter_ved_historikkstart_vurderes() -> None:
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    assert vurder(v, kandidat(), historikkstart=kl(UKE_39, 0)).gyldige


def test_uke_som_starter_ett_minutt_før_historikkstart_er_datafeil() -> None:
    # 11-timersvinduet starter 26.09 20:00, langt etter. Det er uka som krever historikken.
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    resultat = datafeil(v, historikkstart=kl(UKE_39, 0) + MINUTT)
    assert "historikkstarten" in resultat.grunner[0]


def test_ugyldig_vakt_i_uka_utenfor_11_timer_er_datafeil() -> None:
    # Vakten søndag 27.09, ugyldig egen vakt tirsdag 22.09: utenfor ±11 t, men i uka.
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    ugyldig = rom(kl(date(2026, 9, 22), 15), kl(date(2026, 9, 22), 7))
    assert utc(ugyldig.start) < elleve_timer.vindu(v).start
    resultat = datafeil(v, kandidat(ugyldig, id=3))
    assert "ansatt 3" in resultat.grunner[0]


def test_ugyldig_vakt_i_uka_før_vurderes_normalt() -> None:
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    ugyldig = rom(kl(date(2026, 9, 18), 15), kl(date(2026, 9, 18), 7))
    assert [k.id for k in vurder(v, kandidat(ugyldig, id=3)).gyldige] == [3]


def test_ugyldig_vakt_som_slutter_ved_ukestart_er_innenfor() -> None:
    # Det lukkede tidsrommet [søndag 20.09 20:00, mandag 21.09 00:00] når uka.
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    datafeil(v, kandidat(rom(kl(UKE_39, 0), kl(date(2026, 9, 20), 20))))


def test_ugyldig_vakt_hoppes_over_når_regelen_kalles_direkte() -> None:
    # Forutsetningen i docstringen: datafeilsjekken har allerede kjørt.
    v = vakt(kl(date(2026, 9, 27), 7), kl(date(2026, 9, 27), 15))
    ugyldig = rom(kl(date(2026, 9, 22), 15), kl(date(2026, 9, 22), 7))
    assert not bryter_trettifem_timer(kandidat(ugyldig), v)
