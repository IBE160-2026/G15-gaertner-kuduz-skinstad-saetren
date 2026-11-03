"""Tester for testdataene i story 1.2 mot en database i `tmp_path`.

Hjelpefunksjonene for de fire harde reglene og for Ulempepoeng finnes bare her.
De er ikke regelmotoren (Epic 2) eller Ulempemodellen (story 4.7), men en
uavhengig kontroll av at dataene gir fasiten. All tidsaritmetikk skjer i UTC,
fordi subtraksjon av to datetime med samme tzinfo ellers bruker veggklokketid.
"""

import os
import subprocess
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Engine, func, inspect, select, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from adaptere.lagring.database import (
    MILJOVARIABEL,
    STANDARD_STI,
    database_sti,
    lag_engine,
    lag_sessionmaker,
    opprett_skjema,
)
from adaptere.lagring.modeller import AnsattRad, TurnusRad, VaktRad
from adaptere.lagring.testdata import FASIT, HISTORIKK, PERIODE, PREFERANSER, VAKTTIDER, fyll_testdata

OSLO = ZoneInfo("Europe/Oslo")
UTC = ZoneInfo("UTC")
BACKEND = Path(__file__).resolve().parents[2]

REGLER = ("kompetanse", "kolliderende", "elleve-timer", "trettifem-timer")
PREFERANSEPOENG = {tekst: poeng for tekst, poeng in PREFERANSER.values()}


# --- Hjelpefunksjoner -------------------------------------------------------


@dataclass(frozen=True)
class Intervall:
    start: datetime  # UTC
    slutt: datetime  # UTC


def intervall(vakt: VaktRad) -> Intervall:
    return Intervall(vakt.start.astimezone(UTC), vakt.slutt.astimezone(UTC))


def timer(fra: datetime, til: datetime) -> float:
    return (til.astimezone(UTC) - fra.astimezone(UTC)) / timedelta(hours=1)


def overlapper(a: Intervall, b: Intervall) -> bool:
    """Halvåpne [start, slutt): vakter som møtes i et skift, overlapper ikke."""
    return a.start < b.slutt and b.start < a.slutt


def kalenderuke(t: datetime) -> Intervall:
    """Mandag 00:00 til neste mandag 00:00 i Europe/Oslo, som UTC."""
    lokal = t.astimezone(OSLO).date()
    mandag = lokal - timedelta(days=lokal.weekday())
    return Intervall(
        datetime.combine(mandag, time(0), tzinfo=OSLO).astimezone(UTC),
        datetime.combine(mandag + timedelta(days=7), time(0), tzinfo=OSLO).astimezone(UTC),
    )


def berorte_uker(maal: Intervall) -> list[Intervall]:
    uker = [kalenderuke(maal.start)]
    while uker[-1].slutt < maal.slutt:
        uker.append(kalenderuke(uker[-1].slutt))
    return uker


def lengste_fri(vakter: list[Intervall], uke: Intervall) -> float:
    """Lengste sammenhengende fri i uka, regnet fra unionen av vaktene."""
    klippet = sorted(
        (max(v.start, uke.start), min(v.slutt, uke.slutt))
        for v in vakter
        if overlapper(v, uke)
    )
    lengste, fri_fra = 0.0, uke.start
    for start, slutt in klippet:
        if start > fri_fra:
            lengste = max(lengste, timer(fri_fra, start))
        fri_fra = max(fri_fra, slutt)
    return max(lengste, timer(fri_fra, uke.slutt))


def bryter_kompetanse(ansatt: AnsattRad, vakt: VaktRad) -> bool:
    vakttype = "dag" if vakt.vakttype == "mellom" else vakt.vakttype
    nivaa = ansatt.kompetanse.get(vakttype)
    return nivaa is None or nivaa < vakt.minstenivå


def bryter_kollisjon(egne: list[Intervall], maal: Intervall) -> bool:
    return any(overlapper(v, maal) for v in egne)


def bryter_elleve_timer(egne: list[Intervall], maal: Intervall) -> bool:
    """Nærmeste ikke-overlappende vakt før eller etter gir under 11 t hvile."""
    ikke_overlappende = [v for v in egne if not overlapper(v, maal)]
    foer = [v.slutt for v in ikke_overlappende if v.slutt <= maal.start]
    etter = [v.start for v in ikke_overlappende if v.start >= maal.slutt]
    return bool(
        (foer and timer(max(foer), maal.start) < 11)
        or (etter and timer(maal.slutt, min(etter)) < 11)
    )


