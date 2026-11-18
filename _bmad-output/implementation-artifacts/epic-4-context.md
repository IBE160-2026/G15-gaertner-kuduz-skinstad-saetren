# Epic 4 Context: Rangering etter kostnad, arbeidsbelastning og ansattpreferanser

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Når de gyldige kandidatene for en vakt er kjent (Epic 2), rangeres de slik at
turnusansvarlig ser hvem som passer best uten å sammenligne alle manuelt. Hver gyldig
kandidat får en deterministisk poengsum uten KI, bygget av kostnad, arbeidsbelastning og
ansattpreferanse. Arbeidsbelastningen vises i to deler hver for seg: timebelastning
(eksisterende timer mot en ukentlig terskel) og ulempebelastning (ubekvem arbeidstid de
foregående fire ukene). Kandidatlisten viser kompetanse, kostnad, timebelastning,
ulempebelastning og preferanse per kandidat; en godkjenningsflate viser et nøytralt
avviksnotat når valgt kandidat ikke er den topprangerte. Alle beregninger ligger i
domenekjernen, uavhengig av KI.

## Stories

- Story 4.1: Timer i perioden per kandidat
- Story 4.2: Arbeidsbelastningslinje med terskel
- Story 4.3: Forenklet kostnad per kandidat
- Story 4.7: Ulempebelastning per kandidat
- Story 4.4: Rangering av gyldige kandidater
- Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten
- Story 4.6: Rangeringstabellen på smalere skjermer

Anbefalt byggerekkefølge: 4.1 → 4.2 → 4.3 → 4.7 → 4.4 → 4.5 → 4.6. Story 4.7 er med vilje
nummerert utenfor rekkefølgen, for å unngå omnummerering av allerede sporede
story-/sprint-nøkler.

## Requirements & Constraints

- **Kostnadsmodell:** hver ansatt har en individuell timelønn (bare testdata, ingen nye
  lagringsfelt i dette epicet). Ordinær ukentlig terskel er 36 timer; timer utover det i
  en kalenderuke koster 150 %. Vaktkostnad = forskjellen i modellert lønnskostnad før og
  etter tildelingen, summert over hver kalenderuke vakten berører (håndterer ukeskifte og
  sommertidsskifte via faktisk forløpt tid i `Europe/Oslo`). Vises med to desimaler,
  merket «Ordinær» eller «Inkluderer overtid»; ingen enkelt kr/t-tall skal vises som satsen
  for en blandet vakt.
- **Terskel for timebelastning:** eksisterende timer i kalenderuken vakten starter i (uten
  vakten som vurderes), delt på 36. Den visuelle «høy belastning»-indikatoren bytter ved
  minst 32,4 timer (32t24m) før visningsavrunding — en kandidat på nøyaktig 32 t er
  fortsatt under terskelen. Dette er bare kosmetisk og påvirker aldri rangeringspoengene.
- **Ulempemodell:** hver arbeidstime i de 672 faktiske timene før vaktens start (halvåpent
  intervall, uten selve vakten) gir ulempepoeng etter tidspunkt — hverdag 06–18: 0, hverdag
  18–22: 1, helg (lørdag 00:00–søndag 24:00) 06–22: 2, natt 22–06 alle dager: 3. Hver time
  telles én gang, i høyeste kategori (natt > helg > kveld > dag); fordelingen som vises
  (kveld/helg/natt) må summere (×1/×2/×3) til samme total. Tiden måles som faktiske
  forløpte minutter i `Europe/Oslo` over sommertidsskifte; poengene avrundes først ved
  visning. Helligdager telles som vanlige hverdager (v1-vedtak). En kandidat uten vakter i
  måleperioden viser «0 p» og en ulempescore på 100, ikke en tom verdi. Ulempescore =
  maks(0, 100 × (1 − ulempepoeng / tak)); standardtaket er 300 poeng, gitt som en
  parameter (ikke en miljøvariabel) slik at det kan justeres og varieres i tester. Lik
  poengsum gir alltid lik ulempescore.
