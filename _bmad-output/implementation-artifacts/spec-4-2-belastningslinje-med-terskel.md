---
title: 'Story 4.2: Arbeidsbelastningslinje med terskel'
type: 'feature'
created: '2026-11-15'
status: 'done'
baseline_commit: 'f72013cad9103090ee691639465d72e302e16b7b'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatlisten viser timer i uka som tall (4.1), men turnusansvarlig ser ikke med et blikk hvem som nærmer seg for mye (FR8). Grensen for høy belastning (minst 32,4 t, P-04/K-02) er vedtatt, men ikke implementert eller testet.

**Approach:** Domenekjernen regner deterministisk ut Timebelastning som prosent av 36 t og om Kandidaten er på eller over 32,4 t. Kandidatsvaret sender begge verdiene, og kandidatlisten viser en 110×7px linje fylt proporsjonalt, i `accent` under grensen og `warn` ved og over.

## Boundaries & Constraints

**Always:** Terskelen 32,4 t sammenlignes som eksakt `timedelta` (1944 minutter, heltallsregning, ikke flyttall) mot uavrundet tid, ikke mot det viste tallet (P-04). Grunnlaget er `timer_i_startuka` fra 4.1 (uten Vakten som bemannes, P-02). Fargene er bare `accent` og `warn` fra tokens; aldri rød. 110×7px blir egne tokens (AV-13). Domenet er ren Python uten KI (NFR1, AD-1, AD-2). Linjen vises bare for Gyldige kandidater. Fyllet kuttes ved 100 % av linja; tallet i teksten viser faktisk verdi.

**Never:** Ikke ta med ulempebelastning i linja (4.7) og ikke gi 90 %-grensen poeng i Rangeringen (4.4). Ingen kostnad (4.3), rangering (4.4) eller nøkkeltall (4.5). Ikke endre `minutter_i_uka`-kontrakten, regelmotorens vurdering av hvem som er gyldig eller dataskjemaet. Ikke lagre verdiene.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ingen vakter | 0:00 | 0 %, ikke høy, tom linje | N/A |
| Ingrid i #4127 | 32:00 | 88,9 %, ikke høy, `accent` | N/A |
| Rett under | 32:23 (og 32:23:59) | ikke høy, `accent` | N/A |
| Nøyaktig på | 32:24 | høy, `warn` | N/A |
| Rett over | 32:25 | høy, `warn` | N/A |
| Normaluka og mer | 36:00 / 40:00 | 100 % / 111,1 %, høy; fyll kuttes ved 100 % | N/A |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/timer_i_uka.py` -- `timer_i_startuka` (timedelta) og `minutter_i_uka`; gjenbrukes, endres ikke.
- `backend/domene/regelmotor/` -- ny modul `timebelastning.py` (faller inn under import-linter-kontrakten) med konstantene 36 t og 32,4 t og funksjon fra `timedelta` til prosent og høy-flagg.
- `backend/adaptere/api/main.py` -- `KandidatUt` (~137) og de to stedene den bygges (~332 og ~371, kandidatruten og `godkjenningsgrunnlag`). Legg til to felt ved siden av `minutter_i_uka`; endre ikke `ulempebelastning`.
- `frontend/src/api.ts` -- `Kandidat`-typen (~59) får feltene.
- `frontend/src/komponenter/Kandidatflate.tsx` -- `<li>` i kandidatlisten (~163); linja settes ved `timer-i-uka`, før ulempeblokken. Ulempeblokken røres ikke.
- `frontend/src/tekster.ts`, `frontend/src/stil/app.css`, `frontend/src/stil/tokens.css` -- tekst, stil og tokens for 110×7px og radius. Rå størrelser bare i tokens (AV-13).
- `backend/tester/regelmotor/test_timer_i_uka.py` -- mønster for grensetester. `backend/tester/api/test_kandidater.py` og `test_godkjenningsgrunnlag.py` -- API-mønster; sistnevnte kontrollerer kontraktsfeltene og må utvides.
- `frontend/tester/komponenter/kandidatflate.test.tsx` -- mønster for komponenttester.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/regelmotor/timebelastning.py` -- ren funksjon: prosent av 36 t (uavrundet) og `høy` fra eksakt sammenligning mot 32,4 t -- FR8, P-04
- [x] `backend/tester/regelmotor/test_timebelastning.py` -- alle rader i matrisen, inkludert 32:23:59, 32:24:00 og gjentatt kjøring -- grensetester er beviset (AGENTS.md)
- [x] `backend/adaptere/api/main.py` -- felt `timebelastning_prosent` og `hoy_belastning` på `KandidatUt`, satt begge steder -- liten endring
- [x] `backend/tester/api/` -- Ingrid i #4127 gir 88,9 % og ikke høy; en kandidat på 32:24 gir høy; godkjenningsgrunnlaget har feltene
- [x] `frontend/src/` -- type, linje (110×7px, fyll i `accent`/`warn`, kuttet ved 100 %), tokens og tekster; skjermleser får «høy belastning» som tekst, ikke bare farge
- [x] `frontend/tester/komponenter/kandidatflate.test.tsx` -- linja med riktig fargeklasse og bredde for under, på og over grensen, og at 4.1-verdien og ulempeblokken er uendret
- [x] `docs/ki-logg/`, `docs/emne/vurderingsmatrise.md`, `docs/beslutninger/avklaringspunkter.md` (K-02: visning og test gjort) og sesjonsloggen -- sporbar kvalitetssikring

