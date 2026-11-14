---
title: 'Komponenttester for frontend (Vitest, Testing Library, jsdom)'
type: 'chore'
created: '2026-11-14'
status: 'in-progress'
baseline_commit: '5a71652b05ff1e295ba559d6e20ffe7ef518b190'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/implementation-artifacts/handoff-frontendtesting-2026-11-14.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Ingen frontendtest rendrer en komponent. Tilstander, knapper og ruter i `Vaktvalg`, `Kandidatflate` (med `Kandidatliste` og `EkskludertBoks`), `Godkjenningsflate` og `App` kontrolleres bare for hånd i nettleseren. Feil oppdages sent, ofte i PR-gjennomgang, og dekningen er ujevn etter kriterium 3 i sensorveiledningen.

**Approach:** Legg til Vitest med Testing Library og jsdom ved siden av dagens `node --test`. Skriv rendrede tester for de fem utsatte punktene (1.5, 2.1, 2.4, 2.5 og 3.1), og vis at hver test kan feile med en mutasjon. Dokumenter hva som testes automatisk og hva som fortsatt er manuelt i `docs/testing.md`.

## Boundaries & Constraints

**Always:**
- Pakkene installeres med eksakt versjon (`npm install -D -E`): `vitest` 5.1.0, `@testing-library/react` 16.3.3, `@testing-library/dom` 10.4.2, `@testing-library/user-event` 14.6.10 og `jsdom` 28.1.0. Løftet om Node 22.12 står fast.
- `npm run test` kjører `node --test` og deretter `vitest run`. CI og README får ingen ny kommando. `node --test` gir fortsatt 48 tester.
- Vitest tar bare med `tester/komponenter/**/*.test.tsx`. Testfilene typesjekkes av `tsc` gjennom et eget `tsconfig.test.json`, og `npm run build` kjører det også.
- Elementer finnes etter rolle og tilgjengelig navn med tekstene fra `src/tekster.ts`, ikke etter CSS-klasse. Testdata har typer fra `src/api.ts`.
- `fetch` stubbes per URL med `vi.stubGlobal`. `afterEach` kjører `cleanup()`, `vi.unstubAllGlobals()` og `settSesjonsvarsler(null)`. App-tester setter stien med `history.replaceState` før render.
- Hver test eller testgruppe har en påvist mutasjon i `src/` som gjør den rød. Mutasjonen og den røde meldingen noteres i KI-loggen, og koden tilbakestilles. `git diff 5a71652 -- frontend/src` er tom når arbeidet er ferdig.
- Dokumentasjon på bokmål. Når et punkt i `deferred-work.md` er løst, beholdes det og merkes som løst, med testfila det gjelder.

**Never:**
- Ikke endre oppførselen til komponentene, og ikke flytte de 48 `node:test`-testene.
- Ikke ta med Playwright eller ende-til-ende-tester. Ikke test layout, farger eller synlighet via CSS.
- Ikke ta med punktet fra 1.3 om at `FEILTEKSTER` skal stemme med backend. Det står igjen i `deferred-work.md`.

**Beslutninger (Johannes, 2026-11-14):** jsdom 28.1.0, ikke happy-dom. De gamle testene blir værende i `node:test`. Alle fem utsatte punkter dekkes. Testoversikten og den manuelle sjekklisten ligger i én fil, `docs/testing.md`. Hvem som gjennomgår PR-en, avklares når den opprettes. Spesifikasjonen holdes samlet, selv om den er over 1600 tokens.

**Beslutning om manuell kontroll (Johannes, 2026-11-14, alternativ A):** Manuell kontroll trengs bare når de automatiske testene ikke kan kontrollere det aktuelle. Et `persistent_facts`-punkt i `_bmad/custom/bmad-build.toml` sier dette. «Manual checks» i nye spesifikasjoner tar bare med punkter fra sjekklisten i `docs/testing.md`. Koblingen i komponentene dekkes av tester i `tester/komponenter/`.

## I/O & Edge-Case Matrix

