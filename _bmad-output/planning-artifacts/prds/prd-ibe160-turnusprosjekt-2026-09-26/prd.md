---
title: "PRD: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-10-30
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
- **Hard regel** — Et absolutt krav (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen og 35-timersregelen i v1) som utelukker en Kandidat uten unntak. Beregnes deterministisk — aldri av KI.
- **Kompetansenivå** — Hvor godt en ansatt er opplært for en gitt type Vakt, fra delvis opplært til fullt kvalifisert. Avgjør om Kandidaten oppfyller Vaktens minstekrav (Hard regel, §4.2). Kompetansenivå gir ingen poeng i Rangeringen.
- **Myk faktor** — Et hensyn som brukes til å rangere Gyldige kandidater seg imellom: kostnad, arbeidsbelastning (Timebelastning og Ulempebelastning) og Ansattpreferanse.
- **Arbeidsbelastning** — Samlebetegnelse for Timebelastning og Ulempebelastning. De to beregnes, vektes og vises hver for seg (§4.3, §4.4).
- **Timebelastning** — Kandidatens planlagte timer i kalenderuken Vakten starter i, uten Vakten som vurderes, som andel av normaluken på 36 timer (FR-8).
- **Ulempebelastning** — Hvor mye ubekvem arbeidstid (kveld, helg og natt) Kandidaten har hatt i de fire ukene før Vaktens start, målt i Ulempepoeng (FR-14).
- **Ulempepoeng** — Poeng per arbeidstime etter tidspunkt i Ulempemodellen (§4.3), summert over måleperioden.
- **Ulempescore** — Ulempepoengene omregnet til 0–100 poeng på fast skala, til bruk i Rangeringen (§4.4).
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
- Valget starter filtrering og Rangering av Kandidater (FR-2 til FR-9 og FR-14) uten ytterligere handling fra Turnusansvarlig.

### 4.2 Regelmotor (harde regler)

**Beskrivelse:** Et lite, godt testet utvalg harde regler filtrerer bort Kandidater som ikke kan ta Vakten. Utvalget følger addendumets anbefaling og er bekreftet av gruppen: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen (daglig hvile) og 35-timersregelen (ukentlig fri). Maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — addendum anbefaler et lite utvalg som beviselig fungerer, fremfor et stort utvalg som bare er halvveis på plass.

**Funksjonelle krav:**

#### FR-2: Filtrere på kompetanse-minstekrav

Systemet skal utelukke en Kandidat hvis Kandidatens Kompetansenivå er under Vaktens definerte minstekrav.

**Konsekvenser (testbare):**
- 100 % av Kandidatene med Kompetansenivå under minstekravet filtreres bort i definerte testscenarioer.
- Minstekravet senkes ikke dersom ingen Kandidater oppfyller det; systemet viser da ingen gyldige kandidater (FR-6).
- Kompetansenivå påvirker bare filtreringen og inngår ikke i poengberegningen i FR-9. To ellers identiske Gyldige kandidater får samme totalscore selv om Kompetansenivået deres er forskjellig.

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

**Beskrivelse:** For hver Gyldig kandidat beregnes en forenklet kostnadsvurdering (ordinær sats vs. overtidssats) og gjeldende arbeidsbelastning. Arbeidsbelastningen består av Timebelastning (FR-8) og Ulempebelastning (FR-14), som beregnes og vises hver for seg. Rangeringen (§4.4) bygger på disse Myke faktorene.

**Kostnadsmodell (bekreftet av gruppen 2026-10-06):** Hver Ansatt har en individuell timelønn (testdata). Ordinær ukentlig terskel er **36 timer/uke** (addendum §2, grensen for helkontinuerlig skiftarbeid). Timer en Kandidat allerede er satt opp på denne uken, pluss timene i Vakten som vurderes, sammenlignes mot terskelen: timer til og med 36 timer kostes til ordinær timelønn, timer utover kostes til **150 % av ordinær timelønn** (lovens minstekrav er 40 % tillegg, 50 % er vanlig praksis og enkelt å beregne). Dette er en bevisst forenkling, ikke en tariffberegning — se Out of Scope.

