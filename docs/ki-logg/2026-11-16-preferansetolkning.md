# KI-logg: story 5.1 – tolke tekstbaserte ansattpreferanser med KI

## Oppgave og prompt

Implementeringen ble delegert til en underagent (Claude Opus 5.5 i Claude Code) med denne prompten: «Read `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md` fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.» Agenten leste spesifikasjonen, epic-konteksten for epic 5, prototypene i `scripts/modelltest_prd_fasit.py` og `scripts/modelltest_robusthet.py` og den eksisterende koden for rangering, lagring, grunnlagsmerke og API.

## Hva modellen leverte

- **Porten** `backend/domene/porter/rangering.py`: `TolketPreferanse` har fått `begrunnelse` og `modell` i tillegg til `kategori`. Domenetestene i `test_rangering.py` lager tolkninger med en liten hjelpefunksjon. Regelmotoren er ikke endret.
- **KI-adapteren** `backend/adaptere/ki/`:
  - `begrenser.py`: `Begrenser` med høyst 18 kallstarter i et glidende vindu på 60 s og høyst 5 samtidige. Den gir `TidsbudsjettOpbrukt` uten å vente når ventingen ville gått forbi fristen.
  - `openrouter.py`: `OpenRouterKiAdapter.tolk(tekst) -> TolketPreferanse | Tolkefeil`, `urllib_transport` uten omdirigering, `les_svar` og konstantene. Leverandøren er prefikset før «/» i modellnavnet.
- **Lagring**: seks nullbare kolonner på `ansatt` (`tolket_kategori`, `tolket_begrunnelse`, `tolket_modell`, `tolket_teksthash`, `tolkefeil`, `tolkeformat`). Ny `preferansetolkning.py` med `les_tolkning` (validering ved lesing), `tolkninger`, `ventende_tekster` og `lagre_resultat` (én betinget `UPDATE`). `Kandidatgrunnlag` har fått `tolkede` og `feilede` fra de samme radene som `ansatte`.
- **API**: `ki_fra_miljo()` (bare for modulobjektet `app`), `tolk_ventende(okter, ki)`, `lag_app(..., ki=None)` med `lifespan` som starter en daemon-tråd, og kandidatruten sender `tolkede` og `feilede` til `ranger`.
- **Tester**: `tester/conftest.py` (autouse-fixture), `tester/ki/test_openrouter.py`, `tester/lagring/test_preferansetolkning.py` og `tester/api/test_preferansetolkning.py`, til sammen 91 nye tester.
- **Dokumentasjon**: `.env.example` (`KI_MODUS`), README (oppstart med nøkkel, sletting av databasen, `--reload`, endret grunnlag), AGENTS.md og `docs/testing.md`.

## Prompten til modellen

Prompten er kopiert ordrett fra `PROMPT` i `scripts/modelltest_prd_fasit.py`, den samme som ble testet mot de 15 fasittekstene i PRD §4.5 og 14 tilleggstekster (se [robusthetstesten](2026-10-16-robusthet-luna.md)). Forespørselen følger `payload_for`: `max_tokens` 600, `reasoning: {"enabled": false}`, `provider` med `only`, `allow_fallbacks: false` og `require_parameters: true`, og et strengt JSON-skjema med `kategori` (enum med de fem nøklene i `PREFERANSEPOENG`) og `begrunnelse`. Brukerinnholdet er `{"tekst": ...}` som JSON, så teksten behandles som data. Svarkontrollen følger `parse`, og i tillegg kreves `finish_reason == "stop"`. Kategoriene i enum-en hentes fra `PREFERANSEPOENG`, så skjemaet og poengtabellen kan ikke komme ut av takt.

## Avgjørelser underveis

Disse står ikke i spesifikasjonen og bør ses over i PR-gjennomgangen:

- **`urllib`, ikke OpenAI-SDK eller `httpx`.** Backend har ingen HTTP-klient i kjøretid (`httpx2` er bare en testavhengighet for `TestClient`), modelltestene bruker `urllib`, og spesifikasjonen forbyr nye pakker. Valget mellom SDK og ren HTTP-klient var åpent i arkitekturen (§ Deferred). Feilkropper fra OpenRouter leses ikke, fordi de kan gjengi prompten.
- **Frosne dataklasser, ikke Pydantic, i porten.** AC-en sier «Pydantic-modellen». Spesifikasjonen ba om å følge presedensen fra 2.5 og 4.4, som er vedtatt som AV-18. Valideringen som Pydantic ville gitt, skjer i stedet i `les_svar` (svar fra modellen) og `les_tolkning` (lagret verdi).
- **`Tolkefeil` og `Tolker` ligger i `adaptere/ki`, ikke i `domene/porter`.** Domenet trenger bare å vite hvem som har feilet (`feilede`), ikke hvorfor. `Tolker` er en `Protocol`, så `DemoKiAdapter` i 5.7 og de falske adapterne i testene har samme form.
- **429 uten lesbar `X-RateLimit-Reset`** venter 60 s (ett vindu), innenfor budsjettet. Spesifikasjonen sier ikke hva som skal skje da. Konstanten er merket som forslag.
- **Andre statuser enn 200, 429 og 5xx** (også 3xx, siden omdirigering er slått av) gir `4xx` uten nytt forsøk.
- **`modell` i `TolketPreferanse`** er modellen som ble bedt om, ikke `model` i svaret. Leverandøren er låst, så de skal være like.
- **Validering ved lesing** krever også ikke-tom `tolket_modell`, og at en lagret feil ikke har kategori, begrunnelse eller modell samtidig. Begge gir `venter_paa_tolkning` ellers.
- **`ki_fra_miljo` slår av tolkningen også når `OPENROUTER_MODEL` mangler «/»**, med samme WARNING-form. `KI_MODUS` sammenlignes etter `strip()`, men skiller mellom store og små bokstaver.
- **Logging**: én WARNING når tolkningen er av, én WARNING per tekst som ender med feil, og INFO ellers. Teksten og nøkkelen logges aldri, bare ansatt-ID og feiltype. Python skriver WARNING til stderr også uten loggoppsett, så linjen vises under uvicorn.
- **En uventet unntak i adapteren for én tekst** logges med `logger.exception`, og de andre tekstene tolkes videre. Teksten får da ikke noe lagret resultat og venter til neste oppstart.

