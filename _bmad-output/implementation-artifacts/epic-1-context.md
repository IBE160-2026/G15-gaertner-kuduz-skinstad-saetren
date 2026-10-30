# Epic 1 Context: Innlogging og vaktoversikt

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Turnusansvarlig logger inn med brukernavn og passord, ser avdelingens vakter i perioden med vakter som mangler bemanning flagget øverst under «Krever handling», og kan velge vakten som skal bemannes på nytt. Da vises vaktens tidspunkt og kompetansekrav. Epicet legger grunnmuren resten bygger på: prosjektskjelett som kjører fra en ren klone (story 1.1, ferdig), fiktive testdata som dekker scenarioene senere epics trenger, sesjon og tilgangskontroll, designtokens, appbar og brødsmulesti. Kandidatfiltrering, rangering og godkjenning kommer i senere epics. Kandidatflaten får her bare en tydelig plassholder.

## Stories

- Story 1.1: Prosjektoppsett som kjører fra en ren klone (ferdig)
- Story 1.2: Fiktiv turnus med ansatte og vakter
- Story 1.3: Innlogging for turnusansvarlig
- Story 1.4: Beskyttede flater og utløpt sesjon
- Story 1.5: Vaktoversikt med «Krever handling»
- Story 1.6: Velge vakten som skal bemannes

## Requirements & Constraints

- **Én rolle:** bare turnusansvarlig logger inn. Ingen registrering, passordgjenoppretting, SSO, flere roller eller kontosperring.
- **Tilgangskontroll:** alt utenom innlogging og helsesjekk krever gyldig sesjon, både i API-et (avvisning med feilformen) og i frontend (omdirigering til Logg inn, også ved direkte URL).
- **Hemmeligheter:** passordet til testbrukeren, JWT-signeringsnøkkelen og JWT-utløpstiden leses fra miljøvariabler. Hver ny variabel dokumenteres uten verdi i `.env.example`. Les aldri `.env`. Utløpstiden er ikke fastsatt, så den får en dokumentert standardverdi.
- **Bare fiktive data:** ingen ekte personopplysninger og ingen integrasjon mot reelle systemer.
- **Testdata (en fiktiv Turnus):** én avdeling (Kirurgisk sengepost, uke 39–40 2026) med 20–30 Ansatte og Vakter. Kommandoen er dokumentert og idempotent, så den ikke lager duplikater. Turnusen har et tidspunkt for sist oppdatert. Dataene må dekke disse scenarioene:
  - Vakt #4127 (dagvakt, søn. 27.09.2026 07:00–15:00) mangler bemanning og har gyldige kandidater. Silje Amundsen meldte fra sykemeldt kl. 06:14.
  - Vakt #4189 (nattevakt) mangler bemanning, og alle Ansatte blir utelukket av de harde reglene.
  - Minst én gyldig Kandidat har så mange timer denne uken at vakten gir overtid (over 36 t/uke).
  - Billigste Kandidat er ikke øverst i rangeringen. Det finnes tekstbaserte preferanser og kjente utelukkelser per hard regel.
  - Perioden dekker hele kalenderuker, fordi 35-timersregelen sjekkes per uke.
- **Felter:** en Vakt har vaktnummer, vakttype (dag/kveld/natt), start og slutt, kompetansekrav og enten en tildelt Ansatt eller markeringen «mangler bemanning». Mangler vakten bemanning, lagres også hvem som var satt opp og når det ble meldt fra. En Ansatt har fiktivt navn, stilling, ansiennitet i år, Kompetansenivå per vakttype, individuell timelønn (ordinær sats) og eventuelt en forhåndsdefinert tekstbasert preferanse. Timelønnen eies av story 1.2, fordi det ikke er valgt migreringsverktøy. Story 4.3 legger ikke til egne satsfelt, og overtidssatsen regnes ut og lagres ikke.
- **Kvalitetssikring:** pytest på backend. KI-generert kode logges i `docs/ki-logg/<dato>-<tema>.md` med oppgave, prompt, leveranse, rettelser og kvalitetssikring.

## Technical Decisions

- **Heksagonal struktur:** `domene/` importerer aldri fra `adaptere/*`. API-et ligger i `adaptere/api` (FastAPI), lagringen i `adaptere/lagring` (SQLAlchemy/SQLite) og frontend i `frontend/src`, som bare snakker HTTP med API-et. Komposisjon og avhengighetsinjeksjon skjer i oppstartslaget til `adaptere/api`.
- **Skjemaeierskap:** `adaptere/lagring` eier SQLAlchemy-modellene og skjemaet alene. Domenet kjenner bare egne Python- og Pydantic-typer, og konverteringen skjer i lagringsadapteren. Story 1.2 oppretter bare tabellene Turnus, Vakt og Ansatt. Brukertabellen kommer med innloggingen. Primærnøkler tildeles av lagringen, og ID-formatet er ikke fastsatt. Ingen kodevei utenom den framtidige skrivefunksjonen for Godkjenning (Epic 3) skal kunne markere en vakt som bemannet.
- **Tid:** alle vakttidspunkt lagres og beregnes i `Europe/Oslo` med sommertid, aldri med fast UTC-offset. API-et bruker ISO 8601.
- **Sesjon:** vellykket innlogging gir ett JWT i en `httpOnly`-cookie, aldri i `localStorage`, og det sendes automatisk på senere kall. Tokenet fornyes ikke stille: når det utløper, må brukeren logge inn på nytt. Utlogging fjerner cookien. Passordhashing skjer bare i `adaptere/lagring`, og API-et lagrer aldri en hash selv.
- **Feilform:** alle faktiske feil svarer med `{ "kode": string, "melding": string }`. `melding` vises aldri i UI. Frontend slår opp `kode` i en egen norsk tekstliste. Eksakte feilkoder er ikke fastsatt. Dette gjelder feil innlogging, manglende eller utløpt sesjon, ukjent vakt-ID og vakt som ikke mangler bemanning.
- **Frontend:** designtokens (farger, typografiroller, spacing 4/8/12/16/22/32, radius sm 3px/4px/full) implementeres som CSS-variabler etter DESIGN.md. Systemfonten er `Segoe UI, Arial, sans-serif`. Ingen skygger (bare 1px kantlinjer), ingen gradienter og ingen farger utenfor paletten.
- **Utsatt:** migreringsverktøy, SQLAlchemy-versjon, ID-format og JWT-utløpstid. Velg enkelt og dokumenter valget, men ikke bygg mer enn storien trenger.

