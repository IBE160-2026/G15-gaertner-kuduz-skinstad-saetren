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
  [Avhengighetsfiguren](docs/figurer/epics-stories-avhengigheter.svg) oppdateres manuelt
  når storystatus endres.
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
den for macOS/Linux og Git Bash. Appen er laget for å virke på alle tre. Den er testet
på Windows og på macOS. På macOS bestod 275 av 275 backendtester 2026-11-11. Fra en ren
klone på macOS 2026-11-12, med Python 3.12.14 og Node 26.8.1, bestod 337 av 337
backendtester og 26 av 26 frontendtester, `npm run build` gikk gjennom, og innlogging og
Vaktvalg virket. Linux kjøres bare i CI. Bash-kommandoene er kontrollert i Git Bash
(OP-05).

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
Databasen har fem tabeller: `turnus`, `ansatt`, `vakt`, `bruker` og `godkjenning`.
Kommandoen tømmer og fyller tabellene på nytt og kan kjøres flere ganger. Databasen havner i
`backend/turnushjelperen.db`, med mindre miljøvariabelen `TURNUSHJELPEREN_DB` peker et
annet sted. Slett filen hvis skjemaet er endret. En database fra før story 1.3 trenger
ikke slettes: kommandoen legger til tabellene som mangler. Ved skjemaendring i en
eksisterende tabell må databasefilen fortsatt slettes. Story 5.1 har lagt til
kolonner for preferansetolkningen i `ansatt`, så en database fra før story 5.1 må
slettes før kommandoen kjøres på nytt. Ellers feiler backend med «no such column».

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

#### Preferansetolkning med KI (story 5.1)

Når backend starter, tolker den preferansetekstene til de ansatte med
`openai/gpt-6-luna` via OpenRouter, i bakgrunnen. Appen kan brukes mens det pågår.
Hver tekst får én av fem kategorier, og koden gir poengene (100/75/50/25/0). Til en
tekst er tolket, viser kandidatlisten «Preferanse venter på tolkning» med midlertidig
50 poeng. Hent listen på nytt for å se ferdige tolkninger. Testdataene har 19 tekster,
og hver Ansatt tolkes for seg, så det blir 19 betalte kall. Med høyst 18 kall i
minuttet tar det ca. 1–2 minutter. Ferdige tolkninger lagres i databasen og tolkes
ikke på nytt. En tekst som ikke kunne tolkes, vises som «Preferanse kunne ikke
tolkes» og prøves igjen neste gang backend starter. Det finnes ennå ingen knapp for
nytt forsøk.

Fremdriften vises ikke i terminalen. Backend logger hver tekst på nivå INFO, og
Kjør backend med én worker. Låsene som samordner preferansetolkning ved oppstart og
brukerutløste forsøk deles ikke mellom flere serverprosesser.

uvicorn viser ikke INFO fra appens egne meldinger i oppsettet over. I terminalen ser du
bare advarsler, for eksempel `kunne ikke tolkes (nettverk)`, og feil. Hent
kandidatlisten på nytt for å følge med: tolkingen er ferdig når ingen rad lenger sier
«Preferanse venter på tolkning».

Backend leser ikke `.env`. Nøkkelen settes i terminalen før uvicorn startes, uten at
den vises på skjermen:

PowerShell:

```
$env:OPENROUTER_API_KEY = [Net.NetworkCredential]::new('', (Read-Host -AsSecureString 'OpenRouter-nøkkel')).Password
.venv\Scripts\python -m uvicorn adaptere.api.main:app --reload
```

bash:

```
IFS= read -rsp 'OpenRouter-nøkkel: ' OPENROUTER_API_KEY && export OPENROUTER_API_KEY
.venv/bin/python -m uvicorn adaptere.api.main:app --reload
```

`OPENROUTER_MODEL` velger en annen modell (tom gir `openai/gpt-6-luna`). `KI_MODUS`
er `openrouter` (standard) eller `demo`.

#### Demo-modus uten nøkkel (story 5.7, AD-6, SM-9)

