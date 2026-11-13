"""11-timersregelen, daglig hvile (story 2.3, FR4, AV-04), og vinduet for datafeil (A5).

Bare enhetsdata i domenet, uten database. Fasiten for #4127 og #4189 testes
gjennom API-et i `tester/api/test_kandidater.py`.

Alle tider i en sammenligning bruker samme `ZoneInfo`-objekt (`OSLO`). Da regner
Python på veggklokka hvis koden glemmer omregningen til UTC, og
sommertidstestene fanger det.
"""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor import elleve_timer, kolliderende_vakt, kompetanse
from domene.regelmotor.elleve_timer import ÅRSAK, bryter_elleve_timer
from domene.regelmotor.vurdering import REGLER, Regel, vurder_kandidater
from domene.typer import Datafeil, Kandidat, Kandidatvurdering, Tidsrom, Vakt

OSLO = ZoneInfo("Europe/Oslo")
# Seeden: periodestart 21.09 − 672 t og periodeslutt 05.10 (beslutning 2A).
HISTORIKKSTART = datetime(2026, 8, 24, 0, 0, tzinfo=OSLO)
DATAGRENSE = datetime(2026, 10, 5, 0, 0, tzinfo=OSLO)
DAG_START = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)
DAG_SLUTT = DAG_START + timedelta(hours=8)
ELLEVE = timedelta(hours=11)
MINUTT = timedelta(minutes=1)


def vakt(vakttype: str = "dag", *, start: datetime = DAG_START, slutt: datetime | None = None,
         minstenivå: int = 1) -> Vakt:
    return Vakt(
        vaktnummer=4127, vakttype=vakttype, start=start,
        slutt=start + timedelta(hours=8) if slutt is None else slutt,
        minstenivå=minstenivå, satt_opp_ansatt_id=None,
    )


def kandidat(*egne: object, id: int = 1, kompetanse: dict | None = None) -> Kandidat:
    nivåer = {"dag": 4, "kveld": 4, "natt": 4} if kompetanse is None else kompetanse
    return Kandidat(id=id, navn=f"Ansatt {id:02d}", kompetanse=nivåer, vakter=egne)  # type: ignore[arg-type]


def rom(start: datetime, slutt: datetime) -> Tidsrom:
    return Tidsrom(start, slutt)


def utc(tid: datetime) -> datetime:
    return tid.astimezone(UTC)


def slutter_ved(slutt: datetime, timer: int = 8) -> Tidsrom:
    """En egen vakt som slutter ved `slutt`, med lengde regnet i faktisk tid."""
    return rom((utc(slutt) - timedelta(hours=timer)).astimezone(OSLO), slutt)


def starter_ved(start: datetime, timer: int = 8) -> Tidsrom:
    return rom(start, (utc(start) + timedelta(hours=timer)).astimezone(OSLO))


def vurder(v: Vakt, *kandidater: Kandidat, historikkstart: datetime = HISTORIKKSTART,
           datagrense: datetime = DATAGRENSE, regler: tuple[Regel, ...] = REGLER) -> Kandidatvurdering:
    resultat = vurder_kandidater(v, kandidater, datagrense, historikkstart, regler)
    assert isinstance(resultat, Kandidatvurdering), resultat
    return resultat


def årsaker(v: Vakt, k: Kandidat, **kw: datetime) -> tuple[str, ...]:
    resultat = vurder(v, k, **kw)
    return resultat.utelukkede[0].årsaker if resultat.utelukkede else ()


def datafeil(v: Vakt, *kandidater: Kandidat, historikkstart: datetime = HISTORIKKSTART,
             datagrense: datetime = DATAGRENSE, regler: tuple[Regel, ...] = REGLER) -> Datafeil:
    resultat = vurder_kandidater(v, kandidater or (kandidat(),), datagrense, historikkstart, regler)
    assert isinstance(resultat, Datafeil), resultat
    assert resultat.grunner
    # Svaret oppgir alltid datagrensen, også når historikkstarten er årsaken.
    assert resultat.datagrense == datagrense
    return resultat


# --- Grensene: 11:00 er gyldig, 10:59 utelukker -----------------------------------


def test_nøyaktig_11_timer_før_er_gyldig() -> None:
    assert årsaker(vakt(), kandidat(slutter_ved(DAG_START - ELLEVE))) == ()


def test_nøyaktig_11_timer_etter_er_gyldig() -> None:
    assert årsaker(vakt(), kandidat(starter_ved(DAG_SLUTT + ELLEVE))) == ()


def test_10_59_før_utelukker() -> None:
    assert årsaker(vakt(), kandidat(slutter_ved(DAG_START - ELLEVE + MINUTT))) == (ÅRSAK,)


