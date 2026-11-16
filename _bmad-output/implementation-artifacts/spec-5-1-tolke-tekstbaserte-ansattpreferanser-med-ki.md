---
title: 'Story 5.1: Tolke tekstbaserte ansattpreferanser med KI'
type: 'feature'
created: '2026-11-16'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '35bf789cdfac580588757894f0bb71f39d1fe128'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Alle med registrert preferansetekst står på «Preferanse venter på tolkning» og 50 poeng, fordi ingen tolker tekstene (FR-10, P-05). `backend/adaptere/ki/` er tom.

**Approach:** `adaptere/ki` får en `OpenRouterKiAdapter` som tolker én tekst til en av de fem kategoriene med JSON-skjema, med AD-7s begrenser og avgrensede nye forsøk. `adaptere/lagring` lagrer sluttresultatet på `ansatt`, og `adaptere/api` tolker ventende tekster i bakgrunnen og sender lagrede tolkninger og feil inn i `ranger`.

## Boundaries & Constraints

**Always:**
- AD-1/AD-2: `domene/` importerer aldri `adaptere/`. Bare `adaptere/ki` lager en ny `TolketPreferanse`. `adaptere/lagring` validerer en lagret verdi ved lesing (kategori i `PREFERANSEPOENG`, `tolkeformat == 1`, hash lik SHA-256 av gjeldende tekst, ikke-tom begrunnelse); avvik gir `venter_paa_tolkning`. Rangeringen gjør aldri et KI-kall.
- Tolkning per Ansatt (19 tekster i testdataene, 15 unike), ingen deling på tvers av ansatte.
- Bare sluttresultatet per tekst skrives, aldri mellomliggende forsøk. Suksess nullstiller `tolkefeil`; feil nullstiller kategori, begrunnelse og modell. `tolket_teksthash` settes alltid. Skrivingen er én betinget `UPDATE … WHERE id = :id AND preferanse = :tekst`; ingen transaksjon holdes åpen under HTTP-kallet; 0 rader betyr at teksten er endret, og resultatet forkastes.
- AD-7: `provider = {"only": [<prefiks før «/» i modellen>], "allow_fallbacks": False, "require_parameters": True}`, `reasoning` av, `strict` JSON-skjema med `kategori` (enum) og `begrunnelse`. Én felles begrenser: høyst 18 kall per 60 s og 5 samtidige. 429 venter til `X-RateLimit-Reset` (epoke-ms). 402, andre 4xx og ubrukelige svar prøves ikke på nytt.
- **Forslag, valgt av Mithad 2026-11-16, ikke gruppevedtak (P-05/OP-03, PRD §8):** ved 5xx og nettverksfeil 3 nye forsøk etter 2, 4 og 8 s. 429 teller ikke mot de 3, men all venting (også i begrenseren og ved 429) teller mot et budsjett på 90 s per tekst, målt med monoton klokke fra første forsøk på å få plass i begrenseren. Tidsavbrudd per kall er min(45 s, gjenstående budsjett). Sluttstatus er den eksisterende `kunne_ikke_tolkes`, med feiltypen i `tolkefeil`: siste feil (`429`, `5xx`, `nettverk`, `4xx`, `ubrukelig`), eller `tidsbudsjett` når neste venting ville gått over budsjettet. Konstantene står samlet i adapteren og merkes som forslag i PR-en.
- Lagrede feil prøves på nytt ved neste oppstart (eneste vei til nytt forsøk til «Prøv igjen» finnes).
- Konfig leses av `ki_fra_miljo()` i `adaptere/api`, som bare brukes for modulobjektet `app`: `OPENROUTER_API_KEY`; `OPENROUTER_MODEL` (tom gir `openai/gpt-6-luna`); `KI_MODUS` (`openrouter` | `demo`, tom gir `openrouter`). Mangler nøkkel, er modus `demo` eller er modus ukjent, startes ingen tolkning, og det logges én WARNING-linje ved oppstart, f.eks. «Preferansetolkning er av: OPENROUTER_API_KEY er ikke satt. Se README.»
- **Beslutning (Mithad 2026-11-16):** tolkningen starter i en daemon-tråd fra FastAPI `lifespan` når backend starter. Appen kan brukes mens den pågår. `lag_app(..., ki=None)` starter aldri tolkning.
- Alle tester bruker falsk transport og falsk klokke; ingen nettverk, nøkkel eller faktisk venting. En autouse-fixture fjerner `OPENROUTER_API_KEY` og `KI_MODUS`.

