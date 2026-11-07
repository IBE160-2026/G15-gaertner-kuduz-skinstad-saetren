# Story 1.3: Innlogging for turnusansvarlig

Dato: spesifikasjonen 2026-11-06, implementeringen 2026-11-07. Branch:
`story-1.3-innlogging`. Agent: Claude Code (Claude Opus 5.5), som underagent i
`bmad-build` (OP-04).

Dette er agentens egenrapportering. Et gruppemedlem må lese den gjennom og korrigere.
Gjennomgangen fra underagentene som ikke har sett implementeringen, og rettelsene etter
den, føres inn av orkestratoren under «Hva som ble rettet, og hvorfor».

## Oppgaven

Implementere spesifikasjonen
`_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md`:
tabellen `bruker` med Kari Vestby, passordhash i `adaptere/lagring`, ett JWT i en
`httpOnly`-cookie fra `adaptere/api`, endepunktene `POST /api/innlogging`, `GET /api/meg`
og `GET /api/innloggingsinfo`, feilformen fra AD-4 for alle feil, og i frontend
designtokens (AV-13, AV-14), appbar, innloggingsflate og en foreløpig startside. OP-10
er besvart i spesifikasjonen.

## Prompten

Prompten fra orkestratoren i `bmad-build` til underagenten, ordrett:

> Read C:\Users\johan\Documents\Studier\IBE160 Programmering med KI\turnushjelperen\_bmad-output\implementation-artifacts\spec-1-3-innlogging-for-turnusansvarlig.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start.
>
> When done, report what you changed, how you verified it, and anything left incomplete or risky.

Johannes' instruksjon til orkestratoren (Claude Code, Claude Opus 5.5) 2026-11-07,
ordrett: `/bmad-build`. Orkestratoren fant én aktiv spesifikasjon (`ready-for-dev`) og
spurte om den skulle fortsette. Johannes svarte: «1. iverksett». Spesifikasjonen var
godkjent av Johannes 2026-11-06 (commit `d758a4a`).

De tre gjennomgangsagentene fikk promptene fra `bmad-build` steg 4 uten endringer og
bare diffen fra `daac9ca`. Edge Case Hunter fikk i tillegg spesifikasjonen. Rettelsene
ble sendt tilbake til implementeringsagenten med malen fra samme steg.

## Hva modellen leverte

Backend:

- `backend/requirements.txt`: `pyjwt==2.15.1`.
- `backend/adaptere/lagring/modeller.py`: `BrukerRad` med CHECK-regel for
  `passord_kilde` (`tilfeldig` eller `personlig`) og unikt `brukernavn`.
- `backend/adaptere/lagring/brukere.py`: `hash_passord` (scrypt, n=2^14, r=8, p=1,
  16 byte salt, formatet `scrypt$n$r$p$salt$hash`), `verifiser_innlogging`,
  `hent_innlogget` og `hent_passord_kilde`. Ukjent bruker sjekkes mot en dummy-hash som
  lages ved import, så feil brukernavn koster like mye som feil passord.
  Sammenligningen bruker `hmac.compare_digest`.
- `backend/adaptere/lagring/testdata.py`: `fyll_testdata` tømmer `bruker` først.
  `legg_til_turnusansvarlig` og `velg_passord` er nye. `main()` skriver `bruker: 1`,
  brukernavnet og hvilken passordvariant som gjelder.
- `backend/adaptere/api/sesjon.py`: `les_minutter` (standard 480, ellers bare sifre og
  over 0, ellers `UgyldigUtlopstid`), `lag_token`, `les_token` (bare HS256, krever
  `sub`, `iat` og `exp`), `sett_cookie` og `les_cookie`.
- `backend/adaptere/api/main.py`: `lag_app(nokkel, minutter, engine)` og `app = lag_app()`.
  Håndterere for `RequestValidationError` (422 uten detaljer, så passordet ikke sendes
  tilbake), `starlette.exceptions.HTTPException` (404, 405, ellers `ukjent_feil`) og
  `Exception` (500). API-et oppretter ikke skjemaet selv, så en database uten testdata
  gir `intern_feil`, slik matrisen sier.
- Tester: `tester/api/test_innlogging.py` (52 tester, 56 etter rettelsene),
  `tester/lagring/test_brukere.py` (16) og fire nye i `tester/lagring/test_testdata.py`.
  Totalt 107, 111 etter rettelsene.