def test_10_59_etter_utelukker() -> None:
    assert årsaker(vakt(), kandidat(starter_ved(DAG_SLUTT + ELLEVE - MINUTT))) == (ÅRSAK,)


@pytest.mark.parametrize("hvile_min,brudd", [(659, True), (660, False), (661, False), (0, True), (1, True)])
def test_hvile_før_og_etter_rundt_grensen(hvile_min: int, brudd: bool) -> None:
    hvile = timedelta(minutes=hvile_min)
    assert bryter_elleve_timer(kandidat(slutter_ved(DAG_START - hvile)), vakt()) is brudd
    assert bryter_elleve_timer(kandidat(starter_ved(DAG_SLUTT + hvile)), vakt()) is brudd


def test_vakt_som_møter_vakten_før_utelukker_på_11_timer_ikke_kollisjon() -> None:
    # 0 t hvile: halvåpne intervall kolliderer ikke, men hvilen er 0.
    assert årsaker(vakt(), kandidat(slutter_ved(DAG_START))) == (ÅRSAK,)


def test_vakt_som_møter_vakten_etter_utelukker_på_11_timer_ikke_kollisjon() -> None:
    assert årsaker(vakt(), kandidat(starter_ved(DAG_SLUTT))) == (ÅRSAK,)


def test_ingen_egne_vakter_innenfor_11_timer_utelukkes_ikke() -> None:
    langt_før = slutter_ved(DAG_START - timedelta(hours=30))
    langt_etter = starter_ved(DAG_SLUTT + timedelta(hours=30))
    assert årsaker(vakt(), kandidat(langt_før, langt_etter)) == ()
    assert årsaker(vakt(), kandidat()) == ()


def test_dag_etter_kveld_dagen_før_utelukker() -> None:
    # Kveld 26.09 15–23 og dag 27.09 07–15: 8 t hvile.
    kveld = rom(datetime(2026, 9, 26, 15, 0, tzinfo=OSLO), datetime(2026, 9, 26, 23, 0, tzinfo=OSLO))
    assert årsaker(vakt(), kandidat(kveld)) == (ÅRSAK,)


def test_natt_etter_dag_samme_dato_utelukker() -> None:
    # Natt 28.09 23–07 etter dag 28.09 07–15: 8 t hvile. Etter natten: dag 29.09 15–23 gir 8 t.
    natt = vakt("natt", start=datetime(2026, 9, 28, 23, 0, tzinfo=OSLO))
    dag = rom(datetime(2026, 9, 28, 7, 0, tzinfo=OSLO), datetime(2026, 9, 28, 15, 0, tzinfo=OSLO))
    kveld_etter = rom(datetime(2026, 9, 29, 15, 0, tzinfo=OSLO), datetime(2026, 9, 29, 23, 0, tzinfo=OSLO))
    assert årsaker(natt, kandidat(dag)) == (ÅRSAK,)
    assert årsaker(natt, kandidat(kveld_etter)) == (ÅRSAK,)
    # Kveld 29.09 18:00 gir nøyaktig 11 t etter natten.
    assert årsaker(natt, kandidat(starter_ved(datetime(2026, 9, 29, 18, 0, tzinfo=OSLO)))) == ()


# --- Nærmeste vakt og overlapp (beslutning A) ------------------------------------


def test_nærmeste_vakt_før_avgjør_også_når_en_fjernere_er_i_orden() -> None:
    fjern = slutter_ved(DAG_START - timedelta(hours=40))
    nær = slutter_ved(DAG_START - timedelta(hours=10))
    assert årsaker(vakt(), kandidat(fjern, nær)) == (ÅRSAK,)
    assert årsaker(vakt(), kandidat(nær, fjern)) == (ÅRSAK,)


def test_overlappende_vakt_teller_bare_som_kolliderende_vakt() -> None:
    # Beslutning A (Mithad 2026-11-11, OP-12): én årsak for samme forhold.
    for egen in (
        rom(DAG_START - timedelta(hours=1), DAG_START + timedelta(hours=1)),
        rom(DAG_SLUTT - timedelta(hours=1), DAG_SLUTT + timedelta(hours=1)),
        rom(DAG_START, DAG_SLUTT),
        rom(DAG_START - timedelta(hours=1), DAG_SLUTT + timedelta(hours=1)),
    ):
        assert årsaker(vakt(), kandidat(egen)) == (kolliderende_vakt.ÅRSAK,), egen
        assert not bryter_elleve_timer(kandidat(egen), vakt())