**Never:** Ingen `DemoKiAdapter` (5.7), ingen Avveining (5.3), ingen redigering av tekst (5.9), ingen endring av vekter eller `PREFERANSEPOENG`. Ingen ny pakke i `requirements.txt`. Ingen KI-feil utelukker en Kandidat. Backend leser fortsatt ikke `.env` (gruppevalg); å endre det foreslås bare i PR-beskrivelsen. **Utsatt (Mithad 2026-11-16):** brukerutløst «Prøv igjen» etter endelig feil er ikke med; ført i `deferred-work.md`, og 5.1 kan ikke settes `done` før det er levert eller gruppa godtar utsettelsen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Vellykket | tekst nr. 4, svar `positiv_ved_behov` | lagret, `tolket`, 75 poeng | N/A |
| Ingen tekst | `preferanse` None eller blank | ingen kall, `ingen_registrert`, 50 | N/A |
| Venter | tekst uten lagret tolkning | `venter_paa_tolkning`, 50 | N/A |
| Endret tekst | lagret hash ≠ gjeldende | `venter_paa_tolkning` | gammel kategori brukes ikke |
| Endret under kall | tekst endres mens falskt kall pågår | ingenting lagres | resultat forkastes |
| 5xx/nettverk | feiler hver gang | 4 kall, venting 2/4/8 s, `kunne_ikke_tolkes` | `tolkefeil` = `5xx`/`nettverk` |
| 5xx så OK | 503, deretter gyldig | `tolket` | N/A |
| 429 | reset 5 s fram, så gyldig | venter 5 s, `tolket` | N/A |
| 429 over budsjett | reset 100 s fram | ingen venting, `kunne_ikke_tolkes` | `tidsbudsjett` |
| 402/400 | ett svar | 1 kall, `kunne_ikke_tolkes` | `4xx`, ikke nytt forsøk |
| Ubrukelig | ugyldig JSON, ukjent kategori, manglende/ekstra felt, tom begrunnelse, tom `choices`, `finish_reason` ≠ `stop` | `kunne_ikke_tolkes` | `ubrukelig`, intet oppdiktet |
| Ugyldig lagret | `tolkeformat` 2 eller ukjent kategori i databasen | `venter_paa_tolkning`, tolkes ved oppstart | N/A |

</frozen-after-approval>

## Code Map

