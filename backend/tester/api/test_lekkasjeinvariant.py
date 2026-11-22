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
from copy import copy, deepcopy
from dataclasses import dataclass, field, replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, update

from adaptere.api import main
from adaptere.api.main import lag_app
from adaptere.ki import avveining
from adaptere.ki.openrouter import PROMPT, URL, HttpSvar, OpenRouterKiAdapter, Tolkefeil
from adaptere.ki.openrouter import skjema as preferanseskjema
from adaptere.lagring.database import lag_engine, lag_sessionmaker, opprett_skjema
from adaptere.lagring.modeller import AnsattRad
from adaptere.lagring.testdata import ANSATTE, FASIT, PREFERANSER, fyll_testdata, legg_til_turnusansvarlig
from domene.porter.rangering import RangertKandidat, TolketPreferanse
from domene.regelmotor.ulempebelastning import beregn_ulempebelastning
from domene.typer import Datafeil
from tester.api.test_innlogging import NOKKEL, PASSORD, engine, logg_inn  # noqa: F401
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
                assert type(v) is int, f"{k} må være en heltalls-ID, fikk {v!r}"
                yield v
            yield from kandidat_ider(v, nøkler)
    elif isinstance(verdi, list):
        for v in verdi:
            yield from kandidat_ider(v, nøkler)


def nevner_utelukket(verdi: object) -> set[str]:
    return {navn for s in strenger(verdi) for navn in UTELUKKEDE.values() if navn in s}


def brukerdata(forespørsel: dict, systemtekst: str, portnavn: str, svarskjema: dict) -> dict:
    assert set(forespørsel) == {"model", "max_tokens", "reasoning", "provider", "messages", "response_format"}
    assert forespørsel["response_format"] == {
        "type": "json_schema", "json_schema": {"name": portnavn, "strict": True, "schema": svarskjema},
    }
    meldinger = forespørsel["messages"]
    assert len(meldinger) == 2
    system, bruker = meldinger
    assert system == {"role": "system", "content": systemtekst}
    assert set(bruker) == {"role", "content"} and bruker["role"] == "user"
    assert isinstance(bruker["content"], str)

    def unike_felt(par: list[tuple[str, object]]) -> dict:
        objekt = dict(par)
        assert len(objekt) == len(par), "duplikatfelt i brukermeldingen"
        return objekt

    data = json.loads(bruker["content"], object_pairs_hook=unike_felt)
    assert isinstance(data, dict)
    return data


def kontroller_tolking(flyt: Flyt, *, med_http: bool) -> None:
    assert flyt.ki is not None and flyt.transport is not None
    forventet = Counter(PREFERANSE_VED_ID.values())
    assert Counter(flyt.ki.tolkninger) == forventet
    sendt: Counter[str] = Counter()
    for forespørsel in flyt.transport.til("preferanse"):
        data = brukerdata(forespørsel, PROMPT, "preferanse", preferanseskjema())
        assert set(data) == {"tekst"} and isinstance(data["tekst"], str)
        assert not list(kandidat_ider(forespørsel))
        sendt[data["tekst"]] += 1
    assert sendt == (forventet if med_http else Counter())


def poenggrunnlag(rad: RangertKandidat | None) -> dict | None:
    if rad is None:
        return None
    return {"kandidat_id": rad.id, "plass": rad.plass,
            "poeng": {f: float(getattr(rad.eksakte_poeng, f))
                      for f in ("kostnad", "timebelastning", "ulempe", "preferanse", "total")}}


def kontroller_påstand(påstand: dict, kandidat: RangertKandidat, referanse: RangertKandidat | None) -> None:
    # Påstandenes felt og verdier må være avgrenset selv om adapterens påstandsgenerator endres.
    assert påstand["kandidat_id"] == kandidat.id
    faktorer = {"kostnad", "timebelastning", "ulempe", "preferanse"}
    if påstand["type"] == "regler":
        assert set(påstand) == {"type", "kandidat_id"}
    elif påstand["type"] == "egen":
        assert set(påstand) == {"type", "kandidat_id", "faktor", "retning"}
        assert påstand["faktor"] in faktorer and påstand["retning"] in {"opp", "ned"}
    else:
        assert påstand["type"] == "sammenligning" and referanse is not None
        assert set(påstand) == {"type", "kandidat_id", "referanse_id", "faktor", "retning"}
        assert påstand["referanse_id"] == referanse.id
        assert påstand["faktor"] in faktorer | {"total"} and påstand["retning"] in {"høyere", "lavere", "lik"}


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
    assert flyt.transport is not None and flyt.ki is not None
    forespørsler = flyt.transport.til("avveining")
    if not forespørsler:
        return
    assert len(forespørsler) == len(flyt.ki.forklaringer)
    for forespørsel, (kandidat, referanse) in zip(forespørsler, flyt.ki.forklaringer, strict=True):
        data = brukerdata(forespørsel, avveining.PROMPT, "avveining", avveining.skjema())
        ider = set(kandidat_ider(data))
        assert ider and not ider & UTELUKKEDE.keys(), \
            f"utelukket ID i forklaringsforespørselen: {ider & UTELUKKEDE.keys()}"
        assert not nevner_utelukket(forespørsel)
        assert set(data) == {"kandidat", "referanse", "tillatte"}
        assert data["kandidat"] == poenggrunnlag(kandidat)
        assert data["referanse"] == poenggrunnlag(referanse)
        assert isinstance(data["tillatte"], list) and data["tillatte"]
        for påstand in data["tillatte"]:
            kontroller_påstand(påstand, kandidat, referanse)


