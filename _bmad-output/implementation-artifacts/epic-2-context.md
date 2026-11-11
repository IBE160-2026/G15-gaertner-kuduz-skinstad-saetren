# Epic 2 Context: Gyldige kandidater for en vakt

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Etter vaktvalg ser turnusansvarlig hvem som faktisk kan ta vakten. Fire harde regler filtrerer bort resten: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen og 35-timersregelen. En ekskludert-boks viser hvor mange som er utelukket og hvorfor, og en egen tomtilstand vises når ingen er gyldige. Reglene beregnes deterministisk i domenekjernen, uten KI, og hver regel bevises med grensetester. Det er prosjektets sterkeste bevis på kvalitetssikring. Epicet håndhever også grensen mellom domene og adaptere. Rangering, kostnad og KI-forklaring kommer i Epic 4 og 5.

## Stories

- Story 2.1: Gyldige kandidater filtrert på kompetanse-minstekrav
- Story 2.2: Filtrere bort kandidater med kolliderende vakt
- Story 2.3: Filtrere på 11-timersregelen (daglig hvile)
- Story 2.4: Filtrere på 35-timersregelen (ukentlig fri)
- Story 2.5: Ekskludert-boks med oppsummering av utelukkelser
- Story 2.6: Tydelig melding når ingen kandidater er gyldige

## Requirements & Constraints

- **KI-grense (absolutt):** KI beregner aldri harde regler, arbeidstid eller hvile. Epicet gjør ingen KI-kall. En utelukket Kandidat skal aldri kunne nå rangering eller KI-laget, og det er en testbar invariant.
- **Reproduserbart:** samme Kandidat og Vakt gir samme resultat hver gang. Ingen tilfeldighet og ingen avhengighet av systemklokke eller maskin.
- **Kandidatgrunnlag (AV-06, vedtatt):** alle Ansatte i Turnusen vurderes, unntatt den som var satt opp på Vakten. Alle andre regnes som tilgjengelige, og det finnes ingen fraværsmodell, så en Ansatt som er meldt syk fra en annen vakt, vurderes likevel. At to ulike Ansatte har vakter som overlapper, er ikke et regelbrudd (AV-02).
- **Kompetanse:** en Kandidat er gyldig når nivået for vakttypen er lik eller høyere enn Vaktens minstenivå. Nivå under minstenivået gir utelukkelse, og det gjør også et manglende nivå. Mellomvakten bruker nivået for dag (AV-02, story 1.2). Nivåene er heltall 1–4: Under opplæring, Delvis opplært, Kvalifisert og Fullt kvalifisert. Minstekravet senkes aldri, selv om ingen oppfyller det. Kompetanse gir ingen rangeringspoeng og vises bare som tag.
- **Kollisjon:** vakter er halvåpne intervall `[start, slutt)`. Ett minutts overlapp gir utelukkelse, mens vakter som bare berører hverandre, ikke gjør det. En vakt som omslutter Vakten eller ligger inne i den, gir utelukkelse. Overlapp regnes på faktiske tidspunkt, ikke på kalenderdato.
- **11 t (AV-04, vedtatt prototypetolkning):** det må være minst 11 t mellom forrige vakts slutt og Vaktens start, og mellom Vaktens slutt og neste vakts start. 11:00 er gyldig og 10:59 gir utelukkelse. Tiden regnes som faktisk forløpt tid, også over begge sommertidsskiftene.
- **35 t (AV-04):** etter at Vakten er lagt til, må hver berørt kalenderuke ha minst 35 t sammenhengende fri. Uka går fra mandag 00:00 til neste mandag 00:00 i `Europe/Oslo`. 35:00 er gyldig og 34:59 gir utelukkelse. Krysser Vakten ukeskiftet, sjekkes begge ukene. Uker med sommertidsskifte har 167 eller 169 faktiske timer.
- **Avgrensning (AV-04, OP-01):** reglene skal ikke presenteres som full juridisk kontroll etter arbeidsmiljøloven. Tariffunntakene (8 t og 28 t), maks arbeidstid per døgn og uke og overtidsgrensene er bevisst utelatt.
- **Datafeil (P-08, vedtatt):** ukjent historikk er ikke det samme som fri. Mangler nødvendig turnusdekning, gyldige tider eller Vaktens minstekrav, stoppes vurderingen med datafeil. Da vises ingen liste og ingen Godkjenning, og meldingen oppgir den kjente datagrensen: seeddataene slutter 05.10.2026 kl. 00:00. At en Kandidat mangler kompetanse, er ikke en datafeil, men en utelukkelse. Datafeil skal aldri vises som «ingen gyldige».
- **Ingen gyldige kandidater (FR6, P-11):** svaret er et 200-svar med `status: "ingen_gyldige_kandidater"`. Tomtilstanden viser utelukkelsesoppsummeringen og teksten «Innleie av personell kan vurderes», uten knapp.
- **Tester:** hver regel har sin egen modul under `tester/regelmotor/` som dekker grensetilfellene, og en regel er ikke ferdig uten den. Testdekning per regel går foran antall regler. Fasiten i seeden er beregnet på forhånd (AV-07). Regelmotoren skal stemme med fasiten, og fasiten skal ikke tilpasses koden.
- **Fasit i seeden (KS-04 er utført for disse to vaktene):**
  - #4127 er dagvakt 27.09 07–15 med minstenivå 3. 20 er utelukket: 8 på kompetanse, 7 på kollisjon, 4 på 11 t og 1 på 35 t. 4 er gyldige: Jonas, Mette, Thomas og Ingrid.
  - #4189 er nattevakt 28.09 23–07 med minstenivå 3. Alle 24 er utelukket: 3 på kompetanse (blant dem Silje, som mangler nivå for natt), 2 på kollisjon, 18 på 11 t og 1 på 35 t.
  - Ingen bryter mer enn én regel på samme vakt. Det er gjort med vilje.