def bryter_trettifem_timer(egne: list[Intervall], maal: Intervall) -> bool:
    """Med vakten lagt til mangler en berørt kalenderuke 35 t sammenhengende fri."""
    return any(lengste_fri(egne + [maal], uke) < 35 for uke in berorte_uker(maal))


def brudd(ansatt: AnsattRad, egne: list[Intervall], vakt: VaktRad) -> set[str]:
    maal = intervall(vakt)
    resultat = {
        "kompetanse": bryter_kompetanse(ansatt, vakt),
        "kolliderende": bryter_kollisjon(egne, maal),
        "elleve-timer": bryter_elleve_timer(egne, maal),
        "trettifem-timer": bryter_trettifem_timer(egne, maal),
    }
    return {regel for regel, brutt in resultat.items() if brutt}


def ulempepoeng_per_time(lokal: datetime) -> int:
    """PRD §4.3: natt > helg > kveld > dag. Helligdager er vanlige dager."""
    if lokal.hour >= 22 or lokal.hour < 6:
        return 3
    if lokal.weekday() >= 5:
        return 2
    if lokal.hour >= 18:
        return 1
    return 0


def ulempepoeng(egne: list[Intervall], vaktstart: datetime) -> float:
    """Ulempepoeng i [start − 672 t, start), med minuttoppløsning (AV-09)."""
    slutt = vaktstart.astimezone(UTC)
    start = slutt - timedelta(hours=672)
    minutter = 0
    for v in egne:
        t, til = max(v.start, start), min(v.slutt, slutt)
        while t < til:
            minutter += ulempepoeng_per_time(t.astimezone(OSLO))
            t += timedelta(minutes=1)
    return minutter / 60


def timer_i_uka(egne: list[Intervall], uke: Intervall) -> float:
    """Planlagte timer i Vakter som starter i kalenderuka (FR-8)."""
    return sum(timer(v.start, v.slutt) for v in egne if uke.start <= v.start < uke.slutt)


def kostnad(timelonn: int, timer_foer: float, vaktlengde: float = 8) -> float:
    """Timer til og med 36 i uka til ordinær sats, resten til 150 % (PRD §4.3)."""
    ordinaer = max(0.0, min(vaktlengde, 36 - timer_foer))
    return timelonn * (ordinaer + 1.5 * (vaktlengde - ordinaer))


# --- Fixtures ----------------------------------------------------------------


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = lag_engine(tmp_path / "test.db")
    opprett_skjema(engine)
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with lag_sessionmaker(engine)() as session:
        yield session


@dataclass
class Data:
    turnus: TurnusRad
    ansatte: dict[int, AnsattRad]
    vakter: list[VaktRad]

    def ansatt(self, navn: str) -> AnsattRad:
        (treff,) = [a for a in self.ansatte.values() if a.navn == navn]
        return treff

    def vakt(self, vaktnummer: int) -> VaktRad:
        (treff,) = [v for v in self.vakter if v.vaktnummer == vaktnummer]
        return treff

    def egne(self, ansatt_id: int) -> list[Intervall]:
        return sorted(
            (intervall(v) for v in self.vakter if v.tildelt_ansatt_id == ansatt_id),
            key=lambda v: v.start,
        )

    def kandidater(self, vakt: VaktRad) -> list[AnsattRad]:
        return [a for a in self.ansatte.values() if a.id != vakt.satt_opp_ansatt_id]


@pytest.fixture
def data(session: Session) -> Data:
    (turnus,) = session.scalars(select(TurnusRad)).all()
    ansatte = {a.id: a for a in session.scalars(select(AnsattRad))}
    vakter = list(session.scalars(select(VaktRad).order_by(VaktRad.start)))
    return Data(turnus, ansatte, vakter)


def tid(*args: int) -> datetime:
    return datetime(*args, tzinfo=OSLO)


# --- Hjelpefunksjonene selv ------------------------------------------------


