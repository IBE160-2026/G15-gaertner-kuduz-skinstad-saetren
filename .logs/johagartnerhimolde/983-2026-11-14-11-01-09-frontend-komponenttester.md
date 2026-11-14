# Frontend-komponenttester

## 2026-11-14 kl. 11:01 — johagartnerHiMolde

### Oppgave
Innføre automatiske komponenttester for frontend etter [handoffen](../../_bmad-output/implementation-artifacts/handoff-frontendtesting-2026-11-14.md). Testene skal erstatte mest mulig av den manuelle nettleserkontrollen og dokumentere testingen bedre for kriterium 3 i sensorveiledningen. Arbeidet gjøres i en branch med PR.

### Plan
- Branch: `frontend-komponenttester`, laget fra `main` (`5a71652`).
- Beslutninger fra Johannes:
  - DOM-miljøet er jsdom 28.1.0.
  - De 48 `node:test`-testene flyttes ikke, og `npm run test` kjører begge testsettene.
  - Alle fem utsatte punkter dekkes (1.5, 2.1, 2.4, 2.5 og 3.1).
  - Testoversikten og den manuelle sjekklisten ligger i én fil, `docs/testing.md`.
  - Spesifikasjonen holdes samlet, selv om den er på rundt 2 600 tokens.
  - Alternativ A: manuell kontroll trengs bare når testene ikke kan kontrollere det aktuelle. Regelen legges i `_bmad/custom/bmad-build.toml`.
- Arbeidsmåte: `bmad-build` med underagenter. Én kartla koden, én implementerer fra spesifikasjonen, og egne agenter gjennomgår uten å ha sett implementeringen.
- Spesifikasjon: [spec-frontend-komponenttester.md](../../_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md).

### Resultat
- **Spesifikasjonen** ble godkjent ved sjekkpunkt 1 og er nå `done`. Handoffen og spesifikasjonen ligger i `0e1b86b`.
- **Implementeringen** ble gjort av en underagent som bare hadde spesifikasjonen som grunnlag. Arbeidet er committet i `de74a3a`.
  - Vitest 5.1.0, Testing Library og jsdom 28.1.0 er installert. `npm run test` kjører `node --test && vitest run`, og `npm run build` typesjekker testene.
  - 12 komponenttester i `frontend/tester/komponenter/` dekker de fem utsatte punktene.
  - Alle 13 mutasjonene ga rød test. `frontend/src` er uendret.
  - Dokumentasjon: `docs/testing.md` (testoversikt og manuell sjekkliste), README, AGENTS.md, ARCHITECTURE-SPINE (Testing-raden og Stack), `deferred-work.md`, vurderingsmatrisen, OP-16 og `modellvalg-stories.md`.
  - Regelen om manuell kontroll står i `_bmad/custom/bmad-build.toml`.
  - [KI-logg](../../docs/ki-logg/2026-11-14-komponenttester.md).
- **Gjennomgang:** tre uavhengige lag (blind-hunter, edge-case-hunter, verification-gap) ga 24 funn. 13 ble rettet, 2 utsatt til `deferred-work.md` (vite-sårbarheten og P-13-henvisningen i AGENTS.md) og 6 avvist. Detaljene står i Review Triage Log i spesifikasjonen.
- **Verifisert av orkestratoren:**
  - `npm run build` består. `node --test` gir 48 av 48, og Vitest 12 av 12 i én kjøring.
  - Fire parallelle kjøringer feiler fortsatt på denne maskinen (7,7 GB RAM, CPU 77–100 % før start). Funnet er ført i KI-loggen, og den gale påstanden fra underagenten er rettet der.
  - Node 22.12 er ikke kjørt lokalt. Johannes valgte at CI skal kontrollere det.
- **Lukket i issues.md:** punktet om å vurdere en komponentrigg.

### Åpne punkter
- Push branchen og opprett PR. Avklar hvem i gruppa som gjennomgår den.
- Kontroller at CI er grønn på Node 22.12 og `lts/*` (ikke kjørt lokalt).
- Vite 8.3.1 har en høy sårbarhet (rettet i 8.3.8). Utsatt i `deferred-work.md`.
- AGENTS.md sier «P-13 én gang (OP-16)», men henvisningen bør være P-13 i §12. Avgjøres i PR-gjennomgangen.