Frontend:

- `frontend/vite.config.ts`: proxy for `/api` til `http://127.0.0.1:8000`.
- `frontend/src/stil/tokens.css`: alle farger og størrelser. Skrift i `rem` med px i
  kommentar, resten i `px`. Egne tokens for kantbredde, fokusramme, 1180px, 360px og
  16px-margen.
- `frontend/src/stil/app.css`: appskall, `login-card`, felt, `button-primary`, `tag`,
  `meta` og `panel`. Bare `var(...)`, ingen tall med enhet og ingen fargekoder.
- `frontend/src/tekster.ts` og `frontend/src/api.ts`: tekster etter `kode` med
  reservetekst, `IngenKontaktFeil` for nettverksfeil og svar som ikke er JSON.
- `frontend/src/komponenter/Appbar.tsx`, `LoggInn.tsx`, `Startside.tsx`, `App.tsx`,
  `main.tsx`.

Dokumentasjon: `.env.example`, `README.md`, `AGENTS.md` og, etter implementeringen,
`epics.md`, `ARCHITECTURE-SPINE.md`, `avklaringspunkter.md` (OP-10) og
`epic-1-context.md`.

## Valg agenten tok

Spesifikasjonen avgjør ikke disse:

- **Nærmeste token for mockupens mål.** Overskriften (16px) bruker `heading` (15px),
  feltetikettene (11px, versaler) bruker `column-header` (10,5px, versaler, 0,4px
  sporing), feltene og knappen (13px) bruker `body`, rollenotatet (11,5px) `body` og
  merknaden om registrering (10,5px) `meta`. Kortets polstring 28/30/24px ble
  32/32/22px. Feltpolstringen 9px 11px ble `row-padding` (9px 12px). Tagg-polstringen
  1px 7px ble 0 8px.
- **Feilteksten i skjemaet er fet `text-main`, ikke `danger`.** DESIGN.md reserverer
  `danger` for utelukkelser og mangel, og sier at den ikke skal brukes som generell
  obs-farge.
- **Etter feil innlogging** tømmes passordfeltet og fokus flyttes dit. Brukernavnet
  beholdes.
- **`login-card` ligger utenfor `.innhold`**, så `100%` i `min(360px, 100% - 32px)`
  er hele bredden og ikke bredden minus 44px polstring. Ved 360px er kortet 328px.
- **Appbaren bryter linjen** på smale skjermer, slik at «Innlogget: …» ikke gir
  vannrett rulling.
- **Mens `/api/meg` venter**, er høyre side av appbaren tom, så verken «Ikke innlogget»
  eller innloggingsflaten blinker forbi for en som er innlogget.
- **`intern_feil` i frontend** sier «Feil på serveren. Er testdataene lastet? Se
  README.», fordi den vanligste årsaken er en database uten tabellen `bruker`.
- **Lengdegrenser** på 50 tegn for brukernavn (som kolonnen i `bruker`) og 256 for passord, så ingen kan be
  serveren hashe vilkårlig store tekster. For lange verdier gir 422.
- **Testpassordet** er `secrets.token_urlsafe(9)`, 12 tegn.
- **README** viser hvordan passordet skrives inn uten at det vises eller havner i
  historikken (`Read-Host -AsSecureString` i PowerShell, `IFS= read -rs` i bash).

## Hva som ble rettet, og hvorfor

Under arbeidet:

- **Tegnkoding i underprosesstestene.** Testen av at API-et ikke starter med ugyldig
  utløpstid feilet fordi `subprocess.run(text=True)` leste feilmeldingen med Windows'
  standardkoding (cp1252), og «må være» ble feil. Lagt til `encoding="utf-8"`.
- **Advarsel fra PyJWT** om for kort nøkkel i testen som lager et HS512-token. Tokenet
  lages nå med advarselen slått av, så testen fortsatt bruker riktig nøkkel og bare
  feil algoritme.
- **Testene var avhengige av miljøet.** Med `TURNUSHJELPEREN_JWT_MINUTTER` satt i
  terminalen ville cookietesten feilet. Testappene får nå utløpstiden eksplisitt.
- **En meningsløs linje** (`... if False else None`) i en test for unikt brukernavn
  ble fjernet før første kjøring.