**Acceptance Criteria:**
- Given en Kandidat under 32,4 t før avrunding (32:23, Ingrid 32:00), when linja vises, then er den 110×7px, fylt proporsjonalt og i `accent`.
- Given en Kandidat på minst 32,4 t (32:24), when linja vises, then er fyllet `warn`, aldri rødt, og tallet ved siden av viser minuttene.
- Given samme grunnlag, when beregningen kjøres på nytt, then er prosent og høy-flagg identiske.
- Given kandidatflaten ved smale og brede vinduer, when raden vises, then overlapper ikke linja navn, tag, timer, ulempeblokk eller «Velg», og ingenting klippes (AV-17).

## Implementation Notes

## Spec Change Log

## Review Triage Log

| Kilde | Funn | Verdikt | Rute | Evidens |
|---|---|---|---|---|
| verification-gap | `hoy_belastning=True` testes aldri via godkjenningsgrunnlaget | medium | patch | Bare Jonas (16 t, `False`) og nøkkelsett testes der. Ny test med Ingrid +23/+24 min i `test_godkjenningsgrunnlag.py`. |
| blind-hunter | Eksakt float-likhet `100 * 16 / 36` i API-testen | low | avvist | Testen består, inngangen er fast, og en endring i regnerekkefølgen ville feile synlig. |
| blind-hunter | `belastning()` kaller `timer_i_startuka` og `minutter_i_uka` hver for seg | low | avvist | Begge er rene funksjoner av samme input og kan ikke avvike. Fiks ville kreve endring i 4.1-kontrakten, som spesifikasjonen forbyr. |
| blind-hunter | Determinismetester sammenligner funksjon med seg selv | low | avvist | Funksjonen er ren; testen er spesifisert («kjøres på nytt»). Ingen skjult tilstand å teste. |
| blind-hunter / edge-case | Negativ `timedelta` i `timebelastning` | false | avvist | `timer_i_startuka` summerer vakter med slutt etter start og kan ikke gi negativ verdi. |
| blind-hunter / edge-case | Hjelpefunksjonen kan velte Ingrids gyldighet, `next()` gir `StopIteration` | false | avvist | Testene består og forlengelsen er 23–25 min. Mangler Ingrid, feiler testen uansett. |
| blind-hunter | Kontrast mellom `--color-tag-bg` og `accent`/`warn`, ingen tekst for normal belastning | maybe-false | defer | Hører til manuell fargekontroll (OP-16) som spesifikasjonen allerede krever; tallet i raden er 4.1-teksten. |
| blind-hunter | Skjøre `startsWith`-sjekker på bredde | low | avvist | Prefikset er presist nok til å skille under/på/over, og sjekken er stabil i jsdom. |
| blind-hunter | `hoy_belastning` uten «ø» | false | avvist | Navnet er fastsatt i spesifikasjonen. |
| blind-hunter / edge-case | Fast 110 px kan gi overflow ved svært smale vinduer | maybe-false | defer | Minste vindu i AV-17 er 680 px. Avgjøres av manuell layoutkontroll som står i Verification. |
| blind-hunter | Dokumentasjonspåstander og statusrekkefølge | low | avvist | KI-loggen oppdateres med gjennomgangen. |
| edge-case | NaN/null fra backend gir ugyldig bredde | false | avvist | Backend-typen er `float`; en kontraktsbrudd-feil skal være synlig, ikke maskeres. |
| edge-case | Testhjelperen regner `minutter >= 1944` i frontend | low | avvist | Fixtureren etterligner backend; ingen produksjonskode sammenligner mot terskelen. |

## Design Notes

Terskelen er `timedelta(minutes=36*60*9//10)` = 1944 min. En float-sammenligning (`0.9 * 36`) kan gi 32,400000000000006, og 32:24 ville da kunne falle under grensen. Uavrundet tid brukes fordi 32:23:59 skal være under grensen. 4.1 sender `minutter_i_uka` ned-rundet, så backend regner fra `timedelta` og sender flagget ferdig. Frontend skal aldri sammenligne mot 32,4 selv.

## Verification

**Commands:**
- `cd backend && .venv/bin/python -m pytest` -- expected: alle tester består
- `cd frontend && npm run build && npm run test` -- expected: bygg og tester består (én kjøring om gangen, se AGENTS.md)

**Manual checks (if no CLI):**
- Ekte backend med testdata (docs/testing.md, OP-16): #4127 viser Ingrid 32:00 med `accent`-linje og #4189 er uendret. Layout ved flere vindusbredder, også smale (AV-17), farger (`accent`/`warn`, aldri rød), tastaturfokus på «Velg» og at linja ikke tar fokus. Skjermleser er valgfri.

**Manuell kontroll (docs/testing.md):** Ragnhild, 2026-11-15, Safari (versjon ikke notert) på macOS, story 4.2
1. 1080, 960, 680 og 1600 px: bestått (360 px som regresjon: bestått)
2. Tastatur og fokus: bestått, fokus stopper bare på «Velg», aldri på linja
3. Farger: bestått i lys drakt. Appen har ingen mørk drakt (DESIGN.md: «ikke dark-mode-først»), så mørk drakt er ikke relevant
4. Større skrift: bestått
5. Ekte backend: bestått. Ingrid 32:00 (`accent`), 32:23 (`accent`), 32:24 og 32:25 (`warn`), de andre radene `accent`. Ulempeblokken uendret, #4189 uendret
Målrettet kontroll av flyt uten komponenttest: grensen 32:23/32:24/32:25 mot ekte backend, bestått
Ikke relevant: mørk drakt, se punkt 3
Ikke avgjort: VoiceOver leste «Høy belastning» bokstav for bokstav. Testeren er ikke vant til VoiceOver, så det kan skyldes bruken og ikke koden. Valgfri kontroll, ikke krav for 4.2.
