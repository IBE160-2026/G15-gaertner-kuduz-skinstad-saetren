# KI-logg: Komponenttester for frontend (Vitest, Testing Library, jsdom)

Dato: 2026-11-14. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md),
[handoffen](../../_bmad-output/implementation-artifacts/handoff-frontendtesting-2026-11-14.md), `AGENTS.md` og
OP-16 i [avklaringspunktene](../beslutninger/avklaringspunkter.md). Implementert av en underagent
(Claude Opus 5.5) i `bmad-build`, på branchen `frontend-komponenttester`. Loggen er agentens
egenrapportering og bør leses gjennom av et gruppemedlem.

## Oppgaven

Ingen frontendtest rendret en komponent. Tilstander, knapper og ruter i `Vaktvalg`, `Kandidatflate`,
`Godkjenningsflate` og `App` var bare kontrollert for hånd. Oppgaven var å innføre Vitest med Testing
Library og jsdom ved siden av `node --test`, skrive rendrede tester for de fem utsatte punktene
(1.5, 2.1, 2.4, 2.5 og 3.1), vise at hver test kan feile, og dokumentere hva som testes automatisk
og hva som fortsatt er manuelt.

## Prompten

Instruksjonen til implementeringsagenten, ordrett:

> Read C:\Users\johan\Documents\Studier\IBE160 Programmering med KI\turnushjelperen\_bmad-output\implementation-artifacts\spec-frontend-komponenttester.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start.
>
> When done, report what you changed, how you verified it, and anything left incomplete or risky.

## Hva modellen leverte

- **Pakker** (`npm install -D -E`): `vitest` 5.1.0, `@testing-library/react` 16.3.3,
  `@testing-library/dom` 10.4.2, `@testing-library/user-event` 14.6.10 og `jsdom` 28.1.0.
  28.x er siste jsdom som støtter Node 22.12: `npm view jsdom@29 engines` gir
  `^20.19.0 || ^22.13.0 || >=24.0.0` for alle 29.x, og 30 og 31 krever ^22.22.2.
  `package-lock.json` er oppdatert. `npm ls` viser ingen ugyldige avhengigheter.
- **Skript** i `frontend/package.json`: `test` er `node --test && vitest run`, og `build` er
  `tsc --noEmit && tsc --noEmit -p tsconfig.test.json && vite build`.
- **`frontend/vitest.config.ts`**: jsdom, og `include` bare `tester/komponenter/**/*.test.tsx`, så
  Vitest ikke prøver å kjøre `node:test`-filene.
- **`frontend/tsconfig.test.json`**: utvider `tsconfig.json` og tar med `src`, `tester/komponenter`
  og `vitest.config.ts`. `tsconfig.json` og `vite.config.ts` er ikke endret.
- **`frontend/tester/komponenter/hjelpere.ts`**: `json(data, status)`, `falskFetch` med en kø av svar
  per URL (det siste svaret gjentas), `kallTil` og felles `afterEach` med `cleanup()`,
  `vi.unstubAllGlobals()` og `settSesjonsvarsler(null)`. Et kall til en URL testen ikke har satt opp,
  feiler testen i `afterEach`, fordi et kast inne i `fetch` ellers bare ville blitt «Får ikke kontakt»
  i komponenten. Testdataene har typene fra `src/api.ts` (med `satisfies`, så feil form fanges av `tsc`).
- **Fire testfiler, 12 tester**, én eller flere per rad i matrisen i spesifikasjonen:
  `vaktvalg.test.tsx` (1), `app.test.tsx` (2), `kandidatflate.test.tsx` (6) og
  `godkjenningsflate.test.tsx` (3). Elementene finnes etter rolle og navn med tekstene fra
  `src/tekster.ts`.
- **Dokumentasjon:** ny [`docs/testing.md`](../testing.md) (testoversikt og manuell sjekkliste),
  README «Tester», AGENTS.md «Kjøring og verifisering», Testing-raden i ARCHITECTURE-SPINE,
  `deferred-work.md`, vurderingsmatrisen, OP-16 i avklaringspunktene, `docs/modellvalg-stories.md`
  og `persistent_facts` i `_bmad/custom/bmad-build.toml`.

