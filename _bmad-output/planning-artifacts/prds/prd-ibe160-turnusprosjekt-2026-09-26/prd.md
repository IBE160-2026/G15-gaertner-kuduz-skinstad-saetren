---
title: "PRD: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-09-26
---

# PRD: Turnushjelperen
*Produktnavn bekreftet av gruppen 2026-09-26. Prosjektet omtales fortsatt som «IBE160 Turnusprosjekt» i emnesammenheng (proposal, refleksjonsrapport); «Turnushjelperen» er navnet på selve web-appen.*

## 0. Dokumentets formål

Denne PRD-en er skrevet for prosjektgruppen selv (4 medlemmer) og bygger videre på `product-brief.md` og dens `addendum.md`. Den definerer *hva* Turnushjelperen skal gjøre og *hvorfor*, som grunnlag for arkitektur, epics/stories og den godkjente proposalen til IBE160. Krav er gruppert per funksjon med globalt nummererte FR-er; antakelser er merket `[ASSUMPTION]` inline og samlet i §9.

## 1. Visjon

Når en planlagt vakt i en eksisterende turnus plutselig må dekkes av noen andre, skal den turnusansvarlige gå fra «denne vakten mangler bemanning» til et begrunnet forslag om hvem som bør ta den — uten å måtte kontrollere alle 20–30 ansatte manuelt.

Turnushjelperen er en web-app som fungerer som beslutningsstøtte for én vaktendring om gangen: harde regler (kompetanse, kolliderende vakter, arbeidstids- og hviletidskrav) filtrerer bort ugyldige kandidater, en enkel og reproduserbar modell rangerer de gyldige etter arbeidsbelastning, kostnad og ansattpreferanser, og KI tolker de tekstbaserte preferansene og forklarer avveiningene mellom kandidatene i klartekst. Turnushjelperen anbefaler — den bestemmer aldri selv, og den kan aldri anbefale en kandidat som en hard regel har utelukket.

Dette betyr noe fordi det viser en konkret, testbar arbeidsdeling mellom regelbasert programmering og generativ KI: det som må være forutsigbart (lovkrav, kostnad) forblir deterministisk, mens det som er mykt og menneskelig (preferanser, avveininger) får KI-støtte — uten at KI noensinne får siste ord.

En enkel digital turnusløsning kan vise hvem som er ledig; en regelbasert løsning kan filtrere bort ugyldige kandidater. Turnushjelperens særpreg er kombinasjonen av kontrollerbare regler, enkel kostnadsberegning, ansattpreferanser, forklarbar KI-støtte og menneskelig sluttbeslutning — ikke én enkelt unik teknologi (product-brief.md, «Hva gjør dette annerledes»).

*Langsiktig retning utover v1 er beskrevet i `product-brief.md` («Visjon») og er ikke del av denne PRD-en.*

## 2. Målgruppe

### 2.1 Jobs To Be Done

- **Funksjonelt:** Raskt identifisere hvilke av 20–30 ansatte som faktisk kan ta en konkret vakt, uten å sjekke alle manuelt mot kompetanse, kolliderende vakter og arbeidstids-/hviletidsregler.
- **Funksjonelt:** Sammenligne de gyldige kandidatene på kostnad (ordinær vs. overtid), arbeidsbelastning og registrerte preferanser — og forstå *hvorfor* én kandidat rangeres over en annen.
- **Emosjonelt/sosialt:** Kunne stå inne for beslutningen overfor både den ansatte som får vakten og virksomheten — vite at valget er saklig begrunnet, ikke bare «den jeg husket først».
- **Kontekstuelt:** Håndtere dette i en presset situasjon (vakten mangler bemanning *nå*), der løsningen må gi et forståelig beslutningsgrunnlag raskt, ikke en fullstendig ny turnusplan.

### 2.2 Ikke-brukere (v1)

Ansatte er **ikke** brukere av Turnushjelperen i v1 — de kan verken logge inn, se egne vakter, eller registrere preferanser selv (preferanser legges inn av turnusansvarlig eller forhåndsdefineres i testdata). En lesende ansattoversikt og vaktbytte mellom ansatte er eksplisitt vurdert og lagt til stretch goals / senere versjon (se addendum §3). Dette skiller Turnushjelperen fra en ansattportal.

