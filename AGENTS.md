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
SQLAlchemy. KI-leverandøren er OpenRouter med `anthropic/claude-haiku-5.5`.
Ingen applikasjonskode finnes ennå; `scripts/modelltest_openrouter.py` er et
isolert modellforsøk før story 5.1. Planleggingsgrunnlaget er `product-brief.md`
i roten, PRD, UX, arkitektur og epics under `_bmad-output/planning-artifacts/`.

## Policy

- Utvidelser av funksjonalitet går i egen branch. Småendringer går rett på `main`
  inntil gruppa bestemmer noe annet.
- KI skal aldri beregne harde regler, arbeidstid eller kostnad — de må være
  reproduserbare. KI brukes bare til å tolke tekstbaserte preferanser og forklare
  avveininger mellom kandidater som regelmotoren allerede har godkjent.
- Aldri skriv API-nøkler i kildekode. Les dem fra miljøvariabler, og dokumenter nye
  variabler i `.env.example` uten verdier.
- Endrer commiten filer fra tidligere arbeid, si i brødteksten hvorfor: snudd
  beslutning, en utsatt avgjørelse som kom til forfall, eller feil oppdaget i
  ettertid. Det står ikke i diffen og kan ikke rekonstrueres senere.
- Måtte generert kode rettes, si i brødteksten hva som var galt. Det er
  dokumentasjonen av kvalitetssikring emnet ber om.
- Går arbeidet i branch, er PR-gjennomgangen kvalitetssikringen. Den enkelte er
  ansvarlig for gjennomgangen av eget arbeid.
- Kode generert av KI logges i `docs/ki-logg/<dato>-<tema>.md`: oppgaven, prompten,
  hva modellen leverte, hva som ble rettet og hvorfor, og hvordan resultatet er
  kvalitetssikret. Emnet vurderer denne dokumentasjonen.
- En hard regel i regelmotoren er ikke ferdig før den har tester som dekker
  grensetilfellene. Testene er det sterkeste beviset på kvalitetssikring.

## Hvor ting ligger

- Gjeldende brief: `product-brief.md` i roten. Filen under
  `_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/brief.md`
  er en henvisning til rotfilen — rediger bare `product-brief.md`.
- Lovgrunnlag (aml. kap. 10), emnekrav, kilder og forkastede alternativer:
  `addendum.md` i samme mappe. Les den før du foreslår harde regler.
- Hvorfor noe ble valgt bort: `.memlog.md` i samme mappe.
- Modelltest: `docs/modelltest-openrouter.md` beskriver kjøring og vurdering;
  resultater og begrensninger dokumenteres i `docs/ki-logg/2026-10-15-modelltest-haiku.md`.
  Sammenligning med Luna og Gemma (Mistral ikke testet, HTTP 429):
  `docs/ki-logg/2026-10-15-modellsammenligning.md` har resultat, konklusjon og hva som gjenstår.
- Hold `_bmad/`, `.claude/skills/` og `.agents/skills/` utenfor søk i prosjektkoden —
  det er BMAD-rammeverket og utgjør 446 av 455 sporede filer.

## Kjøring og verifisering

- Modellforsøket er kjørt med Python 3.12.5 og standardbiblioteket, uten installasjon.
  Fra roten: `python scripts/modelltest_openrouter.py` er tørrkjøring;
  `python -m unittest discover -s scripts -p "test_modelltest*.py"` tester verktøyet;
  `python scripts/modelltest_openrouter.py --live` gjør 32 betalte OpenRouter-kall.
  Live krever `OPENROUTER_API_KEY` i miljøet eller lokal `.env`. Les testveiledningen
  før kjøring. Exit 0 gjelder maskinkontrollen, ikke manuell vurdering av norsk/fakta.
- TODO — appen er ikke implementert. Når `package.json` og Python-prosjektfilen
  finnes, fyll inn faktiske kommandoer for installasjon, kjøring og test av appen.
- TODO — ingen CI. Legger dere til `.github/workflows/`, noter her hva CI kjører som
  de lokale kommandoene ikke dekker.
- Ferdige, testede spørringer for å hente ut KI-dokumentasjonen ved innlevering
  ligger i `docs/ki-logg/README.md`. Ikke skriv dem på nytt.

## Konvensjoner som avviker fra standard

- Dokumentasjon, commit-meldinger og brukergrensesnitt skrives på norsk bokmål. Kode,
  kodekommentarer og tekniske termer kan være på engelsk der det er mer presist.
- `.claude/skills/` (Claude Code) og `.agents/skills/` (Codex) er samme innhold for to
  harnesses, begge sporet med vilje slik at agentoppsettet følger repoet. Endrer du en
  skill eller en `customize.toml` i den ene, speil endringen i den andre.
- Oppsett som skal gjelde hele gruppa må ligge i sporede filer.
  `_bmad/config.user.toml`, `_bmad/custom/*.user.toml` og `.claude/settings.local.json`
  er gitignorerte og gjelder bare din maskin.

## Kjente fallgruver

- `.agents/`-kopien har CRLF i arbeidstreet, `.claude/`-kopien har LF. Sammenlign dem
  med linjeskift ignorert — `diff <(tr -d '\r' < a) <(tr -d '\r' < b)` — ellers ser
  alle 214 identiske filer ut som endret.

<!-- /bmad:context -->

## Sensorveiledning og vurderingsgrunnlag

- Les `docs/emne/sensorveiledning-del-1.md` før planlegging,
  implementering og kvalitetssikring. PDF-en i samme mappe er originalkilden.
- Bruk kriteriene til å prioritere og kvalitetssikre arbeidet.
  Oppdater vurderingsmatrisen ved milepæler med lenker til faktiske bevis.
- Koble implementerte krav til stories, PR-er, tester og KI-logger.
  Begrunn avvik fra godkjent proposal og gjeldende plan.
- Hvis vurderingsgrunnlaget ikke kan leses, opplys om dette før
  vurderinger som avhenger av det.