def kontroller_api_svar(flyt: Flyt) -> None:
    """Kandidatrader, godkjenningsgrunnlag og avveiningssvar har bare Gyldige kandidater."""
    rader = flyt.liste["kandidater"]
    assert rader and {r["id"] for r in rader} <= GYLDIGE.keys()
    assert {r["navn"] for r in rader} <= set(GYLDIGE.values())
    # Hele listesvaret unntatt Ekskludert-boksen, så også et nytt toppfelt fanges.
    uten_boks = {k: v for k, v in flyt.liste.items() if k != "utelukkelser"}
    assert not nevner_utelukket(uten_boks)
    idfelt = ("id", "kandidat_id", "referanse_id")
    assert not set(kandidat_ider(uten_boks, idfelt)) & UTELUKKEDE.keys()
    for id, grunnlag in flyt.grunnlag.items():
        assert grunnlag["status"] == "ok" and grunnlag["kandidat"]["id"] == id and id in GYLDIGE
        if grunnlag["topprangert"] is not None:
            assert grunnlag["topprangert"]["id"] in GYLDIGE
        assert not nevner_utelukket(grunnlag)
        assert not set(kandidat_ider(grunnlag, idfelt)) & UTELUKKEDE.keys()
    assert flyt.avveininger
    for id, avv in flyt.avveininger.items():
        assert avv["kandidat_id"] == id and id in GYLDIGE
        assert not nevner_utelukket(avv)
        assert not set(kandidat_ider(avv, idfelt)) & UTELUKKEDE.keys()
    # Live-ruten skal bare vise faktakontrollert tekst for det aktuelle kandidatparet.
    # Tall i lovlige poengsummer kan være identiske med en utelukket kandidats ID.
    assert flyt.transport is not None and flyt.ki is not None
    if flyt.transport.til("avveining"):
        for kandidat, referanse in flyt.ki.forklaringer:
            svar = flyt.avveininger[kandidat.id]
            if svar["status"] == "ok":
                tillatte = {p.tekst for p in avveining.tillatte_påstander(kandidat, referanse)}
                assert set(svar["paastander"]) <= tillatte


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
    kontroller_tolking(flyt, med_http=fabrikk is openrouter)


@pytest.fixture(scope="module")
def registrert_flyt(tmp_path_factory: pytest.TempPathFactory) -> Flyt:
    testmotor = lag_engine(tmp_path_factory.mktemp("lekkasjekontroll") / "api.db")
    try:
        opprett_skjema(testmotor)
        with lag_sessionmaker(testmotor).begin() as session:
            fyll_testdata(session)
            legg_til_turnusansvarlig(session, PASSORD, "tilfeldig")
        return kjør_flyt(openrouter, testmotor)
    finally:
        testmotor.dispose()


@pytest.fixture
def flyt(registrert_flyt: Flyt) -> Flyt:
    """Uavhengige kopier av observasjonene som endres i de isolerte kontrollene."""
    assert registrert_flyt.ki is not None and registrert_flyt.transport is not None
    ki = copy(registrert_flyt.ki)
    ki.tolkninger = ki.tolkninger.copy()
    transport = copy(registrert_flyt.transport)
    transport.forespørsler = deepcopy(transport.forespørsler)
    return replace(registrert_flyt, ki=ki, transport=transport,
                   grunnlag=deepcopy(registrert_flyt.grunnlag), avveininger=deepcopy(registrert_flyt.avveininger))


@pytest.mark.parametrize("portnavn", ["avveining", "preferanse"])
@pytest.mark.parametrize("avvik", ["systemtekst", "systemrolle", "brukerrolle", "ekstra_melding",
                                   "meldingsfelt", "ekstra_forespørselsfelt", "skjemabeskrivelse"])
