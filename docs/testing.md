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
| Backend: regelmotor, API, lagring og arkitektur | `backend/` | `.venv\Scripts\python -m pytest` | 412 |
| Frontend: ren logikk (`node:test`) og komponenter (Vitest) | `frontend/` | `npm run test` | 48 + 12 |
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
  vaktdetaljer, kandidater og godkjenningsgrunnlaget, med 401, 404, datafeil og fasiten
  for #4127 og #4189 (AV-07).
- **Lagring** ([`tester/lagring/`](../backend/tester/lagring/)): testdataene mot fasiten,
  og brukere og passord.
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
| [`vaktvalg.test.tsx`](../frontend/tester/komponenter/vaktvalg.test.tsx) | Feil i Vaktvalg gir «Prøv igjen», og trykket henter på nytt | 1.5 |
| [`app.test.tsx`](../frontend/tester/komponenter/app.test.tsx) | 401 etter bekreftet sesjon viser innloggingen med «Sesjonen er utløpt» | 1.5 |
| | Stien `/vakt/4127/godkjenning/6` viser godkjenningsflaten | 3.1 |
| [`kandidatflate.test.tsx`](../frontend/tester/komponenter/kandidatflate.test.tsx) | Feil i kandidatlisten gir «Prøv igjen», og trykket henter listen på nytt. Datafeil viser tekst og datagrense uten liste | 2.1 |
| | Tom liste viser «Ingen gyldige kandidater» og ingen «Velg»-knapp | 2.4 |
| | Ingen Ekskludert-boks ved 0 utelukkede. «Vis full liste» lukket, åpen og lukket med `aria-expanded` | 2.5 |
| | «Velg» sender vaktnummer og id for riktig kandidat, uten kall | 3.1 |
| [`godkjenningsflate.test.tsx`](../frontend/tester/komponenter/godkjenningsflate.test.tsx) | «Godkjenn erstatning» gjør ingen kall. «Avbryt» og tilbakelenken går tilbake. Datafeil og 404 viser ingen knapper for godkjenning | 3.1 |

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

- **Layout og bredde:** vannrett siderulling ved 360 px, at innholdet får plass ved
  1600 px, og at flaten tåler større rotskrift (AV-14, DESIGN.md).
- **Farger og fokusmarkering:** at nye elementer bruker designtokens (AV-13), at
  varselfarger og kontrast er riktige, og at fokusrammen synes når man går med tab
  (UX-DR24).
- **Samspillet med ekte backend:** komponenttestene bruker en falsk `fetch`. Om
  frontend og backend er enige om svarformen, kontrolleres av backendens API-tester og
  typene i `src/api.ts`, men ikke ende til ende.
- **Forståelse (P-13):** om en testperson uten hint forstår kandidatvisningen. Det er en
  brukertest, ikke en kodekontroll, og gjøres én gang, ikke per story.

Alt annet i koblingen i komponentene, som tilstander, knapper, ruter og hvilke kall som
gjøres, dekkes av komponenttestene og skal ikke kontrolleres for hånd (OP-16, alternativ
A).

## Manuell sjekkliste for nye flater

«Manual checks» i nye spesifikasjoner tar bare med punkter herfra. Kontrollen gjøres i
nettleseren mot ekte backend med testdata (README steg 2–4), før PR.

1. **360 px og 1600 px** i enhetsverktøylinjen: ingen vannrett siderulling, og alt
   innhold er lesbart.
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
1. 360 px og 1600 px: bestått / avvik: <hva>
2. Tastatur og fokus: bestått / avvik: <hva>
3. Farger: bestått / avvik: <hva>
4. Større skrift: bestått / avvik: <hva>
5. Ekte backend: bestått / avvik: <hva>
Ikke relevant: <punkt og hvorfor>
```

P-13s forståelsestest står for seg: én testperson, ett operativsystem og én skjermflate,
med tre oppgaver uten hint (§12 i avklaringspunktene). Den er ikke utført ennå.