Etter den uavhengige gjennomgangen 2026-11-07, ført inn av orkestratoren. Tre
underagenter som ikke hadde sett implementeringen, ga til sammen 25 funn. Orkestratoren
kontrollerte hvert funn mot koden. 13 ble rettet, 1 ble utsatt og 11 ble avvist med
begrunnelse (Review Triage Log #12–#36 i spesifikasjonen). Det som var galt i den
genererte koden og dokumentasjonen:

- **Levetiden til tokenet var ikke testet.** Ingen test kontrollerte `exp - iat` mot
  `minutter`, så `timedelta(seconds=…)` eller fast 480 minutter i `main.py` ville gått
  gjennom. Nå testes `exp - iat == 1800` for 30 minutter, og et token som er 479 minutter
  gammelt, godtas fortsatt.
- **Lengdegrensene var ikke testet og stemte ikke med skjemaet.** API-et godtok 100 tegn
  i brukernavnet, mens kolonnen er `String(50)`. Grensen er nå 50. Tester for 51 og 257
  tegn gir 422, og 50 og 256 tegn gir 401.
- **`passord_kilde` hadde typen `str`** i svaret fra `/api/innloggingsinfo`. Typen er nå
  de tre lovlige verdiene, så OpenAPI-kontrakten stemmer med frontend.
- **Brukernavnet ble ikke trimmet**, så et mellomrom fra autofyll ga feil innlogging.
- **README:** det personlige passordet ble liggende i terminalmiljøet og ble arvet av
  uvicorn. Variabelen fjernes nå etter testdatakommandoen. `read` i bash uten `IFS=`
  fjernet mellomrom først og sist i passordet.
- **Planleggingsdokumentene var ikke helt oppdatert.** OP-10-avsnittet i `epics.md` sto
  som åpent. AD-3 sa at utløpstiden ikke var fastsatt. Det åpne `/api/innloggingsinfo`
  var ikke ført som unntak i story 1.4, så 1.4 ville stengt det. Arkitekturen hadde
  «dokumenteres udokumentert».
- **KI-loggen og vurderingsmatrisen** manglet Johannes' instruksjon, gjennomgangen og
  bevisene for story 1.3.

Utsatt til `deferred-work.md`: ingen test binder frontendens feiltekster til
backendkodene, fordi spesifikasjonen utelukker frontendtester. Avvist blant annet: svært
store verdier i `TURNUSHJELPEREN_JWT_MINUTTER` (over ca. 4·10⁹) gir 500 i stedet for
stopp ved oppstart, og en gammel sesjon gjelder også etter ny kjøring av testdata, fordi
SQLite gjenbruker id 1. Begge er lite sannsynlige, og rettelsen ville gitt mer kode.

## Kvalitetssikring

- Etter rettelsene, kjørt av orkestratoren: `pytest` ga 111 passed både uten og med
  `TURNUSHJELPEREN_PASSORD` satt. Testdatakommandoen ga `bruker: 1` to ganger på rad.
  `npm run build` ga ingen feil, og grep-kontrollen for rå størrelser ga ingen treff.
- `pytest` fra `backend/` (Python 3.12.5), før rettelsene etter gjennomgangen: 107 passed, både uten
  `TURNUSHJELPEREN_PASSORD` og med variabelen satt i terminalen. API-testene består
  også med `TURNUSHJELPEREN_JWT_MINUTTER=30` satt.
- Testene dekker hele I/O-matrisen, blant annet cookieattributtene, at tokenet ikke
  står i kroppen, at feil brukernavn og feil passord gir identisk kropp, at
  `hashlib.scrypt` kalles én gang også for ukjent bruker (tellet via `monkeypatch`), at
  ingen innsendte verdier står i 422-svaret, utløpt token, feil nøkkel, `alg: none`,
  HS512, slettet bruker, ny nøkkel etter omstart, 404, 405 og 500, begge
  passordvariantene, at et tilfeldig passord virker og at det forrige slutter å virke.
- Mutasjonskontroll: fire endringer ble lagt inn én om gangen og tilbakestilt, og hver
  ga røde tester. Dummy-hashen fjernet (1 feilet), HS512 godtatt (1 feilet),
  valideringshåndtereren koblet fra (9 feilet) og `SameSite=Lax` (1 feilet).
- `npm run build` fra `frontend/`: ingen typefeil.
- `grep -rnE "[0-9.]+(px|rem)|#[0-9a-fA-F]{3,6}" frontend/src/komponenter frontend/src/stil/app.css`:
  ingen treff.
- Testdatakommandoen er kjørt to ganger mot den eksisterende `backend/turnushjelperen.db`
  fra story 1.2. Første kjøring la til tabellen `bruker`, og begge ga `bruker: 1`.

**Manuelle tester i Chrome, 2026-11-07, utført av agenten med nettleserverktøyet:**

| Test | Resultat |
|---|---|
| Innloggingsflaten uten innlogging | «TURNUSHJELPEREN» til venstre, «Ikke innlogget» til høyre, felt, rollenotat, `button-primary` og taggen «Testpassord» med forklaring. Ikke noe passord. |
| Feil passord | «Feil brukernavn eller passord» i skjemaet, brukernavnet beholdt, passordfeltet tømt og fokusert. |
| Riktig passord | Appbaren viser «Innlogget: Kari Vestby (turnusansvarlig) · Avdeling Kirurgisk sengepost». `document.cookie` er tom (httpOnly). |
| Last siden på nytt | Fortsatt innlogget. |
| Backend stoppet, siden lastet | Innloggingsflaten med «Får ikke kontakt med serveren.». |
| Backend startet på nytt, testdata lastet med `TURNUSHJELPEREN_PASSORD` | Logget ut. Kortet viser «Personlig passord» og «Valgt med TURNUSHJELPEREN_PASSORD.». |
| Fokusramme | Synlig på brukernavnfeltet, passordfeltet og knappen. Tab flytter mellom dem. |
| 1600px, standard og 20px rotskrift | Appbaren 1600px, innholdet 1180px, ingen vannrett rulling. Brødtekst 12,5px → 15,625px, polstring og kanter uendret (32px, 1px), ingen klipt tekst. |
| 360px, standard og 20px rotskrift | Ingen element utenfor 360px, kortet 328px, appbaren bryter linjen. Ingen klipt tekst. |

Begrensninger i de manuelle testene, som et gruppemedlem bør gjøre for hånd:

- **Enter i skjemaet.** Nettleserverktøyets syntetiske tastetrykk sendte ikke skjemaet,
  verken fra passordfeltet eller fra knappen. Skjemaet bruker `<form>` med en
  `type="submit"`-knapp, og `requestSubmit()` ga riktig resultat, men innlogging bare
  med tastaturet (tab og enter) er ikke bekreftet med ekte tastetrykk. Bekreftet av
  Johannes 2026-11-07, se under.
- **20px standard skriftstørrelse** ble simulert med `font-size: 20px` på `<html>`, ikke
  med innstillingen i nettleseren. Virkningen på `rem` er den samme.
- **360px bredde** ble simulert med `width: 360px` på `<body>`, fordi vinduet ikke lot
  seg gjøre smalere. Mediespørringer finnes ikke, så resultatet bør være det samme.

**Manuell test utført av Johannes W. Gaertner, 2026-11-07, Windows og ekte tastatur:**

| Test | Resultat |
|---|---|
| Testdata med tilfeldig testpassord (variant B), backend og frontend etter README | Testdataene og backend startet som forventet. `npm run dev` stoppet i PowerShell med `UnauthorizedAccess` («running scripts is disabled»), fordi Windows' standardpolicy blokkerer `npm.ps1`. Med `npm.cmd run dev` startet frontend. README-steg 4 og «Kjente fallgruver» i AGENTS.md er oppdatert. |
| Innlogging bare med tastaturet (tab og enter) som `kari.vestby` | Forventet resultat. |

Ikke kontrollert:

- Ikke kjørt på macOS/Linux. Fysisk test der er strøket 2026-11-07 (OP-05), fordi verken
  sensor eller noen i gruppa har Mac. Bash-kommandoene for passordvariantene er i stedet
  kjørt i Git Bash på Windows av orkestratoren 2026-11-07, mot en midlertidig database.
  `IFS= read -rsp` beholdt mellomrom først og sist, og innloggingen virket med det
  passordet. Uten `IFS=` ble mellomrommene fjernet, som gjennomgangen sa. Variant B ga et
  tilfeldig passord på 12 tegn.
- Utskriften av «kjøring» blir feil i Git Bash på Windows (cp1252 i en pipe). Passordet
  er bare ASCII og vises riktig.
