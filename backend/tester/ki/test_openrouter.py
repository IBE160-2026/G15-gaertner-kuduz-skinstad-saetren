"""`OpenRouterKiAdapter` og begrenseren (story 5.1, AD-7, P-05).

Alle tester bruker falsk transport og falsk klokke: ingen nettverk, ingen nøkkel og
ingen faktisk venting. Klokka går bare når `sov` kalles eller transporten flytter den.
"""

import io
import json
import logging
import ssl
from collections.abc import Callable, Mapping
from contextlib import ExitStack
from dataclasses import dataclass, field
from email.message import Message
from urllib.error import HTTPError, URLError

import pytest

from adaptere.ki import openrouter
from adaptere.ki.begrenser import Begrenser, TidsbudsjettOpbrukt
from adaptere.ki.openrouter import (
    PROMPT,
    URL,
    HttpSvar,
    Nettverksfeil,
    OpenRouterKiAdapter,
    Tolkefeil,
    les_svar,
    urllib_transport,
)
from adaptere.lagring.testdata import PREFERANSER
from domene.porter.rangering import TolketPreferanse
from domene.regelmotor.rangering import PREFERANSEPOENG

NØKKEL = "test-nokkel-ikke-ekte"
TEKST_4 = PREFERANSER[4][0]
VEGG_START = 1_800_000_000.0  # epoke-sekunder for den falske veggklokka


class FalskKlokke:
    def __init__(self) -> None:
        self.nå = 1000.0
        self.søvn: list[float] = []

    def __call__(self) -> float:
        return self.nå

    def sov(self, sekunder: float) -> None:
        assert sekunder >= 0
        self.søvn.append(sekunder)
        self.nå += sekunder

    def vegg(self) -> float:
        return VEGG_START + (self.nå - 1000.0)


@dataclass
class Kall:
    url: str
    kropp: dict
    headere: Mapping[str, str]
    tidsavbrudd: float


Svar = HttpSvar | Exception | Callable[[float], HttpSvar]


@dataclass
class FalskTransport:
    """Gir svarene i rekkefølge. Det siste gjentas. En funksjon får tidsavbruddet."""

    svar: list[Svar]
    kall: list[Kall] = field(default_factory=list)

    def __call__(self, url: str, kropp: bytes, headere: Mapping[str, str], tidsavbrudd: float) -> HttpSvar:
        self.kall.append(Kall(url, json.loads(kropp), dict(headere), tidsavbrudd))
        neste = self.svar[min(len(self.kall), len(self.svar)) - 1]
        if isinstance(neste, Exception):
            raise neste
        if callable(neste):
            return neste(tidsavbrudd)
        return neste


def innhold(innhold: object, finish_reason: str = "stop") -> bytes:
    tekst = innhold if isinstance(innhold, str) else json.dumps(innhold, ensure_ascii=False)
    return json.dumps({"choices": [{"message": {"content": tekst}, "finish_reason": finish_reason}]}).encode()


def ok(kategori: str = "positiv_ved_behov", begrunnelse: str = "Personen tar gjerne en ekstravakt ved behov.") -> HttpSvar:
    return HttpSvar(200, {}, innhold({"kategori": kategori, "begrunnelse": begrunnelse}))


def status(kode: int, headere: Mapping[str, str] | None = None) -> HttpSvar:
    return HttpSvar(kode, dict(headere or {}), b"")


def adapter(klokke: FalskKlokke, transport: FalskTransport, modell: str = "openai/gpt-6-luna",
            begrenser: Begrenser | None = None) -> OpenRouterKiAdapter:
    return OpenRouterKiAdapter(
        NØKKEL, modell, transport=transport, klokke=klokke, sov=klokke.sov, veggklokke=klokke.vegg,
        begrenser=begrenser,
    )


# --- Forespørselen (AD-7) --------------------------------------------------------


