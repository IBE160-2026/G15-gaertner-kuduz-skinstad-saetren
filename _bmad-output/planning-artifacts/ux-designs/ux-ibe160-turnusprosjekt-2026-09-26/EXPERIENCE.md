---
title: "EXPERIENCE: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-11-06
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

Web-app med desktop som bindende flate. Mobil og nettbrett er v2; v1 skal fungere godt i smale nettleservinduer på en datamaskin (AV-17, 2026-11-14). Ingen egen native app. PWA er en mulighet, ikke v1-forpliktelse.

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
| "Satt sammen fra beregnede tall, ikke KI-generert" (kilden sagt rett ut) | Å presentere forhåndsgenerert tekst eller maltekst som om den var et live KI-svar |

Gjennomgående prinsipp: systemet beskriver tilstand og begrunner tall — det formaner aldri og feirer aldri. Dette følger direkte av at Turnushjelperen er beslutningsstøtte, ikke beslutningstaker (PRD §1, §4.6).

## Component Patterns

Atferd. Visuelle spesifikasjoner ligger i `DESIGN.md.Components`.

| Komponent | Bruk | Atferdsregler |
|---|---|---|
| Appbar | Alle flater | Viser innlogget bruker + avdeling når autentisert; viser "Ikke innlogget" på Logg inn-flaten. Statisk på tvers av navigasjon — endrer seg kun ved innlogging/utlogging, ikke per handling. I demo-modus (ingen API-nøkkel, arkitekturens AD-6) vises en nøytral tag "Demo-modus" til venstre for innlogget bruker — statisk så lenge appen kjører. |
| Rangeringstabell | Kandidatrangering | Når kandidatberegningen er ferdig, vises inntil fem høyest rangerte gyldige kandidater og antall utelukkede per Hard regel uten ekstra handling (SM-3/AV-15). Én rad per gyldig kandidat, sortert etter rangering. Rad kan ekspanderes/kollapses uavhengig av andre rader. Kompetansenivå vises som informasjon, men gir ingen rangeringspoeng — kompetanse er bare et hardt minstekrav (FR-2, FR-9). |
| Forklaringsrad/-panel (Avveining) | Kandidatrangering, Godkjenning | Topprangerte/anbefalte kandidats Avveining (KI-begrunnelse) er **utvidet som standard** ved sideinnlasting; øvrige er kollapset bak "Vis begrunnelse ▾". En gyldig forklaring har minst én relevant, faktakontrollert myk faktor; ved én gyldig kandidat brukes ingen referansesammenligning. Ved feil vises merket reservetekst. Vaktkostnad, Timebelastning, Ulempebelastning og preferansekategori/-status med poeng vises ved panelet også da (SM-4/AV-15). Nevner aldri en kandidat utelukket av en Hard regel (FR-11). Hvert panel har en kildelinje nederst i `meta`: "KI-generert · <modellnavn>" (godkjent live-forklaring), "Forhåndsgenerert KI-forklaring · <modellnavn>, <dato>", "Satt sammen fra beregnede tall, ikke KI-generert" (mal), eller "Reservetekst · KI-forklaring utilgjengelig" når `avveining_feilet`. Kildelinjen vises i alle moduser, ikke bare i demo-modus (PRD §4.5). |
| Arbeidsbelastningslinje | Kandidatrangering, Godkjenning | Viser eksisterende timer i kalenderuken vakten starter i, fordelt etter faktisk overlapp. Bytter til «høy belastning» ved minst 32,4 t før avrunding (P-02/P-04); 32 t er under grensen. Vis timeverdien presist nok til at fargeskiftet kan forstås. |
| Ulempeindikator (lagt til 2026-10-30) | Kandidatrangering, Godkjenning, Avviksnotat | Egen kolonne rett etter timebelastningen. Viser ulempepoeng for de fire ukene før vakten og fordelingen på kveld-, helg- og nattetimer, slik at turnusansvarlig ser hva belastningen består av. Ingen terskel og ingen fargeendring. En kandidat uten vakter i perioden viser "0 p" (PRD §4.3, FR-14). |
| Kostnadsindikator | Kandidatrangering, Godkjenning | Viser samlet Vaktkostnad med to desimaler, «Ordinær» eller «Inkluderer overtid», og timer × satser i detaljer. Én sats får ikke representere en blandet Vakt (P-01/P-03). |
| Ekskludert-boks | Kandidatrangering | Skjuler ikke at 20+ ansatte finnes — oppsummerer antall og fordeling per Hard regel (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen; FR-2–FR-5), med "Vis full liste ▾" for detaljer på forespørsel. |
| Varselboks | Vaktvalg | Én vakt om gangen kan være i "krever handling"-tilstand per rad; knappen "Velg vakt — finn erstatter →" er eneste vei inn i kandidatrangering for den vakten. |
| Avviksnotat | Godkjenning | Vises **kun** når valgt kandidat ≠ topprangert kandidat. Viser side-om-side-sammenligning (kostnad, Kompetansenivå, timebelastning, ulempebelastning) mellom valgt og topprangert, som nøytral informasjon — blokkerer ikke godkjenning. |
| Bekreftelsesboks (to-stegs godkjenning) | Godkjenning | Steg 1: velg kandidat i rangeringen. Steg 2: eksplisitt "Godkjenn erstatning" i bekreftelsesboksen. Ingen endring i turnusen anses gjennomført mellom disse stegene (FR-12). "Avbryt" fører tilbake uten noen tilstandsendring. |
| Innloggingsskjema | Logg inn | Brukernavn + passord. Ingen tilgang til noen annen flate (§4.1–§4.6) uten gyldig innlogging (FR-13). |

