# Epic 1 Context: Innlogging og vaktoversikt

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Turnusansvarlig logger inn med brukernavn og passord, ser avdelingens vakter i perioden med vakter som mangler bemanning flagget øverst under «Krever handling», og kan velge vakten som skal bemannes på nytt. Da vises vaktens tidspunkt og kompetansekrav. Epicet legger grunnmuren resten bygger på. Skjelettet (1.1) og de fiktive testdataene med historikk og fasit (1.2) er ferdige. Det som gjenstår, er sesjon og tilgangskontroll, designtokens, appskall med appbar og brødsmulesti, vaktoversikten og vaktvalget. Kandidatfiltrering, rangering og godkjenning kommer i senere epics. Kandidatflaten får her bare en tydelig plassholder.

## Stories

- Story 1.1: Prosjektoppsett som kjører fra en ren klone (ferdig)
- Story 1.2: Fiktiv turnus med ansatte og vakter (ferdig)
- Story 1.3: Innlogging for turnusansvarlig
- Story 1.4: Beskyttede flater og utløpt sesjon
- Story 1.5: Vaktoversikt med «Krever handling»
- Story 1.6: Velge vakten som skal bemannes

## Requirements & Constraints

- **Én rolle:** bare turnusansvarlig logger inn. Ingen registrering, passordgjenoppretting, SSO, flere roller eller kontosperring.
- **Tilgangskontroll:** alt utenom innlogging og helsesjekk krever gyldig sesjon, både i API-et (avvisning med feilformen) og i frontend (omdirigering til Logg inn, også ved direkte URL og når sesjonen har utløpt).
- **Hemmeligheter:** passordet til testbrukeren, JWT-signeringsnøkkelen og JWT-utløpstiden leses fra miljøvariabler. Hver ny variabel dokumenteres uten verdi i `.env.example`. Les aldri `.env`. Utløpstiden er ikke fastsatt og får en dokumentert standardverdi. Merk at backend i dag ikke leser `.env` selv, bare miljøet.
- **Testbruker:** brukerkontoen for turnusansvarlig opprettes av den eksisterende testdatakommandoen. Passordet lagres bare som hash.
- **Bare fiktive data:** ingen ekte personopplysninger og ingen integrasjon mot reelle systemer.
- **Testdataene som vises (fra 1.2):** én Turnus for Kirurgisk sengepost, uke 39–40 2026, med periodestart, periodeslutt og tidspunkt for sist oppdatert. Fire vakttyper med faste tider: dag 07–15, mellom 10–18, kveld 15–23 og natt 23–07 (AV-02). Vakt #4127 (dagvakt søn. 27.09.2026) og #4189 (nattevakt) mangler bemanning. For slike vakter er det lagret hvem som var satt opp og når det ble meldt fra.
- **Visningsperiode:** en vakt hører til perioden som inneholder starttidspunktet. Perioden er halvåpen, `[fra, til)` (AV-03). Vakthistorikken før periodestart finnes i databasen, men skal aldri vises på Vaktvalg.
- **Kvalitetssikring:** pytest på backend. KI-generert kode logges i `docs/ki-logg/<dato>-<tema>.md`. Manuell test av skriftstørrelse dokumenteres i storyen som innfører tokenene (se UX).

## Technical Decisions

- **Heksagonal struktur:** `domene/` importerer aldri fra `adaptere/*`. API-et ligger i `adaptere/api`, lagringen i `adaptere/lagring` og frontend i `frontend/src`, som bare snakker HTTP med API-et. Komposisjon skjer i oppstartslaget til `adaptere/api`.
- **Skjemaeierskap:** `adaptere/lagring` eier SQLAlchemy-modellene og skjemaet alene. Konverteringen til domenetyper skjer der. Brukertabellen er ny i 1.3. Det finnes ikke noe migreringsverktøy, så et nytt skjema betyr at databasen slettes og testdataene lastes på nytt. Ingen kodevei utenom den framtidige skrivefunksjonen for Godkjenning (Epic 3) skal kunne markere en vakt som bemannet.
- **Tid:** alle vakttidspunkt lagres og beregnes i `Europe/Oslo` med sommertid, aldri med fast UTC-offset. API-et bruker ISO 8601.
- **Sesjon:** vellykket innlogging gir ett JWT i en `httpOnly`-cookie, aldri i `localStorage`, og det sendes automatisk på senere kall. Tokenet fornyes ikke stille. Utlogging fjerner cookien. Passordhashing skjer bare i `adaptere/lagring`.
- **Feilform:** alle faktiske feil svarer med `{ "kode": string, "melding": string }`. `melding` vises aldri i UI. Frontend slår opp `kode` i en egen norsk tekstliste. Eksakte koder er ikke fastsatt. Det gjelder feil innlogging, manglende eller utløpt sesjon, ukjent vakt-ID og vakt som ikke mangler bemanning.
- **Avklares i spesifikasjonen for 1.3 (OP-10), ikke vedtatt:**
  1. Hvordan cookien når API-et: Vite-proxy for `/api` eller CORS med credentials.
  2. Hvordan sensor får en testbruker fra en ren klone, og hva som skjer når passord- eller nøkkelvariabelen mangler.
  3. Bibliotek for JWT og passordhashing. Gruppa har ikke avgjort om versjoner skal låses eksakt.
  4. Hvordan brukertabellen ser ut i skjemaet.
- **Utsatt:** JWT-utløpstid, ID-format og migreringsverktøy. Velg enkelt, dokumenter valget og bygg ikke mer enn storien trenger.

## UX & Interaction Patterns

