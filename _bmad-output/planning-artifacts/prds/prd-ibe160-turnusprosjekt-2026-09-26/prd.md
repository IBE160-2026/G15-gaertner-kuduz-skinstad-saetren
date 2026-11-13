---
title: "PRD: Turnushjelperen"
status: final
created: 2026-09-26
updated: 2026-11-13
---

# PRD: Turnushjelperen
*Produktnavn bekreftet av gruppen 2026-09-26. Prosjektet omtales fortsatt som «IBE160 Turnusprosjekt» i emnesammenheng (proposal, refleksjonsrapport); «Turnushjelperen» er navnet på selve web-appen.*

## 0. Dokumentets formål

Denne PRD-en er skrevet for prosjektgruppen selv (4 medlemmer) og bygger videre på `product-brief.md` og dens `addendum.md`. Den definerer *hva* Turnushjelperen skal gjøre og *hvorfor*, som grunnlag for arkitektur, epics/stories og den godkjente proposalen til IBE160. Krav er gruppert per funksjon med globalt nummererte FR-er; antakelser er merket `[ASSUMPTION]` inline og samlet i §9.

**Hva `status: final` betyr:** Kravene er låst og endres bare etter gruppevedtak. Implementasjonen er ikke ferdig. Status for hver story står i `sprint-status.yaml`, og kontroller som gjenstår, står i epics. De få spørsmålene som fortsatt er åpne, står i §8 med eier og frist.

**Lesemåte:** Kravene skal kunne leses uten andre filer. Hvor kravene kommer fra (beslutnings-ID-er, stories og arkitekturvalg), står samlet i §10. Hvert FR er merket med prioritet:
- **Kjerne:** må virke for at produktet virker.
- **Etter kjerne:** planlagt i v1, men starter først når kjerneflyten virker.
- **Strekk:** tas bare hvis det er tid igjen.

Fordelingen står i §6.

## 1. Visjon

Når en planlagt vakt i en eksisterende turnus plutselig må dekkes av noen andre, skal den turnusansvarlige gå fra «denne vakten mangler bemanning» til et begrunnet forslag om hvem som bør ta den — uten å måtte kontrollere alle 20–30 ansatte manuelt.

Turnushjelperen er en web-app som fungerer som beslutningsstøtte for én vaktendring om gangen: fire avgrensede prototyperegler (kompetanse, kollisjon, 11 timer hvile før/etter og 35 timer fri i berørt kalenderuke) filtrerer bort ugyldige kandidater, en enkel og reproduserbar modell rangerer de gyldige etter arbeidsbelastning, kostnad og ansattpreferanser, og KI tolker tekstbaserte preferanser og forklarer avveininger. Turnushjelperen anbefaler — den bestemmer aldri selv, og den kan aldri anbefale en kandidat som en hard regel har utelukket. Prototypen gir ingen garanti om full juridisk kontroll.

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

Ansatte er **ikke** brukere av Turnushjelperen i v1 — de kan verken logge inn, se egne vakter eller registrere preferanser selv. Kjerneflyten bruker forhåndsdefinerte preferanser i testdata. Redigering av preferansetekst av turnusansvarlig er planlagt etter kjerneflyten (§6.2). En lesende ansattoversikt og vaktbytte mellom ansatte er vurdert og lagt til senere versjon (se addendum §3).

### 2.3 Sentrale brukerreiser

- **UJ-1. Turnusansvarlig finner en erstatter for en vakt som mangler bemanning.**
  - **Persona + kontekst:** Kari, turnusansvarlig for en avdeling med ca. 25 ansatte, får beskjed om at en ansatt har meldt fra syk til en vakt i morgen.
  - **Inngangstilstand:** Kari er innlogget i Turnushjelperen og har den eksisterende turnusen tilgjengelig.
  - **Sti:** (1) Kari velger den konkrete vakten som må bemannes på nytt. (2) Systemet viser en rangert liste over gyldige kandidater — ansatte som ikke oppfyller kompetanse-minstekravet, har kolliderende vakt, eller ville brutt hviletids-/arbeidstidsregler, er allerede filtrert bort. (3) Kari åpner en kandidat og ser kostnadsvurdering, arbeidsbelastning, og en KI-generert forklaring av avveiningene (f.eks. «rangeres over nr. 2 fordi overtidskostnaden er lavere, selv om nr. 2 har uttrykt ønske om flere vakter»). (4) Kari sammenligner 2–3 kandidater på denne måten.
  - **Klimaks:** Kari ser tydelig hvorfor den øverste kandidaten er anbefalt, og stoler på grunnlaget uten å måtte sjekke de resterende 20+ ansatte manuelt.
  - **Oppløsning:** Kari velger kandidaten hun mener er riktig (ikke nødvendigvis den øverste) og bekrefter valget — Turnushjelperen gjennomfører ingen endring på egen hånd.
  - **Edge case:** Ingen kandidater er gyldige (alle filtrert bort av harde regler) — Turnushjelperen viser egen tomtilstand med utelukkelsesoppsummering (FR-6). Ukjent eller ugyldig nødvendig datagrunnlag gir i stedet en Datafeil uten rangering eller godkjenning.

**[ASSUMPTION]** Persona-navnet «Kari» og detaljene rundt henne er oppdiktet for å gjøre reisen konkret — dette er ikke ment å representere en reell bruker, kun en fiktiv illustrasjon slik brief-omfanget (fiktiv turnus, ingen ekte personopplysninger) tilsier.

## 3. Ordliste

