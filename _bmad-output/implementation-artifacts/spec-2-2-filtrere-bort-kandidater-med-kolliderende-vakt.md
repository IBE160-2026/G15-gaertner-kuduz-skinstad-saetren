---
title: 'Story 2.2: Filtrere bort kandidater med kolliderende vakt'
type: 'feature'
created: '2026-11-11'
status: 'done'
baseline_commit: '0fc10f0d15ffb757ffce05cefac51d90dfe02667'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatlisten er bare filtrert på kompetanse (2.1). En Ansatt som allerede jobber i samme tidsrom, vises som Kandidat, og turnusansvarlig må selv finne dobbeltbookingen (FR3).

**Approach:** Legg til regelen «kolliderende vakt» som nummer to i regellisten fra 2.1. Kandidaten får sine egne tildelte vakter med i grunnlaget, og regelen sammenligner dem med Vakten på faktiske tidspunkt som halvåpne intervall. Endepunktet og flaten er uendret, bortsett fra at listen blir kortere.

## Boundaries & Constraints

**Always:**
- Vakter er halvåpne intervall `[start, slutt)`. `a.start < b.slutt and b.start < a.slutt` gir kollisjon. Vakter som bare berører hverandre, gir ikke kollisjon. Omsluttende og omsluttet vakt gir kollisjon.
- Tidene sammenlignes i UTC (som `vaktdatafeil` i 2.1), ikke på kalenderdato eller veggklokke, slik at nattevakter over midnatt og timen som går to ganger i oktober blir riktig.
- Kandidatens vakter er alle rader i `vakt` med `tildelt_ansatt_id` lik Kandidatens id, uavhengig av periode. Vakten som skal bemannes, har ingen tildelt Ansatt og er derfor aldri med. To ulike Ansatte med overlappende vakter er ikke et regelbrudd (AV-02).
- Regelen legges inn som en `Regel` i `REGLER` etter kompetanse, med `bryter`, `vaktkrav` og `kandidatkrav`. Årsaken heter «kolliderende vakt». Alle årsaker samles fortsatt uten å stoppe ved første brudd.
- Datafeil (P-08): en av Kandidatens vakter uten tidssone, eller med `start` ikke før `slutt`, gir `Datafeil`, ikke utelukkelse eller gyldig. Svarformen er uendret.
- `Kandidat` utvides med `vakter` med standardverdi tom, slik at 2.1-tester og kall virker uendret. Domenet er fortsatt rent og uten rammeverk. Konverteringen fra SQLAlchemy skjer i `adaptere/lagring/kandidatgrunnlag.py` (AD-5).
- Svaret er uendret: bare Gyldige kandidater alfabetisk, uten utelukkede og uten vakter (NFR2). Den midlertidige merknaden blir «Filtrert på kompetanse og kolliderende vakt. Flere regler kommer.», og den fjernes fortsatt i 2.4.
- Testdatafasiten tilpasses aldri koden (AV-07). Regelmotoren importerer ikke testhjelperne i `tester/lagring/test_testdata.py`.

**Never:**
- Regler for 11 t eller 35 t, Ekskludert-boks, tomtilstand, Rangering, kostnad eller KI-kall.
- Endringer i skjema eller testdata, ny tabell eller migrering.
- At vakter i svaret eller på flaten avslører hvilken vakt en Kandidat kolliderer med.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Ett minutts overlapp | egen vakt slutter 1 min etter Vaktens start | utelukket, «kolliderende vakt» | — |
| Møtes | egen vakt slutter nøyaktig ved Vaktens start, eller starter nøyaktig ved Vaktens slutt | ikke utelukket av denne regelen | — |
| Omslutter / omsluttet | egen vakt dekker hele Vakten, eller ligger helt inne i den | utelukket | — |
| Natt over midnatt | Vakt 23–07 og egen vakt 06–14 neste dag | utelukket; egen vakt 07–15 gir ikke kollisjon | — |
| Sommertid | Vakt natt 24.–25.10 med timen som går to ganger, og egen vakt i den timen | regnet på faktiske tidspunkt | — |
| Flere brudd | kollisjon og for lavt kompetansenivå | begge årsaker, i rekkefølgen kompetanse-minstekrav, kolliderende vakt | — |
| Flere egne vakter | bare én av dem overlapper | utelukket | — |
| Ingen egne vakter | tom liste | ikke utelukket | — |
| #4127 | seed | 9 gyldige: de 16 fra 2.1 minus de 7 med `kolliderende` i fasiten | — |
| #4189 | seed | 19 gyldige: de 21 fra 2.1 minus de 2 med `kolliderende` | — |
| Ugyldig vakt | Kandidatens vakt uten tidssone, eller `start >= slutt` | `status: "datafeil"` uten liste | ingen utelukkelse |

