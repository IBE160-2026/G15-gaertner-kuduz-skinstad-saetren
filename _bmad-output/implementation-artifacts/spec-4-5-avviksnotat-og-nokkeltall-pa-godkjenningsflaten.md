---
title: 'Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten'
type: 'feature'
created: '2026-11-17'
status: 'draft'
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

**Problem:** Godkjenningsflatens kandidatkort viser bare navn, kompetanse og kostnad. Turnusansvarlig ser ikke timebelastningen eller ulempebelastningen før hun godkjenner, og får ingen nøytral påminnelse når hun bevisst velger en annen enn den topprangerte (FR12, UX-DR18).

**Approach:** Legg timebelastningslinjen og ulempeindikatoren til kandidatkortet, slik de allerede vises i rangeringstabellen (story 4.2/4.7). Når valgt kandidat ikke har `plass == 1`, vis et nøytralt avviksnotat med kostnad, kompetanse, timebelastning og ulempe side om side for valgt og topprangert kandidat. Godkjenningsendepunktet må da levere en fullt rangert kandidat (`RangertKandidat`), ikke bare `Kandidat`, og topprangerts tall ved siden av.

## Boundaries & Constraints

**Always:**
- `GodkjenningsgrunnlagUt.kandidat` blir `RangertKandidatUt` (var `KandidatUt`). Ruten kjører `ranger(...)` på samme måte som kandidatruten, finner valgt kandidat i resultatet via `ansatt_id`, og bygger den med `rangert_ut`.
- Nytt felt `topprangert: RangertKandidatUt | None`. `None` nøyaktig når valgt kandidats `plass == 1`. Ellers er det kandidaten med `plass == 1` i samme rangering, bygget med samme `rangert_ut`. Bruk `plass`, ikke en egen sammenligning av `totalscore` (de uavrundede totalene er allerede riktig avgjort i `domene/regelmotor`, inkludert likhetsbryting).
- Kandidatkortet viser, i tillegg til det som er der i dag: timebelastningslinjen (som i rangeringstabellen, `warn`-farge ved `hoy_belastning`, aldri `danger`) og ulempeindikatoren (poengsum + kveld/helg/natt-fordeling). Ingen terskel eller fargeskifte på ulempe (UX-DR28).
- Avviksnotatet («Avvik fra anbefalt rangering», stiplet kant, `--color-breadcrumb-bg`) vises bare når `topprangert` ikke er `null`. Det viser kostnad, kompetansenivå, timebelastning og ulempebelastning for valgt og topprangert kandidat, i den rekkefølgen, side om side i én kompakt linje (som mockupen), med navn foran hvert sett med tall. Inkluderer teksten «Turnushjelperen anbefaler, den bestemmer aldri selv.». Blokkerer aldri godkjenningsknappen og antyder aldri at valget er feil (UX-DR23).
- `timebelastningslinje` og `ulempeindikator` (i dag inline JSX i `Kandidatrad` i `Kandidatflate.tsx`) skilles ut som egne komponenter og gjenbrukes uendret i rangeringstabellen, kandidatkortet og begge sidene av avviksnotatet.
- Nye eller endrede koblinger får komponenttester (OP-16, `docs/testing.md`): kandidatkortets nye indikatorer, og avviksnotatets vis/skjul og sammenligningslinje, i `frontend/tester/komponenter/godkjenningsflate.test.tsx`.
- Testdatafasiten tilpasses aldri koden (AV-07). For #4127 uten tolkede preferanser (gjeldende, siden 5.2 ikke er koblet inn): Jonas Bakke er nr. 1 (79,40), Mette Solberg nr. 2 (72,40). Velges Mette, viser avviksnotatet Jonas som topprangert.