- **Ansatt** — En person i avdelingens Turnus, med navn, timelønn, Kompetansenivå per vakttype og eventuelt en registrert Ansattpreferanse. Fiktiv i v1. Ansatte er ikke brukere av Turnushjelperen (§2.2).
- **Turnus** — En eksisterende bemanningsplan for en avdeling, bestående av vakter tildelt ansatte over en periode. Fiktiv i v1 (20–30 ansatte).
- **Vakt** — En enkelt planlagt arbeidsøkt for én ansatt, med start-/sluttidspunkt og et kompetansekrav.
- **Turnusansvarlig** — Primærbrukeren. Den eneste rollen som har tilgang til Turnushjelperen i v1.
- **Kandidat** — En ansatt som vurderes for å overta en Vakt som må bemannes på nytt.
- **Gyldig kandidat** — En Kandidat som ikke er utelukket av noen Hard regel.
- **Hard regel** — Et absolutt krav (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen og 35-timersregelen i v1) som utelukker en Kandidat uten unntak. Beregnes deterministisk — aldri av KI.
- **Kompetansenivå** — Hvor godt en Ansatt er opplært for en gitt type Vakt, på en skala fra 1 (under opplæring) til 4 (fullt kvalifisert). Avgjør om Kandidaten oppfyller Vaktens minstekrav (Hard regel, §4.2). Kompetansenivå gir ingen poeng i Rangeringen.
- **Myk faktor** — Et hensyn som brukes til å rangere Gyldige kandidater seg imellom: kostnad, arbeidsbelastning (Timebelastning og Ulempebelastning) og Ansattpreferanse.
- **Arbeidsbelastning** — Samlebetegnelse for Timebelastning og Ulempebelastning. De to beregnes, vektes og vises hver for seg (§4.3, §4.4).
- **Timebelastning** — Kandidatens planlagte timer i kalenderuken Vakten starter i, uten Vakten som vurderes, som andel av normaluken på 36 timer (FR-8).
- **Ulempebelastning** — Hvor mye ubekvem arbeidstid (kveld, helg og natt) Kandidaten har hatt i de fire ukene før Vaktens start, målt i Ulempepoeng (FR-14).
- **Ulempepoeng** — Poeng per arbeidstime etter tidspunkt i Ulempemodellen (§4.3), summert over måleperioden.
- **Ulempescore** — Ulempepoengene omregnet til 0–100 poeng på fast skala, til bruk i Rangeringen (§4.4).
- **Ansattpreferanse** — Tekstbasert informasjon om en ansatts ønsker eller begrensninger, tolket av KI-laget som del av Rangeringen.
- **Rangering** — Den sorterte listen over Gyldige kandidater, ordnet etter Myke faktorer.
- **Avveining** — KI-generert forklaring av hvorfor én Kandidat rangeres over en annen.
- **Vaktkostnad** — Økningen i forenklet, modellberegnet lønnskostnad når den vurderte Vakten legges til, summert over berørte kalenderuker.
- **Godkjenning** — Turnusansvarliges eksplisitte, endelige valg av Kandidat. Ingen endring anses gjennomført før Godkjenning er gitt.
- **Datafeil** — Tilstanden når nødvendig turnusgrunnlag for den valgte Vakten mangler eller er ugyldig, for eksempel ukjent historikk rundt Vakten. Systemet beregner da ingen Kandidater og tilbyr verken Rangering eller Godkjenning. En Datafeil er ikke det samme som at ingen Kandidater er gyldige (FR-6).
- **Demo-modus** — Kjøring uten nøkkel til språkmodellen. Tolkninger og Avveininger kommer da fra svar som er generert på forhånd, eller fra en mal bygd av de beregnede tallene. Grensesnittet viser alltid hvilken kilde en Avveining har (§4.5).
- **Reservetekst** — En forhåndsdefinert tekst som vises i stedet for KI-forklaringen når språkmodellen feiler, svarer ubrukelig eller ikke består faktakontrollen. Reserveteksten er tydelig merket og hindrer aldri Rangering eller Godkjenning (FR-11).

## 4. Funksjoner

### 4.1 Vaktvalg

**Beskrivelse:** Turnusansvarlig velger en eksisterende Vakt i Turnusen som må bemannes på nytt. Dette utløser kandidatvurdering (§4.2–§4.4). Realiserer UJ-1.

**Funksjonelle krav:**

#### FR-1: Velge vakt som må bemannes på nytt

*Prioritet: Kjerne.*

Turnusansvarlig kan velge én Vakt fra en eksisterende Turnus. Realiserer UJ-1.

**Konsekvenser (testbare):**
- Systemet viser Vaktens tidspunkt og kompetansekrav ved valg.
- Når nødvendig datagrunnlag er komplett, starter valget filtrering og Rangering av Kandidater (FR-2 til FR-9 og FR-14) uten ytterligere handling fra Turnusansvarlig.
- Mangler nødvendig turnusgrunnlag for den valgte Vakten, viser systemet «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» med den kjente datagrensen der den finnes. Systemet tilbyr da verken Rangering eller Godkjenning. Dette er en Datafeil og forskjellig fra at ingen Kandidater er gyldige (FR-6).
- Et forsinket svar for en tidligere valgt Vakt eller Kandidat skal ikke erstatte den aktive visningen.

### 4.2 Regelmotor (harde regler)

**Beskrivelse:** Et lite, godt testet utvalg harde regler filtrerer bort Kandidater som ikke kan ta Vakten. Utvalget følger addendumets anbefaling og er bekreftet av gruppen: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen (daglig hvile) og 35-timersregelen (ukentlig fri). Maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — addendum anbefaler et lite utvalg som beviselig fungerer, fremfor et stort utvalg som bare er halvveis på plass. **[ASSUMPTION]** Utvalget revurderes bare hvis gruppen ønsker et bredere regelsett (§9).

**Kandidatgrunnlag:** Alle Ansatte i Turnusen vurderes, bortsett fra den Ansatte som opprinnelig var satt opp på Vakten som skal bemannes på nytt. Øvrige Ansatte antas tilgjengelige med mindre planlagte Vakter eller Harde regler utelukker dem. **[ASSUMPTION]** Dette er en fast demonstrasjonsforutsetning, ikke en garanti for faktisk tilgjengelighet; v1 har ingen separat fraværsmodell (§9).

**Avgrenset hvilekontroll:** v1 bruker prototypemodellen i FR-4 og FR-5. Kontrollen krever relevante nabovakter og komplette berørte kalenderuker, også utenfor perioden som vises. Modellen skal ikke fremstilles som full juridisk kontroll av arbeidsmiljøloven.

**Nødvendig datadekning:** Ukjent historikk er ikke dokumentert fri. Mangler nødvendig historikk eller fremtidige nabovakter, gyldige start- og sluttider, Vaktens kompetansekrav eller Kandidatens kostnadsgrunnlag, stopper vurderingen med Datafeil. Manglende Kompetansenivå hos en Kandidat er ikke Datafeil, men utelukkelse etter FR-2. Testdataene har planlagte Vakter til 2026-10-05 kl. 00:00 i `Europe/Oslo`. En Vakt der hvilen etter den ikke kan kontrolleres fordi dataene slutter, gir derfor Datafeil og ikke en kandidatliste. Vaktene som brukes i demonstrasjonen, ligger innenfor dataene.

