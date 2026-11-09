---
title: 'Story 1.6: Velge vakten som skal bemannes'
type: 'feature'
created: '2026-11-09'
status: 'done'
baseline_commit: 'f8b0efbfc430deebfd8f4e16dd19e3c6703f1037'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Knappen på en vakt som mangler bemanning går til `/vakt/<nr>/kandidater`, men adressen viser «Fant ikke siden». Turnusansvarlig kan dermed ikke se hvilken vakt og hvilket kompetansekrav hun arbeider med (FR1).

**Approach:** Vis en beskyttet kandidatflate på den eksisterende adressen. Den henter den valgte vakten fra innlogget brukers turnus, viser tidspunkt og kompetansekrav, og har en tydelig plassholder fram til Epic 2 leverer kandidater.

## Boundaries & Constraints

**Always:** API-et returnerer bare en vakt som både tilhører innlogget brukers turnus, mangler bemanning og starter i turnusens halvåpne visningsperiode (AV-03). Tidspunkter sendes som ISO 8601 med offset og vises i `Europe/Oslo`. Feil følger `{kode, melding}` (AD-4); frontend viser sin egen nøytrale tekst, ikke backendens melding. Brødsmulestien viser `Turnus > <avdeling> > Vakt #<nr> — <vakttype> <dato>` (UX-DR3). Eksisterende «Velg vakt»-knapper forblir bare på vakter under «Krever handling» (UX-DR5).

**Never:** Endre vakt eller testdata, vise kandidatnavn eller falske kandidatresultater, starte KI-kall, eller implementere regler/rangering fra senere epics. Ingen ny databasetabell eller migrering.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Valgt vakt | Innlogget bruker åpner #4127 eller #4189 | Egen URL; avdeling, vakttype, start/slutt og `minstenivå` vises; kandidatplassholder | Ingen |
| Direkte URL | Eksisterende vakt i perioden som er bemannet, vakt utenfor perioden eller ukjent nummer | Ingen vaktdetaljer | 404 `ikke_funnet`; nøytral tekst fra frontendlisten |
| Annen turnus | Vakt tilhører ikke brukerens turnus | Ingen vaktdetaljer | 404 `ikke_funnet` |
| Sesjon | Manglende/utløpt sesjon | Ingen vaktdetaljer; innloggingsflaten vises | 401 `mangler_sesjon` via eksisterende vern |
| Feil | Nettverksbrudd eller serverfeil | Nøytral feilmelding og «Prøv igjen» | Ingen backendmelding vises |

</frozen-after-approval>

## Code Map