### 2.3 Sentrale brukerreiser

- **UJ-1. Turnusansvarlig finner en erstatter for en vakt som mangler bemanning.**
  - **Persona + kontekst:** Kari, turnusansvarlig for en avdeling med ca. 25 ansatte, får beskjed om at en ansatt har meldt fra syk til en vakt i morgen.
  - **Inngangstilstand:** Kari er innlogget i Turnushjelperen og har den eksisterende turnusen tilgjengelig.
  - **Sti:** (1) Kari velger den konkrete vakten som må bemannes på nytt. (2) Systemet viser en rangert liste over gyldige kandidater — ansatte som ikke oppfyller kompetanse-minstekravet, har kolliderende vakt, eller ville brutt hviletids-/arbeidstidsregler, er allerede filtrert bort. (3) Kari åpner en kandidat og ser kostnadsvurdering, arbeidsbelastning, og en KI-generert forklaring av avveiningene (f.eks. «rangeres over nr. 2 fordi overtidskostnaden er lavere, selv om nr. 2 har uttrykt ønske om flere vakter»). (4) Kari sammenligner 2–3 kandidater på denne måten.
  - **Klimaks:** Kari ser tydelig hvorfor den øverste kandidaten er anbefalt, og stoler på grunnlaget uten å måtte sjekke de resterende 20+ ansatte manuelt.
  - **Oppløsning:** Kari velger kandidaten hun mener er riktig (ikke nødvendigvis den øverste) og bekrefter valget — Turnushjelperen gjennomfører ingen endring på egen hånd.
  - **Edge case:** Ingen kandidater er gyldige (alle filtrert bort av harde regler) — Turnushjelperen må vise dette tydelig i stedet for en tom eller misvisende liste. **[ASSUMPTION]** Nøyaktig hvordan «ingen gyldige kandidater» presenteres er ikke bestemt ennå — dekkes som egen FR i §4.

**[ASSUMPTION]** Persona-navnet «Kari» og detaljene rundt henne er oppdiktet for å gjøre reisen konkret — dette er ikke ment å representere en reell bruker, kun en fiktiv illustrasjon slik brief-omfanget (fiktiv turnus, ingen ekte personopplysninger) tilsier.

## 3. Ordliste

- **Turnus** — En eksisterende bemanningsplan for en avdeling, bestående av vakter tildelt ansatte over en periode. Fiktiv i v1 (20–30 ansatte).
- **Vakt** — En enkelt planlagt arbeidsøkt for én ansatt, med start-/sluttidspunkt og et kompetansekrav.
- **Turnusansvarlig** — Primærbrukeren. Den eneste rollen som har tilgang til Turnushjelperen i v1.
- **Kandidat** — En ansatt som vurderes for å overta en Vakt som må bemannes på nytt.
- **Gyldig kandidat** — En Kandidat som ikke er utelukket av noen Hard regel.
- **Hard regel** — Et absolutt krav (kompetanse, kolliderende vakt, hviletid, maks arbeidstid) som utelukker en Kandidat uten unntak. Beregnes deterministisk — aldri av KI.
- **Kompetansenivå** — Hvor godt en ansatt er opplært for en gitt type Vakt, fra delvis opplært til fullt kvalifisert. Avgjør (a) om Kandidaten oppfyller Vaktens minstekrav (Hard regel, §4.2), og (b) hvor nær Kandidaten er full kvalifisering, blant Gyldige kandidater (Myk faktor, §4.4).
- **Myk faktor** — Et hensyn som brukes til å rangere Gyldige kandidater seg imellom: kostnad, arbeidsbelastning, Ansattpreferanse, og hvor nært Kandidatens Kompetansenivå er full kvalifisering for vakttypen.
- **Ansattpreferanse** — Tekstbasert informasjon om en ansatts ønsker eller begrensninger, tolket av KI-laget som del av Rangeringen.
- **Rangering** — Den sorterte listen over Gyldige kandidater, ordnet etter Myke faktorer.
- **Avveining** — KI-generert forklaring av hvorfor én Kandidat rangeres over en annen.
- **Godkjenning** — Turnusansvarliges eksplisitte, endelige valg av Kandidat. Ingen endring anses gjennomført før Godkjenning er gitt.

