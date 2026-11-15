# Testoversikt og manuell sjekkliste

Hva som testes automatisk, hvordan testene kjøres, og hva som fortsatt kontrolleres for
hånd og hvorfor. Dette er testplanen sensorveiledningen ber om under kriterium 3,
«dokumenterte manuelle tester eller testplaner der automatiske tester ikke er
hensiktsmessige» ([sensorveiledningen](emne/sensorveiledning-del-1.md)).

Opprettet 2026-11-14 sammen med komponenttestene (OP-16 i
[avklaringspunktene](beslutninger/avklaringspunkter.md)). Tallene gjelder denne datoen.

## Kommandoer

| Hva | Hvor | Kommando | Antall 2026-11-14 |
|---|---|---|---|
| Backend: regelmotor, API, lagring og arkitektur | `backend/` | `.venv\Scripts\python -m pytest` | 427 |
| Frontend: ren logikk (`node:test`) og komponenter (Vitest) | `frontend/` | `npm run test` | 49 + 23 |
| Frontend: typesjekk av kode og tester, og bygg | `frontend/` | `npm run build` | – |
| Modellverktøyene i `scripts/` | roten | `python -m unittest discover -s scripts -p "test_modelltest*.py"` | – |

I Windows PowerShell brukes `npm.cmd run test` og `npm.cmd run build` (se AGENTS.md).
`npm run test` kjører først `node --test` og deretter `vitest run`. Feiler den første,
kjøres ikke den andre. Bare komponenttestene kjøres med `npx vitest run` fra `frontend/`
(`npx.cmd` i PowerShell), og `npx vitest` kjører dem på nytt ved hver lagring (watch).
Én fil: `npx vitest run tester/komponenter/kandidatflate.test.tsx`.

CI ([`.github/workflows/`](../.github/workflows/)) kjører backendtestene med Python 3.12
og nyeste 3.x, og `npm run build` og `npm run test` med Node 22.12 og nyeste LTS, ved
hver push. Testene av modellverktøyene i `scripts/` og den manuelle sjekklisten under
er ikke med i CI.

## Trege maskiner og tidsavbrudd

Komponenttestene starter jsdom, en nettleser-DOM i Node, for hver testfil. Det krever
mye minne og CPU, og på en svak maskin kan testene få tidsavbrudd selv om koden er
riktig. Målt 2026-11-14 på maskinen der testene ble skrevet:

| | |
|---|---|
| Maskin | Intel Core i3-1115G4 (2 kjerner, 4 tråder), 7,7 GB RAM, Windows 11 |
| Belastning før start | 0,6 GB ledig RAM, CPU 35–100 % (VS Code, Chrome, Claude Code) |
| Én kjøring av `npx vitest run` | 12 av 12 på 17–21 s, med én og med fire arbeidere |
| Fire samtidige kjøringer, standard antall arbeidere (16 jsdom) | 1–4 tester per kjøring feilet med tidsavbrudd (125–154 s), også med `testTimeout` på 20 s |
| Fire samtidige kjøringer med `maxWorkers: 1` (4 jsdom) | 12 av 12 i alle fire (53 s hver) |

Derfor er oppsettet:

- `maxWorkers: 1` i [`vitest.config.ts`](../frontend/vitest.config.ts): én testfil om
  gangen. På maskinen over var det ikke tregere.
- `testTimeout: 20_000` (20 s per test) i `vitest.config.ts` og `asyncUtilTimeout: 5000`
  (5 s for `findBy…` og `waitFor`) i
  [`oppsett.ts`](../frontend/tester/komponenter/oppsett.ts).

Ser du «Test timed out» eller «Unable to find …» på kode som består i CI:

1. Kjør bare én testkjøring om gangen. Det gjelder også agenter og underagenter som
   kjører `npm run test` parallelt.
2. Lukk tunge programmer og kjør på nytt.
3. Hjelper ikke det, hev `testTimeout` i `vitest.config.ts` og `asyncUtilTimeout` i
   `oppsett.ts`. Skriv målingene inn i tabellen over, så gruppa ser hva som kreves.