**Funksjonelle krav:**

#### FR-2: Filtrere på kompetanse-minstekrav

*Prioritet: Kjerne.*

Systemet skal utelukke en Kandidat hvis Kandidatens Kompetansenivå er under Vaktens definerte minstekrav.

**Konsekvenser (testbare):**
- 100 % av Kandidatene med Kompetansenivå under minstekravet filtreres bort i definerte testscenarioer.
- Minstekravet senkes ikke dersom ingen Kandidater oppfyller det; systemet viser da ingen gyldige kandidater (FR-6).
- Kandidat uten registrert Kompetansenivå for vakttypen utelukkes med årsaken «kompetanse-minstekrav». Manglende minstekrav på selve Vakten er derimot Datafeil.
- Kompetansenivå påvirker bare filtreringen og inngår ikke i poengberegningen i FR-9. To ellers identiske Gyldige kandidater får samme totalscore selv om Kompetansenivået deres er forskjellig.

#### FR-3: Filtrere på kolliderende vakt

*Prioritet: Kjerne.*

Systemet skal utelukke en Kandidat som allerede har en Vakt som overlapper i tid med Vakten som skal bemannes.

**Konsekvenser (testbare):**
- 100 % av Kandidatene med tidsmessig overlappende Vakt filtreres bort i definerte testscenarioer. Vakter behandles som halvåpne tidsintervaller: slutt nøyaktig ved den vurderte Vaktens start er ikke kollisjon, mens ett minutts overlapp er det.

#### FR-4: Filtrere på 11-timersregelen (daglig hvile)

*Prioritet: Kjerne.*

Systemet skal utelukke en Kandidat dersom hvilen mellom forrige Vakts slutt og den vurderte Vaktens start, eller mellom den vurderte Vaktens slutt og neste Vakts start, ville blitt mindre enn 11 sammenhengende timer. Dette er den vedtatte prototypetolkningen av daglig hvile i v1.

**Konsekvenser (testbare):**
- 100 % av Kandidatene som ville brutt 11-timersregelen filtreres bort i definerte testscenarioer.
- Hvile på nøyaktig 11 timer oppfyller denne regelen; 10 timer og 59 minutter gjør det ikke. Grensen kontrolleres både før og etter Vakten, i faktisk forløpt tid i `Europe/Oslo`, også ved sommertidsskifte.
- Samme Kandidat og samme Vakt gir samme filtreringsresultat hver gang (reproduserbart).

#### FR-5: Filtrere på 35-timersregelen (ukentlig fri)

*Prioritet: Kjerne.*

Systemet skal utelukke en Kandidat dersom Kandidatens Vakter, etter at den vurderte Vakten er lagt til, ikke etterlater minst 35 timer sammenhengende fri innenfor hver berørte kalenderuke. Kalenderuken går fra mandag kl. 00:00 til neste mandag kl. 00:00 i `Europe/Oslo`. Dette er den vedtatte prototypetolkningen av ukentlig fri i v1.

**Konsekvenser (testbare):**
- 100 % av Kandidatene som ville brutt 35-timersregelen filtreres bort i definerte testscenarioer.
- En lengste sammenhengende friperiode på nøyaktig 35 timer oppfyller denne regelen; 34 timer og 59 minutter gjør det ikke. Varigheten beregnes i faktisk forløpt tid, også ved sommertidsskifte.
- Krysser Vakten ukeskiftet, kontrolleres begge ukene. Brudd i én av dem utelukker Kandidaten.

#### FR-6: Vise når ingen kandidater er gyldige

*Prioritet: Kjerne.*

Systemet skal informere Turnusansvarlig med en eksplisitt melding når ingen Kandidater er gyldige for den valgte Vakten, i stedet for å vise en tom liste. Realiserer UJ-1 (edge case).

**Konsekvenser (testbare):**
- Meldingen for «ingen gyldige kandidater» er tekstlig og visuelt forskjellig fra en laste- eller feiltilstand, slik at Turnusansvarlig ikke kan forveksle de to.
- Tomtilstanden oppsummerer hvorfor Kandidater ble utelukket og sier «Innleie av personell kan vurderes», uten knapp eller påstand om at appen tilbyr innleie. En Datafeil skal aldri presenteres som null gyldige.

**Feature-spesifikke NFR-er:**
- En Kandidat utelukket av en Hard regel skal aldri kunne opptre i Rangeringen (§4.4) eller nevnes av KI-forklaringen (§4.5) — testbar invariant.
- Harde regler beregnes deterministisk. KI har ingen rolle i denne funksjonen.

### 4.3 Kostnads- og arbeidsbelastningsvurdering

**Beskrivelse:** For hver Gyldig kandidat beregnes en forenklet kostnadsvurdering (ordinær sats vs. overtidssats) og gjeldende arbeidsbelastning. Arbeidsbelastningen består av Timebelastning (FR-8) og Ulempebelastning (FR-14), som beregnes og vises hver for seg. Rangeringen (§4.4) bygger på disse Myke faktorene.

**Kostnadsmodell:** Hver Ansatt har en individuell timelønn (testdata). Ordinær ukentlig terskel er **36 timer/uke** (addendum §2, grensen for helkontinuerlig skiftarbeid). Modellert kostnad for timer til og med 36 i hver kalenderuke er ordinær timelønn, og for timer utover er den **150 %** av ordinær timelønn. Kalenderuken er mandag kl. 00:00 til neste mandag kl. 00:00 i `Europe/Oslo`. Faktisk forløpt arbeidstid fra både eksisterende og vurdert Vakt fordeles etter overlapp med hver uke, også ved sommertid. Vakter som slutter nøyaktig på ukegrensen gir ingen timer i neste uke. **Vaktkostnaden er forskjellen i modellert kostnad før og etter tildelingen, summert over berørte uker**; opprinnelig ansatts lønn trekkes ikke fra. Dette er en forenklet modell, ikke en tariffberegning — se Out of Scope.

**Ulempemodell (besluttet av bruker 2026-10-30, utvider ÅB-3):** Ulempebelastningen måler hvor mye ubekvem arbeidstid Kandidaten har hatt i de fire ukene før Vakten. Hver arbeidstime gir Ulempepoeng etter tidspunkt:

| Tidsrom | Ulempepoeng per time |
| --- | --- |
| Hverdag (mandag–fredag) kl. 06–18 | 0 |
| Hverdag kl. 18–22 | 1 |
| Helg (lørdag 00:00–søndag 24:00) kl. 06–22 | 2 |
| Natt kl. 22–06, alle dager | 3 |

- Hver arbeidstime telles bare én gang, i kategorien med høyest poeng: natt > helg > kveld > dag. En nattetime i helgen gir 3 poeng og telles som natt. Fordelingen som vises, følger samme regel, slik at kveldstimer × 1 + helgetimer × 2 + nattetimer × 3 alltid er lik Ulempepoengene.
- Tiden regnes i faktisk forløpt tid i `Europe/Oslo` med sommertid og med minuttoppløsning. En halv time kveld gir 0,5 poeng. Poengene avrundes først ved visning.
- Måleperioden er de 672 faktiske timene bakover fra Vaktens starttidspunkt, som halvåpent intervall [start − 672 t, start). Over et sommertidsskifte er det ikke det samme som 28 kalenderdøgn (gruppevedtak AV-09, 2026-11-02). Vakten som vurderes, er ikke med. En Vakt som krysser grensen for måleperioden, telles bare for delen innenfor. Perioden regnes fra Vaktens start og ikke fra dagens dato, slik at samme input alltid gir samme resultat (SM-5).
- Helligdager regnes som vanlige ukedager i v1 (bekreftet av gruppa 2026-11-02).
- **Ulempescore = maks(0, 100 × (1 − Ulempepoeng / tak)).** Vedtatt v1-tak er **300 Ulempepoeng**, omtrent 100 nattetimer på fire uker. Taket er én navngitt parameter, sammen med vektene i §4.4, og er det samme på alle maskiner, slik at samme input alltid gir samme resultat.
- **[ASSUMPTION]** Taket bygger på regneeksempler med antatte, typiske turnusprofiler, ikke på en kilde (§9).
- Skalaen er fast, ikke relativ til de Gyldige kandidatene, slik at små forskjeller gir små utslag. 40 mot 42 Ulempepoeng gir 0,1 poeng forskjell i totalscoren, mens en skala relativ til kandidatene kunne gitt opptil 15. Lik Ulempebelastning gir alltid lik Ulempescore, og en ny Kandidat endrer ikke de andres score. Taket på 300 er valgt fremfor 240 og 432 ut fra regneeksempler med typiske turnuser: vanlige turnuser gir omtrent 50–180 poeng over fire uker, nattunge 250–320. Regneeksemplene bruker vakttidene dag 07–15, kveld 15–23 og natt 23–07 og kan kjøres på nytt (§10). 432 er ikke et teoretisk maksimum, fordi overtid er tillatt, og faste nattevakter (ca. 320 poeng) får bevisst Ulempescore 0.
- Timebelastning og Ulempebelastning vises separat. Ulempebelastningen vises med samlet poengsum og fordeling på kveld-, helg- og nattetimer, uten terskel eller fargeskifte. 90 %-grensen i FR-8 gjelder bare Timebelastningen.

**Funksjonelle krav:**

#### FR-7: Beregne forenklet kostnad per kandidat

*Prioritet: Kjerne.*

Systemet kan beregne Vaktkostnaden for hver Gyldig kandidat etter modellen over, med ordinære og eventuelle overtidstimer.

**Konsekvenser (testbare):**
- Samme fullstendige strukturerte beslutningsgrunnlag (Kandidat, Vakt, øvrig Turnus og timelønn) gir samme beregnede kostnad hver gang (reproduserbart).
- 32 eksisterende timer + en ny åttetimersvakt ved 300 kr/t gir 3 000 kr i Vaktkostnad (4 t × 300 + 4 t × 450). Ved 40 eksisterende timer gir vakten 3 600 kr.
- En søndag 23–mandag 07-vakt fordeles med 1 t i første og 7 t i neste uke uten sommertidsskifte. Ved 36/20 eksisterende timer og 300 kr/t gir dette 2 550 kr (1 × 450 + 7 × 300). Nøyaktig 36 t, ukeskifte og begge sommertidsskifter er grensetilfeller.
- Vis samlet Vaktkostnad med to desimaler og «Ordinær» når ingen nye timer er overtid, ellers «Inkluderer overtid». Detaljer viser timer × sats per del, slik at de summerer til beløpet. Visningsavrunding endrer ikke uavrundet poengberegning.
- Beregningen er ikke avhengig av KI.

**Out of Scope:**
- Full lønnskostnad med alle tillegg, avgifter og tariffregler (eksplisitt utenfor omfang, jf. brief).

#### FR-8: Vise gjeldende timebelastning per kandidat

*Prioritet: Kjerne.*

Systemet kan vise hvor mye hver Gyldig kandidat allerede er satt opp til å arbeide i den aktuelle uken, som andel av normaluken på 36 timer (samme terskel som FR-7). Dette er Timebelastningen, den ene av arbeidsbelastningens to deler. Den andre er Ulempebelastningen (FR-14).

**Terskel:** Timebelastningen er Kandidatens eksisterende timer i kalenderuken den valgte Vakten **starter** i, delt på 36 timer. Også timer fra en eksisterende Vakt som startet i forrige uke fordeles etter faktisk overlapp. Den vurderte Vakten legges ikke til her. Visningen bytter til «høy belastning» ved **minst 32,4 timer (32 t 24 min)** før visningsavrunding. Dette er kun en visuell indikator og endrer ikke rangeringspoeng. En Kandidat med 32 timer er derfor under grensen.

**Konsekvenser (testbare):**
- Timebelastningen oppdateres konsistent med Turnusens øvrige Vakter for Kandidaten.
- Prosentandelen beregnes som eksisterende timer i startuken ÷ 36. Ved 32 t 23 min vises ikke «høy belastning», ved 32 t 24 min vises den; avrundet timetekst må ikke skjule hvorfor fargen skifter. Prosent over 100 kan vises selv om linjen stopper ved full bredde.

#### FR-14: Beregne og vise ulempebelastning per kandidat

*Prioritet: Kjerne.*

Systemet kan beregne Ulempepoeng for hver Gyldig kandidat etter Ulempemodellen over, ut fra Kandidatens Vakter i de 672 faktiske timene før Vaktens start, og regne dem om til en Ulempescore på fast skala. Ulempebelastningen vises separat fra Timebelastningen, med samlet poengsum og fordeling på kveld-, helg- og nattetimer. *Lagt til 2026-10-30. Nummeret er valgt for å unngå omnummerering.*