def test_forespørselen_binder_leverandør_skjema_og_slår_av_resonnering() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([ok()])
    adapter(klokke, transport).tolk(TEKST_4)
    (kall,) = transport.kall
    assert kall.url == URL == "https://openrouter.ai/api/v1/chat/completions"
    assert kall.headere == {"Content-Type": "application/json", "Authorization": f"Bearer {NØKKEL}"}
    assert kall.tidsavbrudd == 45
    kropp = kall.kropp
    assert kropp["model"] == "openai/gpt-6-luna"
    assert kropp["provider"] == {"only": ["openai"], "allow_fallbacks": False, "require_parameters": True}
    assert kropp["reasoning"] == {"enabled": False}
    assert kropp["messages"] == [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": json.dumps({"tekst": TEKST_4}, ensure_ascii=False)},
    ]
    assert kropp["response_format"] == {"type": "json_schema", "json_schema": {
        "name": "preferanse", "strict": True, "schema": {
            "type": "object",
            "properties": {"kategori": {"type": "string", "enum": list(PREFERANSEPOENG)},
                           "begrunnelse": {"type": "string"}},
            "required": ["kategori", "begrunnelse"],
            "additionalProperties": False,
        },
    }}


def test_leverandøren_er_prefikset_i_modellen() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([ok()])
    tolkning = adapter(klokke, transport, modell="anthropic/claude-haiku-5.5").tolk(TEKST_4)
    assert transport.kall[0].kropp["provider"]["only"] == ["anthropic"]
    assert transport.kall[0].kropp["model"] == "anthropic/claude-haiku-5.5"
    assert isinstance(tolkning, TolketPreferanse) and tolkning.modell == "anthropic/claude-haiku-5.5"


@pytest.mark.parametrize("modell", ["gpt-6-luna", "/gpt", "openai/", ""])
def test_modell_uten_leverandør_avvises(modell: str) -> None:
    with pytest.raises(ValueError):
        OpenRouterKiAdapter(NØKKEL, modell)


def test_nøkkelen_vises_ikke_i_repr() -> None:
    assert NØKKEL not in repr(OpenRouterKiAdapter(NØKKEL))


# --- Matrisen ---------------------------------------------------------------------


def test_vellykket_tolkning() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([ok(begrunnelse="  Tar gjerne en ekstravakt.  ")])
    assert adapter(klokke, transport).tolk(TEKST_4) == TolketPreferanse(
        "positiv_ved_behov", "Tar gjerne en ekstravakt.", "openai/gpt-6-luna",
    )
    assert klokke.søvn == []


@pytest.mark.parametrize(("feil", "feiltype"), [
    (status(500), "5xx"), (status(503), "5xx"), (Nettverksfeil("URLError"), "nettverk"),
])
def test_forbigående_feil_hver_gang_gir_fire_kall(feil: Svar, feiltype: str) -> None:
    klokke, transport = FalskKlokke(), FalskTransport([feil])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil(feiltype)
    assert len(transport.kall) == 4
    assert klokke.søvn == [2, 4, 8]


def test_siste_feil_bestemmer_feiltypen() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([status(502), Nettverksfeil("x"), status(500), Nettverksfeil("x")])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("nettverk")


def test_5xx_så_ok() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([status(503), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [2]


def test_429_venter_til_reset() -> None:
    klokke = FalskKlokke()
    reset = str(int((klokke.vegg() + 5) * 1000))
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [5]


def test_429_teller_ikke_mot_de_tre_nye_forsøkene() -> None:
    klokke = FalskKlokke()

    def grense(_: float) -> HttpSvar:
        return status(429, {"x-ratelimit-reset": str(int((klokke.vegg() + 1) * 1000))})

    transport = FalskTransport([grense, status(500), grense, status(500), status(500), status(500)])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("5xx")
    assert len(transport.kall) == 6
    assert klokke.søvn == [1, 2, 1, 4, 8]


def test_429_over_budsjett_venter_ikke() -> None:
    klokke = FalskKlokke()
    reset = str(int((klokke.vegg() + 100) * 1000))
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), ok()])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("tidsbudsjett")
    assert len(transport.kall) == 1
    assert klokke.søvn == []


def test_429_med_19_sifre_leses_og_går_over_budsjettet() -> None:
    # Grensen i `_venting_429`: 19 sifre leses som tidsstempel, 20 sifre er uleselige.
    klokke = FalskKlokke()
    transport = FalskTransport([status(429, {"x-ratelimit-reset": "9" * 19}), ok()])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("tidsbudsjett")
    assert len(transport.kall) == 1
    assert klokke.søvn == []


