"""Kjøretidstest av lekkasjeinvarianten (NFR2, SM-2, AD-1, AD-2, story 5.6).

Den statiske delen av grensen er import-linter-kontrakten i `tester/test_arkitektur.py`.
Denne modulen viser oppførselen ved kjøring: gjennom hele API-flyten for vakt #4127, som
har utelukkelser etter alle fire harde regler, når ingen utelukket kandidat-ID eller
utelukket navn forklaringsporten, og ingen utelukket Kandidat står i kandidatradene,
godkjenningsgrunnlaget eller avveiningssvarene. Ekskludert-boksen (`utelukkelser`)
skal derimot vise dem (story 2.5).

Adapteren er ekte `OpenRouterKiAdapter` med en falsk transport som registrerer hver
forespørsel. `response_format.json_schema.name` skiller forklaringsporten (`avveining`)
fra tolkingsporten (`preferanse`). Tolkingsporten får tekst før filtreringen og har lov
til det (AD-2), men bare med `tekst`, uten kandidat-ID eller vaktstatus.

I tillegg registreres hvert kall på selve porten (`forklar` og `tolk`), slik at
`DemoKiAdapter` fra story 5.7 kan legges til i `ADAPTERFABRIKKER` uten at testen skrives
om (AD-6). Den negative kontrollen viser at kontrollene feiler når en utelukket
Kandidat slipper gjennom regelmotoren. Ingen test bruker nettverk, nøkkel eller faktisk
venting.
"""

import json
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from adaptere.api import main
from adaptere.api.main import lag_app
from adaptere.ki.openrouter import PROMPT, URL, HttpSvar, OpenRouterKiAdapter, Tolkefeil
from adaptere.lagring.testdata import ANSATTE, FASIT, PREFERANSER
from domene.porter.rangering import RangertKandidat, TolketPreferanse
from domene.regelmotor.ulempebelastning import beregn_ulempebelastning
from domene.typer import Datafeil
from tester.api.test_innlogging import NOKKEL, engine, logg_inn  # noqa: F401
from tester.api.test_kandidater import ID_VED_NAVN, KOMPETANSE, UTFALL_TIL_ÅRSAK
from tester.ki.test_openrouter import FalskKlokke, innhold

VAKT = 4127
LISTE = f"/api/vakter/{VAKT}/kandidater"
UKJENT = 987654

UTFALL = FASIT[VAKT]["utfall"]
UTELUKKEDE: dict[int, str] = {ID_VED_NAVN[n]: n for n, u in UTFALL.items() if u != "gyldig"}
GYLDIGE: dict[int, str] = {ID_VED_NAVN[n]: n for n, u in UTFALL.items() if u == "gyldig"}
# Én utelukket per hard regel, til den negative kontrollen. Den må ha et nivå for
# vakttypen (dag), ellers stopper Rangeringen selv med ValueError før noe lekker.
ÉN_PER_REGEL = {u: next(ID_VED_NAVN[n] for n, v in UTFALL.items() if v == u and "dag" in KOMPETANSE[n])
                for u in UTFALL_TIL_ÅRSAK}
PREFERANSE_VED_ID = {ansatt_id: PREFERANSER[nr][0] for ansatt_id, *_, nr in ANSATTE if nr is not None}


# --- Registrering på porten og på transporten --------------------------------------


class RegistrerendeTransport:
    """Lagrer hver forespørsel og svarer gyldig på begge porter.

    `avveiningssvar` lager modellens svar fra brukerinnholdet. Standard er alle
    tillatte påstander uendret, som alltid består faktakontrollen.
    """

    def __init__(self, avveiningssvar: Callable[[dict], dict] | None = None) -> None:
        self.forespørsler: list[dict] = []
        self.avveiningssvar = avveiningssvar or (lambda data: {"paastander": data["tillatte"]})

    def __call__(self, url: str, kropp: bytes, _headere: object, _tidsavbrudd: float) -> HttpSvar:
        assert url == URL
        forespørsel = json.loads(kropp)
        self.forespørsler.append(forespørsel)
        data = json.loads(forespørsel["messages"][1]["content"])
        if port(forespørsel) == "preferanse":
            return HttpSvar(200, {}, innhold({"kategori": "noytral", "begrunnelse": "Ingen tydelig holdning."}))
        assert port(forespørsel) == "avveining"
        return HttpSvar(200, {}, innhold(self.avveiningssvar(data)))

    def til(self, navn: str) -> list[dict]:
        return [f for f in self.forespørsler if port(f) == navn]


