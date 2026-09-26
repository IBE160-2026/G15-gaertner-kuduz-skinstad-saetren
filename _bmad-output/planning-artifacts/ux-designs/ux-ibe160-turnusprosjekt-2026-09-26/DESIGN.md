---
title: "DESIGN: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-09-26
name: Turnushjelperen
description: Beslutningsstøtte-fagsystem for turnusansvarlig — tett, klinisk, navy/grå. Ikke et konsumentprodukt, ikke dark-mode-først.
colors:
  bg-app: '#eef1f4'
  bg-panel: '#ffffff'
  bg-header: '#16324a'
  border: '#c7d0d9'
  text-main: '#1b2733'
  text-mute: '#5b6b7a'
  accent: '#16324a'
  ok: '#1f7a4d'
  warn: '#a15a00'
  danger: '#8c2f2f'
  row-alt: '#f5f7f9'
  tag-bg: '#e7ecf1'
typography:
  brand:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 14.5px
    fontWeight: '700'
    letterSpacing: 0.3px
  heading:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 15px
    fontWeight: '700'
  section-label:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 12px
    fontWeight: '700'
    letterSpacing: 0.5px
  column-header:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 10.5px
    fontWeight: '700'
    letterSpacing: 0.4px
  body:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 12.5px
    fontWeight: '400'
    lineHeight: '1.55'
  meta:
    fontFamily: 'Segoe UI, Arial, sans-serif'
    fontSize: 11px
    fontWeight: '400'
rounded:
  sm: 3px
  DEFAULT: 4px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 22px
  '6': 32px
  content-padding: 22px
  row-padding: 9px 12px
components:
  appbar:
    background: '{colors.bg-header}'
    foreground: '#ffffff'
  table:
    background: '{colors.bg-panel}'
    border: '{colors.border}'
    radius: '{rounded.DEFAULT}'
    rowAltBackground: '{colors.row-alt}'
    columnHeaderBackground: '#f0f3f6'
  rank-badge:
    color: '{colors.accent}'
    fontWeight: '700'
  workload-bar:
    track: '#e2e7ec'
    fill-normal: '{colors.accent}'
    fill-warn: '{colors.warn}'
    warnThreshold: '~90%'
    radius: '{rounded.sm}'
  cost-indicator:
    ordinary: '{colors.ok}'
    overtime: '{colors.warn}'
    neverUses: '{colors.danger}'
  tag:
    background: '{colors.tag-bg}'
    border: '{colors.border}'
    radius: '{rounded.sm}'
  explain-panel:
    background: '#f2f6f9'
    labelColor: '{colors.accent}'
    up: '{colors.ok}'
    down: '{colors.danger}'
    radius: '{rounded.sm}'
  excluded-box:
    border: 'dashed 1px {colors.border}'
    background: '#f7f9fb'
    radius: '{rounded.DEFAULT}'
  alert-box:
    background: '{colors.bg-panel}'
    borderLeft: '4px solid {colors.danger}'
    border: '{colors.border}'
    radius: '{rounded.DEFAULT}'
  empty-state:
    background: '{colors.bg-panel}'
    border: '{colors.border}'
    radius: '{rounded.DEFAULT}'
    iconBackground: '#f3e3e3'
    iconColor: '{colors.danger}'
    iconRadius: '{rounded.full}'
  deviation-note:
    border: 'dashed 1px {colors.border}'
    background: '#f7f9fb'
    labelColor: '{colors.accent}'
    radius: '{rounded.DEFAULT}'
  button-primary:
    background: '{colors.accent}'
    foreground: '#ffffff'
    radius: '{rounded.sm}'
  button-secondary:
    background: '#ffffff'
    foreground: '{colors.text-main}'
    border: '{colors.border}'
    radius: '{rounded.sm}'
  login-card:
    background: '{colors.bg-panel}'
    border: '{colors.border}'
    radius: '{rounded.DEFAULT}'
  confirm-box:
    background: '{colors.bg-panel}'
    border: '{colors.border}'
    radius: '{rounded.DEFAULT}'
---

## Brand & Style