På en sterk maskin kan flere arbeidere gjøre kjøringen raskere:
`npx vitest run --maxWorkers=4`.

## Hva som testes automatisk

### Backend

- **Harde regler, én testmodul per regel** (konvensjon fra arkitekturen), med
  grensetilfellene:
  - [`test_kompetanse.py`](../backend/tester/regelmotor/test_kompetanse.py) – kompetanse-minstekrav
  - [`test_kolliderende_vakt.py`](../backend/tester/regelmotor/test_kolliderende_vakt.py) – kolliderende vakt
  - [`test_11_timersregelen.py`](../backend/tester/regelmotor/test_11_timersregelen.py) – daglig hvile, sommertid
  - [`test_35_timersregelen.py`](../backend/tester/regelmotor/test_35_timersregelen.py) – ukentlig fri, ukeskifte
  - [`test_utelukkelsesoppsummering.py`](../backend/tester/regelmotor/test_utelukkelsesoppsummering.py) – Ekskludert-boksens tall
- **API** ([`tester/api/`](../backend/tester/api/)): innlogging og sesjon, vaktoversikt,
  vaktdetaljer, kandidater og godkjenning, med 401, 404, datafeil og fasiten
  for #4127 og #4189 (AV-07). Story 3.2 tester også endret grunnlag (P-09),
  ugyldig kandidat, atomisk bemanning, rollback, dublett og samtidige POST-kall (AD-5).
- **Lagring** ([`tester/lagring/`](../backend/tester/lagring/)): testdataene mot fasiten,
  brukere og passord, og at hver tabell er tatt med i grunnlagsmerket eller
  bevisst holdt utenfor (P-09).
- **Arkitektur** ([`test_arkitektur.py`](../backend/tester/test_arkitektur.py)):
  import-linter-kontrakten som forbyr `domene` å importere `adaptere` (AD-1, AD-2).

### Frontend: ren logikk (`node:test`)

Filene `frontend/tester/*.test.mjs` tester rene moduler i `src/` med en falsk `fetch`.
TypeScript buntes med `rolldown`.

- [`sesjon.test.mjs`](../frontend/tester/sesjon.test.mjs) – sesjonsvarsleren og sesjonsgenerasjonen i `api.ts`
- [`format.test.mjs`](../frontend/tester/format.test.mjs) – datoer og tider i `Europe/Oslo`, også kjørt i en annen tidssone
- [`kandidater.test.mjs`](../frontend/tester/kandidater.test.mjs) – tilstandene til kandidatlisten og tekstene i Ekskludert-boksen
- [`godkjenning.test.mjs`](../frontend/tester/godkjenning.test.mjs) – tilstandene til godkjenningsflaten og stiene

### Frontend: komponenter (Vitest, Testing Library, jsdom)

Filene `frontend/tester/komponenter/*.test.tsx` rendrer komponentene i jsdom og trykker
på knappene som en bruker. Elementene finnes etter rolle og tilgjengelig navn med
tekstene fra `src/tekster.ts`, ikke etter CSS-klasse. `fetch` er falsk, med ett sett svar
per URL ([`hjelpere.ts`](../frontend/tester/komponenter/hjelpere.ts)). En URL testen ikke
har satt opp, feiler testen.

