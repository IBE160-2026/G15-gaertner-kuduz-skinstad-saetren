---
title: "EXPERIENCE: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-09-26
sources:
  - _bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/.memlog.md
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/direction-a-fagsystem.html
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-innlogging.html
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-vaktvalg.html
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-godkjenning.html
---

# Turnushjelperen — Experience-spine

## Foundation

Responsiv web-app — samme kodebase (JS-frontend, Python-backend) på tvers av desktop og mobil/nettbrett. Ingen egen native app. **[ASSUMPTION, vurdert]** installerbar som PWA er nevnt som en mulighet i beslutningsloggen, men er ikke en bekreftet forpliktelse for v1.

Ingen navngitt UI-komponentbibliotek (ikke shadcn/MUI/Tailwind-system) — et egendefinert, tett "fagsystem"-formspråk bygget for dette produktet. `DESIGN.md` er den visuelle identitetsreferansen; denne spine-filen er atferden. Kun norsk bokmål — ingen i18n i v1.

Én rolle, ingen tilstandsforgrening på bruker: **Turnusansvarlig** er den eneste som logger inn og bruker systemet (FR-13). Ansatte er ikke brukere, jf. PRD §2.2 — ingen ansatt-flate finnes noe sted i denne spinen. Enkel brukernavn/passord-innlogging — ingen SSO, ingen selvbetjent registrering eller passordgjenoppretting.

## Information Architecture

| Flate | Nås fra | Formål |
|---|---|---|
| Logg inn | Appen åpnes uten gyldig sesjon | Autentisering av turnusansvarlig (FR-13) |
| Vaktvalg (turnusoversikt) | Etter innlogging | Oversikt over avdelingens vakter i perioden; vakten som mangler bemanning er flagget øverst under "Krever handling" (FR-1) |
| Kandidatrangering | Vaktvalg → "Velg vakt — finn erstatter →" | Rangert liste over gyldige kandidater med kostnad, arbeidsbelastning, Kompetansenivå og Avveining (FR-2–FR-11) |
| Godkjenning | Kandidatrangering → velg en kandidat (ikke nødvendigvis nr. 1) | Bekreft valgt erstatter, inkl. eksplisitt notat om avvik fra topprangert kandidat (FR-12) |

Ingen sidemeny eller fanenavigasjon i v1 — flyten er lineær og skjermene henger sammen via brødsmulesti (`Turnus > Avdeling > Vakt > …`) fremfor global navigasjon, fordi produktet løser *én* vaktendring om gangen (§5 Ikke-mål: ingen full turnusgenerering eller flere samtidige endringer). Modal/dialog-dybde er ikke eksplisitt vist i mockupene; godkjenning er modellert som egen flate (URL), ikke en dialog oppå kandidatrangeringen.

→ Komposisjonsreferanse: `mockups/key-innlogging.html` (logg inn), `mockups/key-vaktvalg.html` (vaktvalg), `mockups/direction-a-fagsystem.html` (kandidatrangering), `mockups/key-godkjenning.html` (godkjenning). Spine vinner ved konflikt.

## Voice and Tone

Mikrotekst. Merkevarestemme og estetisk holdning ligger i `DESIGN.md.Brand & Style`.

| Do | Don't |
|---|---|
| "Mangler bemanning" | "FEIL: ingen bemanning!" |
| "Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff." | "Noe gikk galt" / en tom liste uten forklaring |
| "Ikke gjennomført — venter på eksplisitt godkjenning" | "Advarsel! Handling påkrevd!" |
| "Turnushjelperen anbefaler, den bestemmer aldri selv." | Språk som antyder at systemet har valgt eller utført noe automatisk |
| "Avvik fra anbefalt rangering" (nøytralt, informativt) | "Du har valgt feil kandidat" / noe som antyder at avvik fra rangeringen er galt |
| Korte, presise, tallbaserte setninger ("21 kandidater utelukket av harde regler") | Utropstegn, oppmuntrende språk, gamification ("Bra jobbet!") |

Gjennomgående prinsipp: systemet beskriver tilstand og begrunner tall — det formaner aldri og feirer aldri. Dette følger direkte av at Turnushjelperen er beslutningsstøtte, ikke beslutningstaker (PRD §1, §4.6).