**Konsekvenser (testbare):**
- Samme fullstendige strukturerte beslutningsgrunnlag (Kandidat, Vakt og dokumentert historikk) gir samme Ulempepoeng og Ulempescore hver gang (reproduserbart).
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
| Ansattpreferanse | 25 % | Fem faste nivåer: 100, 75, 50, 25 eller 0 poeng etter §4.5. Manglende tekst gir 50 poeng merket «ingen registrert preferanse»; ventende/feilet tolkning av registrert tekst gir midlertidig 50 med egen status (P-05). |


Totalscore = 0,40 × kostnadspoeng + 0,20 × timebelastningspoeng + 0,15 × Ulempescore + 0,25 × preferansepoeng. Kompetanse vurderes utelukkende som Hard regel i FR-2.

Kostnad og Timebelastning bruker en skala relativ til de Gyldige kandidatene. Ulempebelastning bruker fast skala, slik at små forskjeller i Ulempepoeng ikke gir store utslag (begrunnelse i §4.3). Vektene og taket for Ulempescore ligger samlet som navngitte parametere i domenekjernen.

**Like verdier og avrunding:** Hvis alle Gyldige kandidater har samme kostnad eller samme Timebelastning, får alle 50 poeng for den aktuelle faktoren. Dette gjelder også når bare én Kandidat er gyldig. Faktorpoeng og totalscore beregnes og sorteres uavrundet; ved identisk totalscore sorteres Kandidatene på stigende ansatt-ID. Faktorpoeng og totalscore avrundes bare ved visning, til én desimal. Lik visningsscore betyr derfor ikke nødvendigvis lik totalscore.

**Funksjonelle krav:**

#### FR-9: Rangere gyldige kandidater

*Prioritet: Kjerne.*

Systemet kan rangere **alle** Gyldige kandidater for en Vakt basert på modellen over. Min–maks beregnes over alle Gyldige før listen begrenses til de fem høyest rangerte. Finnes færre enn fem, vises alle; finnes ingen, gjelder FR-6. Turnusansvarlig kan velge «Vis alle gyldige kandidater» eller tilsvarende for å se og velge øvrige etter FR-12.

**Konsekvenser (testbare):**
- Minst ett testscenario demonstrerer at den billigste Kandidaten ikke rangeres høyest, fordi andre Myke faktorer samlet sett veier tyngre.
- Minst ett testscenario har to Gyldige kandidater med **identisk** kostnad, Timebelastning og preferansepoeng, men ulik Ulempebelastning; Ulempescoren alene forklarer forskjellen i totalscore og rekkefølge. Testdataene har et slikt par med 7,0 totalpoengs forskjell (§10).
- Samme input (Kandidater, Vakt, preferanser) gir samme rangeringsrekkefølge hver gang — poengmodellen er en ren, deterministisk beregning, ikke avhengig av KI.
- Når alle Gyldige kandidater har samme kostnad, får alle 50 kostnadspoeng. Når alle har samme Timebelastning, får alle 50 timebelastningspoeng. Begge særreglene gjelder også ved én Gyldig kandidat. Ulempescore beregnes fortsatt på sin faste skala.
- To Kandidater med identisk uavrundet totalscore rangeres etter stigende ansatt-ID. Visningsavrunding endrer verken rekkefølgen eller hvilke inntil fem Kandidater som vises.

### 4.5 KI-forklaring av avveininger

**Beskrivelse:** KI tolker tekstbaserte Ansattpreferanser og genererer en forståelig forklaring per Kandidat: hvorfor Kandidaten kan ta Vakten, hva som trekker opp, hva som trekker ned, kostnadsvurdering og relevante Ansattpreferanser. KI forklarer og tolker — den beregner aldri Harde regler, arbeidstid eller kostnad, og kan aldri overstyre Rangeringen eller utføre en endring selv.

**Funksjonelle krav:**

#### FR-10: Tolke tekstbaserte ansattpreferanser

*Prioritet: Kjerne.*

Systemet kan bruke en språkmodell til å tolke tekstbaserte Ansattpreferanser og gjøre dem tilgjengelige som input til Rangeringen (§4.4).

Registrerte Ansattpreferanser gjelder hele demonstrasjonsperioden. v1 har ikke preferanser med egne gyldighetsdatoer.

**Konsekvenser (testbare):**
- Tolkede preferanser sendes som strukturert kategori til Rangeringen. Koden tildeler kategoriens faste poengsum; språkmodellen utfører ikke selve poengberegningen eller Rangeringen.
- Alle de 15 definerte preferansetekstene under skal tolkes til forventet kategori. Eksakt ordlyd i KI-forklaringen er ikke en del av fasiten.
- Manglende registrert preferanse gir 50 poeng og merkes «ingen registrert preferanse». Det skal ikke fremstilles som et uttrykkelig nøytralt ønske.
- Registrert tekst som venter på første tolkning gir midlertidig 50 poeng med «Preferanse venter på tolkning»; feilet/ugyldig tolkning gir midlertidig 50 med «Preferanse kunne ikke tolkes». Råteksten og status beholdes, uten oppdiktet nøytral tolkning. Kandidaten utelukkes ikke, og brukeren ser at rangeringen kan endres.
- Ved forbigående feil (nettverksfeil, serverfeil eller for mange kall) gjør systemet høyst tre automatiske nye forsøk. Senest 90 sekunder etter første kall får tolkningen status feilet. Etter endelig feil kan Turnusansvarlig be om nytt forsøk. Vellykket tolkning lagres for den aktuelle teksten og oppdaterer rangeringen før bekreftelse; endret tekst bruker aldri gammel tolkning. En gyldig kategori som oppdages som semantisk feil følger feilflyten. Ukjent tekst i Demo-modus er ikke «ingen registrert».

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

*Prioritet: Kjerne. Valgfri sammenligning av to merkede kandidater er Strekk.*

Systemet kan generere en KI-basert forklaring for hver Kandidat i Rangeringen: hvorfor Kandidaten kan ta Vakten, hvilke forhold som trekker opp, hvilke som trekker ned, kostnadsvurdering, og relevante Ansattpreferanser.