| Testfil | Hva | Utsatt punkt |
|---|---|---|
| [`vaktvalg.test.tsx`](../frontend/tester/komponenter/vaktvalg.test.tsx) | Feil gir «Prøv igjen»; etter godkjenning vises bekreftelse med ansatt og vakt over oppdatert oversikt | 1.5, 3.2 |
| [`app.test.tsx`](../frontend/tester/komponenter/app.test.tsx) | 401 etter bekreftet sesjon viser innloggingen med «Sesjonen er utløpt» | 1.5 |
| | Stien `/vakt/4127/godkjenning/6` viser godkjenningsflaten; vellykket POST går via `App` til ny Vaktvalg-visning | 3.1, 3.2 |
| [`kandidatflate.test.tsx`](../frontend/tester/komponenter/kandidatflate.test.tsx) | Feil i kandidatlisten gir «Prøv igjen», og trykket henter listen på nytt. Datafeil viser tekst og datagrense uten liste. Hver rad viser timer i startuka som t:mm, også 0:00 uten vakter | 2.1, 4.1 |
| | Tomtilstanden (`ingen_gyldige_kandidater`) har ikon, full tekst, boks og innleietekst uten knapp utenom «Vis full liste». `ok` med tom liste gir feiltilstand. Lasting, feil, datafeil og ingen gyldige har ulik tekst, panelklasse og kombinasjon av rolle, ikon og knapp | 2.6 |
| | Ingen Ekskludert-boks ved 0 utelukkede. «Vis full liste» lukket, åpen og lukket med `aria-expanded` | 2.5 |
| | «Velg» sender vaktnummer og id for riktig kandidat, uten kall | 3.1 |
| [`godkjenningsflate.test.tsx`](../frontend/tester/komponenter/godkjenningsflate.test.tsx) | «Godkjenn erstatning» sender grunnlagsmerket; endret grunnlag krever nytt trykk; ugyldig kandidat og datafeil stopper godkjenning; allerede bemannet vakt gir bare «Til Vaktvalg» med fokus; sent POST-svar, sesjonsbytte og dobbeltklikk kontrolleres | 3.1, 3.2 |

Hver test er vist å kunne feile: en bevisst feil i komponenten gjorde den rød. Mutasjonene
og de røde meldingene står i [KI-loggen](ki-logg/2026-11-14-komponenttester.md).

**Nye komponenttester:**

- Legg dem i `frontend/tester/komponenter/` med navnet `*.test.tsx`. Vitest kjører bare
  de filene. Bruk ikke `*.test.ts`: typesjekken tar dem med, men Vitest gjør det ikke, og
  på Node 23.6 og nyere plukker `node --test` dem opp og feiler på importen av `vitest`.
- Bruk `falskFetch` og testdataene i `hjelpere.ts`, som har typene fra `src/api.ts`.
  Rutenøkkelen er stien for GET, eller `"POST /api/…"` med metode. Et kall uten rute
  feiler testen. Bygg regulære uttrykk av TEKSTER med `malRegex` eller `regexTekst`.
- Opprydding mellom testene (`cleanup`, stubbene, sesjonsvarsleren og stien) står i
  `oppsett.ts` og gjelder alle filene. App-tester setter stien med
  `window.history.replaceState` før render.
- Vis at testen kan feile: legg inn én bevisst feil i komponenten, se testen bli rød,
  tilbakestill, og noter mutasjonen og den røde meldingen i KI-loggen.
- `npm run build` typesjekker testene (`tsconfig.test.json`).

## Hva som er manuelt, og hvorfor

jsdom bygger DOM-en, men gjør ingen layout, beregner ikke CSS og viser ingenting. Derfor
kan komponenttestene ikke kontrollere:

- **Layout og bredde:** at v1 fungerer i smale nettleservinduer på en datamaskin
  (AV-17), at siden ikke ruller vannrett og at brede tabeller ruller i sin egen
  beholder (AV-14), samt at flaten tåler større skrift. Story 4.6 foreslår 1080,
  960 og 680 px som kontrollbredder; de kan justeres når storien spesifiseres.
- **Farger og fokusmarkering:** at nye elementer bruker designtokens (AV-13), at
  varselfarger og kontrast er riktige, og at fokusrammen synes når man går med tab
  (UX-DR24).
- **Samspillet med ekte backend:** komponenttestene bruker en falsk `fetch`. Om
  frontend og backend er enige om svarformen, kontrolleres av backendens API-tester og
  typene i `src/api.ts`, men ikke ende til ende.
- **Forståelse (P-13):** om en testperson uten hint forstår kandidatvisningen. Det er en
  brukertest, ikke en kodekontroll, og gjøres én gang, ikke per story.

De 12 komponenttestene dekker flytene som er listet i tabellen over, ikke alle
tilstander, knapper, ruter og API-kall i appen. Når en story legger til eller endrer en slik kobling,
må den legge til en komponenttest for flyten. Dersom testen ikke kan skrives i den
aktuelle storyen, dokumenteres en målrettet manuell kontroll som et åpent punkt.
Automatisk dekkede flyter trenger ikke samme manuelle kontroll (OP-16, alternativ A).