</frozen-after-approval>

## Code Map

- `backend/domene/typer.py` -- `Kandidat` (frosset dataklasse, `kompetanse` har `compare=False`). Legg til `vakter: tuple[Tidsrom, ...] = ()` og en liten `Tidsrom(start, slutt)`. Ikke endre `Vakt`, `Utelukket`, `Kandidatvurdering` eller `Datafeil`.
- `backend/domene/regelmotor/vurdering.py` -- `REGLER` (l.~50), `Regel`, `vurder_kandidater`. Legg regelen til i `REGLER`. Datafeilsjekken kjører allerede `kandidatkrav` per Kandidat. Ikke endre sorteringen.
- `backend/domene/regelmotor/kompetanse.py` -- mønster for en regelmodul: `ÅRSAK`, `bryter_*`, `*datafeil`. Ny modul `kolliderende_vakt.py` følger samme form.
- `backend/adaptere/lagring/kandidatgrunnlag.py` -- `hent_kandidatgrunnlag` bygger `Kandidat` fra `AnsattRad`. Hent alle `VaktRad` med `tildelt_ansatt_id IS NOT NULL` i én spørring (ikke én per Ansatt), grupper på ansatt-id og legg dem på Kandidaten.
- `backend/adaptere/lagring/modeller.py` -- `VaktRad.tildelt_ansatt_id`, `start`/`slutt` (`OsloTid`). Ikke endre.
- `backend/adaptere/api/main.py` -- ruten `kandidater()` (l.~235) kaller `vurder_kandidater` og trenger ingen endring. `KandidatUt` skal ikke få nye felt.
- `backend/tester/lagring/test_testdata.py` -- `bryter_kollisjon`, `overlapper`, `Data.egne` og `FASIT[nr]["utfall"]` er uavhengig fasit. Brukes bare i tester.
- `backend/tester/regelmotor/test_kompetanse.py` -- mønster for enhetsdata (`vakt()`, `kandidat()`, `vurder()`). `backend/tester/api/test_kandidater.py` -- `forventet_gyldige` (l.~34) filtrerer bare på `kompetanse` og må endres til også å utelate `kolliderende`. Antallene 16 og 21 blir 9 og 19. Docstringen og `test_bare_gyldige_sendes_nfr2` må følge.
- `backend/tester/test_arkitektur.py`, `pyproject.toml` -- import-linter. Den nye modulen under `domene/` faller inn under kontrakten. Ikke endre.
- `frontend/src/tekster.ts` (l.96) og `frontend/tester/kandidater.test.mjs` (l.75) -- teksten `midlertidigMerknad`. `README.md` (l.~173) beskriver merknaden og regelstatus.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/typer.py` -- `Tidsrom` og `Kandidat.vakter` med standardverdi tom -- gir regelen data uten å bryte 2.1
- [x] `backend/domene/regelmotor/kolliderende_vakt.py` -- `ÅRSAK`, `bryter_kollisjon` og `vaktdatafeil` for Kandidatens vakter, tider i UTC -- regelen
- [x] `backend/domene/regelmotor/vurdering.py` -- ny `Regel` i `REGLER` etter kompetanse -- lister alle årsaker i fast rekkefølge
- [x] `backend/adaptere/lagring/kandidatgrunnlag.py` -- én spørring for tildelte vakter, gruppert per Ansatt -- AD-5, ingen N+1
- [x] `backend/tester/regelmotor/test_kolliderende_vakt.py` -- hele matrisen over, determinisme og datafeil -- kravet om en testmodul per regel
- [x] `backend/tester/api/test_kandidater.py` -- fasiten for #4127 (9) og #4189 (19) mot `FASIT`, og at vakter ikke lekker i svaret -- AV-07
- [x] `frontend/src/tekster.ts`, `frontend/tester/kandidater.test.mjs`, `README.md` -- ny merknadstekst og regelstatus
- [x] `docs/ki-logg/2026-11-11-kolliderende-vakt.md`, `docs/emne/vurderingsmatrise.md` -- KI-logg og bevis

**Acceptance Criteria:**
- Given en valgt vakt, when kandidatflaten lastes, then listen er filtrert på både kompetanse og kolliderende vakt, med samme visning som i 2.1.
- Given en Kandidat med overlapp bare etter å ha regnet om til UTC (sommertidsskiftet), when regelen kjører, then utfallet følger faktisk forløpt tid.
- Given en bevisst endring av regelen til lukkede intervall, when `pytest` kjøres, then minst én test feiler. Mutasjonen gjøres én gang og dokumenteres i KI-loggen.
- Given hele pakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then alt består.

## Implementation Notes

- 2026-11-11: Implementert av en underagent fra spec-en alene. Etter to uavhengige gjennomganger (se Review Triage Log): 275 backendtester og 26 frontendtester består, og bygget går gjennom.
- 2026-11-11: Johannes gjorde nettleserkontrollen i Verification manuelt og godkjente den.
- 2026-11-11: Funn A5 er vedtatt som alternativ B. Datafeilsjekken skal bare gjelde Kandidatens vakter i et vindu per regel. Det bygges i story 2.3. Til da validerer 2.2 all tildelt historikk (se avklaringspunktene, §11).

## Spec Change Log

## Review Triage Log

Uavhengig gjennomgang 2026-11-11: blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), alle med Sonnet og uten å ha sett implementeringen. Hvert funn er vurdert mot koden. Diff-filen som gjennomgangsagentene leste, hadde git-advarsler flettet inn midt i linjer (min feil: stderr gikk til filen). Funn om at filen var ødelagt, gjelder bare den kopien.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG | UTC-omregningen i `overlapper` er ikke vernet av noen test | medium: reviewer fjernet begge `astimezone(UTC)` og 120 tester var grønne. Hver av de fem tidstestene gir samme svar på veggklokke. Påstanden «faktisk forløpt tid» er ikke håndhevet. | patch |
| BH | Testkommentar og navn på `test_overlapp_finnes_bare_etter_omregning_til_utc` beskriver to scenarioer og tester ett | low: følger samme rettelse som over. | patch |
| BH, ECH | `compare=False` på `Kandidat.vakter` gjør at determinismetestene ikke ser vaktene | medium: `test_samme_input_gir_samme_output` og ikke-mutasjonstesten kan ikke fange at en vakt endres eller droppes. Rettes i testene, ikke i typen (samme mønster som `kompetanse`). | patch |
| BH | Vakten som vurderes valideres ikke av kollisjonsregelen (`vaktkrav` er tom) | false: `vaktdatafeil` i `vurder_kandidater` sjekker tidssone og start før slutt for alle regler før noen Kandidat vurderes. | avvist |
| ECH | `bryter_kollisjon` kalt direkte med naive tider bruker maskinens lokale sone | low: veien går alltid gjennom datafeilsjekken i `vurder_kandidater`, og en vakt som ikke kan nå funksjonen med naive tider, trenger ikke en guard til. | avvist |
| BH, ECH | Datafeilmeldingen bruker listeposisjon, ikke vaktnummer, så raden kan ikke slås opp | low: `Tidsrom` har ikke id. Fiksen gir en ny offentlig flate på domenetypen, og grunnene brukes bare til logg. | avvist |
| BH, ECH | Én ugyldig historisk vakt stopper alle kandidatlister | false: det er vedtatt i P-08 (ukjent historikk er ikke fri) og står i spec-ens Always. Testen låser det med vilje. | avvist |
| BH, ECH | Spørringen henter alle tildelte vakter uten periode eller turnus | low: v1 har én turnus (AV-06), og Intent sier uavhengig av periode. `order_by` er uskadelig. | avvist |
| BH, VG | `hent_kandidatgrunnlag` er ikke testet direkte | low: fasittallene 9 og 19 feiler hvis `vakter` droppes. VG fant dekningen tilstrekkelig. Tidssone fra SQLite dekkes av `OsloTid`-testene fra 1.2. | avvist |
| BH | AGENTS.md sier «den første harde regelen … story 2.1» | low: stemmer ikke lenger. Rettingen gjelder en agentkontekstfil. | defer |
| BH, ECH | `test_vakter_lekker_ikke_i_svaret` bruker delstrenger i `str(svar)` | low: nøkkelsettene for svaret og hver Kandidat er allerede sjekket i `test_gyldige_stemmer_med_fasiten` og `test_alfabetisk_med_kompetansenivå_for_vakttypen`. | avvist |
| BH | Magiske tall og at fasitnøkkelen `"kolliderende"` ikke er koblet til `ÅRSAK` | low: fasiten er uavhengig av koden med vilje (AV-07). | avvist |
| BH, ECH | `Kandidat(vakter=None)` gir `TypeError`, og `_har_offset` gir «mangler tidssone» for ikke-datetime | low: adapteren sender alltid tupler av `Tidsrom`. En guard legger til en gren uten kjent vei dit. | avvist |
| BH | `_vakt` i `kollisjonsdatafeil` er ubrukt | false: parameteren kreves av `Regel.kandidatkrav`, og `kompetansedatafeil` har samme form. | avvist |
| BH | Diff-filen er ødelagt av git-advarsler | false for koden: arbeidsfilene parser og 271 tester består. Feilen lå i hvordan jeg skrev diff-filen. | avvist |

Andre gjennomgang 2026-11-11 med `bmad-review`: adversarial (A), edge-case-hunter (EC) og verification-gap (VG), alle med Opus og uten å ha sett gjennomgangen over. Tallet 271 i første gjennomgang gjaldt før de to `fold`-testene, som ga 273.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG | Ingen test viser at egne vakter hentes uavhengig av periode | medium: reviewer avgrenset spørringen til perioden og 273 var grønne. Ny API-test, og mutasjonen gir nå 1 rød. | patch |
| VG | Datafeil for ugyldig tildelt vakt er ikke testet ende til ende | medium: bare domenetester. Ny API-test, og et filter på `start < slutt` i adapteren gir nå 1 rød. | patch |
| EC | Vaktens egen rad blir egen vakt ved ny kontroll i Epic 3 | low nå: CHECK-kravet gjør at en vakt med tildelt Ansatt ikke mangler bemanning, og `finn_ubemannet_vakt` krever det. Gjelder 3.2. | defer |
| EC | `kompetanse={}` blir full kompetanse i testhjelperen | low: ingen test bruker det, men rettingen er én linje. | patch |
| EC, A | Mutasjonstallet 13 og «gjennomgang gjenstår» i KI-logg og vurderingsmatrise | low: kjørt på nytt, 14 av 124. Tekstene oppdatert. | patch |
| A | Spec `done` mot sprint-status `review` | false: samme mønster som 2.1. Spec-en er `done` når `bmad-build` er ferdig, og sprint-status går til `done` etter PR-godkjenning. | avvist |
| A | All historikk valideres, mens P-08 sier «nødvendig» grunnlag | maybe-false: avhenger av hvordan gruppa leser P-08. Lagt fram for gruppa i PR-en. | avklaring |
| A | NFR2-testene forbyr årsaker som 2.5 skal vise | low: 2.5 avgjør formen. Testene beskriver kontrakten fram til da. | avvist |
| A | `compare=False` på alt regelgrunnlag | low: dekket av `vakter_i` i testene. Kan tas opp i 2.3 når flere regler leser `vakter`. | avvist |
| A | `epic-2-context.md` beskriver tilstanden før 2.2 og mistet punkter | low: konteksten kompileres på nytt når planleggingsfilene endres, og 2.3 leser også spec-en for 2.2. | avvist |
| A | Spørringen er uten avgrensning, og datafeilgrunnen har listeposisjon | low: samme som i første gjennomgang. | avvist |
| A | Regelnøkler skrevet inn direkte i API-testen, og grensetabellen kaller `bryter_kollisjon` direkte | low: 2.3 endrer `IMPLEMENTERTE_REGLER` uansett. Koblingen dekkes av fasit- og rekkefølgetestene. | avvist |
| A | «kompetanse» i merknaden mot «kompetanse-minstekrav» | low: merknaden fjernes i 2.4. | avvist |
| A | AGENTS.md er utdatert, og `lambda` i `REGLER` | low: AGENTS.md er allerede utsatt. `lambda` er kosmetisk. | avvist |

## Design Notes

`Tidsrom` er egen type, ikke `Vakt`, fordi Kandidatens vakter ikke trenger vaktnummer, vakttype eller minstenivå, og fordi 2.3 og 2.4 trenger samme type for nabovakter og uker. Da 2.3 og 2.4 utvider grunnlaget, kan `Kandidat.vakter` brukes direkte.

## Verification

**Commands:**
- Fra `backend/`: `.venv\Scripts\python -m pytest` -- alle tester består, også import-linter.
- Fra `frontend/`: `npm.cmd run build` og `npm.cmd test` -- alt består.

**Manual checks:**
- Logg inn, velg #4127 og #4189 og kontroller at listene har 9 og 19 kandidater, og at ingen av dem med `kolliderende` i fasiten vises.
