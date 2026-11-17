---
title: 'Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten'
type: 'feature'
created: '2026-11-17'
status: 'done'
baseline_commit: 'edd41341c753b6967ee03b67a3404380f34e9dfb'
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
- Kandidatkortet viser timebelastningslinjen med synlig timetall og forståelig skjermlesertekst, som i rangeringstabellen (`warn`-farge og tekstvarsel ved `hoy_belastning`, aldri `danger`), og ulempeindikatoren (poengsum + kveld/helg/natt-fordeling). Ingen terskel eller fargeskifte på ulempe (UX-DR28).
- Avviksnotatet («Avvik fra anbefalt rangering», stiplet kant, `--color-breadcrumb-bg`) vises bare når `topprangert` ikke er `null`. Det viser kostnad, kompetansenivå, timebelastning og ulempebelastning for valgt og topprangert kandidat, i den rekkefølgen, som to kompakte kandidatgrupper side om side, med navn foran hvert sett med tall; innholdet kan brytes over flere linjer. Inkluderer teksten «Turnushjelperen anbefaler, den bestemmer aldri selv.». Blokkerer aldri godkjenningsknappen og antyder aldri at valget er feil (UX-DR23).
- Timebelastning med timetall og `ulempeindikator` (i dag inline JSX i `Kandidatrad` i `Kandidatflate.tsx`) skilles ut og gjenbrukes i rangeringstabellen, kandidatkortet og begge kandidatgruppene i avviksnotatet. Hver gruppe har navn, kostnad, nivå, timebelastning og ulempeindikator med fordeling; verdiene trenger ikke utgjøre én sammenhengende tekstnode.
- Nye eller endrede koblinger får komponenttester (OP-16, `docs/testing.md`): kandidatkortets nye indikatorer, og avviksnotatets vis/skjul og sammenligningslinje, i `frontend/tester/komponenter/godkjenningsflate.test.tsx`.
- Testdatafasiten tilpasses aldri koden (AV-07). For #4127 i et kontrollert grunnlag uten lagrede tolkninger: Jonas Bakke er nr. 1 (79,40), Mette Solberg nr. 2 (72,40). Velges Mette, viser avviksnotatet Jonas som topprangert. Lagrede tolkninger fra 5.1 brukes allerede i rangeringen og kan endre rekkefølgen (P-05).

