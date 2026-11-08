<!-- bmad:context -->
<!-- Grunnlag verifisert 2026-09-23 mot 98f3536. Status og modelltestkommandoer
     oppdatert 2026-10-15 på 2b06245041b499e84027bb9058267afdccec93cc med arbeidsendringer.
     Vedlikeholdes av bmad-project-context;
     endringer inne i denne blokka blir erstattet ved refresh.
     Behold det du vil ta vare på utenfor markørene. -->

## G15 — IBE160 Turnusprosjekt

Beslutningsstøtte for turnusansvarlige som må bemanne én enkelt vakt på nytt: harde
regler filtrerer bort ugyldige kandidater, en enkel modell rangerer de gyldige, og KI
forklarer avveiningene. Gruppeprosjekt i IBE160 ved Høgskolen i Molde, fire medlemmer.
Planlagt stack er React/TypeScript med Vite, Python/FastAPI og SQLite via
SQLAlchemy. KI-leverandøren er OpenRouter med `openai/gpt-6-luna` (valgt 2026-10-16, før det
Haiku 5.5). Appen har et skjelett fra story 1.1 i `backend/` og `frontend/` og
lagring med fiktive testdata fra story 1.2 i `backend/adaptere/lagring/` og
innlogging med designtokens og appskall fra story 1.3, men ingen domenelogikk ennå; `scripts/modelltest_*.py` er isolerte modellforsøk før story 5.1. Planleggingsgrunnlaget er `product-brief.md`
i roten, PRD, UX, arkitektur og epics under `_bmad-output/planning-artifacts/`.

## Policy

- Branch og PR er et aktivt valg den enkelte gjør. Vurder hvor stort arbeidet er, og
  hvor mange definerende avgjørelser det inneholder:
  - Avgrensede endringer som er lette å etterprøve — rettelser, dokumentasjon, små
    tillegg — kan gå rett på `main`. Vi stoler på hverandre, og den enkelte er
    ansvarlig for kvalitetssikringen av eget arbeid.
  - Større eller mer komplekse endringer, eller avgjørelser som binder resten av
    gruppa (datamodell, regelmotor, arkitektur, felles oppsett), bør gå i branch med
    PR, slik at et annet gruppemedlem ser over.
  - Agenter kan foreslå branch eller `main` med en kort begrunnelse, men oppretter
    ikke branch eller PR uten at brukeren har valgt det.
- KI skal aldri beregne harde regler, arbeidstid eller kostnad — de må være
  reproduserbare. KI brukes bare til å tolke tekstbaserte preferanser og forklare
  avveininger mellom kandidater som regelmotoren allerede har godkjent.
- Aldri skriv API-nøkler i kildekode. Les dem fra miljøvariabler, og dokumenter nye
  variabler i `.env.example` uten verdier.
- CI får aldri `OPENROUTER_API_KEY` eller andre hemmeligheter. Tester mot KI-porten
  bruker en falsk OpenRouter, slik at ingen push gir betalte kall.
- Endrer commiten filer fra tidligere arbeid, si i brødteksten hvorfor: snudd
  beslutning, en utsatt avgjørelse som kom til forfall, eller feil oppdaget i
  ettertid. Det står ikke i diffen og kan ikke rekonstrueres senere.
- Måtte generert kode rettes, si i brødteksten hva som var galt. Det er
  dokumentasjonen av kvalitetssikring emnet ber om.
- Uansett vei skal kvalitetssikringen kunne spores: i branch er det PR-gjennomgangen,
  rett på `main` er det commit-meldingen og, for KI-generert kode, KI-loggen.
- Kode generert av KI logges i `docs/ki-logg/<dato>-<tema>.md`: oppgaven, prompten,
  hva modellen leverte, hva som ble rettet og hvorfor, og hvordan resultatet er
  kvalitetssikret. Emnet vurderer denne dokumentasjonen.
- En hard regel i regelmotoren er ikke ferdig før den har tester som dekker
  grensetilfellene. Testene er det sterkeste beviset på kvalitetssikring.
- `bmad-build` kjøres med underagenter: én samler epic-konteksten, og egne agenter
  gjennomgår koden uten å ha sett implementeringen. Det koster mer enn å gjøre alt i
  én økt, men gir en uavhengig gjennomgang. Valgt av Kuduz 2026-10-24 før story 1.2.
  Ikke drøftet i gruppa ennå — er dere uenige, endre dette punktet.

## Hvor ting ligger