Turnushjelperen er et **fagsystem, ikke et konsumentprodukt**. Turnusansvarlig bruker det under tidspress — en vakt mangler bemanning *nå* — og trenger maksimal informasjonstetthet uten omveier: nøkkeltall synlig direkte i raden, ingen ekstra klikk for det som betyr noe. Den visuelle registeren er tett, klinisk og nøktern: tabellform fremfor kort, skarpe kanter fremfor myke, en navy/grå palett fremfor varme eller lekne farger.

Retningen (`mockups/direction-a-fagsystem.html`) ble valgt over to bygde og forkastede alternativer — «rolig/human» (`.working/direction-b-rolig.html`) og «forklaringsdrevet» mørk tech (`.working/direction-c-forklaring.html`) — se `.memlog.md` for full begrunnelse.

To designprinsipper følger direkte av dette:
1. **Tetthet som forblir skannbar** — en tabellrad viser rangering, kompetanse, kostnad og arbeidsbelastning samtidig, uten at brukeren må åpne noe.
2. **Progressiv visning av Avveining** (KI-begrunnelse) — den øverste/anbefalte kandidatens Avveining er utvidet som standard; øvrige er kollapset bak «Vis begrunnelse ▾». Avveiningen er alltid tilgjengelig, aldri påtvunget.

Ingen dark-mode-først (dette er et arbeidsverktøy brukt i dagslys på en arbeidsplass, ikke en kveldsapp). Ingen gamification, ingen chat-bobler, ingen lekne ikoner.

## Colors

Paletten er bevisst begrenset og nøktern — fargen skal bære mening (status, kostnadstype, alvorlighetsgrad), aldri dekorasjon.

- **`bg-header` (`#16324a`, marineblå)** er samtidig `accent` — brukt på topplinjen (appbar), primærknapper, rangeringstall og lenker. Ett mørkt, tillitvekkende navy signaliserer «pålitelig fagsystem».
- **`bg-app` (`#eef1f4`)** er den kjølige, lyse bakgrunnen bak innholdet — aldri ren hvit, for å skille appflaten fra panelene som ligger oppå den.
- **`bg-panel` (`#ffffff`)** er panel-, tabell- og kortbakgrunn — alt "innhold" ligger på ren hvit for kontrast mot `bg-app`.
- **`text-main` (`#1b2733`)** og **`text-mute` (`#5b6b7a`)** er primær og sekundær tekst. Ingen ren svart — samme nøkternt kjølige register som resten av paletten.
- **`ok` (`#1f7a4d`, grønn)** betyr **ordinær sats** i kostnadsvisning. Betyr aldri "suksess"-melding eller ferdig-status generelt — bruken er avgrenset til kostnadstype.
- **`warn` (`#a15a00`, oker/brun)** betyr **overtid** i kostnadsvisning, og **høy arbeidsbelastning** (terskel ca. 90 %+) i arbeidsbelastningslinjen. Dette er en bevisst beslutning: overtid og høy belastning er *dyrere/tyngre*, ikke *feil* — rødt ville feilaktig signalisere en feiltilstand for noe som er et gyldig, om enn kostbart, valg.
- **`danger` (`#8c2f2f`, rødt)** er reservert for faktiske utelukkelser og tomme/manko-tilstander: ikonet i "ingen gyldige kandidater", "trekker ned"-punkter i Avveiningen, og varsel-ikonet for en vakt som mangler bemanning. Rødt brukes **aldri** for overtid eller kostnad — se over.
- **`row-alt` (`#f5f7f9`)** er annenhver rad i tabeller, for lesbarhet i tette lister.
- **`tag-bg` (`#e7ecf1`)** er bakgrunnen for kompetanse- og preferanse-tags — nøytral, informativ, ikke statusbærende.

Unngå: rødt for overtid/høy belastning (skal alltid være `warn`, aldri `danger`), gradienter, flere farger enn de som er listet over, og enhver dekorativ bruk av `accent` utover navigasjon/handling/rangering.

## Typography

Systemfont (`Segoe UI, Arial, sans-serif`) — ingen egen merkevarefont. Dette er et internt fagverktøy; typografisk identitet kommer fra hierarki og tetthet, ikke fra en signaturfont.

Rollene er tettere trappet enn i et konsumentprodukt, fordi flaten skal romme mye informasjon:

