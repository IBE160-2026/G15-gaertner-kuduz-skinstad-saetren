# Sjekkliste: live KI for sensor (story 5.8)

> **Status:** utkast 2026-11-23, skrevet av Claude Code for Ragnhild Sætren. Oppgavene er
> utsatt til nær innleveringsfristen
> ([deferred-work.md](../../_bmad-output/implementation-artifacts/deferred-work.md),
> 2026-11-23). ÅB-8 ble avgjort 2026-11-28: sensor får den felles utviklingsnøkkelen (AV-21 i
> [avklaringspunktene](../beslutninger/avklaringspunkter.md)). De andre punktene er ikke
> gjennomført. Sensor følger
> [README: KI: demo-modus eller live](../../README.md#ki-demo-modus-eller-live), og
> nøkkelen settes i terminalen (AV-20 i
> [avklaringspunktene](../beslutninger/avklaringspunkter.md)).

Skriv navn i «Ansvarlig» når noen tar et punkt, og kryss av når det er gjort. Ingen
nøkkel, nøkkelprefiks utover `sk-or-v1-…` eller kredittbeløp skal inn i denne filen.

## Før innlevering

- [x] **Avgjør ÅB-8.** Hele gruppa velger ut fra forbruket i OpenRouters
  aktivitetsoversikt. Ansvarlig: Johannes W. Gaertner, på vegne av gruppa.
  - **Avgjort 2026-11-28 (AV-21): utfall 1.** Sensor får den felles utviklingsnøkkelen,
    som har egen kredittgrense. Gruppa hadde brukt omtrent USD 0,2 så langt. Johannes
    eier nøkkelen og sender den til sensor på e-post og i direktemelding i Teams, i
    tillegg til innleveringsteksten. Utviklingsbruken på nøkkelen stopper ved innlevering.
  - Grunnlag: én kjøring hos sensor gir opptil 19 tolkekall hver gang backend startes
    med nøkkel (alle 19 etter at testdataene er lastet), og ett kall per forklaring som
    åpnes. Kostnaden per kall leses i aktivitetsoversikten.
  - Utfall 1, den felles utviklingsnøkkelen: sjekk at kreditten holder for sensor.
    Utviklingsbruken på nøkkelen stopper ved innlevering, og nøkkelen byttes etter
    sensur.
  - Utfall 2, en egen sensornøkkel: lag den i OpenRouter med kredittgrense.
  - Før valget inn i [avklaringspunktene](../beslutninger/avklaringspunkter.md).
- [ ] **Sjekk git-historikken for nøkler.** Ansvarlig: ______ Kjør fra roten av
  repoet, på innleveringscommiten. Kommandoene er like i PowerShell og bash:

  ```
  git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"
  git log --all -m --text --oneline -E -G "sk-or-v1-[0-9a-f]{32}"
  git log --all --oneline -E --grep "sk-or-v1-[0-9a-f]{32}"
  ```

  Den første henter commitene fra alle PR-er på GitHub, også de som ikke er merget. Den
  andre finner commits som legger til eller fjerner en nøkkel i en fil, i alle brancher,
  også i merge-commits og binærfiler. Den tredje finner en nøkkel i commit-meldingene.
  Ingen utskrift betyr ingen treff. De falske nøklene i testene (`sk-or-v1-fake-…`) gir
  ikke treff. Noter resultatet her: dato ______, commit ______, resultat ______.

  Gir en av kommandoene treff, er nøkkelen lekket selv om den er slettet senere. Bytt den i
  OpenRouter med en gang, og si fra til gruppa før noe annet.
- [ ] **Sjekk at ingen `.env` er sporet.** `git ls-files` skal ikke vise noen fil som
  heter `.env`. `.env.example` er ment å være sporet. Ansvarlig: ______
- [ ] **Test fra en ren klone, bare etter README.** Én person kloner repoet til en ny
  mappe og følger README fra steg 1 uten annen hjelp. Bruk Windows med PowerShell hvis
  mulig, fordi sensor ikke har Mac (OP-05). Ansvarlig: ______
  - Demo-modus: start backend uten nøkkel. Appbaren viser «Demo-modus», og #4127 viser
    forklaringer merket «Forhåndsgenerert KI-forklaring».
  - Live: sett sensornøkkelen etter README og start backend i samme terminal. Appbaren
    viser ikke «Demo-modus», og forklaringene merkes «KI-generert · openai/gpt-6-luna».
    Begge deler må stemme: uten KI i det hele tatt mangler også demomerket.
  - Noter dato, operativsystem, commit og avvik fra README her: ______

## I innleveringsteksten

- [ ] **Lim inn teksten under, med nøkkelen.** Nøkkelen står i innleveringsteksten og
  sendes i tillegg til sensor på e-post og i direktemelding i Teams, aldri i repoet
  (AV-21). Ansvarlig: Johannes W. Gaertner
- [ ] **Navngi den som bytter nøkkelen etter sensur**, i teksten under. Det er Johannes
  W. Gaertner (AV-21). Ansvarlig: Johannes W. Gaertner

> **Kjøring og innlogging.** Start appen etter [README: Kom i gang](../../README.md#kom-i-gang).
> Logg inn som `kari.vestby`. Passordet velger du selv i steg 2, variant A. Det står
> ikke noe passord i repoet.
>
> **Live KI.** Appen kan kjøres uten nøkkel i demo-modus. For live KI mot OpenRouter
> bruker du denne nøkkelen: `<nøkkel settes inn ved innlevering>`. Den er også sendt
> deg på e-post og i Teams. Sett den som
> `OPENROUTER_API_KEY` i samme terminal som du starter backend fra, slik
> [README](../../README.md#ki-demo-modus-eller-live) viser. Backend leser ikke `.env`.
> Live er aktiv når appbaren ikke viser «Demo-modus», og forklaringene merkes
> «KI-generert · openai/gpt-6-luna». Er kreditten brukt opp, viser appen
> reservetekst i stedet for KI-forklaringer, og resten virker som før. Nøkkelen byttes
> etter sensur. Ansvarlig for det: Johannes W. Gaertner.

## Etter sensur

- [ ] **Bytt utviklingsnøkkelen i OpenRouter** (utfall 1, AV-21). Ansvarlig: Johannes
  W. Gaertner