def test_meldingsavvik_avvises(portnavn: str, avvik: str, flyt: Flyt) -> None:
    assert flyt.transport is not None
    forespørsel = flyt.transport.til(portnavn)[0]
    meldinger = forespørsel["messages"]
    lekket = str(next(iter(UTELUKKEDE)))
    if avvik == "systemtekst":
        meldinger[0]["content"] += f" {lekket}"
    elif avvik == "systemrolle":
        meldinger[0]["role"] = "assistant"
    elif avvik == "brukerrolle":
        meldinger[1]["role"] = "assistant"
    elif avvik == "ekstra_melding":
        meldinger.append({"role": "user", "content": lekket})
    elif avvik == "meldingsfelt":
        meldinger[1]["name"] = lekket
    elif avvik == "ekstra_forespørselsfelt":
        forespørsel["metadata"] = {"ansatt_id": lekket}
    else:
        forespørsel["response_format"]["json_schema"]["description"] = f"Kandidat-ID {lekket}"
    with pytest.raises(AssertionError):
        if portnavn == "avveining":
            kontroller_forklaringsforespørslene(flyt)
        else:
            kontroller_tolking(flyt, med_http=True)


@pytest.mark.parametrize("sted", ["brukerinnhold", "kandidat", "poeng", "påstand"])
def test_ukjent_felt_med_utelukket_id_i_forklaringen_avvises(sted: str, flyt: Flyt) -> None:
    assert flyt.transport is not None
    bruker = flyt.transport.til("avveining")[0]["messages"][1]
    data = json.loads(bruker["content"])
    steder = {"brukerinnhold": data, "kandidat": data["kandidat"], "poeng": data["referanse"]["poeng"],
              "påstand": data["tillatte"][0]}
    steder[sted]["intern_id"] = next(iter(UTELUKKEDE))
    bruker["content"] = json.dumps(data)
    with pytest.raises(AssertionError):
        kontroller_forklaringsforespørslene(flyt)


@pytest.mark.parametrize("grense", ["port", "transport"])
@pytest.mark.parametrize("avvik", ["endret", "mangler", "ekstra"])
def test_avvik_fra_råtekst_per_ansatt_avvises(grense: str, avvik: str, flyt: Flyt) -> None:
    assert flyt.ki is not None and flyt.transport is not None
    # To ansatte har samme råtekst. Å miste den ene er usynlig ved mengdesammenligning.
    tekst = next(t for t, n in Counter(PREFERANSE_VED_ID.values()).items() if n > 1)
    if grense == "port":
        tekster = flyt.ki.tolkninger
        if avvik == "mangler":
            tekster.remove(tekst)
        elif avvik == "ekstra":
            tekster.append(tekst)
        else:
            tekster[tekster.index(tekst)] = f"{tekst} [status=ute]"
    else:
        forespørsel = next(f for f in flyt.transport.til("preferanse")
                          if json.loads(f["messages"][1]["content"])["tekst"] == tekst)
        if avvik == "mangler":
            flyt.transport.forespørsler.remove(forespørsel)
        elif avvik == "ekstra":
            flyt.transport.forespørsler.append(forespørsel)
        else:
            forespørsel["messages"][1]["content"] = json.dumps({"tekst": f"{tekst} [status=ute]"})
    with pytest.raises(AssertionError):
        kontroller_tolking(flyt, med_http=True)


def test_legitime_ord_i_råteksten_tillates(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    ansatt_id = next(iter(PREFERANSE_VED_ID))
    tekst = "Jeg er en gyldig kandidat til vaktnummer 4127."
    monkeypatch.setitem(PREFERANSE_VED_ID, ansatt_id, tekst)
    with engine.begin() as tilkobling:
        tilkobling.execute(update(AnsattRad).where(AnsattRad.id == ansatt_id).values(preferanse=tekst))
    kontroller_tolking(kjør_flyt(openrouter, engine), med_http=True)


@pytest.mark.parametrize("endepunkt", ["grunnlag", "avveininger"])
@pytest.mark.parametrize("idfelt", ["id", "kandidat_id", "referanse_id"])
@pytest.mark.parametrize("idtype", [int, str])
def test_nestet_utelukket_id_i_api_svar_avvises(endepunkt: str, idfelt: str, idtype: type, flyt: Flyt) -> None:
    svar = flyt.grunnlag if endepunkt == "grunnlag" else flyt.avveininger
    next(iter(svar.values()))["historikk"] = [{"kobling": {idfelt: idtype(next(iter(UTELUKKEDE)))}}]
    with pytest.raises(AssertionError):
        kontroller_api_svar(flyt)


def test_utelukket_id_i_påstandstekst_avvises(flyt: Flyt) -> None:
    next(iter(flyt.avveininger.values()))["paastander"].append(f"Kandidat-ID {next(iter(UTELUKKEDE))}")
    with pytest.raises(AssertionError):
        kontroller_api_svar(flyt)


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