- Gjeldende brief: `product-brief.md` i roten. Filen under
  `_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/brief.md`
  er en henvisning til rotfilen — rediger bare `product-brief.md`.
- Lovgrunnlag (aml. kap. 10), emnekrav, kilder og forkastede alternativer:
  `addendum.md` i samme mappe. Les den før du foreslår harde regler.
- Hvorfor noe ble valgt bort: `.memlog.md` i samme mappe.
- Modellvalget: `docs/modelltest-openrouter.md` beskriver testverktøyene. Loggene i
  `docs/ki-logg/` i rekkefølge: Haiku alene (`2026-10-15-modelltest-haiku.md`),
  sammenligning med Luna, Mistral og Gemma (`2026-10-15-modellsammenligning.md`),
  beslutningstest Haiku mot Luna (`2026-10-16-beslutningstest-haiku-luna.md`) og
  robusthetstest av Luna med fasittest mot PRD §4.5 (`2026-10-16-robusthet-luna.md`).
  Luna er valgt. Kravene fra robusthetstesten står i AD-7 i arkitekturen.
- Når et gruppemedlem spør hvordan de får lagt inn API-nøkkelen eller kjører live
  mot Luna: følg skillen `api-nokkel-oppsett` (`.claude/skills/` og `.agents/skills/`).
  Les aldri `.env`.
- Hold `_bmad/`, `.claude/skills/` og `.agents/skills/` utenfor søk i prosjektkoden —
  det er BMAD-rammeverket og utgjør 446 av 455 sporede filer.

## Kjøring og verifisering

- Modellforsøket er kjørt med Python 3.12.5 og standardbiblioteket, uten installasjon.
  Fra roten: `python scripts/modelltest_openrouter.py` er tørrkjøring;
  `python -m unittest discover -s scripts -p "test_modelltest*.py"` tester verktøyet;
  `python scripts/modelltest_openrouter.py --live` gjør 32 betalte OpenRouter-kall.
  Live krever `OPENROUTER_API_KEY` i miljøet eller lokal `.env`. Les testveiledningen
  før kjøring. Exit 0 gjelder maskinkontrollen, ikke manuell vurdering av norsk/fakta.
- Beslutningstesten: `python scripts/modelltest_beslutning.py` er tørrkjøring;
  `--live --model <modell> --prompt A|B` gjør 255 betalte kall per kjøring (tak USD 0,25);
  `--analyse` regenererer tabellene i `docs/ki-logg/beslutningstest/` uten nettverk.
  Testene dekkes av samme `unittest`-kommando.
- Robusthets- og fasittesten: `python scripts/modelltest_robusthet.py --live --politikk takt`
  (218 kall, ca. 25 min) og `python scripts/modelltest_prd_fasit.py --live` (145 kall).
  Uten `--live` er begge tørrkjøring.
- Regneeksemplene bak taket på 300 Ulempepoeng (PRD §4.3):
  `python scripts/ulempe_regneeksempler.py`, uten nettverk. `--vakttider 2026-10-30`
  gjenskaper tallene fra før gruppa valgte vakttidene 2026-11-02.
- Backend (Python 3.12 eller nyere), fra `backend/`. På macOS/Linux er stien
  `.venv/bin/python` i stedet for `.venv\Scripts\python`:
  1. Installasjon: `python -m venv .venv` og deretter
     `.venv\Scripts\python -m pip install -r requirements-dev.txt`.
  2. Testdata: `.venv\Scripts\python -m adaptere.lagring.testdata` tømmer og fyller
     de fire tabellene `bruker`, `turnus`, `vakt` og `ansatt` i én transaksjon og kan
     kjøres flere ganger. Turnusansvarlig er `kari.vestby`. Med
     `TURNUSHJELPEREN_PASSORD` satt i terminalen er passordet personlig og skrives ikke
     ut. Uten den lages et tilfeldig testpassord som skrives ut og gjelder til neste
     kjøring. Den siste linjen i utskriften sier hvilken variant som gjelder. Backend
     leser ikke `.env`. Databasen er `backend/turnushjelperen.db` (gitignorert), eller
     stien i `TURNUSHJELPEREN_DB`. Det finnes ikke noe migreringsverktøy: endres skjemaet
     i `adaptere/lagring/modeller.py`, slett databasefilen og kjør kommandoen på nytt.
     Nye tabeller legges til av `create_all` uten sletting.
  3. Kjøring: `.venv\Scripts\python -m uvicorn adaptere.api.main:app --reload`. Svarer
     på `http://127.0.0.1:8000/api/helse`. JWT-nøkkelen lages ved hver oppstart, så alle
     logges ut ved omstart, også ved `--reload`. `TURNUSHJELPEREN_JWT_MINUTTER`
     (standard 480) må være et positivt heltall, ellers starter ikke API-et.
  - Test: `.venv\Scripts\python -m pytest`. Testene bygger appen med `lag_app` mot en
    database i `tmp_path` og rører ikke `backend/turnushjelperen.db`.