@pytest.mark.parametrize(("sekunder", "søvn", "kall"), [(89, [89], 2), (90, [], 1)])
def test_tolk_venter_ikke_når_ventingen_slutter_ved_fristen(sekunder: int, søvn: list[float], kall: int) -> None:
    # Story 5.4 endret `>` til `>=` i den felles `_send`, så grensen gjelder også tolkningen.
    klokke = FalskKlokke()
    reset = str(int((klokke.vegg() + sekunder) * 1000))
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse if kall == 2 else Tolkefeil)
    assert klokke.søvn == søvn
    assert len(transport.kall) == kall


def test_429_uten_reset_venter_ett_vindu() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([status(429), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [60]


@pytest.mark.parametrize("kode", [400, 401, 402, 403, 404, 408, 422, 301])
def test_4xx_prøves_ikke_på_nytt(kode: int) -> None:
    klokke, transport = FalskKlokke(), FalskTransport([status(kode), ok()])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("4xx")
    assert len(transport.kall) == 1
    assert klokke.søvn == []


UBRUKELIGE = {
    "ugyldig JSON i innholdet": innhold("{ikke json"),
    "innholdet er ikke et objekt": innhold(["positiv_ved_behov"]),
    "ukjent kategori": innhold({"kategori": "uklar", "begrunnelse": "Uklart."}),
    "kategori som tall": innhold({"kategori": 75, "begrunnelse": "Uklart."}),
    "manglende begrunnelse": innhold({"kategori": "noytral"}),
    "ekstra felt": innhold({"kategori": "noytral", "begrunnelse": "Nøytral.", "poeng": 50}),
    "tom begrunnelse": innhold({"kategori": "noytral", "begrunnelse": "   "}),
    "begrunnelse som tall": innhold({"kategori": "noytral", "begrunnelse": 1}),
    "tom choices": json.dumps({"choices": []}).encode(),
    "manglende choices": json.dumps({"id": "x"}).encode(),
    "finish_reason length": innhold({"kategori": "noytral", "begrunnelse": "Nøytral."}, "length"),
    "manglende finish_reason": json.dumps({"choices": [{"message": {"content": "{}"}}]}).encode(),
    "innhold null": json.dumps({"choices": [{"message": {"content": None}, "finish_reason": "stop"}]}).encode(),
    "kropp er ikke JSON": b"<html>",
    "tom kropp": b"",
}


@pytest.mark.parametrize("kropp", UBRUKELIGE.values(), ids=UBRUKELIGE.keys())
def test_ubrukelig_svar_prøves_ikke_på_nytt_og_diktes_ikke_opp(kropp: bytes) -> None:
    klokke, transport = FalskKlokke(), FalskTransport([HttpSvar(200, {}, kropp), ok()])
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("ubrukelig")
    assert len(transport.kall) == 1
    assert les_svar(kropp, "openai/gpt-6-luna") is None


# --- Tidsbudsjett (forslag, P-05/OP-03) -----------------------------------------


def test_tidsavbruddet_er_gjenstående_budsjett_når_det_er_under_45_s() -> None:
    klokke = FalskKlokke()

    def tregt(tidsavbrudd: float) -> HttpSvar:
        klokke.nå += min(50.0, tidsavbrudd)
        return status(500)

    transport = FalskTransport([tregt, ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    # 45 s første kall, 2 s venting, så 90 − 47 = 43 s igjen.
    assert [k.tidsavbrudd for k in transport.kall] == [45, 43]


def test_neste_venting_over_budsjett_gir_tidsbudsjett() -> None:
    klokke = FalskKlokke()

    def tregt(tidsavbrudd: float) -> HttpSvar:
        klokke.nå += min(40.0, tidsavbrudd)
        raise Nettverksfeil("TimeoutError")

    transport = FalskTransport([tregt])
    # 40 + 2 + 40 + 4 + 4 (tidsavbrudd) = 90; neste venting på 8 s går over.
    assert adapter(klokke, transport).tolk(TEKST_4) == Tolkefeil("tidsbudsjett")
    assert [k.tidsavbrudd for k in transport.kall] == [45, 45, 4]
    assert klokke.søvn == [2, 4]


# --- Begrenseren -----------------------------------------------------------------


def test_19_kall_det_19_venter_til_vinduet_er_ledig() -> None:
    klokke, transport = FalskKlokke(), FalskTransport([ok()])
    ki = adapter(klokke, transport)
    for _ in range(18):
        assert isinstance(ki.tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == []
    assert isinstance(ki.tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [60]
    assert len(transport.kall) == 19


def test_venting_i_begrenseren_teller_mot_budsjettet() -> None:
    klokke = FalskKlokke()
    begrenser = Begrenser(18, 5, klokke=klokke, sov=klokke.sov)
    for _ in range(18):
        with begrenser.plass(klokke() + 90):
            pass
    klokke.nå += 1
    # Ledig plass om 59 s. Reset 40 s etter det går over budsjettet (59 + 40 > 90).
    reset = str(int((klokke.vegg() + 59 + 40) * 1000))
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), ok()])
    assert adapter(klokke, transport, begrenser=begrenser).tolk(TEKST_4) == Tolkefeil("tidsbudsjett")
    assert klokke.søvn == [59]
    assert len(transport.kall) == 1


def test_begrenseren_gir_opp_uten_å_vente_når_fristen_er_for_nær() -> None:
    klokke = FalskKlokke()
    begrenser = Begrenser(2, 5, klokke=klokke, sov=klokke.sov)
    for _ in range(2):
        with begrenser.plass(klokke() + 90):
            pass
    with pytest.raises(TidsbudsjettOpbrukt):
        with begrenser.plass(klokke() + 30):
            pass
    assert klokke.søvn == []


def test_høyst_fem_samtidige() -> None:
    klokke = FalskKlokke()
    begrenser = Begrenser(18, 5, klokke=klokke, sov=klokke.sov)
    with ExitStack() as stakk:
        for _ in range(5):
            stakk.enter_context(begrenser.plass(klokke() + 90))
        with pytest.raises(TidsbudsjettOpbrukt):
            with begrenser.plass(klokke()):
                pass
    # Plassene er sluppet igjen.
    with begrenser.plass(klokke()):
        pass


def test_429_med_reset_i_fortiden_venter_minst_ett_sekund() -> None:
    klokke = FalskKlokke()
    reset = str(int((klokke.vegg() - 30) * 1000))
    transport = FalskTransport([status(429, {"x-ratelimit-reset": reset}), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [1]


def test_429_med_reset_i_sekunder_venter_minst_ett_sekund() -> None:
    klokke = FalskKlokke()
    transport = FalskTransport([status(429, {"x-ratelimit-reset": str(int(klokke.vegg()))}), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [1]


@pytest.mark.parametrize("verdi", ["²", "١٢٣", "12a", "-5", "", pytest.param("9" * 400, id="over-flyttallsgrensen"),
                                   pytest.param("9" * 20, id="20-sifre"),
                                   pytest.param("9" * 5000, id="over-heltallsgrensen")])
def test_429_med_uleselig_reset_venter_ett_vindu(verdi: str) -> None:
    klokke = FalskKlokke()
    transport = FalskTransport([status(429, {"x-ratelimit-reset": verdi}), ok()])
    assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    assert klokke.søvn == [60]


# --- urllib_transport (uten nettverk) ----------------------------------------------


class FalskRespons:
    def __init__(self, kropp: bytes, headere: dict[str, str]) -> None:
        self.status = 200
        self.headers = Message()
        for navn, verdi in headere.items():
            self.headers[navn] = verdi
        self._kropp = kropp

    def read(self) -> bytes:
        return self._kropp

    def __enter__(self) -> "FalskRespons":
        return self

    def __exit__(self, *_: object) -> None:
        return None


def falsk_opener(monkeypatch: pytest.MonkeyPatch, utfall: object) -> list[tuple[object, float]]:
    åpnet: list[tuple[object, float]] = []

    class Opener:
        def open(self, forespørsel: object, timeout: float) -> object:
            åpnet.append((forespørsel, timeout))
            if isinstance(utfall, BaseException):
                raise utfall
            return utfall

    monkeypatch.setattr(openrouter, "build_opener", lambda *_handlere: Opener())
    return åpnet


def http_feil(kode: int, headere: dict[str, str]) -> HTTPError:
    melding = Message()
    for navn, verdi in headere.items():
        melding[navn] = verdi
    return HTTPError(URL, kode, "feil", melding, io.BytesIO(b'{"error": "hemmelig prompt"}'))


def send() -> HttpSvar:
    return urllib_transport(URL, b"{}", {"Authorization": "Bearer x"}, 12.5)


def test_transport_200_gir_kropp_og_headere_i_små_bokstaver(monkeypatch: pytest.MonkeyPatch) -> None:
    åpnet = falsk_opener(monkeypatch, FalskRespons(b"svar", {"X-RateLimit-Remaining": "17"}))
    assert send() == HttpSvar(200, {"x-ratelimit-remaining": "17"}, b"svar")
    ((forespørsel, timeout),) = åpnet
    assert timeout == 12.5
    assert forespørsel.get_method() == "POST"  # type: ignore[attr-defined]


@pytest.mark.parametrize(("kode", "headere", "forventet"), [
    (402, {}, {}),
    (429, {"X-RateLimit-Reset": "1800000005000", "Retry-After": "5"},
     {"x-ratelimit-reset": "1800000005000", "retry-after": "5"}),
])
def test_transport_http_feil_gir_status_uten_kropp(
    monkeypatch: pytest.MonkeyPatch, kode: int, headere: dict[str, str], forventet: dict[str, str],
) -> None:
    falsk_opener(monkeypatch, http_feil(kode, headere))
    assert send() == HttpSvar(kode, forventet, b"")


@pytest.mark.parametrize("feil", [URLError("ingen forbindelse"), TimeoutError("timed out")])
def test_transport_nettverksfeil(monkeypatch: pytest.MonkeyPatch, feil: Exception) -> None:
    falsk_opener(monkeypatch, feil)
    with pytest.raises(Nettverksfeil):
        send()


def sertifikatfeil(kode: object = "CERTIFICATE_VERIFY_FAILED") -> ssl.SSLCertVerificationError:
    # Slik `urllib` på macOS uten sertifikatlager feilet 2026-11-16. Fra Python settes
    # ikke `reason`, så testen setter den som OpenSSL ville gjort.
    feil = ssl.SSLCertVerificationError(1, "[SSL: CERTIFICATE_VERIFY_FAILED] Bearer hemmelig")
    feil.reason = kode
    return feil


@pytest.mark.parametrize(("feil", "årsak"), [
    (URLError(sertifikatfeil()), "URLError/SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED"),
    (sertifikatfeil(), "SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED"),
    (URLError(ConnectionRefusedError(61, "Bearer hemmelig")), "URLError/ConnectionRefusedError"),
    (URLError("Bearer hemmelig"), "URLError"),
    (TimeoutError("Bearer hemmelig"), "TimeoutError"),
    (sertifikatfeil("ikke en kode: Bearer hemmelig"), "SSLCertVerificationError"),
    (sertifikatfeil(None), "SSLCertVerificationError"),
])
def test_nettverksfeil_viser_årsaken_uten_feiltekst(
    monkeypatch: pytest.MonkeyPatch, feil: Exception, årsak: str,
) -> None:
    falsk_opener(monkeypatch, feil)
    with pytest.raises(Nettverksfeil) as fanget:
        send()
    assert str(fanget.value) == årsak
    assert fanget.value.__cause__ is None and fanget.value.__suppress_context__


def test_nettverksfeil_logges_som_warning_uten_nøkkel(caplog: pytest.LogCaptureFixture) -> None:
    klokke = FalskKlokke()
    transport = FalskTransport([Nettverksfeil("URLError/SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED"), ok()])
    with caplog.at_level(logging.WARNING, logger="adaptere.ki.openrouter"):
        assert isinstance(adapter(klokke, transport).tolk(TEKST_4), TolketPreferanse)
    advarsler = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert [r.getMessage() for r in advarsler] == [
        "Nettverksfeil mot OpenRouter: URLError/SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED",
    ]
    assert NØKKEL not in caplog.text and TEKST_4 not in caplog.text