Ingen fil i `frontend/src/` er endret.

## Hva som ble rettet, og hvorfor

- **Typecast i testdataene:** første versjon av `kandidatflate.test.tsx` hentet `datagrense` med
  `as Extract<Kandidatsvar, …>`. En cast skjuler feil form for `tsc`, som spesifikasjonen vil fange.
  Rettet før første kjøring: konstantene i `hjelpere.ts` bruker `satisfies Kandidatsvar`, som både
  kontrollerer formen og beholder den smale typen.
- **Mutasjonen «send feil id» (3.1):** den første ideen var at «Velg» alltid sendte den første
  kandidaten. API-et sorterer alfabetisk, så Jonas Bakke er først, og mutasjonen ville ikke blitt
  oppdaget av testen som velger Jonas. Mutasjonen ble i stedet å bytte argumentene i `onVelg`, som
  sender vaktnummeret som id.
- **Opprydding etter typefeiltesten:** agenten forsøkte å rydde opp med `git checkout -- .` i
  `frontend/`. Det ville også ha forkastet endringene i `package.json`. Kommandoen ble stoppet av
  tillatelsessystemet før den kjørte. Kontrollen ble gjort på nytt med en midlertidig, egen testfil
  som ble slettet etterpå.
- **YAML i `deferred-work.md`:** oppsummeringene som begynner med `[LØST …]` måtte stå i anførselstegn,
  som `[UTFØRT …]`-punktet fra 2.3, ellers leses de som en liste.
- **Punktet fra 2.5** sto ikke i `deferred-work.md`, bare som avvist funn i Review Triage Log i
  spesifikasjonen for 2.5. Det er ført inn og merket løst, så alle fem punktene står samlet.
- **Utdaterte kommentarer:** `tester/kandidater.test.mjs` og `tester/godkjenning.test.mjs` sa
  «Det finnes ingen komponenttestrigg». Bare kommentarene er endret. Testene er ikke flyttet eller endret.

## Mutasjoner

Hver mutasjon ble lagt inn i `frontend/src/` av et skript som leste filen som bytes, byttet én
tekststreng, kjørte hele Vitest-pakken, noterte de røde testene og skrev originalen tilbake.
`git diff 5a71652 -- frontend/src` var tom etterpå. M1–M9 er radene i spesifikasjonens matrise.
Mutasjonene med «b» er ekstra kontroller.

| # | Punkt | Mutasjon | Røde tester (av 12) | Rød melding |
|---|---|---|---|---|
| M1 | 1.5 Vaktvalg | `forsok` fjernet fra deps (`[forsok]` → `[]`) | 1: vaktvalg «feil gir Prøv igjen …» | `Unable to find role="heading" and name "Krever handling"` |
| M2 | 1.5 401 (App) | `vedAvvistSesjon?.()` kommentert ut i `api.ts` | 1: app «401 … sesjonen er utløpt» | `Unable to find role="heading" and name "Logg inn"` |
| M3 | 2.1 Kandidatliste | `forsok` fjernet fra deps (`[vaktnummer, forsok]` → `[vaktnummer]`) | 1: kandidatflate «feil gir Prøv igjen …» | `Unable to find role="button" and name "Velg Jonas Bakke"` |
| M3b | 2.1 Datafeil | linjen med datagrensen fjernet | 1: kandidatflate «datafeil viser tekst og datagrense» | `Unable to find an element with the text: Turnusgrunnlaget går til 05.10.2026 00:00.` |
| M4 | 2.4 Tom liste | `length === 0` → `length !== 0` | 4, blant dem «tom liste viser ingen gyldige» | `Unable to find an accessible element with the role "status"` |
| M5 | 2.5 Ekskludert-boks | `if (oppsummering.totalt === 0) return null;` fjernet | 1: «vises ikke når ingen er utelukket» | `expected <p class="brodtekst"></p> to be null` |
| M5b | 2.5 Ekskludert-boks | `aria-expanded={åpen}` → `aria-expanded={false}` | 1: «Vis full liste er lukket, åpen og lukket igjen» | `expected 'false' to be 'true'` |
| M6 | 3.1 Velg | `onVelg(data.vaktnummer, ansattId)` → `onVelg(ansattId, data.vaktnummer)` | 1: «Velg sender vaktnummer og id» | `expected "vi.fn()" to be called with arguments: [ 4127, 6 ]` |
| M7 | 3.1 Rute (App) | `godkjenning !== null` → `godkjenning === null` i rutevalget | 2, blant dem «stien /vakt/4127/godkjenning/6 …» | `Unable to find role="heading" and name "Jonas Bakke"` |
| M8 | 3.1 Godkjenn | «Godkjenn erstatning» øker også `forsok`, så flaten henter på nytt | 1: «Godkjenn erstatning gjør ingen kall …» | `expected "vi.fn()" to be called 1 times, but got 2 times` |
| M8b | 3.1 Avbryt | `onClick={onTilbake}` → `onClick={() => {}}` på «Avbryt» | 1: «Godkjenn erstatning gjør ingen kall og viser bare at ingenting er lagret; Avbryt går tilbake» | `expected "vi.fn()" to be called 1 times, but got 0 times` |
| M9 | 3.1 Datafeil | knappene «Avbryt» og «Godkjenn erstatning» lagt inn i datafeilgrenen | 1: «datafeil viser ingen knapper» | `expected <button type="button"></button> to be null` |
| M9b | 3.1 404 | samme knapper lagt inn i 404-grenen | 1: «404 viser kan ikke velges …» | `expected <button type="button"></button> to be null` |