def test_overlapp_og_en_annen_vakt_for_nær_gir_begge_årsakene() -> None:
    overlapp = rom(DAG_START + timedelta(hours=2), DAG_START + timedelta(hours=3))
    for_nær = slutter_ved(DAG_START - timedelta(hours=5))
    assert årsaker(vakt(), kandidat(overlapp, for_nær)) == (kolliderende_vakt.ÅRSAK, ÅRSAK)


def test_for_lavt_nivå_og_for_kort_hvile_gir_begge_årsakene_i_fast_rekkefølge() -> None:
    k = kandidat(slutter_ved(DAG_START), kompetanse={"dag": 1})
    assert årsaker(vakt(minstenivå=3), k) == (kompetanse.ÅRSAK, ÅRSAK)


def test_regelen_ligger_som_nummer_tre_av_fire_i_regellisten() -> None:
    assert ÅRSAK == "11-timersregelen"
    assert [r.årsak for r in REGLER] == ["kompetanse-minstekrav", "kolliderende vakt", "11-timersregelen", "35-timersregelen"]
    assert REGLER[2].bryter is elleve_timer.bryter_elleve_timer
    assert REGLER[2].vindu is elleve_timer.vindu


# --- Sommertid: faktisk forløpt tid i UTC -----------------------------------------
# Seedens dekning går 24.08–05.10, så testene sender egne grenser.


def test_vårskiftet_11_timer_på_veggklokka_er_10_faktiske_og_utelukker() -> None:
    # Natt til 29.03.2026 går klokka fra 02:00 til 03:00.
    egen_slutt = datetime(2026, 3, 28, 20, 0, tzinfo=OSLO)
    vakt_start = datetime(2026, 3, 29, 7, 0, tzinfo=OSLO)
    assert vakt_start.replace(tzinfo=None) - egen_slutt.replace(tzinfo=None) == ELLEVE
    assert utc(vakt_start) - utc(egen_slutt) == timedelta(hours=10)
    egen = rom(datetime(2026, 3, 28, 12, 0, tzinfo=OSLO), egen_slutt)
    grenser = {"historikkstart": datetime(2026, 3, 1, tzinfo=OSLO), "datagrense": datetime(2026, 4, 30, tzinfo=OSLO)}
    v = vakt(start=vakt_start, slutt=datetime(2026, 3, 29, 15, 0, tzinfo=OSLO))
    assert årsaker(v, kandidat(egen), **grenser) == (ÅRSAK,)


def test_vårskiftet_etter_vakten() -> None:
    # Kveld 28.03 15–23, neste vakt 29.03 10:00: 11 t på veggklokka, 10 faktiske.
    v = vakt("kveld", start=datetime(2026, 3, 28, 15, 0, tzinfo=OSLO), slutt=datetime(2026, 3, 28, 23, 0, tzinfo=OSLO))
    neste = rom(datetime(2026, 3, 29, 10, 0, tzinfo=OSLO), datetime(2026, 3, 29, 18, 0, tzinfo=OSLO))
    grenser = {"historikkstart": datetime(2026, 3, 1, tzinfo=OSLO), "datagrense": datetime(2026, 4, 30, tzinfo=OSLO)}
    assert årsaker(v, kandidat(neste), **grenser) == (ÅRSAK,)


def test_høstskiftet_10_5_timer_på_veggklokka_er_11_5_faktiske_og_er_gyldig() -> None:
    # Natt til 25.10.2026 går klokka fra 03:00 til 02:00.
    egen_slutt = datetime(2026, 10, 24, 20, 30, tzinfo=OSLO)
    vakt_start = datetime(2026, 10, 25, 7, 0, tzinfo=OSLO)
    assert vakt_start.replace(tzinfo=None) - egen_slutt.replace(tzinfo=None) == timedelta(hours=10, minutes=30)
    assert utc(vakt_start) - utc(egen_slutt) == timedelta(hours=11, minutes=30)
    egen = rom(datetime(2026, 10, 24, 12, 30, tzinfo=OSLO), egen_slutt)
    grenser = {"historikkstart": datetime(2026, 10, 1, tzinfo=OSLO), "datagrense": datetime(2026, 11, 30, tzinfo=OSLO)}
    v = vakt(start=vakt_start, slutt=datetime(2026, 10, 25, 15, 0, tzinfo=OSLO))
    assert årsaker(v, kandidat(egen), **grenser) == ()


