# KI-logg: Story 1.4 – beskyttede flater og utløpt sesjon

## Oppgave og prompt

Oppgaven var å implementere [spesifikasjonen for Story 1.4](../../_bmad-output/implementation-artifacts/spec-1-4-beskyttede-flater-og-utlopt-sesjon.md) fullt ut, med spesifikasjonen som eneste kilde til kravene. Den ba om standardvern før API-ruting, utlogging med sletting av cookie, URL-vern, håndtering av utløpt sesjon, sesjonsgenerasjon mot gamle svar, tester og dokumentasjon. Epic-konteksten og `AGENTS.md` var påkrevd kontekst. OP-10 bestemmer JWT i `HttpOnly`-cookie gjennom Vite-proxy, og AV-13/14 bestemmer stil og bredde.

## Det modellen leverte

- Middleware som krever gyldig token og eksisterende bruker for alle `/api`-kall utenom de tre offentlige metode/sti-parene. Den kjører før ruting og returnerer AD-4-feilen `mangler_sesjon`; avvist cookie slettes.
- `POST /api/utlogging` som sletter samme cookie. Automatisk API-dokumentasjon er slått av.
- Frontend med History API, sjekk av `/api/meg` ved oppstart og tilbake/frem, skjult innhold mens sjekken pågår, egen ikke-funnet-tilstand og «Logg ut». Beskyttede 401-svar varsles før JSON-lesing og bare for generasjonen som sendte kallet.
- Regresjonstester for standardvernet, ukjent rute, metode, ugyldige token, utlogging og deaktivert dokumentasjon. README er oppdatert.

## Rettelser og begrunnelser

- `kall<T>` håndterer 204 uten JSON eksplisitt, siden utlogging ellers ville blitt tolket som nettverksfeil.
- 401 uten JSON blir fortsatt klassifisert som avvist sesjon, siden en proxy kan svare uten AD-4-kropp.
- Vernet avgrenser `/api` og `/api/…` presist, slik at stier med samme bokstavprefiks ikke trekkes inn.
- De eldre 404/405-testene logger nå inn først, siden ukjent rute og metode skal gi 401 uten sesjon.
- Uavhengig kodegjennomgang fant at tilbake/frem kunne oppheve utloggingssperren, og at et sent innloggingssvar kunne sette cookie etter at UI hadde forkastet svaret. Utlogging sperrer nå navigasjonskontroll til svaret er håndtert; sent innloggingssvar utløser ny kontroll av faktisk cookie.
- Ved nettverksfeil under navigasjon beholdes mål-URL-en, og beskyttet innhold skjules til brukeren prøver kontrollen igjen. Fokus flyttes til retry-knappen eller brukernavnfeltet når flaten skifter.
- Frontendens løpssituasjoner manglet kjørbar kontroll. Tre små Node-tester med styrte svar ble lagt til uten nye pakker. En backendtest kontrollerer felles vern etter at brukeren er slettet.

## Kvalitetssikring

- `backend/.venv/Scripts/python -m pytest -q`: 127 tester bestod etter reviewrettelsene.
- `npm.cmd run test` i `frontend/`: 3 tester bestod. `npm.cmd run build`: typesjekk og Vite-bygg bestod.
- Nettlesermatrisen fra spesifikasjonen er ikke manuelt bekreftet i denne økten. Lokale backend- og Vite-servere startet med en isolert testdatabase, men Computer Use meldte at nettleseren `iab` ikke er tilgjengelig. Særlig vist innhold ved direkte URL, tastatur og 360px/1600px må kontrolleres i en faktisk nettleser før Story 1.4 kan godkjennes.

Dette er implementeringsbevis for FR13/NFR6 og AD-4, ikke en påstand om at Story 1.4 er godkjent eller ferdig gjennomgått etter OP-04.

## Videre kontroll 2026-11-08

Backend og Vite ble startet mot en isolert testdatabase med fiktive testdata. Den innebygde nettleseren svarte «No browser is available». Windows Computer Use kunne heller ikke koble til sin native pipe (`Systemet finner ikke angitt fil`). Serverne ble stoppet. Ingen faktisk nettleservisning, tastaturkontroll eller kontroll ved 360px/1600px ble dermed gjennomført. De tidligere resultatene (127 backendtester, 3 frontendtester og vellykket bygg) står ved lag, men storyen beholdes `in-review` med sprintstatus `in-progress` til nettlesermatrisen er kjørt og dokumentert.

