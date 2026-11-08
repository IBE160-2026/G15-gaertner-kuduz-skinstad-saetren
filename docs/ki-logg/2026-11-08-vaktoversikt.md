# KI-logg: Story 1.5 – vaktoversikt med «Krever handling»

## Oppgave og prompt

Oppgaven var å implementere [spesifikasjonen for Story 1.5](../../_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md) fullt ut. Prompten til implementeringsagenten (Claude Opus 5.5, startet av `bmad-build`):

> Read `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md` fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.

Konteksten var `epic-1-context.md`, `AGENTS.md`, beslutningsreferatet, `epics.md` (story 1.5), `mockups/key-vaktvalg.html` og DESIGN.md. Beslutningene i spesifikasjonen er tatt av Mithad Kuduz 2026-11-08 (OP-11). Relevante vedtak: AV-03 (starttid avgjør perioden), AV-13 (tokens, `rem` for skrift) og AV-14 (1180 px, tabell som ruller i egen beholder).

## Det modellen leverte

- `backend/adaptere/lagring/vaktoversikt.py`: `hent_vaktoversikt(okt, bruker_id)` henter turnusen via `bruker.turnus_id`, vakter med start i `[periode_start, periode_slutt)` sortert etter start og vaktnummer, delt i «krever handling» (med navnet på den som var satt opp, `meldt_fra` og grunnen) og bemannet (navn, stilling, ansiennitet). Antall ansatte er antall rader i `ansatt` (kjent begrensning med én avdeling).
- `GET /api/vaktoversikt` i `adaptere/api/main.py` med Pydantic-modeller. Bare data; tekst lages i frontend. Ingen 404-gren. Blir brukeren borte mellom vernet og spørringen, svarer ruten 401 `mangler_sesjon` som vernet.
- `backend/tester/api/test_vaktoversikt.py`: 10 tester for vern, innhold, sortering, periodegrensen (#3338/#3339 ute, #4265 inne), at historikken ikke vises, tidssone og databasen der ingen mangler bemanning. Fixturene importeres fra `test_innlogging.py`.
- `frontend/src/format.ts` med rene funksjoner i `Europe/Oslo`, bygget fra tallene i `formatToParts`. Ukedagnavnene og vakttypene står i `tekster.ts`.
- `Vaktvalg.tsx` og `Brodsmulesti.tsx`. `Startside.tsx` og `TEKSTER.startside` er slettet. `App` gir `onVelgVakt`, som kaller `naviger` og `setSti`.
- Nye tokens i `tokens.css` og stiler i `app.css` uten rå mål eller fargekoder.
- `frontend/tester/format.test.mjs`: 10 tester som fester teksten.

## Rettelser og begrunnelser

- **`"test": "node --test tester/"` virket ikke.** Spesifikasjonen ba om denne kommandoen. Med Node 26 tolkes argumentet som et filmønster, ikke en mappe, og kjøringen feilet med «test failed» uten at noen test ble funnet. Med Node 20 hadde det virket, så kommandoen kan ikke dekke begge. Endret til `"test": "node --test"`, som finner `*.test.mjs` rekursivt og hopper over `node_modules` i både Node 20 og nyere. Kontrollert: alle testfilene kjøres (3 sesjonstester og formateringstestene). Dette er et avvik fra ordlyden i spesifikasjonen, ikke fra hensikten.
- **Linjeskift.** En redigering i `api.ts` ga blandede linjeskift (`\r\r\n`). Rettet før commit.
- **Ukedag uten ICU-tekst.** Spesifikasjonen ba om `formatToParts` med stor forbokstav. For at teksten ikke skal avhenge av ICU-versjonen, hentes bare tallene (år, måned, dag, time, minutt) fra `formatToParts`, og ukedagen regnes fra datoen og slås opp i tekstlisten.

Valg som ikke står i spesifikasjonen:

- Brødsmulestien vises når dataene er lastet, fordi perioden kommer fra API-et. Under lasting vises bare lasteteksten.
- Teksten «Ingen bemannede vakter i perioden» når tabellen ville vært tom, så tabellen aldri står uten rader.
- Linja ved døgnskifte har fargen `#8a99a8` (token `--color-day-divider`), en mørkere variant av kantfargen, og bredden 2 px. Fargen er ikke en statusfarge.
- Linja i varselboksen bruker `body` (12,5 px) i stedet for mockupens 12 px, fordi DESIGN.md ikke har en 12 px-rolle for brødtekst.
- Cellene i tabellen brytes ikke. På smale skjermer ruller tabellen i beholderen (AV-14).

### Rettet etter uavhengig kodegjennomgang (2026-11-08)

Gjennomgangen ble gjort av en egen agent som ikke hadde sett implementeringen. Den fant ti mangler, og alle er rettet:

1. **Formateringstestene var ikke følsomme for tidssone.** Gruppas maskiner går i Oslo-tid, så testene ville bestått også uten `timeZone: "Europe/Oslo"`. `format.test.mjs` kjører nå hele fila på nytt i en underprosess med `TZ=America/New_York`, satt i `env` slik at det virker også på Windows. Underprosessen kontrollerer først at sonen faktisk er en annen. Kontrollert ved å fjerne `timeZone` midlertidig: testen feilet, og etter at endringen ble tilbakestilt, bestod den.
2. **Regelen for radklassene var ikke testet.** Den er flyttet til den rene funksjonen `radklasser(vakter, i)` i `format.ts`, som Vaktvalg bruker, og er festet i testene: første rad har fet dato og ingen linje, et senere døgnskifte har linje, og `row-alt` står på annenhver rad.
3. **Tabellbeholderen kunne ikke nås med tastatur.** Den ruller på 360 px og har nå `tabIndex={0}`, `role="region"` og `aria-labelledby="bemannet"`.
4. **Bevisene for nettleserkontrollen lå utenfor repoet.** Skriptene og fire skjermbilder er kopiert til [`2026-11-08-vaktoversikt/`](2026-11-08-vaktoversikt/README.md). De ble sjekket for passord, nøkler og personlige stier først.
5. **Nødløsningen i ruten var ikke testet.** Det gjelder tilfellet der `hent_vaktoversikt` gir `None`. En test bytter ut funksjonen og kontrollerer 401, `mangler_sesjon` og at cookien slettes.
6. **Periodegrensen var ikke testet ved de eksakte kantene.** Testen legger inn én vakt nøyaktig ved `periode_start` (med) og én nøyaktig ved `periode_slutt` (ikke med), i sin egen database.
7. **Tidssonetesten dekket bare `bemannet`.** Den dekker nå også `krever_handling` (start, slutt og `meldt_fra`) og `periode_start`, `periode_slutt` og `sist_oppdatert`.
8. **To grener var ikke testet:** en varighet som ikke er hele timer («(7,5 t)»), og `varsellinje` når `satt_opp` er satt, men `grunn` eller `meldt_fra` mangler.
9. **Punktum.** «Ingen bemannede vakter i perioden» mistet punktumet, så teksten ligner «Ingen vakter krever handling nå».
10. **README.** Den sa at `npm run test` kjører testfilene i `tester/`. Det riktige er at `node --test` leter i hele `frontend/` utenom `node_modules`. Teksten er rettet, og de nye linjene er brutt om til samme bredde som resten.

## Kvalitetssikring

- Fra `backend/`: `.venv\Scripts\python -m pytest` ga **137 bestått** (127 fra før og 10 nye) før gjennomgangen. Etter rettelsene ga `tester/api/test_vaktoversikt.py` **12 bestått**. Hele pakken kjøres på nytt av koordinatoren.
- Fra `frontend/`: `npm.cmd test` ga **13 bestått** før gjennomgangen og **15 bestått** etter rettelsene, iberegnet kjøringen i New York-tid. `npm.cmd run build` bestod (typesjekk og Vite-bygg).
- **Nettleserkontroll i headless Chrome 156 via Chrome DevTools Protocol**, mot backend og Vite med en egen database i en midlertidig mappe (testdata og eget testpassord). Skriptene og skjermbildene ligger i [`2026-11-08-vaktoversikt/`](2026-11-08-vaktoversikt/README.md). Kontrollen ble kjørt før rettelsene etter gjennomgangen, så den viser ikke at tabellbeholderen kan nås med tab. Tjenestene ble stoppet etterpå. Resultat, for 1600 og 360 px og standard skriftstørrelse 16 og 20 px:
  - brødsmulesti «Turnus > Kirurgisk sengepost > Uke 39–40, 2026» med avdelingen i fet skrift;
  - `h1` «Vaktvalg» visuelt skjult, to `h2` og `h3` «Vakt #4127 — Dagvakt, Kirurgisk sengepost» og «Vakt #4189 — Nattevakt, Kirurgisk sengepost»;
  - linjene nøyaktig som i matrisen, med «Mangler bemanning» i `danger` og fet;
  - 164 rader, 82 med `row-alt`, 13 døgnskifter med linje, ingen linje på første rad, fet dato på første rad;
  - «Bemannet» i `text-main`, ikke `ok`;
  - fotnoten «Turnus oppdatert 27.09.2026 06:20 · 25 ansatte totalt i avdelingen»;
  - ingen vannrett siderulling i noen av de fire variantene; tabellen ruller i egen beholder på 360 px; ingen klippet tekst ved 20 px; ingen utropstegn i teksten utenom ikonet.
- **Tastatur:** tab nådde begge «Velg vakt»-knappene, og enter ga `/vakt/4127/kandidater` og `/vakt/4189/kandidater` med «Fant ikke siden.».
- Skjermbildene ble sammenlignet med `key-vaktvalg.html`. Avvikene er de som er bestemt i spesifikasjonen: ingen «Se detaljer», nøytral tag og fotnoten fra dataene.
- Ikke kontrollert i nettleser: tomtilstanden «Ingen vakter krever handling nå» (dekket av API-testen for tom liste, ikke vist i nettleser) og feiltilstanden med «Prøv igjen» (ikke prøvd med stoppet backend). Uavhengig kodegjennomgang er ikke gjort i denne økten.

Dette er implementeringsbevis for FR1, UX-DR3, UX-DR5, UX-DR6 og AV-03, ikke en påstand om at Story 1.5 er godkjent.