- `backend/adaptere/lagring/modeller.py` — `VaktRad` har `vaktnummer`, `turnus_id`, `mangler_bemanning`, Oslo-tid og `minstenivå`; `BrukerRad.turnus_id` eier tilgang. Ikke endre skjema.
- `backend/adaptere/lagring/vaktoversikt.py` — mønster for turnusoppslag og periodefilter; lag eget lesende detaljoppslag i lagringsadapteren.
- `backend/adaptere/api/main.py` — `lag_app`, `Okt`, sesjonsmiddleware, `feil()` og Pydantic-svar; `/api/vaktoversikt` er rutemønsteret.
- `backend/tester/api/test_vaktoversikt.py` og `test_innlogging.py` — testklient og innloggingsfixturer med midlertidig database.
- `frontend/src/App.tsx` — `velgVakt` lager allerede URL; routingen viser nå «Fant ikke siden». `popstate` bruker `kontroller()`.
- `frontend/src/komponenter/Vaktvalg.tsx` — mønster for lasting, feil, retry/fokus, 401 og sesjonsgenerasjon. `Brodsmulesti.tsx` brukes om igjen.
- `frontend/src/api.ts`, `format.ts`, `tekster.ts` — beskyttet `kall`, Oslo-formatering og all brukertekst. `app.css` må bruke tokens fra `tokens.css` (AV-13).

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/lagring/vaktdetaljer.py` — les valgt vakt innenfor brukerens turnus og periode, bare når den mangler bemanning; returner data uten kandidater.
- [x] `backend/adaptere/api/main.py` — legg til beskyttet `GET /api/vakter/{vaktnummer}` med Pydantic-svar og 404 i felles feilform.
- [x] `backend/tester/api/test_vaktdetaljer.py` — test matrisen på API-siden, inkludert annen turnus/periode og ingen data ved avvisning.
- [x] `frontend/src/api.ts`, `App.tsx`, `komponenter/Kandidatflate.tsx` — hent detaljene, rute direkte URL/tilbakeknapp og vis lasting, 404, 401, retry og plassholder.
- [x] `frontend/src/tekster.ts`, `format.ts`, `stil/tokens.css`, `stil/app.css` — vis norsk vakttekst, kompetansekrav, brødsmulesti og nøktern plassholder uten rå mål utenfor tokens.
- [x] `frontend/tester/` — test rutetolkning og formatering der funksjonene har meningsfull logikk.
- [x] `README.md`, `docs/ki-logg/2026-11-09-vaktdetaljer.md`, `docs/emne/vurderingsmatrise.md`, `sprint-status.yaml` — dokumenter flyt, KI-arbeid, bevis og reell status.

**Acceptance Criteria:**
- Given en innlogget bruker på Vaktvalg, when hun velger #4127, then kandidatflaten viser riktig vakt, tidspunkt, kompetansekrav og plassholder uten kandidater.
- Given en gyldig detalj-URL, when siden lastes direkte eller via tilbakeknappen, then samme vakt vises under riktig brødsmulesti.
- Given 360 px, 1600 px og 20 px standard skriftstørrelse, when flaten vises, then teksten er lesbar uten klipping eller vannrett siderulling.
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then består alt.

## Implementation Notes

- 2026-11-09: Lesende detaljoppslag er lagt i lagringsadapteren med 404 for ukjent, bemannet, historisk og annen turnus. Felles sesjonsvern tar 401. Kandidatflaten viser ingen kandidatdata.
- 2026-11-09: Nettleserkontroll med simulerte API-svar er dokumentert i `../../docs/ki-logg/2026-11-09-vaktdetaljer-nettleserkontroll.md`. Den dekker direkte URL, tilbakeknapp, 404, 401, 500/retry og layout ved 360/1600 px og 20 px standardskrift. API-testene dekker tilgang og periodegrenser mot testdatabasen.

## Spec Change Log

## Review Triage Log

Uavhengig gjennomgang 2026-11-09: blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG). Hvert funn er vurdert mot kode og dokumenterte kontroller.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| BH | Ingen egen tilbake-lenke fra kandidatflaten | low: Direkte URL har ingen app-lenke til Vaktvalg, men normalflyten går via Vaktvalg og nettleserens tilbakeknapp er kontrollert. Ny navigasjon er mer enn en enkel korreksjon for et sjeldent tilfelle. | avvist |
| BH | Brødsmule mangler under lasting/feil | low: `Kandidatflate` viser den eksakte brødsmulen bare med vaktdetaljer. En 404 kan ikke ha korrekt vakttype og dato; en generisk brødsmule i korte/uvanlige tilstander krever en ny variant. Den godkjente vaktflaten viser brødsmulen som krevd. | avvist |
| BH | «Minstenivå 3» mangler skala | low: Dataene bruker nivå 1–4 (`testdata.py`), og teksten sier ikke maksimum. En direkte tekstendring kan gjøre kravet klarere. | patch |
| BH | 401 under detaljoppslaget er ikke nettlesertestet | medium: Den opprinnelige nettleserkontrollen prøvde bare 401 fra `/api/meg`. Detaljkallet bruker sesjonsvarsleren, men denne stien var ikke kontrollert. Ny kontroll viste omdirigering til `/logg-inn` uten vaktdetaljer. | patch dokumentasjon |
| BH | Ingen sammenhengende nettleserkontroll mot databasen | medium: Den første kontrollen brukte simulerte svar. Ny kontroll med midlertidig seedet database, innlogging, Vaktvalg, detaljoppslag og tilbakeknapp bestod. | patch dokumentasjon |
| BH | Gammelt svar kan overskrive nyere vakt | false: `App` gir komponenten `key={vaktnummer}`. Ved vaktbytte rydder effekten opp og setter `aktiv = false`; gammel respons kan dermed ikke sette state på ny komponent. | avvist |
| BH | Sesjonsloggen er bare planleggingsstatus | low: Loggen ble skrevet ved første milepæl og trenger oppdatering med leveranse og kontroll før avslutning. | patch |
| ECH | Slettet bruker mellom middleware og oppslag gir 404 | low: Et samtidig slettet brukeroppslag kan gi 404, men brukeren kan ikke slettes gjennom v1-appen. Ny databasekontroll og gren for denne racen gir mer kompleksitet enn nytte i normal bruk. | avvist |
| VG | Komponentinnholdet testes ikke av `npm test` | low: Testene dekker API, URL og formatering, mens kandidatflatens faktiske innhold er kontrollert i Playwright og skjermbilder. Å innføre en ny komponenttestrigg for denne ene statiske flaten er mer enn en direkte korreksjon; manuell kontroll er dokumentert. | avvist |

## Verification

**Commands:**
- Fra `backend/`: `.venv\Scripts\python -m pytest` — alle tester består.
- Fra `frontend/`: `npm.cmd run build` og `npm.cmd test` — typesjekk, bygg og tester består.