| Punkt | Tilstand (falsk `fetch`) | Forventet | Mutasjon som må gi rød test |
|---|---|---|---|
| 1.5 Vaktvalg | `/api/vaktoversikt` 500, deretter 200 | `alert` med «Prøv igjen». Trykk gir nytt kall og viser oversikten | fjern `forsok` fra deps |
| 1.5 401 (App) | `/api/meg` 200, `/api/vaktoversikt` 401 | Innloggingen viser `TEKSTER.sesjonUtlopt` | ikke kall sesjonsvarsleren |
| 2.1 Kandidatliste | `/kandidater` 500, deretter 200, og datafeil | Feil med «Prøv igjen» gir ny henting. Datafeil viser tekst og datagrense uten liste | fjern `forsok` fra deps |
| 2.4 Tom liste | `kandidater: []` | `ingenGyldige` vises, ingen «Velg»-knapp | `=== 0` blir `!== 0` |
| 2.5 Ekskludert-boks | `totalt: 0`, og `totalt > 0` | Ved 0 vises ingen boks. Ellers lukket → åpen → lukket, med `aria-expanded` false/true/false | fjern `totalt === 0`-sjekken |
| 3.1 Velg | to gyldige | `onVelg(4127, 6)` for Jonas Bakke | send feil id |
| 3.1 Rute (App) | sti `/vakt/4127/godkjenning/6` | Godkjenningsflaten med kandidaten som overskrift | snu rutevalget |
| 3.1 Godkjenn/Avbryt | ok-svar | Godkjenn gir ingen nye kall, bare `ikkeLagret`. Avbryt kaller `onTilbake` | Godkjenn henter på nytt |
| 3.1 Datafeil og 404 | datafeil, og 404 `ikke_funnet` | Ingen knapp for «Godkjenn erstatning». 404 viser `ikkeFunnet` | vis knappene ved datafeil |

</frozen-after-approval>

## Code Map

- `frontend/package.json`: skriptene `build` og `test`, og `devDependencies` som er låst eksakt.
- `frontend/tsconfig.json`: `include` er `src` og `vite.config.ts`, med `jsx: react-jsx`, `moduleResolution: bundler` og `types: vite/client`. Endres ikke. Utvides av `tsconfig.test.json`.
- `frontend/vite.config.ts`: inneholder plugin og proxy. Endres ikke. Vitest får egen `vitest.config.ts`.
- `src/komponenter/Vaktvalg.tsx`: props `{onVelgVakt}`. Lasting er `status` (l.57), feil og «Prøv igjen» er `alert` (l.66–78). `forsok` står i deps på l.49. Ved 401 rendrer komponenten `null` (l.55).
- `src/komponenter/Kandidatflate.tsx`: props `{vaktnummer, onVelg}`.
  - `Kandidatliste` (l.101) og `EkskludertBoks` (l.178) er interne funksjoner og testes gjennom `Kandidatflate`.
  - `Kandidatliste` har `forsok` i deps på l.106. Feil står på l.122–132, datafeil på l.133, tom liste på l.144 og «Velg» med `velgEtikett` på l.160–165.
  - `EkskludertBoks` rendrer `null` når `totalt === 0` (l.181), og knappen har `aria-expanded` (l.186). Knappeteksten har et pilspan med `aria-hidden`, så navnet matches med regex.
- `src/komponenter/Godkjenningsflate.tsx`: props `{vaktnummer, ansattId, onTilbake}`. 404 står på l.50, datafeil på l.66 og `trykket`/`ikkeLagret` på l.111–115.
- `src/App.tsx` og `src/navigasjon.ts`:
  - App kaller `hentMeg` ved oppstart (l.53).
  - Sesjonsvarsleren (l.74) kaller `visInnlogging` (l.34–44), som setter `sesjonUtlopt` når sesjonen var bekreftet før.
  - Godkjenningsruten står på l.152–159, med mønsteret `^/vakt/N/godkjenning/M$` (navigasjon.ts l.24).