## State Patterns

| Tilstand | Flate | Behandling |
|---|---|---|
| Innlogging feilet | Logg inn | Viser «Feil brukernavn eller passord.» inline i skjemaet, med samme melding for ukjent brukernavn og feil passord (FR-13). Ingen kontosperring er spesifisert. |
| Beregner rangering | Kandidatrangering | SM-3/AV-15 krever at listen og antall utelukkede vises når kandidatberegningen er ferdig, uten ekstra handling. **[ASSUMPTION]** Eksakt ventetilstand mellom vaktvalg og ferdig liste er ikke vist i kildene. KI-genererte Avveininger kan ha merkbar ventetid; rad/rangering kan vises mens forklaringene lastes progressivt. Transport og visningsmønster bekreftes før implementasjon. |
| Ingen gyldige kandidater | Kandidatrangering | Egen tomtilstand med utelukkelsesoppsummering og «Innleie av personell kan vurderes», uten knapp (P-11). Skilles tydelig fra lasting og P-08s datafeil. |
| Krever handling (vakt mangler bemanning) | Vaktvalg | Flagget øverst i egen seksjon, atskilt fra normalt bemannede vakter i samme periode. |
| Ingen vakter krever handling | Vaktvalg | **[ASSUMPTION]** Ingen kilde viser denne tilstanden (mockupen viser alltid nøyaktig én flagget vakt). Foreslått: "Krever handling"-seksjonen skjules helt, eller vises med en kort nøytral tekst ("Ingen vakter krever handling nå") — ingen tom "!"-boks, siden dette er en normaltilstand, ikke noe som mangler. |
| Avvik fra anbefalt rangering | Godkjenning | Nøytral informasjonsboks, ikke en advarsel eller blokkerende validering — avvik er en gyldig arbeidsflyt (FR-12). |
| Godkjenning ikke gjennomført | Godkjenning | Eksplisitt statuslinje ("ikke gjennomført — venter på eksplisitt godkjenning") vises helt til bekreftelse er gitt. |
| Avveining feilet/tom/ubrukelig eller forkastet i faktakontroll | Kandidatrangering, Godkjenning | Tydelig merket reservetekst i stedet for Avveiningen, med egen kildelinje for `avveining_feilet` og aldri en etikett som fremstiller reserveteksten som godkjent KI-forklaring; rangering og Godkjenning fungerer videre. Eksakt reservetekst fastsettes i story 5.4 (P-06). |
| Demo-modus (ingen API-nøkkel) | Alle flater etter innlogging | Appbaren viser taggen "Demo-modus"; Avveininger vises med kildelinjen "forhåndsgenerert" eller "mal". Flyten fungerer ellers som i live-modus. Dette er en normaltilstand, ikke en feil — derfor ingen `warn`- eller `danger`-farge (AD-6, PRD §4.5). |
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

Mulig tillegg i v2 (2026-11-06): utvidet tilgjengelighet for svaksynte, med skjermleserstøtte som alternativtekst for ikoner, etiketter på skjemafelt, tabelloverskrifter skjermleseren kan lese og opplesing av åpnet/lukket begrunnelse og statusmeldinger. Avgrensningen over gjelder fortsatt for v1.

## Responsive & Platform

Desktop og gjeldende tilgjengelighetskrav er bindende. Alle fire mockup-skjermene (`mockups/`) er desktopillustrasjoner; 1180px er en presentasjonsramme, mens appinnholdet har `max-width: 1180px` (AV-14).

Besluttet 2026-11-06 (AV-14): 1180px er rammens bredde, ikke produktets. Appbaren går over hele bredden, innholdet får `max-width: 1180px`, og under det ruller brede tabeller vannrett i sin egen beholder. Siden som helhet skal ikke rulle vannrett.