## Component Patterns

Atferd. Visuelle spesifikasjoner ligger i `DESIGN.md.Components`.

| Komponent | Bruk | Atferdsregler |
|---|---|---|
| Appbar | Alle flater | Viser innlogget bruker + avdeling når autentisert; viser "Ikke innlogget" på Logg inn-flaten. Statisk på tvers av navigasjon — endrer seg kun ved innlogging/utlogging, ikke per handling. |
| Rangeringstabell | Kandidatrangering | Én rad per gyldig kandidat, sortert etter rangering. Rad kan ekspanderes/kollapses uavhengig av andre rader. Når ingen kandidat har full kvalifisering for vakttypen, rangeres kandidaten med Kompetansenivå nærmest full kvalifisering høyere enn de som er lenger unna (FR-9) — vises som normal rangeringsrekkefølge, ikke et eget merke. |
| Forklaringsrad/-panel (Avveining) | Kandidatrangering, Godkjenning | Topprangerte/anbefalte kandidats Avveining (KI-begrunnelse) er **utvidet som standard** ved sideinnlasting; øvrige er kollapset bak "Vis begrunnelse ▾". Nevner aldri en kandidat utelukket av en Hard regel (testbar invariant, FR-11). |
| Arbeidsbelastningslinje | Kandidatrangering, Godkjenning | Fylles proporsjonalt med gjeldende timer denne perioden. Bytter visuell tilstand fra normal til "høy belastning" ved ~90 %+ terskel — ingen eget tekstlig varsel, kun fargeendring i linjen. |
| Kostnadsindikator | Kandidatrangering, Godkjenning | Viser "Ordinær" eller "Overtid" per kandidat, alltid sammen med kr/t. Aldri et tredje "feil"-signal. |
| Ekskludert-boks | Kandidatrangering | Skjuler ikke at 20+ ansatte finnes — oppsummerer antall og fordeling per Hard regel (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen; FR-2–FR-5), med "Vis full liste ▾" for detaljer på forespørsel. |
| Varselboks | Vaktvalg | Én vakt om gangen kan være i "krever handling"-tilstand per rad; knappen "Velg vakt — finn erstatter →" er eneste vei inn i kandidatrangering for den vakten. |
| Avviksnotat | Godkjenning | Vises **kun** når valgt kandidat ≠ topprangert kandidat. Viser side-om-side-sammenligning (kostnad, Kompetansenivå, arbeidsbelastning) mellom valgt og topprangert, som nøytral informasjon — blokkerer ikke godkjenning. |
| Bekreftelsesboks (to-stegs godkjenning) | Godkjenning | Steg 1: velg kandidat i rangeringen. Steg 2: eksplisitt "Godkjenn erstatning" i bekreftelsesboksen. Ingen endring i turnusen anses gjennomført mellom disse stegene (FR-12). "Avbryt" fører tilbake uten noen tilstandsendring. |
| Innloggingsskjema | Logg inn | Brukernavn + passord. Ingen tilgang til noen annen flate (§4.1–§4.6) uten gyldig innlogging (FR-13). |

## State Patterns

