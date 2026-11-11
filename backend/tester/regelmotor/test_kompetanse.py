"""Kompetanse-minstekrav og grunnmønsteret i vurderingen (story 2.1).

Bare enhetsdata i domenet, uten database. Fasiten for #4127 og #4189 testes
gjennom API-et i `tester/api/test_kandidater.py`.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from domene.regelmotor.kompetanse import ÅRSAK, bryter_kompetanse, kompetansenivå
from domene.regelmotor.vurdering import REGLER, Regel, vurder_kandidater
from domene.typer import Datafeil, Kandidat, Kandidatvurdering, Vakt

OSLO = ZoneInfo("Europe/Oslo")
DATAGRENSE = datetime(2026, 10, 5, 0, 0, tzinfo=OSLO)
DAG_START = datetime(2026, 9, 27, 7, 0, tzinfo=OSLO)


def vakt(vakttype: str = "dag", minstenivå: int = 3, *, start: datetime = DAG_START,
         slutt: datetime | None = None, satt_opp: int | None = None) -> Vakt:
    return Vakt(
        vaktnummer=4127, vakttype=vakttype, start=start,
        slutt=start + timedelta(hours=8) if slutt is None else slutt,
        minstenivå=minstenivå, satt_opp_ansatt_id=satt_opp,
    )


def kandidat(id: int, kompetanse: dict, navn: str | None = None) -> Kandidat:
    return Kandidat(id=id, navn=navn or f"Ansatt {id:02d}", kompetanse=kompetanse)


def vurder(v: Vakt, *kandidater: Kandidat, **kw) -> Kandidatvurdering:  # type: ignore[no-untyped-def]
    resultat = vurder_kandidater(v, kandidater, DATAGRENSE, **kw)
    assert isinstance(resultat, Kandidatvurdering), resultat
    return resultat


def gyldige_id(resultat: Kandidatvurdering) -> list[int]:
    return [k.id for k in resultat.gyldige]


# --- Selve regelen: matrisen og grensene 1–4 -----------------------------------


@pytest.mark.parametrize("nivå,minstenivå,gyldig", [
    (nivå, minstenivå, nivå >= minstenivå) for nivå in range(1, 5) for minstenivå in range(1, 5)
])
def test_gyldig_bare_ved_nivå_lik_eller_over_minstenivå(nivå: int, minstenivå: int, gyldig: bool) -> None:
    resultat = vurder(vakt("dag", minstenivå), kandidat(1, {"dag": nivå}))
    assert gyldige_id(resultat) == ([1] if gyldig else [])
    if not gyldig:
        assert resultat.utelukkede[0].årsaker == (ÅRSAK,)


def test_lik_minstekrav_er_gyldig_og_ett_under_utelukkes() -> None:
    resultat = vurder(vakt("dag", 3), kandidat(1, {"dag": 3}), kandidat(2, {"dag": 2}))
    assert gyldige_id(resultat) == [1]
    (utelukket,) = resultat.utelukkede
    assert utelukket.kandidat.id == 2
    assert utelukket.årsaker == ("kompetanse-minstekrav",)


@pytest.mark.parametrize("vakttype", ["dag", "kveld", "natt"])
def test_manglende_nivå_for_vakttypen_utelukker(vakttype: str) -> None:
    andre = {t: 4 for t in ("dag", "kveld", "natt") if t != vakttype}
    resultat = vurder(vakt(vakttype, 1), kandidat(1, andre))
    assert gyldige_id(resultat) == []
    assert resultat.utelukkede[0].årsaker == (ÅRSAK,)


def test_tom_kompetanse_utelukker_og_er_ikke_datafeil() -> None:
    resultat = vurder(vakt("natt", 1), kandidat(1, {}))
    assert resultat.utelukkede[0].årsaker == (ÅRSAK,)


def test_mellomvakt_bruker_nivået_for_dag() -> None:
    v = vakt("mellom", 3, start=datetime(2026, 9, 27, 10, 0, tzinfo=OSLO))
    resultat = vurder(v, kandidat(1, {"dag": 3}), kandidat(2, {"kveld": 4}), kandidat(3, {"dag": 2, "kveld": 4}))
    assert gyldige_id(resultat) == [1]
    assert [u.kandidat.id for u in resultat.utelukkede] == [2, 3]
    assert kompetansenivå(kandidat(1, {"dag": 3}), v) == 3
    assert kompetansenivå(kandidat(2, {"kveld": 4}), v) is None


def test_mellom_som_egen_nøkkel_brukes_ikke() -> None:
    v = vakt("mellom", 3)
    assert bryter_kompetanse(kandidat(1, {"mellom": 4}), v)


def test_minstekravet_senkes_ikke_når_ingen_oppfyller_det() -> None:
    resultat = vurder(vakt("dag", 4), *(kandidat(i, {"dag": 3}) for i in range(1, 6)))
    assert resultat.gyldige == ()
    assert len(resultat.utelukkede) == 5


def test_kompetansenivå_er_nivået_for_vakttypen() -> None:
    k = kandidat(1, {"dag": 2, "kveld": 3, "natt": 4})
    assert [kompetansenivå(k, vakt(t)) for t in ("dag", "mellom", "kveld", "natt")] == [2, 2, 3, 4]


# --- Kandidatgrunnlaget, alle årsaker, rekkefølge og determinisme ------------


def test_den_som_var_satt_opp_er_ikke_i_grunnlaget() -> None:
    resultat = vurder(vakt("dag", 1, satt_opp=1), kandidat(1, {"dag": 4}), kandidat(2, {"dag": 4}))
    alle = gyldige_id(resultat) + [u.kandidat.id for u in resultat.utelukkede]
    assert alle == [2]


def test_satt_opp_med_ugyldig_kompetanse_gir_ikke_datafeil() -> None:
    # Den som var satt opp, vurderes ikke, så dataene hennes er ikke grunnlag.
    resultat = vurder(vakt("dag", 1, satt_opp=1), kandidat(1, {"dag": 0}), kandidat(2, {"dag": 4}))
    assert gyldige_id(resultat) == [2]


def test_alle_årsaker_samles_uten_å_stoppe_ved_første_brudd() -> None:
    kall: list[int] = []

    def alltid_brudd(k: Kandidat, _v: Vakt) -> bool:
        kall.append(k.id)
        return True

    ekstra = Regel(årsak="testregel", bryter=alltid_brudd, vaktkrav=lambda _v: [], kandidatkrav=lambda _k, _v: [])
    resultat = vurder(vakt("dag", 3), kandidat(1, {"dag": 1}), kandidat(2, {"dag": 4}), regler=REGLER + (ekstra,))

    assert resultat.gyldige == ()
    årsaker = {u.kandidat.id: u.årsaker for u in resultat.utelukkede}
    assert årsaker == {1: (ÅRSAK, "testregel"), 2: ("testregel",)}
    # Også Kandidaten som allerede brøt kompetansekravet, ble sjekket mot neste regel.
    assert sorted(kall) == [1, 2]


def test_norsk_alfabetisk_rekkefølge_med_id_som_likhetsbryter() -> None:
    navn = ["Åse Berg", "Øystein Lie", "Ærlig Dahl", "Zara Moe", "anne Holm", "Anne Holm",
            "Émile Aas", "Per Halvorsen", "Peran Ask", "Thomas Nygård", "Thomas Nygaard"]
    kandidater = [kandidat(i, {"dag": 4}, n) for i, n in enumerate(navn, start=10)]
    # Samme navn to ganger: id avgjør.
    kandidater += [kandidat(3, {"dag": 4}, "Anne Holm")]

    resultat = vurder(vakt("dag", 1), *reversed(kandidater))

    assert [(k.navn, k.id) for k in resultat.gyldige] == [
        ("Anne Holm", 3), ("Anne Holm", 15), ("anne Holm", 14),
        ("Émile Aas", 16), ("Per Halvorsen", 17), ("Peran Ask", 18),
        ("Thomas Nygaard", 20), ("Thomas Nygård", 19),
        ("Zara Moe", 13), ("Ærlig Dahl", 12), ("Øystein Lie", 11), ("Åse Berg", 10),
    ]


def test_å_i_nfd_form_sorteres_som_å() -> None:
    nfd = "Åse Berg"  # Å skrevet som A + kombinerende ring
    resultat = vurder(vakt("dag", 1), kandidat(1, {"dag": 4}, nfd), kandidat(2, {"dag": 4}, "Zara Moe"),
                      kandidat(3, {"dag": 4}, "Anne Holm"))
    assert [k.id for k in resultat.gyldige] == [3, 2, 1]


def test_utelukkede_er_også_sortert() -> None:
    resultat = vurder(vakt("dag", 4), kandidat(2, {"dag": 1}, "Åse"), kandidat(1, {"dag": 1}, "Berit"))
    assert [u.kandidat.navn for u in resultat.utelukkede] == ["Berit", "Åse"]


def test_samme_input_gir_samme_output_uansett_rekkefølge_inn() -> None:
    kandidater = [kandidat(i, {"dag": 1 + i % 4, "natt": 4}, f"Navn {chr(80 - i)}") for i in range(1, 13)]
    v = vakt("dag", 3)
    forste = vurder_kandidater(v, kandidater, DATAGRENSE)
    for _ in range(3):
        assert vurder_kandidater(v, kandidater, DATAGRENSE) == forste
        assert vurder_kandidater(v, list(reversed(kandidater)), DATAGRENSE) == forste


def test_vurderingen_endrer_ikke_grunnlaget() -> None:
    kompetanse = {"dag": 3}
    k = kandidat(1, kompetanse)
    kompetanse["dag"] = 1
    assert gyldige_id(vurder(vakt("dag", 3), k)) == [1]
    with pytest.raises(TypeError):
        k.kompetanse["dag"] = 1  # type: ignore[index]


# --- Datafeil (P-08): ingen Kandidat vurderes ---------------------------------


def datafeil(v: Vakt, *kandidater: Kandidat, datagrense: datetime = DATAGRENSE) -> Datafeil:
    resultat = vurder_kandidater(v, kandidater or (kandidat(1, {"dag": 4}),), datagrense)
    assert isinstance(resultat, Datafeil), resultat
    assert resultat.datagrense == datagrense
    assert resultat.grunner
    return resultat


def test_vakt_som_slutter_ved_datagrensen_er_gyldig_og_ett_minutt_etter_er_datafeil() -> None:
    ved = vakt("kveld", 1, start=DATAGRENSE - timedelta(hours=8))
    assert isinstance(vurder_kandidater(ved, [kandidat(1, {"kveld": 1})], DATAGRENSE), Kandidatvurdering)

    etter = vakt("kveld", 1, start=DATAGRENSE - timedelta(hours=8) + timedelta(minutes=1))
    assert etter.slutt == datetime(2026, 10, 5, 0, 1, tzinfo=OSLO)
    assert "datagrensen" in datafeil(etter, kandidat(1, {"kveld": 1})).grunner[0]


def test_nattevakt_over_datagrensen_er_datafeil() -> None:
    # Som #4265: natt 04.10 23:00–05.10 07:00.
    natt = vakt("natt", 2, start=datetime(2026, 10, 4, 23, 0, tzinfo=OSLO))
    datafeil(natt, kandidat(1, {"natt": 4}))


def test_datagrensen_sammenlignes_på_tidspunkt_ikke_offset() -> None:
    # 05.10 00:00 i Oslo er 04.10 22:00 UTC.
    grense_utc = DATAGRENSE.astimezone(timezone.utc)
    ved = vakt("kveld", 1, start=DATAGRENSE - timedelta(hours=8))
    assert isinstance(vurder_kandidater(ved, [kandidat(1, {"kveld": 1})], grense_utc), Kandidatvurdering)


@pytest.mark.parametrize("minstenivå", [0, 5, -1, True])
def test_ugyldig_minstenivå_er_datafeil_ikke_utelukkelse(minstenivå: int) -> None:
    datafeil(vakt("dag", minstenivå))


@pytest.mark.parametrize("verdi", [0, 5, "3", 3.0, None, True])
def test_ugyldig_kompetanseverdi_er_datafeil_ikke_utelukkelse(verdi: object) -> None:
    # Også verdien for en annen vakttype enn Vaktens.
    datafeil(vakt("dag", 1), kandidat(1, {"dag": 4}), kandidat(2, {"dag": 4, "natt": verdi}))


def test_kompetanse_som_ikke_er_en_tabell_er_datafeil() -> None:
    datafeil(vakt("dag", 1), kandidat(1, [("dag", 4)]))  # type: ignore[arg-type]


@pytest.mark.parametrize("slutt", [DAG_START, DAG_START - timedelta(minutes=1)])
def test_start_ikke_før_slutt_er_datafeil(slutt: datetime) -> None:
    datafeil(vakt("dag", 1, slutt=slutt))


def test_start_før_slutt_regnes_på_faktisk_tid_over_sommertidsskiftet() -> None:
    # 25.10.2026 går klokka fra 03:00 til 02:00. 02:30 sommertid kommer før
    # 02:10 vintertid, selv om veggklokka sier det motsatte.
    start = datetime(2026, 10, 25, 2, 30, tzinfo=OSLO, fold=0)
    slutt = datetime(2026, 10, 25, 2, 10, tzinfo=OSLO, fold=1)
    grense = datetime(2026, 11, 1, tzinfo=OSLO)
    resultat = vurder_kandidater(vakt("natt", 1, start=start, slutt=slutt), [kandidat(1, {"natt": 1})], grense)
    assert isinstance(resultat, Kandidatvurdering)


@pytest.mark.parametrize("felt", ["start", "slutt"])
def test_tid_uten_tidssone_er_datafeil(felt: str) -> None:
    v = vakt("dag", 1)
    naiv = getattr(v, felt).replace(tzinfo=None)
    datafeil(Vakt(**{**v.__dict__, felt: naiv}))


def test_ukjent_vakttype_er_datafeil() -> None:
    datafeil(vakt("helg", 1))


def test_datafeil_samler_alle_grunnene() -> None:
    v = vakt("dag", 0, slutt=DAG_START)
    resultat = datafeil(v, kandidat(1, {"dag": "3"}))
    assert len(resultat.grunner) == 3
