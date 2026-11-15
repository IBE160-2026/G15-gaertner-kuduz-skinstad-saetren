---
title: 'Story 3.2: Gjennomføre godkjenning og bemanne vakten'
type: 'feature'
created: '2026-11-15'
status: 'done'
route: 'dispatch'
baseline_commit: 'ca7a57555d96c96ab579efab19848206453a69f4'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Godkjenningsflaten fra 3.1 lagrer ingenting. Turnusansvarlig må kunne bekrefte en gyldig erstatter eksplisitt og se en varig bemannet vakt (FR12).

**Approach:** Et beskyttet POST-endepunkt kontrollerer hele regelgrunnlaget på nytt, sammenligner det med vist grunnlag og lagrer godkjenningen og bemanningen atomisk. Flaten håndterer avvik og sender brukeren til Vaktvalg etter suksess.

## Boundaries & Constraints

**Always:**
- Godkjenning krever ett aktivt, eksplisitt trykk. Lagre valgt ansatt, godkjennende bruker, vakt og tidspunkt. Én skrivefunksjon i lagringsadapteren tar et fullstendig Godkjenning-objekt og er eneste vei som setter bemanningen (AD-5, P-12).
- Regelmotoren vurderer hele grunnlaget i POST før lagring. Ugyldig kandidat gir nøytral feilkode uten å røpe regelårsaker. Ufullstendig grunnlag gir egen datafeilstatus med datagrense og ingen lagring (P-08, NFR2).
- Et opakt grunnlagsmerke fra GET omfatter data som påvirker gjeldende visning og regelvurdering. POST sammenligner mot nyberegnet merke. Endring gir oppdaterte data på flaten og krever nytt trykk. Utvid merket når Epic 4 og 5 legger til beregninger (P-09).
- DB håndhever høyst én Godkjenning per vakt, og en betinget, atomisk oppdatering av ubemannet vakt hindrer samtidige dubletter. Godkjenning og vaktendring ligger i samme transaksjon.
- Sene svar for annen vakt/kandidat eller utløpt sesjon forkastes. Etter suksess vises nøytral bekreftelse øverst på Vaktvalg, og ny oversikt viser vakten som bemannet (UX-DR20, OP-16).

**Never:** Ingen automatisk godkjenning, SMS, KI eller lagring av forklaring. Kostnad, rangering og preferansetolkning fra Epic 4/5 implementeres ikke her. Testene gjør ingen betalte modellkall.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Bekreftelse | #4127, Jonas, uendret grunnlag | Én Godkjenning, bemannet vakt, Vaktvalg med melding | — |
| Endret grunnlag | Vakt/ansatt/historikk endres etter GET | Oppdatert visning, nytt bekreftelsestrykk | Ingen lagring ved første POST |
| Mistet gyldighet | Kandidaten bryter en hard regel ved POST | Ingen endring | Nøytral kode og melding |
| Datafeil | Nødvendig historikk eller vaktdata er ugyldig | Ingen endring | Egen datafeil, ikke «ingen gyldige» |
| Dublett og samtidighet | To POST for samme vakt | Nøyaktig én Godkjenning | Andre svar får egen feilkode |
| Navigasjon/sesjon | Sent svar etter URL-bytte eller utlogging | Ingen gammel visning eller suksessnavigasjon | Sesjonsvernet gjelder også POST |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py` — GET-grunnlag ved linje 290 gjenbruker hele `hent_kandidatgrunnlag` og `vurder_kandidater`; legg POST og faste feilkoder her. `request.state.bruker.id` kommer fra middleware.
- `backend/adaptere/lagring/modeller.py` — `VaktRad` har CHECK for samsvar mellom `mangler_bemanning` og `tildelt_ansatt_id`; legg til `GodkjenningRad` med unik vakt-FK. `database.py` oppretter nye tabeller med `create_all`.
- `backend/adaptere/lagring/kandidatgrunnlag.py` — hent hele settet, ikke filtrer før regelkontroll. Ny lagringsmodul får én skrivefunksjon med transaksjon og betinget UPDATE.
- `backend/adaptere/lagring/testdata.py` — slett godkjenninger før vakt/bruker ved gjentatt seeding.
- `frontend/src/api.ts`, `godkjenning.ts` — bygg POST på eksisterende `kall` og vern mot sene GET-svar; knytt svar til aktiv vakt/kandidat og sesjon.
- `frontend/src/komponenter/Godkjenningsflate.tsx`, `App.tsx`, `Vaktvalg.tsx`, `tekster.ts` — erstatt midlertidig knapp, vis endret grunnlag/feil og bekreftelse etter navigasjon. Bruk eksisterende designtokens.
- `backend/tester/api/test_godkjenningsgrunnlag.py`, `frontend/tester/komponenter/godkjenningsflate.test.tsx` — oppdater 3.1-testene som i dag krever POST 405/ingen kall, og dekk hele matrisen.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/lagring/modeller.py`, ny godkjenningsmodul og `testdata.py` — varig, atomisk skrivevei og gjentatt seeding.
- [x] `backend/adaptere/api/main.py` — POST med regelkontroll, grunnlagsmerke, entydige svar og sesjonsvern.
- [x] `frontend/src/api.ts`, `godkjenning.ts`, `Godkjenningsflate.tsx`, `App.tsx`, `Vaktvalg.tsx`, `tekster.ts` — fullfør flyten og vern mot sene svar.
- [x] Backend- og komponenttester — gyldig, endret, ugyldig, datafeil, dublett/samtidighet, andre endepunkter uten skriving og navigasjon.
- [x] `README.md`, `docs/testing.md`, `docs/ki-logg/2026-11-15-godkjenning-bemanning.md`, `docs/emne/vurderingsmatrise.md` og sprintstatus — spor API, test, KI-arbeid og reviewklar status.