- Frontend (Node 20.19 eller nyere), fra `frontend/` i en egen terminal mens backend
  kjører: `npm install`, deretter `npm run dev` (http://localhost:5173). Vite sender
  `/api` videre til `http://127.0.0.1:8000`. `npm run build` typesjekker og bygger.
  Rå størrelser og fargekoder står bare i `frontend/src/stil/tokens.css` (AV-13).
- CI kjører tre workflows på hver push til alle brancher, på Linux:
  - `.github/workflows/skills-speiling.yml`: speilingstesten for skills. Lokalt:
    `python -m unittest discover -s scripts -p "test_skills*.py"`.
  - `.github/workflows/backend-tester.yml`: `pytest` i `backend/` med Python 3.12
    (laveste versjon vi lover) og nyeste stabile 3.x. Det er den eneste kjøringen
    utenfor Windows (OP-05). Rød 3.x med grønn 3.12 er som regel versjonsdrift og rettes
    som vanlig vedlikehold, oftest ved å oppdatere en pakkelås.
  - `.github/workflows/frontend-tester.yml`: `npm ci`, `npm run build` og `npm run test`
    i `frontend/` med Node 20.19 (laveste versjon vi lover) og nyeste Node. Samme regel
    for versjonsdrift som for backend.
  - CI dekker ikke testene av modellverktøyene i `scripts/` eller manuell test. Grønn CI
    er ikke det samme som gjennomgått kode.
  - Rød CI blokkerer ikke merge, og `main` har ingen branchebeskyttelse. Det er et valg:
    den som merger, ser resultatet i PR-en og tar ansvaret (Policy).
- Ferdige, testede spørringer for å hente ut KI-dokumentasjonen ved innlevering
  ligger i `docs/ki-logg/README.md`. Ikke skriv dem på nytt.

## Konvensjoner som avviker fra standard

- Dokumentasjon, commit-meldinger og brukergrensesnitt skrives på norsk bokmål. Kode,
  kodekommentarer og tekniske termer kan være på engelsk der det er mer presist.
- `.claude/skills/` (Claude Code) og `.agents/skills/` (Codex) er samme innhold for to
  harnesses, begge sporet med vilje slik at agentoppsettet følger repoet. Endrer du en
  skill eller en `customize.toml` i den ene, speil endringen i den andre.
  `scripts/test_skills_speiling.py` kontrollerer dette, også i CI. Et nytt unntak må
  inn i `POINTERS` i testen.
- Oppsett som skal gjelde hele gruppa må ligge i sporede filer.
  `_bmad/config.user.toml`, `_bmad/custom/*.user.toml` og `.claude/settings.local.json`
  er gitignorerte og gjelder bare din maskin.
- Koden skal virke på tvers av operativsystem: `pathlib` for stier, eksplisitt
  `encoding="utf-8"` ved lesing, skriving og underprosesser, og ingen kall eller
  kommandoer som bare finnes på Windows. README viser både PowerShell og bash. Fysisk
  test skjer bare på Windows, fordi verken sensor eller noen i gruppa har Mac (OP-05,
  2026-11-07). Bash-kommandoer kontrolleres i Git Bash.

## Kjente fallgruver

- `.agents/`-kopien har CRLF i arbeidstreet, `.claude/`-kopien har LF. Sammenlign dem
  med linjeskift ignorert — `diff <(tr -d '\r' < a) <(tr -d '\r' < b)` — ellers ser
  alle de identiske filene ut som endret.
- Gruppens OpenRouter-konto har en grense på 20 Luna-kall per kalenderminutt
  (`limit_source: openrouter_new_account`). Kjør ikke flere live-tester samtidig, og
  regn med 429 uten begrenseren i AD-7. Haiku hadde ikke denne grensen.
- I Windows PowerShell med standardpolicyen stoppes `npm` med `UnauthorizedAccess`
  («running scripts is disabled»), fordi `npm` der er skriptet `npm.ps1`. Bruk
  `npm.cmd install` og `npm.cmd run dev`. Funnet av Johannes 2026-11-07 ved den
  manuelle testen av story 1.3. Det gjelder trolig flere i gruppa. README-steg 4 sier
  det samme.

<!-- /bmad:context -->

## Gruppevedtak og avklaringspunkter

- Prosjektets beslutningsreferat ligger i
  [docs/beslutninger/avklaringspunkter.md](docs/beslutninger/avklaringspunkter.md).
  Les relevante punkter før planlegging, implementering eller kvalitetssikring
  som berører dokumentets temaer, særlig seeddata, vakttyper, tidsberegning,
  hvilekontroll, rangering, ulempbelastning, KI-kontrakter og UX.

- Bruk referatet sammen med produktbrief, PRD, arkitektur og aktuelle stories.
  Skill mellom vedtatte beslutninger, anbefalinger, åpne spørsmål og kontroller
  som gjenstår. Et vedtak om å utføre en kontroll betyr ikke at kontrollen er utført.

- Ved motstrid mellom referatet og andre styrende filer: oppgi beslutnings-ID,
  berørte filer og hva som avviker. Foreslå en konkret løsning og be om avklaring
  før arbeid som avhenger av konflikten. Fortsett arbeid som ikke berøres.

- Henvis til relevante beslutnings-ID-er (AV-, K-, OP- og KS-) i stories,
  PR-er og dokumentasjon når de begrunner arbeidet. Ikke kopier hele referatet.

- Referatet erstatter ikke eksisterende agentinstruksjoner, loggregler,
  tester eller godkjenningskrav. Ikke marker punkter som løst eller stories
  som ferdige uten dokumentert grunnlag.

## Sesjonslogg

- Bruk `sesjonslogg` før sluttoppsummeringen for hver fullført oppgave som endrer
  kode, dokumentasjon, konfigurasjon eller data. Oppgavens størrelse avgjør ikke om
  den skal logges. Rene git-operasjoner (commit, pull, fetch, push, merge, brancher)
  logges ikke — de står i git-historikken (AV-08, oppdatert 2026-11-06).
- Logg også undersøkelser uten tilstandsendringer når de gir viktige funn,
  beslutninger eller oppfølgingspunkter for prosjektet. Rene faktaspørsmål uten
  endringer eller noe å ta vare på trenger ikke logg. Denne avgrensningen gjelder
  også dersom skillbeskrivelsen bare nevner tilstandsendringer.
- I lengre oppgaver: opprett eller oppdater loggen ved første vesentlige milepæl,
  og oppdater den ved senere milepæler, slik at utført arbeid er dokumentert dersom
  økten avbrytes.
- Før sluttsvaret: kontroller at loggen beskriver oppgaven, faktisk fremgangsmåte,
  resultat og kvalitetssikring, og at nye og løste oppfølgingspunkter er ført i
  `.logs/<bruker>/issues.md`. Skriv «Ingen.» ved ingen åpne punkter. Sesjonsloggen
  erstatter ikke kravene til KI-dokumentasjon i `docs/ki-logg/`.
- Commit loggfilene etter skillens fremgangsmåte. Push bare når brukeren har bedt
  om det; en lokal commit deler ikke loggen med gruppa.
- Et uttrykkelig forbud fra brukeren mot filendringer eller commits går foran
  loggkravet. Hvis det eller en teknisk hindring stopper logging eller commit,
  opplys konkret om hva som ikke ble lagret eller committet i sluttsvaret.
- For denne skillen er `.claude/skills/sesjonslogg/SKILL.md` autoritativ.
  `.agents/skills/sesjonslogg/SKILL.md` inneholder bare metadata og en henvisning,
  som et unntak fra speilingsregelen over. Ved endret navn eller bruksområde må
  metadataene i henvisningsfilen også oppdateres.

## Sensorveiledning og vurderingsgrunnlag

- Les `docs/emne/sensorveiledning-del-1.md` før planlegging,
  implementering og kvalitetssikring. PDF-en i samme mappe er originalkilden.
- Bruk kriteriene til å prioritere og kvalitetssikre arbeidet.
  Oppdater vurderingsmatrisen ved milepæler med lenker til faktiske bevis.
- Koble implementerte krav til stories, PR-er, tester og KI-logger.
  Begrunn avvik fra godkjent proposal og gjeldende plan.
- Hvis vurderingsgrunnlaget ikke kan leses, opplys om dette før
  vurderinger som avhenger av det.