- **`brand`** (14,5px/700) — kun i appbar-logoen "TURNUSHJELPEREN".
- **`heading`** (15px/700) — vaktoverskrifter, kandidatnavn i godkjenningsvisningen, kortoverskrifter.
- **`section-label`** (12px/700, versaler, 0,5px sporing) — seksjonsoverskrifter som "Rangerte kandidater", "Krever handling".
- **`column-header`** (10,5px/700, versaler, 0,4px sporing) — tabellens kolonneoverskrifter.
- **`body`** (12,5px/400) — tabellinnhold, Avveining (KI-begrunnelse), brødtekst i bokser.
- **`meta`** (11px/400, `text-mute`) — undertekst under navn (stilling/ansiennitet), tidsstempler, fotnoter.

Ingen kursiv, ingen display-størrelser. Fet vekt (700) brukes til navn, tall og seksjonsoverskrifter — aldri til lange avsnitt.

## Layout & Spacing

Skala: 4 / 8 / 12 / 16 / 22 / 32px. Innholdspolstring (`content-padding`, 22px) er fast for hovedflaten; tabellrader bruker en tettere `row-padding` (9px 12px) for å holde den tettheten som «Retning A» ble valgt for.

Layouten er én kolonne av tett stablede seksjoner (varselboks → seksjonsoverskrift → tabell → ekskludert-boks → fotnote), ikke et flerkolonne-dashbord. Brødsmulesti (`Turnus > Avdeling > Vakt`) ligger fast øverst under appbar på alle skjermer etter innlogging, som fast stedsforankring i en tett flate.

**[ASSUMPTION]** Eksakte breakpoints for mobil/nettbrett-tilpasning er ikke bestemt i noen av kildene (mockupene, f.eks. `mockups/direction-a-fagsystem.html`, viser kun en fast desktop-bredde på 1180px) — se EXPERIENCE.md § Responsive & Platform for hvordan tabelltettheten foreslås tilpasset smalere flater.

## Elevation & Depth

Flaten er flat med utstrakt bruk av 1px kantlinjer (`{colors.border}`) i stedet for skygge — konsistent med fagsystem-registeret: skygge signaliserer "svevende, lekent UI-lag", kantlinje signalerer "tabellrad, fast struktur". Eneste skygge i mockupene (`mockups/direction-a-fagsystem.html` og de tre `key-*.html`-skjermene) ligger på den ytre nettleser-rammen (presentasjonsartefakt for mockup-visning) og er **ikke** en del av selve produktets UI.

Paneler skilles fra appflaten (`bg-app`) utelukkende via flatfarge (`bg-panel`) og kantlinje — aldri via skygge eller elevasjon som hierarki-signal.

## Shapes

To trinn, begge små — dette er ikke et rundet, konsumentaktig UI:
- **`rounded/sm` (3px)** — knapper, inputfelt, tags.
- **`rounded/DEFAULT` (4px)** — paneler, kort, tabeller, bokser (vaktboks, ekskludert-boks, tomtilstand, bekreftelsesboks).
- **`rounded/full`** — kun for de sirkulære ikonbakgrunnene i varsel- og tomtilstand-ikonet (`!`).

Ingen pille-former, ingen store radiuser. Skarpheten er bevisst — den signaliserer "presist verktøy", ikke "vennlig app".

## Components

