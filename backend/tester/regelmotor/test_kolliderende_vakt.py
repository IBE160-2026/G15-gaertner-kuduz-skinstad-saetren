"""Kolliderende vakt (story 2.2): halvåpne intervall på faktisk tid.

Bare enhetsdata i domenet, uten database. Fasiten for #4127 og #4189 testes
gjennom API-et i `tester/api/test_kandidater.py`.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor import kolliderende_vakt, kompetanse
from domene.regelmotor.kolliderende_vakt import ÅRSAK, bryter_kollisjon
from domene.regelmotor.vurdering import REGLER, vurder_kandidater
from domene.typer import Datafeil, Kandidat, Kandidatvurdering, Tidsrom, Vakt

OSLO = ZoneInfo("Europe/Oslo")
DATAGRENSE = datetime(2026, 11, 8, 0, 0, tzinfo=OSLO)
DAG_START = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)
DAG_SLUTT = DAG_START + timedelta(hours=8)


def vakt(vakttype: str = "dag", *, start: datetime = DAG_START, slutt: datetime | None = None,
         minstenivå: int = 1) -> Vakt:
    return Vakt(
        vaktnummer=4127, vakttype=vakttype, start=start,
        slutt=start + timedelta(hours=8) if slutt is None else slutt,
        minstenivå=minstenivå, satt_opp_ansatt_id=None,
    )


def kandidat(*egne: Tidsrom, id: int = 1, kompetanse: dict | None = None) -> Kandidat:
    return Kandidat(id=id, navn=f"Ansatt {id:02d}", kompetanse=kompetanse or {"dag": 4, "natt": 4}, vakter=egne)


def vurder(v: Vakt, *kandidater: Kandidat) -> Kandidatvurdering:
    resultat = vurder_kandidater(v, kandidater, DATAGRENSE)
    assert isinstance(resultat, Kandidatvurdering), resultat
    return resultat


def utelukket(v: Vakt, k: Kandidat) -> bool:
    resultat = vurder(v, k)
    if resultat.utelukkede:
        assert resultat.utelukkede[0].årsaker == (ÅRSAK,)
        return True
    return False


def rom(start: datetime, slutt: datetime) -> Tidsrom:
    return Tidsrom(start, slutt)


# --- Grensene: halvåpne intervall ---------------------------------------------


def test_ett_minutts_overlapp_i_slutten_av_egen_vakt_utelukker() -> None:
    egen = rom(DAG_START - timedelta(hours=8), DAG_START + timedelta(minutes=1))
    assert utelukket(vakt(), kandidat(egen))


def test_ett_minutts_overlapp_i_starten_av_egen_vakt_utelukker() -> None:
    egen = rom(DAG_SLUTT - timedelta(minutes=1), DAG_SLUTT + timedelta(hours=8))
    assert utelukket(vakt(), kandidat(egen))


def test_egen_vakt_som_slutter_nøyaktig_ved_vaktens_start_kolliderer_ikke() -> None:
    egen = rom(DAG_START - timedelta(hours=8), DAG_START)
    assert not utelukket(vakt(), kandidat(egen))


def test_egen_vakt_som_starter_nøyaktig_ved_vaktens_slutt_kolliderer_ikke() -> None:
    egen = rom(DAG_SLUTT, DAG_SLUTT + timedelta(hours=8))
    assert not utelukket(vakt(), kandidat(egen))


def test_ett_minutt_fra_hver_side_kolliderer_ikke() -> None:
    før = rom(DAG_START - timedelta(hours=8), DAG_START - timedelta(minutes=1))
    etter = rom(DAG_SLUTT + timedelta(minutes=1), DAG_SLUTT + timedelta(hours=8))
    assert not utelukket(vakt(), kandidat(før, etter))


def test_egen_vakt_som_omslutter_vakten_utelukker() -> None:
    egen = rom(DAG_START - timedelta(hours=1), DAG_SLUTT + timedelta(hours=1))
    assert utelukket(vakt(), kandidat(egen))


def test_egen_vakt_som_ligger_helt_inne_i_vakten_utelukker() -> None:
    egen = rom(DAG_START + timedelta(hours=2), DAG_START + timedelta(hours=3))
    assert utelukket(vakt(), kandidat(egen))


def test_identisk_tidsrom_utelukker() -> None:
    assert utelukket(vakt(), kandidat(rom(DAG_START, DAG_SLUTT)))


@pytest.mark.parametrize("forskyvning_min,kolliderer", [
    (-481, False), (-480, False), (-479, True), (479, True), (480, False), (481, False),
])
def test_forskyvning_rundt_grensene(forskyvning_min: int, kolliderer: bool) -> None:
    start = DAG_START + timedelta(minutes=forskyvning_min)
    assert bryter_kollisjon(kandidat(rom(start, start + timedelta(hours=8))), vakt()) is kolliderer


# --- Natt over midnatt og sommertid -------------------------------------------


def test_natt_over_midnatt_utelukker_vakt_som_starter_før_nattens_slutt() -> None:
    natt = vakt("natt", start=datetime(2026, 9, 28, 23, 0, tzinfo=OSLO))
    tidlig = rom(datetime(2026, 9, 29, 6, 0, tzinfo=OSLO), datetime(2026, 9, 29, 14, 0, tzinfo=OSLO))
    assert utelukket(natt, kandidat(tidlig))


def test_natt_over_midnatt_og_vakt_som_starter_ved_slutten_kolliderer_ikke() -> None:
    natt = vakt("natt", start=datetime(2026, 9, 28, 23, 0, tzinfo=OSLO))
    sen = rom(datetime(2026, 9, 29, 7, 0, tzinfo=OSLO), datetime(2026, 9, 29, 15, 0, tzinfo=OSLO))
    assert not utelukket(natt, kandidat(sen))


def test_samme_kalenderdato_uten_overlapp_kolliderer_ikke() -> None:
    # Dag 07–15 og kveld 15–23 samme dato.
    kveld = rom(datetime(2026, 9, 27, 15, 0, tzinfo=OSLO), datetime(2026, 9, 27, 23, 0, tzinfo=OSLO))
    assert not utelukket(vakt(), kandidat(kveld))


# Natt 24.–25.10.2026: sommertiden slutter natt til søndag 25.10, og klokka 02:00–03:00
# går to ganger. Vakten 23:00–07:00 veggklokke varer derfor 9 faktiske timer
# (21:00 UTC til 06:00 UTC).
SOMMERTID_NATT = vakt("natt", start=datetime(2026, 10, 24, 23, 0, tzinfo=OSLO))


def test_sommertidsnatten_er_ni_timer_faktisk() -> None:
    forløpt = SOMMERTID_NATT.slutt.astimezone(timezone.utc) - SOMMERTID_NATT.start.astimezone(timezone.utc)
    assert forløpt == timedelta(hours=9)


def test_egen_vakt_i_timen_som_går_to_ganger_kolliderer() -> None:
    andre_gang = datetime(2026, 10, 25, 2, 30, tzinfo=OSLO, fold=1)
    # Tillegget går via UTC: `+ timedelta` på en tid med tzinfo regner på veggklokka.
    egen = rom(andre_gang, andre_gang.astimezone(timezone.utc) + timedelta(minutes=10))
    assert utelukket(SOMMERTID_NATT, kandidat(egen))


def test_vakt_som_starter_ved_sommertidsnattens_slutt_kolliderer_ikke() -> None:
    # Vakten slutter 25.10 07:00 CET = 06:00 UTC. 06:59 CET er 05:59 UTC og kolliderer
    # (naiv veggklokke i Oslo gir her samme svar), mens 07:00 CET berører.
    slutt = SOMMERTID_NATT.slutt
    berører = rom(slutt, slutt + timedelta(hours=8))
    ett_minutt_inn = rom(slutt - timedelta(minutes=1), slutt + timedelta(hours=8))
    assert not utelukket(SOMMERTID_NATT, kandidat(berører))
    assert utelukket(SOMMERTID_NATT, kandidat(ett_minutt_inn))


def test_egen_vakt_med_start_etter_slutt_på_veggklokka_er_gyldig_og_kolliderer() -> None:
    # 02:50 første gang (00:50 UTC) til 02:10 andre gang (01:10 UTC) ser omvendt ut på
    # veggklokka, men er gyldig på faktisk tid, så det er ikke datafeil, og den ligger
    # i Vaktens tidsrom. Testen sier ikke noe om selve UTC-omregningen i overlappsjekken.
    start = datetime(2026, 10, 25, 2, 50, tzinfo=OSLO, fold=0)
    slutt = datetime(2026, 10, 25, 2, 10, tzinfo=OSLO, fold=1)
    assert start.astimezone(timezone.utc) < slutt.astimezone(timezone.utc)
    assert utelukket(SOMMERTID_NATT, kandidat(rom(start, slutt)))


def i_oslo(*, utc: datetime) -> datetime:
    return utc.astimezone(OSLO)


def test_overlapp_på_veggklokka_men_ikke_på_faktisk_tid_utelukker_ikke() -> None:
    # Vakten slutter 02:30 første gang (00:30 UTC). Egen vakt starter 02:15 andre gang
    # (01:15 UTC), altså 45 minutter etter. På veggklokka ser 02:15 ut til å komme før
    # 02:30, så uten omregning til UTC ville dette blitt en kollisjon.
    vakt_slutt = datetime(2026, 10, 25, 2, 30, tzinfo=OSLO, fold=0)
    egen_start = datetime(2026, 10, 25, 2, 15, tzinfo=OSLO, fold=1)
    assert vakt_slutt.astimezone(timezone.utc) == datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc)
    assert egen_start.astimezone(timezone.utc) == datetime(2026, 10, 25, 1, 15, tzinfo=timezone.utc)
    vakt_start = i_oslo(utc=vakt_slutt.astimezone(timezone.utc) - timedelta(hours=6))
    egen_slutt = i_oslo(utc=egen_start.astimezone(timezone.utc) + timedelta(hours=8))
    assert not utelukket(vakt("natt", start=vakt_start, slutt=vakt_slutt), kandidat(rom(egen_start, egen_slutt)))


def test_speilvendt_overlapp_på_veggklokka_men_ikke_på_faktisk_tid_utelukker_ikke() -> None:
    # Rollene byttet: egen vakt slutter 02:30 første gang (00:30 UTC), og Vakten starter
    # 02:15 andre gang (01:15 UTC).
    egen_slutt = datetime(2026, 10, 25, 2, 30, tzinfo=OSLO, fold=0)
    vakt_start = datetime(2026, 10, 25, 2, 15, tzinfo=OSLO, fold=1)
    egen_start = i_oslo(utc=egen_slutt.astimezone(timezone.utc) - timedelta(hours=6))
    vakt_slutt = i_oslo(utc=vakt_start.astimezone(timezone.utc) + timedelta(hours=8))
    assert not utelukket(vakt("natt", start=vakt_start, slutt=vakt_slutt), kandidat(rom(egen_start, egen_slutt)))


def test_egen_vakt_før_timen_som_går_to_ganger_regnes_på_faktisk_tid() -> None:
    # Egen vakt 18:00–23:00 CEST (16:00–21:00 UTC) slutter akkurat ved Vaktens start.
    egen = rom(datetime(2026, 10, 24, 18, 0, tzinfo=OSLO), SOMMERTID_NATT.start)
    assert not utelukket(SOMMERTID_NATT, kandidat(egen))


def test_tider_i_ulike_tidssoner_sammenlignes_som_samme_tidspunkt() -> None:
    egen_utc = rom(
        (DAG_START - timedelta(hours=8)).astimezone(timezone.utc),
        (DAG_START + timedelta(minutes=1)).astimezone(timezone.utc),
    )
    assert utelukket(vakt(), kandidat(egen_utc))
    berører = rom((DAG_START - timedelta(hours=8)).astimezone(timezone.utc), DAG_START.astimezone(timezone.utc))
    assert not utelukket(vakt(), kandidat(berører))


# --- Flere vakter og ingen vakter ----------------------------------------------


def test_bare_én_av_flere_egne_vakter_overlapper() -> None:
    langt_før = rom(DAG_START - timedelta(days=3), DAG_START - timedelta(days=3) + timedelta(hours=8))
    overlapp = rom(DAG_START + timedelta(hours=7), DAG_START + timedelta(hours=15))
    langt_etter = rom(DAG_START + timedelta(days=9), DAG_START + timedelta(days=9, hours=8))
    assert utelukket(vakt(), kandidat(langt_før, overlapp, langt_etter))
    assert not utelukket(vakt(), kandidat(langt_før, langt_etter))


def test_ingen_egne_vakter_utelukkes_ikke() -> None:
    assert not utelukket(vakt(), kandidat())
    assert kandidat().vakter == ()


def test_kandidat_uten_vakter_virker_uendret_fra_2_1() -> None:
    k = Kandidat(id=1, navn="Ola", kompetanse={"dag": 3})
    assert k.vakter == ()
    assert vurder(vakt(minstenivå=3), k).gyldige == (k,)


def test_overlappende_vakter_for_ulike_ansatte_er_ikke_regelbrudd() -> None:
    # AV-02: bare Kandidatens egne vakter teller. Den ene har en vakt i samme tidsrom
    # og utelukkes, mens den andre uten egne vakter er gyldig.
    a = kandidat(rom(DAG_START, DAG_SLUTT), id=1)
    b = kandidat(id=2)
    resultat = vurder(vakt(), a, b)
    assert [k.id for k in resultat.gyldige] == [2]
    assert [u.kandidat.id for u in resultat.utelukkede] == [1]


# --- Flere brudd og rekkefølge -------------------------------------------------


def test_kollisjon_og_for_lavt_nivå_gir_begge_årsaker_i_fast_rekkefølge() -> None:
    k = kandidat(rom(DAG_START, DAG_SLUTT), kompetanse={"dag": 1})
    resultat = vurder(vakt(minstenivå=3), k)
    assert resultat.utelukkede[0].årsaker == (kompetanse.ÅRSAK, "kolliderende vakt")
    assert ÅRSAK == "kolliderende vakt"


def test_regelen_ligger_som_nummer_to_i_regellisten() -> None:
    assert [r.årsak for r in REGLER] == ["kompetanse-minstekrav", "kolliderende vakt"]
    assert REGLER[1].bryter is kolliderende_vakt.bryter_kollisjon


def test_bare_kollisjon_gir_bare_den_årsaken() -> None:
    k = kandidat(rom(DAG_START, DAG_SLUTT), kompetanse={"dag": 4})
    assert vurder(vakt(minstenivå=3), k).utelukkede[0].årsaker == (ÅRSAK,)


# --- Determinisme --------------------------------------------------------------


def test_samme_input_gir_samme_output() -> None:
    kandidater = [
        kandidat(rom(DAG_START + timedelta(hours=i - 4), DAG_START + timedelta(hours=i + 4)), id=i)
        for i in range(1, 13)
    ]
    v = vakt()
    første = vurder_kandidater(v, kandidater, DATAGRENSE)
    assert isinstance(første, Kandidatvurdering)
    assert første.gyldige and første.utelukkede
    for _ in range(3):
        for resultat in (
            vurder_kandidater(v, kandidater, DATAGRENSE),
            vurder_kandidater(v, list(reversed(kandidater)), DATAGRENSE),
        ):
            assert resultat == første
            assert isinstance(resultat, Kandidatvurdering)
            # `vakter` er ikke med i likhetssjekken, så de sammenlignes eksplisitt.
            assert vakter_i(resultat) == vakter_i(første)


def vakter_i(resultat: Kandidatvurdering) -> tuple[list, list]:
    return (
        [(k.id, k.vakter) for k in resultat.gyldige],
        [(u.kandidat.id, u.kandidat.vakter) for u in resultat.utelukkede],
    )


def test_vurderingen_endrer_ikke_kandidatens_vakter() -> None:
    egen = rom(DAG_START, DAG_SLUTT)
    ledig = rom(DAG_START + timedelta(days=2), DAG_SLUTT + timedelta(days=2))
    kandidater = (kandidat(egen, id=1), kandidat(ledig, id=2))
    før = [(k.id, k.vakter) for k in kandidater]

    resultat = vurder(vakt(), *kandidater)

    assert [(k.id, k.vakter) for k in kandidater] == før == [(1, (egen,)), (2, (ledig,))]
    assert vakter_i(resultat) == ([(2, (ledig,))], [(1, (egen,))])


# --- Datafeil (P-08) ------------------------------------------------------------


def datafeil(*kandidater: Kandidat) -> Datafeil:
    resultat = vurder_kandidater(vakt(), kandidater, DATAGRENSE)
    assert isinstance(resultat, Datafeil), resultat
    assert resultat.grunner
    return resultat


@pytest.mark.parametrize("felt", ["start", "slutt"])
def test_egen_vakt_uten_tidssone_er_datafeil_ikke_utelukkelse(felt: str) -> None:
    gyldig = rom(DAG_START - timedelta(hours=8), DAG_START - timedelta(hours=1))
    naiv = Tidsrom(**{**gyldig.__dict__, felt: getattr(gyldig, felt).replace(tzinfo=None)})
    resultat = datafeil(kandidat(naiv, id=7))
    assert "ansatt 7" in resultat.grunner[0]
    assert "tidssone" in resultat.grunner[0]


def test_naiv_egen_vakt_som_ville_overlappet_er_likevel_datafeil() -> None:
    naiv = Tidsrom(DAG_START.replace(tzinfo=None), DAG_SLUTT.replace(tzinfo=None))
    datafeil(kandidat(naiv))


@pytest.mark.parametrize("forskyvning", [timedelta(0), timedelta(minutes=-1)])
def test_egen_vakt_med_start_ikke_før_slutt_er_datafeil(forskyvning: timedelta) -> None:
    start = DAG_START + timedelta(hours=1)
    datafeil(kandidat(rom(start, start + forskyvning)))


def test_ugyldig_vakt_hos_den_ene_stopper_hele_vurderingen() -> None:
    ok = kandidat(id=1)
    feil = kandidat(rom(DAG_START, DAG_START), id=2)
    resultat = datafeil(ok, feil)
    assert resultat.datagrense == DATAGRENSE
