# G15 — Prompt Patrol

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Medlemmer

- Johannes W Gaertner
- Mithad Kuduz
- Kim O Skinstad
- Ragnhild Sætren

## Planleggingsgrunnlag

- [Product brief](product-brief.md) – eneste gjeldende brief for prosjektet.
- [PRD](_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md) – krav til
  funksjonalitet, harde regler og rangering.
- UX: [DESIGN](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md)
  beskriver hvordan appen ser ut, og
  [EXPERIENCE](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md)
  hvordan den oppfører seg.
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md)
  – tekniske beslutninger (AD-1 og videre) som holder delene konsistente.
- [Epics og stories](_bmad-output/planning-artifacts/epics.md) – oppdelingen av arbeidet. Fremdriften
  står i [sprintstatus](_bmad-output/implementation-artifacts/sprint-status.yaml).
- [Beslutningsreferat](docs/beslutninger/avklaringspunkter.md) – gruppevedtak (AV-, K-, OP- og KS-punkter)
  fra møtet 2026-11-02 og senere oppdateringer.

## Modelltest før KI-integrasjonen

Gruppa har valgt `openai/gpt-6-luna` via OpenRouter etter disse testene:

- [Haiku 5.5 alene](docs/ki-logg/2026-10-15-modelltest-haiku.md) og
  [sammenligning med Luna, Mistral og Gemma](docs/ki-logg/2026-10-15-modellsammenligning.md), 15. oktober.
- [Forhåndsregistrert beslutningstest Haiku mot Luna](docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md)
  og [robusthetstest av Luna](docs/ki-logg/2026-10-16-robusthet-luna.md), 16. oktober.

[Testveiledningen](docs/modelltest-openrouter.md) beskriver de isolerte Python-testene.

## Kjøre appen

Appen har innlogging for turnusansvarlig, vaktoversikt (Vaktvalg), valg av vakt og fiktive
testdata. Kandidatlisten kommer i Epic 2. Du trenger Python 3.12 eller nyere og
Node 22.12 eller nyere. Backend og testene er kjørt med Python 3.12.5 og 3.15.2 på Windows
(2026-11-04). Kommandoene under er for Windows PowerShell. På macOS/Linux bytter du
`.venv\Scripts\python` med `.venv/bin/python`. Der det står en egen bash-kommando, er
den for macOS/Linux og Git Bash. Appen er laget for å virke på alle tre, men er bare
testet på Windows. Bash-kommandoene er kontrollert i Git Bash (OP-05).

På Windows er en filsti begrenset til 260 tegn, med mindre lange stier er slått på. Den
lengste filen i repoet har en sti på 125 tegn, så stien du kloner til, bør være kortere
enn ca. 130 tegn. Ellers kan checkout feile med «Filename too long», og `python -m venv`
kan feile i `ensurepip`. Det gjelder også git-worktrees, for eksempel når agenter
jobber i en egen kopi. `git config --global core.longpaths true` løser det for git. For
Python må lange stier slås på i Windows, og det krever administratorrettigheter.

### 1. Installer backend

Fra mappa `backend/`:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

### 2. Last testdata og noter passordet

Testdatakommandoen legger inn de fiktive testdataene (Kirurgisk sengepost, uke 39–40
2026, 25 ansatte) og turnusansvarlig Kari Vestby med brukernavnet `kari.vestby`.
Databasen har fire tabeller: `turnus`, `ansatt`, `vakt` og `bruker`. Kommandoen tømmer
og fyller tabellene på nytt og kan kjøres flere ganger. Databasen havner i
`backend/turnushjelperen.db`, med mindre miljøvariabelen `TURNUSHJELPEREN_DB` peker et
annet sted. Slett filen hvis skjemaet er endret. En database fra før story 1.3 trenger
ikke slettes: kommandoen legger til tabellen `bruker`.

Passordet kan lages på to måter. Backend leser ikke `.env`, så variabelen må settes i
terminalen før kommandoen kjøres.

**A. Personlig passord (ved innlevering).** Du velger passordet selv, så det står aldri
i repoet. Kjør fra `backend/`. Passordet du skriver, vises ikke på skjermen.

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

Utskriften slutter med `Passord: personlig, fra TURNUSHJELPEREN_PASSORD`. Passordet
skrives ikke ut. Den siste linjen fjerner variabelen igjen, så passordet ikke blir
liggende i terminalen og arves av backend i steg 3.

**B. Tilfeldig testpassord (når gruppa tester).** Variabelen må mangle eller være tom.
Har du satt den i samme terminal, fjerner du den først.

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

Utskriften slutter med `Passord: tilfeldig testpassord, gjelder til neste kjøring:`
og passordet. Noter det. Neste kjøring lager et nytt passord, og det gamle slutter å
virke.

**Hvilken variant gjelder?** Den siste linjen i utskriften sier det. Innloggingskortet
viser det også, uten passordet: taggen «Personlig passord» eller «Testpassord». Står det
«Ingen bruker», er testdataene ikke lastet.

### 3. Start backend

Fra `backend/`:

```
.venv\Scripts\python -m uvicorn adaptere.api.main:app --reload
```

Helsesjekken svarer på http://127.0.0.1:8000/api/helse. En innlogging varer i 480
minutter (én vakt). Vil du ha en annen varighet, setter du `TURNUSHJELPEREN_JWT_MINUTTER`
til et positivt heltall i terminalen før uvicorn startes, for eksempel
`$env:TURNUSHJELPEREN_JWT_MINUTTER = "30"` i PowerShell eller
`export TURNUSHJELPEREN_JWT_MINUTTER=30` i bash. Er verdien ikke et positivt heltall,
starter ikke API-et.

