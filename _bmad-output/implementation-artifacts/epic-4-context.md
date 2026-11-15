# Epic 4 Context: Rangering etter kostnad, arbeidsbelastning og ansattpreferanser

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

De gyldige kandidatene, altså de som har passert de fire harde reglene fra epic 2, rangeres etter kostnad, arbeidsbelastning og ansattpreferanse. Da ser turnusansvarlig hvem som passer best uten å sammenligne alle manuelt. Arbeidsbelastningen består av timebelastning og ulempebelastning, som vises hver for seg. Rangeringstabellen viser nøkkeltallene direkte i raden. Et nøytralt avviksnotat vises når turnusansvarlig velger en annen enn nr. 1. Alle beregninger er deterministiske, ligger i `domene/regelmotor` og bruker ikke KI. Story 4.1, 4.2, 4.3 og 4.7 er ferdige. Neste story er 4.4, som også leverer porten `RangertKandidat` som epic 5 bygger på.

## Stories

- Story 4.1: Timer i perioden per kandidat
- Story 4.2: Arbeidsbelastningslinje med terskel
- Story 4.3: Forenklet kostnad per kandidat
- Story 4.4: Rangering av gyldige kandidater
- Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten
- Story 4.6: Rangeringstabellen på smalere skjermer
- Story 4.7: Ulempebelastning per kandidat

## Requirements & Constraints

**Faktorene (ferdige i 4.1–4.3 og 4.7)**
- Timebelastning: eksisterende timer i kalenderuken (man 00:00 til man 00:00, `Europe/Oslo`) som Vakten starter i, uten Vakten selv, delt på 36. «Høy belastning» begynner ved minst 32,4 t før visningsavrunding (P-04/K-02). Det er bare en visuell indikator og gir ingen rangeringspoeng.
- Kostnad: modellert merkostnad ved tildeling, summert over berørte uker. Grensen er 36 t per uke, med 150 % sats utover, og opprinnelig ansatt trekkes ikke fra (P-01–P-03).
- Ulempe: Ulempepoeng i de 672 faktiske timene før vaktstart (AV-09). Ulempescore = maks(0, 100 × (1 − poeng / tak)), med tak 300 (AV-11).

**Rangeringsmodellen (4.4)**
- Totalscore = 0,40 × kostnadspoeng + 0,20 × timebelastningspoeng + 0,15 × Ulempescore + 0,25 × preferansepoeng. Hver faktor gir 0–100 poeng, og listen sorteres synkende (FR9, AV-11).
- Vektene og ulempetaket er navngitte rangeringsparametere i `domene/regelmotor` og sendes inn som argumenter, slik at testene kan variere dem. De er ikke miljøvariabler, og det finnes ingen innstillingsside (AV-11).
- Kostnad og timebelastning normaliseres med min–maks over **alle** gyldige kandidater: lavest verdi gir 100, høyest gir 0, og verdiene imellom skaleres lineært. Har alle samme verdi for en faktor, får alle 50 poeng for den. Det gjelder også når bare én kandidat er gyldig (AV-05). Ulempescoren bruker fast skala og normaliseres ikke.
- Kompetansenivå gir ingen poeng. To kandidater som er like på alt unntatt kompetanse over minstekravet, får lik totalscore (FR2, FR9).
- Faktorpoeng og totalscore regnes og sorteres uavrundet. De avrundes bare ved visning, til én desimal (K-03). K-03 har ikke avtalt hvordan en verdi midt mellom to tideler avrundes. Følg eksisterende kontrakt, og ikke lag en ny produktregel.
- Ved reelt lik uavrundet totalscore sorteres kandidatene på stigende ansatt-ID (AV-05, K-03).
- Rangeringen bruker kostnaden som `float`, ikke `Decimal`. `beregn_kostnad` regner fortsatt i `Decimal` uten avrunding underveis. Vedtatt av Johannes på vegne av gruppa 2026-11-15, referatet §11.
- **Ikke vedtatt, må avgjøres i spesifikasjonen for 4.4:** hvordan likhet mellom to totalscorer sjekkes. Matematisk like totaler kan skille seg i siste siffer, for eksempel 10.714285714285714 mot 10.714285714285715, og da slår ID-regelen ikke inn.
- Preferanse: kategoriene gir 100, 75, 50, 25 eller 0 poeng. Uten `TolketPreferanse`, som gjelder hele epic 4, får kandidaten midlertidig 50 poeng med egen status. Registrert tekst har vente- eller feilstatus («Preferanse venter på tolkning» / «Preferanse kunne ikke tolkes»), og manglende tekst har «Ingen registrert». Ventende eller feilet tolkning utelukker aldri kandidaten (P-05).
- Min–maks regnes før listen kuttes. Inntil fem høyest rangerte vises, sammen med antall utelukkede per hard regel, uten ekstra handling (SM-3, AV-15). Er det færre enn fem, vises alle. Turnusansvarlig kan velge «Vis alle gyldige kandidater» eller tilsvarende og velge en annen gyldig kandidat (FR9, FR12).
- Null gyldige gir tomtilstanden fra FR6 (P-11). Mangler turnusgrunnlaget eller er det ugyldig, stopper vurderingen med datafeil, uten rangering og uten godkjenning (P-08).
- Samme input gir samme rekkefølge hver gang, også ved likhet (NFR1, SM-5).