def test_høstskiftet_etter_vakten() -> None:
    # Kveld 24.10 15–23, neste vakt 25.10 09:30: 10,5 t på veggklokka, 11,5 faktiske.
    v = vakt("kveld", start=datetime(2026, 10, 24, 15, 0, tzinfo=OSLO), slutt=datetime(2026, 10, 24, 23, 0, tzinfo=OSLO))
    neste = rom(datetime(2026, 10, 25, 9, 30, tzinfo=OSLO), datetime(2026, 10, 25, 17, 30, tzinfo=OSLO))
    grenser = {"historikkstart": datetime(2026, 10, 1, tzinfo=OSLO), "datagrense": datetime(2026, 11, 30, tzinfo=OSLO)}
    assert årsaker(v, kandidat(neste), **grenser) == ()


def test_vinduet_regnes_i_utc_over_vårskiftet() -> None:
    # Vakten starter 29.03 07:00 CEST = 05:00 UTC. Vinduet starter 11 faktiske timer
    # før, 28.03 18:00 UTC = 19:00 CET. På veggklokka ville det blitt 20:00 CET.
    v = vakt(start=datetime(2026, 3, 29, 7, 0, tzinfo=OSLO), slutt=datetime(2026, 3, 29, 15, 0, tzinfo=OSLO))
    assert elleve_timer.vindu(v).start == datetime(2026, 3, 28, 18, 0, tzinfo=UTC)
    grense = datetime(2026, 4, 30, tzinfo=OSLO)
    ved = datetime(2026, 3, 28, 19, 0, tzinfo=OSLO)
    assert vurder(v, kandidat(), historikkstart=ved, datagrense=grense, regler=ELLEVE_REGLER).gyldige
    datafeil(v, historikkstart=ved + MINUTT, datagrense=grense, regler=ELLEVE_REGLER)


# --- Determinisme ---------------------------------------------------------------


def test_samme_input_gir_samme_output() -> None:
    kandidater = [kandidat(slutter_ved(DAG_START - timedelta(hours=i)), id=i) for i in range(1, 25)]
    v = vakt()
    første = vurder(v, *kandidater)
    assert første.gyldige and første.utelukkede
    for _ in range(3):
        assert vurder(v, *kandidater) == første
        assert vurder(v, *reversed(kandidater)) == første
    assert [k.id for k in første.gyldige] == list(range(11, 25))


# --- Vinduet og datadekningen (P-08, vedtak A5) ---------------------------------
# Vakten 27.09 07–15 har vinduet [26.09 20:00, 28.09 02:00). Fra story 2.4 starter
# det samlede vinduet ved mandag 21.09 (35-timersregelen), så testene av
# startgrensen til 11-timersvinduet kjører uten regel fire.
ELLEVE_REGLER = REGLER[:3]
V_START = DAG_START - ELLEVE
V_SLUTT = DAG_SLUTT + ELLEVE


def test_vinduet_til_regelen() -> None:
    assert elleve_timer.vindu(vakt()) == Tidsrom(utc(V_START), utc(V_SLUTT))
    assert kolliderende_vakt.vindu(vakt()) == Tidsrom(utc(DAG_START), utc(DAG_SLUTT))
    assert REGLER[0].vindu(vakt()) is None


def test_vindu_nøyaktig_ved_datagrensen_vurderes() -> None:
    # slutt + 11 t == datagrense
    v = vakt(start=DATAGRENSE - ELLEVE - timedelta(hours=8))
    assert v.slutt == datetime(2026, 10, 4, 13, 0, tzinfo=OSLO)
    assert vurder(v, kandidat()).gyldige


def test_vindu_ett_minutt_over_datagrensen_er_datafeil() -> None:
    v = vakt(start=DATAGRENSE - ELLEVE - timedelta(hours=8) + MINUTT)
    assert "datagrensen" in datafeil(v).grunner[0]


@pytest.mark.parametrize("start,vakttype", [
    (datetime(2026, 10, 4, 7, 0, tzinfo=OSLO), "dag"),
    (datetime(2026, 10, 4, 15, 0, tzinfo=OSLO), "kveld"),
    (datetime(2026, 10, 4, 23, 0, tzinfo=OSLO), "natt"),
])
def test_vakter_04_10_er_datafeil_som_p08_krever(start: datetime, vakttype: str) -> None:
    datafeil(vakt(vakttype, start=start))


def test_vindu_nøyaktig_ved_historikkstart_vurderes() -> None:
    # start − 11 t == historikkstart
    assert vurder(vakt(), kandidat(), historikkstart=V_START, regler=ELLEVE_REGLER).gyldige


def test_vindu_ett_minutt_før_historikkstart_er_datafeil() -> None:
    resultat = datafeil(vakt(), historikkstart=V_START + MINUTT, regler=ELLEVE_REGLER)
    assert "historikkstarten" in resultat.grunner[0]