**Ulempemodell (besluttet av bruker 2026-10-30, utvider ÅB-3):** Ulempebelastningen måler hvor mye ubekvem arbeidstid Kandidaten har hatt i de fire ukene før Vakten. Hver arbeidstime gir Ulempepoeng etter tidspunkt:

| Tidsrom | Ulempepoeng per time |
| --- | --- |
| Hverdag (mandag–fredag) kl. 06–18 | 0 |
| Hverdag kl. 18–22 | 1 |
| Helg (lørdag 00:00–søndag 24:00) kl. 06–22 | 2 |
| Natt kl. 22–06, alle dager | 3 |

- Hver arbeidstime telles bare én gang, i kategorien med høyest poeng: natt > helg > kveld > dag. En nattetime i helgen gir 3 poeng og telles som natt. Fordelingen som vises, følger samme regel, slik at kveldstimer × 1 + helgetimer × 2 + nattetimer × 3 alltid er lik Ulempepoengene.
- Tiden regnes i faktisk forløpt tid i `Europe/Oslo` med sommertid og med minuttoppløsning. En halv time kveld gir 0,5 poeng. Poengene avrundes først ved visning.
- Måleperioden er de 28 døgnene bakover fra Vaktens starttidspunkt. Vakten som vurderes, er ikke med. En Vakt som krysser grensen for måleperioden, telles bare for delen innenfor. Perioden regnes fra Vaktens start og ikke fra dagens dato, slik at samme input alltid gir samme resultat (SM-5).
- **[ASSUMPTION]** Helligdager regnes som vanlige ukedager i v1.
- **Ulempescore = maks(0, 100 × (1 − Ulempepoeng / tak)).** Taket er foreløpig **300 Ulempepoeng**, omtrent 100 nattetimer på fire uker. Taket er én navngitt, konfigurerbar parameter i domenekjernen, sammen med vektene i §4.4. Det skal ikke være en miljøvariabel, fordi samme input da kunne gitt ulikt resultat på ulike maskiner.
- Skalaen er fast, ikke relativ til de Gyldige kandidatene, slik at små forskjeller gir små utslag. 40 mot 42 Ulempepoeng gir 0,1 poeng forskjell i totalscoren, mens en skala relativ til kandidatene kunne gitt opptil 15. Lik Ulempebelastning gir alltid lik Ulempescore, og en ny Kandidat endrer ikke de andres score. Taket på 300 er valgt fremfor 240 og 432 ut fra regneeksempler med typiske turnuser: vanlige turnuser gir omtrent 50–190 poeng over fire uker, nattunge 250–370 (se `.memlog.md`).
- Timebelastning og Ulempebelastning vises separat. Ulempebelastningen vises med samlet poengsum og fordeling på kveld-, helg- og nattetimer, uten terskel eller fargeskifte. 90 %-grensen i FR-8 gjelder bare Timebelastningen.

**Funksjonelle krav:**

#### FR-7: Beregne forenklet kostnad per kandidat

Systemet kan beregne en forenklet kostnadsvurdering for hver Gyldig kandidat etter kostnadsmodellen over, basert på om Vakten utløser ordinær sats, overtidssats, eller en kombinasjon for Kandidaten.

**Konsekvenser (testbare):**
- Samme Kandidat og samme Vakt gir samme beregnet kostnad hver gang (reproduserbart).
- En Kandidat hvis ukentlige timer (eksisterende Vakter + denne Vakten) holder seg på eller under 36 timer, kostes utelukkende til ordinær sats.
- En Kandidat som med denne Vakten overstiger 36 timer denne uken, får timene utover terskelen kostet til 150 % av ordinær sats; øvrige timer forblir på ordinær sats.
- Beregningen er ikke avhengig av KI.

**Out of Scope:**
- Full lønnskostnad med alle tillegg, avgifter og tariffregler (eksplisitt utenfor omfang, jf. brief).