**Never:** Endre rangeringsformelen, vektene eller `RangertKandidat`s felt. Endre godkjenningslogikken, `grunnlagsmerke` eller POST-ruten. Story 4.6 (smale skjermer) og Epic 5 (KI-forklaring, utvidelseskolonnen).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Topprangert valgt | #4127, Jonas Bakke (plass 1) | kandidatkort med timebelastningslinje og ulempeindikator; `topprangert` er `null`; ikke noe avviksnotat | — |
| Ikke topprangert valgt | #4127, Mette Solberg (plass 2) | avviksnotat vises: Mette (2 960 kr, nivå 4/4, 16 t, 180 p) og Jonas (2 960 kr, nivå 3/4, 16 t, 40 p) side om side | — |
| Datafeil | som i dag | `DatafeilUt`, ingen kandidat eller topprangert | uendret fra i dag |
| Endret grunnlag før bekreftelse | rangeringen endrer plassering mens flaten er åpen | nytt GET med nytt `grunnlagsmerke`, `plass` og `topprangert` oppdateres fra samme snapshot | uendret fra i dag (P-09) |
| Én gyldig kandidat | bare én Gyldig for vakten | `plass == 1`, `topprangert` er `null` | — |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py`:
  - `GodkjenningsgrunnlagUt.kandidat` endres fra `KandidatUt` til `RangertKandidatUt`. Nytt felt `topprangert: RangertKandidatUt | None`.
  - I `godkjenningsgrunnlag()` (l.~503): etter at `vurdering` er klar (ikke `Datafeil`), kjør `rangert = ranger(vurdering, grunnlag.vakt, grunnlag.tolkede, grunnlag.feilede)` (samme mønster som `kandidater()`, l.~490). Finn `valgt = next((r for r in rangert if r.id == ansatt_id), None)`; `None` gir fortsatt 404 (samme NFR2-begrunnelse som i dag). Bygg `kandidat = rangert_ut(valgt, grunnlag.ansatte_ved_id[ansatt_id], grunnlag.vakt, vurdering.ulempe_per_kandidat[ansatt_id])` — se om `kandidatgrunnlag.py` allerede har et oppslag fra id til `Kandidat`, ellers lag et lite `{k.id: k for k in grunnlag.ansatte}`. `topprangert_r = None if valgt.plass == 1 else next(r for r in rangert if r.plass == 1)`, og bygg `RangertKandidatUt` for den på samme måte når den ikke er `None`.
  - Gjenbruk `rangert_ut` uendret (den tar allerede `RangertKandidat, Kandidat, Vakt, Ulempebelastning`).
- `backend/tester/api/test_godkjenningsgrunnlag.py`:
  - `test_gyldig_kandidat_gir_vakt_og_kandidat` (l.60): nøkkelsettet blir `{"status", "vakt", "kandidat", "topprangert", "grunnlagsmerke"}`.
  - `test_jonas_på_4127_har_nøyaktig_dette_svaret` (l.77): Jonas er `plass: 1`, `topprangert: None`. Legg til en tilsvarende test for Mette (`plass: 2`, `topprangert` er Jonas' fulle `RangertKandidatUt`, uavrundede tall fra `test_rangering.py`/`FAKTORER_4127`).
  - `test_kandidaten_har_bare_kontraktsfeltene` (l.168): nøkkelsettet for `kandidat` blir `RANGERT_FELT` (allerede definert i `test_kandidater.py`, importer eller dupliser).
  - `test_svaret_for_gyldig_nevner_ingen_utelukket` (l.157): sjekk også at `topprangert`, der den finnes, ikke nevner noen utelukket.
  - Ny test: `topprangert` er nøyaktig `None` når valgt er nr. 1, og nøyaktig nr. 1-kandidaten (ikke en kopi av valgt) når valgt ikke er nr. 1.
- `frontend/src/api.ts`:
  - `Godkjenningssvar`s `"ok"`-gren: `kandidat: Kandidat` → `kandidat: RangertKandidat`, nytt felt `topprangert: RangertKandidat | null`.
- `frontend/src/godkjenning.ts`:
  - `Godkjenningstilstand`s `"klar"`-gren får `kandidat: RangertKandidat` og `topprangert: RangertKandidat | null`, satt i `tilstandFraSvar`.
  - `frontend/tester/godkjenning.test.mjs`: oppdater fixturene til `RangertKandidat`-formen og `topprangert`.
- `frontend/src/komponenter/Kandidatflate.tsx`:
  - Skill ut `Belastningslinje({ prosent, høy }: { prosent: number; høy: boolean })` og `Ulempeindikator({ ulempe }: { ulempe: Ulempebelastning })` fra dagens inline JSX i `Kandidatrad` (linjene med `belastningslinje`/`belastningsfyll` og `kandidat-ulempe`). Eksporter dem (de brukes fra `Godkjenningsflate.tsx`), og bruk dem uendret i `Kandidatrad`.
- `frontend/src/komponenter/Godkjenningsflate.tsx`:
  - Kandidatkortet (`<section className="panel kandidatkort">`, l.157): legg til `Belastningslinje` og `Ulempeindikator` fra `tilstand.kandidat` etter `Kostnadsvisning`.
  - Ny komponent `Avviksnotat({ valgt, topprangert })`, vist mellom kandidatkortet og bekreftelsesboksen, bare når `tilstand.topprangert` ikke er `null`.
- `frontend/src/tekster.ts`: i `godkjenning`-seksjonen (l.157), legg til teksten for avviksnotatets overskrift, sammenligningslinjen (mal per kandidat: navn, kostnad, nivå, timer, ulempe) og «Turnushjelperen anbefaler, den bestemmer aldri selv.».
- `frontend/src/stil/app.css`: `.avviksnotat` som `.ekskludert-boks` (`border: var(--border-width) dashed var(--color-border); background: var(--color-breadcrumb-bg);`), med en liten overskriftsstil for «Avvik fra anbefalt rangering» (som `.lbl` i mockupen: `accent`-farge, store bokstaver). Bare tokens (AV-13).
- `frontend/tester/komponenter/godkjenningsflate.test.tsx`: utvid med Jonas (nr. 1, ingen notat, kort viser begge indikatorene) og Mette (nr. 2, notat med riktig sammenligningslinje), etter mønsteret i `hjelpere.ts`.
- `docs/testing.md`: ny rad i komponenttest-tabellen for de to nye flytene, og et nytt avsnitt «Story 4.5 – avviksnotat og nøkkeltall» etter mønsteret fra 4.3/4.4.
- Ikke endre: `domene/regelmotor/rangering.py`, `domene/porter/rangering.py`, `kandidater()`-ruten, POST-ruten for godkjenning, `grunnlagsmerke`.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/adaptere/api/main.py` — `RangertKandidatUt` og `topprangert` i `GodkjenningsgrunnlagUt`, bygget i `godkjenningsgrunnlag()`.
- [ ] `backend/tester/api/test_godkjenningsgrunnlag.py` — oppdater de fire berørte testene og legg til testen for `topprangert`.
- [ ] `frontend/src/api.ts`, `godkjenning.ts`, `tester/godkjenning.test.mjs` — ny type og felt.
- [ ] `frontend/src/komponenter/Kandidatflate.tsx` — skill ut `Belastningslinje` og `Ulempeindikator`.
- [ ] `frontend/src/komponenter/Godkjenningsflate.tsx`, `tekster.ts`, `stil/app.css` — nøkkeltall på kortet og `Avviksnotat`.
- [ ] `frontend/tester/komponenter/godkjenningsflate.test.tsx` — komponenttester for begge flytene (OP-16).
- [ ] `docs/testing.md`, `docs/ki-logg/<dato>-avviksnotat.md`, `docs/emne/vurderingsmatrise.md`, `epic-4-context.md` — dokumenter flyt, KI-arbeid, bevis og status.