def test_seedens_historikkstart_dekker_vakt_tidlig_i_perioden() -> None:
    # Periodestart 21.09 00:00: vinduet starter 20.09 13:00, langt etter 24.08.
    v = vakt(start=datetime(2026, 9, 21, 0, 0, tzinfo=OSLO))
    assert vurder(v, kandidat()).gyldige


def test_historikkstart_uten_tidssone_er_datafeil() -> None:
    datafeil(vakt(), historikkstart=HISTORIKKSTART.replace(tzinfo=None))


def test_ugyldig_vakt_stopper_før_vinduet_regnes_ut() -> None:
    # start >= slutt hos Vakten: én grunn, ingen vindusgrunn.
    resultat = datafeil(vakt(slutt=DAG_START))
    assert resultat.grunner == ("vakt 4127: start er ikke før slutt",)


def test_ugyldig_vakt_langt_unna_vurderes_normalt() -> None:
    # Uke 35, Vakt 27.09: kan ikke påvirke noen regel (A5).
    uke_35 = datetime(2026, 8, 26, 7, 0, tzinfo=OSLO)
    ugyldig = rom(uke_35, uke_35 - timedelta(hours=2))
    k = kandidat(ugyldig, id=2)
    resultat = vurder(vakt(), k)
    assert [g.id for g in resultat.gyldige] == [2]


def test_ugyldig_vakt_i_vinduet_er_datafeil() -> None:
    i_vinduet = DAG_START - timedelta(hours=5)
    datafeil(vakt(), kandidat(id=1), kandidat(rom(i_vinduet, i_vinduet), id=2))


def test_ugyldig_vakt_i_vinduet_hos_den_som_var_satt_opp_gir_ikke_datafeil() -> None:
    i_vinduet = DAG_START - timedelta(hours=5)
    v = Vakt(4127, "dag", DAG_START, DAG_SLUTT, 1, satt_opp_ansatt_id=2)
    assert vurder(v, kandidat(id=1), kandidat(rom(i_vinduet, i_vinduet), id=2)).gyldige


def test_punkt_i_vinduets_start_er_innenfor() -> None:
    datafeil(vakt(), kandidat(rom(V_START, V_START)), regler=ELLEVE_REGLER)


def test_punkt_i_vinduets_slutt_er_utenfor() -> None:
    assert vurder(vakt(), kandidat(rom(V_SLUTT, V_SLUTT))).gyldige


def test_omvendt_vakt_rett_før_vinduet_er_utenfor() -> None:
    # Det lukkede tidsrommet [V_START − 3 t, V_START − 1 min] berører ikke vinduet.
    assert vurder(vakt(), kandidat(rom(V_START - MINUTT, V_START - timedelta(hours=3))), regler=ELLEVE_REGLER).gyldige


def test_omvendt_vakt_som_slutter_i_vinduets_start_er_innenfor() -> None:
    # Det lukkede tidsrommet [V_START − 3 t, V_START] når vinduets start.
    datafeil(vakt(), kandidat(rom(V_START, V_START - timedelta(hours=3))), regler=ELLEVE_REGLER)


def test_omvendt_vakt_som_spenner_over_hele_vinduet_er_innenfor() -> None:
    datafeil(vakt(), kandidat(rom(V_SLUTT + timedelta(hours=1), V_START - timedelta(hours=1))))


def test_omvendt_vakt_som_starter_ett_minutt_før_vinduets_slutt_er_innenfor() -> None:
    datafeil(vakt(), kandidat(rom(V_SLUTT + timedelta(hours=2), V_SLUTT - MINUTT)))


@pytest.mark.parametrize("felt", ["start", "slutt"])
def test_egen_vakt_uten_tidssone_er_datafeil_også_langt_unna(felt: str) -> None:
    langt_unna = rom(datetime(2026, 8, 26, 7, 0, tzinfo=OSLO), datetime(2026, 8, 26, 15, 0, tzinfo=OSLO))
    naiv = Tidsrom(**{**langt_unna.__dict__, felt: getattr(langt_unna, felt).replace(tzinfo=None)})
    resultat = datafeil(vakt(), kandidat(naiv, id=7))
    assert "ansatt 7" in resultat.grunner[0] and "tidssone" in resultat.grunner[0]


def test_gyldig_vakt_utenfor_datadekningen_hos_kandidaten_er_i_orden() -> None:
    # Det er vinduet som må være dekket, ikke Kandidatens historikk.
    tidlig = rom(datetime(2026, 8, 1, 7, 0, tzinfo=OSLO), datetime(2026, 8, 1, 15, 0, tzinfo=OSLO))
    assert vurder(vakt(), kandidat(tidlig)).gyldige
