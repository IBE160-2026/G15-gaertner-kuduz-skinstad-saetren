---
title: 'Story 1.2: Fiktiv turnus med ansatte og vakter'
type: 'feature'
created: '2026-10-24'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/AGENTS.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Backenden har verken lagring eller data. Story 1.3–1.6 og Epic 2, 4 og 5 trenger en fiktiv turnus med kjente scenarioer.

**Approach:** SQLAlchemy-modeller for Turnus, Vakt og Ansatt i `adaptere/lagring` på SQLite. En idempotent kommando fyller én turnus: Kirurgisk sengepost, uke 39–40 2026, med 25 Ansatte. En fasit sier hvilken hard regel som utelukker hvem på #4127 og #4189, og tester sjekker den mot dataene.

## Boundaries & Constraints

**Always:**
- Bare tabellene `turnus`, `vakt` og `ansatt`, eid av `adaptere/lagring` (AD-5). `domene/` røres ikke.
- Tidspunkt lagres som ISO 8601 med offset og leses som aware `datetime` i `ZoneInfo("Europe/Oslo")`, aldri med fast offset.
- Perioden er man. 21.09.2026 00:00 til søn. 04.10.2026 24:00.
- Navnene fra mockupene beholdes. Kari Vestby er turnusansvarlig, ikke Ansatt. Er mockup og PRD uenige, gjelder PRD §4.3 og FR-2. Timene justeres så kostnadsmerkingen stemmer.
- Databasestien kommer fra `TURNUSHJELPEREN_DB`, med standardverdi `backend/turnushjelperen.db` (gitignorert).

**Never:** brukertabell (story 1.3), API-endepunkter, regelmotor i `domene/`, ekte personopplysninger, og noen annen kodevei enn seedingen som markerer en vakt som bemannet.

