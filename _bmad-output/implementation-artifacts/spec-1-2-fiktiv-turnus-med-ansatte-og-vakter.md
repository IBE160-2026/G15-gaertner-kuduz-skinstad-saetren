---
title: 'Story 1.2: Fiktiv turnus med ansatte og vakter'
type: 'feature'
created: '2026-10-24'
status: 'draft'
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
- (2026-10-30) Vakttidene følger PR #4: dag 07:00–15:00, kveld 15:00–22:30, natt 22:00–07:30. Vaktskiftene overlapper, og overlapp er kolliderende vakt.
- (2026-10-30) Turnus har `periode_start` og `periode_slutt` som halvåpent intervall [21.09.2026 00:00, 05.10.2026 00:00). En Vakt hører til perioden når den starter innenfor.
- (2026-10-30) 1.2 bygges på `main`. Historikk fra 24.08 og ulempescenarioet fra PR #4 legges til seedingen når PR #4 er merget.
- (2026-10-30) De 24 utelukkede på #4189 fordeles 13 kolliderende, 8 elleve-timer og 3 kompetanse.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Første kjøring | Ingen databasefil | 1 Turnus, 25 Ansatte, Vakter i hele perioden, bare de tre tabellene | N/A |
| Ny kjøring | Fylt database | Samme radtall, ingen duplikater | N/A |
| #4127 | Dagvakt 27.09 07–15, krav 3 | Mangler bemanning. Silje satt opp, meldte fra 27.09 06:14. Minst 3 gyldige ifølge fasiten | N/A |
| #4189 | Natt 28.09 22:00–29.09 07:30 | Mangler bemanning. Alle 24 utelukkes, og hver grunn stemmer med dataene | N/A |
| Overtid | Gyldig kandidat på #4127 | Timer i uke 39 + 8 > 36 | N/A |
| Billigste ikke øverst | Gyldige på #4127 | Billigste har høyest belastning eller dårligst preferanse | N/A |
| Ansatt-felt | Hvilken som helst Ansatt | Navn, stilling, ansiennitet, timelønn, minst ett nivå | N/A |
| Tidssone | Vakt lest tilbake | `tzinfo` er Europe/Oslo og klokkeslettet er uendret | N/A |

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
- Harde regler (epics.md, story 2.1–2.4) som testhjelperne implementerer:
  - **Kompetanse:** nivået for vakttypen mangler eller er under minstenivået.
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
  - `VaktRad`: `turnus_id`, `vaktnummer`, `vakttype`, `start`, `slutt`, `minstenivå`, `tildelt_ansatt_id`, `mangler_bemanning`, `satt_opp_ansatt_id`, `meldt_fra` og `meldt_fra_grunn`.
- [ ] `backend/adaptere/lagring/testdata.py` -- Ansatte med faste ID-er 1–25 og Vakter som faste data, uten tilfeldighet.
  - `FASIT`: vaktnummer → ansattnavn → regel eller «gyldig».
  - `fyll_testdata(session)` og `__main__`, som skriver radtallene.
- [ ] `backend/tester/lagring/__init__.py` og `test_testdata.py` -- tester matrisen mot en database i `tmp_path`. Hjelpefunksjonene for de fire reglene ligger bare i testen.
- [ ] `.env.example`, `.gitignore` (`*.db`), `AGENTS.md`, `README.md` -- dokumenter variabelen og kommandoen. I AGENTS.md: slett databasefilen når skjemaet endres.
- [ ] `docs/ki-logg/<dato>-testdata.md` -- KI-logg etter malen.

**Acceptance Criteria:**
- Given hele testpakken, when `pytest` kjøres, then består alle testene, også `test_helse`.
- Given fasiten, when testen sjekker en utelukket Ansatt, then bryter vedkommende nøyaktig regelen fasiten oppgir og ingen annen, og hver gyldig Ansatt bryter ingen.
- Given alle tildelte Vakter, when reglene kjøres per Ansatt, then har ingen Ansatt overlapp, hvile under 11 t eller en kalenderuke uten 35 t sammenhengende fri.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

**Bemanning:** omtrent 13 på jobb per døgn, for eksempel 6 dag, 4 kveld og 3 natt. Det gir omtrent 180 Vakter. Vaktnumrene ligger i serien #4100–#4299. Mockupens vakter beholder nummer, Ansatt og dato:
- #4128: kveld 27.09, Per Halvorsen.
- #4130: dag 28.09, Mette Solberg.
- #4131: natt 28.09, Thomas Nygård.
- #4135: dag 29.09, Jonas Bakke.
- #4136: kveld 29.09, Ingrid Dahl.

Grunnturnusen følger selv reglene. Kveld kan for eksempel aldri etterfølges av dag neste morgen, fordi det gir 8,5 t hvile.

**Gyldige på #4127** (timer i uke 39 uten #4127, bare dagvakter på hverdager):

| Ansatt | Nivå dag | Kr/t | Timer | Kostnad | Preferanse (PRD nr.) | På #4189 |
|---|---|---|---|---|---|---|
| Jonas Bakke | 3 | 370 | 16 | ordinær | 4 (75) | kolliderer (#4135) |
| Thomas Nygård | 3 | 350 | 24 | ordinær, billigst | 13 (0) | kolliderer (#4131) |
| Mette Solberg | 4 | 395 | 24 | ordinær | 10 (25) | elleve-timer (#4130) |
| Ingrid Dahl | 4 | 385 | 32 | overtid, 89 % | 1 (100) | elleve-timer (#4136) |

- De fire har ingen vakt som slutter etter 26.09 20:00, og ingen som starter før 28.09 02:00.
- Rekkefølgen blir Jonas, Thomas, Mette, Ingrid. Det gjelder med vektene på `main` (40/35/25) og med vektene i PR #4 (40/20/15/25), både med og uten preferanser.
- Ingrid skal vises med høy belastning. Story 4.2 setter grensen så 32 t regnes som høy.
- Thomas står på 2/4 i mockupen, men det strider mot FR-2, så han får nivå 3.

**Utelukket på #4127 (20):**
- 7 kolliderende: 4 på dag 27.09 og 3 på natt 26.09 22:00–27.09 07:30.
- 4 elleve-timer: kveld 26.09, som gir 8,5 t hvile; kveld 27.09 med Per, som gir 0 t; og natt 27.09, som gir 7 t.
- 8 kompetanse og 1 trettifem-timer.

**Utelukket på #4189 (24):**
- 13 kolliderende: natt 28.09, kveld 28.09 og dag 29.09.
- 8 elleve-timer: dag 28.09 og kveld 29.09.
- 3 kompetanse. Silje Amundsen er en av dem, fordi hun mangler nivå for natt.
- Satt opp var Eirik Moen, som meldte fra 26.09 21:40 med grunnen «sykemeldt». Silje har samme grunn.

**Ellers:**
- Stillingene er Sykepleier, Spesialsykepleier og Helsefagarbeider.
- Preferansetekstene hentes ordrett fra PRD-tabellen. Noen Ansatte har ingen.
- Minstenivået er 3 for #4127 og #4189.
- Ingen bryter flere regler på samme vakt. Det er bevisst, for at fasiten skal bli entydig.
- Parene for story 4.4 og 5.2 er enhetstestdata i domenet.

## Verification

**Commands:**
- `.venv\Scripts\python -m pip install -r requirements-dev.txt` -- expected: sqlalchemy og tzdata installeres.
- `.venv\Scripts\python -m pytest` -- expected: alle tester består.
- `.venv\Scripts\python -m adaptere.lagring.testdata` to ganger -- expected: like radtall begge gangene.