#### FR-8: Vise gjeldende timebelastning per kandidat

Systemet kan vise hvor mye hver Gyldig kandidat allerede er satt opp til å arbeide i den aktuelle uken, som andel av normaluken på 36 timer (samme terskel som FR-7). Dette er Timebelastningen, den ene av arbeidsbelastningens to deler. Den andre er Ulempebelastningen (FR-14).

**Terskel (bekreftet av gruppen 2026-10-06):** Timebelastningen vises som Kandidatens planlagte timer *denne uken* (uten den Vakten som vurderes) delt på 36 timer. «Denne uken» er kalenderuken (mandag–søndag, `Europe/Oslo`) som Vakten starter i (presisert 2026-10-30). Terskelen bytter til «høy belastning»-visning ved ~90 % (ca. 32–33 timer). Samme 36-timers normaluke som kostnadsmodellen i FR-7 — én terskel, to visninger. Til forskjell fra FR-7 legger denne visningen **ikke** til den vurderte Vakten; den viser eksisterende belastning som den er. 90 %-grensen er bare en visuell indikator og påvirker ikke poengene i §4.4.

**Konsekvenser (testbare):**
- Timebelastningen oppdateres konsistent med Turnusens øvrige Vakter for Kandidaten.
- Prosentandelen beregnes som planlagte timer denne uken ÷ 36, og bytter visuell tilstand ved ~90 % av terskelen.

#### FR-14: Beregne og vise ulempebelastning per kandidat

Systemet kan beregne Ulempepoeng for hver Gyldig kandidat etter Ulempemodellen over, ut fra Kandidatens Vakter i de 28 døgnene før Vaktens start, og regne dem om til en Ulempescore på fast skala. Ulempebelastningen vises separat fra Timebelastningen, med samlet poengsum og fordeling på kveld-, helg- og nattetimer. *Lagt til 2026-10-30. Nummeret er valgt for å unngå omnummerering.*

**Konsekvenser (testbare):**
- Samme Kandidat og samme Vakt gir samme Ulempepoeng og Ulempescore hver gang (reproduserbart).
- Hver arbeidstime telles bare én gang, i kategorien med høyest poeng (natt > helg > kveld > dag).
- Ulempepoeng på eller over taket gir Ulempescore 0. Lik poengsum gir lik Ulempescore.
- En Kandidat uten Vakter i måleperioden får 0 Ulempepoeng og Ulempescore 100.
- Beregningen er ikke avhengig av KI.

### 4.4 Rangering av kandidater

**Beskrivelse:** Gyldige kandidater rangeres etter Myke faktorer (§3) ved en poengbasert modell: hver Myk faktor gir 0–100 poeng per Kandidat, vektes, og summeres til en totalscore. Høyest totalscore rangeres øverst. Rangeringen er ikke rent kostnadsstyrt — brief krever at minst ett scenario skal demonstrere at billigste Kandidat ikke nødvendigvis rangeres høyest.

**Vekting (oppdatert etter brukerens beslutning 2026-10-15, arbeidsbelastning delt 2026-10-30):**

Kostnad vektes med 40 %, arbeidsbelastning med 35 % og Ansattpreferanse med 25 %. Arbeidsbelastningens 35 % er delt i Timebelastning (20 %) og Ulempebelastning (15 %). Vektene summerer til 100 %.

| Myk faktor | Vekt | Poengsetting |
| --- | --- | --- |
| Kostnad | 40 % | Lavest kostnad blant Gyldige kandidater for Vakten = 100 poeng, høyest = 0 poeng, lineær skala imellom. |
| Arbeidsbelastning: Timebelastning | 20 % | Lavest Timebelastning (FR-8) blant Gyldige kandidater = 100 poeng, høyest = 0 poeng, lineær skala imellom. |
| Arbeidsbelastning: Ulempebelastning | 15 % | Fast skala: Ulempescore = maks(0, 100 × (1 − Ulempepoeng / 300)), etter Ulempemodellen i §4.3 (FR-14). |
| Ansattpreferanse | 25 % | Fem faste nivåer: 100, 75, 50, 25 eller 0 poeng etter kategoriene i §4.5. Manglende registrert preferanse = 50 poeng, merket «ingen registrert preferanse». |