**Testscenarioer for 4.4 (AV-07, AV-12)**
- Den billigste kandidaten er ikke rangert øverst (FR9, SM-6).
- Jonas og Mette på #4127 har lik kostnad, timebelastning og preferansepoeng, men ulik ulempe (40 mot 180 p). Det gir nøyaktig 7,0 totalpoeng i forskjell.
- Fasiten for #4127 er beregnet på forhånd i story 1.2 og kontrollert etter KS-02. Med de tolkede preferansene (75/75/0/100): Jonas 85,654761…, Mette 78,654761…, Thomas 59,0, Ingrid 37,0. Med 50 poeng for alle, som gjelder før epic 5: Jonas 79,40, Mette 72,40, Thomas 71,50, Ingrid 24,50. Thomas er billigst og er ikke øverst i noen av dem.
- Paret som er likt unntatt kompetanse, og paret for story 5.2, er enhetstestdata i domenet, ikke i seeden.
- Ny eller endret fasit må kontrolleres for hånd mot formelen før den godkjennes (KS-02). Fasiten skal ikke kopieres fra programmets resultat (AV-07).

## Technical Decisions

- Heksagonal arkitektur. `domene/*` importerer aldri `adaptere/*`, og import-linter-testen håndhever det (AD-1, AD-2). Domenet kaller aldri KI. Rangeringen leser bare en lagret `TolketPreferanse` som vanlig input og gjør aldri et live KI-kall (AD-1).
- `RangertKandidat` (Pydantic) eies av `domene/porter` og konstrueres **bare** av `domene/regelmotor`. Minimumsfeltene er:
  - kandidat-ID og navn og Kompetansenivå
  - Vaktkostnad med fordeling på ordinær tid og overtid (kostnadstype og beløp)
  - Timebelastning i timer og prosent av terskelen
  - Ulempepoeng, Ulempescore og timer fordelt på kveld, helg og natt
  - rangeringsplass, preferansepoeng, tolkestatus og eventuell `TolketPreferanse`
  - Det endelige skjemaet fastsettes i 4.4/5.3 og testes.

  Sammenligningen med referansekandidaten (P-07) leveres separat i epic 5, ikke i 4.4.
- Bare gyldige kandidater deltar i Rangeringen. En utelukket kandidat kan aldri havne i `RangertKandidat` (NFR2). Den opprinnelig oppsatte ansatte er utelukket (AV-06).
- API-svar for kandidatvurderingen bruker `status`-diskriminatoren (`ok`, `ingen_gyldige_kandidater`, `datafeil` med `kode` og `datagrense`). Faktiske feil har formen `{kode, melding}`, og `melding` vises aldri i UI (AD-4).
- Godkjenningsgrunnlaget er konsistent: data som påvirker Rangeringen, må være med i grunnlagsmerket. Endret grunnlag gir ny beregning og krever ny bekreftelse (P-09, AD-5).

## UX & Interaction Patterns

- Rangeringstabellen erstatter den alfabetiske listen fra 2.1. Kolonnene er:
  - rangeringsnummer (`rank-badge`: `accent`, fet, 14px)
  - kandidat (navn med `meta`-undertekst)
  - Kompetansenivå med tag, som bare er informasjon
  - kostnad («Ordinær» / «Inkluderer overtid», to desimaler)
  - timebelastning (linje 110×7px)
  - «Ulempe» («182 p», med «kveld 16 t · helg 32 t · natt 34 t» i `meta`, uten terskel og uten farge)
  - preferanse med tag
  - en tom kolonne for ekspander-lenken fra epic 5

  Annenhver rad har `row-alt`. Nøkkeltallene er synlige uten klikk (UX-DR7–DR11, DR28).
- Taggene er nøytrale (`tag-bg`). Preferansetaggen viser kategori eller status, for eksempel «Ingen registrert» (UX-DR11).
- Tomtilstand, datafeil og lasting er tekstlig og visuelt forskjellige (UX-DR16). All brukertekst står i frontendens norske tekstliste og velges ut fra `kode`/`status`. Teksten er kort og tallbasert og antyder aldri at systemet har valgt (UX-DR23).
- Desktop er bindende. Tabellen ruller i sin egen beholder, og siden ruller aldri vannrett (UX-DR25, AV-14). Alle handlinger kan nås med tastatur, og HTML-en er semantisk (UX-DR24).

## Cross-Story Dependencies

- 4.4 bruker timene fra 4.1, kostnaden fra 4.3 og Ulempescoren fra 4.7. Seedscenarioene kommer fra 1.2 (#4127, #4189, #4261–#4265).
- 4.5 bruker topprangert kandidat og nøkkeltallene fra 4.4 i avviksnotatet (UX-DR18). 4.6 bruker tabellen fra 4.4 med ulempekolonnen (AV-17).
- P-13s forståelsestest gjøres etter at kandidatvisningen fungerer (4.4) og før 4.6 er ferdig.
- Epic 5: 5.1/5.2 sender lagrede `TolketPreferanse` inn i regelmotoren og erstatter midlertidig 50. En ny tolkning må endre grunnlagsmerket (P-05, P-09). 5.3 forklarer `RangertKandidat`. Hele `RangertKandidat` inngår i identiteten til forhåndsgenererte Avveininger i demo-modus (5.7, AD-6), så endres feltene, må de genereres på nytt.
