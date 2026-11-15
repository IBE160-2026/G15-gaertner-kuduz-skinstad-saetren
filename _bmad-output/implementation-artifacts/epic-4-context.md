# Epic 4 Context: Rangering etter kostnad, arbeidsbelastning og ansattpreferanser

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

De gyldige kandidatene (godkjent av regelmotorens harde regler i epic 2) rangeres etter kostnad, arbeidsbelastning og ansattpreferanse, slik at turnusansvarlig ser hvem som passer best uten å sammenligne manuelt. Arbeidsbelastningen deles i timebelastning og ulempebelastning, som vises hver for seg. Tabellen viser nøkkeltallene direkte i raden, og et nøytralt avviksnotat vises når en annen enn nr. 1 velges. Alle beregninger er deterministiske, ligger i `domene/regelmotor` og bruker ikke KI.

## Stories

- Story 4.1: Timer i perioden per kandidat
- Story 4.2: Arbeidsbelastningslinje med terskel
- Story 4.3: Forenklet kostnad per kandidat
- Story 4.4: Rangering av gyldige kandidater
- Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten
- Story 4.6: Rangeringstabellen på smalere skjermer
- Story 4.7: Ulempebelastning per kandidat

## Requirements & Constraints

- Beregninger er reproduserbare: samme input gir samme resultat, også ved likhet. KI regner aldri kostnad, arbeidstid eller rangering.
- «Perioden» for timebelastning er kalenderuken (mandag 00:00 til neste mandag 00:00, `Europe/Oslo`) som vakten starter i, uten vakten som vurderes. Ingen vakter gir 0, ikke tom. Kostnaden kan berøre begge uker ved ukeskifte. Sommertid og nattevakt over midnatt må dekkes av tester.
- Timebelastning = timer i startuken / 36. Høy belastning begynner ved minst 32,4 t (0,90 × 36) før visningsavrunding (vedtak P-04/K-02). Ingrid har 32:00 og er under grensen; 32:23 er under, 32:24 er over. 90 %-grensen er bare en visuell indikator uten rangeringspoeng, og er ikke en hard regel.
- Kostnad: individuell timelønn (fra lagringen), ordinær grense 36 t/uke, 150 % sats utover, regnet som differansen i lønnskostnad før og etter tildelingen. Vis to desimaler, «Ordinær» eller «Inkluderer overtid» og timer × sats; aldri én kr/t for en blandet vakt. Overtidssatsen regnes ut og lagres ikke. Eksempler: 32 + 8 t à 300 kr gir 3 000 kr; 36/20 t før søndag 23 til mandag 07 gir 2 550 kr.
- Ulempebelastning: poeng per time i 672 faktiske timer før vaktstart (halvåpent vindu, uten vakten selv, delvis overlapp telles delvis). Hverdag 06–18 = 0, hverdag 18–22 = 1, helg 06–22 = 2, natt 22–06 = 3; høyeste kategori vinner (natt > helg > kveld). Helligdager er vanlige ukedager. Minuttoppløsning, avrund først ved visning. Ulempescore = maks(0, 100 × (1 − poeng / tak)), tak standard 300, sendt inn som argument og ikke lest fra miljøvariabel. Ingen nye datafelt.
- Totalscore = 0,40 × kostnad + 0,20 × timebelastning + 0,15 × ulempescore + 0,25 × preferanse, hver 0–100. Kompetansenivå gir ingen poeng. Vekter og tak er navngitte rangeringsparametere i `domene/regelmotor`.
- Min–maks-normalisering; 50 faktorpoeng når alle er like. Sorter på uavrundede verdier, avrund bare til visning med én desimal. Reelt lik totalscore brytes med stigende ansatt-ID.
- Uten tolket preferanse (før epic 5, eller KI-feil/venting) gir preferansen midlertidig 50 poeng med egen status; manglende tekst merkes «Ingen registrert».
- Testscenarioer: billigste kandidat skal ikke automatisk bli nr. 1; Jonas og Mette på vakt #4127 har lik kostnad, timer og preferanse men ulik ulempe, og forskjellen er 7,0 totalpoeng (fasit fra story 1.2, ikke endret).
- Visning: inntil fem høyest rangerte kandidater og antall utelukkede per hard regel, uten ekstra handling. Null gyldige gir tomtilstanden. Ved manglende eller ugyldig turnusgrunnlag (Datafeil) vises ingen rangering eller godkjenning.
- Hver hard regel og grensetilfelle skal ha tester; 4.2 skal teste rett under, på og over terskel; 4.7 har egen testmodul `tester/regelmotor/test_ulempebelastning.py`.