Totalscore = 0,40 × kostnadspoeng + 0,20 × timebelastningspoeng + 0,15 × Ulempescore + 0,25 × preferansepoeng. Kompetanse vurderes utelukkende som Hard regel i FR-2.

Kostnad og Timebelastning bruker en skala relativ til de Gyldige kandidatene. Ulempebelastning bruker fast skala, slik at små forskjeller i Ulempepoeng ikke gir store utslag (begrunnelse i §4.3). Vektene og taket for Ulempescore ligger samlet som navngitte parametere i domenekjernen.

**Funksjonelle krav:**

#### FR-9: Rangere gyldige kandidater

Systemet kan rangere alle Gyldige kandidater for en Vakt basert på den poengbaserte modellen over. Kandidatlisten viser inntil fem av de høyest rangerte. Finnes færre enn fem Gyldige kandidater, vises alle; finnes ingen, gjelder FR-6. Turnusansvarlig skal fortsatt kunne få tilgang til øvrige Gyldige kandidater for valg etter FR-12.

**Konsekvenser (testbare):**
- Minst ett testscenario demonstrerer at den billigste Kandidaten ikke rangeres høyest, fordi andre Myke faktorer samlet sett veier tyngre.
- Minst ett testscenario demonstrerer at Ulempebelastningen endrer rekkefølgen mellom to Kandidater som ellers er nesten like.
- Samme input (Kandidater, Vakt, preferanser) gir samme rangeringsrekkefølge hver gang — poengmodellen er en ren, deterministisk beregning, ikke avhengig av KI.

### 4.5 KI-forklaring av avveininger

**Beskrivelse:** KI tolker tekstbaserte Ansattpreferanser og genererer en forståelig forklaring per Kandidat: hvorfor Kandidaten kan ta Vakten, hva som trekker opp, hva som trekker ned, kostnadsvurdering og relevante Ansattpreferanser. KI forklarer og tolker — den beregner aldri Harde regler, arbeidstid eller kostnad, og kan aldri overstyre Rangeringen eller utføre en endring selv.

**Funksjonelle krav:**

#### FR-10: Tolke tekstbaserte ansattpreferanser

Systemet kan bruke en språkmodell til å tolke tekstbaserte Ansattpreferanser og gjøre dem tilgjengelige som input til Rangeringen (§4.4).

**Konsekvenser (testbare):**
- Tolkede preferanser sendes som strukturert kategori til Rangeringen. Koden tildeler kategoriens faste poengsum; språkmodellen utfører ikke selve poengberegningen eller Rangeringen.
- Alle de 15 definerte preferansetekstene under skal tolkes til forventet kategori. Eksakt ordlyd i KI-forklaringen er ikke en del av fasiten.
- Manglende registrert preferanse gir 50 poeng og merkes «ingen registrert preferanse». Det skal ikke fremstilles som et uttrykkelig nøytralt ønske.

**Preferansekategorier og poeng:**

| Poeng | Tolkning |
| --- | --- |
| 100 | Ønsker aktivt flere vakter |
| 75 | Positiv til ekstravakt ved behov |
| 50 | Nøytral |
| 25 | Foretrekker å slippe, men er åpen ved behov |
| 0 | Tydelig ønske om å unngå ekstravakter |

Manglende registrert preferanse gir 50 poeng, men vises som «ingen registrert preferanse», ikke som et uttrykkelig nøytralt ønske. En tekst som ikke uttrykker noen tydelig holdning til flere vakter eller ekstravakter, for eksempel bare ønsker om tidspunkt, tolkes som nøytral (50 poeng): personen har verken bedt om eller avslått ekstravakter og regnes som åpen. Skillet mellom 25 og 0 poeng er om personen åpner for ekstravakter ved behov. Preferanser påvirker bare rangeringen av gyldige kandidater og utelukker ingen automatisk; de overstyrer aldri harde regler.

