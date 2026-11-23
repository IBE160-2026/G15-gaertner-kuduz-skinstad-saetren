---
title: 'Loggoppsett for backend – appens INFO-meldinger i terminalen'
type: 'bugfix'
created: '2026-11-23'
status: 'done'
baseline_commit: '8bcc39cb236f0f124a2d8d721e968708c1bef9e0'
route: 'dispatch'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Backend har ikke noe loggoppsett. Under uvicorn viser Python bare WARNING og høyere fra appens egne loggere (`adaptere.*`) via sin innebygde siste utvei. INFO-fremdriften fra `tolk_ventende` («N tekster venter», «tolket») vises derfor aldri. Ved live-kontrollen 2026-11-16 ga 19 tolkninger ingen linjer, og fremdriften måtte følges i databasen (`deferred-work.md`, story 5.1). Når sensor kjører live i story 5.8, ser det ut som ingenting skjer i 1–2 minutter.

**Approach:** Ved import av `adaptere/api/main.py`, før `app = lag_app(ki=ki_fra_miljo())`, får loggeren `adaptere` én egen terminalhandler på nivå INFO, med samme utseende som uvicorns egne linjer. Da vises også meldingene `ki_fra_miljo()` logger ved oppstart. README rettes.

## Boundaries & Constraints

**Always:** Oppsettet gjelder bare loggeren `adaptere` og undernivåene. Rotloggeren og uvicorns loggere røres ikke. Det kalles før `ki_fra_miljo()`. Det er idempotent, slik at gjentatt kall ikke gir doble linjer. `propagate` forblir `True`, slik at pytests `caplog` fortsatt fanger postene. Ingen melding får nøkkelen eller preferanseteksten. Eksisterende meldinger endres ikke.

**Beslutning (Ragnhild 2026-11-23, valg C):** Arkitekturdokumentet (`ARCHITECTURE-SPINE.md`, Deferred «Runtime-/driftslogging») røres ikke. Endringen behandles som en feilretting innenfor det utsatte punktet og går rett på `main`. En ny merknad i `deferred-work.md` sier at spinen bør oppdateres ved neste arkitekturgjennomgang eller i retrospektiven for epic 5.

**Never:** Ingen ny miljøvariabel, loggfil eller ny avhengighet. Ingen endring i `ki_fra_miljo()`, `AvveiningUt` eller avveiningsruten, som PR #38 (story 5.7) endrer. Ingen endring i `lag_app`. Ingen `logging.basicConfig` eller annen endring av rotloggeren.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fremdrift | `tolk_ventende` logger INFO | Linjen vises i terminalen, for eksempel `INFO:     Preferansetolkning: 19 tekster venter.` | N/A |
| Advarsel | WARNING fra `adaptere.*` | Vises én gang, nå med nivåprefiks | N/A |
| Gjentatt oppsett | Funksjonen kalles to ganger | Fortsatt én handler, hver post skrives én gang | N/A |
| Tester | `caplog.at_level(...)` i eksisterende tester | Fanger som før, alle tester grønne | N/A |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py:67` -- `logger = logging.getLogger(__name__)`. Ny hjelpefunksjon kan ligge rett under.
- `backend/adaptere/api/main.py:411-433` -- `tolk_ventende`: INFO-meldingene som skal bli synlige. Endres ikke.
- `backend/adaptere/api/main.py:665` -- `app = lag_app(ki=ki_fra_miljo())`. Oppsettet kalles på linjen over. PR #38 endrer ikke denne linjen.
- `backend/adaptere/ki/openrouter.py:29,327` -- logger WARNING om nettverksfeil. Får nivåprefiks, ellers uendret.
- `backend/tester/conftest.py` -- fjerner KI-miljøvariabler. Modulen `main` importeres i flere tester, så oppsettet kjøres også under pytest.
- `backend/tester/api/test_preferansetolkning.py`, `tester/api/test_kandidater.py`, `tester/ki/test_openrouter.py` -- bruker `caplog.at_level` mot `adaptere.*`. Skal fortsatt bestå.
- `README.md:160-176` -- avsnittet om fremdrift. Setningen på linje 169 er avbrutt midt i («…på nivå INFO, og») av avsnittet om én worker. Linje 166–167 sier at det ikke finnes noen knapp for nytt forsøk, men «Prøv igjen» kom i PR #33. PR #38 endrer fra linje 193.
- `_bmad-output/implementation-artifacts/deferred-work.md:5-7` -- punktet som markeres løst, med `status:` som i punktet over (linje 4).

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py` -- legg til en liten funksjon som gir loggeren `adaptere` en `StreamHandler` (stderr) på INFO med formatet `%(levelname)s:     %(message)s`, merket slik at den ikke legges til to ganger. Den tar en valgfri strøm for testbarhet. Kall den rett før `app = lag_app(...)`. -- Gjør fremdriften synlig uten å røre rot- eller uvicorn-loggere.
- [x] `backend/tester/api/test_terminallogg.py` -- test med `io.StringIO`: en INFO-post fra `adaptere.api.main` havner i strømmen, gjentatt kall gir én handler og én linje, og rotloggerens handlere er uendret. Rydd bort handleren etter testen. -- Dekker matrisen.
- [x] `README.md` -- skriv avsnittet om fremdrift på nytt: fremdriften vises i terminalen som `INFO:`-linjer, gi et eksempel, rett opp den avbrutte setningen og fjern påstanden om at knappen mangler (vis til «Prøv igjen»). -- README sier i dag det motsatte.
- [x] `_bmad-output/implementation-artifacts/deferred-work.md` -- legg `status: Løst 2026-11-23 …` på punktet, med en lenke til KI-loggen. Legg til et nytt punkt (`source_spec:` denne spesifikasjonen) om at `ARCHITECTURE-SPINE.md` linje 116 og 215 sier at runtime-logging ikke er besluttet, mens terminalvisning på INFO nå finnes, og at det bør oppdateres ved neste arkitekturgjennomgang eller i retrospektiven for epic 5. -- Lukker funnet og gjør avviket sporbart (valg C).
- [x] `docs/ki-logg/2026-11-23-loggoppsett-backend.md` -- oppgave, prompt, leveranse, rettinger og kvalitetssikring. -- AGENTS.md krever det for KI-generert kode.