## Technical Decisions

- Rene Python-beregninger under `backend/domene/regelmotor`; `domene` må ikke importere `adaptere` (import-linter-kontrakt i `tester/test_arkitektur.py`).
- Porten `RangertKandidat` i `domene/porter` konstrueres bare av regelmotoren. Den har kandidat-referanse, Kompetansenivå, kostnadstype og beløp, timebelastning (timer og prosent), ulempe (poeng, score, timer for kveld/helg/natt), rangeringsplass og eventuell `TolketPreferanse`. Feltendringer påvirker KI-forklaringen i epic 5, der hele forklaringsgrunnlaget inngår i identiteten til forhåndsgenererte avveininger.
- Tidsberegning i faktisk forløpt tid i `Europe/Oslo`, ikke antatt konstant klokketid gjennom sommertid.
- Tester mot en database i `tmp_path`; seeddata fra story 1.2 (vakthistorikk fra minst 672 t før periodestart) brukes.
- Rangeringsparametere (vekter, tak) skal justeres ett sted.

## UX & Interaction Patterns

- Rangeringstabell: rangeringsnummer (`accent`, fet, 14px), kandidat (navn + `meta`-undertekst), Kompetansenivå med tag, kostnad, timebelastning, ulempe, preferanse med tag, og en tom kolonne for ekspander-lenken fra epic 5. Annenhver rad `row-alt`. Nøkkeltall synlige uten klikk. Erstatter den alfabetiske listen fra story 2.1.
- Belastningslinje: 110×7 px, fylt proporsjonalt, `accent` under 32,4 t og `warn` fra og med 32,4 t, aldri rød. Vis nok timepresisjon til at fargeskiftet kan forstås.
- Ulempekolonne rett etter timebelastning, overskrift «Ulempe»: poeng i `body` (f.eks. «182 p»), fordeling i `meta` («kveld 16 t · helg 32 t · natt 34 t»); «0 p» uten vakter. Ingen terskel, linje eller fargeskifte, aldri `warn` eller `danger`.
- Godkjenning er egen flate med egen URL. Kandidatkortet viser kostnadsindikator, belastningslinje og ulempeindikator. Avviksnotatet «Avvik fra anbefalt rangering» (stiplet kant, valgt mot topprangert side om side) vises bare ved valg av en annen enn nr. 1, blokkerer ikke og antyder ikke feil, og inneholder «Turnushjelperen anbefaler, den bestemmer aldri selv.»
- Smale nettleservinduer (1080, 960, 680 px; mobil og nettbrett er v2): ingen vannrett sidescroll, tabellen ruller i egen beholder med rangering og navn synlig, valgt vakt, åpne begrunnelser og valgt kandidat bevares. Skjermbilder ved de tre breddene, og en enkel forståelsestest (én testperson, tre oppgaver uten hint) dokumenteres før 4.6 ferdigstilles.
- Frontendtester: komponenttester etter rolle og tekster fra `src/tekster.ts`; stubb `fetch` med `falskFetch`. Ikke kjør flere testkjøringer samtidig.

## Cross-Story Dependencies

- Anbefalt rekkefølge: 4.1 → 4.2 → 4.3 → 4.7 → 4.4 → 4.5 → 4.6.
- 4.2 og 4.3 bygger på timeberegningen i 4.1; 4.3 bruker timelønn lagret i story 1.2.
- 4.4 trenger 4.1–4.3 og ulempescoren fra 4.7, og kan ikke ferdigstilles før 4.7. 4.5 og 4.6 trenger 4.4 og 4.7.
- Bygger på epic 2 (gyldige kandidater) og epic 3 (godkjenningsflaten); story 1.2 leverer seeddata og fasit.
- Epic 5 bruker `RangertKandidat` og preferansepoengene (5.2), og forklaringene i 5.3 og 5.7 må lages etter 4.7.
