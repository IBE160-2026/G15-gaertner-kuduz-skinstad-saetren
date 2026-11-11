# Epic 2 Context: Gyldige kandidater for en vakt

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Etter vaktvalg ser turnusansvarlig hvem som faktisk kan ta vakten. Fire harde regler filtrerer bort resten: kompetanse-minstekrav, kolliderende vakt, 11-timersregelen og 35-timersregelen. En ekskludert-boks viser hvor mange som er utelukket og hvorfor, og en egen tomtilstand vises når ingen er gyldige. Reglene beregnes deterministisk i domenekjernen, uten KI, og hver regel bevises med grensetester, som er prosjektets sterkeste bevis på kvalitetssikring. Rangering, kostnad og KI-forklaring kommer i Epic 4 og 5.

## Stories

- Story 2.1: Gyldige kandidater filtrert på kompetanse-minstekrav
- Story 2.2: Filtrere bort kandidater med kolliderende vakt
- Story 2.3: Filtrere på 11-timersregelen (daglig hvile)
- Story 2.4: Filtrere på 35-timersregelen (ukentlig fri)
- Story 2.5: Ekskludert-boks med oppsummering av utelukkelser
- Story 2.6: Tydelig melding når ingen kandidater er gyldige

## Requirements & Constraints

- **KI-grense (absolutt):** KI beregner aldri harde regler, arbeidstid eller hvile. Epicet gjør ingen KI-kall. En utelukket Kandidat skal aldri nå rangering eller KI-laget, og det er en testbar invariant.
- **Reproduserbart:** samme Kandidat og Vakt gir samme resultat hver gang, uten tilfeldighet og uten avhengighet av klokke eller maskin.
- **Kandidatgrunnlag (AV-06):** alle Ansatte vurderes, unntatt den som var satt opp på Vakten. Det finnes ingen fraværsmodell, så en Ansatt som er syk fra en annen vakt, vurderes likevel. Overlappende vakter for ulike Ansatte er ikke et regelbrudd (AV-02).
- **Kompetanse:** gyldig når nivået for vakttypen er lik eller høyere enn Vaktens minstenivå. Under, eller manglende nivå, gir utelukkelse. Mellomvakten bruker nivået for dag. Nivåene er heltall 1–4. Minstekravet senkes aldri, og kompetanse gir ingen rangeringspoeng.
- **Kollisjon:** vakter er halvåpne intervall `[start, slutt)`. Ett minutts overlapp gir utelukkelse, mens vakter som bare berører hverandre, ikke gjør det. En vakt som omslutter Vakten eller ligger inne i den, gir utelukkelse. Overlapp regnes på faktiske tidspunkt, ikke kalenderdato.
- **11 t (AV-04):** minst 11 t mellom forrige vakts slutt og Vaktens start, og mellom Vaktens slutt og neste vakts start. 11:00 er gyldig, 10:59 gir utelukkelse. Tiden er faktisk forløpt tid, også over begge sommertidsskiftene.
- **35 t (AV-04):** etter at Vakten er lagt til, må hver berørt kalenderuke ha minst 35 t sammenhengende fri. Uka går mandag 00:00 til neste mandag 00:00 i `Europe/Oslo`. 35:00 er gyldig, 34:59 gir utelukkelse. Krysser Vakten ukeskiftet, sjekkes begge ukene. Uker med sommertidsskifte har 167 eller 169 faktiske timer.
- **Avgrensning (AV-04, OP-01):** reglene presenteres ikke som full juridisk kontroll etter arbeidsmiljøloven. Tariffunntak (8 t og 28 t), maks arbeidstid og overtidsgrenser er utelatt.
- **Datafeil (P-08):** ukjent historikk er ikke det samme som fri. Mangler nødvendig turnusdekning, gyldige tider eller Vaktens minstekrav, stoppes vurderingen uten liste og uten Godkjenning, og meldingen oppgir datagrensen (seeddataene slutter 05.10.2026 kl. 00:00). Manglende kompetansenivå hos en Kandidat er utelukkelse, ikke datafeil. Datafeil vises aldri som «ingen gyldige». Story 2.1 dekker bare grunnlaget kompetanseregelen trenger, og 2.3 og 2.4 utvider sjekken til nabovakter og hele uker og avgjør hvor historikken starter.
- **Vindu for datafeil (vedtatt 2026-11-11, PR #14, alternativ B):** datafeilsjekken for Kandidatens vakter gjelder bare vakter som kan påvirke reglene, innenfor et vindu rundt Vakten per regel: overlapp (2.2), ±11 t (2.3) og hele berørte kalenderuker (2.4). Ugyldig historikk innenfor vinduet gir fortsatt datafeil. Story 2.3 har bygget vinduet og rettet sjekken: `Regel.vindu`, det samlede vinduet må ligge innenfor `[historikkstart, datagrense]`, og bare Kandidatens vakter i vinduet valideres. Historikken starter ved `turnus.periode_start − 672 t` (24.08.2026 kl. 00:00, beslutning 2A). Vakter som slutter etter 04.10 kl. 13:00, gir nå datafeil. Se avklaringspunktene, §11.
- **Ingen gyldige kandidater (FR6, P-11):** 200-svar med `status: "ingen_gyldige_kandidater"`. Tomtilstanden viser utelukkelsesoppsummeringen og teksten «Innleie av personell kan vurderes», uten knapp.
- **Tester:** hver regel har egen modul under `tester/regelmotor/` som dekker grensetilfellene, og er ikke ferdig uten. Fasiten i seeden er beregnet på forhånd (AV-07), regelmotoren skal stemme med den, og fasiten tilpasses aldri koden.
- **Fasit (KS-04 utført for disse to vaktene):**
  - #4127, dagvakt 27.09 07–15, minstenivå 3: 20 utelukket (8 kompetanse, 7 kollisjon, 4 på 11 t, 1 på 35 t) og 4 gyldige: Jonas, Mette, Thomas og Ingrid.
  - #4189, nattevakt 28.09 23–07, minstenivå 3: alle 24 utelukket (3 kompetanse, blant dem Silje som mangler nivå for natt, 2 kollisjon, 18 på 11 t, 1 på 35 t).
  - Ingen bryter mer enn én regel på samme vakt, med vilje.
- **Dokumentasjon:** KI-generert kode logges i `docs/ki-logg/`. Grensesnittet er bare på norsk bokmål.

**Motstrid og åpne spørsmål (må avklares, skal ikke fylles med antakelser):**

1. **Overlappende vakter og 11 t:** avgjort av Mithad som eier av story 2.3 (beslutning 1A, 2026-11-11, OP-12): en overlappende vakt teller bare som kolliderende vakt, og nærmeste ikke-overlappende vakt avgjør 11 t, som testhjelperne fra story 1.2. Implementert i 2.3.
2. **#4261–#4265 som datafeileksempel:** story 2.1 i epics nevner dem, men de er bemannede og gir 404 fra vaktdetaljene, så datafeilen nås ikke gjennom vanlig flyt. Den testes i domenet og med endret testdatabase. Story 2.3 valgte at historikken starter ved `periode_start − 672 t` (beslutning 2A).
3. **Merknaden `[ASSUMPTION]` i story 2.4** («testdataene dekker hele kalenderuker») er erstattet av P-08 og KS-04, men står fortsatt i epics.
4. **Eksempeltallene** i UX og story 2.5 («21 utelukket», «9 under kompetanse-minstekrav · 7 kolliderende vakt») stemmer ikke med fasiten for #4127. Tester og tekst følger fasiten.
5. **Nivåbegrepet:** ordlisten i PRD sier at nivåene går «fra delvis opplært», mens seeden har fire nivåer fra «Under opplæring». Tag-teksten følger seeden.

## Technical Decisions

- Regelmotoren i `domene/regelmotor` er ren Python. Domenetypene er rene Python- eller Pydantic-typer, og konverteringen fra SQLAlchemy skjer i `adaptere/lagring` (AD-5). Regelmotoren får alt som argumenter og kaller verken database, nett eller klokke.
- En import-linter-kontrakt hindrer `domene` i å importere `adaptere/*`, og kjøres som del av `pytest` (AD-1, AD-2). Den er på plass fra story 2.1.
- Reglene ligger i en felles regelliste i `domene/regelmotor/vurdering.py`. En ny regel legges inn der med årsak, sjekk og det den krever av grunnlaget, og datafeilsjekken arves. Kandidatene må utvides med vaktene reglene trenger, siden de i dag bare bærer id, navn og kompetanse.
- Alle tidspunkt er tidssonebevisste i `Europe/Oslo`, og lagringen avviser naive `datetime`. Varigheter og sammenligning regnes i faktisk forløpt tid (UTC), ikke etter veggklokka, på grunn av timen som går to ganger når sommertiden slutter. `tzdata` trengs på Windows.
- Hver Kandidat vurderes mot alle reglene uten å stoppe ved første brudd, og alle årsakene samles. Årsakene heter «kompetanse-minstekrav», «kolliderende vakt», «11-timersregelen» og «35-timersregelen».
- Porten `UtelukkelsesOppsummering` ligger i `domene/porter` og konstrueres bare av regelmotoren. Den gir antall per regel og total, og en Kandidat telles én gang i totalen.
- API-et svarer 200 med `status`: `ok`, `ingen_gyldige_kandidater` eller `datafeil`. Faktiske feil har formen `{kode, melding}`. Datafeil er vedtatt som 200 med `status: "datafeil"`, `kode: "mangler_turnusgrunnlag"` og `datagrense` (ISO 8601 med offset), uten kandidatliste, og binder story 2.6. Frontend viser tekst fra egen tekstliste ut fra `kode` eller `status`, aldri `melding`. Tidspunkt sendes som ISO 8601 med offset.
- Til Rangering kommer i Epic 4, sorteres listen alfabetisk på navn i norsk rekkefølge, med id som likhetsbryter.
- Fasitens testhjelpere i `tester/lagring/test_testdata.py` er bare for å kontrollere fasiten. Regelmotoren skal ikke importere dem.

## UX & Interaction Patterns

- Kandidatflaten ligger på `/vakt/<nr>/kandidater`. Filtreringen starter automatisk, og hver Kandidat vises med navn og Kompetansenivå som nøytral tag. Story 2.1 la inn en midlertidig merknad om at bare kompetanse er filtrert, som fjernes i 2.4.
- Ekskludert-boksen står under listen med stiplet kant og bakgrunn `#f7f9fb`. Den viser total og antall per regel, og «Vis full liste ▾» viser hver utelukket Ansatt med alle årsaker og kan lukkes igjen. Den skal ikke skjule at avdelingen har over 20 ansatte.
- Tomtilstanden har et sirkulært «!»-ikon i `danger` og teksten «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» Ekskludert-boksen vises fortsatt.
- Lasting, feil, datafeil og ingen gyldige har ulik tekst og ulikt utseende, og en test viser at ingen er like. Datafeilen sier «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» og oppgir datagrensen.
- `danger` brukes bare for faktiske utelukkelser og tomtilstanden. Teksten er kort, uten utropstegn, og antyder aldri at systemet har valgt noe.
- Alt kan nås med tab og enter, med semantisk HTML. Komponentene bruker bare designtokens (AV-13), og innholdet har `max-width: 1180px` (AV-14). Desktop er bindende nå, mens mobil og nettbrett avklares etter en fungerende kandidatvisning (P-13, OP-02).
- Et forsinket svar for en tidligere valgt vakt skal ikke erstatte visningen av den aktive vakten (P-09).

## Cross-Story Dependencies

- Epicet bygger på story 1.2 (seed, fasit, kompetanse per vakttype, `satt_opp_ansatt_id`), 1.4 (sesjon) og 1.6 (kandidatflaten og vaktdetaljene).
- Story 2.3 er implementert: 11-timersregelen er regel nummer tre, og vinduet per regel avgrenser datafeilsjekken. 2.4 legger til hele berørte uker som vindu i samme mønster og fjerner den midlertidige merknaden.
- Story 2.1 er implementert og la grunnmønsteret: domenetyper, regelliste, import-linter, API-kontrakt og datafeil-stopp. 2.2–2.4 legger nye regler inn i samme løp, og etter hver story er listen filtrert på alle reglene så langt.
- Story 2.5 forutsetter at alle årsaker samles. Seeden har ingen Ansatt med flere brudd, så telling med flere brudd må testes med enhetsdata i domenet. Story 2.6 bygger på at datafeil og ingen gyldige holdes adskilt.
- Nedstrøms: Epic 3 kjører regelkontrollen på nytt ved Godkjenning, Epic 4 rangerer bare gyldige Kandidater, og lekkasjetesten i story 5.6 bruker ID-ene til utelukkede Kandidater fra regelmotoren.