**Beslutninger:**
- #4127 ligger søndag 27.09.2026. Mockupens «lørdag» er feil og rettes i UI-storiene.
- Kompetansenivået er et heltall 1–4 per vakttype: Under opplæring, Delvis opplært, Kvalifisert, Fullt kvalifisert. Mangler nivået, er den ansatte ikke opplært for vakttypen. Hver Vakt har et minstenivå.
- `python -m adaptere.lagring.testdata` fra `backend/` tømmer og fyller de tre tabellene i én transaksjon. `create_all`, uten migreringsverktøy. ID-ene er heltall, og vaktnummeret er et eget unikt felt.
- Sist oppdatert er 27.09.2026 06:20.
- 24 kandidater vurderes per vakt, fordi den som var satt opp ikke regnes med.
- Timelønnen er kr 350–420. Overtid er timer over 36 per kalenderuke, til 150 %. Overtidssatsen lagres ikke.
- (2026-11-02, besluttet av gruppa, erstatter PR #4-tidene fra 2026-10-30) Alle vakter er 8 timer: dag 07:00–15:00, mellom 10:00–18:00, kveld 15:00–23:00 og natt 23:00–07:00. Vakter som møtes i et skift, kolliderer ikke, fordi vaktene er halvåpne intervaller.
- (2026-10-30) Turnus har `periode_start` og `periode_slutt` som halvåpent intervall [21.09.2026 00:00, 05.10.2026 00:00). En Vakt hører til perioden når den starter innenfor.
- (2026-11-02, erstatter «legges til når PR #4 er merget») PR #4 er merget. Vakthistorikk 24.08–20.09 for alle Ansatte, turnusprofiler og ulempescenarioet er med i denne storien.
- (2026-11-02, AV-10) Historikken er et fast, eksplisitt sett med Vakter i dataene. Den lages ikke av noen generator eller noe mønster i kode.
- (2026-11-02, AV-09, erstatter «28 døgn») Ulempepoeng måles over de 672 faktiske timene før vaktens start, som halvåpent intervall [start − 672 t, start). En Vakt som krysser grensen, telles bare med delen innenfor. For #4127 er vinduet [30.08 07:00, 27.09 07:00).
- (2026-11-02, AV-12, erstatter «nesten lik») Ulempescenarioet ligger på #4127. Mette Solberg og Jonas Bakke har identisk timelønn (kr 370), identiske timer i uke 39 (16) og identiske preferansepoeng (75), men ulik Ulempebelastning (180 mot 40 poeng). Forventet forskjell i totalscore er 7,0 poeng.
- (2026-11-02, AV-07) `FASIT` har også forventet rangering og totalscore for #4127, beregnet på forhånd og ikke hentet fra programmet. Sorteringen bruker uavrundet totalscore, og ved lik totalscore stigende ansatt-ID (AV-05, K-03).
- (2026-11-02, erstatter 13 · 8 · 3) De 24 utelukkede på #4189 fordeles 2 kolliderende, 18 elleve-timer, 3 kompetanse og 1 trettifem-timer.
- (2026-11-02, besluttet av gruppa) Fjerde vakttype: mellomvakt 10:00–18:00 (`mellom`). Den bruker Kompetansenivået for dag og har ingen egen nøkkel i kompetansen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Første kjøring | Ingen databasefil | 1 Turnus, 25 Ansatte, Vakter i hele perioden, bare de tre tabellene | N/A |
| Ny kjøring | Fylt database | Samme radtall, ingen duplikater | N/A |
| #4127 | Dagvakt 27.09 07–15, krav 3 | Mangler bemanning. Silje satt opp, meldte fra 27.09 06:14. Minst 3 gyldige ifølge fasiten | N/A |
| #4189 | Natt 28.09 23:00–29.09 07:00 | Mangler bemanning. Alle 24 utelukkes, og hver grunn stemmer med dataene | N/A |
| Overtid | Gyldig kandidat på #4127 | Timer i uke 39 + 8 > 36 | N/A |
| Billigste ikke øverst | Gyldige på #4127 | Billigste har høyest belastning eller dårligst preferanse | N/A |
| Ansatt-felt | Hvilken som helst Ansatt | Navn, stilling, ansiennitet, timelønn, minst ett nivå | N/A |
| Tidssone | Vakt lest tilbake | `tzinfo` er Europe/Oslo og klokkeslettet er uendret | N/A |
| Historikk | Vakter med start før 21.09 | Hver Ansatt har tildelte Vakter fra 24.08. Ingen mangler bemanning, og alle starter før periodestart | N/A |
| Ulempespredning | Ulempepoeng for hver Ansatt i vinduet til #4127 | Laveste ≤ 10, høyeste > 250 | N/A |
| Ulempescenario | Jonas og Mette på #4127 | Identisk timelønn, timer og preferanse. Ulempepoeng nøyaktig 40 og 180 | N/A |
| Rangeringsfasit | Gyldige på #4127 | Data for timelønn, timer, preferanse og Ulempepoeng er nøyaktig de verdiene `FASIT` er beregnet fra | N/A |

</frozen-after-approval>

## Code Map

- `backend/adaptere/lagring/__init__.py` -- tom, finnes. Nye moduler legges ved siden av.
- `backend/domene/`, `backend/adaptere/api/main.py`, `backend/adaptere/ki/` -- røres ikke.
- `backend/tester/test_helse.py` -- testmønster: absolutt import fra `backend/`-roten, norske testnavn, `-> None`, ren `assert`. `tester/regelmotor/__init__.py` viser at undermapper har tom `__init__.py`.
- `backend/pyproject.toml` -- `testpaths=["tester"]`, `pythonpath=["."]`. Endres ikke.
- `backend/requirements.txt` -- eksakt låste versjoner. `.venv` er Python 3.14 uten sqlalchemy og tzdata.
- `.gitignore` mangler `*.db`. `.env.example` i roten har bare OpenRouter-variablene.
- `AGENTS.md` -- «Kjøring og verifisering», punktet om backend. Innledningen sier «ingen domenelogikk ennå».
- `docs/ki-logg/2026-10-19-prosjektoppsett.md` -- mal for KI-loggen.
- `scripts/ulempe_regneeksempler.py` -- regner Ulempepoeng etter PRD §4.3 med gruppas vakttider. Er referanse for testhjelperen for ulempe, og røres ikke.
- Ulempemodellen (PRD §4.3) som testhjelperen implementerer: per time 0 for hverdag 06–18, 1 for hverdag 18–22, 2 for helg 06–22 og 3 for natt 22–06. Hver time telles én gang med høyeste kategori, med minuttoppløsning. Vinduet er de 672 faktiske timene før vaktens start (AV-09), som i PRD §4.3 og story 4.7.
- Harde regler (epics.md, story 2.1–2.4) som testhjelperne implementerer:
  - **Kompetanse:** nivået for vakttypen mangler eller er under minstenivået. For `mellom` slås nivået for `dag` opp.
  - **Kolliderende vakt:** overlapp ≥ 1 min på halvåpne `[start, slutt)`.
  - **Elleve-timer:** nærmeste ikke-overlappende vakt før eller etter gir under 11 t hvile i reell tid. Overlappende vakter hører bare til kollisjonsregelen.
  - **Trettifem-timer:** med vakten lagt til mangler en berørt kalenderuke (man.–søn.) 35 t sammenhengende fri. Fritiden regnes fra unionen av vaktene.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/requirements.txt` -- legg til `sqlalchemy==2.1.6` og `tzdata==2026.5`. tzdata trengs fordi Windows mangler IANA-databasen.
- [ ] `backend/adaptere/lagring/database.py` -- `lag_engine(sti=None)`:
  - leser `TURNUSHJELPEREN_DB`. En relativ sti tolkes fra arbeidsmappen.
  - Uten variabel brukes `turnushjelperen.db` i `backend/`, uavhengig av arbeidsmappe.
  - I tillegg sessionmaker og `opprett_skjema(engine)`.
- [ ] `backend/adaptere/lagring/modeller.py` -- TypeDecoratoren `OsloTid` avviser naive `datetime`.
  - `TurnusRad`: `avdeling`, `periode_start`, `periode_slutt`, `sist_oppdatert`.
  - `AnsattRad`: navn, stilling, ansiennitet, timelønn, `kompetanse` som JSON `{"dag"|"kveld"|"natt": nivå}` og valgfri `preferanse`.
  - `VaktRad`: `turnus_id`, `vaktnummer`, `vakttype` (`dag`, `mellom`, `kveld` eller `natt`), `start`, `slutt`, `minstenivå`, `tildelt_ansatt_id`, `mangler_bemanning`, `satt_opp_ansatt_id`, `meldt_fra` og `meldt_fra_grunn`.
- [ ] `backend/adaptere/lagring/testdata.py` -- Ansatte med faste ID-er 1–25, uten tilfeldighet.
  - Både vaktene i perioden og historikken 24.08–20.09 er faste, eksplisitte data, uten generator (AV-10). Historikken får vaktnumre i serien #3000–#3999.
  - `FASIT`: vaktnummer → ansattnavn → regel eller «gyldig». For #4127 også forventet rekkefølge og uavrundet totalscore fra designnotatene (AV-07).
  - `fyll_testdata(session)` og `__main__`, som skriver radtallene.
- [ ] `backend/tester/lagring/__init__.py` og `test_testdata.py` -- tester matrisen mot en database i `tmp_path`. Hjelpefunksjonene for de fire reglene og for Ulempepoeng ligger bare i testen.
- [ ] `.env.example`, `.gitignore` (`*.db`), `AGENTS.md`, `README.md` -- dokumenter variabelen og kommandoen. I AGENTS.md: slett databasefilen når skjemaet endres.
- [ ] `docs/ki-logg/<dato>-testdata.md` -- KI-logg etter malen.

**Acceptance Criteria:**
- Given hele testpakken, when `pytest` kjøres, then består alle testene, også `test_helse`.
- Given fasiten, when testen sjekker en utelukket Ansatt, then bryter vedkommende nøyaktig regelen fasiten oppgir og ingen annen, og hver gyldig Ansatt bryter ingen.
- Given alle tildelte Vakter, også historikken, when reglene kjøres per Ansatt, then har ingen Ansatt overlapp, hvile under 11 t eller en kalenderuke uten 35 t sammenhengende fri.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

**Bemanning:** omtrent 13 på jobb per døgn, for eksempel 5 dag, 2 mellom, 3 kveld og 3 natt, med færre i helgen. Mellomvakter gir naturlige utelukkelser: søndag 27.09 kolliderer med #4127, og mandag 28.09 og tirsdag 29.09 gir 5 t og 3 t hvile rundt #4189. Det gir omtrent 180 Vakter i perioden, i serien #4100–#4299, og omtrent 350 i historikken. Mockupens vakter beholder nummer, Ansatt og dato:
- #4128: kveld 27.09, Per Halvorsen.
- #4130: dag 28.09, Mette Solberg.
- #4131: natt 28.09, Thomas Nygård.
- #4135: dag 29.09, Jonas Bakke.
- #4136: kveld 29.09, Ingrid Dahl.

Grunnturnusen følger selv reglene. Kveld kan for eksempel aldri etterfølges av dag neste morgen, fordi det gir 8 t hvile.

**Gyldige på #4127** (timer i uke 39 uten #4127, bare dagvakter på hverdager):

| Ansatt | Nivå dag | Kr/t | Timer | Kostnad | Preferanse (PRD nr.) | Ulempepoeng (eksakt) | På #4189 |
|---|---|---|---|---|---|---|---|
| Jonas Bakke | 3 | 370 | 16 | ordinær | 4 (75) | 40 | elleve-timer (#4135, 0 t) |
| Mette Solberg | 4 | 370 | 16 | ordinær | 5 (75) | 180 | elleve-timer (#4130, 8 t) |
| Thomas Nygård | 3 | 350 | 24 | ordinær, billigst | 13 (0) | 120 | kolliderer (#4131) |
| Ingrid Dahl | 4 | 385 | 32 | overtid, 89 % | 1 (100) | 60 | elleve-timer (#4136, 8 t) |

- De fire har ingen vakt som slutter etter 26.09 20:00, og ingen som starter før 28.09 02:00.
- **Rangeringsfasit for #4127** (AV-07, beregnet på forhånd med vektene 40/20/15/25 og formlene i PRD §4.4, som er kontrollert etter KS-02):

  | Plass | Ansatt | Kostnad (kr) | Totalscore, uavrundet | Visning |
  |---|---|---|---|---|
  | 1 | Jonas Bakke | 2960 | 85,654761… | 85,7 |
  | 2 | Mette Solberg | 2960 | 78,654761… | 78,7 |
  | 3 | Thomas Nygård | 2800 | 59,0 | 59,0 |
  | 4 | Ingrid Dahl | 3850 (4 t overtid) | 37,0 | 37,0 |

  - Jonas og Mette har like kostnadspoeng (84,76), timepoeng (100) og preferansepoeng (75). Ulempescore er 86,67 mot 40,00. Forskjellen er 0,15 × 46,67 = **7,0 totalpoeng** (AV-12). Uten ulempe ville de stått likt, og da avgjør stigende ansatt-ID (AV-05).
  - Med nøytral preferanse for alle (Epic 5 ikke på plass) blir det Jonas 79,40, Mette 72,40, Thomas 71,50 og Ingrid 24,50. Thomas er fortsatt ikke øverst.
  - Testene i 1.2 sjekker at dataene gir nøyaktig disse inputene. Selve rangeringen testes i story 4.4.
- Ingrid skal vises med høy belastning. Story 4.2 setter grensen så 32 t regnes som høy.
- Thomas står på 2/4 i mockupen, men det strider mot FR-2, så han får nivå 3.

**Utelukket på #4127 (20):**
- 7 kolliderende: dag og mellom 27.09, for eksempel 5 + 2.
- 4 elleve-timer:
  - natt 26.09 23:00–27.09 07:00, som berører #4127 uten å kollidere (0 t hvile)
  - kveld 26.09 (8 t)
  - kveld 27.09 med Per (0 t)
  - natt 27.09 23:00 (8 t)
- 8 kompetanse og 1 trettifem-timer.

**Utelukket på #4189 (24):**
- 2 kolliderende: natt 28.09, blant dem Thomas.
- 18 elleve-timer:
  - dag, mellom og kveld 28.09 (8 t, 5 t og 0 t hvile)
  - dag, mellom og kveld 29.09 (0 t, 3 t og 8 t)
- 3 kompetanse. Silje Amundsen er en av dem, fordi hun mangler nivå for natt.
- 1 trettifem-timer: med #4189 lagt til mangler uke 40 35 t sammenhengende fri.
- Satt opp var Eirik Moen, som meldte fra 26.09 21:40 med grunnen «sykemeldt». Silje har samme grunn.

**Ellers:**
- Stillingene er Sykepleier, Spesialsykepleier og Helsefagarbeider.
- Preferansetekstene hentes ordrett fra PRD-tabellen. Noen Ansatte har ingen.
- Minstenivået er 3 for #4127 og #4189.
- Ingen bryter flere regler på samme vakt. Det er bevisst, for at fasiten skal bli entydig.
- Paret «like unntatt kompetanse» (story 4.4) og paret for story 5.2 er enhetstestdata i domenet. Ulempeparet er Jonas og Mette i seeden.

**Turnusprofiler** (Ulempepoeng i vinduet til #4127):
- bare dag på hverdager: ca. 0
- dag og mellom med hver tredje helg: ca. 50–80
- tredelt: ca. 120–180
- kveldstung: ca. 150
- natt-tung: over 250

Profilene velges så fasiten for #4127 og #4189 står seg. Ulempepoeng per vakt på hverdag:
- dag og mellom: 0
- kveld: 7
- natt: 21

I helgen:
- dag og mellom: 16
- kveld: 17
- natt som går inn i eller ut av helgen: 21–23

Eksakte summer som 40, 60, 120 og 180 lar seg derfor sette sammen av hele vakter.

KS-04 (datadekning ved periodegrensene) er ikke kontrollert. Det finnes ingen vakter etter natten 04.10–05.10. Det holder for #4127 og #4189, men ikke for regelsjekk av vakter i slutten av perioden. Historikken slutter 20.09 og påvirker bare elleve- og trettifem-timersregelen i begynnelsen av uke 39. Testen regner alle reglene over hele datasettet.

## Verification

**Commands:**
- `.venv\Scripts\python -m pip install -r requirements-dev.txt` -- expected: sqlalchemy og tzdata installeres.
- `.venv\Scripts\python -m pytest` -- expected: alle tester består.
- `.venv\Scripts\python -m adaptere.lagring.testdata` to ganger -- expected: like radtall begge gangene.
