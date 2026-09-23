<!-- bmad:context -->
<!-- Verifisert 2026-09-23 mot f9a45f0. Vedlikeholdes av bmad-project-context;
     endringer inne i denne blokka blir erstattet ved refresh.
     Behold det du vil ta vare på utenfor markørene. -->

## G15 — IBE160 Turnusprosjekt

Beslutningsstøtte for turnusansvarlige som må bemanne én enkelt vakt på nytt: harde
regler filtrerer bort ugyldige kandidater, en enkel modell rangerer de gyldige, og KI
forklarer avveiningene. Gruppeprosjekt i IBE160 ved Høgskolen i Molde, fire medlemmer.
Stacken er besluttet på overordnet nivå — JavaScript frontend, Python backend — men
rammeverk er ikke valgt, og ingen applikasjonskode finnes ennå. Planleggingsgrunnlaget
er `product-brief.md` i roten.

## Policy

- Utvidelser av funksjonalitet går i egen branch. Småendringer går rett på `main`
  inntil gruppa bestemmer noe annet.
- KI skal aldri beregne harde regler, arbeidstid eller kostnad — de må være
  reproduserbare. KI brukes bare til å tolke tekstbaserte preferanser og forklare
  avveininger mellom kandidater som regelmotoren allerede har godkjent.
- Aldri skriv API-nøkler i kildekode. Les dem fra miljøvariabler, og dokumenter nye
  variabler i `.env.example` uten verdier.

## Hvor ting ligger

- Gjeldende brief: `product-brief.md` i roten. Kopien under
  `_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/brief.md`
  er identisk — rediger roten, ikke kopien.
- Lovgrunnlag (aml. kap. 10), emnekrav, kilder og forkastede alternativer:
  `addendum.md` i samme mappe. Les den før du foreslår harde regler.
- Hvorfor noe ble valgt bort: `.memlog.md` i samme mappe.
- Hold `_bmad/`, `.claude/skills/` og `.agents/skills/` utenfor søk i prosjektkoden —
  det er BMAD-rammeverket og utgjør 446 av 455 sporede filer.

## Kjøring og verifisering

- TODO — ingen kode ennå. Når `package.json` og Python-prosjektfilen finnes, fyll inn
  de faktiske kommandoene for installasjon, kjøring og test her. Ikke gjett dem.
- TODO — ingen CI. Legger dere til `.github/workflows/`, noter her hva CI kjører som
  de lokale kommandoene ikke dekker.

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