**Definerte preferansetekster med fasit:**

| Nr. | Preferansetekst | Forventet tolkning | Poeng |
| --- | --- | --- | --- |
| 1 | «Jeg ønsker flere vakter denne uken.» | Ønsker aktivt flere vakter | 100 |
| 2 | «Jeg vil gjerne jobbe mer enn den oppsatte turnusen.» | Ønsker aktivt flere vakter | 100 |
| 3 | «Prioriter meg gjerne når det blir ledige ekstravakter.» | Ønsker aktivt flere vakter | 100 |
| 4 | «Jeg trenger ikke flere vakter, men tar gjerne en ekstra ved behov.» | Positiv til ekstravakt ved behov | 75 |
| 5 | «Hvis dere mangler folk, stiller jeg gjerne på en ekstravakt.» | Positiv til ekstravakt ved behov | 75 |
| 6 | «Jeg er positiv til ekstravakter, selv om jeg ikke aktivt ber om flere.» | Positiv til ekstravakt ved behov | 75 |
| 7 | «Jeg har ingen ønsker om flere eller færre vakter.» | Nøytral | 50 |
| 8 | «For meg spiller det ingen rolle om jeg får en ekstravakt.» | Nøytral | 50 |
| 9 | «Jeg stiller meg nøytral til å jobbe utover den oppsatte turnusen.» | Nøytral | 50 |
| 10 | «Jeg foretrekker å slippe ekstravakter, men kan ta en hvis det trengs.» | Foretrekker å slippe, men er åpen ved behov | 25 |
| 11 | «Spør helst andre først, men jeg er åpen for en ekstravakt ved bemanningsbehov.» | Foretrekker å slippe, men er åpen ved behov | 25 |
| 12 | «Jeg ønsker helst bare de oppsatte vaktene, men kan stille dersom dere mangler folk.» | Foretrekker å slippe, men er åpen ved behov | 25 |
| 13 | «Jeg ønsker ikke ekstravakter denne uken.» | Tydelig ønske om å unngå ekstravakter | 0 |
| 14 | «Jeg ønsker færre vakter og ber om å slippe ekstraarbeid.» | Tydelig ønske om å unngå ekstravakter | 0 |
| 15 | «Jeg ønsker kun å jobbe de vaktene som allerede står i turnusen.» | Tydelig ønske om å unngå ekstravakter | 0 |

#### FR-11: Generere forklaring per kandidat

Systemet kan generere en KI-basert forklaring for hver Kandidat i Rangeringen: hvorfor Kandidaten kan ta Vakten, hvilke forhold som trekker opp, hvilke som trekker ned, kostnadsvurdering, og relevante Ansattpreferanser.

**Konsekvenser (testbare):**
- Forklaringen nevner aldri en Kandidat som er utelukket av en Hard regel (testbar invariant, jf. addendum §4).
- Forklaringen kan vise til Timebelastning og Ulempebelastning med fordeling på kveld, helg og natt, men bare med tallene regelmotoren har beregnet. KI beregner dem aldri selv.
- Ved feil, tomt eller ubrukelig svar fra språkmodellen viser systemet en forhåndsdefinert reservetekst eller feilmelding i stedet for KI-forklaringen — aldri en anbefaling uten gyldig grunnlag — og systemet fortsetter å fungere uten å krasje.

