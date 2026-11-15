# Epic 4 Context: Rangering etter kostnad, arbeidsbelastning og ansattpreferanser

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Gi turnusansvarlig et etterprøvbart beslutningsgrunnlag for gyldige kandidater: kostnad, eksisterende arbeidstid, ubekvem arbeidstid og ansattpreferanse beregnes eller tolkes hver for seg, og kandidatene rangeres deterministisk. Nøkkeltallene skal være synlige før brukeren tar den endelige beslutningen om én vakt.

## Stories

- Story 4.1: Timer i perioden per kandidat
- Story 4.2: Arbeidsbelastningslinje med terskel
- Story 4.3: Forenklet kostnad per kandidat
- Story 4.4: Rangering av gyldige kandidater
- Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten
- Story 4.6: Rangeringstabellen på smalere skjermer
- Story 4.7: Ulempebelastning per kandidat

## Requirements & Constraints

- Bare kandidater som har passert de harde reglene, rangeres. Kompetanse er et minstekrav, ikke en poengfaktor. Beregning av kostnad, arbeidstid, ulempe og rangering skal være reproduserbar og uavhengig av KI.
- Eksisterende timebelastning gjelder kalenderuken vakten starter i, mandag 00:00 til neste mandag 00:00 i `Europe/Oslo`. Timer telles etter faktisk overlapp, også ved ukegrense og sommertid. Den vurderte vakten legges ikke til. Andel av 36 timer vises; minst 32,4 timer gir visuell høy belastning uten å endre poeng.
- Forenklet vaktkostnad er økningen i modellert lønnskostnad når vakten tildeles. Bruk individuell timelønn, ordinær sats til og med 36 timer per kalenderuke og 150 % for timer over. Fordel eksisterende og ny vakt på berørte uker etter faktisk forløpt tid. Dette er ikke full tariff- eller lønnsberegning.
- Ulempebelastning gjelder de 672 faktisk forløpte timene før vaktstart, som halvåpent intervall; klipp historiske vakter ved grensen og utelat den vurderte vakten. Hver arbeidstime tilordnes én høyeste kategori: hverdag 06–18 gir 0 poeng, hverdag 18–22 gir 1, helg 06–22 gir 2, natt 22–06 gir 3. Helg er lørdag og søndag; helligdager behandles som vanlige ukedager. Bruk faktisk tid i Oslo, også over sommertid, og behold minuttoppløsning uten beregningsavrunding.
- Ulempescore er `maks(0, 100 × (1 − Ulempepoeng / tak))` med fast tak 300 i v1. Den er uavhengig av hvilke andre kandidater som vurderes. Vis kveld-, helg- og nattetimer separat, med poengsummen som `kveld × 1 + helg × 2 + natt × 3`.
- Total rangering vekter kostnad 40 %, timebelastning 20 %, ulempebelastning 15 % og ansattpreferanse 25 %. Kostnad og timebelastning normaliseres mot alle gyldige kandidater; når alle er like, får alle 50 faktorpoeng. Ulempe bruker fast skala. Sorter på uavrundet totalscore, deretter stigende ansatt-ID ved eksakt likhet; avrund bare ved visning. Vis først inntil fem, med tilgang til øvrige gyldige.

## Technical Decisions

- Domenekjernen i `domene/regelmotor` utfører alle beregninger. `domene/porter` eier de typede grensesnittene; `RangertKandidat` bærer beregnede nøkkeltall og konstrueres bare av regelmotoren. Ingen modul i domenet importerer adaptere. `adaptere/api` orkestrerer, `adaptere/lagring` eier dataskjema og oversetter lagrede data til domenetyper, og frontend snakker kun med API-et.
- Tidspunkter lagres som ISO 8601 i UTC og leses med tidssone. Intervaller, overlapp og faktisk varighet sammenlignes som tidspunkter i UTC; kalendergrenser og visning følger Oslo-tid.
- Datafeil ved manglende eller ugyldig turnusgrunnlag skal stoppe kandidatvurdering og godkjenning. Den er forskjellig fra null gyldige kandidater. Endret grunnlag krever ny beregning og bekreftelse.
- Backend testes med pytest; frontendlogikk og komponentflyt testes med prosjektets eksisterende testrigg. Manuelle kontroller brukes målrettet for layout, farger, fokus og ekte backend når automatiske tester ikke dekker det.

## UX & Interaction Patterns

- Kandidatflaten er en kompakt, skannbar tabell. Hver rad viser kompetanse, samlet vaktkostnad og type, eksisterende timebelastning, ulempepoeng med fordeling, og preferanse. Ulempe står rett etter timebelastning og er ren tekst uten terskel, linje eller fargevarsel.
- Godkjenningsflaten viser samme nøkkeltall. Velger brukeren en annen enn den topprangerte, vises en nøytral sammenligning; dette hindrer ikke godkjenning. Farge for høy timebelastning og overtid er `warn`; ulempe er ingen varselstatus.
- Desktop er målplattform. Smale nettleservinduer skal bevare synlig kobling mellom kandidat og nøkkeltall ved vannrett rulling; mobil og nettbrett er utsatt til v2.

## Cross-Story Dependencies

- Vakthistorikk og faste vakttyper kommer fra story 1.2. Story 4.7 leverer Ulempescore til 4.4, og visningsdata til 4.5 og 4.6. Story 4.4 bygger også på timer fra 4.1, visning fra 4.2 og kostnad fra 4.3.
- Rangering og nøkkeltall blir faktagrunnlag for KI-forklaringer i epic 5; forklaringer og demotekst må bruke gjeldende beregnede data. KI kan tolke preferanser og formulere avveininger, men beregner ikke tallene.
