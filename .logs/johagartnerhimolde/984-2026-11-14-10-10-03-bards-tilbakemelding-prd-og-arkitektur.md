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

## 2026-11-14 kl. 10:42 — johagartnerHiMolde

### Oppgave
Sjekke om et oppsett for komponenttester virker med versjonene vi bruker (Vite 8.3.1, React 19.3.0, TypeScript 7.0.2, Node 22.12 som laveste versjon), før gruppa bestemmer seg.

### Plan
- Kopierte `frontend/` (uten `node_modules`) til scratchpad og installerte kandidatene med eksakte versjoner. Repoet er ikke rørt.
- Skrev to komponenttester: Godkjenningsflate (Godkjenn gjør ingen kall og viser linjen fra 2A, Avbryt kaller `onTilbake`) og Kandidatflate («Velg» sender vakt og id).
- Kjørte dem med jsdom og happy-dom på Node 26.7 og 22.12, prøvde en mutasjon, typesjekket med TypeScript 7 og kjørte de eksisterende testene og bygget.

### Resultat
- Vitest 5.1.0 (peer: Vite ^6–^8) og @testing-library/react 16.3.3 (peer: React ^18–^19) passer til versjonene våre. `npm ls` viser ingen ugyldige peer-avhengigheter, bare valgfrie som mangler.
- **Nyeste jsdom (30 og 31) krever Node ^22.22.2.** jsdom 28.1.0 (^22.12.0) og happy-dom 21.0.4 (>=20) holder løftet om Node 22.12.
- Begge testene bestod med jsdom 28.1.0 og happy-dom 21.0.4, både på Node 26.7 og på Node 22.12 (`npx -p node@22.12.0`). Tid: cirka 4 s med jsdom og 2 s med happy-dom.
- Mutasjonen der «Godkjenn» henter data på nytt, ga rød test («called 1 times, but got 2 times»).
- `tsc` med TypeScript 7.0.2 godtok testfilene etter én retting i testkoden (type på `vi.fn`).
- `node --test` kjører fortsatt bare de 48 eksisterende testene, fordi Vitest-filene er `.test.tsx` og `include` er avgrenset. `npm run build` bestod.
- Prøveoppsettet ligger i scratchpad og er ikke tatt inn i repoet.

### Åpne punkter
- Gruppa velger om oppsettet skal innføres (OP-ID, egen PR). Punktet står allerede i `issues.md`.

## 2026-11-14 kl. 10:49 — johagartnerHiMolde

### Oppgave
Lage en handoff til en ny økt som skal innføre komponenttester for frontend i en egen branch. Målene er å spare manuell testing og diskusjoner om feil i gruppa, og å gi bedre dokumentasjon av testing (kriterium 3 i sensorveiledningen).

### Plan
- Samlet dagens tilstand (testoppsett, CI, README, arkitektur), de utsatte punktene som skyldes manglende rigg, resultatet fra prøveoppsettet og kravene i AGENTS.md.

### Resultat
- [`handoff-frontendtesting-2026-11-14.md`](../../_bmad-output/implementation-artifacts/handoff-frontendtesting-2026-11-14.md) inneholder mål, oppstart, dagens tilstand, de fem utsatte punktene med kilder, versjoner og konfigurasjon fra prøveoppsettet, foreslått omfang i tre deler (oppsett, tester, dokumentasjon), fem beslutninger å avklare, fallgruver og når arbeidet er ferdig. OP-16 er foreslått som ID.
- Handoffen er ikke committet. Den skal tas med i første commit på den nye branchen.

### Åpne punkter
- Neste økt: innføre komponenttester etter handoffen. Punktet om komponentrigg i `issues.md` dekker dette.
