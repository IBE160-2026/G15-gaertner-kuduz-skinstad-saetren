# Story 3.2 – godkjenning og bemanning

## 2026-11-15 kl. 09:39 — Kimsk81

### Oppgave

Kjøre bmad-build for story 3.2 til klar for gjennomgang. Starte med branch, commit og push slik at gruppa ser at storyen er tatt.

### Plan

- Lese byggflyt, AGENTS.md, sprintstatus, Epic 3, story, gruppevedtak og sensorveiledning.
- Kartlegge eksisterende kode med underagenter og skrive spesifikasjon etter bmad-build.
- Etter spesifikasjonsgodkjenning: implementere, teste, få uavhengig kodegjennomgang og føre KI-logg og vurderingsbevis.
- Trekke inn siste `main`, vurdere Johannes' AD-5-notat og samordne story 3.2 med ny arkitektur og story 2.6.

### Resultat

- Opprettet og pushet `story-3.2-godkjenning-bemanning` med tom startcommit `da818ac`, slik brukeren ba om.
- Oppdaterte `_bmad-output/implementation-artifacts/epic-3-context.md` fordi `epics.md` var nyere enn hurtigkonteksten. Samlet kodekart for transaksjon, dublettvern, API, frontend og tester med underagenter.
- Skrev og fikk godkjent `_bmad-output/implementation-artifacts/spec-3-2-godkjenning-og-bemanning.md`. Implementerte beskyttet POST, opakt grunnlagsmerke fra konsistent GET, varig Godkjenning og bemanning i én transaksjon, frontendbekreftelse og håndtering av endret eller ufullstendig grunnlag, dublett, sen respons og usikkert POST-svar. KI-arbeidet og rettingene er dokumentert i `docs/ki-logg/2026-11-15-godkjenning-bemanning.md`.
- Tre uavhengige kodegjennomganger førte til retting av blant annet GET-snapshot, grunnlagsmerkets identitet, sen respons, usikkert svar, rollback og manglende integrasjonstest. En ekstra uavhengig kontroll ble gjort etter AD-5-refaktoreringen; to dokumenterte avveininger ble beholdt, ingen ny kodefeil påvist.
- Trakk `main` inn i branchen etter brukerens beskjed. Johannes' notat om grunnlagsmerke og tidlig SQLite-lås var allerede dekket. Den nye AD-5 krevde at transaksjonen ble flyttet fra API-et til lagringsadapteren; dette er nå gjort og testet. Story 2.6 er samordnet. Oppdaterte README, testveiledning, vurderingsmatrise, arkitekturens lagringsoversikt og sprintstatus (`review`).
- Etter samordningen bestod 427 backendtester, 49 frontendmodultester, 23 komponenttester og frontendbygget. Nettleserkontroll mot ekte backend ved 1000 px viste godkjenning av Jonas for #4127 og bemannet vakt i Vaktvalg før siste tekstendring. Arbeidet ble committet som `1e5807a`. Ingen betalte KI-kall ble gjort.
- Opprettet [PR #23](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/23) mot `main` for gruppas vurdering. PR-en er åpen, uten mergekonflikt, og de fem viste CI-jobbene for backend, frontend og skills-speiling bestod.

### Åpne punkter

- Fokus- og kontrastkontroll av godkjenningsflyten i nettleser gjenstår som manuell kvalitetssikring (OP-16). Det er ført i `issues.md`.