**Feature-spesifikke NFR-er:**
- Grensen mellom deterministisk lag (§4.2–§4.4) og KI-laget er en hard systemgrense: KI mottar allerede filtrerte og beregnede data, og kan ikke endre dem.
- **Kjørbar uten gruppens API-nøkkel:** Systemet kan kjøres i en demo-modus uten nøkkel til språkmodellen. Tolkede preferanser og Avveininger kommer da fra modellsvar som er generert på forhånd og lagret i testdataene, eller fra en mal bygd utelukkende av de beregnede tallene. Brukergrensesnittet viser alltid om en Avveining er live, forhåndsgenerert eller malbasert. En feil i live-modus gir reservetekst (FR-11), ikke stille overgang til demo-modus.

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
- Forenklet kostnads- og arbeidsbelastningsvurdering per Gyldig kandidat, med Timebelastning og Ulempebelastning hver for seg (§4.3).
- Rangering av Gyldige kandidater etter kostnad (40 %), arbeidsbelastning (35 %: Timebelastning 20 %, Ulempebelastning 15 %) og Ansattpreferanse (25 %) (§4.4).
- KI-tolkning av tekstbaserte Ansattpreferanser og KI-generert forklaring per Kandidat (§4.5).
- Menneskelig Godkjenning som forutsetning for enhver endring (§4.6).
- Enkel innlogging for Turnusansvarlig (§4.7).

### 6.2 Utenfor omfang for MVP

- Alt listet i §5 Ikke-mål.

## 7. Suksesskriterier

**Primære**
- **SM-1**: 100 % av Kandidatene som bryter en implementert Hard regel filtreres bort i definerte testscenarioer. Validerer FR-2 til FR-5.
- **SM-2**: En Kandidat utelukket av en Hard regel blir aldri anbefalt av KI — testbar invariant. Validerer FR-9, FR-11.
- **SM-3**: Turnusansvarlig får presentert inntil fem av de høyest rangerte Gyldige kandidatene for en fiktiv Turnus (20–30 ansatte) uten å måtte kontrollere alle manuelt. Validerer FR-1, FR-9.
- **SM-4**: Systemet forklarer hvilke faktorer som påvirker Rangeringen av hver Kandidat. Validerer FR-11.
- **SM-5**: Samme strukturerte input gir samme resultat hver gang for Harde regler, kostnadsberegninger, Timebelastning og Ulempebelastning (reproduserbarhet). Validerer FR-2 til FR-9 og FR-14.
- **SM-6**: Minst ett scenario demonstrerer at den billigste Kandidaten ikke nødvendigvis rangeres høyest. Validerer FR-9.
- **SM-7**: KI tolker alle 15 definerte preferansetekster i §4.5 til forventet kategori og bruker tolkningen i forklaringen. Manglende registrert preferanse gir 50 poeng og vises som «ingen registrert preferanse». Validerer FR-10, FR-11.
- **SM-8**: Turnusansvarlig er alltid den som tar den endelige beslutningen (Godkjenning kreves). Validerer FR-12.
- **SM-9** *(teknisk kvalitet)*: Systemet kan bygges og kjøres fra et rent klonet repo, uten manuelle unntak eller udokumenterte oppsettsteg, og uten gruppens API-nøkkel (demo-modus, §4.5). Validerer hele leveransen (§4); addendum §6 peker på dette som et teknisk kvalitetskriterium som bør videreføres i PRD/spec.

**Motmetrikker (skal ikke optimeres)**
- **SM-C1**: Antall implementerte Harde regler skal ikke maksimeres på bekostning av testdekning per regel — addendums anbefaling («fire regler som beviselig fungerer er verdt mer enn tolv som er halvveis») veier tyngre enn regelmengde. Motvirker en eventuell trang til å utvide §4.2 uten tilsvarende testarbeid.
- **SM-C2**: Rask responstid på KI-forklaringen skal ikke optimeres på bekostning av at forklaringen faktisk er korrekt og aldri nevner en utelukket Kandidat. Motvirker SM-3/SM-4 ved å hindre at hastighet trumfer den testbare invarianten i SM-2.

## 8. Åpne spørsmål

1. **Bekreft med faglærer** om KI i selve produktet (ikke bare i utviklingsprosessen) er et karakterkrav eller et rent produktvalg (addendum §5). Bør avklares før proposal leveres. Faglærers tilbakemelding på product brief (2026-10-06) vurderer KI/regelmotor-skillet som en styrke, men bekrefter ikke eksplisitt dette spørsmålet — fortsatt åpent.
2. Nøyaktig tekst/utforming av «ingen gyldige kandidater»-meldingen (§4.2, FR-6) — atferden er spesifisert (skal skille seg fra laste-/feiltilstand), men ordlyden er åpen for forslag fra resten av gruppen.