## Manuell sjekkliste for nye flater

«Manual checks» i nye spesifikasjoner tar med relevante punkter herfra og eventuelle
målrettede kontroller av flyter som ennå ikke har komponenttest. Kontrollen gjøres i
nettleseren mot ekte backend med testdata (README steg 2–4), før PR.
Egne akseptkriterier i storyen kontrolleres i tillegg. For story 4.6 gjelder blant
annet synlig kandidatidentitet ved vannrett rulling i rangeringstabellen, bevaring av
valgt vakt, åpne begrunnelser og valgt kandidat ved vindusendring, og skjermbilder ved
de tre smale kontrollbreddene (AV-17, epics).

1. **1080, 960 og 680 px** i et datamaskinvindu, samt 1600 px: ingen vannrett
   siderulling, ingen tekst som klippes eller overlapper, og alle handlinger kan nås.
   Brede tabeller ruller bare i sin egen beholder (AV-14, AV-17). 360 px kan brukes
   som ekstra regresjonskontroll, men er ikke et mobilkrav i v1.
2. **Tastatur:** gå gjennom den nye flaten med tab og enter alene. Fokusrammen synes på
   hvert element, og rekkefølgen følger siden.
3. **Farger:** nye elementer bruker tokens fra `frontend/src/stil/tokens.css`, ikke rå
   fargekoder (AV-13). Varsel og datafeil ser ut som i DESIGN.md.
4. **Større skrift:** skriftstørrelse «Stor» i Chrome-innstillingene. Ingen tekst
   klippes eller overlapper.
5. **Ekte backend:** flaten viser testdataene for #4127 og #4189 som forventet, etter
   innlogging gjennom Vite-proxyen.

Før resultatet i «Verification» i spesifikasjonen for storyen, eller i KI-loggen hvis
arbeidet ikke har en spesifikasjon. Bruk denne malen:

```markdown
**Manuell kontroll (docs/testing.md):** <navn>, <dato>, <nettleser og versjon> på <OS>, story <nr>
1. 1080, 960, 680 og 1600 px: bestått / avvik: <hva>
2. Tastatur og fokus: bestått / avvik: <hva>
3. Farger: bestått / avvik: <hva>
4. Større skrift: bestått / avvik: <hva>
5. Ekte backend: bestått / avvik: <hva>
Målrettet kontroll av flyt uten komponenttest: <flyt, resultat eller ikke relevant>
Ikke relevant: <punkt og hvorfor>
```

P-13s forståelsestest står for seg: én testperson, ett operativsystem og én skjermflate,
med tre oppgaver uten hint (§12 i avklaringspunktene). Planlagt arbeidsmål er før
story 4.6 ferdigstilles; dette er ikke et eget gruppevedtak om frist. Testen er ikke utført ennå.

## Story 4.3 – kostnad per kandidat (2026-11-15)

Domenetester i [`test_kostnad.py`](../backend/tester/regelmotor/test_kostnad.py) dekker 36-timersgrensen, ukeskifte, overlapp, brøktimer, begge sommertidsskifter og ugyldig lønn. API-testene kontrollerer #4127-fasit og begge kandidatgrunnlagene. Kandidat- og godkjenningsflatens komponenttester dekker kostnadsfordeling, overtid og oppdatert grunnlag. Etter integreringen med story 4.2 viser overtid og høy belastning hvert sitt `Varselmerke`. Komponenttesten «høy belastning og overtid vises som hvert sitt varselmerke» dekker ingen varsler, bare høy belastning, bare overtid og begge samtidig. P-09 for endret lønn testes i `test_godkjenningsgrunnlag.py`. Visuell kontroll og gjenstående punkter står i [spesifikasjonen](../_bmad-output/implementation-artifacts/spec-4-3-forenklet-kostnad-per-kandidat.md). Den integrerte raden med begge varslene er ikke kontrollert i nettleser.
