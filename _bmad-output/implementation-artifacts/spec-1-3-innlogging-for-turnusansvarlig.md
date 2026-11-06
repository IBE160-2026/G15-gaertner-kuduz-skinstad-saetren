---
title: 'Story 1.3: Innlogging for turnusansvarlig'
type: 'feature'
created: '2026-11-06'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen er åpen for alle og har verken bruker, sesjon, designtokens eller appskall. Story 1.4–1.6 og senere epics bygger på alle fire (FR13).

**Approach:** Turnusansvarlig Kari Vestby opprettes av testdatakommandoen med passordhash i en ny tabell `bruker`, med et personlig eller et tilfeldig testpassord. `POST /api/innlogging` setter ett JWT i en `httpOnly`-cookie, `GET /api/meg` sier hvem som er innlogget, og `GET /api/innloggingsinfo` sier hvilken passordvariant som gjelder. Frontend får designtokens, appbar, innloggingsflate og en foreløpig startside.

## Boundaries & Constraints

**Always:**
- Hashing og brukeroppslag bare i `adaptere/lagring`, JWT bare i `adaptere/api` (AD-3). `domene/` røres ikke.
- Alle feil svarer `{ "kode", "melding" }` (AD-4): valideringsfeil, 404 og 405 fra rutingen og uventede unntak. `melding` er en fast tekst per kode og gjentar aldri det som ble sendt inn. Frontend viser tekst fra egen tekstliste etter `kode`, aldri `melding`, og har en reservetekst for ukjent kode og for manglende kontakt med API-et.
- Passord og utløpstid leses fra miljøet, aldri fra kildekoden eller `.env` (NFR7). En tom verdi regnes som manglende, slik databasestien gjør i dag. JWT-nøkkelen finnes bare i minnet. Nye variabler står uten verdi i `.env.example`.
- Tokens etter AV-13: skrift i `rem` med px i kommentar, resten i `px`. Alle størrelser og farger i komponentene og `app.css` kommer fra tokens, også 360px, 1px-kanter, fokusrammen og 16px-margen i `min(...)`. Mål og farger i mockupen som ikke finnes i DESIGN.md, erstattes med nærmeste token. Appbarteksten er hvit (UX-DR2). Ingen fast høyde på tekstbeholdere. Bredde etter AV-14.
- Feil brukernavn og feil passord gir samme svar og omtrent samme svartid.
- Skjemafeltene har `<label for>`, `autocomplete="username"` og `"current-password"`, `type="password"` og synlig fokusramme.

**Never:** utlogging, vern av andre endepunkter og omdirigering ved direkte URL (story 1.4), router, kontosperring, registrering, token i `localStorage` eller i svarkroppen, egenlaget JWT-kode, tester for frontend.