**Løst (2026-10-30):**
- Arbeidsbelastning utvidet med ubekvem arbeidstid (utvider ÅB-3). Arbeidsbelastningens 35 % er delt i Timebelastning 20 % og Ulempebelastning 15 %. Kostnad 40 % og Ansattpreferanse 25 % er uendret. Ulempebelastningen beregnes etter Ulempemodellen i §4.3 over de 28 døgnene før Vaktens start, på fast skala med konfigurerbart tak (300 Ulempepoeng), og vises separat med fordeling på kveld, helg og natt (FR-14). 90 %-grensen beholdes som visuell indikator for Timebelastning. «Denne uken» i FR-8 er presisert til kalenderuken Vakten starter i. Se §4.3, §4.4 og epics story 4.7.

**Løst (2026-10-14):**
- Kjøring uten gruppens nøkkel (faglærers tilbakemelding 2026-10-06, punkt 3; tidligere åpent spørsmål 3). KI-leverandøren er OpenRouter med `openai/gpt-6-luna` som standardmodell, satt i en miljøvariabel (endret fra `anthropic/claude-haiku-5.5` 2026-10-16 etter modelltest, se `docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md`). Dette erstatter Google Gemini, som ble valgt i arkitektursteget 2026-09-29 (arkitekturens AD-6). Sensor får en OpenRouter-nøkkel med kreditt, levert i innleveringen og aldri i repoet. Om det blir den felles utviklingsnøkkelen eller en egen sensornøkkel, og hvor mye kreditt den får, avgjøres nær innlevering ut fra faktisk forbruk (epics ÅB-8). Uten nøkkel starter appen i demo-modus (§4.5). Se `sprint-change-proposal-2026-10-14.md`.

**Løst (2026-10-06):**
- Innbyrdes vekting mellom Myke faktorer i Rangeringen — se §4.4. Oppdatert 2026-10-15: kompetansenærhet er tatt ut. Kostnad vektes med 40 %, arbeidsbelastning med 35 % og Ansattpreferanse med 25 %. Kompetanse vurderes bare som Hard regel (FR-2).
- Konkret detaljnivå i kostnadsmodellen (§4.3, FR-7) — se §4.3 for terskel (36 t/uke) og overtidstillegg (150 %).
- Arbeidsbelastningsterskelen («~90 %» i arbeidsbelastningslinjen, opprinnelig fra DESIGN.md/arkitekturens Deferred-liste, ikke et nummerert punkt her) — se §4.3, FR-8: samme 36-timers normaluke som kostnadsmodellen.

**Vurdert og bevisst utelatt fra denne PRD-en:** addendumets punkt om «arbeidsdeling og frister» er et prosjektstyringsspørsmål for gruppen, ikke et produktkrav — det hører hjemme i gruppens egen fremdriftsplan, ikke i PRD-en.

## 9. Antakelser-indeks

- Fra §2.3 (UJ-1): Persona-navnet «Kari» er oppdiktet for å gjøre brukerreisen konkret — representerer ingen reell bruker, i tråd med at Turnusen er fiktiv.
- Fra §4.2/§8: Regelutvalget (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen) er bekreftet av bruker; maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — revurderes bare hvis gruppen ønsker et bredere regelsett.
- Fra §4.3 (Ulempemodell): Helligdager regnes som vanlige ukedager i v1. Taket på 300 Ulempepoeng bygger på regneeksempler med antatte, typiske vakttider og turnusprofiler, ikke på en kilde, og kan justeres i én parameter.
- Fra §7 (SM-9): Antakelse om at «kjører fra et rent klonet repo» er det addendum mener med teknisk kvalitetskriterium fra emnekravet — ikke eksplisitt bekreftet av gruppen, men utledet direkte fra addendum §6.