- `src/api.ts`: typene `Vaktoversikt` (l.28), `Vaktdetaljer` (l.38, flat og uten `status`), `Kandidat`, `UtelukkelsesOppsummering`, `Kandidatsvar` (l.61) og `Godkjenningssvar` (l.67). `settSesjonsvarsler` står på l.105, og modulnivå-tilstanden på l.94–95.
- `src/tekster.ts`: blokkene `TEKSTER.vaktvalg` (l.64), `kandidatflate` (l.82), `godkjenning` (l.105) og `ekskludertBoks` (l.147), og `provIgjen` og `sesjonUtlopt`.
- `.github/workflows/frontend-tester.yml`: kjører `npm ci`, `build` og `test` på 22.12 og `lts/*`. Endres ikke.
- Dokumenter:
  - `README.md:232`: avsnittet «### Tester».
  - `ARCHITECTURE-SPINE.md:111`: Testing-raden, under `_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/`.
  - `docs/emne/vurderingsmatrise.md`: siste milepæl står på l.37.
  - `docs/beslutninger/avklaringspunkter.md`: OP-15 i §2 står på l.84 og seksjonen for OP-15 i §11 på l.696.
  - `docs/modellvalg-stories.md`: tabellen over modellvalg.

## Tasks & Acceptance

**Execution:**
- [ ] `frontend/package.json` og `package-lock.json`: installer pakkene. Sett `test` til `node --test && vitest run` og `build` til `tsc --noEmit && tsc --noEmit -p tsconfig.test.json && vite build`.
- [ ] `frontend/vitest.config.ts` og `frontend/tsconfig.test.json`: oppsett som i handoffen. `tsconfig.test.json` utvider `tsconfig.json` og tar med `src` og `tester/komponenter`.
- [ ] `frontend/tester/komponenter/hjelpere.ts`: `json(data, status)`, falsk `fetch` per URL med kø av svar, felles `afterEach` og typede testdata.
- [ ] `frontend/tester/komponenter/{vaktvalg,kandidatflate,godkjenningsflate,app}.test.tsx`: én test per rad i matrisen.
- [ ] Mutasjoner: kjør hver mutasjon, se testen bli rød, tilbakestill og noter resultatet.
- [ ] `docs/testing.md`: hva som testes automatisk (backend per regel, API, frontendlogikk og komponenter), med kommandoer og lenker. Hva som er manuelt og hvorfor: 360 px og layout, farger og fokus, og P-13. En kort manuell sjekkliste med bare det jsdom ikke kan.
- [ ] Oppdater README «### Tester», AGENTS.md «Kjøring og verifisering», Testing-raden i spine, `deferred-work.md` (fem punkter løst), vurderingsmatrisen (milepæl med lenker), OP-16 i §2 og §11 (ingen tom linje mellom radene i tabellen) og raden i `modellvalg-stories.md` («Komponenttestrigg | Opus | grunnmønster»).
- [ ] `_bmad/custom/bmad-build.toml`: legg til `persistent_facts`-punktet fra beslutningen om manuell kontroll. Den sporede filen gjelder for hele gruppa. Kontroller at render-skriptet tar det med.
- [ ] `docs/ki-logg/2026-11-14-komponenttester.md`: oppgave, prompt, leveranse, rettelser og mutasjonstabellen.

**Acceptance Criteria:**
- Gitt en ren `npm ci`, når `npm run test` kjøres på Node 22.12 og på nyeste LTS, så består 48 `node:test`-tester og alle Vitest-testene.
- Gitt en typefeil i en komponenttest, når `npm run build` kjøres, så feiler bygget.
- Gitt Windows PowerShell (`npm.cmd`) og Git Bash, når `npm run test` kjøres, så er resultatet det samme.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `npm.cmd run build` i `frontend/`: består.
- `npm.cmd run test` i `frontend/`: 48 tester i `node:test`, og alle Vitest-testene består.
- `npx -y -p node@22.12.0 node node_modules/vitest/vitest.mjs run` i `frontend/`: består.
- `git diff 5a71652 -- frontend/src`: tom.
