# Bårds tilbakemelding på PRD og technology.md

## 2026-11-14 kl. 10:10 — johagartnerHiMolde

### Oppgave
Johannes ba (via `bmad-help`) om å bli tatt gjennom Bårds tilbakemelding på PRD-en og det han har lagt inn under arkitektur.

### Plan
- Leste `tilbakemelding-prd.md` (Bård, 12.11), `reconcile-bard-2026-11-13.md`, Mithads logg for PR #18 og commit `1e24843`.
- Kontrollerte i `prd.md` at R2–R4 fra kontrollen er rettet, og søkte etter svar på refleksjonsspørsmålene.
- Leste `architecture/technology.md` (Bård, `a284263`) og sammenlignet med ARCHITECTURE-SPINE og det som er bygd.

### Resultat
- Punktene 4.1, 4.2, 4.3 og 4.5 er løst i PR #18. 4.4 er delvis løst: FR-10 («avgrensede automatiske nye forsøk») står bevisst åpen, med frist før story 5.1. R2 og R3 (krav om myk faktor i FR-11 og definisjonen av Avveining) er rettet i `1e24843`.
- Refleksjonsspørsmålene i §7 av tilbakemeldingen er ikke besvart i noen fil i repoet.
- `technology.md` beskriver et annet prosjekt (`pytagoras-website-v2`, Pytagoras Forlag), ikke Turnushjelperen. Commit-meldingen sier at den er «Teknologioversikt fra faglærer som referanse for arkitekturarbeidet», så den ser ut til å være lagt der med vilje (Mithads åpne punkt). Det er ingen tilbakemelding på arkitekturen vår.
- Det som er mest relevant for oss: Vitest/Playwright (kan dekke komponentriggen som mangler), mock-fallback (vi har demo-modus), single-origin `/api` (vi har Vite-proxy), en fast oppstartsvakt for konfigurasjon, rate limiting på innlogging og et migreringsverktøy (Alembic står åpent i AD-5 og blir aktuelt når 3.2 skriver til databasen).
- Ingen filer er endret utenom denne loggen.

### Åpne punkter
- Gruppa bør svare på Bårds to refleksjonsspørsmål (regneeksemplene for taket på 300 og hvilke KI-forslag som ble godtatt uten å kutte). Det er godt materiale for KI-dokumentasjonen.
- Vurder om en komponentrigg (Vitest + Testing Library, eventuelt Playwright for e2e) skal inn i arkitekturen, siden den mangler i 2.4, 2.5 og 3.1 (`deferred-work.md`).

## 2026-11-14 kl. 10:16 — johagartnerHiMolde

### Oppgave
Johannes ba om fordeler og ulemper, arbeidsmengde og konsekvenser ved å innføre et testoppsett for frontend-komponenter.

### Plan
- Kartla dagens oppsett: `node --test` med `rolldown`-bunting av rene moduler (5 testfiler, 48 tester), ingen rendring av komponenter.
- Talte utsatte punkter som skyldes manglende rigg i `deferred-work.md` og spesifikasjonene: 1.5, 2.1, 2.4, 3.1 og to avviste rader i 2.5.
- Sjekket Testing-raden i ARCHITECTURE-SPINE (bare pytest) og kriterium 3 i sensorveiledningen.

### Resultat
- Anbefaling til Johannes: Vitest + Testing Library + jsdom i en egen liten PR før 3.2, cirka en halv til én dag. De eksisterende testene beholdes. Testene som mangler skrives når komponentene endres likevel (2.6, 3.2), pluss noen få utvalgte nå. Playwright venter, eventuelt til 4.6 eller en røyktest før innlevering.
- Vitest-versjonen må prøves mot Vite 8, React 19.3 og TypeScript 7. Kompatibiliteten er ikke kontrollert.
- Ingen filer er endret.

### Åpne punkter
- Beslutningen om rigg står som åpent punkt i `issues.md` fra økten over.