**Never:** Endre rangeringsformelen, vektene eller `RangertKandidat`s felt. Endre godkjenningslogikken, `grunnlagsmerke` eller POST-ruten. Story 4.6 (smale skjermer) og Epic 5 (KI-forklaring, utvidelseskolonnen).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Topprangert valgt | #4127, Jonas Bakke (plass 1) | kandidatkort med timebelastningslinje og ulempeindikator; `topprangert` er `null`; ikke noe avviksnotat | — |
| Ikke topprangert valgt | #4127, Mette Solberg (plass 2) | avviksnotat vises: Mette (2 960 kr, nivå 4/4, 16 t, 180 p) og Jonas (2 960 kr, nivå 3/4, 16 t, 40 p) side om side | — |
| Datafeil | som i dag | `DatafeilUt`, ingen kandidat eller topprangert | uendret fra i dag |
| Endret grunnlag før bekreftelse | rangeringen endrer plassering mens flaten er åpen; brukeren bekrefter | POST svarer `endret_grunnlag`; nytt GET gir nytt `grunnlagsmerke`, `plass` og `topprangert` fra samme snapshot, og ny bekreftelse kreves | uendret fra i dag (P-09); ingen automatisk oppdatering før bekreftelsesforsøket |
| Én gyldig kandidat | bare én Gyldig for vakten | `plass == 1`, `topprangert` er `null` | — |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py`:
  - `GodkjenningsgrunnlagUt.kandidat` endres fra `KandidatUt` til `RangertKandidatUt`. Nytt felt `topprangert: RangertKandidatUt | None`.
  - I `godkjenningsgrunnlag()` (l.~503): den eksisterende linjen `kandidat = next((k for k in vurdering.gyldige if k.id == ansatt_id), None)` (l.~519) avgjør fortsatt 404 som i dag — ikke endre den grenen. Når `kandidat` ikke er `None`: kjør `rangert = ranger(vurdering, grunnlag.vakt, grunnlag.tolkede, grunnlag.feilede)` (samme mønster som `kandidater()`, l.~490), og bygg `gyldige = {k.id: k for k in vurdering.gyldige}` lokalt (samme uttrykk som allerede brukes i `kandidater()`, l.~489) for oppslag fra id til `Kandidat`. Siden `ranger()` bare rangerer `vurdering.gyldige`, og `ansatt_id` allerede er bekreftet der, finnes den garantert i `rangert`: `valgt = next(r for r in rangert if r.id == ansatt_id)`, uten en `None`-gren — det er ikke en ny feiltilstand. Bygg `kandidat = rangert_ut(valgt, gyldige[ansatt_id], grunnlag.vakt, vurdering.ulempe_per_kandidat[ansatt_id])`. `topprangert_r = None if valgt.plass == 1 else next(r for r in rangert if r.plass == 1)`, og bygg `RangertKandidatUt` for den på samme måte (med `gyldige[topprangert_r.id]`) når den ikke er `None`.
  - Gjenbruk `rangert_ut` uendret (den tar allerede `RangertKandidat, Kandidat, Vakt, Ulempebelastning`).
- `backend/tester/api/test_godkjenningsgrunnlag.py`:
  - `test_gyldig_kandidat_gir_vakt_og_kandidat` (l.60): nøkkelsettet blir `{"status", "vakt", "kandidat", "topprangert", "grunnlagsmerke"}`.
  - `test_jonas_på_4127_har_nøyaktig_dette_svaret` (l.77): Jonas er `plass: 1`, `topprangert: None`. Legg til en tilsvarende test for Mette (`plass: 2`, `topprangert` er Jonas' fulle `RangertKandidatUt`, uavrundede tall fra `test_rangering.py`/`FAKTORER_4127`).
  - `test_kandidaten_har_bare_kontraktsfeltene` (l.168): nøkkelsettet for `kandidat` blir `RANGERT_FELT` (allerede definert i `test_kandidater.py`, importer eller dupliser).
  - `test_svaret_for_gyldig_nevner_ingen_utelukket` (l.157): sjekk også at `topprangert`, der den finnes, ikke nevner noen utelukket.
  - Ny test: `topprangert` er nøyaktig `None` når valgt er nr. 1, og nøyaktig nr. 1-kandidaten (ikke en kopi av valgt) når valgt ikke er nr. 1.
  - Styr fasittesten slik at ingen lagrede tolkninger finnes. Legg til en test uten live-kall med lagret tolkning som endrer topplasseringen, og sammenlign valgt kandidat og `topprangert` med samme grunnlags kandidatliste (P-05). Et syntetisk eksempel er Mette med «ønsker flere» (100 preferansepoeng) og Jonas med 50; dette er en testtilstand, ikke en påstand om seedteksten.
- `frontend/src/api.ts`:
  - `Godkjenningssvar`s `"ok"`-gren: `kandidat: Kandidat` → `kandidat: RangertKandidat`, nytt felt `topprangert: RangertKandidat | null`.
- `frontend/src/godkjenning.ts`:
  - `Godkjenningstilstand`s `"klar"`-gren får `kandidat: RangertKandidat` og `topprangert: RangertKandidat | null`, satt i `tilstandFraSvar`.
  - `frontend/tester/godkjenning.test.mjs`: oppdater fixturene til `RangertKandidat`-formen og `topprangert`.
- `frontend/src/komponenter/Kandidatflate.tsx`:
  - Skill ut `Belastningslinje({ minutter, prosent, høy })` med dagens synlige timer, skjermlesertekst, grafiske linje og eventuelle varsel, samt `Ulempeindikator({ ulempe })` med poeng og fordeling. Eksporter og gjenbruk dem i `Kandidatrad` og `Godkjenningsflate.tsx`.
- `frontend/src/komponenter/Godkjenningsflate.tsx`:
  - Kandidatkortet (`<section className="panel kandidatkort">`, l.157): legg til `Belastningslinje` og `Ulempeindikator` fra `tilstand.kandidat` etter `Kostnadsvisning`.
  - Ny komponent `Avviksnotat({ valgt, topprangert })`, vist mellom kandidatkortet og bekreftelsesboksen, bare når `tilstand.topprangert` ikke er `null`.
- `frontend/src/tekster.ts`: i `godkjenning`-seksjonen (l.157), legg til teksten for avviksnotatets overskrift, sammenligningslinjen (mal per kandidat: navn, kostnad, nivå, timer, ulempe) og «Turnushjelperen anbefaler, den bestemmer aldri selv.».
- `frontend/src/stil/app.css`: `.avviksnotat` som `.ekskludert-boks` (`border: var(--border-width) dashed var(--color-border); background: var(--color-breadcrumb-bg);`), med en liten overskriftsstil for «Avvik fra anbefalt rangering» (som `.lbl` i mockupen: `accent`-farge, store bokstaver). Bare tokens (AV-13).
- `frontend/tester/komponenter/hjelpere.ts`: `JONAS` og `GODKJENNING_JONAS` (brukt av alle 12 eksisterende tester i `godkjenningsflate.test.tsx`) typer `kandidat` som `Kandidat`, uten rangeringsfelt eller `topprangert`. Må oppdateres til `RangertKandidat` med Jonas' fasitverdier (plass 1, totalscore 79,40 osv. fra `test_rangering.py`/`UTEN_TOLKNING_4127`) og `topprangert: null`, ellers feiler `satisfies Godkjenningssvar`-typesjekken og `npm.cmd run build`. Legg til en tilsvarende `GODKJENNING_METTE`-fixture (plass 2, `topprangert` er Jonas' fulle `RangertKandidat`).
- `frontend/tester/komponenter/godkjenningsflate.test.tsx`:
  1. Med `GODKJENNING_JONAS`: kontroller synlig og tilgjengelig timetall, ulempepoeng og fordeling på kandidatkortet; avviksnotatet finnes ikke i DOM-en. Kontroller også tekstvarsel ved høy belastning.
  2. Med `GODKJENNING_METTE`: kontroller hver kandidatgruppe separat: navn, 2 960 kr, nivå 4/4 mot 3/4, 16 t, 180 mot 40 ulempepoeng og riktig kveld/helg/natt-fordeling. Kontroller at bekreftelsesknappen er aktiv.
  3. Utvid testen av `endret_grunnlag`: POST avvises, nytt GET gir endret toppkandidat og nytt merke, notatet oppdateres eller forsvinner riktig, og ny bekreftelse sender det nye merket (P-09).
- `docs/testing.md`: ny rad i komponenttest-tabellen for de to nye flytene, og et nytt avsnitt «Story 4.5 – avviksnotat og nøkkeltall» etter mønsteret fra 4.3/4.4.
- Ikke endre: `domene/regelmotor/rangering.py`, `domene/porter/rangering.py`, `kandidater()`-ruten, POST-ruten for godkjenning, `grunnlagsmerke`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py` — `RangertKandidatUt` og `topprangert` i `GodkjenningsgrunnlagUt`, bygget i `godkjenningsgrunnlag()`.
- [x] `backend/tester/api/test_godkjenningsgrunnlag.py` — oppdater berørte tester og test `topprangert` både uten tolkninger og med lagret tolkning som endrer rangeringen.
- [x] `frontend/src/api.ts`, `godkjenning.ts`, `tester/godkjenning.test.mjs` — ny type og felt.
- [x] `frontend/src/komponenter/Kandidatflate.tsx` — skill ut `Belastningslinje` og `Ulempeindikator`.
- [x] `frontend/src/komponenter/Godkjenningsflate.tsx`, `tekster.ts`, `stil/app.css` — nøkkeltall på kortet og `Avviksnotat`.
- [x] `frontend/tester/komponenter/hjelpere.ts` — oppdater `JONAS`/`GODKJENNING_JONAS` til `RangertKandidat` + `topprangert: null`, og legg til `GODKJENNING_METTE`.
- [x] `frontend/tester/komponenter/godkjenningsflate.test.tsx` — test tilgjengelig timetall, begge kandidatgruppenes verdier og endret rangering etter `endret_grunnlag` (OP-16, P-09).
- [x] `docs/testing.md`, `docs/ki-logg/<dato>-avviksnotat.md`, `docs/emne/vurderingsmatrise.md`, `epic-4-context.md` — dokumenter flyt, KI-arbeid, bevis og status.