Mangler `OPENROUTER_API_KEY`, starter backend automatisk i demo-modus: ingen
nettverkskall, ingen venting og appen krasjer ikke. Backend skriver én linje i
terminalen, for eksempel `Preferansetolkning kjører i demo-modus:
OPENROUTER_API_KEY er ikke satt. Se README.` Det samme gjelder et eksplisitt satt
`KI_MODUS=demo`, med eller uten nøkkel (da uten noen WARNING, siden det er et
bevisst valg). Et ukjent `KI_MODUS` eller en nøkkel/modell med feil form gir
fortsatt ingen KI i det hele tatt, akkurat som før story 5.7.

Demo-modus (`DemoKiAdapter`, `backend/adaptere/ki/demo.py`) viser forhåndsgenererte
svar for de 15 fasittekstene i PRD §4.5 og for Avveiningen til de fire Gyldige
kandidatene på vakt #4127, laget med `OpenRouterKiAdapter` og samme prompt som live
(se `docs/ki-logg/`). Innholdet ligger i `backend/adaptere/ki/demoinnhold.json` og
regenereres med:

```
python scripts/generer_demoinnhold.py --live
```

(19 betalte kall, se skriptets docstring). Uten `--live` er det en tørrkjøring.
Hver forhåndsgenerert Avveining faktakontrolleres på nytt mot gjeldende tall ved
hvert oppslag (P-06): endrer testdataene eller vektene seg, faller demo-modus
automatisk tilbake til et mal-svar satt sammen av kode, aldri en foreldet
sammenligning. En preferansetekst uten forhåndsgenerert treff gir «kunne ikke
tolkes» med midlertidig 50 poeng, aldri en oppdiktet kategori.

Kjent begrensning: frontend viser i dag kildelinjen («Forhåndsgenerert
KI-forklaring» / «Satt sammen fra beregnede tall») bare for `ki_kilde: "live"`
(`frontend/src/kandidater.ts`, `gyldigAvveining`). Avveininger fra demo-modus
(`"forhandsgenerert"` eller `"mal"`) blir derfor ikke vist av dagens frontend, selv
om backend-svaret er riktig. Dette er et åpent punkt for en egen UI-story, se
`_bmad-output/implementation-artifacts/deferred-work.md`.

Dette er verdt å vite:

- `--reload` starter backend på nytt ved hver kodeendring, og da startes tolkningen
  på nytt for tekstene som ikke er ferdige. Det kan gi flere betalte kall. Uten
  `--reload` skjer det bare når du starter backend selv.
- En ny tolkning endrer beslutningsgrunnlaget. Står du på godkjenningsflaten mens
  tolkningen pågår, kan «Godkjenn erstatning» gi «grunnlaget er endret». Flaten
  henter da grunnlaget på nytt, og du trykker igjen.
- Ved 5xx-feil og nettverksfeil prøver backend tre ganger til, etter 2, 4 og 8 s. Ved
  429 venter den til OpenRouter sier at grensen er nullstilt. All venting for én tekst
  er begrenset til 90 s. 402, andre 4xx-feil og svar som ikke følger formatet prøves
  ikke på nytt. Tallene er vedtatt som AV-19 (2026-11-16) og står som konstanter i `backend/adaptere/ki/openrouter.py`.
- Mangler `X-RateLimit-Reset` eller kan ikke leses, venter backend 60 s ved 429, og
  aldri under 1 s. 3xx og andre uventede statuser lagres som feiltypen `4xx`.
  `KI_MODUS` skiller mellom store og små bokstaver: `OpenRouter` slår av tolkningen.
  En nøkkel med andre tegn enn synlige ASCII-tegn slår også av tolkningen.
- Er databasen fra før story 5.1, stopper tolkningen med én feilmelding som ber deg
  slette databasen og laste testdata på nytt.
- På macOS kan Python mangle rotsertifikater. Da feiler alle kall etter ca. 14 s, og
  hver tekst står som «Preferanse kunne ikke tolkes» med feiltypen `nettverk`, selv om
  nettet virker. Årsaken er `CERTIFICATE_VERIFY_FAILED`, som backend ikke skriver ut.
  Pek Python til systemets sertifikater når du starter backend (bash/zsh):

  ```
  SSL_CERT_FILE=/etc/ssl/cert.pem .venv/bin/python -m uvicorn adaptere.api.main:app
  ```

  Dette er prøvd på macOS 2026-11-16 (Python 3.15.2). Tekster som feilet, prøves på nytt
  ved neste oppstart. Ikke sjekket på Windows.

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