| Tilstand | Flate | Behandling |
|---|---|---|
| Innlogging feilet | Logg inn | **[ASSUMPTION]** Ingen kilde viser denne tilstanden. Minimal antatt behandling: feilmelding inline i skjemaet ("Feil brukernavn eller passord"), ingen kontosperring spesifisert — må bekreftes før implementasjon. |
| Beregner rangering | Kandidatrangering | **[ASSUMPTION]** Ingen kilde viser en ventetilstand mellom vaktvalg og ferdig rangert liste. Regelmotor-filtrering antas rask (ingen egen tilstand nødvendig); KI-genererte Avveininger kan ha merkbar ventetid — foreslått at rad/rangering vises umiddelbart mens hver Avveining lastes progressivt per rad, fremfor å blokkere hele tabellen. Bør bekreftes før implementasjon. |
| Ingen gyldige kandidater | Kandidatrangering | Eksplisitt forklarende melding (se Voice and Tone) — tydelig visuelt og tekstlig forskjellig fra en laste- eller feiltilstand (FR-6, testbar invariant). **[ASSUMPTION]** foreslåtte handlingsalternativer i meldingsteksten ("del opp vakten", "hent inn ekstravakt", "kontakt bemanningsansvarlig") er illustrative i mockupen, ikke bekreftede produktfunksjoner — ingen av disse er FR-er i PRD-en. |
| Krever handling (vakt mangler bemanning) | Vaktvalg | Flagget øverst i egen seksjon, atskilt fra normalt bemannede vakter i samme periode. |
| Ingen vakter krever handling | Vaktvalg | **[ASSUMPTION]** Ingen kilde viser denne tilstanden (mockupen viser alltid nøyaktig én flagget vakt). Foreslått: "Krever handling"-seksjonen skjules helt, eller vises med en kort nøytral tekst ("Ingen vakter krever handling nå") — ingen tom "!"-boks, siden dette er en normaltilstand, ikke noe som mangler. |
| Avvik fra anbefalt rangering | Godkjenning | Nøytral informasjonsboks, ikke en advarsel eller blokkerende validering — avvik er en gyldig arbeidsflyt (FR-12). |
| Godkjenning ikke gjennomført | Godkjenning | Eksplisitt statuslinje ("ikke gjennomført — venter på eksplisitt godkjenning") vises helt til bekreftelse er gitt. |
| Avveining feilet/tom/ubrukelig | Kandidatrangering, Godkjenning | Forhåndsdefinert reservetekst eller feilmelding i stedet for Avveiningen — aldri en anbefaling uten gyldig grunnlag, og systemet fortsetter å fungere (FR-11). **[ASSUMPTION]** eksakt reservetekst er ikke definert i noen kilde — dekkes ikke av mockupene, må besluttes separat. |
| Ikke innlogget / utløpt sesjon | Alle flater unntatt Logg inn | Ingen tilgang til §4.1–§4.6-funksjonalitet; sendes til Logg inn (FR-13). |
| Vellykket godkjenning gjennomført | Godkjenning → Vaktvalg | Kort bekreftelsesmelding øverst (f.eks. "Erstatning bekreftet — Jonas Bakke er satt opp på Vakt #4127"), deretter tilbake til vaktvalg-oversikten. Vakten vises ikke lenger under "Krever handling". |

## Interaction Primitives

- Klikk for å handle — ingen swipe-, dra- eller høyreklikk-mønstre i noen av kildene.
- Ekspander/kollapse per rad ("Vis begrunnelse ▾" / "Skjul begrunnelse ▴") er uavhengig per kandidat — å åpne én lukker ikke en annen.
- Godkjenning er alltid et eksplisitt to-stegs valg (velg → bekreft), aldri ett klikk som utfører en endring direkte.
- Ingen automatisk utførelse noe sted: KI genererer forslag og forklaring, men ingen handling gjennomføres uten Turnusansvarliges eksplisitte godkjenning (PRD §4.6, testbar invariant SM-8).
- **Bevisst utelatt:** automatisk SMS-/varslingsutsendelse til valgt kandidat etter godkjenning ble foreslått og deretter trukket tilbake av gruppen — ikke en del av opplevelsen, og skal ikke implementeres.
- **[ASSUMPTION]** tastatursnarveier er ikke definert i noen kilde (ingen kommandopalett, ingen "g t"-type navigasjon som i mer avanserte fagsystemer) — vanlig tab/enter-tastaturnavigasjon er eneste bekreftede forventning, jf. Accessibility Floor.

## Accessibility Floor

Behandling. Visuell kontrast ligger i `DESIGN.md`.

Enkel, fornuftig standard — **ikke** et utvidet WCAG-program. Dette er en bevisst, uttalt avgrensning i beslutningsloggen, ikke et PRD-krav:

- Tilstrekkelig fargekontrast for tekst og fargekodede statuser (kostnad, arbeidsbelastning) mot bakgrunnene definert i `DESIGN.md.Colors`.
- Full tastaturnavigerbarhet: alle knapper, ekspander-lenker og skjemafelt må kunne nås og aktiveres uten mus.
- Ingen bekreftet skjermleser-/ARIA-innsats utover det som følger naturlig av semantisk HTML — ikke spesifisert som eget krav.