Lokal PR-gjennomgang av commit `9473de4` ble gjort av to uavhengige agenter. API-gjennomgangen fant ingen nye avvik. Frontend-gjennomgangen fant at fokusrammen på «Logg ut» brukte samme farge som appbaren og derfor ikke var synlig ved tastaturnavigasjon. CSS ble rettet til å bruke den eksisterende lyse fargetokenen `--color-on-accent`. Visuell bekreftelse i nettleser gjenstår.

## Nettleserkontroll med Playwright MCP 2026-11-08

Kontrollen brukte lokale backend- og Vite-tjenester med en isolert SQLite-database i midlertidig mappe, seedet med fiktive data og et eget testpassord. Databasen ble fjernet og tjenestene stoppet etterpå. OP-10s tre offentlige metode/sti-par og AV-13/14s visningskrav ble kontrollert. Ingen prosjektkode ble rettet under denne kontrollen.

| Akseptansekriterium i spesifikasjonen | Fremgangsmåte og observert resultat | Status |
|---|---|---|
| Standardvern for `/api` uten gyldig JWT | Uten sesjon ga `/api/meg`, `/api/utlogging`, ukjent `/api`-sti og feil metode 401 med `{kode,melding}` og `mangler_sesjon`. `GET /api/helse` og `GET /api/innloggingsinfo` ga 200; sistnevnte viste bare `passord_kilde`. Feil legitimasjon på offentlig `POST /api/innlogging` ga `feil_innlogging`. Med sesjon ga `/api/meg` 200 og ukjent sti 404. `document.cookie` var tom også mens sesjonen virket, i tråd med `HttpOnly`. | Bestått |
| Direkte beskyttet URL uten sesjon | Åpnet `/turnus/kirurgisk-sengepost` uten cookie. URL ble erstattet med `/logg-inn`; bare innloggingsflate ble vist, uten utløpsmelding eller beskyttet innhold. | Bestått |
| Utløpt sesjon og 401 uten JSON | Startet backend med `TURNUSHJELPEREN_JWT_MINUTTER=1`, logget inn og lot siden stå åpen over ett minutt. Utlogging som beskyttet handling ga 401 og ett nettverkskall, uten stille fornyelse eller gjentakelse. Innlogging med «Sesjonen er utløpt. Logg inn på nytt.» ble vist. En simulert 401 uten JSON fra `/api/meg` ga samme visning. | Bestått |
| Utlogging og cookie | Tastatur-Enter på «Logg ut» ga 204; appbaren viste «Ikke innlogget», innloggingsfeltet fikk fokus, og `/api/meg` ga deretter 401. | Bestått |
| Tastatur og bredder | Ved 360 og 1600 px var knappen innenfor vinduet, `:focus-visible` ga hvit, heltrukket fokusramme og dokumentets rullebredde var lik visningsbredden. | Bestått |

Ytterligere nettleserprøver: `/logg-inn` med gyldig sesjon gikk til oversikten; ukjent beskyttet URL med gyldig sesjon viste «Fant ikke siden.»; tilbake-navigasjon kontrollerte sesjonen før oversikten ble vist. Med styrt forsinkelse i nettleserens `fetch`-lag ble et gyldig `/api/meg`-svar levert etter faktisk utlogging; beskyttet innhold kom ikke tilbake. Et 401-svar fra en gammel sesjonsgenerasjon ble levert etter utlogging og ny innlogging; den nye oversikten ble stående uten utløpsmelding. Disse to prøvene styrte svartid/svarkropp i Playwright, mens inn- og utlogging traff det lokale API-et. Ingen av prøvene feilet. Nettleseren viste forventede 401-feil i konsollen og en 404 for `favicon.ico`; sistnevnte er ikke del av Story 1.4s akseptansekriterier.

Regresjonskontroll i denne økten: `backend/.venv/Scripts/python -m pytest -q` ga **127 bestått**; `npm.cmd run test` i `frontend/` ga **3 bestått**. Alle fem akseptansekriterier er dermed verifisert i nettleser. Storyen beholdes `in-review` og sprintstatus `in-progress`: arbeidet er på feature-branch, og PR-gjennomgangen kan ikke avsluttes uten PR. Det ble ikke pushet eller opprettet PR i denne økten.