Besluttet 2026-11-14 (AV-17): Mobil og nettbrett er v2. Appen kjører lokalt og krever en datamaskin, så en telefon eller et nettbrett når den ikke i v1. V1 skal i stedet fungere godt i smale nettleservinduer: på en skjerm på høykant, med flere vinduer side om side, og når vinduet endrer størrelse. Story 4.6 kontrollerer flatene ved 1080, 960 og 680 px. Der skal hele tiden være synlig hvilken Kandidat en rad i rangeringstabellen gjelder, også når tabellen er rullet vannrett. Hvordan det løses (fast første kolonne eller opplysninger flyttet inn i raden), avgjøres i story 4.6.

**Innspill til v2, ikke v1-krav.** Forslaget under var en ubekreftet tilpasning avledet fra tettheten i `DESIGN.md`. Det bygges ikke i v1 (AV-17), men kan brukes når appen får hosting og mobil og nettbrett tas opp igjen:

| Flate | Foreslått behandling |
|---|---|
| Desktop (bred flate) | Full rangeringstabell som i mockupene — alle kolonner synlige samtidig. |
| Nettbrett (smalere flate) | Tabellen beholder radform, men mindre kritiske kolonner (f.eks. ansiennitet i undertekst) kan flyttes ned i raden fremfor egen kolonne. |
| Mobil (smalest) | Hver kandidatrad kan trenge å bli et stablet kort fremfor en tabellrad for å unngå horisontal scroll — rangeringsnummer, navn og kostnad forblir øverst synlig; arbeidsbelastningslinje, ulempeindikator og Avveining under. Ekspander/kollapse-mønsteret for Avveining videreføres uendret. |

Ingen plattformspesifikke konvensjoner (iOS/Android native) er relevante — dette er utelukkende nettleserbasert.

## Key Flows

### UJ-1 — Turnusansvarlig finner en erstatter for en vakt som mangler bemanning (Kari)

**Persona + kontekst:** Kari, turnusansvarlig for en avdeling med ca. 25 ansatte, får beskjed om at en ansatt har meldt seg syk til en vakt i morgen.

**Inngangstilstand:** Kari er innlogget i Turnushjelperen og har den eksisterende turnusen tilgjengelig.

1. Kari er innlogget (Logg inn-flaten er inngangsporten til alt annet i systemet, men ikke en del av denne konkrete reisen).
2. På Vaktvalg ser hun umiddelbart Vakt #4127 flagget under "Krever handling": Silje Amundsen har meldt seg syk. Øvrige vakter i perioden vises nøkternt bemannet under, for kontrast.
3. Hun trykker "Velg vakt — finn erstatter →". Systemet viser en rangert liste over gyldige kandidater — ansatte under kompetanse-minstekravet, med kolliderende vakt, eller som ville brutt 11- eller 35-timersregelen, er allerede filtrert bort (Kandidatrangering).
4. Jonas Bakkes rad (nr. 1 i #4127-fasiten) har forklaringen utvidet som standard. Kari åpner også «Vis begrunnelse» for Mette Solberg (nr. 2). Ingrid Dahl har 32 t eksisterende timebelastning, er under 32,4-timersgrensen og har en Vaktkostnad på 3 850 kr med fire overtidstimer; hun er nr. 4.
5. Hun sammenligner 2–3 kandidater på denne måten — kostnad, arbeidsbelastning og Avveining side om side i tabellen, uten å måtte sjekke de resterende 21 ansatte manuelt.
6. **Klimaks:** Kari ser hvorfor Jonas er rangert øverst, men velger bevisst Mette (nr. 2). På Godkjenning vises et nøytralt avviksnotat: Jonas er fortsatt gyldig og rangert øverst, men ikke valgt — «Turnushjelperen anbefaler, den bestemmer aldri selv.»
7. **Oppløsning:** Kari trykker "Godkjenn erstatning" i bekreftelsesboksen. Ingen endring i turnusen var gjennomført før dette eksplisitte trykket.

**Edge case (samme flyt, annen vakt):** Ingen kandidater er gyldige for Vakt #4189 (nattevakt 28.09) — opprinnelig ansatt vurderes ikke, og de 24 øvrige er utelukket av Harde regler. Tomtilstanden viser utelukkelsesoppsummering og «Innleie av personell kan vurderes» uten knapp (P-11). Ved #4261–#4265 stopper vurderingen derimot med datafeil som opplyser at seeddata slutter 05.10; ingen rangering eller godkjenning vises (P-08). Oppgavebasert forståelsestest gjenstår etter fungerende kandidatvisning og før story 4.6 (P-13/OP-02). Mobil og nettbrett er avklart som v2 (AV-17).