**Beslutninger (OP-10, 2026-11-06):**
- Cookien når API-et gjennom Vite-proxy for `/api` til `http://127.0.0.1:8000`. Samme opphav gir `SameSite=Strict` og ingen CORS.
- PyJWT 2.15.1, låst eksakt som de andre pakkene, med HS256. Passordhash med `hashlib.scrypt` fra standardbiblioteket, med tilfeldig salt per bruker.
- Tabellen `bruker`: `id`, `brukernavn` (unik), `navn`, `passord_hash`, `passord_kilde`, `turnus_id` (FK). Avdelingen hentes fra Turnus. Brukernavnet er `kari.vestby` (mockupen). `create_all` legger tabellen til i en eksisterende database, så den trenger ikke slettes.
- Utløpstiden er 480 minutter (én vakt) når `TURNUSHJELPEREN_JWT_MINUTTER` mangler. Er verdien ikke et positivt heltall, starter ikke API-et, og meldingen sier hva som er galt.
- Cookien heter `turnushjelperen_sesjon`, med `HttpOnly`, `SameSite=Strict`, `Path=/api` og `Max-Age` lik utløpstiden. Ikke `Secure`, fordi utviklingsserveren går over http.
- `GET /api/meg` gjør at en innlogget som laster siden på nytt, fortsatt er innlogget.
- (Johannes, 2026-11-06) Passordet er det turnusansvarlig skriver inn på nettsiden. Er `TURNUSHJELPEREN_PASSORD` satt, brukes det som Karis personlige passord. Det er varianten ved innlevering, og den som installerer, velger passordet selv, slik at det aldri står i repoet. Mangler variabelen, lager testdatakommandoen et tilfeldig testpassord (`secrets`). Det er varianten når gruppa tester. Utskriften sier alltid hvilken variant som gjelder: «Passord: personlig, fra TURNUSHJELPEREN_PASSORD» eller «Passord: tilfeldig testpassord, gjelder til neste kjøring: <passord>». README forklarer begge variantene steg for steg, med kommandoer som kan kopieres for PowerShell og for bash, og innleveringsvarianten først.
- (Johannes, 2026-11-06) Innloggingskortet viser varianten med en `tag` og en `meta`-linje i designsystemet: «Testpassord» med «Laget tilfeldig av testdatakommandoen og står i terminalen.», «Personlig passord» med «Valgt med TURNUSHJELPEREN_PASSORD.», eller «Ingen bruker» med «Last testdataene først, se README.» `bruker` lagrer `passord_kilde` (`tilfeldig` eller `personlig`). Det åpne `GET /api/innloggingsinfo` svarer `{passord_kilde}`, med `null` når det ikke finnes noen bruker, og viser aldri selve passordet.
- (Johannes, 2026-11-06, OP-10/#10) Planleggingsdokumentene oppdateres på samme branch etter implementeringen: story 1.3 i `epics.md`, `ARCHITECTURE-SPINE.md:108` og `:199`, OP-10 i `avklaringspunkter.md` §2.3 og §11, og `epic-1-context.md`.
- (Johannes, 2026-11-06) JWT-nøkkelen lages tilfeldig (`secrets.token_bytes(32)`) ved hver oppstart og holdes bare i minnet. Det finnes ingen miljøvariabel for den. Det avviker fra akseptansekravet i epics om at nøkkelen leses fra miljøet, fordi en fast nøkkel bare gir at sesjonen overlever en omstart, og en nøkkel som aldri skrives ned, ikke kan lekke. README sier at alle logges ut når serveren starter på nytt, også ved `--reload`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Riktig innlogging | `kari.vestby` og riktig passord | 200 `{navn, avdeling}`, cookie satt, ingen token i kroppen | N/A |
| Feil passord | Riktig brukernavn | 401 | `{kode: "feil_innlogging"}`, inline «Feil brukernavn eller passord» |
| Ukjent bruker | Annet brukernavn | Som feil passord, og passordet hashes likevel | Samme kode og tekst |
| Manglende eller feil felt | Tom JSON, manglende felt, passord som tall | 422, uten innsendte verdier i svaret | `{kode: "ugyldig_foresporsel"}` |
| Gyldig sesjon | `GET /api/meg` med cookie | 200 `{navn, avdeling}` | N/A |
| Ingen eller ugyldig sesjon | Uten cookie, utløpt, feil nøkkel, `alg: none` eller bruker som ikke finnes | 401 | `{kode: "mangler_sesjon"}` |
| Omstart av API-et | Cookie fra før omstarten | 401 | `{kode: "mangler_sesjon"}` |
| Ukjent sti eller metode | `GET /api/finnes-ikke`, `PUT /api/innlogging` | 404 eller 405 | `ikke_funnet`, `metode_ikke_tillatt` |
| Passordvariant på kortet | `GET /api/innloggingsinfo` med tilfeldig, personlig eller ingen bruker | `{passord_kilde: "tilfeldig" \| "personlig" \| null}`, og kortet viser tilhørende tag og tekst | N/A |
| Uventet feil | For eksempel `bruker` mangler fordi testdata ikke er lastet | 500 | `{kode: "intern_feil"}` |
| API-et svarer ikke | Proxyen gir 502 eller nettverksfeil | Innloggingsflaten vises med «Får ikke kontakt med serveren.» | Reservetekst i frontend |
| Gjentatt testdata | Kommandoen kjøres to ganger | Én bruker, ingen duplikat | N/A |
| Uten passordvariabel | `TURNUSHJELPEREN_PASSORD` mangler eller er tom | Utskriften viser «tilfeldig testpassord» og passordet, som virker ved innlogging. `passord_kilde` er `tilfeldig` | N/A |
| Med passordvariabel | Variabelen er satt | Utskriften viser «personlig, fra TURNUSHJELPEREN_PASSORD», uten passordet. `passord_kilde` er `personlig` | N/A |
| Ugyldig utløpstid | `TURNUSHJELPEREN_JWT_MINUTTER` er `abc`, `0` eller negativ | API-et starter ikke | Melding om at verdien må være et positivt heltall |

</frozen-after-approval>

## Code Map

- `backend/adaptere/lagring/modeller.py` -- `Base`, `TurnusRad`. `BrukerRad` legges til her.
- `backend/adaptere/lagring/database.py` -- `lag_engine`, `lag_sessionmaker`, `opprett_skjema` (`create_all`). `:22` viser mønsteret for tom variabel. Endres ikke.
- `backend/adaptere/lagring/testdata.py:814` `fyll_testdata` -- sletter `vakt`, `ansatt`, `turnus`. Må slette `bruker` først (FK). `main()` (`:857`) kjører alt i én `begin()`. Returverdien `{"turnus","ansatt","vakt"}` testes eksakt (`test_testdata.py:284–287`) og beholdes.
- `backend/tester/lagring/test_testdata.py:263` -- forventer bare tre tabeller og må få `bruker`. Testen på `:291` krever lik utskrift fra to kjøringer (`:301`) og arver `os.environ` (`:293`).
- `backend/adaptere/api/main.py` -- bare `/api/helse` og en modulvariabel `app`. Komposisjonen skjer her (AD-2).
- `backend/tester/test_helse.py` -- testmønster: `TestClient`, norske testnavn, `-> None`.
- `frontend/src/App.tsx`, `frontend/src/main.tsx`, `frontend/vite.config.ts` -- tomt skjelett uten CSS og proxy. React 19.3, TypeScript 7, ingen router og ingen testverktøy.
- `_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-innlogging.html` -- tekst og oppsett for kortet (overskrift, undertekst, rollenotat, merknad om at det ikke finnes registrering).
- `.env.example` -- toppkommentaren «Sett ekte nøkkel bare i .env» gjelder bare OpenRouter. `README.md:56–66` nevner testdata etter uvicorn. `AGENTS.md:91` sier at testdataene har tre tabeller.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/requirements.txt` -- legg til `pyjwt==2.15.1`.
- [ ] `backend/adaptere/lagring/modeller.py` -- `BrukerRad` etter beslutningen.
- [ ] `backend/adaptere/lagring/brukere.py` -- `hash_passord`, `verifiser_innlogging(session, brukernavn, passord)` og `hent_innlogget(session, bruker_id)` og `hent_passord_kilde(session)`. De to første returnerer en dataklasse `Innlogget(id, navn, avdeling)` eller `None`. Sammenlign med `hmac.compare_digest`, og hash mot en dummy også for ukjent bruker.
- [ ] `backend/adaptere/lagring/testdata.py` -- slett `bruker` i `fyll_testdata`. `legg_til_turnusansvarlig(session, passord, passord_kilde)`. `main()` velger passordvariant etter beslutningen og skriver varianten og `bruker: 1`.
- [ ] `backend/adaptere/api/sesjon.py` -- `lag_token` og `les_token` med `algorithms=["HS256"]`, les og valider utløpstiden, og sett og les cookien.
- [ ] `backend/adaptere/api/main.py` -- `lag_app(nokkel=None, minutter=None, engine=None)`. Mangler et argument, lages nøkkelen tilfeldig, minuttene leses fra miljøet, og engine fra `lag_engine()`. `app = lag_app()`. Avhengighet for databaseøkten, `POST /api/innlogging`, `GET /api/meg`, `GET /api/innloggingsinfo` og håndterere for `RequestValidationError`, `starlette.exceptions.HTTPException` og `Exception`.
- [ ] `backend/tester/api/__init__.py`, `test_innlogging.py`, `backend/tester/lagring/test_brukere.py` -- hele matrisen. Hver test bygger appen med `lag_app` mot en database i `tmp_path`, og ingen test rører `backend/turnushjelperen.db`. Testene dekker også cookieattributtene, at hashen ikke er passordet, ulikt salt, at et passord med feil type ikke står i svaret, at scrypt kjøres for ukjent bruker (teller via `monkeypatch`), at en ny nøkkel ikke godtar et token fra en annen, begge passordvariantene og at et tilfeldig passord virker ved innlogging. Underprosesstestene setter eller fjerner `TURNUSHJELPEREN_PASSORD` eksplisitt i miljøet de sender med. Oppdater `test_testdata.py` med fire tabeller og brukeren.
- [ ] `frontend/vite.config.ts` -- proxy for `/api`.
- [ ] `frontend/src/stil/tokens.css`, `frontend/src/stil/app.css` -- tokens etter DESIGN.md og AV-13, også for kantbredde, fokusramme og kortbredde. Appskall etter AV-14, `login-card`, felt og `button-primary`. Bare `tokens.css` inneholder tall med enhet.
- [ ] `frontend/src/tekster.ts`, `frontend/src/api.ts` -- tekster etter `kode` med reservetekst og «Får ikke kontakt med serveren.», og faste UI-tekster. `loggInn`, `hentMeg` og `hentInnloggingsinfo` med `credentials: "same-origin"`. Tekstene for de tre passordvariantene. Nettverksfeil og svar som ikke er JSON, blir en egen feiltype.
- [ ] `frontend/src/komponenter/Appbar.tsx`, `LoggInn.tsx`, `Startside.tsx`, `frontend/src/App.tsx`, `frontend/src/main.tsx` -- `hentMeg` ved oppstart. Ingen innloggingsflate vises før svaret er kommet. Ved feil vises innloggingsflaten med reserveteksten. `LoggInn` viser passordvarianten som `tag` og `meta` under rollenotatet. Bruk `<form>`, slik at enter sender skjemaet.
- [ ] `.env.example` -- de nye variablene som valgfrie, uten verdi. Ved hver variabel står det at backend ikke leser `.env`, og at variabelen må settes i terminalen før kommandoen kjøres.
- [ ] `README.md`, `AGENTS.md` -- nummererte steg i rekkefølge: installer, last testdata og noter passordet, start backend, og start frontend i en egen terminal. Begge passordvariantene forklares med kommandoer for PowerShell og bash, sammen med hvordan man ser hvilken variant som gjelder. README sier at alle logges ut ved omstart, og at testdataene nå har fire tabeller.
- [ ] `docs/ki-logg/2026-11-06-innlogging.md` -- KI-logg etter `2026-11-03-testdata.md`, med de manuelle testene.
- [ ] `_bmad-output/planning-artifacts/epics.md`, `_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md`, `docs/beslutninger/avklaringspunkter.md`, `_bmad-output/implementation-artifacts/epic-1-context.md` -- etter implementeringen. Story 1.3 og konteksten: tilfeldig nøkkel uten variabel, passordvariantene og at OP-10 er besvart. Arkitekturen: nøkkelen fjernes fra miljøvariablene på `:108`, og utløpstiden på `:199` er 480 minutter. Avklaringspunktene: OP-10 avklart, med svarene og avviket for nøkkelen. Commit-meldingen sier hvorfor eldre filer endres.

**Acceptance Criteria:**
- Given hele testpakken, when `pytest` kjøres med og uten `TURNUSHJELPEREN_PASSORD` satt i terminalen, then består alle testene.
- Given `npm run build`, when den kjøres, then gir den ingen typefeil.
- Given at jeg ikke er innlogget, when jeg åpner appen, then viser appbaren «TURNUSHJELPEREN» til venstre og «Ikke innlogget» til høyre, og kortet har felt for brukernavn og passord, rollenotatet og en knapp i `button-primary`.
- Given testdata lastet med og uten `TURNUSHJELPEREN_PASSORD`, when jeg åpner innloggingsflaten, then viser kortet «Personlig passord» eller «Testpassord» med forklaring i `tag` og `meta`, og aldri selve passordet.
- Given feil passord, when jeg logger inn, then står «Feil brukernavn eller passord» i skjemaet, og feltene beholder brukernavnet.
- Given at appen kjører med proxy, when Kari logger inn bare med tastaturet (tab og enter), then er fokus synlig på hvert felt, og etterpå vises «Innlogget: Kari Vestby (turnusansvarlig) · Avdeling Kirurgisk sengepost». Etter at siden er lastet på nytt, er hun fortsatt innlogget.
- Given nettleserens standard skriftstørrelse på 20px, when innloggingsflaten vises, then vokser teksten uten å klippes, mens spacing og kanter er uendret.
- Given vindusbredde 360px og 1600px, when flatene vises, then ruller ikke siden vannrett, appbaren går over hele bredden, og innholdet er høyst 1180px bredt.
- Given `grep -rnE "[0-9.]+(px|rem)|#[0-9a-fA-F]{3,6}" frontend/src/komponenter frontend/src/stil/app.css`, when den kjøres, then gir den ingen treff.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Gjennomgang av spesifikasjonen før godkjenning, 2026-11-06, én uavhengig underagent, sammenholdt med sensorveiledningen og tilbakemeldingen på produktbriefen. Johannes tok inn alle funnene.

| # | Funn | Vurdering | Rute |
|---|---|---|---|
| 1 | 404, 405 og 500 får ikke feilformen (AD-4) | medium | tatt inn |
| 2 | Valideringsfeil kan sende passordet tilbake i svaret | medium | tatt inn |
| 3 | Blank side når API-et ikke svarer | medium | tatt inn |
| 4 | Testene kan treffe den ekte databasen og arver miljøet | medium | tatt inn |
| 5 | Ugyldige verdier i miljøvariablene er ikke definert | medium | tatt inn |
| 6 | Akseptansekriteriene mangler deler av storien, etiketter og fokus | medium | tatt inn |
| 7 | README-rekkefølgen og `.env`-misforståelsen | medium | tatt inn |
| 8 | Grep-kontrollen kolliderer med AV-14, kanter og fokus | low | tatt inn |
| 9 | Linjenumre og stier i Code Map | low | tatt inn |
| 10 | Planleggingsdokumentene oppdateres ikke med svarene på OP-10 | low | tatt inn som egen oppgave etter implementeringen (valg A). Vurderingsmatrisen finnes ikke i repoet og er ikke med. |
| 11 | Ingen test for hashing ved ukjent bruker eller token for slettet bruker | low | tatt inn |

Produktbrief-tilbakemeldingen: bare punktet om at avansert autentisering er et stretch goal er relevant, og det følges i Never-lista.

## Design Notes

API-et kaller `verifiser_innlogging` og sender passordet videre bare dit. Det lagrer aldri en hash selv (AD-3). Hashformat: `scrypt$<n>$<r>$<p>$<salt-hex>$<hash-hex>` med n=2**14, r=8 og p=1, slik at parametrene kan endres senere uten å ugyldiggjøre gamle hasher. JWT-innholdet er `sub` (bruker-ID som streng), `iat` og `exp`, ingen navn. Navnet hentes fra databasen i `/api/meg`, slik at tokenet ikke bærer data som kan bli utdatert.

Feilkoder: `feil_innlogging` (401), `mangler_sesjon` (401), `ugyldig_foresporsel` (422), `ikke_funnet` (404), `metode_ikke_tillatt` (405), `intern_feil` (500). Andre statuskoder fra rutingen får `ukjent_feil`.

## Verification

**Commands:**
- `.venv\Scripts\python -m pip install -r requirements-dev.txt` (fra `backend/`) -- expected: PyJWT installeres.
- `.venv\Scripts\python -m pytest` -- expected: alle tester består.
- `.venv\Scripts\python -m adaptere.lagring.testdata` to ganger mot den eksisterende databasen -- expected: `bruker: 1` begge gangene og tabellen `bruker` lagt til.
- `npm run build` (fra `frontend/`) -- expected: ingen feil.

**Manual checks:**
- Logg inn i nettleseren med riktig og feil passord, bare med tastaturet. Last siden på nytt, og start backend på nytt.
- Stopp backend og last siden: innloggingsflaten vises med «Får ikke kontakt med serveren.».
- Sett standard skriftstørrelse til 20px, og prøv vindusbreddene 360px og 1600px. Resultatene føres i KI-loggen.