Alle 13 mutasjonene ga minst én rød test. M7 gjorde også 401-testen rød, fordi den snudde betingelsen
rendrer `Godkjenningsflate` med `godkjenning === null` og krasjer App.

## Kvalitetssikring

- `npm run test` i Git Bash og `npm.cmd run test` i Windows PowerShell: 48 av 48 `node:test`-tester
  og 12 av 12 Vitest-tester bestått, begge på Node 26.7.0. Ingen advarsler om `act(...)` i utskriften.
- `npm run build`: bestått. Med en midlertidig testfil med en typefeil
  (`const feilType: number = "tekst"`) feilet bygget med `TS2322` i `tsc -p tsconfig.test.json`.
  Filen ble slettet etterpå.
- `node --test` gir fortsatt 48 tester, så Vitest-filene (`*.test.tsx`) blir ikke plukket opp av den.
- `npm ls --depth=0`: alle pakkene i eksakt versjon, ingen ugyldige avhengigheter.
- **Node 22.12 er ikke kjørt lokalt.** `npx -y -p node@22.12.0 …` ble stoppet av
  tillatelsessystemet, fordi det laster ned Node. `engines` i `package-lock.json` er kontrollert i
  stedet: `vitest` (`^22.12.0 || ^24.0.0 || >=26.0.0`), `jsdom` og avhengighetene
  (`^20.19.0 || ^22.12.0 || >=24.0.0`) og Testing Library godtar 22.12. CI kjører 22.12 og `lts/*`
  ved push. Prøveoppsettet i handoffen besto på 22.12 med de samme versjonene.
- `npm audit` melder én høy sårbarhet i `vite` 8.3.1 (rettet i 8.3.8). Den fantes før dette arbeidet
  og gjelder utviklingsserveren. Vite er ikke oppgradert her, fordi spesifikasjonen ikke omfatter det.
- Render-skriptet for `bmad-build` (`_bmad/scripts/render_skill.py`) er kjørt, og det nye
  `persistent_facts`-punktet står i den genererte `workflow.md`.

## Retting etter kodegjennomgang (2026-11-14)

En gjennomgang av implementeringen fant disse feilene i den genererte koden og dokumentasjonen.
Alle er rettet:

- **Ustabil 401-test:** kjeden `/api/meg` → `/api/vaktoversikt` 401 → innlogging tok mer enn
  Testing Librarys standard på 1000 ms når fire `npx vitest run` gikk parallelt, og alle fire
  feilet på `app.test.tsx`. Rettet med `configure({ asyncUtilTimeout: 5000 })` i det nye
  `oppsett.ts`. Implementeringsagenten rapporterte 12 av 12 i fire parallelle kjøringer.
  Orkestratorens kontroll etterpå ga et annet bilde: fire parallelle kjøringer feilet fortsatt,
  med tidsavbrudd i 1–4 tester per kjøring. Da var `asyncUtilTimeout` like høy som Vitests
  standard `testTimeout` på 5 s. Orkestratoren hevet `testTimeout` til 20 s i
  `vitest.config.ts`, men fire parallelle kjøringer feilet fortsatt (125–154 s per kjøring).
  Maskinen hadde 7,7 GB RAM med 0,6 GB ledig og 77–100 % CPU før testene startet. Én kjøring
  alene består (12 av 12 på 19 s). Rettingen dekker moderat last. Fire samtidige kjøringer med
  til sammen 16 jsdom-instanser tåler ikke denne maskinen. CI kjører én instans.
- **Skjult opprydding:** `afterEach` ble registrert som en sideeffekt av å importere
  `hjelpere.ts`, og `window.history` ble ikke nullstilt. Flyttet til
  `tester/komponenter/oppsett.ts` i `test.setupFiles`, som også setter stien tilbake til `/`.
  `hjelpere.ts` eksporterer `hentOgNullstillUventede` til sjekken.
- **Metode i `falskFetch`:** rutene var nøklet bare på URL, så en POST i story 3.2 ville fått
  GET-svaret, og `kallTil` ville talt begge. Nå kan nøkkelen ha metode (`"POST /api/…"`), en
  nøkkel uten metode gjelder GET, og et kall med en metode uten rute er uventet. `kallTil`
  teller per metode.
- **`json()` med 204:** `new Response(kropp, { status: 204 })` kaster, også for 101, 205 og 304,
  og kastet ble «Får ikke kontakt» uten å registreres. Disse statusene får nå kroppen `null`.
- **`vitest.config.ts`** kopierte `plugins: [react()]` i stedet for å utvide `vite.config.ts`, så et
  senere alias eller `define` ville manglet i testene. Nå `mergeConfig(viteConfig, …)`.
- **Hardkodede uttrykk:** `/^Velg /` og `/utelukket av harde regler/` var skrevet på nytt i testen,
  og `new RegExp` av TEKSTER ble bygd uten escaping. Nå bygges uttrykkene av
  `TEKSTER.godkjenning.velgEtikett` og `TEKSTER.ekskludertBoks.totaltUtelukket` med `malRegex`,
  og `regexTekst` escaper. M5 ga fortsatt rød test etter endringen.
- **`docs/testing.md`:** sa feilaktig at en fil som ikke heter `*.test.tsx`, verken tas med av Vitest
  eller typesjekken. `tsconfig.test.json` typesjekker også `.test.ts`, og på Node 23.6 og nyere
  plukker `node --test` opp `*.test.ts` og feiler på importen av `vitest`. Rettet. I tillegg:
  hvordan man kjører bare komponenttestene, ingen frist for P-13 (fristen før story 4.6 gjelder
  mobilvalget, ikke forståelsestesten), en mal for å føre den manuelle kontrollen, og at nye
  komponenttester skal vises å kunne feile.
- **Dokumentasjon ellers:** OP-16 og denne loggen sier nå hvorfor jsdom 29 ikke kan brukes,
  versjonstabellen i ARCHITECTURE-SPINE har fått testverktøyene, `deferred-work.md` fører at
  `npm run test` nå står i AGENTS.md, og vurderingsmatrisen sier at grønn CI på Node 22.12 og
  `lts/*` gjenstår.

Verifisert etter rettingene: `tsc -p tsconfig.test.json` uten feil, `npx vitest run` 12 av 12 alene
(fire parallelle: se punktet om den ustabile 401-testen), og en midlertidig testfil (slettet etterpå) som viste at et
uventet GET-kall og en POST uten POST-rute gjør testen rød, at `kallTil` teller per metode, at
`json()` tåler 204/205/304, og at stien er `/` ved starten av neste test.

## Gjenstår

- Uavhengig kodegjennomgang (`bmad-build` med underagenter) og PR-gjennomgang av et annet
  gruppemedlem.
- Grønn CI på Node 22.12 og `lts/*` etter push.
- Story 3.2 må endre testen for «Godkjenn erstatning», og story 2.6 testen for tom liste.