**Konsekvenser (testbare):**
- Forklaringen nevner aldri en Kandidat som er utelukket av en Hard regel (testbar invariant, jf. addendum §4).
- Forklaringen kan vise til Timebelastning og Ulempebelastning med fordeling på kveld, helg og natt, men bare med tallene regelmotoren har beregnet. KI beregner dem aldri selv.
- Ved feil, tomt eller ubrukelig svar fra språkmodellen viser systemet en forhåndsdefinert reservetekst eller feilmelding i stedet for KI-forklaringen — aldri en anbefaling uten gyldig grunnlag — og systemet fortsetter å fungere uten å krasje.
- KI returnerer strukturerte begrunnelser fra et avgrenset sett. Koden validerer kandidat-/faktareferanser og sammenligningens retning mot beregnet, uavrundet grunnlag og setter inn beregnede navn og tall. Ett ugyldig påstandsfelt forkaster hele forklaringen til fordel for tydelig merket Reservetekst. Rangering og Godkjenning forblir tilgjengelig.
- Tillatte begrunnelsestyper i v1 er at Kandidaten oppfyller de fire prototypereglene, at en navngitt beregnet faktor trekker opp eller ned, og at en faktor/totalscore er høyere, lavere eller lik den forhåndsberegnede referansens. «Lik» krever lik uavrundet verdi. KI leverer type og referanse, ikke egne tall eller navn.
- Forklaringen kan bruke én forhåndsberegnet, Gyldig referansekandidat: nr. 1 sammenlignes med nr. 2, øvrige med nr. 1. Ved én Gyldig kandidat er ingen referanse tilgjengelig. KI kan ikke velge referansen, finne på sammenligninger eller nevne utelukkede kandidater. Valgfri sammenligning av to merkede kandidater er Strekk.

**Feature-spesifikke NFR-er:**
- Grensen mellom deterministisk lag (§4.2–§4.4) og KI-laget er en hard systemgrense: KI mottar allerede filtrerte og beregnede data, og kan ikke endre dem.
- **Kjørbar uten gruppens API-nøkkel:** Systemet kan kjøres i Demo-modus uten nøkkel til språkmodellen. Tolkede preferanser og Avveininger kommer da fra modellsvar som er generert på forhånd og lagret i testdataene, eller fra en mal bygd utelukkende av de beregnede tallene. Brukergrensesnittet viser alltid om en Avveining er live, forhåndsgenerert eller malbasert. En feil i live-modus gir reservetekst (FR-11), ikke stille overgang til demo-modus.

### 4.6 Godkjenning av erstatter

**Beskrivelse:** Turnusansvarlig velger og bekrefter hvilken Kandidat som skal settes inn i Vakten. Turnushjelperen gjennomfører aldri en endring på egen hånd.

**Funksjonelle krav:**

#### FR-12: Godkjenne valgt kandidat

*Prioritet: Kjerne.*

Turnusansvarlig kan velge en hvilken som helst Gyldig kandidat fra Rangeringen — ikke nødvendigvis den øverst rangerte — og gi eksplisitt Godkjenning.

**Konsekvenser (testbare):**
- Ingen endring i Turnusen anses gjennomført før Godkjenning er gitt.
- Systemet kan ikke gjennomføre en Godkjenning automatisk eller uten Turnusansvarliges eksplisitte handling.
- Ved Godkjenning kontrollerer systemet de fire Harde reglene på nytt mot gjeldende Turnus før noe lagres. Er Kandidaten ikke lenger gyldig, lagres ingenting, og Turnusansvarlig får en melding om dette.
- Hvis øvrig beslutningsgrunnlag har endret seg siden visningen, forkastes den gamle vurderingen; nye beregninger vises og Turnusansvarlig må bekrefte på nytt. Forsinkede KI-svar fra tidligere Vakt eller Kandidat brukes ikke. En Datafeil stopper også Godkjenning.
- Ved vellykket Godkjenning lagres hvem som overtar hvilken Vakt og når Godkjenningen ble gitt, og Vakten bemannes med den valgte Kandidaten. Resultatet lagres varig og er synlig når Turnusen åpnes på nytt.
- Etter lagring vises en bekreftelse på Vaktvalg, og Vakten vises blant bemannede Vakter i stedet for under «Krever handling».
- En ny Godkjenning for samme allerede godkjente erstatning avvises, også ved dobbeltklikk. Det finnes bare én Godkjenning for Vakten.
- Den viste KI-forklaringen lagres ikke historisk som del av Godkjenningen. Eventuell senere lagring av nøyaktig vist forklaring og tilhørende beregningsgrunnlag krever egen beslutning og story.


### 4.7 Innlogging

**Beskrivelse:** Enkel innlogging for Turnusansvarlig, slik at Turnushjelperen ikke er åpen for alle — ingen andre roller finnes i v1.

**Funksjonelle krav:**

#### FR-13: Logge inn som turnusansvarlig

*Prioritet: Kjerne.*

Turnusansvarlig kan logge inn med brukernavn og passord for å få tilgang til Turnushjelperen.

**Konsekvenser (testbare):**
- Ingen funksjonalitet i §4.1–§4.6 er tilgjengelig uten gyldig innlogging. Det gjelder både sidene og API-et.
- Feil brukernavn og feil passord gir samme melding, «Feil brukernavn eller passord.», slik at meldingen ikke røper hvilket som var feil.
- Passord lagres aldri i klartekst, bare som saltet hash.
- En økt varer i 480 minutter (én vakt). Når økten er utløpt, sendes Turnusansvarlig til innloggingen, og ingen data vises. Turnusansvarlig kan også logge ut selv.
- API-nøkler og andre hemmeligheter ligger aldri i repoet, i testdataene eller i grensesnittet.

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

Hva som er planlagt etter kjerneflyten, og hva som er Strekk, står i §6.2.

## 6. MVP-omfang

### 6.1 Inkludert

- Én fiktiv Turnus med ca. 20–30 ansatte (§2.2, §4.1).
- Filtrering av Kandidater på fire Harde regler: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen (§4.2).
- Forenklet kostnads- og arbeidsbelastningsvurdering per Gyldig kandidat, med Timebelastning og Ulempebelastning hver for seg (§4.3).
- Rangering av Gyldige kandidater etter kostnad (40 %), arbeidsbelastning (35 %: Timebelastning 20 %, Ulempebelastning 15 %) og Ansattpreferanse (25 %) (§4.4).
- KI-tolkning av tekstbaserte Ansattpreferanser og KI-generert forklaring per Kandidat (§4.5).
- Menneskelig Godkjenning som forutsetning for enhver endring (§4.6).
- Enkel innlogging for Turnusansvarlig (§4.7).

