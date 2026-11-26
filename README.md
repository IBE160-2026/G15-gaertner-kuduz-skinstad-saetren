# G15 Prompt Patrol — Turnushjelperen

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026.

**Turnushjelperen** er en prototype av et beslutningsstøtteverktøy for en
turnusansvarlig som må finne en erstatter når én vakt i en eksisterende turnus
plutselig må dekkes av en annen ansatt.

Appen fjerner kandidater som bryter fire harde regler: kompetansekrav, kolliderende
vakt, 11 timers daglig hvile og 35 timers ukentlig fri. Resten rangeres etter kostnad,
timebelastning, ulempebelastning og preferanser. KI tolker de ansattes preferanser i
fritekst og forklarer avveiningene mellom kandidatene. KI beregner aldri regler,
arbeidstid eller kostnad, og den endelige beslutningen tas alltid av turnusansvarlig.
Alle data er fiktive, og de fire reglene er ingen garanti for full juridisk etterlevelse.

## Medlemmer

- Johannes W Gaertner
- Mithad Kuduz
- Kim O Skinstad
- Ragnhild Sætren

## Forutsetninger

- Python 3.12 eller nyere
- Node.js 22.12 eller nyere
- Ingen API-nøkkel. Uten nøkkel kjører appen i demo-modus med ferdiglagde KI-svar
  (se [KI: demo-modus eller live](#ki-demo-modus-eller-live)).

Appen er testet på Windows og macOS, og testene kjøres på Linux i CI. Kommandoene under
er for Windows PowerShell. På macOS og Linux bytter du `.venv\Scripts\python` med
`.venv/bin/python`. Der det står en egen bash-kommando, gjelder den macOS, Linux og
Git Bash.

## Kom i gang

Du trenger to terminaler: én for backend og én for frontend.

### 1. Installer backend

Fra mappa `backend/`:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

### 2. Last testdata og velg passord

Testdatakommandoen lager en fiktiv avdeling (Kirurgisk sengepost, uke 39–40 2026, 25
ansatte) og turnusansvarlig Kari Vestby med brukernavnet `kari.vestby`. Den tømmer og
fyller databasen på nytt og kan kjøres flere ganger. Ingen passord står i repoet. Velg
én av to varianter, fra `backend/`:

**A. Velg passordet selv (anbefalt for sensor).** Det du skriver, vises ikke på skjermen.

PowerShell:

```
$env:TURNUSHJELPEREN_PASSORD = [Net.NetworkCredential]::new('', (Read-Host -AsSecureString 'Velg passord')).Password
.venv\Scripts\python -m adaptere.lagring.testdata
Remove-Item Env:TURNUSHJELPEREN_PASSORD
```

bash:

```
IFS= read -rsp 'Velg passord: ' TURNUSHJELPEREN_PASSORD && export TURNUSHJELPEREN_PASSORD
.venv/bin/python -m adaptere.lagring.testdata
unset TURNUSHJELPEREN_PASSORD
```

Siste linje i utskriften er `Passord: personlig, fra TURNUSHJELPEREN_PASSORD`.

**B. La kommandoen lage et tilfeldig passord.**

PowerShell:

```
Remove-Item Env:TURNUSHJELPEREN_PASSORD -ErrorAction SilentlyContinue
.venv\Scripts\python -m adaptere.lagring.testdata
```

bash:

```
unset TURNUSHJELPEREN_PASSORD
.venv/bin/python -m adaptere.lagring.testdata
```

Siste linje i utskriften viser passordet. Noter det: neste kjøring lager et nytt.

Innloggingskortet viser hvilken variant som gjelder, men aldri passordet: «Personlig
passord» eller «Testpassord». Står det «Ingen bruker», er steg 2 ikke kjørt.

### 3. Start backend

Fra `backend/`:

```
.venv\Scripts\python -m uvicorn adaptere.api.main:app
```

Uten API-nøkkel skriver backend `Preferansetolkning kjører i demo-modus: OPENROUTER_API_KEY er ikke satt.`
Det er forventet. Helsesjekken svarer på http://127.0.0.1:8000/api/helse.

### 4. Start frontend

Fra `frontend/`, i en ny terminal:

```
npm install
npm run dev
```

Stopper PowerShell `npm` med `UnauthorizedAccess` («running scripts is disabled»), bruker
du `npm.cmd install` og `npm.cmd run dev`.

Åpne http://localhost:5173 og logg inn som `kari.vestby` med passordet fra steg 2.
Backend må kjøre samtidig. Ellers viser innloggingssiden «Får ikke kontakt med
serveren.».

## Slik bruker du appen

Testdataene har to vakter som mangler bemanning: #4127 med fire gyldige kandidater, og
#4189 der ingen er gyldige.

1. **Vaktvalg.** Etter innlogging står vaktene som mangler bemanning, øverst under
   «Krever handling». De 164 bemannede vaktene i perioden står i tabellen under. Velg
   #4127 med «Velg vakt — finn erstatter →».
2. **Gyldige kandidater.** Bare kandidater som består alle fire reglene, vises. De er
   rangert, og for hver kandidat ser du kompetansenivå, kostnad, timer i uka, ulempe
   og preferanse. Høy belastning og overtid er merket. «Endre» i preferansecellen lar deg
   skrive en ny preferansetekst. Den tolkes, og rangeringen oppdateres (i demo-modus
   tolkes bare de forhåndsdefinerte tekstene).
3. **Begrunnelse.** «Vis begrunnelse» åpner KI-forklaringen av avveiningen for
   kandidaten. Tallene i forklaringen er kontrollert mot regelmotorens tall før den
   vises. Feiler KI-en, vises nøkkeltallene med en reservetekst, og du kan fortsatt
   velge kandidaten.
4. **Utelukkede.** Under listen viser Ekskludert-boksen hvor mange som ble utelukket
   av hver regel. «Vis full liste» viser navn og årsak.
5. **Godkjenning.** «Velg» åpner godkjenningsflaten. Velger du en annen enn den
   som står øverst, vises et avviksnotat. Ingenting lagres før du trykker
   «Godkjenn erstatning». Da kontrolleres reglene på nytt. Er grunnlaget endret
   underveis, må du bekrefte på nytt.
6. **Ingen gyldige.** #4189 viser at regelmotoren har kjørt ferdig uten treff, og at
   innleie kan vurderes.

En vakt der testdataene ikke dekker hvilen før og etter, gir en melding om manglende
turnusgrunnlag i stedet for en liste. Testdatakommandoen tilbakestiller alt, også
godkjente vakter.

## KI: demo-modus eller live

KI-en brukes til to ting: å tolke de ansattes preferanser i fritekst og å forklare
avveiningen for én kandidat. Rangeringen gjør aldri selv et KI-kall. Den bruker bare
tolkninger som er lagret.

- **Demo-modus (standard uten nøkkel).** Appbaren viser «Demo-modus». Svarene er
  laget på forhånd med samme modell og prompt som live
  ([`demoinnhold.json`](backend/adaptere/ki/demoinnhold.json)). Forklaringene finnes for
  de fire kandidatene på #4127 og merkes «Forhåndsgenerert KI-forklaring». Endres
  tallene, vises en tekst satt sammen av kode i stedet, og den merkes slik.
- **Live mot OpenRouter.** Sett nøkkelen i samme terminal som du starter backend fra.
  Backend leser ikke `.env`.

  PowerShell:

  ```
  $env:OPENROUTER_API_KEY = [Net.NetworkCredential]::new('', (Read-Host -AsSecureString 'OpenRouter-nøkkel')).Password
  .venv\Scripts\python -m uvicorn adaptere.api.main:app
  ```

  bash:

  ```
  IFS= read -rsp 'OpenRouter-nøkkel: ' OPENROUTER_API_KEY && export OPENROUTER_API_KEY
  .venv/bin/python -m uvicorn adaptere.api.main:app
  ```

  Modellen er `openai/gpt-6-luna`. Ved oppstart tolkes preferansetekstene i bakgrunnen
  med 19 betalte kall, og det tar 1–2 minutter. Fremdriften vises i terminalen, og appen
  kan brukes imens. Live er aktiv når forklaringene merkes
  «KI-generert · openai/gpt-6-luna», appbaren ikke viser «Demo-modus», og terminalen ikke
  skriver demo-linjen fra steg 3. Står det «Demo-modus» likevel, eller viser forklaringene
  reservetekst, se [Feilsøking](#feilsøking).

Feilhåndtering, nye forsøk og flere detaljer står i
[teknisk referanse](docs/teknisk-referanse.md#ki-integrasjonen).

## Konfigurasjon

Alle variablene er valgfrie og settes i terminalen. Backend leser ikke `.env`.
[`.env.example`](.env.example) viser dem uten verdier.

| Variabel | Standard | Hva den gjør |
|---|---|---|
| `OPENROUTER_API_KEY` | ikke satt (demo-modus) | Nøkkel for live KI |
| `OPENROUTER_MODEL` | `openai/gpt-6-luna` | En annen modell |
| `KI_MODUS` | `openrouter` | `demo` tvinger demo-modus, også med nøkkel |
| `TURNUSHJELPEREN_DB` | `backend/turnushjelperen.db` | Sti til databasen |
| `TURNUSHJELPEREN_PASSORD` | tilfeldig | Passordet testdatakommandoen bruker (steg 2) |
| `TURNUSHJELPEREN_JWT_MINUTTER` | 480 | Hvor lenge en innlogging varer, i minutter |

Alle logges ut når backend starter på nytt, fordi nøkkelen som signerer innloggingen
bare finnes i minnet.

## Tester

| Hva | Fra | Kommando |
|---|---|---|
| Backend: regelmotor, API, KI-adapter, lagring og arkitektur | `backend/` | `.venv\Scripts\python -m pytest` |
| Frontend: logikk og komponenter | `frontend/` | `npm run test` |
| Frontend: typesjekk og bygg | `frontend/` | `npm run build` |

Ingen test gjør nettverkskall eller rører databasen din. KI-testene bruker en falsk
OpenRouter. Backendtestene kjører også linteren ruff, og `npm run build` avviser
ubrukte variabler og parametre. GitHub Actions kjører de samme testene på Linux ved hver push, med laveste
og nyeste støttede versjon av Python og Node. Hva som testes automatisk, hva som
kontrolleres manuelt og hvorfor, står i [docs/testing.md](docs/testing.md).

## Feilsøking

- **«no such column» eller feil om databasen:** Databasen er fra en eldre versjon, for
  eksempel fra før preferanseteksten kunne endres (`preferanseversjon`). Slett
  `backend/turnushjelperen.db` og kjør steg 2 på nytt.
- **Lange filstier på Windows:** Kloner du til en sti lengre enn ca. 130 tegn, kan
  checkout feile med «Filename too long», og `python -m venv` kan feile. Klon til en
  kortere sti, for eksempel `C:\g15`. `git config --global core.longpaths true` løser
  det for git, men ikke for Python.
- **`npm install` melder «1 high severity vulnerability»:** Den gjelder bare Vite sin
  lokale utviklingsserver. Gruppa har vurdert den og valgt å ikke oppgradere
  ([§11 i referatet](docs/beslutninger/avklaringspunkter.md)). Ikke kjør
  `npm audit fix`, for det endrer de låste versjonene.
- **Live KI på macOS: alle tekster står som «kunne ikke tolkes» (`nettverk`):** Python
  mangler rotsertifikater. Start backend med
  `SSL_CERT_FILE=/etc/ssl/cert.pem .venv/bin/python -m uvicorn adaptere.api.main:app`.
- **«Demo-modus» i appbaren selv om du har satt nøkkelen:** Backend fant ikke nøkkelen,
  og terminalen skriver demo-linjen fra steg 3. En nøkkel i `.env` eller i en annen
  terminal brukes ikke. Stopp backend med Ctrl+C, sett nøkkelen og start backend på nytt
  i samme terminal.
- **Live KI: forklaringene er reservetekst og preferansene «kunne ikke tolkes» (`4xx`):**
  Kreditten er brukt opp, eller nøkkelen er ugyldig. Appen krasjer ikke. Forklaringene
  merkes «Reservetekst · KI-forklaring utilgjengelig» og viser nøkkeltallene,
  preferansene får midlertidig 50 poeng, og rangering og godkjenning virker. Appen
  bytter ikke selv til demo-modus. Vil du bruke den, stopper du backend med Ctrl+C og
  starter den i en ny terminal uten nøkkel.
- **Ikke «Demo-modus», men forklaringene er reservetekst og terminalen skriver
  `Preferansetolkning er av: OPENROUTER_API_KEY har ugyldige tegn`:** Nøkkelen ble limt
  inn feil. Stopp backend med Ctrl+C, sett nøkkelen på nytt i samme terminal (lim inn
  nøyaktig) og start backend igjen.
- **Logget ut uten grunn:** Backend har startet på nytt. Logg inn igjen.

## Mappestruktur

| Mappe | Innhold |
|---|---|
| `backend/domene/` | Regelmotoren og rangeringen. Ren Python uten KI. |
| `backend/adaptere/` | Lagring (SQLite), API (FastAPI) og KI (OpenRouter og demo) |
| `backend/tester/` | Backendtestene |
| `frontend/` | React og TypeScript med Vite. Testene ligger i `frontend/tester/`. |
| `docs/` | Beslutninger, KI-logger, testing, teknisk referanse og emnedokumenter |
| `_bmad-output/` | Planleggingen: PRD, UX, arkitektur, epics og stories |
| `scripts/` | Modelltestene som ble kjørt før modellvalget |
| `.logs/` | Sesjonslogger per gruppemedlem |
| `_bmad/`, `.claude/`, `.agents/` | BMAD-rammeverket og agentoppsettet for Claude Code og Codex. De er sporet med vilje, slik at hele gruppa bruker samme oppsett. |

## Planlegging og prosess

- [Produktbrief](product-brief.md): problemet, målgruppen og omfanget
- Tilbakemelding fra faglærer på [produktbriefen](tilbakemelding-product-brief.md) (2026-10-06)
  og [PRD-en](_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/tilbakemelding-prd.md) (2026-11-12),
  som er fulgt opp i brief, PRD og epics
- [PRD](_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md): krav, harde regler og rangering
- UX: [DESIGN](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md)
  (utseende) og [EXPERIENCE](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md) (oppførsel)
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md):
  tekniske beslutninger (AD-1 og videre)
- [Epics og stories](_bmad-output/planning-artifacts/epics.md), med fremdriften i
  [sprintstatus](_bmad-output/implementation-artifacts/sprint-status.yaml) og en
  [avhengighetsfigur](docs/figurer/epics-stories-avhengigheter.svg)
- [Beslutningsreferat](docs/beslutninger/avklaringspunkter.md): gruppevedtakene (AV-, K-, OP- og KS-punkter)
- [KI-logger](docs/ki-logg/): prompt, leveranse, rettinger og kvalitetssikring for KI-generert kode.
  [Oversikt og spørringer](docs/ki-logg/README.md)
- Modellvalget: [sammenligning av fire modeller](docs/ki-logg/2026-10-15-modellsammenligning.md),
  [forhåndsregistrert beslutningstest](docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md),
  [robusthetstest av Luna](docs/ki-logg/2026-10-16-robusthet-luna.md) og
  [testveiledning](docs/modelltest-openrouter.md)
- [Teknisk referanse](docs/teknisk-referanse.md): API, KI-integrasjonen og database
- [Sensorveiledning del 1](docs/emne/sensorveiledning-del-1.md) og
  [vurderingsmatrise](docs/emne/vurderingsmatrise.md): hvordan arbeidet er koblet til vurderingskriteriene