- **Dokumentasjon:** KI-generert kode logges i `docs/ki-logg/`. Grensesnittet er bare på norsk bokmål.

**Motstrid og åpne spørsmål (må avklares, skal ikke fylles med antakelser):**

1. **P-08 i story 2.1 lar seg ikke nå:** akseptansekravet bruker #4261–#4265 som eksempel på datafeil. Men disse vaktene er bemannet (04.10, minstenivå 2), og `GET /api/vakter/{nr}` fra story 1.6 svarer 404 for bemannede vakter. Datafeilen nås derfor ikke gjennom vanlig flyt. «Nødvendig turnusgrunnlag» betyr dessuten nabovakter ±11 t og hele berørte uker, og det hører til reglene i 2.3 og 2.4, mens kostnadsgrunnlaget hører til Epic 4. Forslag: 2.1 legger inn en generell dekningssjekk mot den kjente datagrensen, som 2.3 og 2.4 arver. Den testes i domenet og med en endret testdatabase, slik `test_vaktoversikt` allerede gjør.
2. **Formen på datafeilen er ikke fastsatt:** AD-4 lister bare statusene `ok`, `ingen_gyldige_kandidater` og `avveining_feilet`. Om datafeil blir en `{kode, melding}`-feil eller en egen `status` i et 200-svar, skal avgjøres «i berørte stories». Valget i 2.1 binder 2.6.
3. **Overlappende vakter og 11 t:** testhjelperne fra story 1.2 lar overlappende vakter høre bare til kollisjonsregelen og bruker nærmeste vakt som ikke overlapper, for 11 t. Det er nødvendig for at fasiten skal ha bare én regel per Ansatt, men det er en tolkning, ikke et gruppevedtak.
4. Kravet i story 2.4 merket `[ASSUMPTION]` («testdataene dekker hele kalenderuker») er erstattet av P-08 og KS-04.
5. Eksempeltallene i UX og mockup («21 utelukket», «9 under kompetanse-minstekrav · 7 kolliderende vakt») stemmer ikke med fasiten for #4127 (20 utelukket: 8 · 7 · 4 · 1). Tester og tekst skal følge fasiten.
6. Ordlisten i PRD sier at nivåene går «fra delvis opplært til fullt kvalifisert», mens story 1.2 har fire nivåer og begynner med «Under opplæring». Tag-teksten følger story 1.2.

## Technical Decisions