## Hva som ble rettet underveis

- **Fasittesten i API-et** sammenlignet først `totalscore` med `FASIT[4127]` med `==`. Den feilet i siste bit: `FASIT` er summert for hånd i `float` (85,65476190476191), mens Rangeringen gir den korrekt avrundede brøken 7195/84 (85,6547619047619). Testen følger nå presedensen fra `test_rangering.py`: `approx(abs=1e-12)` mot `FASIT` og eksakt likhet med `float(Fraction(...))`.
- **Testen av begrenseren og budsjettet** regnet først reset-tidspunktet fra før ventingen i begrenseren, så det var passert når kallet ble gjort. Forventningen ble rettet før testen ble brukt.
- **En halvskrevet test** (`test_uventet_unntak_...`) fikk en meningsløs forventning i første utkast og ble skrevet om før første kjøring.

### Rettet etter gjennomgang (koordinatoren, 2026-11-16)

- **`conftest.py`** fjernet KI-variablene bare i en fixture, men `adaptere.api.main` importeres når testene samles inn. En nøkkel i terminalen ga da modulobjektet `app` en ekte adapter. Variablene fjernes nå også fra `os.environ` øverst i `conftest.py`.
- **Ingen test viste at `app` faktisk får adapteren.** `lag_app` lagrer nå `app.state.ki`, og en ny test laster modulen på nytt med nøkkel satt. Testen feilet da `app = lag_app()` ble prøvd.
- **429 med reset i fortiden eller i sekunder** ga 0 s venting og nye kall med en gang, som bruker opp vinduet på 18 per minutt. Nå er ventingen minst `MIN_VENTING_429_S` (1 s, forslag). `str.isdigit()` godtok også ikke-ASCII-sifre som «²», og `int()` kastet da `ValueError` ut av `tolk()`. Nå kreves `isascii()` i tillegg.
- **En nøkkel med kontrolltegn eller ikke-ASCII** gjør at `http.client` kaster `ValueError` med headerverdien i meldingen, og `tolk_ventende` logget den med `logger.exception`. Nøkkelen kunne dermed havne i loggen. `ki_fra_miljo` slår nå av tolkningen med «OPENROUTER_API_KEY har ugyldige tegn».
- **En database fra før 5.1** drepte tråden med en rå traceback, fordi den første lesingen lå utenfor `try`. Nå logges én ERROR som ber om å slette databasen.
- **`urllib_transport` var ikke testet.** Nye tester bytter ut `build_opener`. Da `except`-leddene ble byttet om (`HTTPError` er en underklasse av `URLError`), feilet 2 tester.
- **README** sier nå også at 429 uten lesbar reset venter 60 s, at 3xx og andre statuser lagres som `4xx`, og at `KI_MODUS` skiller mellom store og små bokstaver.

## Kvalitetssikring

- **Testkjøring:** `pytest` i `backend/` ga 653 bestått (562 før, 91 nye), inkludert import-linter-kontrakten, før rettingene etter gjennomgangen. Etter rettingene består de berørte testfilene (`tester/ki/`, `tester/api/test_preferansetolkning.py` og `tester/test_helse.py`, 84 tester). Den fulle kjøringen gjøres av koordinatoren.
- **Mutasjoner som gjorde testene røde** (alle tilbakeført, deretter 91 av 91 bestått):
  - Betingelsen `preferanse = :tekst` fjernet fra `UPDATE`: 2 tester feilet.
  - Hash-kontrollen ved lesing fjernet: 3 tester feilet.
  - `allow_fallbacks: true`: forespørselstesten feilet.
  - Budsjettkontrollen før venting fjernet: 3 tester feilet.
  - Kandidatruten kaller `ranger` uten `tolkede` og `feilede`: 5 tester feilet.
- **Oppstart uten nøkkel:** `python -c "import adaptere.api.main"` uten nøkkel skrev `Preferansetolkning er av: OPENROUTER_API_KEY er ikke satt. Se README.` til stderr, og med `KI_MODUS=demo` tilsvarende linje for demo.
- **Ikke kontrollert:** ingen kall mot ekte OpenRouter er gjort, så `urllib_transport` og at Luna gir fasiten i appen (ikke bare i modelltesten) er ikke prøvd. Frontend er ikke endret. `npm run test` ga 52 Node-tester og 37 komponenttester bestått. Gjennomgang av agenter som ikke har sett implementeringen (OP-04) og menneskelig PR-gjennomgang gjenstår.
