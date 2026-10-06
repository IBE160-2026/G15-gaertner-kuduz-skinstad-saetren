---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md
  - _bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/addendum.md
  - _bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-vaktvalg.html
---

# Turnushjelperen - Epic-oppdeling

## Oversikt

Dette dokumentet deler kravene fra PRD, UX-kontrakten (DESIGN.md + EXPERIENCE.md) og arkitektur-spinen opp i epics og stories som kan implementeres. Lovgrunnlaget i addendum §2 er brukt for grensetilfellene i regelmotoren. Mockupen `key-vaktvalg.html` er brukt for detaljene på Vaktvalg-flaten.

## Kravoversikt

### Funksjonelle krav

FR1: Turnusansvarlig kan velge én Vakt fra en eksisterende Turnus som må bemannes på nytt. Ved valg vises Vaktens tidspunkt og kompetansekrav, og valget starter filtrering og Rangering (FR2–FR9) uten ytterligere handling.
FR2: Systemet utelukker en Kandidat hvis Kandidatens Kompetansenivå er under Vaktens definerte minstekrav. 100 % av slike Kandidater filtreres bort i definerte testscenarioer. Blant Gyldige kandidater brukes Kompetansenivå videre som Myk faktor (FR9).
FR3: Systemet utelukker en Kandidat som allerede har en Vakt som overlapper i tid med Vakten som skal bemannes. 100 % filtreres bort i definerte testscenarioer.
FR4: Systemet utelukker en Kandidat som ville fått mindre enn 11 timer sammenhengende hvile per 24 timer ved å ta Vakten. 100 % filtreres bort i testscenarioer, og samme Kandidat + Vakt gir samme resultat hver gang.
FR5: Systemet utelukker en Kandidat som ville fått mindre enn 35 timer sammenhengende fri per 7 dager ved å ta Vakten. 100 % filtreres bort i testscenarioer.
FR6: Når ingen Kandidater er gyldige, viser systemet en eksplisitt melding i stedet for en tom liste. Meldingen er tekstlig og visuelt forskjellig fra laste- og feiltilstand.
FR7: Systemet beregner en forenklet kostnad per Gyldig kandidat (ordinær sats vs. overtidssats). Samme Kandidat + Vakt gir samme kostnad hver gang, og beregningen er uavhengig av KI. Full lønnskostnad med tillegg, avgifter og tariff er utenfor omfang.
FR8: Systemet viser hvor mye hver Gyldig kandidat allerede er satt opp til å arbeide i perioden, konsistent med Kandidatens øvrige Vakter i Turnusen.
FR9: Systemet rangerer alle Gyldige kandidater etter et definert sett Myke faktorer (kostnad, arbeidsbelastning, Ansattpreferanse, kompetansenærhet). Minst ett scenario viser at billigste Kandidat ikke rangeres høyest. Når ingen er fullt kvalifisert, rangeres den nærmest full kvalifisering høyere, med mindre andre Myke faktorer motsier det. Samme input gir samme rekkefølge hver gang.
FR10: Systemet bruker en språkmodell til å tolke tekstbaserte Ansattpreferanser til strukturert input for Rangeringen. Språkmodellen utfører ikke selve rangeringsberegningen.
FR11: Systemet genererer en KI-forklaring (Avveining) per Kandidat i Rangeringen: hvorfor Kandidaten kan ta Vakten, hva som trekker opp og ned, kostnadsvurdering og relevante Ansattpreferanser. Forklaringen nevner aldri en utelukket Kandidat. Ved feil, tomt eller ubrukelig svar vises en forhåndsdefinert reservetekst eller feilmelding, og systemet fortsetter uten å krasje.
FR12: Turnusansvarlig kan velge en hvilken som helst Gyldig kandidat, ikke nødvendigvis den øverste, og gi eksplisitt Godkjenning. Ingen endring i Turnusen anses gjennomført før Godkjenning er gitt, og systemet kan ikke gjennomføre Godkjenning automatisk.
FR13: Turnusansvarlig kan logge inn med brukernavn og passord. Ingen funksjonalitet i FR1–FR12 er tilgjengelig uten gyldig innlogging. Flere roller, tilgangsnivåer og SSO er utenfor omfang.

### Ikke-funksjonelle krav

NFR1 (Reproduserbarhet): Harde regler, kostnad, arbeidsbelastning og Rangering er deterministiske: samme strukturerte input gir samme resultat hver gang (SM-5).
NFR2 (Lekkasje-invariant): En Kandidat utelukket av en Hard regel kan aldri forekomme i Rangeringen eller nevnes i KI-forklaringen. Dette er en testbar invariant (SM-2, PRD §4.2).
NFR3 (KI-grense): KI beregner aldri Harde regler, arbeidstid, kostnad eller Rangering. KI mottar allerede filtrerte og beregnede data og kan ikke endre dem (PRD §4.5, §5).
NFR4 (Robusthet ved KI-feil): Feil, tomt eller ubrukelig svar fra språkmodellen, inkludert fartsgrense, gir reservetekst eller feilmelding i stedet for Avveining, aldri en anbefaling uten grunnlag. Systemet krasjer ikke (FR11).
NFR5 (Menneskelig sluttbeslutning): Ingen endring gjennomføres automatisk. Godkjenning krever alltid Turnusansvarliges eksplisitte handling (SM-8).
NFR6 (Tilgangskontroll): Alle funksjoner utenom innlogging krever gyldig sesjon (FR13).
NFR7 (Hemmeligheter): API-nøkler (Gemini) og JWT-signeringsnøkkel leses fra miljøvariabler og skrives aldri i kildekode. Hver variabel dokumenteres uten verdi i `.env.example` (AGENTS.md).
NFR8 (Testdekning av harde regler): Hver Hard regel har egen testmodul som dekker grensetilfellene. En regel er ikke ferdig uten slike tester. Testdekning per regel prioriteres over antall regler (SM-C1, AGENTS.md).
NFR9 (Kjørbar fra rent repo): Systemet kan bygges og kjøres fra en ren klone uten manuelle unntak eller udokumenterte oppsettsteg (SM-9, addendum §6).
NFR10 (Korrekthet foran hastighet): Rask KI-respons optimeres ikke på bekostning av at forklaringen er korrekt og aldri nevner en utelukket Kandidat (SM-C2).
NFR11 (Fiktive data): Bare fiktive data, ingen ekte personopplysninger og ingen integrasjon mot reelle HR-, lønns- eller turnussystemer (PRD §5).
NFR12 (Omfang): Én Vaktendring om gangen. Ingen generering eller optimalisering av hel Turnus, ingen vaktbytte og ingen ansattportal i v1 (PRD §5).
NFR13 (Språk): Brukergrensesnittet er bare på norsk bokmål, uten i18n i v1 (EXPERIENCE.md § Foundation).

### Tilleggskrav

**Oppstart (påvirker Epic 1 Story 1):** Arkitekturen angir ingen starter-mal. Prosjektet er greenfield og må stilles opp fra bunnen etter kildetreet i ARCHITECTURE-SPINE.md § Structural Seed: `backend/` (Python, FastAPI 0.141.1, SQLAlchemy/SQLite, pytest) og `frontend/` (React 19.3.0, Vite 8.3.1, TypeScript 7.0.2), `docs/ki-logg/` og `.env.example`. Når prosjektfilene finnes, skal de faktiske kommandoene for installasjon, kjøring og test føres inn i AGENTS.md § Kjøring og verifisering.

**Arkitekturstruktur**
- Heksagonal arkitektur (lett): `domene/regelmotor` og `domene/porter` er domenekjernen, ren Python uten avhengighet til rammeverk, database eller KI. Adaptere: `adaptere/api` (FastAPI), `adaptere/web` (React SPA), `adaptere/ki` (Gemini) og `adaptere/lagring` (SQLAlchemy/SQLite).
- AD-1/AD-2: `domene/*` importerer aldri fra noen `adaptere/*`-pakke. Dette håndheves statisk med en import-linter-kontrakt og en test som feiler ved brudd.
- AD-1: En kjøretidstest i `tester/` verifiserer at ingen kandidat-ID som `adaptere/api` sender til `adaptere/ki` finnes blant de utelukkede ID-ene fra regelmotoren, i et scenario med kjente utelukkelser.
- Porter (Pydantic, eid av `domene/porter`):
  - `TolketPreferanse` konstrueres bare av `adaptere/ki`.
  - `RangertKandidat` konstrueres bare av `domene/regelmotor`. Minimumsfelt: kandidat-referanse (id/navn), Kompetansenivå, kostnadstype + beløp, arbeidsbelastning (timer + prosent av terskel), rangeringsplass og tilhørende `TolketPreferanse`.
  - `UtelukkelsesOppsummering` konstrueres bare av `domene/regelmotor` og gir antall per Hard regel til Ekskludert-boksen.
- KI-adapteren har to ensrettede roller som begge orkestreres av `adaptere/api`: tolk (tekst → `TolketPreferanse`) før Rangering, og forklar (`RangertKandidat` → Avveining) etter Rangering. Domenekjernen kaller aldri KI.
- Preferansetolkning skjer én gang per Ansatt/preferansetekst og caches/persisteres av `adaptere/lagring`. Regelmotoren får alltid en lagret, allerede tolket verdi, aldri et live KI-kall under Rangering.
- Komposisjon og avhengighetsinjeksjon skjer i oppstartslaget til `adaptere/api`.

