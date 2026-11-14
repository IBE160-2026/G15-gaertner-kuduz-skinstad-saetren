---
title: 'Komponenttester for frontend (Vitest, Testing Library, jsdom)'
type: 'chore'
created: '2026-11-14'
status: 'done'
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
- [x] `frontend/package.json` og `package-lock.json`: installer pakkene. Sett `test` til `node --test && vitest run` og `build` til `tsc --noEmit && tsc --noEmit -p tsconfig.test.json && vite build`.
- [x] `frontend/vitest.config.ts` og `frontend/tsconfig.test.json`: oppsett som i handoffen. `tsconfig.test.json` utvider `tsconfig.json` og tar med `src` og `tester/komponenter`.
- [x] `frontend/tester/komponenter/hjelpere.ts`: `json(data, status)`, falsk `fetch` per URL med kø av svar, felles `afterEach` og typede testdata.
- [x] `frontend/tester/komponenter/{vaktvalg,kandidatflate,godkjenningsflate,app}.test.tsx`: én test per rad i matrisen.
- [x] Mutasjoner: kjør hver mutasjon, se testen bli rød, tilbakestill og noter resultatet.
- [x] `docs/testing.md`: hva som testes automatisk (backend per regel, API, frontendlogikk og komponenter), med kommandoer og lenker. Hva som er manuelt og hvorfor: 360 px og layout, farger og fokus, og P-13. En kort manuell sjekkliste med bare det jsdom ikke kan.
- [x] Oppdater README «### Tester», AGENTS.md «Kjøring og verifisering», Testing-raden i spine, `deferred-work.md` (fem punkter løst), vurderingsmatrisen (milepæl med lenker), OP-16 i §2 og §11 (ingen tom linje mellom radene i tabellen) og raden i `modellvalg-stories.md` («Komponenttestrigg | Opus | grunnmønster»).
- [x] `_bmad/custom/bmad-build.toml`: legg til `persistent_facts`-punktet fra beslutningen om manuell kontroll. Den sporede filen gjelder for hele gruppa. Kontroller at render-skriptet tar det med.
- [x] `docs/ki-logg/2026-11-14-komponenttester.md`: oppgave, prompt, leveranse, rettelser og mutasjonstabellen.

**Acceptance Criteria:**
- Gitt en ren `npm ci`, når `npm run test` kjøres på Node 22.12 og på nyeste LTS, så består 48 `node:test`-tester og alle Vitest-testene.
- Gitt en typefeil i en komponenttest, når `npm run build` kjøres, så feiler bygget.
- Gitt Windows PowerShell (`npm.cmd`) og Git Bash, når `npm run test` kjøres, så er resultatet det samme.

## Implementation Notes

- 2026-11-14, implementeringsagenten (Opus 5.5):
  - Endret filer: se diffen. `tsconfig.test.json` tar også med `vitest.config.ts`.
  - `falskFetch` feiler testen i `afterEach` ved kall til en URL uten svar.
  - Testdataene bruker `satisfies`, ikke casts.
  - Punktet fra 2.5 sto bare i Review Triage Log for spesifikasjon 2.5. Det er ført inn i `deferred-work.md` og merket løst.
  - Bare kommentarene i `kandidater.test.mjs` og `godkjenning.test.mjs` er endret. Testene er ikke endret.
- Mutasjoner: alle 13 (M1–M9b) ga rød test. Tabellen står i KI-loggen.
- Orkestratoren kontrollerte selv: `npm run build` består. `node --test` gir 48 av 48 og Vitest 12 av 12, på Node 26.7. `git diff 5a71652 -- frontend/src` er tom.
- AK om Node 22.12 er ikke kjørt lokalt. `npx -y -p node@22.12.0` ble stoppet av tillatelsessystemet. `engines` i låsfila godtar 22.12. Kriteriet regnes som oppfylt når CI på branchen er grønn på 22.12 og `lts/*`.
- `npm audit`: én høy sårbarhet i vite 8.3.1 (rettet i 8.3.8). Den fantes før dette arbeidet og er utenfor omfang.

## Spec Change Log

## Review Triage Log