def port(forespørsel: dict) -> str:
    return forespørsel["response_format"]["json_schema"]["name"]


class RegistrerendePort:
    """Samme porter som adapteren den pakker inn, og registrerer hvert kall."""

    def __init__(self, ki: OpenRouterKiAdapter) -> None:
        self._ki = ki
        self.modell = ki.modell
        self.forklaringer: list[tuple[RangertKandidat, RangertKandidat | None]] = []
        self.tolkninger: list[str] = []

    def tolk(self, tekst: str) -> TolketPreferanse | Tolkefeil:
        self.tolkninger.append(tekst)
        return self._ki.tolk(tekst)

    def forklar(self, kandidat: RangertKandidat, referanse: RangertKandidat | None) -> list[str] | None:
        self.forklaringer.append((kandidat, referanse))
        return self._ki.forklar(kandidat, referanse)


def openrouter(transport: RegistrerendeTransport) -> OpenRouterKiAdapter:
    # Falsk klokke: begrenseren (18 per minutt) venter uten faktisk søvn.
    klokke = FalskKlokke()
    return OpenRouterKiAdapter("test", transport=transport, klokke=klokke, sov=klokke.sov, veggklokke=klokke.vegg)


# Story 5.7 legger til `pytest.param(demo, id="demo")` her (AD-6). Fabrikken får
# transporten og kan la være å bruke den. Kontrollene på porten gjelder da som før.
ADAPTERFABRIKKER = [pytest.param(openrouter, id="openrouter")]


# --- Flyten ------------------------------------------------------------------------


@dataclass
class Flyt:
    liste: dict
    grunnlag: dict[int, dict] = field(default_factory=dict)
    avveininger: dict[int, dict] = field(default_factory=dict)
    # Utelukket ID -> (statuskode og kropp for avveining, for godkjenningsgrunnlag).
    direkte: dict[int, tuple[tuple[int, dict], tuple[int, dict]]] = field(default_factory=dict)
    ukjent: tuple[tuple[int, dict], tuple[int, dict]] | None = None
    # Forklaringskall (porten, transporten) etter liste og godkjenningsgrunnlag,
    # og etter direkte oppslag på utelukkede.
    kall_etter_beregning: tuple[int, int] = (0, 0)
    kall_etter_direkte: tuple[int, int] = (0, 0)
    ki: "RegistrerendePort | None" = None
    transport: "RegistrerendeTransport | None" = None


def svar(klient: TestClient, sti: str) -> tuple[int, dict]:
    respons = klient.get(sti)
    return respons.status_code, respons.json()


def kjør_flyt(fabrikk: Callable, engine: Engine) -> Flyt:
    """Hele flyten gjennom API-et. Samler svarene og kontrollerer ingenting selv."""
    transport = RegistrerendeTransport()
    ki = RegistrerendePort(fabrikk(transport))
    app = lag_app(nokkel=NOKKEL, engine=engine, ki=ki)
    with TestClient(app) as klient:
        # Bakgrunnstolkningen ved oppstart, også av tekster fra senere utelukkede.
        app.state.tolketråd.join(timeout=30)
        assert not app.state.tolketråd.is_alive()
        logg_inn(klient)

        def kall() -> tuple[int, int]:
            return len(ki.forklaringer), len(transport.til("avveining"))

        liste = klient.get(LISTE).json()
        flyt = Flyt(liste=liste, ki=ki, transport=transport)
        for rad in liste["kandidater"]:
            flyt.grunnlag[rad["id"]] = klient.get(f"{LISTE}/{rad['id']}").json()
        flyt.kall_etter_beregning = kall()
        for id in UTELUKKEDE:
            flyt.direkte[id] = (svar(klient, f"{LISTE}/{id}/avveining"), svar(klient, f"{LISTE}/{id}"))
        flyt.ukjent = (svar(klient, f"{LISTE}/{UKJENT}/avveining"), svar(klient, f"{LISTE}/{UKJENT}"))
        flyt.kall_etter_direkte = kall()
        for rad in liste["kandidater"]:
            flyt.avveininger[rad["id"]] = klient.get(f"{LISTE}/{rad['id']}/avveining").json()
    return flyt