**API og sesjon**
- AD-3: Vellykket innlogging gir ett JWT i en `httpOnly`-cookie, ikke `localStorage`. Det er ingen stille fornyelse: når tokenet utløper, må brukeren logge inn på nytt. Passordhashing eies alene av `adaptere/lagring`.
- AD-4: Alle faktiske feilresponser har formen `{ "kode": string, "melding": string }`. `melding` vises aldri i UI. Frontend slår opp `kode` i sin egen norske tekstliste.
- AD-4: «Ingen gyldige kandidater» og «Avveining feilet» er ikke HTTP-feil. De er 200-svar med `status`-diskriminator (`"ok" | "ingen_gyldige_kandidater" | "avveining_feilet"`), og frontend styrer teksten ut fra `status`.
- Datoer i API-kontrakten følger ISO 8601.
- Tilstanden i Turnus/Vakt endres aldri uten eksplisitt Godkjenning. Dette håndheves i `adaptere/api`, ikke bare i frontend.

**Lagring og data**
- AD-5: `adaptere/lagring` eier SQLAlchemy-modeller og databaseskjema alene. Domenet kjenner bare egne Pydantic- og Python-typer, og konvertering skjer i lagringsadapteren.
- AD-5: Det finnes én enkelt skrivefunksjon for Godkjenning. Den krever et fullstendig Godkjenning-objekt og er den eneste kodeveien som kan markere en Vakt som bemannet.
- Lagrede entiteter: Turnus, Vakt, Ansatt (med Kompetansenivå og tolket preferanse), Godkjenning (hvem, hvilken Vakt, når) og innloggingssesjon/bruker.
- Avveining lagres ikke. Den regenereres hver gang en Rangering vises.
- Alle Vakt-tidspunkt lagres og beregnes i `Europe/Oslo` med sommertid, ikke fast UTC-offset. Dette er avgjørende for 11- og 35-timersregelen rundt sommertidsovergangene.
- Primærnøkler tildeles av `adaptere/lagring`. ID-formatet er ikke fastsatt.
- Testdata: én fiktiv Turnus med 20–30 ansatte (PRD §6.1). Ansattpreferanser er forhåndsdefinert i testdataene inntil videre (ÅB-4, PRD §2.2). Testdataene må dekke scenarioene som suksesskriteriene krever: billigste Kandidat er ikke øverst (SM-6), ingen er fullt kvalifisert (FR9), ingen gyldige kandidater (FR6, EXPERIENCE: Vakt #4189), tekstbaserte preferanser (SM-7) og kjente utelukkelser per Hard regel (SM-1).

**KI-integrasjon**
- Google Gemini API via miljøvariabel. Modellversjon er ikke valgt. Fartsgrense skal gi `avveining_feilet`, ikke krasj.

**Kvalitetssikring (emnekrav, gjelder alle stories)**
- pytest på backend, med én testmodul per Hard regel under `tester/regelmotor/`.
- KI-generert kode logges i `docs/ki-logg/<dato>-<tema>.md` (oppgave, prompt, leveranse, rettelser og kvalitetssikring), jf. AGENTS.md og addendum §5.
- Kjøres bare lokalt. Hosting er ikke besluttet.

**Utsatte beslutninger som påvirker enkelte stories** (de tre som blokkerer implementering står under § Åpne beslutninger)
- JWT-utløpstid, migreringsverktøy, SQLAlchemy-versjon og ID-format.
- Gemini-modell og retry/backoff-policy.
- Eksakte feilkoder og responsskjema per endepunkt.
- Transport for progressiv lasting av Avveining (streaming, polling eller separate kall).
- Om Avveiningen skal låses ved Godkjenning.
- Runtime-logging.

### Åpne beslutninger

> **ÅPNE BESLUTNINGER.** Opprinnelig satt opp 2026-09-29. Stories som er merket med en blokkerende ÅB-ID, kan skrives og estimeres, men ikke implementeres før gruppa har tatt beslutningen og ført den inn her. **Oppdatering 2026-10-06:** ÅB-1, ÅB-2 og ÅB-3 — de tre som blokkerte Epic 4 og deler av Epic 5 — er nå løst. ÅB-4 til ÅB-7 er fortsatt åpne, men blokkerer ikke (midlertidige tolkninger er i bruk, se status per rad).

| ID | Beslutning | Kilde | Blokkerer | Status |
|---|---|---|---|---|
| **ÅB-1** | ~~Innbyrdes vekting mellom Myke faktorer i Rangeringen~~ — **løst 2026-10-06.** Poengbasert modell (0–100 poeng per faktor, vektet sum): Kostnad 30 %, Arbeidsbelastning 30 %, Ansattpreferanse 20 %, Kompetansenærhet 20 %. Se PRD §4.4 for full tabell og poengsettingsregler. | PRD §4.4 (oppdatert) | FR9 og alle stories som implementerer Rangering | **Løst 2026-10-06** |
| **ÅB-2** | ~~Kostnadsmodellen: hvilke satser og betingelser som skiller ordinær sats fra overtidssats~~ — **løst 2026-10-06.** Individuell timelønn per Ansatt. Ordinær terskel 36 t/uke (addendum §2). Timer utover: 150 % sats. Se PRD §4.3. | PRD §4.3 (oppdatert) | FR7 og stories som implementerer kostnadsberegning | **Løst 2026-10-06** |
| **ÅB-3** | ~~Terskelen for arbeidsbelastning: hva «~90 %» er prosent av~~ — **løst 2026-10-06.** Gjenbruker ÅB-2s 36-timers normaluke: planlagte timer denne uken (uten vurdert Vakt) ÷ 36, «høy belastning» ved ~90 % (ca. 32–33 t). Se PRD §4.3, FR-8. | PRD §4.3 (oppdatert) | FR8, feltet «prosent av terskel» i `RangertKandidat` og UX-DR9 | **Løst 2026-10-06** |
| **ÅB-4** | Om turnusansvarlig skal kunne redigere Ansattpreferanser i appen. | PRD §2.2 | Ingenting. Midlertidig beslutning: preferansene er **forhåndsdefinert i testdataene** i v1 inntil videre, og ingen story bygger et redigeringsskjema. | Åpen, blokkerer ikke |
| **ÅB-5** | Hvordan 11-timersregelen regnes: hvile før og etter vakten hver for seg, eller et rullerende vindu på 24 timer. | aml. § 10-8 (1), addendum §2 | Ingenting. Midlertidig tolkning: hvile før og etter vakten må hver være minst 11 timer (story 2.3). Velger gruppa en annen tolkning, må regelen og grensetestene i `test_11_timersregelen.py` skrives om. | Åpen, blokkerer ikke |
| **ÅB-6** | Hvilket vindu 35-timersregelen gjelder for: kalenderuke (man–søn) eller et rullerende vindu på 7 dager. | aml. § 10-8 (2), addendum §2 | Ingenting. Midlertidig tolkning: kalenderuke (story 2.4). Velger gruppa en annen tolkning, må regelen og grensetestene i `test_35_timersregelen.py` skrives om. | Åpen, blokkerer ikke |
| **ÅB-7** | Responsiv tilpasning: breakpoints og stablingsmønster for nettbrett og mobil. Bare én fast desktopbredde (1180px) er vist i mockupene. | DESIGN.md, EXPERIENCE.md § Responsive & Platform, arkitektur § Deferred | Ingenting. Midlertidig løsning: forslaget i EXPERIENCE.md (story 4.6). Velger gruppa noe annet, må story 4.6 skrives om. | Åpen, blokkerer ikke |

### UX-designkrav

UX-DR1: Designtokens. Farger (`bg-app`, `bg-panel`, `bg-header`/`accent`, `border`, `text-main`, `text-mute`, `ok`, `warn`, `danger`, `row-alt`, `tag-bg`), typografiroller (`brand` 14,5/700, `heading` 15/700, `section-label` 12/700 versaler, `column-header` 10,5/700 versaler, `body` 12,5/400/1,55, `meta` 11/400), spacing-skala (4/8/12/16/22/32, `content-padding` 22px, `row-padding` 9px 12px) og radius (`sm` 3px, `DEFAULT` 4px, `full`) implementeres som CSS-variabler etter DESIGN.md. Systemfont `Segoe UI, Arial, sans-serif`. Ingen skygger (bare 1px kantlinjer), ingen gradienter, ingen farger utover paletten og ikke dark-mode-først.
UX-DR2: Appbar. Bakgrunn `bg-header` med hvit tekst. Til venstre står «TURNUSHJELPEREN» i `brand`-typografi. Til høyre står innlogget bruker + avdeling, eller «Ikke innlogget» på innloggingssiden. Innholdet endres bare ved inn- og utlogging.
UX-DR3: Brødsmulesti ligger fast under appbar på alle skjermer etter innlogging. Etter mockupene er den `Turnus > Avdeling > Periode` på Vaktvalg (for eksempel «Uke 39–40, 2026»), `Turnus > Avdeling > Vakt #<nr> — <vakttype> <dato>` på kandidatflaten og `Turnus > Avdeling > Vakt #<nr> > Kandidater > Godkjenning` på Godkjenning. Det finnes ingen sidemeny eller fanenavigasjon, og flyten er lineær.
UX-DR4: Innloggingsflate. Sentrert `login-card` på 360px på tom `bg-app`-flate, med felt for brukernavn og passord og et rollenotat om at bare turnusansvarlig har tilgang. Mislykket innlogging gir inline «Feil brukernavn eller passord» uten kontosperring [ASSUMPTION]. Det finnes ingen registrering og ingen passordgjenoppretting.
UX-DR5: Vaktvalg-flate etter `mockups/key-vaktvalg.html`. Seksjonen «Krever handling» (`section-label`) ligger øverst. Hver vakt som mangler bemanning, vises i en `alert-box` med 4px venstrekant i `danger` og sirkulært «!»-ikon. Boksen har overskriften «Vakt #<nr> — <vakttype>, <avdeling>» og en linje med dato, tidsrom og varighet, «Mangler bemanning» i fet `danger` og hvem som meldte fra og når (for eksempel «Silje Amundsen meldt fra sykemeldt kl. 06:14»). Primærknappen «Velg vakt — finn erstatter →» er eneste vei inn i kandidatrangeringen for vakten. Under står seksjonen «Øvrige vakter denne perioden — bemannet» som tabell med kolonnene Vakt (#nr i `accent`, fet), Dato, Tid (tidsrom og varighet, med vakttype som undertekst), Ansatt (navn, med stilling og ansiennitet som `meta`) og Status (tag «Bemannet»). En fotnote nederst til høyre viser når Turnusen sist ble oppdatert og antall ansatte i avdelingen. Mockupens «Se detaljer»-lenke og grønne «Bemannet»-tag er ikke tatt med (se story 1.5).
UX-DR6: Tilstanden «Ingen vakter krever handling» på Vaktvalg. Seksjonen skjules, eller den viser nøytral tekst («Ingen vakter krever handling nå»), aldri en tom «!»-boks [ASSUMPTION].
UX-DR7: Rangeringstabell. Kolonnene er rangeringsnummer, kandidat (navn + `meta`-undertekst), Kompetansenivå (+ tag), kostnad, arbeidsbelastning, preferanse (tag) og ekspander-lenke. Én rad per Gyldig kandidat, sortert etter rangering, med `row-alt` på annenhver rad. Nøkkeltallene er synlige direkte i raden, uten klikk. Kompetansenærhet vises som vanlig rekkefølge, ikke som et eget merke.
UX-DR8: Rangeringsnummer (`rank-badge`) i `accent`, fet og 14px.
UX-DR9: Arbeidsbelastningslinje på 110×7px, fylt proporsjonalt. Fyllet er `accent` under terskelen (~90 %) og `warn` ved og over terskelen. Den er aldri rød, og det finnes ingen tekstlig advarsel, bare fargeskifte. Brukes i både rangering og godkjenning.
UX-DR10: Kostnadsindikator. «Ordinær» i `ok` eller «Overtid» i `warn`, alltid med kr/t under i `meta`. Aldri rød, og aldri et tredje «feil»-signal.
UX-DR11: Tag. Bakgrunn `tag-bg`, kant `border` og radius `sm`. Den viser nøytral informasjon: kompetansenivå og preferanse, for eksempel «Ønsker flere vakter», «Fleksibel» eller «Ingen registrert».
UX-DR12: Forklaringspanel (Avveining). Panelet har bakgrunn `#f2f6f9` og viser «▲ Trekker opp» i `ok` og «▼ Trekker ned» i `danger`. Den topprangerte Kandidatens panel er utvidet ved sideinnlasting, og de øvrige er kollapset bak «Vis begrunnelse ▾» / «Skjul begrunnelse ▴». Radene ekspanderes uavhengig, så å åpne én lukker ingen annen. Panelet brukes både i tabellen og i kandidatkortet på Godkjenning.
UX-DR13: Tilstanden «Beregner rangering». Radene vises med en gang regelmotoren er ferdig, mens hver Avveining lastes progressivt per rad uten å blokkere tabellen [ASSUMPTION].
UX-DR14: Tilstanden «Avveining feilet/tom/ubrukelig». En forhåndsdefinert reservetekst vises i forklaringspanelet i stedet for Avveining, og resten av raden og siden fungerer som normalt. Eksakt tekst er ikke fastsatt.
UX-DR15: Ekskludert-boks. Boksen har stiplet kant og bakgrunn `#f7f9fb`. Den oppsummerer antall og årsak per Hard regel (for eksempel «9 under kompetanse-minstekrav · 7 kolliderende vakt») og har «Vis full liste ▾» for detaljer på forespørsel. Den skjuler ikke at 20+ ansatte finnes.
UX-DR16: Tomtilstand «Ingen gyldige kandidater» (`empty-state`). Boksen har sirkulært «!»-ikon i `danger`-toner og forklarende tekst: «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» Den skal være visuelt og tekstlig forskjellig fra laste- og feiltilstand. Handlingsforslagene i mockupen («del opp vakten» o.l.) er illustrative og skal ikke implementeres som funksjoner.
UX-DR17: Godkjenning-flate. Egen flate med egen URL, ikke en dialog. Kandidatkortet viser navn (`heading`), Kompetansenivå, kostnadsindikator, arbeidsbelastningslinje og forklaringspanel.
UX-DR18: Avviksnotat. Notatet vises bare når valgt Kandidat ≠ topprangert. Det gir en side-om-side-sammenligning av kostnad, Kompetansenivå og arbeidsbelastning mellom valgt og topprangert Kandidat. Stilen er nøytral (stiplet kant, «Avvik fra anbefalt rangering», «Turnushjelperen anbefaler, den bestemmer aldri selv.»), og notatet blokkerer ikke godkjenningen.
UX-DR19: Bekreftelsesboks med to-stegs godkjenning. Boksen viser hvem som settes inn i hvilken vakt, med «Avbryt» (sekundær) og «Godkjenn erstatning» (primær). Statuslinjen «Ikke gjennomført — venter på eksplisitt godkjenning» vises til brukeren bekrefter. «Avbryt» fører tilbake uten tilstandsendring.
UX-DR20: Vellykket godkjenning. En kort bekreftelse vises øverst på Vaktvalg (for eksempel «Erstatning bekreftet — Jonas Bakke er satt opp på Vakt #4127»), og vakten vises ikke lenger under «Krever handling».
UX-DR21: Utløpt eller manglende sesjon. Alle flater unntatt Logg inn sender brukeren til Logg inn.
UX-DR22: Knapper. `button-primary` (fylt `accent`, hvit tekst) brukes for hovedhandlingen per skjerm, og `button-secondary` (hvit med kant) for avbryt. Det finnes ingen tertiær- eller ghost-variant.
UX-DR23: Mikrotekst og tone. All brukertekst ligger i en norsk tekstliste i frontend, slått opp på API-ets `kode`/`status`. Teksten skal være kort, presis og tallbasert, uten utropstegn, formaning, feiring eller gamification, og uten språk som antyder at systemet har valgt eller utført noe.
UX-DR24: Tilgjengelighetsgulv. Kontrasten skal være tilstrekkelig for tekst og fargekodede statuser. Alle knapper, ekspander-lenker og skjemafelt skal kunne nås og aktiveres med tastatur (tab/enter), og HTML-en skal være semantisk. Det finnes ikke noe utvidet WCAG- eller ARIA-program.
UX-DR25: Responsiv tilpasning [ASSUMPTION, må bekreftes]. Desktop viser full tabell. Nettbrett beholder radform, men mindre kritiske kolonner flyttes inn i raden. Mobil viser stablede kort med rangering, navn og kostnad øverst og arbeidsbelastning og Avveining under, uten horisontal scroll.
UX-DR26: Bevisst utelatt. Det finnes ingen SMS eller automatisk varsling til valgt Kandidat etter godkjenning, ingen tastatursnarveier utover tab/enter, ingen swipe- eller dra-mønstre og ingen PWA-forpliktelse i v1.

### FR-dekningskart

FR1: Epic 1 - Velge vakt som må bemannes på nytt, med tidspunkt og kompetansekrav (filtreringen den starter, leveres i Epic 2)
FR2: Epic 2 - Filtrere på kompetanse-minstekrav
FR3: Epic 2 - Filtrere på kolliderende vakt
FR4: Epic 2 - Filtrere på 11-timersregelen
FR5: Epic 2 - Filtrere på 35-timersregelen
FR6: Epic 2 - Eksplisitt melding når ingen kandidater er gyldige
FR7: Epic 4 - Forenklet kostnad per kandidat (kostnadsmodell løst, ÅB-2)
FR8: Epic 4 - Arbeidsbelastning per kandidat (terskel løst, ÅB-3)
FR9: Epic 4 - Rangering av gyldige kandidater (vekting løst, ÅB-1)
FR10: Epic 5 - KI-tolkning av tekstbaserte ansattpreferanser
FR11: Epic 5 - KI-forklaring (Avveining) per kandidat, med reservetekst ved feil
FR12: Epic 3 - To-stegs godkjenning av valgt kandidat
FR13: Epic 1 - Innlogging som turnusansvarlig

## Epic-liste

> **Utkast til gjennomgang i gruppa (2026-09-29).** Strukturen er godkjent som arbeidsgrunnlag, men kan endres etter at gruppa har sett over den.

Rekkefølgen er 1 → 2 → 3 → 4 → 5. Hvert epic fungerer uten de senere. Godkjenning (Epic 3) ligger bevisst før rangeringen, så hele flyten fra innlogging til godkjenning virker uavhengig av rekkefølgen epicene bygges i. **Alle tre åpne beslutninger (ÅB-1, ÅB-2, ÅB-3) er løst 2026-10-06** — se § Åpne beslutninger.

### Epic 1: Innlogging og vaktoversikt
Turnusansvarlig logger inn, ser avdelingens vakter i perioden med vakten som mangler bemanning øverst under «Krever handling», og kan velge den. Epicet setter også opp prosjektet fra bunnen, fordi arkitekturen ikke angir noen starter-mal. I tillegg kommer fiktive testdata, designtokens, appbar og brødsmulesti.
**FR-er som dekkes:** FR13, FR1

### Epic 2: Gyldige kandidater for en vakt
Etter vaktvalg ser turnusansvarlig hvem som faktisk kan ta vakten. De fire harde reglene filtrerer bort resten, med én story per regel. Ekskludert-boksen oppsummerer utelukkelsene, og tomtilstanden vises når ingen er gyldige. Grensen mellom domene og adaptere håndheves fra dette epicet. Ikke blokkert.
**FR-er som dekkes:** FR2, FR3, FR4, FR5, FR6

### Epic 3: Godkjenning av erstatter
Turnusansvarlig velger en gyldig kandidat og godkjenner i to steg. Vakten blir bemannet gjennom én eneste skrivevei, og bekreftelsen vises på vaktoversikten. Ikke blokkert.
**FR-er som dekkes:** FR12

### Epic 4: Rangering etter kostnad, arbeidsbelastning og kompetanse
De gyldige kandidatene rangeres. Tabellen viser kostnadstype, arbeidsbelastningslinje og kompetansenærhet, og avviksnotatet vises når turnusansvarlig velger en annen enn nr. 1. Alle tre åpne beslutninger (ÅB-1 vekting, ÅB-2 kostnadsmodell, ÅB-3 arbeidsbelastningsterskel) er løst 2026-10-06 — se PRD §4.3, §4.4.
**FR-er som dekkes:** FR7, FR8, FR9

### Epic 5: KI-forklaring av avveininger
Preferansetekstene tolkes én gang og lagres. Hver rangert kandidat får en Avveining, med reservetekst hvis modellen feiler og kjøretidstest for lekkasje. Tolkingen (FR10) kan startes parallelt med Epic 4. Forklaringen (FR11) krever `RangertKandidat` fra Epic 4.
**FR-er som dekkes:** FR10, FR11

## Epic 1: Innlogging og vaktoversikt

Turnusansvarlig logger inn, ser avdelingens vakter i perioden med vakten som mangler bemanning øverst under «Krever handling», og kan velge den. Epicet setter også opp prosjektet fra bunnen, fordi arkitekturen ikke angir noen starter-mal.

### Story 1.1: Prosjektoppsett som kjører fra en ren klone

As a utvikler i gruppa,
I want et backend- og frontend-skjelett som kan installeres, kjøres og testes med dokumenterte kommandoer,
So that alle i gruppa bygger på samme struktur og systemet kan kjøres fra en ren klone (NFR9, SM-9).

**Acceptance Criteria:**

**Given** en ren klone av repoet
**When** en utvikler følger kommandoene i AGENTS.md § Kjøring og verifisering
**Then** backend (FastAPI 0.141.1) starter lokalt og svarer på et helsesjekk-endepunkt
**And** frontend (React 19.3.0, Vite 8.3.1, TypeScript 7.0.2) starter lokalt og viser en tom side med produktnavnet
**And** ingen udokumenterte eller manuelle oppsettsteg er nødvendig

**Given** kildetreet i ARCHITECTURE-SPINE.md § Structural Seed
**When** skjelettet er opprettet
**Then** mappene `backend/domene/regelmotor`, `backend/domene/porter`, `backend/adaptere/{api,ki,lagring}`, `backend/tester/` og `frontend/src/` finnes
**And** ingen database-tabeller eller domenetyper er opprettet ennå, fordi de kommer i storiene som trenger dem

**Given** testoppsettet
**When** utvikleren kjører testkommandoen for backend
**Then** pytest kjører og rapporterer minst én grønn test (helsesjekk)

**Given** at prosjektet trenger konfigurasjon
**When** skjelettet leses
**Then** `.env.example` finnes og viser hver miljøvariabel uten verdi (NFR7)
**And** `.env` er gitignorert
**And** installasjons-, kjøre- og testkommandoene er ført inn i AGENTS.md, der TODO-punktene erstattes med de faktiske kommandoene
**And** KI-bruken i storien er logget i `docs/ki-logg/<dato>-<tema>.md`

### Story 1.2: Fiktiv turnus med ansatte og vakter

As a turnusansvarlig,
I want at systemet inneholder en fiktiv turnus for én avdeling med 20–30 ansatte og deres vakter,
So that jeg har en realistisk turnus å finne erstattere i, uten ekte personopplysninger (NFR11).

**Acceptance Criteria:**

**Given** en tom database
**When** utvikleren kjører den dokumenterte kommandoen for testdata
**Then** databasen inneholder én Turnus for én avdeling med 20–30 Ansatte og deres Vakter over en periode (i mockupen Kirurgisk sengepost, uke 39–40 2026)
**And** Turnusen har et tidspunkt for sist oppdatert
**And** kommandoen kan kjøres flere ganger uten å lage duplikater

**Given** lagringsadapteren
**When** tabellene opprettes
**Then** bare tabellene for Turnus, Vakt og Ansatt opprettes i denne storien
**And** SQLAlchemy-modellene ligger i `adaptere/lagring`, som eier skjemaet alene (AD-5)

**Given** en Vakt i testdataene
**When** den leses
**Then** den har vaktnummer, vakttype (dag, kveld eller natt), start- og sluttidspunkt lagret i `Europe/Oslo` med sommertid, et kompetansekrav og en tildelt Ansatt eller markering som «mangler bemanning»
**And** en Vakt som mangler bemanning, har hvem som var satt opp og tidspunktet det ble meldt fra (UX-DR5)

**Given** en Ansatt i testdataene
**When** den leses
**Then** den har et fiktivt navn, stilling, ansiennitet i år, et Kompetansenivå per vakttype, en individuell timelønn (ordinær sats, ÅB-2 løst 2026-10-06, se PRD §4.3) og eventuelt en forhåndsdefinert tekstbasert Ansattpreferanse (ÅB-4)

**Given** testdataene
**When** de brukes i demo
**Then** minst én Vakt (#4127) mangler bemanning og har gyldige kandidater etter planen
**And** minst én Vakt (#4189, nattevakt) mangler bemanning og er satt opp slik at alle Ansatte vil bli utelukket av Harde regler
**And** minst én gyldig Kandidat i et testscenario har nok planlagte timer denne uken til at Vakten ville gitt overtid (over 36 t/uke, PRD §4.3), slik at kostnadsmodellens overtidssats faktisk testes

### Story 1.3: Innlogging for turnusansvarlig

As a turnusansvarlig,
I want å logge inn med brukernavn og passord,
So that Turnushjelperen ikke er åpen for alle (FR13).

**Acceptance Criteria:**

**Given** at jeg ikke er innlogget
**When** jeg åpner appen
**Then** jeg ser innloggingsflaten: et sentrert kort på 360px med felt for brukernavn og passord og et rollenotat om at bare turnusansvarlig har tilgang (UX-DR4)
**And** appbaren viser «TURNUSHJELPEREN» til venstre og «Ikke innlogget» til høyre (UX-DR2)

**Given** gyldig brukernavn og passord
**When** jeg logger inn
**Then** API-et utsteder ett JWT som settes i en `httpOnly`-cookie, ikke i `localStorage` (AD-3)
**And** jeg sendes videre til en foreløpig innlogget startside
**And** appbaren viser «Innlogget: <navn> (turnusansvarlig) · Avdeling <avdeling>» (UX-DR2)

**Given** feil brukernavn eller passord
**When** jeg prøver å logge inn
**Then** skjemaet viser «Feil brukernavn eller passord» inline, uten kontosperring [ASSUMPTION, UX-DR4]
**And** API-et svarer med feilformen `{ "kode", "melding" }` (AD-4), og frontend henter teksten fra sin egen norske tekstliste, ikke fra `melding` (UX-DR23, NFR13)

**Given** brukerkontoen for turnusansvarlig
**When** den opprettes av testdatakommandoen
**Then** passordet hentes fra en miljøvariabel som er dokumentert uten verdi i `.env.example`, og står aldri i kildekoden (NFR7)
**And** passordet lagres bare som hash, og hashingen skjer i `adaptere/lagring` (AD-3)
**And** JWT-signeringsnøkkelen og utløpstiden leses fra miljøvariabler (utløpstiden er en utsatt beslutning og får en dokumentert standardverdi)

**Given** innloggingsflaten
**When** jeg bruker bare tastatur
**Then** jeg kan nå begge feltene og innloggingsknappen med tab og logge inn med enter (UX-DR24)
**And** farger, typografi, spacing og radius kommer fra designtokens i CSS-variabler etter DESIGN.md (UX-DR1), og knappen følger `button-primary` (UX-DR22)

### Story 1.4: Beskyttede flater og utløpt sesjon

As a turnusansvarlig,
I want at ingen funksjon er tilgjengelig uten gyldig innlogging, og at jeg sendes til innlogging når sesjonen er utløpt,
So that turnusdata bare kan ses av den som har tilgang (FR13, NFR6).

**Acceptance Criteria:**

**Given** at jeg ikke har gyldig JWT
**When** jeg kaller et hvilket som helst API-endepunkt utenom innlogging og helsesjekk
**Then** API-et avviser kallet med feilformen `{ "kode", "melding" }` (AD-4)

**Given** at jeg ikke har gyldig sesjon
**When** jeg åpner en hvilken som helst flate utenom Logg inn direkte med URL
**Then** jeg sendes til Logg inn (UX-DR21)

**Given** at JWT-et mitt har utløpt
**When** jeg gjør en handling
**Then** jeg sendes til Logg inn, uten stille fornyelse (AD-3)

**Given** at jeg er innlogget
**When** jeg logger ut
**Then** cookien fjernes, og appbaren viser «Ikke innlogget»

### Story 1.5: Vaktoversikt med «Krever handling»

As a turnusansvarlig,
I want å se avdelingens vakter i perioden med vakter som mangler bemanning flagget øverst,
So that jeg straks ser hva som må håndteres.

**Acceptance Criteria:**

**Given** at jeg er innlogget
**When** jeg kommer til Vaktvalg
**Then** jeg ser brødsmulestien `Turnus > <avdeling> > <periode>`, for eksempel «Turnus > Kirurgisk sengepost > Uke 39–40, 2026», fast under appbar (UX-DR3)
**And** seksjonen «Krever handling» ligger øverst, og seksjonen «Øvrige vakter denne perioden — bemannet» ligger under (UX-DR5)

**Given** en Vakt som mangler bemanning
**When** den vises under «Krever handling»
**Then** den står i en varselboks med 4px venstrekant i `danger` og sirkulært «!»-ikon (UX-DR5)
**And** overskriften er «Vakt #<nr> — <vakttype>, <avdeling>», for eksempel «Vakt #4127 — Dagvakt, Kirurgisk sengepost»
**And** linjen under viser dato, tidsrom og varighet, «Mangler bemanning» i fet `danger` og hvem som meldte fra og når, for eksempel «Lørdag 27.09.2026 · 07:00–15:00 (8 t) · Mangler bemanning — Silje Amundsen meldt fra sykemeldt kl. 06:14»
**And** boksen har primærknappen «Velg vakt — finn erstatter →» (UX-DR5, UX-DR22)

**Given** de bemannede vaktene i perioden
**When** de vises
**Then** de står i en tabell med kolonnene Vakt, Dato, Tid, Ansatt og Status (UX-DR5)
**And** vaktnummeret vises i `accent` og fet, tiden vises med varighet og vakttype som undertekst, og den Ansatte vises med navn og stilling og ansiennitet som `meta`
**And** annenhver rad har `row-alt`
**And** statusen «Bemannet» vises som nøytral tag, uten `ok`-farge. Mockupen bruker grønn her, men DESIGN.md reserverer `ok` for ordinær sats, og spine-dokumentet vinner ved konflikt (EXPERIENCE.md § Information Architecture)
**And** mockupens «Se detaljer»-lenke tas ikke med, fordi ingen FR beskriver en detaljvisning for en bemannet vakt

**Given** Vaktvalg-flaten
**When** den vises
**Then** en fotnote nederst til høyre viser når Turnusen sist ble oppdatert og antall ansatte i avdelingen, for eksempel «Turnus oppdatert 26.09.2026 06:20 · 25 ansatte totalt i avdelingen» (UX-DR5)

**Given** at ingen vakter mangler bemanning
**When** jeg kommer til Vaktvalg
**Then** jeg ser ingen tom «!»-boks, men enten ingen seksjon eller den nøytrale teksten «Ingen vakter krever handling nå» [ASSUMPTION, UX-DR6]

**Given** Vaktvalg-flaten
**When** jeg bruker bare tastatur
**Then** jeg kan nå og aktivere hver «Velg vakt»-knapp med tab og enter (UX-DR24)
**And** teksten følger tonen i UX-DR23 (ingen utropstegn, «Mangler bemanning», ikke «FEIL»)

### Story 1.6: Velge vakten som skal bemannes

As a turnusansvarlig,
I want å velge en vakt som mangler bemanning og se tidspunktet og kompetansekravet for den,
So that jeg vet nøyaktig hvilken vakt jeg finner en erstatter for (FR1).

**Acceptance Criteria:**

**Given** en Vakt under «Krever handling»
**When** jeg trykker «Velg vakt — finn erstatter →»
**Then** jeg kommer til kandidatflaten for vakten, med egen URL (i mockupene `/vakt/<nr>/kandidater`)
**And** brødsmulestien viser `Turnus > <avdeling> > Vakt #<nr> — <vakttype> <dato>`, for eksempel «Turnus > Kirurgisk sengepost > Vakt #4127 — Dagvakt 27.09.2026» (UX-DR3)
**And** flaten viser vaktens start- og sluttidspunkt og kompetansekrav (FR1)

**Given** at knappen er den eneste veien inn
**When** jeg ser på en normalt bemannet vakt
**Then** den har ingen «Velg vakt»-knapp (UX-DR5)

**Given** en vakt-ID som ikke finnes, eller en vakt som ikke mangler bemanning
**When** jeg åpner kandidatflaten direkte med URL
**Then** API-et svarer med feilformen `{ "kode", "melding" }`, og frontend viser en nøytral melding fra tekstlisten (AD-4, UX-DR23)

**Given** kandidatflaten i denne storien
**When** den vises
**Then** den har en tydelig plass der kandidatene kommer i Epic 2, men viser ingen kandidater eller falske data ennå

## Epic 2: Gyldige kandidater for en vakt

Etter vaktvalg ser turnusansvarlig hvem som faktisk kan ta vakten. De fire harde reglene filtrerer bort resten, med én story per regel. Ekskludert-boksen oppsummerer utelukkelsene, og tomtilstanden vises når ingen er gyldige. Alle regler er deterministiske og beregnes i `domene/regelmotor`, uten KI (NFR1, NFR3). Hver regel har egen testmodul under `tester/regelmotor/` som dekker grensetilfellene (NFR8).

### Story 2.1: Gyldige kandidater filtrert på kompetanse-minstekrav

As a turnusansvarlig,
I want å se hvilke ansatte som har kompetanse nok til den valgte vakten,
So that jeg slipper å sjekke kompetansen til alle 20–30 manuelt (FR2).

**Acceptance Criteria:**

**Given** en valgt Vakt på kandidatflaten fra story 1.6
**When** flaten lastes
**Then** filtreringen starter automatisk, uten ytterligere handling (FR1)
**And** jeg ser en liste over Gyldige kandidater med navn og Kompetansenivå som tag (UX-DR11)
**And** listen er sortert alfabetisk etter navn for å være deterministisk, fordi Rangering kommer i Epic 4

**Given** kandidatgrunnlaget
**When** regelmotoren kjører
**Then** alle Ansatte i Turnusen vurderes som Kandidater, bortsett fra den Ansatte som var satt opp på Vakten [ASSUMPTION: ikke uttrykt i PRD]

**Given** en Kandidat med Kompetansenivå lik Vaktens minstekrav
**When** regelen kjører
**Then** Kandidaten er gyldig

**Given** en Kandidat med Kompetansenivå ett trinn under minstekravet
**When** regelen kjører
**Then** Kandidaten er utelukket med årsaken «kompetanse-minstekrav»

**Given** en Kandidat uten registrert Kompetansenivå for vakttypen
**When** regelen kjører
**Then** Kandidaten er utelukket med samme årsak

**Given** domenekjernen
**When** storien er ferdig
**Then** domenetypene (for eksempel Vakt og Kandidat) er rene Pydantic- eller Python-typer i `domene/`, og konvertering fra SQLAlchemy skjer i `adaptere/lagring` (AD-5)
**And** en import-linter-kontrakt forbyr at `domene/regelmotor` og `domene/porter` importerer fra noen `adaptere/*`-pakke, og kontrakten kjøres som del av testkommandoen (AD-1, AD-2)
**And** `tester/regelmotor/test_kompetanse.py` dekker grensetilfellene over, og samme input gir samme resultat ved gjentatt kjøring (NFR1)

**Given** API-svaret for kandidatflaten
**When** det returneres
**Then** det er et 200-svar med `status: "ok"` og listen over Gyldige kandidater (AD-4)
**And** ingen utelukket Kandidat finnes i listen (NFR2)

### Story 2.2: Filtrere bort kandidater med kolliderende vakt

As a turnusansvarlig,
I want at ansatte som allerede jobber i samme tidsrom, er filtrert bort,
So that jeg ikke foreslår noen som er dobbeltbooket (FR3).

**Acceptance Criteria:**

**Given** en Kandidat med en Vakt som overlapper Vakten som skal bemannes med minst ett minutt
**When** regelen kjører
**Then** Kandidaten er utelukket med årsaken «kolliderende vakt»

**Given** en Kandidat med en Vakt som slutter nøyaktig når Vakten som skal bemannes starter, eller starter nøyaktig når den slutter
**When** regelen kjører
**Then** Kandidaten er **ikke** utelukket av denne regelen, fordi vakter behandles som halvåpne intervall [start, slutt)

**Given** en Kandidat med en Vakt som helt omslutter, eller helt ligger inne i, Vakten som skal bemannes
**When** regelen kjører
**Then** Kandidaten er utelukket

**Given** en nattevakt som krysser midnatt
**When** overlapp sjekkes
**Then** overlappen beregnes på faktiske tidspunkt i `Europe/Oslo`, ikke på kalenderdato

**Given** testmodulen
**When** storien er ferdig
**Then** `tester/regelmotor/test_kolliderende_vakt.py` dekker alle grensetilfellene over, og resultatet er reproduserbart (NFR1, NFR8)
**And** kandidatlisten på kandidatflaten er filtrert på både kompetanse og kolliderende vakt

### Story 2.3: Filtrere på 11-timersregelen (daglig hvile)

As a turnusansvarlig,
I want at ansatte som ville fått for lite hvile mellom vaktene, er filtrert bort,
So that jeg ikke foreslår en erstatning som bryter kravet om daglig hvile (FR4).

**Acceptance Criteria:**

> **Åpen beslutning ÅB-5 (blokkerer ikke). Midlertidig tolkning:** «Minst 11 timer sammenhengende hvile per 24 timer» implementeres som krav om at hviletiden mellom slutten av Kandidatens forrige vakt og starten av Vakten, og mellom slutten av Vakten og starten av Kandidatens neste vakt, hver er minst 11 timer. Grunnlag: aml. § 10-8 (1), addendum §2. Tariffunntaket (ned til 8 timer) implementeres ikke i v1.

**Given** en Kandidat hvis forrige vakt slutter nøyaktig 11 timer 0 minutter før Vakten starter
**When** regelen kjører
**Then** Kandidaten er **ikke** utelukket av denne regelen

**Given** en Kandidat hvis forrige vakt slutter 10 timer 59 minutter før Vakten starter
**When** regelen kjører
**Then** Kandidaten er utelukket med årsaken «11-timersregelen»

**Given** en Kandidat hvis neste vakt starter 10 timer 59 minutter etter at Vakten slutter
**When** regelen kjører
**Then** Kandidaten er utelukket med samme årsak

**Given** en hvileperiode som krysser overgangen til sommertid, der klokka hoppes fram en time
**When** hviletiden beregnes
**Then** den beregnes i faktisk forløpt tid (for eksempel regnes veggklokketid 11 timer som 10 faktiske timer, som gir utelukkelse)
**And** tilsvarende gjelder overgangen til vintertid, der veggklokketid 10,5 timer regnes som 11,5 faktiske timer, som ikke gir utelukkelse

**Given** en Kandidat uten andre vakter nær Vakten
**When** regelen kjører
**Then** Kandidaten er ikke utelukket av denne regelen

**Given** testmodulen
**When** storien er ferdig
**Then** `tester/regelmotor/test_11_timersregelen.py` dekker alle grensetilfellene over, inkludert begge sommertidsovergangene
**And** samme Kandidat og Vakt gir samme resultat ved gjentatt kjøring (FR4, NFR1)

### Story 2.4: Filtrere på 35-timersregelen (ukentlig fri)

As a turnusansvarlig,
I want at ansatte som ville mistet sin ukentlige fritid, er filtrert bort,
So that jeg ikke foreslår en erstatning som bryter kravet om ukentlig fri (FR5).

**Acceptance Criteria:**

> **Åpen beslutning ÅB-6 (blokkerer ikke). Midlertidig tolkning:** «Minst 35 timer sammenhengende fri per 7 dager» implementeres per kalenderuke (mandag 00:00 til søndag 24:00, `Europe/Oslo`). Etter at Vakten er lagt til, må Kandidatens vakter i hver berørte uke etterlate minst én sammenhengende friperiode på minst 35 timer innenfor uka. Grunnlag: aml. § 10-8 (2), addendum §2. Tariffunntaket (ned til 28 timer) implementeres ikke i v1.

**Given** en Kandidat som etter at Vakten er lagt til, har en lengste sammenhengende friperiode i uka på nøyaktig 35 timer 0 minutter
**When** regelen kjører
**Then** Kandidaten er **ikke** utelukket av denne regelen

**Given** en Kandidat som etter at Vakten er lagt til, har en lengste sammenhengende friperiode i uka på 34 timer 59 minutter
**When** regelen kjører
**Then** Kandidaten er utelukket med årsaken «35-timersregelen»

**Given** en Vakt som krysser ukeskiftet (nattevakt fra søndag til mandag)
**When** regelen kjører
**Then** begge ukene sjekkes, og brudd i én av dem gir utelukkelse

**Given** en uke med sommertidsovergang (167 eller 169 timer)
**When** friperioden beregnes
**Then** den beregnes i faktisk forløpt tid

**Given** at Vakten ligger nær kanten av Turnusens periode
**When** regelen kjører
**Then** testdataene dekker hele kalenderuker, slik at regelen ikke må gjette på vakter utenfor perioden [ASSUMPTION]

**Given** testmodulen
**When** storien er ferdig
**Then** `tester/regelmotor/test_35_timersregelen.py` dekker alle grensetilfellene over, og resultatet er reproduserbart (FR5, NFR1, NFR8)

### Story 2.5: Ekskludert-boks med oppsummering av utelukkelser

As a turnusansvarlig,
I want å se hvor mange ansatte som ble utelukket og hvorfor,
So that jeg kan stole på at listen ikke bare skjuler folk (UX-DR15).

**Acceptance Criteria:**

**Given** en Vakt der noen Kandidater er utelukket
**When** kandidatflaten vises
**Then** under kandidatlisten vises en Ekskludert-boks med stiplet kant og bakgrunn `#f7f9fb`
**And** boksen viser totalt antall utelukkede og antall per Hard regel, for eksempel «21 utelukket av harde regler · 9 under kompetanse-minstekrav · 7 kolliderende vakt · …» (UX-DR23)

**Given** en Kandidat som bryter flere Harde regler
**When** oppsummeringen lages
**Then** Kandidaten telles én gang i totalen og én gang under hver regel den bryter, så summen per regel kan være større enn totalen

**Given** Ekskludert-boksen
**When** jeg trykker «Vis full liste ▾»
**Then** jeg ser hver utelukkede Ansatt med alle årsaker, og kan lukke listen igjen
**And** lenken kan nås og aktiveres med tastatur (UX-DR24)

**Given** API-et
**When** oppsummeringen returneres
**Then** den bygges som porten `UtelukkelsesOppsummering` i `domene/porter`, og konstrueres bare av `domene/regelmotor` (AD-1)

### Story 2.6: Tydelig melding når ingen kandidater er gyldige

As a turnusansvarlig,
I want en tydelig forklaring når ingen ansatte kan ta vakten,
So that jeg ikke tror at listen er tom på grunn av en feil eller treg lasting (FR6).

**Acceptance Criteria:**

**Given** en Vakt der alle Kandidater er utelukket (Vakt #4189 i testdataene)
**When** kandidatflaten lastes
**Then** API-et svarer med 200 og `status: "ingen_gyldige_kandidater"`, ikke en HTTP-feil (AD-4)
**And** flaten viser tomtilstanden med sirkulært «!»-ikon og teksten «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» (UX-DR16)
**And** Ekskludert-boksen vises fortsatt, slik at jeg ser hvorfor alle er utelukket

**Given** kandidatflatens tre tilstander: laster, feil og ingen gyldige kandidater
**When** de vises
**Then** de har ulik tekst og ulikt visuelt uttrykk, og en test verifiserer at ingen to av dem er like (FR6)

**Given** tomtilstanden
**When** den vises
**Then** handlingsforslag som «del opp vakten» vises ikke som knapper eller funksjoner, fordi de ikke er FR-er (UX-DR16)

## Epic 3: Godkjenning av erstatter

Turnusansvarlig velger en gyldig kandidat og godkjenner i to steg. Vakten blir bemannet gjennom én eneste skrivevei, og bekreftelsen vises på vaktoversikten. Etter dette epicet fungerer hele flyten fra innlogging til godkjenning. (ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06.)

### Story 3.1: Velge kandidat og se godkjenningsflaten

As a turnusansvarlig,
I want å velge en hvilken som helst gyldig kandidat og se et bekreftelsesbilde før noe endres,
So that jeg har kontroll over beslutningen og ingenting skjer før jeg bekrefter (FR12, NFR5).

**Acceptance Criteria:**

**Given** listen over Gyldige kandidater på kandidatflaten
**When** jeg velger en Kandidat, uansett plassering i listen
**Then** jeg kommer til Godkjenning-flaten, som er en egen flate med egen URL og ikke en dialog (UX-DR17)
**And** brødsmulestien viser `Turnus > <avdeling> > Vakt #<nr> > Kandidater > Godkjenning` (UX-DR3)

**Given** Godkjenning-flaten
**When** den vises
**Then** kandidatkortet viser navnet (`heading`) og Kompetansenivået (UX-DR17)
**And** bekreftelsesboksen viser hvem som settes inn i hvilken Vakt, med knappene «Avbryt» (`button-secondary`) og «Godkjenn erstatning» (`button-primary`) (UX-DR19, UX-DR22)
**And** statuslinjen «Ikke gjennomført — venter på eksplisitt godkjenning» vises (UX-DR19)

**Given** at jeg har åpnet Godkjenning-flaten
**When** jeg ikke har trykket «Godkjenn erstatning»
**Then** Turnusen og Vakten er uendret i databasen, og en test verifiserer dette (FR12)

**Given** Godkjenning-flaten
**When** jeg trykker «Avbryt»
**Then** jeg kommer tilbake til kandidatflaten, og ingen tilstand er endret (UX-DR19)

**Given** en URL til Godkjenning for en Ansatt som er utelukket av en Hard regel, eller som ikke finnes
**When** jeg åpner den
**Then** API-et svarer med feilformen `{ "kode", "melding" }`, og flaten viser en nøytral melding fra tekstlisten, ikke et bekreftelsesbilde (AD-4, NFR2)

**Given** Godkjenning-flaten
**When** jeg bruker bare tastatur
**Then** jeg kan nå og aktivere begge knappene (UX-DR24)

### Story 3.2: Gjennomføre godkjenning og bemanne vakten

As a turnusansvarlig,
I want å bekrefte erstatteren eksplisitt og se at vakten er bemannet,
So that vaktendringen blir gjennomført, men bare når jeg har bestemt det (FR12).

**Acceptance Criteria:**

**Given** Godkjenning-flaten for en Gyldig kandidat
**When** jeg trykker «Godkjenn erstatning»
**Then** API-et kjører de Harde reglene på nytt for Kandidaten før noe lagres
**And** hvis Kandidaten fortsatt er gyldig, lagres en Godkjenning (hvem, hvilken Vakt, når), og Vakten blir bemannet med Kandidaten

**Given** lagringsadapteren
**When** storien er ferdig
**Then** tabellen for Godkjenning er opprettet i denne storien
**And** `adaptere/lagring` har én eneste skrivefunksjon for Godkjenning som krever et fullstendig Godkjenning-objekt, og den er den eneste kodeveien som kan markere en Vakt som bemannet (AD-5)
**And** en test verifiserer at ingen andre API-endepunkter endrer bemanningen av en Vakt

**Given** at Kandidaten ikke lenger er gyldig når jeg trykker «Godkjenn erstatning», for eksempel fordi data er endret siden flaten ble åpnet
**When** API-et kjører reglene på nytt
**Then** ingenting lagres, og jeg får en nøytral melding om at Kandidaten ikke lenger er gyldig (AD-4, NFR2)

**Given** en Vakt som allerede er bemannet
**When** det sendes en ny godkjenning for den, for eksempel ved dobbeltklikk
**Then** den andre godkjenningen avvises med en feilkode, og det finnes bare én Godkjenning for Vakten

**Given** en vellykket godkjenning
**When** den er lagret
**Then** jeg sendes til Vaktvalg, der en kort bekreftelse vises øverst, for eksempel «Erstatning bekreftet — Jonas Bakke er satt opp på Vakt #4127» (UX-DR20)
**And** Vakten vises ikke lenger under «Krever handling», men blant de bemannede vaktene

**Given** hele systemet
**When** det brukes
**Then** det finnes ingen kodevei der en Godkjenning gjennomføres automatisk eller uten at turnusansvarlig trykker «Godkjenn erstatning» (FR12, NFR5)
**And** ingen SMS eller annen varsling sendes til den valgte Kandidaten (UX-DR26)

## Epic 4: Rangering etter kostnad, arbeidsbelastning og kompetanse

De gyldige kandidatene rangeres. Tabellen viser kostnadstype, arbeidsbelastningslinje og kompetansenærhet, og avviksnotatet vises når turnusansvarlig velger en annen enn nr. 1. Alle beregninger er deterministiske og ligger i `domene/regelmotor`, uten KI (NFR1, NFR3).

> ✅ **Epicet er ikke lenger blokkert.** ÅB-1 (vekting), ÅB-2 (kostnadsmodell) og ÅB-3 (arbeidsbelastningsterskel) er alle løst 2026-10-06 — se PRD §4.3, §4.4 og § Åpne beslutninger.

### Story 4.1: Timer i perioden per kandidat

As a turnusansvarlig,
I want å se hvor mange timer hver gyldig kandidat allerede er satt opp på i perioden,
So that jeg ser hvem som allerede har mye å gjøre (FR8).

**Acceptance Criteria:**

**Given** kandidatlisten
**When** den vises
**Then** hver Gyldig kandidat har en kolonne med antall timer Kandidaten er satt opp på i Turnusens periode, uten Vakten som skal bemannes

**Given** Kandidatens øvrige Vakter i Turnusen
**When** timene beregnes
**Then** summen er konsistent med vaktene (FR8), beregnet i faktisk forløpt tid i `Europe/Oslo`, slik at en nattevakt over sommertidsovergangen teller riktig antall timer
**And** en testmodul dekker vanlige vakter, nattevakt over midnatt og begge sommertidsovergangene, og resultatet er reproduserbart (NFR1)

**Given** en Kandidat uten andre Vakter i perioden
**When** timene vises
**Then** verdien er 0, ikke tom

### Story 4.2: Arbeidsbelastningslinje med terskel

ÅB-3 er løst 2026-10-06 — se PRD §4.3, FR-8 for terskelen brukt i akseptansekriteriene under.

As a turnusansvarlig,
I want en linje som viser arbeidsbelastningen i forhold til en terskel,
So that jeg ser med et blikk hvem som nærmer seg for mye (FR8).

**Acceptance Criteria:**

**Given** terskelen i PRD §4.3 (planlagte timer denne uken, uten vurdert Vakt, ÷ 36 timer)
**When** arbeidsbelastningen beregnes
**Then** domenekjernen regner ut prosent av terskel deterministisk (NFR1)

**Given** en Kandidat under terskelgrensen (~90 %)
**When** linjen vises
**Then** den er 110×7px, fylt proporsjonalt og i `accent` (UX-DR9)

**Given** en Kandidat ved eller over terskelgrensen
**When** linjen vises
**Then** fyllet er `warn`, aldri rødt, og det er ingen tekstlig advarsel, bare fargeskifte (UX-DR9)

**Given** testmodulen
**When** storien er ferdig
**Then** grensetilfellene rett under, nøyaktig på og over terskelgrensen er dekket

### Story 4.3: Forenklet kostnad per kandidat

ÅB-2 er løst 2026-10-06 — se PRD §4.3 for kostnadsmodellen brukt i akseptansekriteriene under.

As a turnusansvarlig,
I want å se om vakten blir ordinær sats eller overtid for hver kandidat, og hva det koster per time,
So that jeg kan ta hensyn til kostnaden i valget (FR7).

**Acceptance Criteria:**

**Given** kostnadsmodellen i PRD §4.3 (individuell timelønn, ordinær terskel 36 t/uke, 150 % sats utover)
**When** kostnaden beregnes for en Gyldig kandidat
**Then** domenekjernen sammenligner Kandidatens planlagte timer denne uken (inkl. denne Vakten) mot 36-timersterskelen, og beregner beløpet: timer til og med 36 t til ordinær sats, timer utover til 150 % sats (FR7)
**And** beregningen er uavhengig av KI (NFR3)
**And** satsfeltene som trengs, legges til i lagringen i denne storien, og testdataene får fiktive satser (NFR11)

**Given** kandidatlisten
**When** kostnaden vises
**Then** «Ordinær» vises i `ok` eller «Overtid» i `warn`, alltid med kr/t under i `meta`, og aldri i rødt (UX-DR10)

**Given** testmodulen
**When** storien er ferdig
**Then** grensetilfellene rett under og rett over overtidsgrensen er dekket
**And** samme Kandidat og Vakt gir samme kostnad ved gjentatt kjøring (FR7, NFR1)

### Story 4.4: Rangering av gyldige kandidater

ÅB-1 (vekting), ÅB-2 (kostnadsmodell) og ÅB-3 (arbeidsbelastningsterskel) er alle løst 2026-10-06 — se PRD §4.3 og §4.4 for de fullstendige modellene, brukt i akseptansekriteriene under.

As a turnusansvarlig,
I want at de gyldige kandidatene er rangert, med nøkkeltallene synlige i hver rad,
So that jeg ser hvem som passer best uten å sammenligne alle manuelt (FR9, SM-3).

**Acceptance Criteria:**

**Given** poengmodellen i PRD §4.4 (Kostnad 30 %, Arbeidsbelastning 30 %, Ansattpreferanse 20 %, Kompetansenærhet 20 %, hver 0–100 poeng)
**When** Rangeringen kjører
**Then** alle Gyldige kandidater får en vektet totalscore og rangeres synkende etter den (FR9)
**And** Rangeringen skjer bare i `domene/regelmotor` og er deterministisk: samme input gir samme rekkefølge, også ved likhet mellom kandidater (NFR1)

**Given** porten `RangertKandidat` i `domene/porter`
**When** Rangeringen produserer resultatet
**Then** hver `RangertKandidat` har minst kandidat-referanse, Kompetansenivå, kostnadstype og beløp, arbeidsbelastning (timer og prosent av terskel), rangeringsplass og eventuell `TolketPreferanse` (AD-1)
**And** bare `domene/regelmotor` konstruerer `RangertKandidat`

**Given** at KI-tolkningen av preferanser ikke er på plass ennå (Epic 5)
**When** Rangeringen kjører uten `TolketPreferanse` for en Kandidat
**Then** preferansefaktoren bidrar nøytralt, og Rangeringen fungerer likevel

**Given** testscenarioet der billigste Kandidat har klart dårligere verdier på de andre Myke faktorene
**When** Rangeringen kjører
**Then** billigste Kandidat er ikke rangert øverst (FR9, SM-6)

**Given** testscenarioet der ingen Gyldig kandidat er fullt kvalifisert
**When** Rangeringen kjører
**Then** Kandidaten nærmest full kvalifisering rangeres høyere enn de som er lenger unna, med mindre de andre Myke faktorene motsier det (FR9)

**Given** kandidatflaten
**When** Rangeringen vises
**Then** rangeringstabellen har kolonnene rangeringsnummer, kandidat (navn og `meta`-undertekst), Kompetansenivå med tag, kostnad, arbeidsbelastning, preferanse med tag og en tom kolonne for ekspander-lenken fra Epic 5 (UX-DR7)
**And** rangeringsnummeret vises i `accent`, fet og 14px (UX-DR8)
**And** annenhver rad har `row-alt`, og kompetansenærhet vises som rekkefølge, ikke som et eget merke (UX-DR7)
**And** den alfabetiske listen fra story 2.1 er erstattet av tabellen

### Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten

ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06. Storien bygger på Rangeringen i 4.4 og nøkkeltallene i 4.2 og 4.3, og kan implementeres når de er ferdige.

As a turnusansvarlig,
I want å se nøkkeltallene for valgt kandidat, og en nøytral sammenligning når jeg velger en annen enn nr. 1,
So that jeg tar et bevisst valg når jeg avviker fra anbefalingen (FR12).

**Acceptance Criteria:**

**Given** Godkjenning-flaten
**When** kandidatkortet vises
**Then** det viser kostnadsindikator og arbeidsbelastningslinje i tillegg til navn og Kompetansenivå (UX-DR17)

**Given** at valgt Kandidat er den topprangerte
**When** Godkjenning-flaten vises
**Then** det vises ikke noe avviksnotat (UX-DR18)

**Given** at valgt Kandidat ikke er den topprangerte
**When** Godkjenning-flaten vises
**Then** avviksnotatet «Avvik fra anbefalt rangering» vises med stiplet kant, med kostnad, Kompetansenivå og arbeidsbelastning side om side for valgt og topprangert Kandidat (UX-DR18)
**And** notatet inneholder «Turnushjelperen anbefaler, den bestemmer aldri selv.»
**And** notatet blokkerer ikke godkjenningen, og teksten antyder ikke at valget er feil (UX-DR23)

### Story 4.6: Rangeringstabellen på smalere skjermer

> **Åpen beslutning ÅB-7 (blokkerer ikke). Midlertidig løsning:** Breakpoints og stablingsmønster er ikke besluttet. Storien bygger på forslaget i EXPERIENCE.md § Responsive & Platform.

As a turnusansvarlig,
I want å kunne bruke Turnushjelperen på nettbrett og mobil,
So that jeg kan finne en erstatter også når jeg ikke sitter ved PC-en.

**Acceptance Criteria:**

**Given** en bred skjerm (desktop)
**When** kandidatflaten vises
**Then** hele rangeringstabellen vises med alle kolonner (UX-DR25)

**Given** en nettbrettbredde
**When** kandidatflaten vises
**Then** tabellen beholder radform, men mindre kritiske opplysninger flyttes inn i raden i stedet for å ha egen kolonne (UX-DR25)

**Given** en mobilbredde
**When** kandidatflaten vises
**Then** hver kandidat vises som et stablet kort med rangering, navn og kostnad øverst og arbeidsbelastning under, uten horisontal scroll (UX-DR25)

**Given** alle flatene (Logg inn, Vaktvalg, kandidatflaten og Godkjenning)
**When** de vises på mobilbredde
**Then** de kan brukes uten horisontal scroll

## Epic 5: KI-forklaring av avveininger

Preferansetekstene tolkes én gang og lagres. Hver rangert kandidat får en Avveining, med reservetekst hvis modellen feiler og kjøretidstest for lekkasje. KI beregner aldri Harde regler, arbeidstid, kostnad eller Rangering (NFR3). `adaptere/ki` kalles bare fra `adaptere/api` og ser bare det portene definerer (AD-1).

> ✅ **Epicet er ikke lenger blokkert.** Story 5.1 kan implementeres parallelt med Epic 4. Story 5.2 til 5.6 bygger på `RangertKandidat` fra story 4.4 — ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06, så Epic 4 kan ferdigstilles og levere den porten.

### Story 5.1: Tolke tekstbaserte ansattpreferanser med KI

As a turnusansvarlig,
I want at de skrevne preferansene til de ansatte blir tolket til noe systemet kan bruke,
So that ønsker som «vil gjerne ha flere vakter» kan tas hensyn til (FR10).

**Acceptance Criteria:**

**Given** en Ansatt med forhåndsdefinert preferansetekst (ÅB-4)
**When** tolkningen kjøres
**Then** `adaptere/ki` sender teksten til Gemini og returnerer en `TolketPreferanse` validert mot Pydantic-modellen i `domene/porter` (AD-1)
**And** bare `adaptere/ki` konstruerer `TolketPreferanse`

**Given** en tolket preferanse
**When** den er laget
**Then** den lagres av `adaptere/lagring` knyttet til Ansatt, og feltene som trengs, legges til i denne storien (AD-1, AD-5)
**And** tolkningen kjøres bare én gang per Ansatt og preferansetekst, og kjøres på nytt bare når teksten endres
**And** Rangeringen kaller aldri KI live, men leser alltid den lagrede verdien (AD-1, NFR1)

**Given** at Gemini svarer med feil, tomt eller ugyldig svar under tolkning
**When** tolkningen kjøres
**Then** ingen `TolketPreferanse` lagres for Ansatten, preferansen regnes som «Ingen registrert», og systemet krasjer ikke (NFR4)

**Given** konfigurasjonen
**When** storien er ferdig
**Then** API-nøkkelen og modellnavnet for Gemini leses fra miljøvariabler og er dokumentert uten verdi i `.env.example` (NFR7)
**And** testene bruker en falsk KI-adapter og krever verken nettverk eller API-nøkkel

**Given** kandidatlisten
**When** den vises
**Then** preferanse-taggen viser den tolkede preferansen, for eksempel «Ønsker flere vakter» eller «Fleksibel», eller «Ingen registrert» (UX-DR11)

### Story 5.2: Rangeringen bruker tolkede preferanser

> ✅ **ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06 (se § Åpne beslutninger).** Storien bygger på Rangeringen i story 4.4.

As a turnusansvarlig,
I want at de ansattes preferanser påvirker rangeringen,
So that den som ønsker flere vakter, kan få dem når alt annet er likt (FR10, SM-7).

**Acceptance Criteria:**

**Given** lagrede `TolketPreferanse`-verdier
**When** `adaptere/api` orkestrerer Rangeringen
**Then** verdiene sendes inn i `domene/regelmotor` som vanlig input, og domenekjernen kaller aldri KI (AD-1)

**Given** to Kandidater som er like på alle andre Myke faktorer, der bare den ene ønsker flere vakter
**When** Rangeringen kjører
**Then** Kandidaten som ønsker flere vakter, rangeres høyere (SM-7)

**Given** samme lagrede preferanser og samme øvrige input
**When** Rangeringen kjøres flere ganger
**Then** rekkefølgen er lik hver gang (NFR1, SM-5)

### Story 5.3: Avveining per kandidat

> ✅ **ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06 (se § Åpne beslutninger).** Storien bygger på `RangertKandidat` fra story 4.4.

As a turnusansvarlig,
I want en forklaring i klartekst av hva som trekker opp og ned for hver kandidat,
So that jeg forstår hvorfor én er rangert over en annen og kan stå inne for valget (FR11, SM-4).

**Acceptance Criteria:**

**Given** en `RangertKandidat`
**When** `adaptere/api` ber `adaptere/ki` om en forklaring
**Then** `adaptere/ki` får bare data formet som porten `RangertKandidat`, og kan ikke kalle inn i domenekjernen for å hente mer (AD-1)
**And** forklaringen inneholder hvorfor Kandidaten kan ta Vakten, hva som trekker opp, hva som trekker ned, kostnadsvurderingen og relevante preferanser (FR11)

**Given** rangeringstabellen
**When** siden lastes
**Then** den topprangerte Kandidatens Avveining er utvidet, og de andre er kollapset bak «Vis begrunnelse ▾» (UX-DR12)
**And** «▲ Trekker opp» vises i `ok` og «▼ Trekker ned» i `danger`, på bakgrunn `#f2f6f9`
**And** å åpne én rad lukker ingen andre, og lenken skifter til «Skjul begrunnelse ▴»
**And** lenkene kan nås og aktiveres med tastatur (UX-DR24)

**Given** Godkjenning-flaten
**When** kandidatkortet vises
**Then** Avveiningen for valgt Kandidat vises i forklaringspanelet (UX-DR12, UX-DR17)

**Given** en Avveining
**When** den er generert
**Then** den lagres ikke, men genereres på nytt hver gang Rangeringen vises (arkitektur § Structural Seed)

### Story 5.4: Reservetekst når KI-forklaringen feiler

> ✅ **ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06 (se § Åpne beslutninger).** Storien bygger på story 5.3.

As a turnusansvarlig,
I want at systemet fortsetter å virke og sier fra tydelig når KI-forklaringen mangler,
So that jeg aldri får en anbefaling uten grunnlag, og aldri står fast (FR11, NFR4).

**Acceptance Criteria:**

**Given** at Gemini svarer med feil, tidsavbrudd, fartsgrense, tomt svar eller et svar som ikke kan brukes
**When** Avveiningen hentes
**Then** API-et svarer med 200 og `status: "avveining_feilet"` for den Kandidaten, ikke en HTTP-feil (AD-4)
**And** forklaringspanelet viser en forhåndsdefinert reservetekst fra frontendens tekstliste i stedet for Avveiningen (UX-DR14, UX-DR23)
**And** resten av raden, Rangeringen og godkjenningen fungerer som normalt

**Given** en Avveining som nevner navnet på en Ansatt som er utelukket av en Hard regel
**When** svaret valideres i `adaptere/ki`
**Then** det forkastes og behandles som ubrukelig, så reserveteksten vises i stedet (NFR2, NFR10)

**Given** testene
**When** storien er ferdig
**Then** en falsk KI-adapter dekker hver feiltype over, og testene verifiserer at systemet ikke krasjer og at reserveteksten vises (FR11)

### Story 5.5: Rader vises før forklaringene er ferdige

> ✅ **ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06 (se § Åpne beslutninger).** Storien bygger på story 5.3.

As a turnusansvarlig,
I want å se rangeringen med en gang, mens forklaringene lastes etter hvert,
So that jeg kan begynne å vurdere kandidatene uten å vente på KI (UX-DR13).

**Acceptance Criteria:**

**Given** at regelmotoren og Rangeringen er ferdige
**When** kandidatflaten lastes
**Then** alle rader med nøkkeltall vises med en gang, uten å vente på noen Avveining [ASSUMPTION, UX-DR13]
**And** hver Avveining lastes inn i sin rad etter hvert, med en lastetilstand som er ulik både reserveteksten og tomtilstanden

**Given** at transporten for progressiv lasting er en utsatt beslutning (arkitektur § Deferred)
**When** storien implementeres
**Then** valget mellom streaming, polling og separate kall per Kandidat tas i storien og dokumenteres i KI-loggen

**Given** at én Avveining feiler
**When** de andre lastes
**Then** de andre radene påvirkes ikke (NFR4)

### Story 5.6: Test av at utelukkede kandidater aldri når KI-laget

> ✅ **ÅB-1, ÅB-2 og ÅB-3 er alle løst 2026-10-06 (se § Åpne beslutninger).** Storien bygger på story 5.3.

As a turnusansvarlig,
I want bevis for at en utelukket ansatt aldri kan bli anbefalt eller nevnt av KI,
So that jeg kan stole på at de harde reglene alltid gjelder (NFR2, SM-2).

**Acceptance Criteria:**

**Given** et testscenario med kjente utelukkelser for hver av de fire Harde reglene
**When** hele flyten kjøres gjennom `adaptere/api` med en falsk KI-adapter som registrerer alt den mottar
**Then** ingen kandidat-ID som sendes til `adaptere/ki`, finnes blant de utelukkede ID-ene fra `domene/regelmotor` (AD-1)
**And** ingen utelukket Kandidat finnes i Rangeringen eller i API-svaret til frontend

**Given** den statiske import-linter-kontrakten fra story 2.1
**When** testkommandoen kjøres
**Then** både kontrakten og kjøretidstesten kjøres, og en av dem feiler hvis grensen brytes (AD-1, AD-2)

**Given** kvalitetssikringen i emnet
**When** storien er ferdig
**Then** testen og hva den beviser, er beskrevet i KI-loggen, slik at den kan brukes som dokumentasjon av kvalitetssikring