`npm install` melder «1 high severity vulnerability». Den gjelder Vite 8.3.1 og bare
utviklingsserveren mens den kjører lokalt. Gruppa har vurdert den og valgt å ikke oppgradere
nå (OP-16 i [avklaringspunktene](docs/beslutninger/avklaringspunkter.md)). Ikke kjør
`npm audit fix`. Den endrer de låste versjonene.

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
Listen hentes automatisk. Etter story 2.4 er den filtrert på alle fire harde
regler: kompetanse-minstekravet (FR2), kolliderende vakt (FR3), 11-timersregelen
(FR4) og 35-timersregelen (FR5). I testdataene gir #4127 4 gyldige (Ingrid Dahl,
Jonas Bakke, Mette Solberg og Thomas Nygård) og #4189 0. Når ingen er gyldige, svarer API-et 200 med
`status: "ingen_gyldige_kandidater"` og tom liste, og flaten viser tomtilstanden
(story 2.6, FR6, UX-DR16): «!»-ikon, «Ingen gyldige kandidater for denne vakten. Dette
er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null
treff.», Ekskludert-boksen og «Innleie av personell kan vurderes» som ren tekst, uten
knapp (P-11). Under listen (eller under tomteksten) viser Ekskludert-boksen
(story 2.5, UX-DR15) hvor mange som er utelukket og av hvilken regel, for eksempel
«20 utelukket av harde regler · 8 under kompetanse-minstekrav · 7 kolliderende
vakt · 4 brudd på 11-timersregelen · 1 brudd på 35-timersregelen» for #4127 og
«24 utelukket …» for #4189. «Vis full liste ▾» viser hver utelukket ansatt med
navn og alle årsakene. Boksen vises bare når minst én kandidat er utelukket, og en
kandidat som bryter flere regler telles én gang i totalen og under hver regel den
bryter. En vakt der hvilen før eller etter eller en berørt kalenderuke ikke
kan kontrolleres fordi testdataene slutter 05.10 kl. 00:00, gir en melding om
manglende turnusgrunnlag (P-08). Det kan ikke nås
gjennom vanlig bruk, fordi bare #4127 og #4189 mangler bemanning, og begge ligger
innenfor dekningen. Det er dekket av API-tester med endret testdatabase. Direkte URL og
nettleserens tilbakeknapp virker. En bemannet, ukjent eller utenforliggende vakt
gir en nøytral feilmelding (AV-03). Feil ved lasting kan prøves på nytt.