## 4. Funksjoner

### 4.1 Vaktvalg

**Beskrivelse:** Turnusansvarlig velger en eksisterende Vakt i Turnusen som må bemannes på nytt. Dette utløser kandidatvurdering (§4.2–§4.4). Realiserer UJ-1.

**Funksjonelle krav:**

#### FR-1: Velge vakt som må bemannes på nytt

Turnusansvarlig kan velge én Vakt fra en eksisterende Turnus. Realiserer UJ-1.

**Konsekvenser (testbare):**
- Systemet viser Vaktens tidspunkt og kompetansekrav ved valg.
- Valget starter filtrering og Rangering av Kandidater (FR-2 til FR-9) uten ytterligere handling fra Turnusansvarlig.

### 4.2 Regelmotor (harde regler)

**Beskrivelse:** Et lite, godt testet utvalg harde regler filtrerer bort Kandidater som ikke kan ta Vakten. Utvalget følger addendumets anbefaling og er bekreftet av gruppen: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen (daglig hvile) og 35-timersregelen (ukentlig fri). Maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — addendum anbefaler et lite utvalg som beviselig fungerer, fremfor et stort utvalg som bare er halvveis på plass.

**Funksjonelle krav:**

#### FR-2: Filtrere på kompetanse-minstekrav

Systemet kan utelukke en Kandidat hvis Kandidatens Kompetansenivå er under Vaktens definerte minstekrav.

**Konsekvenser (testbare):**
- 100 % av Kandidatene med Kompetansenivå under minstekravet filtreres bort i definerte testscenarioer.
- Blant Gyldige kandidater rangeres Kompetansenivå videre som en Myk faktor, ikke som endelig utelukkelse — se FR-9.

#### FR-3: Filtrere på kolliderende vakt

Systemet kan utelukke en Kandidat som allerede har en Vakt som overlapper i tid med Vakten som skal bemannes.

**Konsekvenser (testbare):**
- 100 % av Kandidatene med tidsmessig overlappende Vakt filtreres bort i definerte testscenarioer.

#### FR-4: Filtrere på 11-timersregelen (daglig hvile)

Systemet kan utelukke en Kandidat som ville fått mindre enn 11 timer sammenhengende hvile per 24 timer dersom Kandidaten tar Vakten.

**Konsekvenser (testbare):**
- 100 % av Kandidatene som ville brutt 11-timersregelen filtreres bort i definerte testscenarioer.
- Samme Kandidat og samme Vakt gir samme filtreringsresultat hver gang (reproduserbart).

#### FR-5: Filtrere på 35-timersregelen (ukentlig fri)

Systemet kan utelukke en Kandidat som ville fått mindre enn 35 timer sammenhengende fri per 7 dager dersom Kandidaten tar Vakten.

**Konsekvenser (testbare):**
- 100 % av Kandidatene som ville brutt 35-timersregelen filtreres bort i definerte testscenarioer.

#### FR-6: Vise når ingen kandidater er gyldige

Systemet skal informere Turnusansvarlig med en eksplisitt melding når ingen Kandidater er gyldige for den valgte Vakten, i stedet for å vise en tom liste. Realiserer UJ-1 (edge case).

**Konsekvenser (testbare):**
- Meldingen for «ingen gyldige kandidater» er tekstlig og visuelt forskjellig fra en laste- eller feiltilstand, slik at Turnusansvarlig ikke kan forveksle de to.

**Feature-spesifikke NFR-er:**
- En Kandidat utelukket av en Hard regel skal aldri kunne opptre i Rangeringen (§4.4) eller nevnes av KI-forklaringen (§4.5) — testbar invariant.
- Harde regler beregnes deterministisk. KI har ingen rolle i denne funksjonen.

### 4.3 Kostnads- og arbeidsbelastningsvurdering

**Beskrivelse:** For hver Gyldig kandidat beregnes en forenklet kostnadsvurdering (ordinær sats vs. overtidssats) og gjeldende arbeidsbelastning. Dette er to av de Myke faktorene Rangeringen (§4.4) bygger på.

**Funksjonelle krav:**

#### FR-7: Beregne forenklet kostnad per kandidat