- Regelmotoren ligger i `domene/regelmotor` og er ren Python. Domenetypene, for eksempel Vakt og Kandidat, er rene Pydantic- eller Python-typer i `domene/`. Konverteringen fra SQLAlchemy skjer i `adaptere/lagring` (AD-5). Regelmotoren får alle data som argumenter og kaller verken database, nett eller klokke.
- En import-linter-kontrakt hindrer `domene/regelmotor` og `domene/porter` i å importere noen `adaptere/*`-pakke, og kontrakten kjøres som del av `pytest` (AD-1, AD-2). Import-linter er ikke installert ennå og må legges til som ny dev-avhengighet, låst eksakt som de andre pakkene.
- Alle tidspunkt er tidssonebevisste i `Europe/Oslo`, og lagringen avviser naive `datetime`. Varigheter regnes i faktisk forløpt tid, ikke etter veggklokka. `tzdata` er nødvendig på Windows.
- Hver Kandidat vurderes mot alle reglene uten å stoppe ved første brudd, og alle årsakene samles. Det trengs fordi Ekskludert-boksen teller per regel og den fulle listen viser alle årsaker. Årsakene heter «kompetanse-minstekrav», «kolliderende vakt», «11-timersregelen» og «35-timersregelen».
- Porten `UtelukkelsesOppsummering` ligger i `domene/porter` og konstrueres bare av regelmotoren. Den gir antall per regel og totalen, og en Kandidat telles én gang i totalen.
- API-et svarer 200 med `status` (`"ok"` eller `"ingen_gyldige_kandidater"`). Faktiske feil har formen `{kode, melding}`. Frontend henter teksten fra sin egen tekstliste ut fra `kode` eller `status` og viser aldri `melding`. Tidspunkt sendes i ISO 8601 med offset.
- Til rangeringen kommer i Epic 4, sorteres listen alfabetisk etter navn, slik at den blir deterministisk.
- Testhjelperne for de fire reglene i `tester/lagring/test_testdata.py` finnes bare for å sjekke fasiten. Regelmotoren er produksjonskoden og skal ikke importere dem.

## UX & Interaction Patterns

- Kandidatflaten ligger på `/vakt/<nr>/kandidater` (story 1.6). Filtreringen starter automatisk når flaten lastes. Hver Kandidat vises med navn og Kompetansenivå som nøytral tag (`tag-bg`).
- Ekskludert-boksen står under listen, med stiplet kant og bakgrunn `#f7f9fb`. Den viser totalen og antall per regel, kort og med tall. «Vis full liste ▾» viser hver utelukket Ansatt med alle årsaker, og listen kan lukkes igjen. Boksen skal ikke skjule at avdelingen har over 20 ansatte.
- Tomtilstanden har et sirkulært «!»-ikon i `danger` og teksten «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» Ekskludert-boksen vises fortsatt.
- Fire tilstander skal være ulike i både tekst og utseende: laster, feil, datafeil og ingen gyldige. Datafeilen har teksten «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» og oppgir datagrensen. En test skal vise at ingen av tilstandene er like.
- `danger` brukes bare for faktiske utelukkelser og tomtilstanden. Teksten er kort, uten utropstegn, og antyder aldri at systemet har valgt noe.
- Alt kan nås og brukes med tab og enter, og HTML-en er semantisk. Komponentene bruker bare designtokens (AV-13), og innholdet har `max-width: 1180px` (AV-14).
- Desktop er bindende nå. En fungerende kandidatvisning er milepælen der mobil og nettbrett avklares og forståelsestesten gjennomføres (P-13, OP-02).
- Et forsinket svar for en vakt som var valgt tidligere, skal ikke erstatte visningen av den aktive vakten (P-09).

## Cross-Story Dependencies

- Epicet bygger på story 1.2 (seed, fasit, kompetanse som JSON per vakttype, `minstenivå` og `satt_opp_ansatt_id`), 1.4 (sesjon) og 1.6 (kandidatflaten, `GET /api/vakter/{nr}` og plassholderen).
- Story 2.1 legger grunnlaget for resten av epicet: domenetypene, import-linter, kandidatgrunnlaget, API-kontrakten og datafeil-stoppen. 2.2–2.4 legger nye regler inn i samme løp, og etter hver story er listen filtrert på alle reglene som finnes så langt.
- Story 2.5 forutsetter at alle årsakene samles. Seeden har ingen Ansatt som bryter flere regler, så telling med flere brudd må testes med enhetsdata i domenet. Story 2.6 forutsetter at datafeil og ingen gyldige holdes adskilt fra og med 2.1.
- Nedstrøms:
  - Epic 3 kjører regelkontrollen på nytt ved Godkjenning.
  - Epic 4 rangerer bare gyldige Kandidater.
  - Kjøretidstesten for lekkasje i story 5.6 bruker ID-ene for utelukkede Kandidater fra regelmotoren.