**Acceptance Criteria:**
- Given en vist gyldig kandidat, when turnusansvarlig trykker «Godkjenn erstatning» med uendret grunnlag, then finnes nøyaktig én varig Godkjenning og vakten står under bemannede på Vaktvalg.
- Given endret eller ufullstendig grunnlag, when POST kommer, then lagres ingenting og brukeren får riktig separat tilstand før eventuell ny bekreftelse.
- Given to godkjenningsforsøk for samme vakt, when begge behandles, then høyst ett lykkes, og ingen annen API-rute bemanner vakten.

## Implementation Notes

- 2026-11-15: GET returnerer `grunnlagsmerke` som SHA-256 over sorterte turnus-, ansatt- og vaktrader. POST tar SQLite `BEGIN IMMEDIATE` før ny vurdering, og den eneste skrivefunksjonen oppdaterer vakten betinget og legger til en Godkjenning med unik vakt i samme transaksjon. Merket må utvides med nye beslutningsinnganger i Epic 4/5 (P-09).
- 2026-11-15: Diffkontrollen fant at sent POST-svar kunne gi feil navigasjon ved kandidatbytte. Forespørselsidentitet og komponenttest ble lagt til. Matrisekontrollen førte også til egne tester for POST-datafeil og at andre API-ruter ikke bemanner.
- 2026-11-15: Hele pakken bestod: 418 backendtester, 48 frontendmodultester, 17 komponenttester og frontendbygg. Nettleserkontroll mot egen testdatabase viste godkjenning av Jonas for #4127 og oppdatert Vaktvalg ved 1000 px bredde. Fokus- og kontrastkontroll er ennå ikke gjort.
- 2026-11-15: Etter pull fra main og Johannes' AD-5-notat ble transaksjonseierskapet flyttet fra API-et til lagringsadapterens ene godkjenningsoperasjon. Den tar `BEGIN IMMEDIATE` før lesing, vurderer alle harde regler og grunnlagsmerket og skriver atomisk. En test bekrefter lås før kandidatlesing; rollback-testen injiserer feil ved innsetting. Etter samordningen bestod 427 backendtester, 49 frontendmodultester, 23 komponenttester og frontendbygg.

## Spec Change Log

## Review Triage Log

Uavhengig gjennomgang 2026-11-15: Blind Hunter (BH), Edge Case Hunter (EC) og Verification Gap (VG). Hver rapport ble vurdert mot kode, kontrakt og testene før retting.