Nøkkelen som signerer innloggingen, lages tilfeldig hver gang API-et starter, og lagres
ingen steder. Derfor logges alle ut når serveren starter på nytt, også når `--reload`
starter den på nytt etter en kodeendring. Logg da inn igjen.

### 4. Start frontend i en egen terminal

Fra `frontend/`:

```
npm install
npm run dev
```

Får du `UnauthorizedAccess` eller «running scripts is disabled on this system» i
PowerShell, er det Windows' standardpolicy som stopper skriptet `npm.ps1`. Bruk da
`npm.cmd install` og `npm.cmd run dev`. Det endrer ingenting på maskinen. Git Bash og
`cmd` har ikke denne begrensningen.

Åpne http://localhost:5173 og logg inn som `kari.vestby` med passordet fra steg 2.
Utviklingsserveren sender `/api` videre til backend på http://127.0.0.1:8000, så
backend må kjøre samtidig. Svarer den ikke, viser innloggingssiden «Får ikke kontakt
med serveren.».

Etter innlogging åpnes Vaktvalg på `/turnus/kirurgisk-sengepost`. Vakter som mangler
bemanning står øverst under «Krever handling» (#4127 og #4189 i testdataene), og de
164 bemannede vaktene i perioden står i tabellen under. Vakter som starter før
periodestart, vises ikke (AV-03). «Velg vakt — finn erstatter →» går til
`/vakt/<nr>/kandidater`. Her vises avdeling, vakttype, tidspunkt og minstenivå,
og under dem de gyldige kandidatene alfabetisk med kompetansenivå («Nivå 3/4»).
Listen hentes automatisk. Etter story 2.2 er den filtrert på
kompetanse-minstekravet (FR2) og kolliderende vakt (FR3), og det står i en merknad
under overskriften. Story 2.3 og 2.4 legger til 11- og 35-timersregelen. Med de to
reglene gir #4127 9 gyldige og #4189 19 i testdataene. Direkte URL og
nettleserens tilbakeknapp virker. En bemannet, ukjent eller utenforliggende vakt
gir en nøytral feilmelding (AV-03). Feil ved lasting kan prøves på nytt.

Beskyttede adresser kontrollerer sesjonen før innhold vises. Uten gyldig sesjon
sendes du til `/logg-inn`; en sesjon som bortfaller mens du bruker appen, gir
meldingen «Sesjonen er utløpt. Logg inn på nytt.» og handlingen gjentas ikke.
«Logg ut» sletter nettleserens cookie. Hvis serveren ikke bekrefter utloggingen,
skjules innholdet og du kan prøve igjen. API-et krever sesjon for alle `/api`-kall
unntatt `GET /api/helse`, `POST /api/innlogging` og `GET /api/innloggingsinfo`.
`GET /api/vaktoversikt` gir dataene til Vaktvalg. `GET /api/vakter/{vaktnummer}`
gir bare detaljer for en ubemannet vakt i innlogget brukers turnus og visningsperiode.
`GET /api/vakter/{vaktnummer}/kandidater` gir de gyldige kandidatene for samme
vakter, med samme 401 og 404. Svaret er `{"status": "ok", "kandidater": [{id, navn,
kompetansenivå}]}` med bare gyldige kandidater. Mangler eller er turnusgrunnlaget
ugyldig, for eksempel fordi vakten slutter etter datagrensen 05.10.2026 kl. 00:00,
er svaret fortsatt 200, men `{"status": "datafeil", "kode": "mangler_turnusgrunnlag",
"datagrense": "2026-10-05T00:00:00+02:00"}` uten liste (P-08). Reglene beregnes i
`backend/domene/regelmotor/` uten KI.
API-dokumentasjon er deaktivert.

### Tester

Fra `backend/`: `.venv\Scripts\python -m pytest`. Testene bruker egne databaser i en
midlertidig mappe og rører ikke `backend/turnushjelperen.db`. `tester/test_arkitektur.py`
kjører import-linter-kontrakten i `pyproject.toml`, som forbyr hele `domene`, også
`domene.regelmotor` og `domene.porter`, å importere `adaptere` (AD-1, AD-2). Fra `frontend/`:
`npm run test` kjører `node --test`, som finner alle `*.test.mjs` og andre
testfiler i hele `frontend/` utenom `node_modules`. I dag er det
`tester/sesjon.test.mjs`, `tester/format.test.mjs` og `tester/kandidater.test.mjs`. Formateringstestene kjøres
også en gang til i en underprosess med `TZ=America/New_York`, så de ikke består
bare fordi maskinen går i Oslo-tid. `npm run build` typesjekker og bygger
(`npm.cmd run test` og `npm.cmd run build` i PowerShell hvis skript er blokkert,
se steg 4).

GitHub Actions kjører de samme testene på Linux ved hver push: backend med Python
3.12 og nyeste 3.x, frontend (`npm run build` og `npm run test`) med Node 22.12 og
nyeste LTS, og i tillegg speilingstesten for skills. Resultatet vises i hver PR. CI
får ingen API-nøkler og gjør ingen kall mot Luna. Rød CI stopper ikke en merge, og
grønn CI betyr ikke at koden er gjennomgått.

## Vurderingsgrunnlag

- [Sensorveiledning del 1](docs/emne/sensorveiledning-del-1.md) – tekstgjengivelse med sidereferanser og lenke til original PDF.
- [Vurderingsmatrise](docs/emne/vurderingsmatrise.md) – tiltak, dokumenterte bevis og arbeid som gjenstår.