def iv(start: datetime, slutt: datetime) -> Intervall:
    return Intervall(start.astimezone(UTC), slutt.astimezone(UTC))


def test_vakter_som_moetes_i_et_skift_overlapper_ikke() -> None:
    assert not overlapper(iv(tid(2026, 9, 27, 7), tid(2026, 9, 27, 15)), iv(tid(2026, 9, 27, 15), tid(2026, 9, 27, 23)))
    assert overlapper(iv(tid(2026, 9, 27, 7), tid(2026, 9, 27, 15)), iv(tid(2026, 9, 27, 14, 59), tid(2026, 9, 27, 23)))


def test_elleve_timer_godtar_noyaktig_elleve_timer_hvile() -> None:
    maal = iv(tid(2026, 9, 28, 10), tid(2026, 9, 28, 18))
    assert not bryter_elleve_timer([iv(tid(2026, 9, 27, 15), tid(2026, 9, 27, 23))], maal)
    assert bryter_elleve_timer([iv(tid(2026, 9, 27, 15, 1), tid(2026, 9, 27, 23, 1))], maal)


def test_ulempepoeng_per_vakt_og_vindusgrense() -> None:
    def poeng(dato: date, vakttype: str) -> float:
        fra, til = VAKTTIDER[vakttype]
        start = datetime.combine(dato, fra, tzinfo=OSLO)
        slutt = datetime.combine(dato + timedelta(days=til <= fra), til, tzinfo=OSLO)
        return ulempepoeng([iv(start, slutt)], tid(2026, 10, 5, 0))

    hverdag, fredag, lordag, sondag = date(2026, 9, 23), date(2026, 9, 25), date(2026, 9, 26), date(2026, 9, 27)
    assert [poeng(hverdag, t) for t in VAKTTIDER] == [0, 0, 7, 21]
    assert [poeng(lordag, t) for t in VAKTTIDER] == [16, 16, 17, 23]
    assert poeng(fredag, "natt") == 23
    assert poeng(sondag, "natt") == 21
    # En vakt som krysser vindusgrensen, telles bare med delen innenfor.
    natt = [iv(tid(2026, 9, 23, 23), tid(2026, 9, 24, 7))]
    assert ulempepoeng(natt, tid(2026, 10, 22, 2)) == 12  # vindu fra 24.09 02:00
    assert ulempepoeng(natt, tid(2026, 9, 24, 1, 30)) == 7.5  # vakten pågår ved start


# --- Første og ny kjøring ----------------------------------------------------


def test_forste_kjoring_lager_bare_de_tre_tabellene(engine: Engine, data: Data) -> None:
    assert sorted(inspect(engine).get_table_names()) == ["ansatt", "turnus", "vakt"]
    assert len(data.ansatte) == 25
    assert sorted(data.ansatte) == list(range(1, 26))
    periode = [v for v in data.vakter if data.turnus.periode_start <= v.start < data.turnus.periode_slutt]
    startdager = {v.start.date() for v in periode}
    assert startdager == {date(2026, 9, 21) + timedelta(days=i) for i in range(14)}


def test_ny_kjoring_gir_samme_radtall_og_ingen_duplikater(engine: Engine) -> None:
    def tell() -> tuple[int, int, int, list[int]]:
        with lag_sessionmaker(engine)() as s:
            return (
                s.scalar(select(func.count()).select_from(TurnusRad)),
                s.scalar(select(func.count()).select_from(AnsattRad)),
                s.scalar(select(func.count()).select_from(VaktRad)),
                sorted(s.scalars(select(VaktRad.vaktnummer))),
            )

    foer = tell()
    with lag_sessionmaker(engine).begin() as session:
        radtall = fyll_testdata(session)
    etter = tell()
    assert foer == etter
    assert radtall == {"turnus": foer[0], "ansatt": foer[1], "vakt": foer[2]}
    assert len(set(etter[3])) == len(etter[3])