# --- Kontrollene -------------------------------------------------------------------


def strenger(verdi: object) -> Iterator[str]:
    if isinstance(verdi, str):
        yield verdi
    elif isinstance(verdi, dict):
        for k, v in verdi.items():
            yield from strenger(k)
            yield from strenger(v)
    elif isinstance(verdi, list | tuple):
        for v in verdi:
            yield from strenger(v)


def kandidat_ider(verdi: object, nøkler: tuple[str, ...] = ("kandidat_id", "referanse_id")) -> Iterator[int]:
    """Alle verdier under `nøkler`, uansett hvor dypt de ligger."""
    if isinstance(verdi, dict):
        for k, v in verdi.items():
            if k in nøkler:
                yield v
            yield from kandidat_ider(v, nøkler)
    elif isinstance(verdi, list):
        for v in verdi:
            yield from kandidat_ider(v, nøkler)


def nevner_utelukket(verdi: object) -> set[str]:
    return {navn for s in strenger(verdi) for navn in UTELUKKEDE.values() if navn in s}


def kontroller_forklaringsporten(flyt: Flyt) -> None:
    """Ingen utelukket Kandidat i kallene på `forklar`, verken som kandidat eller referanse."""
    assert flyt.ki is not None
    assert flyt.ki.forklaringer, "flyten ga ingen forklaringskall, så kontrollen beviser ingenting"
    for kandidat, referanse in flyt.ki.forklaringer:
        assert kandidat.id not in UTELUKKEDE and kandidat.navn not in UTELUKKEDE.values()
        if referanse is not None:
            assert referanse.id not in UTELUKKEDE and referanse.navn not in UTELUKKEDE.values()


def kontroller_forklaringsforespørslene(flyt: Flyt) -> None:
    """Ingen utelukket ID eller navn i det som faktisk sendes til modellen.

    En adapter uten HTTP (demo, story 5.7) sender ingen forespørsler, og da dekker
    `kontroller_forklaringsporten` grensen alene.
    """
    assert flyt.transport is not None
    for forespørsel in flyt.transport.til("avveining"):
        data = json.loads(forespørsel["messages"][1]["content"])
        ider = set(kandidat_ider(data))
        assert ider and not ider & UTELUKKEDE.keys(), \
            f"utelukket ID i forklaringsforespørselen: {ider & UTELUKKEDE.keys()}"
        assert not nevner_utelukket(forespørsel)


def kontroller_api_svar(flyt: Flyt) -> None:
    """Kandidatrader, godkjenningsgrunnlag og avveiningssvar har bare Gyldige kandidater."""
    rader = flyt.liste["kandidater"]
    assert rader and {r["id"] for r in rader} <= GYLDIGE.keys()
    assert {r["navn"] for r in rader} <= set(GYLDIGE.values())
    # Hele listesvaret unntatt Ekskludert-boksen, så også et nytt toppfelt fanges.
    uten_boks = {k: v for k, v in flyt.liste.items() if k != "utelukkelser"}
    assert not nevner_utelukket(uten_boks)
    assert not set(kandidat_ider(uten_boks, ("id", "kandidat_id", "referanse_id"))) & UTELUKKEDE.keys()
    for id, grunnlag in flyt.grunnlag.items():
        assert grunnlag["status"] == "ok" and grunnlag["kandidat"]["id"] == id and id in GYLDIGE
        if grunnlag["topprangert"] is not None:
            assert grunnlag["topprangert"]["id"] in GYLDIGE
        assert not nevner_utelukket(grunnlag)
    assert flyt.avveininger
    for id, avv in flyt.avveininger.items():
        assert avv["kandidat_id"] == id and id in GYLDIGE
        assert not nevner_utelukket(avv)