**Acceptance Criteria:**
- Given #4127 og Jonas Bakke valgt, when godkjenningsflaten vises, then kandidatkortet viser timebelastningslinjen og ulempeindikatoren, og ingen avviksnotat vises.
- Given #4127 og Mette Solberg valgt, when flaten vises, then avviksnotatet viser kostnad, kompetansenivå, timebelastning og ulempe for Mette og Jonas side om side, med teksten «Turnushjelperen anbefaler, den bestemmer aldri selv.», og godkjenningsknappen er fortsatt aktiv.
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd run test` kjøres, then alt består.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **Hvorfor `plass` og ikke `totalscore`:** Epic 4-konteksten påpeker at kostnad er `float`, så nær-like totaler kan i prinsippet avvike i siste siffer uten å utløse likhetsbrytingen på ansatt-ID. `plass` er allerede regnet ferdig i domenekjernen med nøyaktige `Fraction`-verdier og den riktige likhetsbrytingen, så å sammenligne `plass == 1` her er korrekt og unngår å gjenta den logikken i API- eller frontend-laget.
- **Sammenligningslinjens form:** følger mockupen (`key-godkjenning.html`, `.deviation-note .compare`) med ekte, gjeldende fasittall: «Mette Solberg: 2 960,00 kr, Nivå 4/4, 16 t i startuken, 180 ulempepoeng · Jonas Bakke: 2 960,00 kr, Nivå 3/4, 16 t i startuken, 40 ulempepoeng.» Valgt kandidat står først. Mockupens eksempel har 75 preferansepoeng for begge fordi den antar tolkede preferanser; det er ikke koblet inn før story 5.2, så preferansepoeng tas ikke med i sammenligningen ennå.

## Verification

**Commands:**
- `backend/`: `.venv\Scripts\python -m pytest`. Forventet: alt består, også import-linter.
- `frontend/`: `npm.cmd run build` og `npm.cmd run test`. Forventet: begge består (`node --test` og Vitest).

**Manual checks (docs/testing.md):** 1080/960/680/1600 px, tastatur og fokus, farger (tokens, ikke rå verdier), større skrift, ekte backend mot #4127 (Jonas og Mette).