- **Appbar** — `{colors.bg-header}` bakgrunn, hvit tekst. Venstre: produktnavn (`brand`-typografi). Høyre: innlogget bruker + avdeling, eller "Ikke innlogget" på innloggingssiden. Atferd (hva som vises pre-/post-innlogging) er spesifisert i EXPERIENCE.md § Component Patterns, ikke her — denne raden er kun visuell.
- **Rangeringstabell** — Kolonner: rangeringsnummer, kandidat (navn + `meta`), Kompetansenivå (+ tag), kostnad (fargekodet), arbeidsbelastning (tall + linje), preferanse (tag), ekspander-lenke. `row-alt` på annenhver rad. Se `mockups/direction-a-fagsystem.html`.
- **Rangeringsnummer (`rank-badge`)** — `{colors.accent}`, fet, 14px — det første tallet blikket skal lande på i raden.
- **Arbeidsbelastningslinje** — 110×7px linje. Fylles med `{colors.accent}` under terskelen (~90 %), bytter til `{colors.warn}` ved og over terskelen. Aldri rødt.
- **Kostnadsindikator** — Tekst "Ordinær" i `{colors.ok}` eller "Overtid" i `{colors.warn}`, med kr/t under i `meta`.
- **Tag** — `{colors.tag-bg}` bakgrunn, `{rounded.sm}`, nøytral informasjon (kompetansenivå-tekst, preferanse som "Ønsker flere vakter", "Fleksibel", "Ingen registrert").
- **Forklaringsrad/-panel (`explain-panel`)** — Utvides under kandidatraden (tabell) eller som eget panel i kandidatkortet (godkjenning). Lyseblå bakgrunn (`#f2f6f9`) skiller den fra resten av tabellen/kortet. "▲ Trekker opp" i `{colors.ok}`, "▼ Trekker ned" i `{colors.danger}`. Atferd (hvilket panel er utvidet som standard) er spesifisert i EXPERIENCE.md § Component Patterns, ikke her.
- **Ekskludert-boks** — Stiplet kantlinje, oppsummerer antall og årsak til utelukkelse (f.eks. "9 under kompetanse-minstekrav · 7 kolliderende vakt"), med "Vis full liste ▾". Se `mockups/direction-a-fagsystem.html`.
- **Varselboks (`alert-box`)** — Brukt på vaktvalg-dashbordet for vakten som mangler bemanning: 4px venstre kant i `{colors.danger}`, sirkulært `!`-ikon, primærknapp "Velg vakt — finn erstatter →". Se `mockups/key-vaktvalg.html`.
- **Tomtilstand (`empty-state`)** — Samme visuelle familie som varselboks (sirkulært `!`-ikon i `danger`-toner), men er en *forklarende* boks, ikke en feilmelding — se ovenfor og EXPERIENCE.md § State Patterns for ordlyd-kravet om at den aldri skal kunne forveksles med en last- eller feiltilstand. Se `mockups/direction-a-fagsystem.html` (variant nederst i filen).
- **Avviksnotat (`deviation-note`)** — Stiplet kant, nøytral bakgrunn (`#f7f9fb`) — signaliserer "informasjon om et bevisst, tillatt valg", ikke en advarsel. Vis-når-regelen ligger i EXPERIENCE.md § Component Patterns. Se `mockups/key-godkjenning.html`.
- **Bekreftelsesboks (`confirm-box`)** — Viser hvem som settes inn i hvilken vakt, med "Avbryt" (`button-secondary`) og "Godkjenn erstatning" (`button-primary`). To-stegs atferd og statuslinje er spesifisert i EXPERIENCE.md § Component Patterns / § State Patterns. Se `mockups/key-godkjenning.html`.
- **Innloggingsskjema (`login-card`)** — Sentrert, smalt (360px) kort på ellers tom `bg-app`-flate. Ett rollenotat forklarer at kun turnusansvarlig har tilgang. Se `mockups/key-innlogging.html`.
- **Knapper** — `button-primary` (`{colors.accent}` fylt, hvit tekst) for hovedhandling per skjerm (velg vakt, godkjenn). `button-secondary` (hvit, kantlinje) for avbryt/sekundærhandling. Ingen tertiær/ghost-variant er definert.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Grønn = ordinær sats, oker/`warn` = overtid og høy belastning | Bruk rødt for overtid eller høy arbeidsbelastning — det er ikke en feil, bare dyrere/tyngre |
| Rødt (`danger`) kun for faktiske utelukkelser og "ingen gyldige kandidater" | Bruk `danger` som generell "obs"-farge |
| Nøkkeltall (kostnad, arbeidsbelastning, kompetanse) synlig direkte i raden | Skjul nøkkeltall bak et klikk eller et eget faneskift |
| Topprangerte/anbefalte kandidats Avveining utvidet som standard | Utvid alle Avveininger samtidig, eller skjul dem alle bak et klikk |
| 1px kantlinjer for struktur og hierarki | Skygger eller elevasjon som hierarkisignal |
| Skarpe, små radiuser (3–4px) | Runde kort, pille-knapper, "vennlig app"-formspråk |
| Ett navy/grå fargespråk, konsekvent på tvers av skjermer | Introduser nye farger eller et nytt visuelt språk per skjerm |