- **Rangeringsvekter:** kostnad 40 %, timebelastning 20 %, ulempebelastning 15 %,
  ansattpreferanse 25 % (vektene er navngitte parametere i regelmotoren, ikke hardkodet).
  Kostnad og timebelastning bruker en skala relativ til de andre gyldige kandidatene for
  denne vakten (lavest = 100, høyest = 0, lineært imellom; er alle like, får alle 50).
  Ulempe bruker den faste ulempescore-skalaen over, uavhengig av andre kandidater.
  Preferanse gir midlertidig 50 poeng (med egen venting-/feilstatus) til KI-tolkningen fra
  Epic 5 er koblet inn; manglende preferansetekst merkes «Ingen registrert» i stedet for
  et uriktig nøytralt valg. Kompetanse er bare en hard regel (Epic 2) og gir aldri
  rangeringspoeng — kandidater som bare skiller seg på kompetanse over minstekravet, får
  identisk poengsum.
- Rangeringen skal være fullt reproduserbar: samme input → samme rekkefølge, hver gang,
  inkludert likhetsbryting. Poeng og totaler beregnes og sorteres uavrundet; viste
  poengsummer avrundes bare til én desimal, så like viste poengsummer garanterer ikke like
  underliggende totaler. Likhet i uavrundet totalscore brytes av stigende ansatt-ID — men
  siden kostnad brukes som `float` (ikke `Decimal`) i dette epicet, kan nær-like totaler
  skille seg i et siste siffer og ikke utløse den likhetsbrytingen; storyens spesifikasjon
  må definere hvordan likhet i totalen faktisk fastslås gitt dette.
- Minst ett testscenario må vise at den billigste gyldige kandidaten *ikke* rangeres øverst
  (myke faktorer kan veie tyngre enn kostnad), og ett må vise to kandidater som er
  identiske på kostnad, timebelastning og preferanse, men skiller seg bare på
  ulempebelastning, der ulempeforskjellen alene forklarer et dokumentert gap i totalscore.
- Når kandidatvurderingen er ferdig, vises inntil de fem høyest rangerte gyldige
  kandidatene pluss et antall utelukket per hard regel, uten ytterligere brukerhandling;
  null gyldige kandidater gir den eksisterende tomtilstanden; en datafeil blokkerer all
  visning av rangering eller godkjenning.
- Alt i dette epicet er deterministisk domenekjernelogikk uten KI-involvering, og skal
  være like reproduserbart som de allerede etablerte garantiene for de harde reglene
  (Epic 2).

## Technical Decisions

- All beregning av kostnad, timebelastning, ulempebelastning og rangering ligger bare i
  `domene/regelmotor`, som domene-/adaptergrensen forbyr å importere noen `adaptere/*`-
  pakke — håndhevet mekanisk av en import-linter-kontrakt dekket av tester.
- Rangeringens resultat er en `RangertKandidat`-verdi som bare produseres av
  `domene/regelmotor`, eksponert gjennom en port i `domene/porter`. Den må som et minimum
  bære: kandidatreferanse, kompetansenivå, kostnadstype og -beløp, timebelastning (timer
  og prosent av terskel), ulempebelastning (ulempepoeng, ulempescore og timer fordelt på
  kveld/helg/natt), rangeringsplass og en valgfri tolket preferanseverdi. Denne typen er
  også grunnlaget senere stories i Epic 5 bygger sine KI-forklaringer fra, så formen her
  avgrenser hva som er tilgjengelig nedstrøms.
- En kandidat utelukket av en hard regel skal aldri kunne opptre i rangeringen.

## UX & Interaction Patterns