Alle FR-ene i §4 er Kjerne.

### 6.2 Etter kjerne, Strekk og utenfor v1

**Etter kjerne (planlagt i v1, starter når kjerneflyten virker):**
- Turnusansvarlig kan redigere preferanseteksten til en Ansatt i appen. Ny tekst tolkes av KI og gir ny Rangering, og gammel tolkning og forklaring gjelder ikke lenger. Storyen trenger egne krav til lagring og tilgangskontroll. *Begrunnelse:* Det gjør KI-tolkningen prøvbar for sensor med egne tekster, men kjerneflyten virker uten. Rekker ikke tiden, dokumenteres den som utsatt.

**Strekk (bare hvis det er tid igjen):**
- Valgfri sammenligning av to merkede Kandidater i forklaringen (FR-11). *Begrunnelse:* Standardsammenligningen med én referanse dekker brukerreisen.
- Historisk lagring av nøyaktig vist forklaring og beregningsgrunnlag ved Godkjenning (FR-12). *Begrunnelse:* Ikke krav i v1, og det trenger egen beslutning og story før det kan bygges.

**Utenfor v1:**
- Alt listet i §5 Ikke-mål. Ansattportal og mer avansert autentisering er senere muligheter.

## 7. Suksesskriterier

**Primære**
- **SM-1**: 100 % av Kandidatene som bryter en implementert Hard regel filtreres bort i definerte testscenarioer. Validerer FR-2 til FR-5.
- **SM-2**: En Kandidat utelukket av en Hard regel blir aldri anbefalt av KI — testbar invariant. Validerer FR-9, FR-11.
- **SM-3**: Turnusansvarlig får presentert inntil fem av de høyest rangerte Gyldige kandidatene for en fiktiv Turnus (20–30 ansatte) uten å måtte kontrollere alle manuelt. *Forslag til målbar form, ikke vedtatt:* Rett etter vaktvalg, uten flere handlinger, vises inntil fem høyest rangerte Gyldige kandidater sammen med antall utelukkede per Hard regel. Validerer FR-1, FR-9.
- **SM-4**: Systemet forklarer hvilke faktorer som påvirker Rangeringen av hver Kandidat. *Forslag til målbar form, ikke vedtatt:* Hver forklaring, også Reserveteksten, viser Vaktkostnad, Timebelastning, Ulempebelastning og preferansekategori med tallene regelmotoren har beregnet. Validerer FR-11.
- **SM-5**: Samme strukturerte input gir samme resultat hver gang for Harde regler, kostnadsberegninger, Timebelastning og Ulempebelastning (reproduserbarhet). Validerer FR-2 til FR-9 og FR-14.
- **SM-6**: Minst ett scenario demonstrerer at den billigste Kandidaten ikke nødvendigvis rangeres høyest. Validerer FR-9.
- **SM-7**: KI tolker alle 15 definerte preferansetekster i §4.5 til forventet kategori og bruker tolkningen i forklaringen. Manglende registrert preferanse gir 50 poeng og vises som «ingen registrert preferanse». Validerer FR-10, FR-11.
- **SM-8**: Turnusansvarlig er alltid den som tar den endelige beslutningen (Godkjenning kreves). Validerer FR-12.
- **SM-9** *(teknisk kvalitet)*: Systemet kan bygges og kjøres fra et rent klonet repo, uten manuelle unntak eller udokumenterte oppsettsteg, og uten gruppens API-nøkkel (demo-modus, §4.5). Validerer hele leveransen (§4); addendum §6 peker på dette som et teknisk kvalitetskriterium som bør videreføres i PRD/spec. **[ASSUMPTION]** Tolkningen av «rent klonet repo» er utledet av addendum §6, ikke eksplisitt bekreftet av gruppen (§9).

**Motmetrikker (skal ikke optimeres)**
- **SM-C1**: Antall implementerte Harde regler skal ikke maksimeres på bekostning av testdekning per regel — addendums anbefaling («fire regler som beviselig fungerer er verdt mer enn tolv som er halvveis») veier tyngre enn regelmengde. Motvirker en eventuell trang til å utvide §4.2 uten tilsvarende testarbeid.
- **SM-C2**: Rask responstid på KI-forklaringen skal ikke optimeres på bekostning av at forklaringen faktisk er korrekt og aldri nevner en utelukket Kandidat. Motvirker SM-3/SM-4 ved å hindre at hastighet trumfer den testbare invarianten i SM-2. *Forslag til målbar form, ikke vedtatt:* Ingen KI-forklaring vises før faktakontrollen i FR-11 er bestått, og senest 90 sekunder etter første kall vises Reservetekst i stedet.

## 8. Åpne spørsmål

Disse spørsmålene er ikke avgjort. Hvert har eier og frist.

| Spørsmål | Eier | Frist |
|---|---|---|
| Skal Turnushjelperen støtte mobil og nettbrett, og i så fall med hvilken visning? Desktop er bindende nå. | Hele gruppa | Etter at kandidatvisningen virker, og før story 4.6 ferdigstilles |
| Hvilken OpenRouter-nøkkel får sensor, hvem betaler, og hvor mye kreditt får den? Den felles utviklingsnøkkelen eller en egen sensornøkkel. | Ikke bestemt | Før innlevering, ut fra faktisk forbruk |
| Skal de målbare formene av SM-3, SM-4 og SM-C2 i §7 vedtas, endres eller strykes? | Hele gruppa | Før story 5.3 (Avveining per kandidat) starter |

### 8.1 Gjennomføring og kontroll (ikke krav)

Kravene over er vedtatt. Kontrollene under er arbeid som gjenstår i stories og tester, ikke åpne spørsmål. Status står i `sprint-status.yaml` og epics.