def kontroller_direkte_oppslag(flyt: Flyt) -> None:
    """Hver utelukket gir det samme 404-svaret som en ukjent ID, og ingen forklaringskall."""
    assert flyt.ukjent is not None and flyt.ukjent[0] == flyt.ukjent[1]
    assert flyt.ukjent[0][0] == 404 and flyt.ukjent[0][1]["kode"] == "ikke_funnet"
    assert flyt.direkte.keys() == UTELUKKEDE.keys()
    for avv, grunnlag in flyt.direkte.values():
        assert avv == flyt.ukjent[0] and grunnlag == flyt.ukjent[1]
    assert flyt.kall_etter_direkte == flyt.kall_etter_beregning


INVARIANTKONTROLLER = [kontroller_forklaringsporten, kontroller_forklaringsforespørslene,
                       kontroller_api_svar, kontroller_direkte_oppslag]


# --- Testene -----------------------------------------------------------------------


def test_fasiten_for_4127_har_utelukkelser_etter_alle_fire_regler() -> None:
    # Mister testdataene en regel, beviser flyttesten ikke lenger grensen for den.
    antall = Counter(UTFALL.values())
    assert set(UTFALL_TIL_ÅRSAK) <= antall.keys()
    assert all(antall[regel] >= 1 for regel in UTFALL_TIL_ÅRSAK)
    assert len(GYLDIGE) >= 2 and len(UTELUKKEDE) == len(UTFALL) - len(GYLDIGE)
    # Minst én utelukket har en preferansetekst, så tolkingsporten får tekst før filtreringen.
    assert UTELUKKEDE.keys() & PREFERANSE_VED_ID.keys()


@pytest.mark.parametrize("fabrikk", ADAPTERFABRIKKER)
def test_utelukkede_når_aldri_forklaringsporten_gjennom_hele_flyten(fabrikk: Callable, engine: Engine) -> None:
    flyt = kjør_flyt(fabrikk, engine)

    # Ekskludert-boksen viser alle utelukkede med navn og årsak (story 2.5).
    boks = flyt.liste["utelukkelser"]
    assert {(u["id"], u["navn"]) for u in boks["utelukkede"]} == set(UTELUKKEDE.items())
    for u in boks["utelukkede"]:
        assert u["årsaker"] == [UTFALL_TIL_ÅRSAK[UTFALL[u["navn"]]]]
    per_regel = Counter(UTFALL.values())
    assert {r["årsak"]: r["antall"] for r in boks["per_regel"]} == {
        årsak: per_regel[utfall] for utfall, årsak in UTFALL_TIL_ÅRSAK.items()
    }

    # Liste og godkjenningsgrunnlag beregnes uten ett eneste forklaringskall.
    assert flyt.kall_etter_beregning == (0, 0)
    for kontroll in INVARIANTKONTROLLER:
        kontroll(flyt)
    assert all(a["status"] == "ok" for a in flyt.avveininger.values())
    assert flyt.ki is not None and {k.id for k, _ in flyt.ki.forklaringer} == GYLDIGE.keys()
    if fabrikk is openrouter:
        assert flyt.transport is not None and len(flyt.transport.til("avveining")) == len(GYLDIGE)


@pytest.mark.parametrize("fabrikk", ADAPTERFABRIKKER)
def test_tolkingsporten_får_bare_tekst_også_fra_senere_utelukkede(fabrikk: Callable, engine: Engine) -> None:
    flyt = kjør_flyt(fabrikk, engine)
    ki, transport = flyt.ki, flyt.transport
    assert ki is not None and transport is not None
    # Tillatt etter AD-2: tolkingen skjer før filtreringen.
    assert set(ki.tolkninger) >= {PREFERANSE_VED_ID[i] for i in UTELUKKEDE.keys() & PREFERANSE_VED_ID.keys()}
    for forespørsel in transport.til("preferanse"):
        assert forespørsel["messages"][0]["content"] == PROMPT
        data = json.loads(forespørsel["messages"][1]["content"])
        assert set(data) == {"tekst"} and isinstance(data["tekst"], str)
        assert not list(kandidat_ider(forespørsel))
        # Ingen vaktstatus eller kandidatfelt i brukermeldingen. Systemprompten er dekket over.
        kropp = json.dumps(forespørsel["messages"][1:], ensure_ascii=False)
        for forbudt in ("kandidat", "utelukk", "gyldig", "vaktnummer", str(VAKT)):
            assert forbudt not in kropp