Systemet kan beregne en forenklet kostnadsvurdering for hver Gyldig kandidat, basert på om Vakten utløser ordinær sats eller overtidssats for Kandidaten.

**Konsekvenser (testbare):**
- Samme Kandidat og samme Vakt gir samme beregnet kostnad hver gang (reproduserbart).
- Beregningen er ikke avhengig av KI.

**Out of Scope:**
- Full lønnskostnad med alle tillegg, avgifter og tariffregler (eksplisitt utenfor omfang, jf. brief).

#### FR-8: Vise gjeldende arbeidsbelastning per kandidat

Systemet kan vise hvor mye hver Gyldig kandidat allerede er satt opp til å arbeide i den aktuelle perioden.

**Konsekvenser (testbare):**
- Arbeidsbelastningen oppdateres konsistent med Turnusens øvrige Vakter for Kandidaten.

### 4.4 Rangering av kandidater

**Beskrivelse:** Gyldige kandidater rangeres etter Myke faktorer (§3). Rangeringen er ikke rent kostnadsstyrt — brief krever at minst ett scenario skal demonstrere at billigste Kandidat ikke nødvendigvis rangeres høyest.

**Funksjonelle krav:**

#### FR-9: Rangere gyldige kandidater

Systemet kan rangere alle Gyldige kandidater for en Vakt basert på et definert sett Myke faktorer.

**Konsekvenser (testbare):**
- Minst ett testscenario demonstrerer at den billigste Kandidaten ikke rangeres høyest, fordi andre Myke faktorer samlet sett veier tyngre.
- Når ingen Gyldig kandidat har full kvalifisering for vakttypen, rangeres Kandidaten med Kompetansenivå nærmest full kvalifisering høyere enn de som er lenger unna, forutsatt at dette ikke motsies av de andre Myke faktorene. **Eksempel** *(fiktivt, illustrerer regelen)*: Jonas' vakt krever spesialkompetanse; ingen tilgjengelig Kandidat er fullt kvalifisert, så den nærmest fullt opplærte Kandidaten rangeres øverst blant de Gyldige — forutsatt at hviletids- og arbeidstidsreglene fortsatt er overholdt.
- Samme input (Kandidater, Vakt, preferanser) gir samme rangeringsrekkefølge hver gang.

**Notes:**
- **[NOTE FOR PM]** Vekting mellom Myke faktorer ikke fullt bestemt — se §8, spørsmål 2.

### 4.5 KI-forklaring av avveininger

**Beskrivelse:** KI tolker tekstbaserte Ansattpreferanser og genererer en forståelig forklaring per Kandidat: hvorfor Kandidaten kan ta Vakten, hva som trekker opp, hva som trekker ned, kostnadsvurdering og relevante Ansattpreferanser. KI forklarer og tolker — den beregner aldri Harde regler, arbeidstid eller kostnad, og kan aldri overstyre Rangeringen eller utføre en endring selv.

**Funksjonelle krav:**

#### FR-10: Tolke tekstbaserte ansattpreferanser

Systemet kan bruke en språkmodell til å tolke tekstbaserte Ansattpreferanser og gjøre dem tilgjengelige som input til Rangeringen (§4.4).

**Konsekvenser (testbare):**
- Tolkede preferanser sendes som strukturert input til Rangeringen — språkmodellen utfører ikke selve rangeringsberegningen.

#### FR-11: Generere forklaring per kandidat

Systemet kan generere en KI-basert forklaring for hver Kandidat i Rangeringen: hvorfor Kandidaten kan ta Vakten, hvilke forhold som trekker opp, hvilke som trekker ned, kostnadsvurdering, og relevante Ansattpreferanser.

**Konsekvenser (testbare):**
- Forklaringen nevner aldri en Kandidat som er utelukket av en Hard regel (testbar invariant, jf. addendum §4).
- Ved feil, tomt eller ubrukelig svar fra språkmodellen viser systemet en forhåndsdefinert reservetekst eller feilmelding i stedet for KI-forklaringen — aldri en anbefaling uten gyldig grunnlag — og systemet fortsetter å fungere uten å krasje.

