---
title: 'Story 2.4: Filtrere på 35-timersregelen (ukentlig fri)'
type: 'feature'
created: '2026-11-11'
status: 'done'
baseline_commit: 'd4a0b1a1b3966a808893551180f67b495e912950'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Etter 2.3 er listen filtrert på kompetanse, kolliderende vakt og 11 t. En Ansatt som ville mistet den ukentlige fritiden, vises fortsatt som Kandidat (FR5, AV-04). Fasiten utelukker Anders Strand (#4127, 34 t) og Line Moe (#4189, 32 t) på denne regelen.

**Approach:** Legg 35-timersregelen inn som regel nummer fire i `REGLER`, med hele berørte kalenderuker som vindu (vedtak A5). Datafeilsjekken arves. Den midlertidige merknaden fjernes.

## Boundaries & Constraints

**Always:**
- Berørte uker: kalenderukene (mandag 00:00 til neste mandag 00:00 i `Europe/Oslo`) som det halvåpne `[start, slutt)` til Vakten overlapper. En Vakt som slutter nøyaktig mandag 00:00, berører bare én uke. Krysser Vakten ukeskiftet, sjekkes begge.
- For hver berørt uke: ta unionen av Kandidatens gyldige vakter og Vakten, klippet til uka. Lengste sammenhengende fri regnes også fra ukestart til første vakt og fra siste vakt til ukeslutt. Fri over ukeskiftet teller bare med delen innenfor uka. Under 35 t 0 min i én av ukene gir utelukkelse med årsaken «35-timersregelen». Nøyaktig 35 t er gyldig. Dette er samme semantikk som `bryter_trettifem_timer` i fasiten.
- Alt regnes i faktisk forløpt tid (UTC). Ukegrensene settes på veggklokka i Oslo og regnes så om til UTC, så uker med sommertidsskifte har 167 eller 169 timer.
- Vindu: `[mandag i første berørte uke, mandag etter siste berørte uke)`, i UTC. Det erstatter `[ASSUMPTION]` i epics: ligger en berørt uke utenfor `[historikkstart, datagrense]`, gir det `Datafeil` (P-08). Ukeslutt nøyaktig på datagrensen er gyldig. Det gjelder #4189 (uka slutter 05.10 kl. 00:00).
- Ren regelmotor, samme input gir samme output, og fasiten tilpasses aldri koden (AV-07). Reglene er ikke full juridisk kontroll (AV-04, OP-01).

**Beslutninger (Ragnhild, 2026-11-11, OP-14):**
- **Overlapp og 35 t (A):** En egen vakt som overlapper Vakten, telles med i unionen, som fasithjelperen `bryter_trettifem_timer`. En Kandidat med kolliderende vakt kan da også få «35-timersregelen». Det skiller seg fra 1A for 11 t, men følger fasiten (AV-07). Seeden har ingen slike tilfeller.
- **Tom liste før 2.6 (B):** Når listen er tom, viser flaten teksten «Ingen gyldige kandidater for denne vakten.» i `meta`-stil, uten ikon og uten `danger`. API-et er uendret (`status: "ok"`, tom liste). 2.6 erstatter teksten med tomtilstanden og API-statusen.
- **Lengde:** Spesifikasjonen er på omtrent 2 800 tokens. Den beholdes hel, fordi den har ett mål.

**Never:** Ekskludert-boks (2.5), API-status `ingen_gyldige_kandidater` eller full tomtilstand med ikon og forklaring (2.6), rangering eller KI. Endring i skjema eller testdata. Å avsløre i svaret hvilken vakt eller uke som bryter regelen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Nøyaktig 35 t | lengste fri i uka med Vakten = 35:00 | ikke utelukket | — |
| 34:59 | lengste fri = 34:59 | utelukket, «35-timersregelen» | — |
| Krysser ukeskiftet | natt søndag 23–mandag 07, brudd bare i den ene uka (test begge retninger) | utelukket | — |
| Slutter mandag 00:00 | Vakten slutter nøyaktig ved ukeskiftet | bare den ene uka sjekkes | — |
| Fri over ukeskiftet | 40 t fri lørdag–tirsdag, men under 35 t på hver side | utelukket | — |
| Vårskiftet (167 t) | uke 23.–30.03.2026, veggklokke 35 t = 34 faktiske | utelukket | — |
| Høstskiftet (169 t) | uke 19.–26.10.2026, veggklokke 34 t = 35 faktiske | ikke utelukket | — |
| Ingen egne vakter | bare Vakten i uka | ikke utelukket | — |
| #4127 | seed | 4 gyldige: Jonas, Mette, Thomas, Ingrid | — |
| #4189 | seed | 0 gyldige, 24 utelukket | — |
| Uke etter datagrensen | Vakt der berørt uke slutter etter `datagrense` | `Datafeil` | ingen liste |
| Ugyldig vakt i uka | `start >= slutt` i berørt uke, utenfor ±11 t | `Datafeil` | ingen liste |
| Ugyldig vakt i uka før | samme, i uka før | vurderes normalt | — |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/trettifem_timer.py` (ny): `ÅRSAK = "35-timersregelen"`, `MINSTE_FRI = timedelta(hours=35)`, `OSLO = ZoneInfo("Europe/Oslo")`, `berørte_uker(vakt)`, `lengste_fri(...)`, `bryter_trettifem_timer(kandidat, vakt)` og `vindu(vakt)`. Formen følger `elleve_timer.py`. Ukestart: `t.astimezone(OSLO).date()`, trekk fra `weekday()` og bruk `datetime.combine(mandag, time(0), tzinfo=OSLO)`. Neste uke er `combine(mandag + 7 dager)`, ikke `+ timedelta` på en tid med tidssone. Dekk sammenligninger og differanser med `.astimezone(UTC)`.
- `backend/domene/regelmotor/elleve_timer.py:26`: `_gyldig_tidsrom` trengs også i 35-timersregelen. Gjør den offentlig (`gyldig_tidsrom`) og importer den. Ikke dupliser den. Ugyldige vakter hoppes over i `bryter`, med samme docstring-forutsetning som `bryter_elleve_timer`.
- `backend/domene/regelmotor/vurdering.py:55`: regel fire i `REGLER` med `vaktkrav`/`kandidatkrav` som tomme lambdaer. Ellers ingen endring. Docstringen nevner allerede 2.4.
- `backend/tester/regelmotor/test_35_timersregelen.py` (ny): hele matrisen, determinisme og vindus-datafeil. Bruk hjelpemønsteret i `test_11_timersregelen.py`. Sommertidstestene sender egne `historikkstart` og `datagrense`, og begge tidene i en sammenligning bruker samme `ZoneInfo`.
- `backend/tester/regelmotor/test_kompetanse.py`, `test_kolliderende_vakt.py` og `test_11_timersregelen.py`: tester som setter `regler=REGLER[:n]` eller teller reglene, må kanskje oppdateres. Endre bare det regel fire faktisk påvirker.
- `backend/tester/api/test_kandidater.py`: `IMPLEMENTERTE_REGLER` (l.32) får `"trettifem-timer"`, 19/23 (l.62) blir 20/24 og docstringen (l.1–7) oppdateres. Test med `assert` at #4189 gir tom liste og `status: "ok"`, slik API-et er til 2.6.
- `frontend/src/tekster.ts:96`, `frontend/src/komponenter/Kandidatflate.tsx:104` og `frontend/tester/kandidater.test.mjs:75`: fjern `midlertidigMerknad`, og legg til teksten for tom liste (beslutning B) i `tekster.ts`. Vis den i `Kandidatliste` når `kandidater` er tom. Testen skal vise at merknaden er borte, og at teksten for tom liste skiller seg fra teksten for lasting, feil og datafeil.
- `README.md:171–178`: regelstatus og tall 4/0.
- Ikke endre: `kandidatgrunnlag.py`, `main.py`, `typer.py`, testdata eller `FASIT`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/regelmotor/trettifem_timer.py` og `elleve_timer.py`: regel, årsak, ukeberegning og vindu i UTC (FR5).
- [x] `backend/domene/regelmotor/vurdering.py`: regel fire i `REGLER`.
- [x] `backend/tester/regelmotor/test_35_timersregelen.py`: hele matrisen. Det er kravet i AC-en i epics.
- [x] `backend/tester/api/test_kandidater.py` og de andre regelmotortestene: fasiten 4/0 mot `FASIT` (AV-07) og datafeil når uka slutter etter datagrensen.
- [x] `frontend/src/tekster.ts`, `Kandidatflate.tsx`, `frontend/tester/kandidater.test.mjs` og `README.md`: merknaden fjernes, teksten for tom liste legges til, og regelstatusen oppdateres.
- [x] `docs/ki-logg/2026-11-11-35-timersregelen.md`, `docs/emne/vurderingsmatrise.md` og `epic-2-context.md`: KI-logg med mutasjonene, bevis og at 2.4 er implementert.
- [x] `docs/beslutninger/avklaringspunkter.md` (AV-04 og §11): grensetestene for 35 t finnes nå. Uke som vindu er bygget etter A5. `[ASSUMPTION]` i epics er erstattet av datafeil (P-08). Planleggingsdokumentene endres ikke.

**Acceptance Criteria:**
- Given en valgt vakt, when kandidatflaten lastes, then listen er filtrert på alle fire reglene, og merknaden er borte.
- Given en mutasjon fra `<` til `<=` i grensen på 35 t, when `pytest` kjøres, then minst én test feiler.
- Given en mutasjon som fjerner UTC-omregningen, eller som setter ukegrensene i UTC i stedet for Oslo-tid, when `pytest` kjøres, then minst én test feiler. Mutasjonene dokumenteres i KI-loggen.
- Given hele pakken, when `pytest`, `npm run build` og `npm test` kjøres, then alt består.

## Design Notes

- **Eksempel:** #4127 (søndag 27.09 07–15) berører uka [21.09, 28.09), og det samlede vinduet blir [21.09 00:00, 28.09 02:00). #4189 (mandag 28.09 23–07) berører uka [28.09, 05.10), og vinduet slutter nøyaktig på datagrensen. Historikkstarten 24.08 er en mandag, så ingen vakt i perioden treffer den nedre grensen.

## Verification

**Commands:**
- `backend/`: `.venv/bin/python -m pytest` (Windows: `.venv\Scripts\python`). Forventet: alt består, også import-linter.
- `frontend/`: `npm run build` og `npm test` (Windows PowerShell: `npm.cmd`). Forventet: begge består.

**Manual checks:**
- Nettleserkontroll: #4127 viser Ingrid Dahl, Jonas Bakke, Mette Solberg og Thomas Nygård uten merknad. #4189 viser «Ingen gyldige kandidater for denne vakten.» uten ikon og rødfarge.

## Implementation Notes

- 2026-11-12: Ragnhild gjorde nettleserkontrollen 2026-11-12: #4127 viste Ingrid Dahl, Jonas Bakke, Mette Solberg og Thomas Nygård uten merknad, og #4189 viste «Ingen gyldige kandidater for denne vakten.» uten ikon og rødfarge.

## Spec Change Log

## Review Triage Log

Tre uavhengige gjennomgangsagenter (blind-hunter, edge-case-hunter og verification-gap, alle Opus 5.5) gikk gjennom diffen fra `d4a0b1a` 2026-11-12. Ingen av funnene ga intent_gap eller bad_spec, så det ble ingen ny runde.

| # | Funn | Dom | Rute |
|---|---|---|---|
| 1 | Ingen test har en egen vakt som ligger helt inne i en annen. Mutasjonen `fri_fra = slutt` i `lengste_fri` overlever (verification-gap, blind-hunter) | medium: med beslutning A kan en Kandidat med kolliderende vakt mangle «35-timersregelen» i årsakene som 2.5 bygger på. Ingen eksisterende test sorterer en vakt først som slutter etter den neste | patch |
| 2 | Teksten for tom liste mangler `role="status"`, mens lastingen i samme klasse har den (blind-hunter, edge-case-hunter) | low: `Kandidatflate.tsx:107` har `role="status"`, den nye grenen ikke. Skjermlesere kunngjør da ikke at listen er tom. Rettelsen er ett attributt | patch |
| 3 | Grenen for tom liste i React testes bare ved å lese kildeteksten (verification-gap, blind-hunter) | medium: ingen test rendrer komponenter (`kandidater-bunt.ts` bunter bare `src/kandidater` og `src/api`). Snudd betingelse ville gått gjennom | defer: krever oppsett for komponenttester. Nettleserkontrollen må gjøres før `done` |
| 4 | AGENTS.md sier fortsatt «den første harde regelen (kompetanse-minstekrav)» (blind-hunter) | low: stemmer, men filen er agentkontekst | defer |
| 5 | Ingen test viser at seeden aldri gir én Ansatt flere årsaker (blind-hunter) | low: kontrollert manuelt 2026-11-12 med `vurder_kandidater` på seeden: #4127 4/20 og #4189 0/24, ingen med mer enn én årsak. Hører til 2.5, som teller per regel | avvist |
| 6 | `hent(...)["kandidater"][0]` i `test_egen_vakt_før_periodestart_som_overlapper_utelukker` gir `IndexError` ved tom liste (blind-hunter, edge-case-hunter) | low: testen feiler uansett høylytt. En vakt-guard tilfører bare kompleksitet | avvist |
| 7 | `gyldig_på_4127()` brukes i tester som kan ha flyttet vakten (blind-hunter) | false: testene på l.300 og l.320 flytter ikke #4127, bare tildelte vakter legges til | avvist |
| 8 | `bryter_trettifem_timer` sjekker ikke selve Vakten ved direkte kall (edge-case-hunter) | low: `vurder_kandidater` gir datafeil for ugyldig Vakt før reglene kjører. Direkte kall fra Epic 3 er hypotetisk og er nevnt i docstringen, som i `bryter_elleve_timer` | avvist |
| 9 | Ny ID hopper over OP-13 (blind-hunter) | false: OP-13 er tatt av Johannes for story 3.1 (Ragnhild, 2026-11-12) | avvist |
| 10 | «OP-12» står fortsatt i sesjonsloggen fra 2026-11-11 og i spesifikasjonen (blind-hunter) | low: §11 i avklaringspunktene retter det. Historiske logger og den frosne delen endres ikke av agenten | avvist |
| 11 | Ingen sesjonslogg for implementeringen, `issues.md` er ikke oppdatert, sprintstatus og spesifikasjonen har ulik status, og triageloggen mangler (blind-hunter) | false: dette er senere steg i samme `bmad-build`-økt, ikke feil i diffen | avvist |