- `backend/domene/porter/rangering.py` -- `TolketPreferanse(kategori)` og `Tolkestatus` finnes (4.4). Utvid med `begrunnelse: str` og `modell: str`. Frosne dataklasser, ikke Pydantic (2.5/4.4-presedensen, AV-18); avviket fra AC «Pydantic-modellen» føres i KI-loggen, og valideringen skjer i `adaptere/ki` (svar) og `adaptere/lagring` (lesing).
- `backend/domene/regelmotor/rangering.py` -- `ranger(vurdering, vakt, tolkede, feilede)` og `preferanse()` håndterer statusene. Ikke endre.
- `backend/adaptere/lagring/modeller.py` -- `AnsattRad`: nullbare `tolket_kategori`, `tolket_begrunnelse`, `tolket_modell`, `tolket_teksthash`, `tolkefeil`, `tolkeformat`. Kolonner på `ansatt` dekkes av `GRUNNLAGSTABELLER` (P-09).
- `backend/adaptere/lagring/kandidatgrunnlag.py` -- `Kandidatgrunnlag` får `tolkede: Mapping[int, TolketPreferanse]` og `feilede: frozenset[int]`, beregnet fra de samme `AnsattRad`-radene som `ansatte` (tekst og tolkning fra samme lesing). Fjern kommentaren om «story 5.1 må ta stilling».
- `backend/adaptere/lagring/database.py` -- les docstringen til `lag_engine` før transaksjonskode; endre ikke `isolation_level`.
- `backend/adaptere/lagring/godkjenninger.py` -- `endret_grunnlag`-flyten (P-09) som en ny tolkning skal utløse.
- `backend/adaptere/lagring/testdata.py` -- `FASIT[4127]` (totalscore 85,65 / 78,65 / 59,0 / 37,0 med preferanse 75/75/0/100). Tolkningskolonnene står tomme etter kjøring.
- `backend/adaptere/api/main.py` -- `app = lag_app()` på linje ~475 importeres av testene; kandidatruten (~398) sender i dag ingen tolkninger.
- `backend/tester/api/test_kandidater.py` -- `RANGERING_4127_UTEN_TOLKNING` (~311) skal fortsatt gjelde uten tolkning.
- `scripts/modelltest_prd_fasit.py` -- `PROMPT`, `payload_for`, `parse`: testet prompt og forespørsel. Kopier innholdet; ikke importer `scripts/`.
- `scripts/modelltest_robusthet.py` -- prototyp på begrenser, 429-reset (epoke-ms) og `urllib` med tidsavbrudd.
- `frontend/src/kandidater.ts`, `tekster.ts` -- viser allerede kategori og status. Ingen endring forventet.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/porter/rangering.py` -- utvid `TolketPreferanse`.
- [x] `backend/adaptere/ki/` (ny: `__init__.py`, `openrouter.py`, `begrenser.py`) -- `OpenRouterKiAdapter.tolk(tekst) -> TolketPreferanse | Tolkefeil` med stdlib `urllib` bak injiserbar transport, monoton klokke og `sleep`.
- [x] `backend/adaptere/lagring/modeller.py`, `kandidatgrunnlag.py`, ny `preferansetolkning.py` -- kolonner, validering ved lesing, `ventende_tekster(session)` (uten gyldig tolkning eller med feil), og betinget `lagre_resultat`.
- [x] `backend/adaptere/api/main.py` -- `ki_fra_miljo()`, `lag_app(..., ki=None)`, `lifespan` med daemon-tråd, synkron `tolk_ventende(okter, ki)` som testene kaller direkte, og `tolkede`/`feilede` fra `Kandidatgrunnlag` til `ranger`.
- [x] `.env.example`, `README.md`, `AGENTS.md` -- `KI_MODUS`, slett databasen etter skjemaendringen, tolkning starter med backend (19 kall, ca. 1–2 min), godkjenning kan gi «endret grunnlag» mens tolkningen pågår, og `--reload` starter tolkningen på nytt.
- [x] `backend/tester/ki/`, `tester/lagring/`, `tester/api/`, `tester/conftest.py` -- matrisen, forespørselsinnholdet (leverandør, modell, skjema, `reasoning`), begrenseren (19. kall venter), WARNING ved oppstart uten nøkkel (`caplog`), at `with TestClient(lag_app(ki=falsk))` starter tråden, og ingen tråd uten `ki`.
- [x] `docs/ki-logg/2026-11-16-preferansetolkning.md`, `docs/testing.md`, `sprint-status.yaml` -- KI-logg (prompt, `urllib`-valget, Pydantic-avviket), status `in-progress` → `review`.

**Acceptance Criteria:**
- Gitt testdataene og en falsk adapter som svarer etter fasiten, når `tolk_ventende` er ferdig, så gir `/api/vakter/4127/kandidater` `totalscore` lik `FASIT[4127]` (85,65 / 78,65 / 59,0 / 37,0), `preferansepoeng` [75, 75, 0, 100] og riktig `preferansekategori`; uten tolkning gjelder fortsatt `RANGERING_4127_UTEN_TOLKNING`.
- Gitt en lagret, gyldig tolkning, når `tolk_ventende` kjøres igjen, så gjøres ingen kall for den teksten.
- Gitt en vist godkjenningsflate, når en tolkning lagres før POST, så gir godkjenningen 409 `endret_grunnlag`; mellomliggende forsøk endrer ikke merket.
- Gitt `pytest` (inkl. import-linter-kontrakten), når den kjøres, så består alle tester.

## Implementation Notes

- 2026-11-16: Implementert av underagent (Opus 5.5). Avgjørelser som spesifikasjonen ikke dekket (429 uten reset venter 60 s, 3xx regnes som `4xx`, modell uten «/» slår av tolkningen, `Tolkefeil`/`Tolker` i `adaptere/ki`) står i [KI-loggen](../../docs/ki-logg/2026-11-16-preferansetolkning.md). Orkestrator kontrollerte diffen, at alle 12 matriserader og 4 AC har kjørende tester, og at `pytest` gir 653 bestått.

## Spec Change Log

## Review Triage Log

| Funn (spec-gjennomgang 2026-11-16, Opus) | Vurdering | Tiltak |
|---|---|---|
| 1 Tråd starter ved import av `app` | high | `ki_fra_miljo` bare for modulobjektet, `lifespan`, `tolk_ventende`, autouse-fixture |
| 2 Rekkefølge-AC skiller ikke tolket/utolket | high | AC på totalscore og poeng fra `FASIT` |
| 3 Betinget lagring ikke atomisk | high | Betinget `UPDATE`, ingen transaksjon under kall, test |
| 4 Pydantic-AC vs. dataklasser | medium | Validering ved lesing, avvik i KI-logg |
| 5 Suksess/feil samtidig, feil ved omstart | medium | Nullstilling, feil prøves ved oppstart |
| 6 90 s tvetydig | medium | Monoton klokke, startpunkt, tidsavbrudd, feiltyperegel |
| 7 Hvor `tolkede` leses | medium | Felt i `Kandidatgrunnlag` fra samme rader |
| 8 Annen modell / ugyldig `KI_MODUS` | medium | Leverandør fra prefiks, tom/ukjent verdi definert |
| 9 Merket endres under tolkning | medium | Bare sluttresultat skrives; dokumentert; test |
| 10 «Ubrukelig» for smalt | low | Matrisen utvidet |
| 11 Logglinje usynlig | low | WARNING, `caplog`-test |
| 12 Antall kall | low | 19 per ansatt; `--reload` dokumentert |

**Kodegjennomgang 2026-11-16 (blind, grensetilfeller, testhull; alle Opus):**

| Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|
| Modul-`app` får ekte adapter ved import under pytest-innsamling (blind, grense, testhull) | medium | Bekreftet: `test_helse.py:3` importerer `app` før autouse-fixturen; ingen kall i dag fordi `TestClient(app)` er uten `with`, men påstanden i conftest/AGENTS.md er usann | patch |
| Produksjonskoblingen `app = lag_app(ki=ki_fra_miljo())` er uten test (testhull) | medium | Forhåndsverifisert hull; `lag_app()` uten `ki` gir grønn suite | patch |
| `urllib_transport` uten test (blind, testhull) | medium | Forhåndsverifisert; omkastede `except` eller manglende `.lower()` ville gitt feil klassifisering live | patch |
| 429 med reset i fortiden gir 0 s venting og raske gjentak (blind, grense) | medium | Bekreftet i `_venting_429`: `max(0.0, …)`; brenner felles vindu til budsjettet går ut | patch |
| Ikke-ASCII-sifre i reset-header gir ValueError ut av `tolk()` (grense) | low | `'²'.isdigit()` er True, `int('²')` feiler; direkte retting | patch |
| Nøkkel med kontrolltegn kan havne i loggen via `logger.exception` (grense) | medium | `http.client` gir ValueError med headerverdien; liten sannsynlighet, men hemmelighet i logg | patch |
| Første lesing i tråden er ubeskyttet; gammel database gir rå traceback (blind, grense) | low | Bekreftet; scenariet README advarer mot er vanlig ved bytte av branch | patch |
| README mangler 60 s uten reset, 3xx som `4xx`, `KI_MODUS` skiller store/små bokstaver (blind) | low | Bekreftet; direkte dokumentrettelse | patch |
| Åpent gruppevedtak om forsøk/budsjett ikke ført i deferred-work (blind) | low | Bekreftet; ført av orkestrator | patch |
| AGENTS.md får storystatus som blir foreldet, og en sammenslått lang linje (blind) | low | Agentkontekstfil | defer |
| Feiltypen `429` kan aldri lagres (blind, grense) | low | Følger av den frosne regelen («`tidsbudsjett` når neste venting ville gått over budsjettet»); ingen skade | avvist |
| Annen feiltype ved omstart endrer merket uten å endre rangering (blind) | low | Samme oppførsel som en ny tolkning under oppstart, som er dokumentert; bare de første minuttene | avvist |
| Varige feil (401, `ubrukelig`) prøves igjen ved hver oppstart (blind) | low | Den frosne intensjonen sier at lagrede feil prøves ved neste oppstart (Mithad) | avvist |
| Begrenser per adapter, ikke per prosess; `--workers N` (blind, grense) | low | Én adapter og én worker i v1; delt begrenser hører til 5.3 | avvist |
| Lifespan stopper ikke tråden og vokter ikke mot dobbel start (blind, grense) | low | Daemon-tråd; hver test lager ny app; uvicorn avslutter prosessen | avvist |
| `begrunnelse` uten lengdegrense (blind) | low | Vises ikke i 5.1; `max_tokens` 600 begrenser | avvist |
| Langsom strøm kan gå forbi tidsavbruddet per kall (grense) | low | Krever ny frist-mekanikk; usannsynlig mot OpenRouter | avvist |
| Semaforen venter på ekte klokke mot falsk frist (grense) | low | Bare testtid; ingen test blokkerer i dag | avvist |
| `per_minutt <= 0` gir IndexError (grense) | false | Konstantene er faste (18 og 5); ingen vei inn med 0 | avvist |

## Design Notes

Én daemon-tråd holder; begrenseren tillater 5 samtidige, men 19 kall tar ca. 1–2 min med 18 per minutt. Tråden bruker egne økter fra `lag_sessionmaker`. `urllib` er valgt fordi backend ikke har en HTTP-klient i kjøretid og modelltestene bruker samme bibliotek (arkitektur § Deferred).

## Verification

**Commands:**
- `cd backend && .venv\Scripts\python -m pytest` -- expected: alle består
- `cd frontend && npm.cmd run test` -- expected: alle består (ingen endring forventet)

**Manual checks (if no CLI):**
- Med ekte nøkkel (valgfritt, 19 betalte kall): slett databasen, last testdata, start backend med nøkkelen satt, og se at taggene for #4127 går fra «venter» til kategori og at rekkefølgen følger fasiten.
- Uten nøkkel: start backend og se WARNING-linjen i terminalen.
