---
title: 'Story 2.3: Filtrere på 11-timersregelen (daglig hvile)'
type: 'feature'
created: '2026-11-11'
status: 'done'
baseline_commit: 'f2188100b434a1ee014b6f4b57cfea4f48e02a74'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Etter 2.2 er listen filtrert på kompetanse og kollisjon. En Ansatt som ville fått under 11 timer hvile før eller etter Vakten, vises fortsatt som Kandidat (FR4, AV-04). I tillegg gir én ugyldig tildelt vakt hvor som helst datafeil for alle lister. Vedtak A5 (PR #14) sier at dette skal avgrenses til et vindu rundt Vakten.

**Approach:** Legg 11-timersregelen inn som regel nummer tre i `REGLER`. Gi hver regel et vindu rundt Vakten, og la datafeilsjekken gjelde bare Kandidatens vakter innenfor det samlede vinduet. Sjekk også at vinduet ligger innenfor datadekningen. Endepunkt og flate er uendret, bortsett fra at listen blir kortere og merknaden endres.

## Boundaries & Constraints

**Always:**
- Hvile = faktisk forløpt tid i UTC. Før: Vaktens start − slutt på Kandidatens vakt. Etter: start på Kandidatens vakt − Vaktens slutt. Under 11 t 0 min gir utelukkelse med årsaken «11-timersregelen». Nøyaktig 11 t er gyldig. Vakter som bare møtes Vakten (0 t hvile) bryter regelen.
- Vindu per regel: kompetanse har ikke noe vindu, kolliderende vakt har `[start, slutt)`, og 11-timersregelen har `[start − 11 t, slutt + 11 t)`. Det samlede vinduet er det minste tidsrommet som dekker alle vinduene. 2.4 legger til hele uker i samme mønster.
- Datafeil (P-08, A5):
  - Vinduet slutter etter `datagrense` eller starter før historikkstarten → `Datafeil`.
  - En av Kandidatens vakter mangler tidssone → `Datafeil`. Den kan ikke plasseres i tid.
  - En vakt med tidssone, der `start >= slutt`, gir `Datafeil` bare når det lukkede tidsrommet `[min(start, slutt), maks(start, slutt)]` overlapper det halvåpne vinduet `[v_start, v_slutt)`. Et punkt nøyaktig i `v_slutt` er utenfor, og et punkt i `v_start` er innenfor.
  - Vinduet er dekket når `historikkstart <= v_start` og `v_slutt <= datagrense`. Nøyaktig på grensen er gyldig.
  - Ugyldige vakter utenfor vinduet ignoreres.
- 2.1-sjekken «slutter etter datagrensen» erstattes av vindussjekken. For #4261–#4265 og andre vakter 04.10 gir det datafeil, slik P-08 krever.
- Svaret er uendret (NFR2), og `datagrense` i svaret er fortsatt `turnus.periode_slutt`, også når datafeilen skyldes historikkstarten. Det er en kjent begrensning, godtatt av Mithad 2026-11-11. Ingen vakt i perioden kan treffe den nedre grensen.
- Kjent begrensning, godtatt av Mithad 2026-11-11: En av Kandidatens vakter som starter før historikkstarten og slutter etter den, regnes som kjent data. Det påvirker ikke #4127 eller #4189. Merknaden blir «Filtrert på kompetanse, kolliderende vakt og 11-timersregelen. Flere regler kommer.» og fjernes i 2.4.
- Ren regelmotor uten klokke eller database. Samme input gir samme output. Testdatafasiten tilpasses aldri koden (AV-07).

**Beslutninger (Mithad, 2026-11-11):**
- **Overlapp og 11 t (A):** En egen vakt som overlapper Vakten, teller bare som kolliderende vakt. 11-timersregelen ser bare på vakter som ikke overlapper Vakten. Nærmeste slutt før og nærmeste start etter avgjør, som fasithjelperen `bryter_elleve_timer` i 1.2. Hver Ansatt får én årsak for samme forhold. Hvem som er gyldige, blir det samme som ved alternativet. Spørsmålet stod åpent for gruppa i §11 og ble avgjort av Mithad som eier av storyen (OP-12).
- **Historikkstart (A):** Datadekningen starter ved `turnus.periode_start − 672 t` (24.08.2026 kl. 00:00 i seeden). Det er samme vindu som ulempemålingen i AV-09, og seedens historikk er bygd for det. Adapteren beregner verdien, og skjemaet endres ikke.

**Never:** 35-timersregelen, Ekskludert-boks, tomtilstand, rangering eller KI. Endring i skjema eller testdata. Å avsløre i svaret hvilken vakt som bryter regelen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Nøyaktig 11 t før | forrige vakt slutter 11:00 t før start | ikke utelukket | — |
| 10:59 før / etter | forrige slutter 10:59 før, eller neste starter 10:59 etter | utelukket, «11-timersregelen» | — |
| Møtes | egen vakt slutter ved Vaktens start | utelukket (0 t hvile) | — |
| Vårskiftet | hvile over natt til 29.03.2026, veggklokke 11 t = 10 faktiske | utelukket | — |
| Høstskiftet | hvile over natt til 25.10.2026, veggklokke 10,5 t = 11,5 faktiske | ikke utelukket | — |
| Ingen nære vakter | ingen egne vakter innenfor ±11 t | ikke utelukket | — |
| #4127 | seed | 5 gyldige: de 9 fra 2.2 minus de 4 med `elleve-timer` i fasiten | — |
| #4189 | seed | 1 gyldig: de 19 fra 2.2 minus de 18 med `elleve-timer` | — |
| Nær datagrensen | Vakt med `slutt + 11 t` etter `datagrense`, som dag 04.10 | `status: "datafeil"` | ingen liste |
| Vindu nøyaktig ved datagrensen | `slutt + 11 t == datagrense` | vurderes normalt | — |
| Ett minutt over datagrensen | `slutt + 11 t == datagrense + 1 min` | `status: "datafeil"` | ingen liste |
| Vindu nøyaktig ved historikkstart | `start − 11 t == historikkstart` | vurderes normalt | — |
| Ett minutt før historikkstart | `start − 11 t == historikkstart − 1 min` | `Datafeil` | ingen liste |
| Ugyldig vakt langt unna | `start >= slutt` uke 35, Vakt 27.09 | vurderes normalt | — |
| Ugyldig vakt i vinduet | `start >= slutt` innenfor ±11 t | datafeil | ingen liste |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/vurdering.py`:
  - `Regel` får feltet `vindu: Callable[[Vakt], Tidsrom | None]`. `REGLER` får regel tre.
  - Rekkefølgen i `vurder_kandidater`:
    1. Valider Vakten (vakttype, tidssone på `start`, `slutt`, `datagrense` og `historikkstart`, og `start < slutt`). Stopp med `Datafeil` der, før noe vindu regnes ut. `astimezone` på en naiv tid tolkes som maskinens lokaltid (vurdering.py:80).
    2. Regn ut det samlede vinduet. Det dekker alltid minst `[vakt.start, vakt.slutt)`, også når ingen regel har vindu, ellers forsvinner datagrensesjekken når bare kompetanse brukes.
    3. Sjekk vinduet mot `[historikkstart, datagrense]`.
    4. Valider Kandidatens vakter mot vinduet.
  - **All vindusaritmetikk skjer etter `astimezone(UTC)`.** `vakt.start - timedelta(hours=11)` på en `ZoneInfo`-tid regner på veggklokka og gir 10 eller 12 faktiske timer over sommertidsskiftet. Det samme gjelder `periode_start − 672 t` i adapteren.
  - Den generelle valideringen av Kandidatens vakter dekker de samme feilene som `kollisjonsdatafeil` i dag: «er ikke et tidsrom», manglende tidssone og `start >= slutt`, nå avgrenset til vinduet.
  - `vurder_kandidater(vakt, ansatte, datagrense, historikkstart, regler=REGLER)`: `historikkstart` kommer før `regler`. Datafeilen beholder `datagrense`.
  - Sorteringen og rekkefølgen på årsakene endres ikke.
- `backend/domene/regelmotor/kolliderende_vakt.py`: `kollisjonsdatafeil` validerer i dag alle vakter. Den **fjernes**, og regelens `kandidatkrav` blir `lambda _k, _v: []`. Valideringen flyttes til den generelle vindussjekken i `vurdering.py`. `overlapper`/`bryter_kollisjon` beholdes.
- Ny `backend/domene/regelmotor/elleve_timer.py`: `ÅRSAK = "11-timersregelen"`, `bryter_elleve_timer` og `vindu`. Formen følger `kompetanse.py`.
- `backend/domene/typer.py`: `Tidsrom` brukes om igjen. `Kandidat` og `Vakt` endres ikke.
- `backend/adaptere/lagring/kandidatgrunnlag.py`: `Kandidatgrunnlag` får `historikkstart = turnus.periode_start − timedelta(hours=672)`. Spørringen etter tildelte vakter beholdes.
- `backend/adaptere/api/main.py`: Ruten `kandidater()` sender `historikkstart` videre. Svarmodellene endres ikke.
- Tester:
  - `backend/tester/regelmotor/test_kompetanse.py`:
    - Hjelperne må få `historikkstart`.
    - `Regel(...)` på l.~125 må få `vindu`.
    - Datagrensetestene på l.~193–212 må regnes om etter det nye vinduet.
  - `backend/tester/regelmotor/test_kolliderende_vakt.py`: Hjelperne må få `historikkstart`. Testene for datafeil på all historikk i 2.2 skrives om etter A5.
  - `backend/tester/api/test_kandidater.py`:
    - `IMPLEMENTERTE_REGLER` (l.~30) må få `"elleve-timer"`, og `forventet_gyldige` utelater den da.
    - 9/19 blir 5/1, og forventet antall utelukkede (l.~59–60) blir 19/23.
    - Datagrensetesten fra 2.1 (start 04.10 16:00/16:01) må følge det nye vinduet.
- Fasit og tekst:
  - `backend/tester/lagring/test_testdata.py` har `bryter_elleve_timer` (l.120) som uavhengig fasit. Den brukes bare i tester og skal ikke importeres av domenet.
  - `frontend/src/tekster.ts:96`, `frontend/tester/kandidater.test.mjs:75` og `README.md:173`: merknaden og regelstatusen.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/regelmotor/elleve_timer.py`: regel, årsak og vindu i UTC (FR4).
- [x] `backend/domene/regelmotor/vurdering.py` og `kolliderende_vakt.py`: `vindu` på `Regel`, samlet vindu, sjekk mot datadekning og vindusbasert validering av vakter (A5, P-08).
- [x] `backend/adaptere/lagring/kandidatgrunnlag.py` og `backend/adaptere/api/main.py`: `historikkstart` fra adapteren til regelmotoren (AD-5).
- [x] `backend/tester/regelmotor/test_11_timersregelen.py`: hele matrisen, begge sommertidsskiftene, determinisme og vindus-datafeil. Det er kravet i AC-en i epics. Sommertidstestene (29.03 og 25.10) ligger utenfor dekningen i seeden. De sender derfor egne verdier for `historikkstart` og `datagrense`. Begge tidene i en sammenligning bruker samme `ZoneInfo`-objekt, ellers fanger mutasjonen i AC-en ikke UTC-feilen.
- [x] `backend/tester/regelmotor/test_kompetanse.py`, `test_kolliderende_vakt.py` og `backend/tester/api/test_kandidater.py`: ny signatur, A5-testene og fasiten 5/1 mot `FASIT` (AV-07).
- [x] `frontend/src/tekster.ts`, `frontend/tester/kandidater.test.mjs` og `README.md`: ny merknad og regelstatus.
- [x] `docs/ki-logg/<dato>-11-timersregelen.md`, `docs/emne/vurderingsmatrise.md` og `_bmad-output/implementation-artifacts/epic-2-context.md`: KI-logg og bevis. Merk A5-punktet i `deferred-work.md` som utført.
- [x] `docs/beslutninger/avklaringspunkter.md` §11: før inn at vakter som slutter etter 04.10 kl. 13:00 nå gir datafeil, fordi `slutt + 11 t` havner etter 05.10 kl. 00:00. KS-04 godtok tidligere at hvilen etter vakter ved periodeslutt ikke ble kontrollert fullt ut. Endringen følger P-08. Før også inn beslutningene 1A og 2A (OP-12).

**Acceptance Criteria:**
- Given en valgt vakt, when kandidatflaten lastes, then listen er filtrert på alle tre reglene.
- Given en mutasjon fra `<` til `<=` i grensen på 11 t, when `pytest` kjøres, then minst én test feiler. Mutasjonen dokumenteres i KI-loggen.
- Given en mutasjon som fjerner UTC-omregningen, when `pytest` kjøres, then minst én sommertidstest feiler.
- Given hele pakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then alt består.

## Implementation Notes

- 2026-11-11: En underagent implementerte storyen, med spesifikasjonen som eneste kilde. Avvik fra Code Map: når Vakten er ugyldig, samles kompetansefeilene likevel, men vinduet regnes ikke ut. Det holder en eksisterende test grønn og er ikke i strid med rekkefølgen.
- 2026-11-11: Etter kodegjennomgangen er seks funn rettet, ett utsatt og resten avvist (se Review Triage Log). 337 backendtester og 26 frontendtester består, og bygget går gjennom.
- Nettleserkontrollen gjenstår: #4127 skal vise 5 kandidater og #4189 1, med ny merknad.

## Spec Change Log

## Review Triage Log

En uavhengig underagent gikk gjennom spesifikasjonen 2026-11-11, før godkjenning. Tallene 5 og 1 og historikkstarten 24.08 ble kontrollert mot fasiten (`test_testdata.py:462–470`, `:685`). Gjennomgangen fant ingen motstrid mot A5, P-08 eller AV-04.

| # | Funn | Dom | Rute |
|---|---|---|---|
| 1 | Det var uklart hva «berører vinduet» betyr for en vakt med `start >= slutt` | middels | låst del rettet etter Mithads godkjenning |
| 2 | Grensetester for selve vinduet manglet | middels | fire rader lagt i matrisen (Mithad) |
| 3 | `datagrense` sendes også når datafeilen skyldes historikkstarten | lav | godtatt som kjent begrensning (Mithad) |
| 4 | En vakt som krysser historikkstarten, regnes som kjent | lav | godtatt som kjent begrensning (Mithad) |
| 5 | `- timedelta` på en `ZoneInfo`-tid regner på veggklokka | høy | Code Map: all aritmetikk i UTC |
| 6 | Vinduet ble regnet ut før Vakten var validert | middels | Code Map: fast rekkefølge |
| 7 | Uten vindu forsvant datagrensesjekken når bare kompetanse brukes | middels | Code Map: vinduet dekker alltid Vakten |
| 8 | Ikke alle testene som brytes, var listet | middels | Code Map: listet med linjer |
| 9 | Sjekken «ikke et tidsrom» manglet, og «tømmes eller fjernes» var tvetydig | middels | Code Map: fjernes, sjekken flyttes |
| 10 | `historikkstart` uten tidssone, og plassen i signaturen | lav | Code Map |
| 11 | Sommertidstestene ligger utenfor dekningen i seeden | lav | oppgaven for testmodulen |
| 12 | Vakter 04.10 gir nå datafeil, som er en endring mot KS-04 | lav | ny oppgave: før det inn i §11 |

Kodegjennomgang 2026-11-11 med blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG). Hvert funn er kontrollert mot koden.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG, ECH, BH | Adaptertesten for `historikkstart` fanger ikke at `.astimezone(UTC)` fjernes. Seedens 672 t krysser ikke noe sommertidsskifte, og forventningen `PERIODE_START - timedelta(days=28)` regner selv på veggklokka | medium: koden er riktig, men en regresjon ville passert. Gjelder perioder der 672 t krysser 29.03 eller 25.10 | patch: forventning i UTC og ny test med `periode_start` 13.04 |
| ECH | Forventningen i den samme testen regner på veggklokka | samme rot som over | patch (samme) |
| ECH, BH | `bryter_elleve_timer` hopper stille over ugyldige vakter. Det er trygt bare via `vurder_kandidater` | low: ingen kaller den direkte i dag, men Epic 3 skal sjekke reglene på nytt. Rettingen er en setning i docstringen | patch: forutsetningen i docstringen |
| ECH | `Regel.vindu` kan returnere naive tider | false: alle tre reglene returnerer `None` eller UTC-tider (`kolliderende_vakt.vindu`, `elleve_timer.vindu`), og `REGLER` er intern | avvist |
| ECH | En vakt som krysser historikkstarten, regnes som kjent | low: kjent begrensning, godtatt av Mithad i den låste delen | avvist |
| BH | epics.md sier fortsatt «Grensetester gjenstår» (l.116, ~502) | low: det er reelt. Endring i et planleggingsdokument gjør `epic-2-context.md` ugyldig for 2.4 og hører til gruppas samordning | defer |
| BH | KS-04-raden og sammendraget peker ikke til endringen i §11 | low: reelt, og rettingen er direkte | patch |
| BH | `sprint-status.yaml` sier `in-progress`, mens spesifikasjonen sier `in-review` | false: steg 5 i `bmad-build` setter sprintstatus til `review`. Statusene er midlertidig ulike midt i gjennomgangen | avvist |
| BH | `utelukket`-hjelperen i `test_kolliderende_vakt.py` krever ikke lenger nøyaktig én årsak | low: VG viser at 1A fortsatt er låst av eksakte tupler, men 2.2-testene ble svakere. Rettingen er direkte: `regler=REGLER[:2]` | patch |
| BH | Datafeilskjermen viser datagrensen 05.10 også for en vakt som slutter 04.10 kl. 13:01 | low: kan ikke nås i dag, fordi bare #4127 og #4189 mangler bemanning. Visningen av datagrensen er godtatt i den låste delen | avvist |
| BH | Språkfeil i den låste delen: «møtes Vakten» | low: rettingen er en endring i spesifikasjonen | avvist |
| BH | A5-punktet i `deferred-work.md` er bare halvveis oppdatert | low: rettingen er direkte | patch |
| BH | README beskriver en datafeil som ikke kan nås, og den manuelle kontrollen dekker den ikke | low: README-delen er rettet direkte. Den manuelle kontrollen ville vært en endring i spesifikasjonen | patch (README), resten avvist |

## Design Notes

- **Hvorfor vinduet ligger på `Regel`:** Ingen regel trenger da sin egen datafeilsjekk for Kandidatens vakter, og 2.4 trenger bare å oppgi ukevinduet.
- **Hvorfor samlet vindu:** Kandidatlisten er én vurdering. Ugyldige data som kan påvirke én regel, gjør hele listen usikker (P-08).
- **Eksempel:** Natt 04.10 23:00 – 05.10 07:00 og kveld 04.10 gir begge vindusslutt etter 05.10 00:00 og dermed datafeil. #4127 får vinduet [26.09 20:00, 28.09 02:00), og #4189 får vinduet [28.09 12:00, 29.09 18:00). Begge ligger innenfor dekningen, i tråd med KS-04.

## Verification

**Commands:**
- `backend/`: `.venv\Scripts\python -m pytest`. Forventet: alt består, også import-linter.
- `frontend/`: `npm.cmd run build` og `npm.cmd test`. Forventet: begge består.

**Manual checks:**
- Nettleserkontroll som i 2.2. #4127 viser 5 kandidater og #4189 viser 1, med ny merknad.