@pytest.mark.parametrize("felt", ["kandidat_id", "referanse_id"])
def test_svar_som_peker_på_utelukket_forkastes_uten_navn(felt: str, engine: Engine) -> None:
    # Første svar er positiv kontroll med den gyldige ID-en, deretter én utelukket per svar.
    erstatninger = iter([None, *UTELUKKEDE])
    brukt: list[int] = []

    def modell(data: dict) -> dict:
        # Første påstand med feltet, med en utelukket ID i stedet for den gyldige.
        påstand = dict(next(p for p in data["tillatte"] if felt in p))
        erstatning = next(erstatninger)
        if erstatning is not None:
            påstand[felt] = erstatning
            brukt.append(erstatning)
        myk = [p for p in data["tillatte"] if p["type"] == "egen" or p.get("faktor") == "preferanse"]
        return {"paastander": [påstand, *myk]}

    transport = RegistrerendeTransport(modell)
    klient = TestClient(lag_app(nokkel=NOKKEL, engine=engine, ki=openrouter(transport)))
    logg_inn(klient)
    rader = klient.get(LISTE).json()["kandidater"]
    rad = rader[0]
    # Samme svarform med gyldig ID består, så avvisningen under skyldes den utelukkede ID-en.
    positiv = klient.get(f"{LISTE}/{rad['id']}/avveining")
    assert positiv.status_code == 200 and positiv.json()["status"] == "ok"
    for _ in UTELUKKEDE:
        avv = klient.get(f"{LISTE}/{rad['id']}/avveining")
        assert avv.status_code == 200
        assert avv.json() == {"status": "avveining_feilet", "vaktnummer": VAKT, "kandidat_id": rad["id"],
                              "grunnlagsmerke": rad["grunnlagsmerke"]}
        assert not nevner_utelukket(avv.json())
    assert sorted(brukt) == sorted(UTELUKKEDE)
    # Det er modellsvaret som pekte på dem, ikke forespørselen.
    for forespørsel in transport.til("avveining"):
        assert not set(kandidat_ider(json.loads(forespørsel["messages"][1]["content"]))) & UTELUKKEDE.keys()


def lekk(monkeypatch: pytest.MonkeyPatch, lekket_id: int) -> None:
    """Lar regelmotoren regne én utelukket Kandidat som gyldig, med egen Ulempebelastning."""
    ekte = main.vurder_kandidater

    def lekkende(vakt, *args, **kwargs):  # type: ignore[no-untyped-def]
        vurdering = ekte(vakt, *args, **kwargs)
        if isinstance(vurdering, Datafeil):
            return vurdering
        lekket = next(u for u in vurdering.utelukkede if u.kandidat.id == lekket_id)
        return replace(
            vurdering,
            gyldige=(*vurdering.gyldige, lekket.kandidat),
            utelukkede=tuple(u for u in vurdering.utelukkede if u is not lekket),
            ulempe_per_kandidat={**vurdering.ulempe_per_kandidat,
                                 lekket_id: beregn_ulempebelastning(lekket.kandidat, vakt)},
        )

    monkeypatch.setattr(main, "vurder_kandidater", lekkende)


@pytest.mark.parametrize("kontroll", INVARIANTKONTROLLER, ids=lambda k: k.__name__)
@pytest.mark.parametrize("regel", list(ÉN_PER_REGEL))
def test_negativ_kontroll_hver_invariantkontroll_feiler_ved_lekkasje(
    regel: str, kontroll: Callable, engine: Engine, monkeypatch: pytest.MonkeyPatch,
) -> None:
    lekket_id = ÉN_PER_REGEL[regel]
    lekk(monkeypatch, lekket_id)
    flyt = kjør_flyt(openrouter, engine)
    # Lekkasjen er virkelig: den utelukkede står som rad og ble sendt til forklaringsporten.
    assert lekket_id in {r["id"] for r in flyt.liste["kandidater"]}
    assert flyt.ki is not None and lekket_id in {k.id for k, _ in flyt.ki.forklaringer}
    with pytest.raises(AssertionError):
        kontroll(flyt)