**Feature-spesifikke NFR-er:**
- Grensen mellom deterministisk lag (§4.2–§4.4) og KI-laget er en hard systemgrense: KI mottar allerede filtrerte og beregnede data, og kan ikke endre dem.

### 4.6 Godkjenning av erstatter

**Beskrivelse:** Turnusansvarlig velger og bekrefter hvilken Kandidat som skal settes inn i Vakten. Turnushjelperen gjennomfører aldri en endring på egen hånd.

**Funksjonelle krav:**

#### FR-12: Godkjenne valgt kandidat

Turnusansvarlig kan velge en hvilken som helst Gyldig kandidat fra Rangeringen — ikke nødvendigvis den øverst rangerte — og gi eksplisitt Godkjenning.

**Konsekvenser (testbare):**
- Ingen endring i Turnusen anses gjennomført før Godkjenning er gitt.
- Systemet kan ikke gjennomføre en Godkjenning automatisk eller uten Turnusansvarliges eksplisitte handling.

### 4.7 Innlogging

**Beskrivelse:** Enkel innlogging for Turnusansvarlig, slik at Turnushjelperen ikke er åpen for alle — ingen andre roller finnes i v1.

**Funksjonelle krav:**

#### FR-13: Logge inn som turnusansvarlig

Turnusansvarlig kan logge inn med brukernavn og passord for å få tilgang til Turnushjelperen.

**Konsekvenser (testbare):**
- Ingen funksjonalitet i §4.1–§4.6 er tilgjengelig uten gyldig innlogging.

**Out of Scope:**
- Flere roller, tilgangsnivåer eller SSO (eksplisitt utenfor omfang for v1, jf. brief).

## 5. Ikke-mål (eksplisitt)

Turnushjelperen v1 skal **ikke**:

- Generere en komplett Turnus fra bunnen av, eller optimalisere en hel Turnus automatisk.
- La KI beregne Harde regler, arbeidstid eller kostnad, eller la KI utføre selve Rangeringen — vurdert og forkastet (addendum §3): lovkrav og kostnad må være reproduserbare, en språkmodell gir sannsynlighet der loven krever determinisme.
- Håndtere vaktbytte mellom ansatte som kjernefunksjonalitet — vurdert og forkastet (addendum §3): det er et annet problem enn sykefravær (dobbel regelvalidering, ansatt som initiativtaker, forutsetter forhandlingsflyt), ikke en variant av dagens problemstilling.
- Garantere full juridisk etterlevelse av arbeidsmiljøloven, eller implementere komplette tariff-, lønns- eller overtidsregler.
- Beregne full lønnskostnad med alle tillegg og avgifter.
- Bruke ekte personopplysninger, eller integreres mot reelle HR-, lønns- eller turnussystemer.
- Håndtere flere kompliserte turnusendringer samtidig — kun én Vakt om gangen i v1.
- Automatisk gjennomføre et KI-forslag uten Godkjenning (§4.6).
- Inneholde en full ansattportal, avansert rollebasert autentisering, eller en generell KI-chat for ansatte.

**[NOTE FOR PM]** Ansattportal og mer avansert autentisering/KI-funksjonalitet er stretch goals dersom kjernen (§4) er ferdig og stabil — ikke en del av v1-leveransen.

## 6. MVP-omfang

### 6.1 Inkludert

- Én fiktiv Turnus med ca. 20–30 ansatte (§2.2, §4.1).
- Filtrering av Kandidater på fire Harde regler: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen (§4.2).
- Forenklet kostnads- og arbeidsbelastningsvurdering per Gyldig kandidat (§4.3).
- Rangering av Gyldige kandidater på flere Myke faktorer, inkludert kompetansenærhet (§4.4).
- KI-tolkning av tekstbaserte Ansattpreferanser og KI-generert forklaring per Kandidat (§4.5).
- Menneskelig Godkjenning som forutsetning for enhver endring (§4.6).
- Enkel innlogging for Turnusansvarlig (§4.7).

### 6.2 Utenfor omfang for MVP

- Alt listet i §5 Ikke-mål.

## 7. Suksesskriterier