- Kandidattabellens kolonner: rangeringsnummer (fet, accent-farge), kandidat (navn +
  metatekst under), kompetanse (med tag), kostnad, timebelastning (tall + 110×7px linje),
  ulempe (poeng i brødtekst, f.eks. «182 p», med fordeling i metatekst, f.eks. «kveld 16 t
  · helg 32 t · natt 34 t»), preferanse (med tag), og en tom kolonne reservert for Epic 5s
  utvidelseslenke. Annenhver rad bruker `row-alt`-bakgrunnen. Denne tabellen erstatter den
  enkle alfabetiske listen fra Epic 2.
- Timebelastningslinjen fylles med `accent`-farge under 32,4 t, bytter til `warn` (aldri en
  danger-/rødfarge) ved minst 32,4 t før avrunding. Ulempekolonnen har ingen terskel, linje
  eller fargeskifte i det hele tatt — 90 %-signalet gjelder bare timebelastningen.
- Godkjenningsflatens kandidatkort viser navn, kompetanse, kostnadsindikator,
  timebelastningslinje og ulempeindikator (poengsum + fordeling). Når valgt kandidat er
  den topprangerte, vises ikke noe avviksnotat. Ellers vises et avviksnotat med stiplet
  kant, «Avvik fra anbefalt rangering», som viser kostnad, kompetanse, timebelastning og
  ulempe side om side for valgt mot topprangert kandidat, inkluderer linjen
  «Turnushjelperen anbefaler, den bestemmer aldri selv», og blokkerer aldri godkjenningen
  eller antyder at valget er feil.
  - Story 4.5 er implementert 2026-11-17: `godkjenningsgrunnlag()` svarer med en fullt
    rangert kandidat og et nytt `topprangert`-felt, bygget fra samme rangering og
    #4127-fasit som kandidatlisten (AV-07) — en direkte lagret tolkning kan endre
    topplasseringen uten live KI-kall (P-05) — og godkjenningsflaten viser
    `Belastningslinje`/`Ulempeindikator` (gjenbrukt fra rangeringstabellen) og
    `Avviksnotat`-komponenten over, som også dekker endret grunnlag før ny
    bekreftelse (P-09). 675 backendtester, 52 modultester og 41 komponenttester
    besto. Se [KI-loggen](../../docs/ki-logg/2026-11-17-avviksnotat.md).
    Nettleserkontroll og menneskelig gjennomgang gjenstår, så storyen er fortsatt
    `in-progress` i `sprint-status.yaml`, ikke ferdig.
- Desktop og gjeldende tilgjengelighetskrav er bindende for dette epicet. Mobil-/
  nettbrettstøtte er utsatt til v2 — den smale skjermen-storyen (4.6) gjelder bare smale
  skrivebordsvinduer (1080 px, 960 px, 680 px), ikke telefon eller nettbrett: full tabell
  på brede skjermer, ingen vannrett siderulling på sidenivå og ingen klippet/overlappende
  tekst ved de tre kontrollbreddene, vannrett rulling bare i tabellens egen beholder med
  rangering+navn alltid synlig under rullingen, og tilstand (valgt vakt, åpne begrunnelser,
  valgt kandidat) bevart ved vindusendring.

## Cross-Story Dependencies

- Story 4.7 (ulempebelastning) bygger på vakthistorikken seedet i Story 1.2 og må være
  ferdig før Story 4.4 (rangering) kan fullføres, siden 4.4 bruker ulempescoren. Story 4.5
  og 4.6 viser begge ulempeindikatoren fra 4.7 og krever at den er ferdig; 4.6 krever i
  tillegg 4.4.
- Story 4.4s `RangertKandidat`-felter påvirker Epic 5 (story 5.3 og 5.7): KI-forklaringen
  og eventuelt forhåndsgenerert demoinnhold leser denne formen, så forhåndsgenerert
  innhold som avhenger av den, må lages først etter at feltene i dette epicet er endelige.
- Story 4.4s testscenario for ulempedrevne rangeringsforskjeller avhenger av bestemte
  fiktive testdata seedet i Story 1.2.