1. P-01–P-04: Implementer og test merkostnad per berørt uke, ukeskifte/sommertid, detaljert kostnadsvisning og 32:23/32:24-grensen. Ingrid beholdes på 32 timer. Forventningen i spesifikasjonen for story 1.2 er rettet 2026-11-10, og fasiten for #4127 er uendret.
2. P-05–P-07: Fastsett KI-kontrakten i stories/arkitektur og test ventende/feilet tolkning, nye forsøk, faktakontroll og referanseregelen mot falsk OpenRouter. Manuell kontroll av norsk og mening kommer i tillegg.
3. P-08/P-09/P-11: Datafeil ved periodekanten, også for #4261–#4265, er bygd og testet i story 2.1–2.3. Gjenstår: gammelt svar og endret beslutningsgrunnlag (Epic 3), og tydelig forskjell mellom Datafeil og null gyldige (story 2.6).
4. P-10B: Story 5.9 er planlagt i backlog; prioriter implementasjon først etter fungerende kjerneflyt. Hvis tiden ikke rekker, før den som utsatt. P-12B krever først senere valg og er ikke v1-krav.
5. P-13/OP-02: Gruppen avklarer mobil/nettbrett etter fungerende kandidatvisning og før story 4.6 ferdigstilles. Gjennomfør og dokumenter en liten oppgavebasert forståelsestest: forklar nr. 1 uten hint, finn en annen gyldig Kandidat, skill datafeil fra null gyldige. Én testperson og ett operativsystem og én skjermflate holder. Akseptmål: alle tre oppgavene løses uten hint. Ellers rettes og noteres det som skapte misforståelsen. Testen er besluttet, ikke utført.
6. E-02: Kontroller levert funksjonalitet mot den godkjente proposalen i `ee6d798` ved innlevering, og forklar planavvik. E-01 er lukket: KI i produktet er et valgt produktscope, ikke et formelt emnekrav ifølge Johannes' gjengivelse av faglærers muntlige utsagn; forelesningsdato er ukjent.

### 8.2 Løste spørsmål (historikk)

Spørsmål som er løst underveis, med dato og grunnlag, står i [`.memlog.md`](.memlog.md) i denne mappen og i [beslutningsreferatet](../../../../docs/beslutninger/avklaringspunkter.md), blant annet P-01–P-13 (§12 i referatet). Historikken er tatt ut av PRD-en 2026-11-13 for å gjøre den kortere, etter faglærers tilbakemelding.

**Vurdert og bevisst utelatt fra denne PRD-en:** addendumets punkt om «arbeidsdeling og frister» er et prosjektstyringsspørsmål for gruppen, ikke et produktkrav — det hører hjemme i gruppens egen fremdriftsplan, ikke i PRD-en.

## 9. Antakelser-indeks

- Fra §2.3 (UJ-1): Persona-navnet «Kari» er oppdiktet for å gjøre brukerreisen konkret — representerer ingen reell bruker, i tråd med at Turnusen er fiktiv.
- Fra §4.2/§8: Regelutvalget (kompetanse-minstekrav, kolliderende vakt, 11-timersregelen, 35-timersregelen) er bekreftet av bruker; maks arbeidstid per døgn/uke og overtidsgrenser er bevisst utelatt fra v1 — revurderes bare hvis gruppen ønsker et bredere regelsett.
- Fra §4.3 (Ulempemodell): Taket på 300 Ulempepoeng bygger på regneeksempler med antatte, typiske turnusprofiler, ikke på en kilde, og kan justeres i én parameter. Helligdager som vanlige ukedager var en antakelse til gruppa bekreftet det 2026-11-02.
- Fra §7 (SM-9): Antakelse om at «kjører fra et rent klonet repo» er det addendum mener med teknisk kvalitetskriterium fra emnekravet — ikke eksplisitt bekreftet av gruppen, men utledet direkte fra addendum §6.
- Fra §4.2: Tilgjengelighet utover planlagte Vakter er en uttrykkelig demonstrasjonsforutsetning (AV-06), ikke en påstand om virkelig tilgjengelighet. Ukjent nødvendig historikk behandles som datafeil (P-08), aldri som dokumentert fri.

## 10. Sporing

Kravene i §4 står alene. Tabellen viser hvor de kommer fra, slik at den som skriver stories og tester, kan finne begrunnelsen. ID-ene er definert i [beslutningsreferatet](../../../../docs/beslutninger/avklaringspunkter.md) og [PRD-beslutningsgrunnlaget](../../../../docs/beslutninger/prd-beslutningsgrunnlag-2026-11-07.md). Stories står i [epics](../../epics.md), og AD-ene i [arkitekturen](../../architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md).

| Krav | Bygger på | Stories |
|---|---|---|
| FR-1 | P-08 (Datafeil), P-09 (forsinkede svar) | 1.5, 1.6 |
| §4.2 Kandidatgrunnlag, hvilekontroll og datadekning | AV-06, AV-04, P-08, KS-04. Testdataene slutter 05.10. Vaktene #4261–#4265 og andre som slutter etter 04.10 kl. 13:00, gir Datafeil. #4127 og #4189 er kontrollert. | 2.1–2.4 |
| FR-2 | AV-02 (mellomvakt bruker dag-nivå), P-08 | 2.1 |
| FR-3 | AV-02 | 2.2 |
| FR-4, FR-5 | AV-04 | 2.3, 2.4 |
| FR-6 | P-11, P-08 | 2.5, 2.6 |
| §4.3 Kostnadsmodell, FR-7 | P-01, P-02, P-03, K-03 | 4.3 |
| §4.3 Ulempemodell, FR-14 | ÅB-3 (utvidet), AV-09 (672 t), AV-11 (tak 300). Regneeksemplene: `scripts/ulempe_regneeksempler.py`. | 4.7 |
| FR-8 | P-02, P-04 (32,4 t). Ingrid i testdataene har 32 t og er under grensen. | 4.1, 4.2 |
| §4.4, FR-9 | AV-05, K-03, AV-12 (#4127: Jonas og Mette, 7,0 totalpoeng), KS-02 | 4.4 |
| FR-10 | P-05, OP-03, AV-06. Tre nye forsøk og 90 sekunder er fra AD-7. | 5.1, 5.2 |
| FR-11 | P-06, P-07, K-04, AD-6 (Demo-modus) | 5.3–5.7 |
| FR-12 | P-08, P-09, P-12, AD-5 | 3.1, 3.2 |
| FR-13 | Brief (én rolle). Bygd i story 1.3 og 1.4: scrypt med salt, økt i 480 minutter (`TURNUSHJELPEREN_JWT_MINUTTER`), ny kontroll og utlogging. | 1.3, 1.4 |
| §6.2 | P-10B, P-07 (valgfri sammenligning), P-12B | 5.9 |
| §8 Åpne spørsmål | OP-02 og P-13 (mobil og nettbrett), ÅB-8 (sensornøkkel) | 4.6, 5.8 |