## UX & Interaction Patterns

- **Appbar** på alle flater: bakgrunn `bg-header`, «TURNUSHJELPEREN» til venstre og «Ikke innlogget» eller «Innlogget: <navn> (turnusansvarlig) · Avdeling <avdeling>» til høyre. Innholdet endres bare ved inn- og utlogging.
- **Logg inn:** sentrert kort på 360px på tom `bg-app`, med felt for brukernavn og passord og et rollenotat om at bare turnusansvarlig har tilgang. Feil innlogging gir inline «Feil brukernavn eller passord». Referanse: `mockups/key-innlogging.html`.
- **Brødsmulesti** fast under appbaren etter innlogging, for eksempel `Turnus > Kirurgisk sengepost > Uke 39–40, 2026` på Vaktvalg og `Turnus > Kirurgisk sengepost > Vakt #4127 — Dagvakt 27.09.2026` på kandidatflaten. Det finnes ingen sidemeny eller faner, og flyten er lineær.
- **Vaktvalg** (referanse `mockups/key-vaktvalg.html`, spine-dokumentene vinner ved konflikt):
  - «Krever handling» ligger øverst. Hver vakt står i en varselboks med 4px venstrekant i `danger` og et sirkulært «!»-ikon. Overskriften er «Vakt #<nr> — <vakttype>, <avdeling>». Linjen under viser dato · tidsrom (varighet) · «Mangler bemanning» i fet `danger` og hvem som meldte fra og når. Primærknappen «Velg vakt — finn erstatter →» er eneste vei videre.
  - Under står «Øvrige vakter denne perioden — bemannet» som tabell med kolonnene Vakt (#nr i `accent`, fet), Dato, Tid (vakttype som undertekst), Ansatt (stilling og ansiennitet som `meta`) og Status. `row-alt` brukes på annenhver rad. «Bemannet» er en nøytral tag, ikke grønn, fordi `ok` er reservert for ordinær sats. «Se detaljer»-lenken fra mockupen er ikke med.
  - Fotnote nederst til høyre, for eksempel «Turnus oppdatert 27.09.2026 06:20 · 25 ansatte totalt i avdelingen».
  - Krever ingen vakter handling, vises aldri en tom «!»-boks. Enten skjules seksjonen, eller den viser «Ingen vakter krever handling nå».
- **Kandidatflaten** har egen URL (`/vakt/<nr>/kandidater`) og viser vaktens start, slutt og kompetansekrav. Plassen for kandidater er tydelig, men den viser ingen falske data. Bemannede vakter har ingen «Velg vakt»-knapp.
- **Knapper:** `button-primary` (fylt `accent`, hvit tekst) for hovedhandlingen og `button-secondary` for avbryt.
- **Tilgjengelighet:** semantisk HTML og tilstrekkelig kontrast. Alle felt og knapper kan nås med tab og aktiveres med enter.
- **Tone:** all brukertekst ligger i den norske tekstlisten og er kort, presis og nøktern, uten utropstegn eller formaning («Mangler bemanning», ikke «FEIL»). Grensesnittet er bare på norsk bokmål, uten i18n.

## Cross-Story Dependencies

- Story 1.1 (ferdig) gir skjelettet og kommandoene i AGENTS.md. Nye kommandoer, som testdatakommandoen, føres inn der.
- Story 1.2 er grunnlaget for 1.3 (testdatakommandoen oppretter brukeren for turnusansvarlig), 1.5 og 1.6. Den er også grunnlaget for Epic 2 (harde regler og #4189), Epic 4 (timelønn og overtidsscenario) og Epic 5 (forhåndsdefinerte preferansetekster og demo-avveininger for #4127).
- Story 1.3 må komme før 1.4. Story 1.4 må være på plass før API-endepunktene for vaktoversikt og vaktdetaljer i 1.5 og 1.6 eksponeres.
- Story 1.6 fører til kandidatflaten, som Epic 2 fyller med gyldige kandidater. Vaktvalg må senere kunne vise bekreftelsen etter godkjenning og fjerne vakten fra «Krever handling» (Epic 3).
- Demo-modus (Epic 5) legger senere en nøytral «Demo-modus»-tag i appbaren, så appbaren bør ha plass til den.