Hver kandidat i listen har knappen «Velg», som går til godkjenningsflaten på
`/vakt/<nr>/godkjenning/<ansatt_id>` (story 3.1). Den viser brødsmulestien
`Turnus > <avdeling> > Vakt #<nr> > Kandidater > Godkjenning`, vakten, et
kandidatkort med navn og nivå, en bekreftelsesboks som sier hvem som settes inn i
hvilken vakt, og statuslinjen «Ikke gjennomført — venter på eksplisitt godkjenning».
«Avbryt» går tilbake til kandidatlisten. «Godkjenn erstatning» kontrollerer alle harde
regler på nytt og bemanner vakten når grunnlaget er uendret. Godkjenningen lagres med
valgt ansatt, vakt, godkjennende bruker og tidspunkt. Vaktvalg åpnes med en bekreftelse
som navngir den ansatte og vaktens nummer, og vakten står blant de bemannede. Er
grunnlaget endret, hentes opplysningene på nytt og
du må trykke igjen. Ugyldig kandidat, datafeil og allerede bemannet vakt får egne
meldinger uten ny godkjenning. Hvis POST-svaret går tapt, sier flaten at utfallet er
usikkert og ber deg kontrollere Vaktvalg før du prøver igjen. En adresse for en
Ansatt som ikke er en gyldig kandidat for vakten, eller for en vakt som ikke
mangler bemanning, gir «Kandidaten kan ikke velges for denne vakten.» med lenke
tilbake til kandidatlisten.

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
kompetansenivå}], "utelukkelser": {"totalt", "per_regel": [{"årsak", "antall"}],
"utelukkede": [{"id", "navn", "årsaker"}]}}`. `kandidater` er fortsatt bare
gyldige kandidater; `utelukkelser` er bygd av regelmotoren fra alle utelukkede, til
Ekskludert-boksen (story 2.5). Mangler eller er turnusgrunnlaget
ugyldig, for eksempel fordi vakten slutter etter datagrensen 05.10.2026 kl. 00:00,
er svaret fortsatt 200, men `{"status": "datafeil", "kode": "mangler_turnusgrunnlag",
"datagrense": "2026-10-05T00:00:00+02:00"}` uten liste (P-08).
`GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id}` gir grunnlaget for
godkjenningsflaten: `{"status": "ok", "vakt": {…som vaktdetaljene}, "kandidat": {id,
navn, kompetansenivå}, "grunnlagsmerke": "…"}`, eller samme datafeilsvar.
Det svarer bare for Ansatte som er
i kandidatlisten for vakten. En utelukket, ukjent eller opprinnelig oppsatt Ansatt gir
samme 404 `ikke_funnet`, uten å si hvorfor (NFR2). `POST` på samme sti krever
`{"grunnlagsmerke": "…"}` og svarer `{"status": "godkjent"}` ved vellykket lagring.
Endret grunnlag, ugyldig kandidat og allerede bemannet vakt gir 409 med ulike
`{kode, melding}`. Datafeil gir 200 med `status: "datafeil"` og datagrense.
Reglene og Rangeringen beregnes i `backend/domene/regelmotor/` uten KI. Rangeringen
bruker bare lagrede tolkninger og gjør aldri et KI-kall.
API-dokumentasjon er deaktivert.

### Tester

Fra `backend/`: `.venv\Scripts\python -m pytest`. Testene bruker egne databaser i en
midlertidig mappe og rører ikke `backend/turnushjelperen.db`. `tester/test_arkitektur.py`
kjører import-linter-kontrakten i `pyproject.toml`, som forbyr hele `domene`, også
`domene.regelmotor` og `domene.porter`, å importere `adaptere` (AD-1, AD-2). Fra `frontend/`:
`npm run test` kjører to sett tester etter hverandre:

- `node --test` finner alle `*.test.mjs` og andre testfiler i hele `frontend/` utenom
  `node_modules`. I dag er det `tester/sesjon.test.mjs`, `tester/format.test.mjs`,
  `tester/kandidater.test.mjs` og `tester/godkjenning.test.mjs`, som tester den rene
  logikken i `src/`. Formateringstestene kjøres også en gang til i en underprosess med
  `TZ=America/New_York`, så de ikke består bare fordi maskinen går i Oslo-tid.
- `vitest run` kjører komponenttestene i `tester/komponenter/*.test.tsx`. De rendrer
  komponentene i jsdom med Testing Library og en falsk `fetch`, og trykker på knappene
  som en bruker.

`npm run build` typesjekker koden og komponenttestene og bygger (`npm.cmd run test`
og `npm.cmd run build` i PowerShell hvis skript er blokkert, se steg 4). Hva som
testes automatisk, og hva som kontrolleres for hånd og hvorfor, står i
[docs/testing.md](docs/testing.md). Komponenttestene bruker mye minne. På en maskin med
lite ledig RAM tar de rundt 20 sekunder, og de kan få tidsavbrudd hvis flere kjøringer
går samtidig. Se «Trege maskiner og tidsavbrudd» i samme fil.

GitHub Actions kjører de samme testene på Linux ved hver push: backend med Python
3.12 og nyeste 3.x, frontend (`npm run build` og `npm run test`) med Node 22.12 og
nyeste LTS, og i tillegg speilingstesten for skills. Resultatet vises i hver PR. CI
får ingen API-nøkler og gjør ingen kall mot Luna. Rød CI stopper ikke en merge, og
grønn CI betyr ikke at koden er gjennomgått.

## Vurderingsgrunnlag

- [Sensorveiledning del 1](docs/emne/sensorveiledning-del-1.md) – tekstgjengivelse med sidereferanser og lenke til original PDF.
- [Vurderingsmatrise](docs/emne/vurderingsmatrise.md) – tiltak, dokumenterte bevis og arbeid som gjenstår.