**Primære**
- **SM-1**: 100 % av Kandidatene som bryter en implementert Hard regel filtreres bort i definerte testscenarioer. Validerer FR-2 til FR-5.
- **SM-2**: En Kandidat utelukket av en Hard regel blir aldri anbefalt av KI — testbar invariant. Validerer FR-9, FR-11.
- **SM-3**: Turnusansvarlig får presentert en kort, rangert liste over de mest aktuelle Kandidatene for en fiktiv Turnus (20–30 ansatte) uten å måtte kontrollere alle manuelt. Validerer FR-1, FR-9.
- **SM-4**: Systemet forklarer hvilke faktorer som påvirker Rangeringen av hver Kandidat. Validerer FR-11.
- **SM-5**: Samme strukturerte input gir samme resultat hver gang for Harde regler og kostnadsberegninger (reproduserbarhet). Validerer FR-2 til FR-9.
- **SM-6**: Minst ett scenario demonstrerer at den billigste Kandidaten ikke nødvendigvis rangeres høyest. Validerer FR-9.
- **SM-7**: KI tolker minst noen definerte tekstbaserte Ansattpreferanser og bruker dem i forklaringen. Validerer FR-10, FR-11.
- **SM-8**: Turnusansvarlig er alltid den som tar den endelige beslutningen (Godkjenning kreves). Validerer FR-12.
- **SM-9** *(teknisk kvalitet)*: Systemet kan bygges og kjøres fra et rent klonet repo, uten manuelle unntak eller udokumenterte oppsettsteg. Validerer hele leveransen (§4); addendum §6 peker på dette som et teknisk kvalitetskriterium som bør videreføres i PRD/spec.

**Motmetrikker (skal ikke optimeres)**
- **SM-C1**: Antall implementerte Harde regler skal ikke maksimeres på bekostning av testdekning per regel — addendums anbefaling («fire regler som beviselig fungerer er verdt mer enn tolv som er halvveis») veier tyngre enn regelmengde. Motvirker en eventuell trang til å utvide §4.2 uten tilsvarende testarbeid.
- **SM-C2**: Rask responstid på KI-forklaringen skal ikke optimeres på bekostning av at forklaringen faktisk er korrekt og aldri nevner en utelukket Kandidat. Motvirker SM-3/SM-4 ved å hindre at hastighet trumfer den testbare invarianten i SM-2.

## 8. Åpne spørsmål

1. **Bekreft med faglærer** om KI i selve produktet (ikke bare i utviklingsprosessen) er et karakterkrav eller et rent produktvalg (addendum §5). Bør avklares før proposal leveres.
2. Endelig innbyrdes vekting mellom Myke faktorer i Rangeringen (kostnad, arbeidsbelastning, Ansattpreferanse, kompetansenærhet, §4.4) — gruppen har bekreftet at kompetansenærhet skal telle tungt når ingen Kandidat er fullt kvalifisert, men fullstendig vekting for øvrig gjenstår. Avklares av gruppen før arkitektur/epics; ingen frist satt ennå.
3. Konkret detaljnivå i kostnadsmodellen (§4.3, FR-7) — nøyaktig hvilke satser og betingelser som skiller ordinær kostnad fra overtidskostnad.
4. Nøyaktig tekst/utforming av «ingen gyldige kandidater»-meldingen (§4.2, FR-6) — atferden er spesifisert (skal skille seg fra laste-/feiltilstand), men ordlyden er åpen for forslag fra resten av gruppen.

**Vurdert og bevisst utelatt fra denne PRD-en:** addendumets punkt om «arbeidsdeling og frister» er et prosjektstyringsspørsmål for gruppen, ikke et produktkrav — det hører hjemme i gruppens egen fremdriftsplan, ikke i PRD-en.

## 9. Antakelser-indeks

- Fra §2.3 (UJ-1): Persona-navnet «Kari» er oppdiktet for å gjøre brukerreisen konkret — representerer ingen reell bruker, i tråd med at Turnusen er fiktiv.
- Fra §4.2/§8: Regelutvalget (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen) er bekreftet av bruker; maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — revurderes bare hvis gruppen ønsker et bredere regelsett.
- Fra §7 (SM-9): Antakelse om at «kjører fra et rent klonet repo» er det addendum mener med teknisk kvalitetskriterium fra emnekravet — ikke eksplisitt bekreftet av gruppen, men utledet direkte fra addendum §6.
