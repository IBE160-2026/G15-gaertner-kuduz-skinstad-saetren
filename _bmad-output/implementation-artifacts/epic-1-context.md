# Epic 1 Context: Innlogging og vaktoversikt

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Turnusansvarlig logger inn, ser avdelingens vakter i perioden med manglende bemanning under «Krever handling», og velger vakten som skal bemannes på nytt. Epicet etablerer kjørbart prosjekt, fiktive data, sesjon og tilgangskontroll før kandidatfiltrering, rangering og godkjenning bygges i senere epics.

## Stories

- Story 1.1: Prosjektoppsett som kjører fra en ren klone
- Story 1.2: Fiktiv turnus med ansatte og vakter
- Story 1.3: Innlogging for turnusansvarlig
- Story 1.4: Beskyttede flater og utløpt sesjon
- Story 1.5: Vaktoversikt med «Krever handling»
- Story 1.6: Velge vakten som skal bemannes

## Requirements & Constraints

- Bare turnusansvarlig logger inn med brukernavn og passord. Ingen registrering, passordgjenoppretting, SSO eller andre roller i v1.
- Alle API-funksjoner krever gyldig sesjon, unntatt innlogging, helsesjekk og `GET /api/innloggingsinfo`. Sistnevnte er et bevisst åpent unntak: innloggingsflaten trenger passordvarianten før innlogging, og responsen viser bare `passord_kilde`, aldri passordet. Manglende eller utløpt sesjon skal avvises av API-et og føre til Logg inn i frontend, også ved direkte URL. Ingen stille tokenfornyelse.
- Kun fiktive data og én vaktendring om gangen. Ingen integrasjon mot reelle HR-, lønns- eller turnussystemer. Ingen turnusendring uten eksplisitt godkjenning i senere epic.
- Én avdeling med 20–30 ansatte og realistiske vakter. Turnusen har periodegrenser og tidspunkt for sist oppdatert. Visningsperioden er halvåpen, og en vakt tilhører perioden der den starter (AV-03). Historikk før perioden skal ikke vises på Vaktvalg.
- Faste vakttider er dag 07–15, mellom 10–18, kveld 15–23 og natt 23–07 (AV-02). Historikken skal dekke minst 672 faktiske timer før periodestart, med ulike turnusprofiler (AV-09). Testscenarioene omfatter manglende bemanning med gyldige kandidater, ingen gyldige kandidater, overtid og ulik ulempebelastning.
- Kjørbarhet dokumenteres med eksakte installasjons-, kjøre- og testkommandoer. KI-bruk, korrigeringer og faktisk kvalitetssikring skal kunne spores til story, tester og KI-logg. Plattformuavhengig kode; fysisk test på Windows, bash-kommandoer kontrolleres i Git Bash (OP-05). Ren klone er fortsatt et åpent oppfølgingspunkt, ikke en utført kontroll.

## Technical Decisions

- Lett heksagonal arkitektur: domenet importerer aldri adaptere; API-oppstarten komponerer lagring, domene og KI. React snakker bare HTTP med FastAPI. SQLAlchemy/SQLite-lagringen eier skjema og passordhashing. Ingen migreringsløsning er valgt.
- Sesjonen er ett JWT i `HttpOnly`-cookie, aldri `localStorage`. Vite-proxy videresender `/api` til backend med samme opphav; `SameSite=Strict`, ingen CORS (OP-10). Utlogging fjerner cookien.
- PyJWT 2.15.1 med HS256 og `hashlib.scrypt` med tilfeldig salt er valgt. Signeringsnøkkelen lages tilfeldig ved hver oppstart og holdes bare i minnet, så omstart logger alle ut. Dette er vedtatt i OP-10; epics har fortsatt en eldre NFR-formulering om nøkkel fra miljøet.
- `TURNUSHJELPEREN_JWT_MINUTTER` er et positivt heltall, standard 480; ugyldig verdi stopper oppstart. Testbrukerens passord kommer fra `TURNUSHJELPEREN_PASSORD`, eller lages tilfeldig og skrives ut av testdatakommandoen. Personlig passord er varianten ved innlevering. Nye variabler dokumenteres uten verdier i `.env.example`; backend leser bare miljøet. Les aldri `.env`.
- Alle faktiske API-feil følger `{ "kode": string, "melding": string }`. Frontend velger norsk tekst fra egen tekstliste ut fra `kode`, og viser aldri backendens `melding` direkte. Eksakte nye feilkoder og responsskjemaer bestemmes i storyene.
- Vakter bruker tidssonen `Europe/Oslo`, med sommertid, og ISO 8601 i API-et. KI skal aldri beregne harde regler, arbeidstid, kostnad eller rangering.

## UX & Interaction Patterns

- Tett, nøkternt fagsystem med navy/grå palett, systemfont og flate paneler med kantlinjer. Bruk DESIGN-tokenene for alle størrelser og farger. Skriftstørrelser i `rem`; spacing, kanter, radius og faste mål i `px`. Tekst skal vokse ved 20px standardskrift uten å klippes (AV-13).
- Appbar over hele bredden; innhold sentrert med maksimal bredde 1180px. Ingen vannrett siderulling ned til 360px. Brede tabeller ruller i egen beholder inntil senere mobiltilpasning (AV-14).
- Appbar viser produktnavn og «Ikke innlogget», eller innlogget navn, rolle og avdeling. Brødsmulesti under appbaren forankrer den lineære flyten. Ingen sidemeny eller faner.
- Logg inn bruker et sentrert kort på opptil 360px med brukernavn, passord og rollenotat. Feil innlogging vises inline. Tab og enter skal fungere for felt og handlinger.
- Vaktvalg viser manglende bemanning øverst som varselbokser med primærhandlingen «Velg vakt — finn erstatter →». Bemannede vakter vises i tabell under, med nøytral status, aldri grønn suksessfarge. Ingen tom varselboks når ingen vakter krever handling. Fotnote viser siste oppdatering og antall ansatte.
- Kandidatflaten har egen URL og viser vaktens tidspunkt og kompetansekrav. Ukjent eller allerede bemannet vakt gir nøytral melding. Inntil Epic 2 vises en tydelig plassholder uten falske kandidater.
- All brukertekst er kort, nøktern norsk bokmål fra tekstlisten. Semantisk HTML, tilstrekkelig kontrast og vanlig tastaturnavigasjon; utvidet skjermleserstøtte er utenfor v1.

## Cross-Story Dependencies

- Prosjektoppsett og testdata er grunnlaget for innlogging. Innlogging, designtokens og appskall fra 1.3 brukes videre i 1.4–1.6.
- Tilgangskontrollen i 1.4 skal være på plass før vaktoversikt og vaktdetaljer eksponeres i 1.5–1.6.
- Vaktvalget leder til kandidatflaten som Epic 2 fyller. Epic 3 skal senere vise bekreftelse på Vaktvalg og flytte godkjent vakt fra «Krever handling» til bemannet.