## Responsive & Platform

Responsiv web-app — samme kodebase skal fungere godt på både desktop og mobil/nettbrett (bekreftet i beslutningsloggen), ikke en separat native app. Alle fire mockup-skjermene (`mockups/`) viser imidlertid kun én fast desktop-bredde (1180px, "nettleser-vindu"-innramming) — **ingen breakpoints, stablingsmønster for tabellen, eller mobiltilpasning er faktisk besluttet eller vist noe sted.**

**[ASSUMPTION]** Følgende er en rimelig, men ubekreftet, tilpasning avledet fra tettheten i `DESIGN.md` og bør bekreftes med gruppen før implementasjon:

| Breakpoint | Foreslått behandling |
|---|---|
| Desktop (bred flate) | Full rangeringstabell som i mockupene — alle kolonner synlige samtidig. |
| Nettbrett (smalere flate) | Tabellen beholder radform, men mindre kritiske kolonner (f.eks. ansiennitet i undertekst) kan flyttes ned i raden fremfor egen kolonne. |
| Mobil (smalest) | Hver kandidatrad kan trenge å bli et stablet kort fremfor en tabellrad for å unngå horisontal scroll — rangeringsnummer, navn og kostnad forblir øverst synlig; arbeidsbelastningslinje og Avveining under. Ekspander/kollapse-mønsteret for Avveining videreføres uendret. |

Ingen plattformspesifikke konvensjoner (iOS/Android native) er relevante — dette er utelukkende nettleserbasert.

## Key Flows

### UJ-1 — Turnusansvarlig finner en erstatter for en vakt som mangler bemanning (Kari)

**Persona + kontekst:** Kari, turnusansvarlig for en avdeling med ca. 25 ansatte, får beskjed om at en ansatt har meldt seg syk til en vakt i morgen.

**Inngangstilstand:** Kari er innlogget i Turnushjelperen og har den eksisterende turnusen tilgjengelig.

1. Kari er innlogget (Logg inn-flaten er inngangsporten til alt annet i systemet, men ikke en del av denne konkrete reisen).
2. På Vaktvalg ser hun umiddelbart Vakt #4127 flagget under "Krever handling": Silje Amundsen har meldt seg syk. Øvrige vakter i perioden vises nøkternt bemannet under, for kontrast.
3. Hun trykker "Velg vakt — finn erstatter →". Systemet viser en rangert liste over gyldige kandidater — ansatte under kompetanse-minstekravet, med kolliderende vakt, eller som ville brutt 11- eller 35-timersregelen, er allerede filtrert bort (Kandidatrangering).
4. Ingrid Dahls rad har Avveiningen (KI-begrunnelsen) utvidet som standard: full kompetanse, ordinær sats, lav arbeidsbelastning, uttrykt ønske om flere vakter. Kari åpner også "Vis begrunnelse" for Jonas Bakke (nr. 2) og Mette Solberg (nr. 3), som har arbeidsbelastningslinje i `warn`-tilstand ved 92 %.
5. Hun sammenligner 2–3 kandidater på denne måten — kostnad, arbeidsbelastning og Avveining side om side i tabellen, uten å måtte sjekke de resterende 21 ansatte manuelt.
6. **Klimaks:** Kari ser tydelig hvorfor Ingrid er anbefalt øverst, men velger bevisst Jonas Bakke (nr. 2) i stedet — kanskje fordi hun, ut fra annen kjennskap til avdelingen, vurderer det riktigere akkurat denne uken. På Godkjenning vises et nøytralt avviksnotat: Ingrid er fortsatt gyldig og rangert øverst, men er ikke valgt — "Turnushjelperen anbefaler, den bestemmer aldri selv."
7. **Oppløsning:** Kari trykker "Godkjenn erstatning" i bekreftelsesboksen. Ingen endring i turnusen var gjennomført før dette eksplisitte trykket.

**Edge case (samme flyt, annen vakt):** Ingen kandidater er gyldige for Vakt #4189 (nattevakt 28.09) — alle 25 ansatte er utelukket av Harde regler. Kandidatrangering viser den forklarende tomtilstanden i stedet for en tom eller misvisende liste, med et tydelig "dette er ikke en feil"-budskap.