**Acceptance Criteria:**
- Given #4127 uten lagrede tolkninger og Jonas Bakke valgt, when godkjenningsflaten vises, then kandidatkortet viser tilgjengelig timetall, timebelastningslinjen og ulempeindikatoren, og ingen avviksnotat vises.
- Given #4127 uten lagrede tolkninger og Mette Solberg valgt, when flaten vises, then avviksnotatet viser kostnad, kompetansenivå, timebelastning og ulempe med fordeling for Mette og Jonas side om side, med teksten «Turnushjelperen anbefaler, den bestemmer aldri selv.», og godkjenningsknappen er fortsatt aktiv.
- Given at rangeringen endres mens godkjenningsflaten er åpen, when bekreftelse avvises med `endret_grunnlag`, then vises oppdatert sammenligning fra nytt grunnlag og ny bekreftelse kreves (P-09).
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd run test` kjøres, then alt består.

## Implementation Notes

- Implementert 2026-11-17 av Claude (Sonnet 5), direkte mot spesifikasjonen i én økt
  (ikke `bmad-build`s underagent-oppsett). Se
  [KI-loggen](../../docs/ki-logg/2026-11-17-avviksnotat.md) for prompt, leveranse og
  rettelser, blant annet at `test_kandidater.py::test_kandidatfeltene_er_de_samme_som_i_godkjenningsgrunnlaget`
  og en eksisterende story 4.7-komponenttest (hardkodet Jonas' gamle, syntetiske
  ulempetall) måtte oppdateres som følge av denne storyen.
- `kompetansenivå`-importen i `main.py` ble fjernet: `godkjenningsgrunnlag()` henter nå
  kompetansenivå fra `rangert_ut` i stedet for å kalle `kompetansenivå()` direkte.
- Menneskelig gjennomgang er ikke gjort. Storyen forblir `in-progress` i
  `sprint-status.yaml` til det er gjort.

## Spec Change Log

- 2026-11-17: Presisert timeverdier og tilgjengelighet, aktiv bruk av lagrede preferansetolkninger, kandidatgrupper med indikatorer og test av endret grunnlag etter gjennomgang av PR 31. Endringene i låst del er godkjent av Kim i samtalen etter gjennomgangen.
- 2026-11-17: Mithad Kuduz (storyens eier, OP-17) godkjente endringene over i denne økten, etter å ha gått gjennom dem linje for linje. PR #31 hadde ingen registrerte kommentarer eller gjennomganger da Kims commits ble pushet direkte til branchen; godkjenningen her er derfor sporet i sesjonsloggen i stedet.

## Review Triage Log

En uavhengig underagent (Sonnet, samme modellnivå som økten) gikk gjennom spesifikasjonen 2026-11-17, før godkjenning. Fasittallene uten tolkning og valget av `plass` fremfor `totalscore` ble kontrollert. Påstanden om at preferanser ikke var koblet inn, ble senere korrigert i Spec Change Log.

Kodegjennomgang 2026-11-17 (etter implementering) med blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), alle Sonnet. ECH fant ingen funn. Ett funn fra VG var allerede verifisert av laget selv (gap-funn, iht. instruksen) og er tatt inn med dets egen dom.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG | Avviksnotatets «høy belastning»-varsel testes ikke for noen av de to kandidatene i selve notatet; testen med `hoy_belastning: true` har `topprangert: null` og når aldri notat-grenen, og notat-testen bruker bare `hoy_belastning: false` på begge | lav (gap-funn, forhåndsverifisert): en regresjon i varselet for notatets to kandidater ville ikke blitt fanget | patch: utvid notat-testen med én side som har høy belastning |
| BH | Avviksnotatets overskrift er et `<p>` (`avviksnotat-lbl`), ikke en overskrift, ulikt søsterseksjonen «Bekreft erstatning» rett under (`<h2>`) | lav: reelt avvik fra sidens egen overskriftshierarki, triviell retting | patch: bytt til `<h2>` med samme klasse |
| BH | `epic-4-context.md`s nye punkt sier «675 backendtester og 41 komponenttester», og utelater «52 modultester» som `docs/testing.md`, vurderingsmatrisen og KI-loggen alle har med | lav: kontrollert, vurderingsmatrisen har faktisk med 52-tallet, bare epic-4-context.md mangler det | patch: legg til tallet |
| BH | Verken `epic-4-context.md` eller vurderingsmatrisens nye avsnitt nevner AV-07 eller P-05/P-09 ved navn, selv om innholdet (fasitdisiplin, lagret tolkning som endrer topplassering) er nettopp det; story 4.4s tilsvarende avsnitt siterer sammenlignbare ID-er | lav: reelt, og i tråd med AGENTS.md og presedens fra 4.4 | patch: legg til ID-ene i begge avsnitt |
| BH | Innrykket i `ulempebelastning`-literalen i den nye `JONAS_SOM_TOPPRANGERT`-fiksturen i `test_godkjenningsgrunnlag.py` er ikke på linje med den tilsvarende Mette-literalen i samme test | lav: kosmetisk, triviell retting | patch |
| BH | Spesifikasjonens `status`-felt sier `in-review`, mens sprint-status, KI-loggen, vurderingsmatrisen og Implementation Notes sier `in-progress` | false: `in-review` er riktig akkurat nå — steg 4 i `bmad-build` setter den eksplisitt før kodegjennomgangen starter, og de andre dokumentene ble skrevet av implementeringsagenten før det. Alle blir `done` sammen i steg 5 | avvist |
| BH | Ingen test dekker tilfellet der `ansatt_id` ikke lenger finnes i `vurdering.gyldige` når `next(...)` kalles uten standardverdi | false: ECH kontrollerte uavhengig at `ranger()` gir nøyaktig én `RangertKandidat` per medlem av `vurdering.gyldige`, og `kandidat`-oppslaget rett over bekrefter allerede medlemskapet. Tilstanden er structurally unreachable, ikke bare hevdet | avvist |
| BH | Avviksnotatets kolonner har ingen «Din valgte»/«Topprangert»-etikett, bare navn | false: følger mockupen (`key-godkjenning.html`), som heller ikke har noen etikett — innledningssetningen navngir allerede hvem som er topprangert, og hvert navn er unikt | avvist |
| BH | `godkjenningsgrunnlag()` kjører `ranger()` på nytt for hvert kall, uten gjenbruk fra kandidatruten | false: den låste delen krever uttrykkelig «på samme måte som kandidatruten»; de to rutene er separate sidelastinger uten delt tilstand noe sted i kodebasen i dag | avvist |
| BH | Spec Change Log nevner ikke rettingen av den gamle 4.7-komponenttesten | false: Spec Change Log er for funn fra kodegjennomgangen, ikke en generell implementeringslogg; rettingen står riktig i Implementation Notes og KI-loggen | avvist |

| # | Funn | Dom | Rute |
|---|---|---|---|
| 1 | Code Map viste til `grunnlag.ansatte_ved_id`, som ikke finnes; det reelle behovet dekkes av et lokalt `{k.id: k for k in vurdering.gyldige}`, som `kandidater()` allerede bygger | høy | rettet i Code Map |
| 2 | En foreslått `None`-gren for `valgt` var dødkode: `ansatt_id` er allerede bekreftet i `vurdering.gyldige` via den eksisterende `kandidat`-variabelen, så `ranger()` finner den garantert | middels | fjernet fra Code Map |
| 3 | Testfiksturene `JONAS`/`GODKJENNING_JONAS` i `hjelpere.ts`, brukt av alle 12 eksisterende tester, manglet rangeringsfelt og `topprangert`; uendret ville `npm.cmd run build` brutt | høy | lagt til som egen oppgave |
| 4 | Komponenttestoppgaven var ikke presis nok til å hindre en svakere test (bare «notat vises» uten å sjekke fravær for Jonas eller de eksakte tallene for Mette) | middels | presisert i Code Map og oppgavelisten |

## Design Notes

- **Hvorfor `plass` og ikke `totalscore`:** Epic 4-konteksten påpeker at kostnad er `float`, så nær-like totaler kan i prinsippet avvike i siste siffer uten å utløse likhetsbrytingen på ansatt-ID. `plass` er allerede regnet ferdig i domenekjernen med nøyaktige `Fraction`-verdier og den riktige likhetsbrytingen, så å sammenligne `plass == 1` her er korrekt og unngår å gjenta den logikken i API- eller frontend-laget.
- **Sammenligningens form:** bygger på mockupen (`key-godkjenning.html`, `.deviation-note .compare`), men hver kandidatgruppe inneholder også de gjenbrukte indikatorene med fordeling. Valgt kandidat står først. Preferansepoeng tas ikke med i notatet; lagrede tolkninger kan likevel påvirke hvilken kandidat som er topprangert.

## Verification

**Commands:**
- `backend/`: `.venv\Scripts\python -m pytest`. Forventet: alt består, også import-linter.
- `frontend/`: `npm.cmd run build` og `npm.cmd run test`. Forventet: begge består (`node --test` og Vitest).

**Manual checks (docs/testing.md):** 1080/960/680/1600 px, tastatur og fokus, farger (tokens, ikke rå verdier), større skrift, ekte backend mot #4127 (Jonas og Mette). For fasiten må testdatabasen være nyfylt uten lagrede tolkninger og bakgrunnstolkning være avslått; bruk separat testdatabase og ikke en database med data som skal beholdes. Kontroller også et grunnlag med lagret tolkning, uten å forutsette Jonas som nr. 1.

**Resultat (2026-11-17):** `backend/.venv\Scripts\python -m pytest` — 675 bestått, inkludert import-linter-kontrakten. `npm.cmd run build` og `npm.cmd run test` (fra `frontend/`) — bygget og 52 `node --test` og 41 Vitest-komponenttester (37 eksisterende + 4 nye) bestod. Manuelle kontroller er ikke utført: ingen nettleser var tilgjengelig i denne økten. Dette er et åpent punkt, ikke et bestått resultat.