def test_kommandoen_kan_kjores_to_ganger_mot_databasen_i_miljovariabelen(tmp_path: Path) -> None:
    db = tmp_path / "kommando.db"
    miljo = {**os.environ, MILJOVARIABEL: str(db), "PYTHONUTF8": "1"}
    kjoringer = [
        subprocess.run(
            [sys.executable, "-m", "adaptere.lagring.testdata"],
            cwd=BACKEND, env=miljo, capture_output=True, text=True, check=True,
        ).stdout
        for _ in range(2)
    ]
    assert kjoringer[0] == kjoringer[1]
    assert "ansatt: 25" in kjoringer[0]
    engine = lag_engine(db)
    try:
        with lag_sessionmaker(engine)() as s:
            assert s.scalar(select(func.count()).select_from(TurnusRad)) == 1
            assert s.scalar(select(func.count()).select_from(AnsattRad)) == 25
            assert s.scalar(select(func.count()).select_from(VaktRad)) == len(HISTORIKK) + len(PERIODE)
    finally:
        engine.dispose()


def test_databasestien(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(MILJOVARIABEL, raising=False)
    assert database_sti() == STANDARD_STI == BACKEND / "turnushjelperen.db"
    monkeypatch.setenv(MILJOVARIABEL, "")
    assert database_sti() == STANDARD_STI
    monkeypatch.setenv(MILJOVARIABEL, "data/relativ.db")
    assert database_sti() == (tmp_path / "data" / "relativ.db").resolve()
    assert database_sti(tmp_path / "argument.db") == (tmp_path / "argument.db").resolve()


# --- Turnus og de to scenarioene ---------------------------------------------


def test_turnusen(data: Data) -> None:
    assert data.turnus.avdeling == "Kirurgisk sengepost"
    assert data.turnus.periode_start == tid(2026, 9, 21, 0)
    assert data.turnus.periode_slutt == tid(2026, 10, 5, 0)
    assert data.turnus.sist_oppdatert == tid(2026, 9, 27, 6, 20)
    assert "Kari Vestby" not in {a.navn for a in data.ansatte.values()}


def test_4127_mangler_bemanning_etter_silje(data: Data) -> None:
    vakt = data.vakt(4127)
    assert (vakt.vakttype, vakt.start, vakt.slutt) == ("dag", tid(2026, 9, 27, 7), tid(2026, 9, 27, 15))
    assert vakt.start.weekday() == 6  # søndag
    assert vakt.minstenivå == 3
    assert vakt.mangler_bemanning and vakt.tildelt_ansatt_id is None
    assert data.ansatte[vakt.satt_opp_ansatt_id].navn == "Silje Amundsen"
    assert (vakt.meldt_fra, vakt.meldt_fra_grunn) == (tid(2026, 9, 27, 6, 14), "sykemeldt")
    utfall = FASIT[4127]["utfall"]
    assert Counter(utfall.values()) == {
        "gyldig": 4, "kolliderende": 7, "elleve-timer": 4, "kompetanse": 8, "trettifem-timer": 1,
    }


def test_4189_mangler_bemanning_etter_eirik(data: Data) -> None:
    vakt = data.vakt(4189)
    assert (vakt.vakttype, vakt.start, vakt.slutt) == ("natt", tid(2026, 9, 28, 23), tid(2026, 9, 29, 7))
    assert vakt.minstenivå == 3
    assert vakt.mangler_bemanning and vakt.tildelt_ansatt_id is None
    assert data.ansatte[vakt.satt_opp_ansatt_id].navn == "Eirik Moen"
    assert (vakt.meldt_fra, vakt.meldt_fra_grunn) == (tid(2026, 9, 26, 21, 40), "sykemeldt")
    utfall = FASIT[4189]["utfall"]
    assert Counter(utfall.values()) == {
        "kolliderende": 2, "elleve-timer": 18, "kompetanse": 3, "trettifem-timer": 1,
    }
    assert utfall["Silje Amundsen"] == "kompetanse"
    assert "natt" not in data.ansatt("Silje Amundsen").kompetanse


def test_bare_4127_og_4189_mangler_bemanning(data: Data) -> None:
    assert sorted(v.vaktnummer for v in data.vakter if v.mangler_bemanning) == [4127, 4189]
    for v in data.vakter:
        if not v.mangler_bemanning:
            assert v.satt_opp_ansatt_id is None and v.meldt_fra is None and v.meldt_fra_grunn is None


@pytest.mark.parametrize("vaktnummer", [4127, 4189])
def test_fasiten_stemmer_med_reglene(data: Data, vaktnummer: int) -> None:
    vakt = data.vakt(vaktnummer)
    utfall = FASIT[vaktnummer]["utfall"]
    assert set(utfall) == {a.navn for a in data.kandidater(vakt)}
    assert len(utfall) == 24
    for ansatt in data.kandidater(vakt):
        forventet = set() if utfall[ansatt.navn] == "gyldig" else {utfall[ansatt.navn]}
        assert brudd(ansatt, data.egne(ansatt.id), vakt) == forventet, ansatt.navn


def test_mockupens_vakter_beholder_nummer_ansatt_og_dato(data: Data) -> None:
    forventet = {
        4128: ("kveld", date(2026, 9, 27), "Per Halvorsen"),
        4130: ("dag", date(2026, 9, 28), "Mette Solberg"),
        4131: ("natt", date(2026, 9, 28), "Thomas Nygård"),
        4135: ("dag", date(2026, 9, 29), "Jonas Bakke"),
        4136: ("kveld", date(2026, 9, 29), "Ingrid Dahl"),
    }
    for nummer, (vakttype, dato, navn) in forventet.items():
        vakt = data.vakt(nummer)
        assert (vakt.vakttype, vakt.start.date(), data.ansatte[vakt.tildelt_ansatt_id].navn) == (vakttype, dato, navn)
    ansiennitet = {"Per Halvorsen": 4, "Mette Solberg": 9, "Thomas Nygård": 1, "Jonas Bakke": 3, "Ingrid Dahl": 6}
    for navn, aar in ansiennitet.items():
        assert data.ansatt(navn).ansiennitet == aar


# --- Kostnad, belastning og rangeringsfasit ----------------------------------


def gyldige_4127(data: Data) -> list[AnsattRad]:
    return [data.ansatt(n) for n, u in FASIT[4127]["utfall"].items() if u == "gyldig"]


def test_minst_tre_gyldige_og_en_gir_overtid_paa_4127(data: Data) -> None:
    vakt = data.vakt(4127)
    gyldige = gyldige_4127(data)
    assert len(gyldige) >= 3
    uke = kalenderuke(intervall(vakt).start)
    assert any(timer_i_uka(data.egne(a.id), uke) + 8 > 36 for a in gyldige)


def test_billigste_gyldige_er_ikke_best_paa_belastning_og_preferanse(data: Data) -> None:
    uke = kalenderuke(intervall(data.vakt(4127)).start)
    gyldige = gyldige_4127(data)

    def pris(a: AnsattRad) -> float:
        return kostnad(a.timelønn, timer_i_uka(data.egne(a.id), uke))

    def belastning(a: AnsattRad) -> float:
        return ulempepoeng(data.egne(a.id), data.vakt(4127).start)

    def preferanse(a: AnsattRad) -> int:
        return PREFERANSEPOENG.get(a.preferanse, 50)

    billigste = min(gyldige, key=pris)
    assert sum(pris(a) == pris(billigste) for a in gyldige) == 1
    assert belastning(billigste) == max(map(belastning, gyldige)) or preferanse(billigste) == min(
        map(preferanse, gyldige)
    )


def test_rangeringsfasiten_bygger_paa_dataene(data: Data) -> None:
    vakt = data.vakt(4127)
    uke = kalenderuke(intervall(vakt).start)
    rangering = FASIT[4127]["rangering"]
    assert {r["navn"] for r in rangering} == {a.navn for a in gyldige_4127(data)}
    for rad in rangering:
        ansatt = data.ansatt(rad["navn"])
        egne = data.egne(ansatt.id)
        timer_uke = timer_i_uka(egne, uke)
        assert ansatt.timelønn == rad["timelønn"], rad["navn"]
        assert timer_uke == rad["timer_uke"], rad["navn"]
        assert PREFERANSEPOENG[ansatt.preferanse] == rad["preferansepoeng"], rad["navn"]
        assert ulempepoeng(egne, vakt.start) == rad["ulempepoeng"], rad["navn"]
        assert kostnad(ansatt.timelønn, timer_uke) == rad["kostnad"], rad["navn"]
    totalscore = [r["totalscore"] for r in rangering]
    assert totalscore == sorted(totalscore, reverse=True)


def test_rangeringsfasiten_er_regnet_riktig_fra_inputene() -> None:
    """Kontroll av aritmetikken i FASIT, ikke en test av rangeringen (story 4.4)."""
    rangering = FASIT[4127]["rangering"]

    def min_maks(verdi: float, alle: list[float]) -> float:
        lav, hoy = min(alle), max(alle)
        return 50.0 if lav == hoy else 100 * (hoy - verdi) / (hoy - lav)

    kostnader = [r["kostnad"] for r in rangering]
    timer_uke = [r["timer_uke"] for r in rangering]
    for r in rangering:
        total = (
            0.40 * min_maks(r["kostnad"], kostnader)
            + 0.20 * min_maks(r["timer_uke"], timer_uke)
            + 0.15 * max(0.0, 100 * (1 - r["ulempepoeng"] / 300))
            + 0.25 * r["preferansepoeng"]
        )
        assert total == pytest.approx(r["totalscore"], abs=1e-9), r["navn"]
    jonas, mette = rangering[0], rangering[1]
    assert jonas["totalscore"] - mette["totalscore"] == pytest.approx(7.0)


def test_ulempescenario_jonas_og_mette(data: Data) -> None:
    vakt = data.vakt(4127)
    uke = kalenderuke(intervall(vakt).start)
    jonas, mette = data.ansatt("Jonas Bakke"), data.ansatt("Mette Solberg")
    assert jonas.timelønn == mette.timelønn == 370
    assert timer_i_uka(data.egne(jonas.id), uke) == timer_i_uka(data.egne(mette.id), uke) == 16
    assert PREFERANSEPOENG[jonas.preferanse] == PREFERANSEPOENG[mette.preferanse] == 75
    assert ulempepoeng(data.egne(jonas.id), vakt.start) == 40
    assert ulempepoeng(data.egne(mette.id), vakt.start) == 180


def test_ulempespredning_i_vinduet_til_4127(data: Data) -> None:
    start = data.vakt(4127).start
    assert timer(start - timedelta(hours=672), start) == 672
    assert (start - timedelta(hours=672)) == tid(2026, 8, 30, 7)
    poeng = [ulempepoeng(data.egne(a.id), start) for a in data.ansatte.values()]
    assert min(poeng) <= 10
    assert max(poeng) > 250


# --- Ansatte, tid og historikk -----------------------------------------------


def test_ansattfeltene(data: Data) -> None:
    for a in data.ansatte.values():
        assert a.navn.strip()
        assert a.stilling in {"Sykepleier", "Spesialsykepleier", "Helsefagarbeider"}
        assert a.ansiennitet >= 0
        assert 350 <= a.timelønn <= 420
        assert a.kompetanse and set(a.kompetanse) <= {"dag", "kveld", "natt"}
        assert all(nivaa in (1, 2, 3, 4) for nivaa in a.kompetanse.values())
        assert a.preferanse is None or a.preferanse in PREFERANSEPOENG
    assert any(a.preferanse is None for a in data.ansatte.values())
    assert any(a.preferanse is not None for a in data.ansatte.values())


def test_tildelte_ansatte_har_kompetansen_vakten_krever(data: Data) -> None:
    for v in data.vakter:
        if v.tildelt_ansatt_id is not None:
            assert not bryter_kompetanse(data.ansatte[v.tildelt_ansatt_id], v), v.vaktnummer


def test_tidspunkt_leses_tilbake_i_europe_oslo(engine: Engine, data: Data) -> None:
    for v in data.vakter:
        for t in (v.start, v.slutt):
            assert isinstance(t.tzinfo, ZoneInfo) and t.tzinfo.key == "Europe/Oslo"
        fra, til = VAKTTIDER[v.vakttype]
        assert (v.start.time(), v.slutt.time()) == (fra, til), v.vaktnummer
        assert timer(v.start, v.slutt) == 8
    with engine.connect() as tilkobling:
        lagret = tilkobling.execute(text("SELECT start FROM vakt WHERE vaktnummer = 4127")).scalar_one()
    assert lagret == "2026-09-27T05:00:00+00:00"


def test_naiv_datetime_avvises(session: Session) -> None:
    session.add(
        TurnusRad(
            avdeling="Naiv",
            periode_start=datetime(2026, 9, 21),
            periode_slutt=tid(2026, 10, 5, 0),
            sist_oppdatert=tid(2026, 9, 27, 6, 20),
        )
    )
    with pytest.raises(StatementError, match="naiv"):
        session.flush()


def gyldig_vakt(**endringer: object) -> VaktRad:
    felt = dict(
        turnus_id=1, vaktnummer=9999, vakttype="dag", start=tid(2026, 10, 6, 7),
        slutt=tid(2026, 10, 6, 15), minstenivå=2, tildelt_ansatt_id=1, mangler_bemanning=False,
    )
    return VaktRad(**{**felt, **endringer})


@pytest.mark.parametrize(
    "endringer",
    [
        {"tildelt_ansatt_id": 999},  # fremmednøkkel
        {"mangler_bemanning": True},  # tildelt og mangler bemanning samtidig
        {"vakttype": "helg"},
        {"minstenivå": 5},
    ],
)
def test_databasen_avviser_ugyldige_vakter(session: Session, endringer: dict) -> None:
    session.add(gyldig_vakt(**endringer))
    with pytest.raises(IntegrityError):
        session.flush()


def test_gyldig_kontrollvakt_godtas(session: Session) -> None:
    session.add(gyldig_vakt())
    session.flush()


def test_oslotid_avviser_annet_enn_datetime(session: Session) -> None:
    session.add(gyldig_vakt(start="2026-10-06T07:00:00+02:00"))
    with pytest.raises(StatementError, match="krever datetime"):
        session.flush()


def test_historikken(data: Data) -> None:
    historikk = [v for v in data.vakter if v.start < data.turnus.periode_start]
    periode = [v for v in data.vakter if data.turnus.periode_start <= v.start < data.turnus.periode_slutt]
    assert len(historikk) + len(periode) == len(data.vakter)
    assert all(3000 <= v.vaktnummer <= 3999 for v in historikk)
    assert all(4100 <= v.vaktnummer <= 4299 for v in periode)
    assert all(not v.mangler_bemanning and v.tildelt_ansatt_id for v in historikk)
    assert min(v.start for v in historikk) >= tid(2026, 8, 24, 0)
    forste_uke = Intervall(tid(2026, 8, 24, 0).astimezone(UTC), tid(2026, 8, 31, 0).astimezone(UTC))
    for a in data.ansatte.values():
        egne = [intervall(v) for v in historikk if v.tildelt_ansatt_id == a.id]
        assert egne and min(v.start for v in egne) < forste_uke.slutt, a.navn


@pytest.mark.parametrize("vaktnummer", [4127, 4189])
def test_datadekning_ved_periodegrensene_ks04(data: Data, vaktnummer: int) -> None:
    """KS-04: dataene dekker ulempevinduet, nabovaktene og hele kalenderuka
    for vaktene som skal bemannes. Dataene går fra 24.08 til periodeslutt."""
    data_fra = tid(2026, 8, 24, 0).astimezone(UTC)
    data_til = data.turnus.periode_slutt.astimezone(UTC)
    maal = intervall(data.vakt(vaktnummer))
    assert data_fra <= maal.start - timedelta(hours=672)
    assert data_fra <= maal.start - timedelta(hours=11)
    assert maal.slutt + timedelta(hours=11) <= data_til
    for uke in berorte_uker(maal):
        assert data_fra <= uke.start and uke.slutt <= data_til
    startdager = {v.start.date() for v in data.vakter}
    forste = date(2026, 8, 24)
    assert startdager == {forste + timedelta(days=i) for i in range(42)}


def test_ingen_ansatt_bryter_reglene_i_egen_turnus(data: Data) -> None:
    """Alle tildelte Vakter, også historikken: ingen overlapp, minst 11 t hvile
    mellom vaktene og minst 35 t sammenhengende fri i hver kalenderuke."""
    for a in data.ansatte.values():
        egne = data.egne(a.id)
        for forrige, neste in zip(egne, egne[1:]):
            assert not overlapper(forrige, neste), a.navn
            assert timer(forrige.slutt, neste.start) >= 11, (a.navn, neste.start)
        uker = {uke for v in egne for uke in berorte_uker(v)}
        for uke in uker:
            assert lengste_fri(egne, uke) >= 35, (a.navn, uke.start)