| # | Funn | Vurdering og bevis | Utfall |
|---|---|---|---|
| BH1 | GET kan lese visning og merke fra ulike databaseøyeblikk | medium: `main.py` beregner merket etter grunnlaget; SQLite-konfigurasjonen starter ikke eksplisitt lesetransaksjon | patch, sammen med EC1 |
| BH2 | Merket kan brukes for annen vakt/kandidat | medium: hashfunksjonen tar bare databaserader, og POST kontrollerer ikke hvilken visning merket kom fra | patch |
| BH3 | Global hash gir ny bekreftelse ved enhver DB-endring og leser alle rader | low: ekstra ny bekreftelse er reell, men databasen har én turnus og 506 vakter; avgrensing krever ny modell for regelvinduer | avvist nå; vurder ved større datamengde |
| BH4 | Kandidat som mister gyldighet får ikke oppdatert kandidatvisning | false: dette er egen matriserad; POST gir nøytral `ugyldig_kandidat` og fjerner godkjenningsknappen. Ny kandidatvurdering nås fra lenken tilbake | avvist |
| BH5 | SQLite-låsetidsavbrudd kan gi 500 | low: mulig ved ekstern skriver som holder lås lenger enn SQLite-timeout, men ikke vist i normal dobbeltklikkflyt; egen timeoutgren ville øke kompleksiteten | avvist |
| BH6 | Tapt POST-svar gir usikker status og senere dublettfeil | medium: nettverksfeil kan skje etter commit; UI bør ikke antyde at ingenting skjedde | patch, sammen med EC2 |
| BH7 | Overgangen gjennom `App` mangler komponenttest | medium: komponenttestene dekker bare callback og Vaktvalg hver for seg, ikke koblingen | patch, sammen med VG1 |
| BH8 | Bekreftelsen identifiserer ikke vakt og ansatt | medium: `Vaktvalg` viser bare generell tekst, mens UX-DR20 gir konkret valg som eksempel | patch |
| BH9 | Atomisitet ved feil etter vaktoppdatering er ikke testet | medium: happy path og samtidighet dekker ikke rollback ved feil i innsetting | patch |
| BH10 | Ventende POST mangler test for sesjonsbytte og dobbeltklikk | medium: koden har sesjonsgenerasjon og `venter`, men ingen test ville fange regresjon | patch |
| EC1 | GET-konsistens | medium: samme rotårsak som BH1 | patch |
| EC2 | Tapt POST-svar | medium: samme rotårsak som BH6; idempotent suksessvar ville bryte storyens krav om 409 ved nytt forsøk | patch med avklarende UI |
| EC3 | Ukjent 200-status kan vises som datafeil | false: POSTs Pydantic-responsmodell tillater bare `godkjent` og `datafeil`; en slik respons kan ikke komme fra denne backendversjonen | avvist |
| VG1 | App-overgangen er ikke testet | medium: søk og testgjennomgang bekrefter bare separate komponenttester | patch, sammen med BH7 |
| VG2 | Merket er bare testet mot endret minstenivå | medium: en feil som utelater ansattdata ville passere dagens test | patch |

Målrettet uavhengig gjennomgang etter AD-5-refaktoreringen fant to forhold: (1) det globale merket kan kreve nytt trykk ved en urelatert databaseendring; dette er den kjente BH3-avveiningen for én turnus med 506 vakter, og (2) godkjenningstidspunktet tas ved brukerens forsøk før eventuell låseventing. Tidspunktet dokumenterer beslutningen; låsen sikrer at ny regelvurdering og skriving skjer mot samme gjeldende tilstand. Ingen nye kodefeil ble påvist.

## Verification

**Commands:**
- `backend/.venv/Scripts/python -m pytest` — alle backendtester og arkitekturkontrakten består.
- `npm.cmd run build` og `npm.cmd run test` fra `frontend/` — bygg og alle komponenttester består.

**Manual checks:**
- Kontroller knapper, fokus, farger og layout i smalt datamaskinvindu mot ekte backend der automatiske tester ikke dekker tilstanden (OP-16, AV-17).