**Acceptance Criteria:**
- Gitt backend startet med `uvicorn adaptere.api.main:app` og en gyldig nøkkel, når tolkningen kjører, så vises «tekster venter» og én «tolket»-linje per tekst i terminalen, og nøkkelen vises aldri.
- Gitt hele testsuiten, når `pytest` kjøres, så består alle tester.

## Verification

**Commands:**
- `.venv/bin/python -m pytest` (fra `backend/`) -- forventet: alle tester bestått, inkludert den nye testen.

**Manual checks:**
- Start backend uten nøkkel. Advarselslinjen om at preferansetolkningen er av, vises én gang med `WARNING:`-prefiks.
- Live med nøkkel er valgfritt (19 betalte kall). Uten live dekker testen INFO-veien.

## Review Triage Log

| # | Kilde | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | Verification Gap | Ingen test sjekker at handleren fra modulimporten skriver til ekte stderr | medium | Alle utskriftstestene bytter handleren ut med `StringIO`; en vanlig `StreamHandler()` ville bestått alle | patch: subprosess-test |
| 2 | Verification Gap, Blind | Ingen test sjekker at `tolk_ventende` faktisk logger INFO-linjene uten preferansetekst | medium | `caplog`-testene i `test_preferansetolkning.py` ser bare på WARNING/ERROR (grep) | patch: ny test |
| 3 | Blind, Edge, VG | README lover «én linje per tekst»; tekster som hoppes over (lås, endret rad, allerede tolket, `main.py:463-469`) gir ingen linje, og «forkastet» mangler | medium | Bekreftet i koden; leser kan tro tolkingen har stoppet | patch: README |
| 4 | Edge | README antyder linjer også for «Prøv igjen», som ikke logger noe | low | Ingen `logger`-kall i forsøksruten (grep); direkte tekstretting | patch: README (gruppe med 3) |
| 5 | Blind, Edge | `WARNING:     ` har fem mellomrom, uvicorn to | low | Stemmer, men formatet er gitt i oppgaven; kodefiks krever egen formatter | avvist (kosmetisk); README-påstanden rettes i 3 |
| 6 | Blind | Advarselstesten bruker en melding koden ikke logger | low | `openrouter.py:327` bruker `"Nettverksfeil mot OpenRouter: %s"` | patch: direkte retting |
| 7 | Blind | KI-loggen siterer prompten med forkortet sti og sier at uavhengig gjennomgang ikke er gjort | low | Sporbarhet; gjennomgangen er gjort nå | patch: KI-logg |
| 8 | Blind | Unntakstekst i WARNING kan lekke URL/header | false | Advarselen fantes og ble vist før via `lastResort`; `test_openrouter.py:494` sjekker nøkkel og tekst | avvist |
| 9 | Blind | `stream`-egenskapen avhenger av rekkefølgen i `__init__` | false | Ingen kaller bruker `setStream`; ingen navngitt skade | avvist |
| 10 | Blind, Edge | Nivået tvinges til INFO, `--log-level` påvirker det ikke | low | `--log-level` setter bare uvicorns loggere; intensjonen er fast INFO | avvist |
| 11 | Blind | Import endrer loggnivået for hele pytest-kjøringen | false | Fravær-sjekkene (`not in caplog.text`) blir strengere, ikke svakere | avvist |
| 12 | Blind, Edge | Doble linjer hvis rotloggeren får handler | low | uvicorns standardoppsett rører ikke rot; `log_cli`/`basicConfig` brukes ikke (grep) | avvist |
| 13 | Edge | `sys.stderr` er `None` under pythonw | low | Ikke en kjøremåte prosjektet støtter; `lastResort` ville feilet likt | avvist |
| 14 | Blind | Modelltabellen sier Sonnet, KI-loggen Opus | false | Tabellen er en anbefaling; brukeren har valgt Opus | avvist |
| 15 | Blind | Statusen `in-review` uten gjennomgang | false | Gjennomgangen kjører i denne økten | avvist (KI-logg i 7) |
| 16 | Blind | Linjenumre i deferred-work blir utdaterte | false | Punktet navngir også seksjonene | avvist |
| 17 | Blind | AGENTS.md og `docs/testing.md` ikke oppdatert | false | Ingen av dem sier noe feil om terminalvisningen | avvist |
