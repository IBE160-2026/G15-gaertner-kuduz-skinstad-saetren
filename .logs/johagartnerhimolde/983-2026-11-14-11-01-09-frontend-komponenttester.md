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
- AGENTS.md sier «P-13 én gang (OP-16)», men henvisningen bør være P-13 i §12. Avgjøres i PR-gjennomgangen.

## 2026-11-14 kl. 12:05 — johagartnerHiMolde

### Oppgave
Johannes ba om to ting. Informasjonen om RAM og CPU fra testkjøringene skulle dokumenteres, fordi andre maskiner kan kreve endringer, og endringer var godkjent på forhånd. Han ville også bli tatt gjennom sårbarheten i Vite for å vurdere om den skulle prioriteres.

### Plan
- Målte `npx vitest run` med én arbeider og med standard antall arbeidere, alene og i fire samtidige kjøringer.
- Hentet de seks GitHub-varslene bak `npm audit` med `gh api advisories/…` og vurderte hvert av dem mot oppsettet vårt.

### Resultat
- **Maskinkrav (`7db5d15`):**
  - Maskinen er en i3-1115G4 med 7,7 GB RAM. Før start var 0,6 GB ledig, og CPU-en lå på 35–100 %.
  - Med `maxWorkers: 1` ga fire samtidige kjøringer 12 av 12 på 21–22 s. Før ga de tidsavbrudd og tok 125–154 s. Én kjøring ble ikke tregere.
  - `vitest.config.ts` har fått `maxWorkers: 1`. `docs/testing.md` har fått seksjonen «Trege maskiner og tidsavbrudd» med målinger og tiltak. README og AGENTS.md («Kjente fallgruver») har fått merknader.
  - Påstanden i KI-loggen om at fire samtidige kjøringer ikke tåles, er rettet.
- **Vite:**
  - Alle seks varslene gjelder bare utviklingsserveren. For oss gjelder bare `launch-editor` på Windows mens `npm run dev` kjører lokalt.
  - Johannes valgte bevisst å ikke oppgradere, fordi risikoen er lav og serveren bare kjører lokalt. Committet som egen commit.
  - Valget er ført i OP-16 (§11) og i `deferred-work.md` (merket valgt bort). README steg 4 forklarer advarselen fra `npm install` og ber om at `npm audit fix` ikke kjøres.
- `npm run build` består. `npm run test` gir 48 av 48 og 12 av 12.
- Lukket i issues.md: punktet om Vite.

### Åpne punkter
- Push branchen og opprett PR. Avklar hvem i gruppa som gjennomgår den.
- Kontroller at CI er grønn på Node 22.12 og `lts/*`.
- Henvisningen til P-13 i AGENTS.md avgjøres i PR-gjennomgangen.