Gjennomgang 1, 2026-11-14. Lag: blind-hunter (B), edge-case-hunter (E) og verification-gap (VG).

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| VG1 | 401-testen i `app.test.tsx` feiler under last | medium | Pre-verifisert: fire parallelle kjøringer feilet på samme test. Kjeden `/api/meg` → `/api/vaktoversikt` 401 → LoggInn går over standardtaket på 1000 ms. | patch |
| B2/E3 | Felles `afterEach` registreres bare ved import av `hjelpere.ts` | medium | Hooken er en sideeffekt av importen. En ny testfil uten import mister `cleanup` og nullstillingen av `fetch` og sesjonsvarsleren. | patch |
| E4 | `window.history` nullstilles ikke mellom tester | low | App leser stien ved oppstart. En App-test uten `settSti` arver forrige sti. Rettelsen er én linje i `afterEach`. | patch |
| B1 | `falskFetch` skiller ikke på HTTP-metode | low | Rutene er nøklet bare på URL. En POST i 3.2 til samme sti ville fått GET-svaret. | patch |
| B1b | `Request`-objekt blir `"[object Request]"` | false | `api.ts:113` kaller `fetch(sti, …)` med en streng. | avvist |
| B3 | `vitest.config.ts` kopierer pluginene i stedet for å utvide `vite.config.ts` | low | Et senere alias eller en `define` i `vite.config.ts` ville manglet i testene. `mergeConfig` er en direkte rettelse. | patch |
| B4 | `npm run build` typesjekker `src` to ganger | low | Koster omtrent et sekund. Kommandoen er fastsatt i spesifikasjonen. | avvist |
| B5 | Ingen dokumentert måte å kjøre bare Vitest | low | `&&` stopper Vitest når `node:test` feiler. `docs/testing.md` nevner det, men gir ingen omvei. Rettes med en dokumentasjonslinje. | patch |
| E2/VGo1 | `docs/testing.md` er feil om `*.test.ts` | low | `tsconfig.test.json` typesjekker også `.test.ts`. På Node ≥23.6 plukker `node --test` opp `**/*.test.ts` og feiler på Vitest-importene. | patch |
| B6/VGo2 | `/utelukket av harde regler/` og `/^Velg /` er hardkodet | low | Endres teksten, består fraværssjekken uten å kontrollere noe. Rettes ved å bygge uttrykket fra `TEKSTER` (`tekster.ts:107`, `:148`). | patch |
| E6 | Regex av `TEKSTER` uten escaping | low | Ingen tekst har metategn i dag. Rettes med én hjelpefunksjon på de samme linjene som B6. | patch |
| E5 | Fraværssjekker mot en avkoblet `del` kan bestå uten å kontrollere noe | false | Alle grenene i `Kandidatliste` returnerer `<section>` på samme plass (`Kandidatflate.tsx:117–153`), så React gjenbruker noden. | avvist |
| E1 | `json()` kaster for status 204/1xx | low | `Response` med kropp og 204 kaster, og kastet blir «Får ikke kontakt» uten å registreres. 3.2 kan få 204. Rettelsen er én linje. | patch |
| B7 | jsdom-regelen er strengere enn begrunnelsen | low | `npm view jsdom@29 engines` gir `^22.13.0`, så 28.x er riktig, men OP-16 nevner bare 30/31. Begrunnelsen i OP-16 og KI-loggen rettes. | patch |
| B8 | 1.3-punktet (`FEILTEKSTER`) er ikke tatt | false | Johannes valgte «alle fem» og ikke «+1.3». Punktet står under Never. | avvist |
| B9 | 1.5-punktet om AGENTS.md er delvis løst, men ikke oppdatert | low | Diffen legger `npm run test` inn i AGENTS.md. Punktet i `deferred-work.md` sier fortsatt at det mangler. | patch |
| B10 | 401 er testet bare for vaktoversikten | low | Spesifikasjonen ba bare om vaktoversikten. Flere tester er mer enn en direkte rettelse. | avvist |
| B11 | Sårbarheten i vite 8.3.1 er ikke fulgt opp | medium | `npm audit` viser én høy, rettet i 8.3.8. Den fantes før denne endringen. | defer |
| B12 | Stack-tabellen i spine mangler testverktøyene | low | Tabellen (l.115–122) versjonsfester React, Vite og TS, men ikke Vitest, Testing Library og jsdom. | patch |
| B13 | P-13 får en frist ingen har satt («før story 4.6»), og AGENTS.md knytter P-13 til OP-16 | low | Avklaringspunktene l.783: fristen gjelder mobilvalget, ikke forståelsestesten. Rettes i `docs/testing.md`. AGENTS.md er agentkontekst. | patch (testing.md) + defer (AGENTS.md) |
| B14 | Den manuelle sjekklisten har ikke noe sted for resultatet | medium | Sensor ser etter dokumenterte manuelle tester. Det trengs en mal: hvem, dato, nettleser/OS, story og resultat per punkt. | patch |
| B15 | Vurderingsmatrisen nevner ikke grønn CI på 22.12 som utestående | low | Node 22.12 er ikke kjørt lokalt, og milepælen nevner bare gjennomgangen. | patch |
| B16 | Mangler i KI-loggen og regel for nye tester | low | M8b mangler testnavn. `docs/testing.md` ber ikke om at nye tester vises å kunne feile. | patch |
| B17 | Lockfila og spesifikasjonen mangler i diffen som ble gjennomgått | false | Utelatt med vilje. Lockfila er kontrollert med `npm ls`. Spesifikasjonen er påstandsfil for edge-case-laget. | avvist |

**Etter rettingen (orkestratoren, 2026-11-14):**
- Alle patch-punktene er rettet av implementeringsagenten. `npm run build` består. `node --test` gir 48 av 48, og `npx vitest run` gir 12 av 12 alene.
- Fire parallelle `npx vitest run` på denne maskinen feilet fortsatt, med tidsavbrudd i 1–4 tester per kjøring, også etter at `testTimeout` ble hevet til 20 s i `vitest.config.ts`. Den linjen la orkestratoren inn selv.
- Maskinen har 7,7 GB RAM, 0,6 GB ledig og 77–100 % CPU før testene starter. Fire kjøringer gir 16 jsdom-instanser og 125–154 s per kjøring.
- Vurdering: det er en stresstest maskinen ikke klarer, ikke en feil i testene. CI kjører én instans. VG1 er rettet for moderat last med `asyncUtilTimeout` 5 s og `testTimeout` 20 s.
- Holder ikke CI på 22.12 og `lts/*`, åpnes punktet igjen.

## Verification

**Commands:**
- `npm.cmd run build` i `frontend/`: består.
- `npm.cmd run test` i `frontend/`: 48 tester i `node:test`, og alle Vitest-testene består.
- `npx -y -p node@22.12.0 node node_modules/vitest/vitest.mjs run` i `frontend/`: består.
- `git diff 5a71652 -- frontend/src`: tom.