- **Designtokens (innføres i 1.3):** farger, typografiroller, spacing (4/8/12/16/22/32, `content-padding` 22px, `row-padding` 9px 12px) og radius (sm 3px, standard 4px, full) blir CSS-variabler etter DESIGN.md. Systemfonten er `Segoe UI, Arial, sans-serif`. Ingen skygger (bare 1px kantlinjer), ingen gradienter og ingen farger utenfor paletten.
- **Enheter (AV-13):** skriftstørrelser skrives i `rem` (1rem = 16px), med px-verdien fra DESIGN.md i en kommentar, for eksempel `--font-body: 0.78125rem; /* 12.5px */`. Spacing, kantlinjer, radius, sporing og faste bredder skrives i `px`. Komponentene bruker ingen rå størrelser. Faste mål som 360px (`login-card`) og 110×7px (belastningslinja) blir egne tokens. Tekstbeholdere har ikke fast høyde. Kontroll: når nettleserens standard skriftstørrelse settes til 20px, vokser teksten uten å klippes, mens spacing og kanter er uendret.
- **Layoutbredde (AV-14):** appbaren går over hele bredden. Innholdet får `max-width: 1180px`, `margin-inline: auto` og `padding-inline` lik `content-padding`. Siden ruller ikke vannrett ned til 360px bredde. Brede tabeller ruller vannrett i sin egen beholder fram til story 4.6. Breakpoints og stabling er fortsatt utsatt.
- **Appbar** på alle flater: bakgrunn `bg-header` og hvit tekst, «TURNUSHJELPEREN» i `brand` til venstre og «Ikke innlogget» eller «Innlogget: <navn> (turnusansvarlig) · Avdeling <avdeling>» til høyre. Innholdet endres bare ved inn- og utlogging. Appbaren må ha plass til en nøytral «Demo-modus»-tag til venstre for brukeren (Epic 5).
- **Logg inn:** sentrert `login-card` med `width: min(360px, 100% - 32px)` på tom `bg-app`, med felt for brukernavn og passord og et rollenotat om at bare turnusansvarlig har tilgang. Feil innlogging gir inline «Feil brukernavn eller passord». Referanse: `mockups/key-innlogging.html`.
- **Brødsmulesti** fast under appbaren etter innlogging: `Turnus > Kirurgisk sengepost > Uke 39–40, 2026` på Vaktvalg og `Turnus > Kirurgisk sengepost > Vakt #4127 — Dagvakt 27.09.2026` på kandidatflaten. Ingen sidemeny eller faner. Flyten er lineær.
- **Vaktvalg** (referanse `mockups/key-vaktvalg.html`, spine-dokumentene vinner ved konflikt):
  - «Krever handling» øverst. Hver vakt står i en `alert-box` med 4px venstrekant i `danger` og et sirkulært «!»-ikon. Overskriften er «Vakt #<nr> — <vakttype>, <avdeling>». Linjen under viser dato · tidsrom (varighet) · «Mangler bemanning» i fet `danger` og hvem som meldte fra og når. Primærknappen «Velg vakt — finn erstatter →» er eneste vei videre.
  - Under står «Øvrige vakter denne perioden — bemannet» som tabell med kolonnene Vakt (#nr i `accent`, fet), Dato, Tid (vakttype som undertekst), Ansatt (stilling og ansiennitet som `meta`) og Status. `row-alt` på annenhver rad. «Bemannet» er en nøytral tag, ikke grønn, fordi `ok` er reservert for ordinær sats. Mockupens «Se detaljer»-lenke er ikke med.
  - Fotnote nederst til høyre: når Turnusen sist ble oppdatert og antall ansatte i avdelingen.
  - Krever ingen vakter handling, vises aldri en tom «!»-boks. Seksjonen skjules, eller den viser «Ingen vakter krever handling nå».
- **Kandidatflaten** har egen URL (`/vakt/<nr>/kandidater`) og viser vaktens start, slutt og kompetansekrav. Plassen for kandidater er tydelig, men viser ingen falske data. Ukjent vakt eller vakt som ikke mangler bemanning gir en nøytral melding fra tekstlisten.
- **Knapper:** `button-primary` (fylt `accent`, hvit tekst) for hovedhandlingen og `button-secondary` for avbryt. Ingen andre varianter.
- **Tilgjengelighet:** semantisk HTML og tilstrekkelig kontrast. Alle felt og knapper kan nås med tab og aktiveres med enter. Skjermleserstøtte er utenfor v1.
- **Tone:** all brukertekst ligger i den norske tekstlisten og er kort, presis og nøktern, uten utropstegn eller formaning («Mangler bemanning», ikke «FEIL»). Bare norsk bokmål, uten i18n.

## Cross-Story Dependencies

- 1.1 og 1.2 er ferdige. Nye kommandoer og miljøvariabler føres inn i AGENTS.md og `.env.example`.
- 1.3 utvider testdatakommandoen fra 1.2 med brukeren for turnusansvarlig, og legger til designtokens og appskall som 1.4–1.6 og senere epics bygger på.
- 1.3 må komme før 1.4. 1.4 må være på plass før endepunktene for vaktoversikt og vaktdetaljer i 1.5 og 1.6 eksponeres.
- 1.6 fører til kandidatflaten, som Epic 2 fyller med gyldige kandidater. Domenedelen av story 2.1 kan startes parallelt på testdataene fra 1.2 (anbefalt, ikke tildelt). Vaktvalg må senere kunne vise bekreftelsen etter godkjenning og fjerne vakten fra «Krever handling» (Epic 3).
