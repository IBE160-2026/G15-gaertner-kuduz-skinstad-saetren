# Epic 4 Context: Rangering etter kostnad, arbeidsbelastning og ansattpreferanser

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

De gyldige kandidatene rangeres, slik at turnusansvarlig ser hvem som passer best uten å sammenligne alle manuelt. Rangeringen bygger på kostnad, arbeidsbelastning (timebelastning og ulempebelastning, vist hver for seg) og ansattpreferanse. Tabellen viser nøkkeltallene direkte i raden, og et nøytralt avviksnotat vises når hun velger en annen enn nr. 1. Alt regnes deterministisk i domenekjernen, uten KI. Epicet erstatter den alfabetiske listen fra Epic 2 og gir Epic 5 sitt faktagrunnlag (`RangertKandidat`). Ingen story i epicet er startet (backlog).

## Stories

- Story 4.1: Timer i perioden per kandidat
- Story 4.2: Arbeidsbelastningslinje med terskel
- Story 4.3: Forenklet kostnad per kandidat
- Story 4.4: Rangering av gyldige kandidater
- Story 4.5: Avviksnotat og nøkkeltall på godkjenningsflaten
- Story 4.6: Rangeringstabellen på smalere skjermer
- Story 4.7: Ulempebelastning per kandidat

## Requirements & Constraints

- **KI-grense (absolutt):** kostnad, timer, ulempe og rangering regnes aldri av KI. Samme fullstendige beslutningsgrunnlag (Kandidat, Vakt, øvrig Turnus, timelønn, historikk) gir samme resultat hver gang, uten klokke eller tilfeldighet. Bare Gyldige kandidater rangeres.
- **Timebelastning (P-02, P-04):** eksisterende timer i kalenderuken Vakten starter i (mandag 00:00 til mandag 00:00, `Europe/Oslo`), uten Vakten som vurderes, delt på 36 t. Vakter fra forrige uke og over sommertid fordeles etter faktisk overlapp. Vakt som slutter nøyaktig mandag 00:00 gir 0 t i neste uke. Ingen Vakter gir 0, ikke tom. «Høy belastning» ved minst 32,4 t (32:24) før visningsavrunding, 32:23 er under, og Ingrid (32 t) er under. Dette er bare en visuell indikator og gir ingen poeng. Visningen må ha nok presisjon til at fargeskiftet kan forstås.
- **Kostnad (P-01, P-02, P-03):** individuell timelønn fra seeden. Timer til og med 36 per kalenderuke er ordinære, utover er 150 %. Vaktkostnad er forskjellen i modellert kostnad før og etter tildelingen, summert over begge berørte uker ved ukeskifte. Opprinnelig ansatts lønn trekkes ikke fra. Overtidssatsen regnes ut og lagres ikke. Visning: to desimaler, «Ordinær» eller «Inkluderer overtid», og timer × sats i detaljer. En blandet Vakt får aldri én kr/t. Regneeksempler: 32 + 8 t ved 300 kr/t er 3 000 kr, 40 + 8 t er 3 600 kr, og søndag 23–mandag 07 med 36/20 t før er 2 550 kr.
- **Ulempebelastning (FR-14, AV-09, AV-11):** poeng per arbeidstime: hverdag 06–18 gir 0, hverdag 18–22 gir 1, helg 06–22 gir 2, natt 22–06 alle dager gir 3. Hver time telles én gang i høyeste kategori (natt > helg > kveld > dag), slik at kveld×1 + helg×2 + natt×3 = poengene. Måleperioden er 672 faktiske timer, `[start − 672 t, start)`, uten Vakten selv, og delvis overlappende vakter telles for den delen som ligger innenfor. Minuttoppløsning, avrunding først ved visning, helligdager som vanlige dager. Ulempescore = maks(0, 100 × (1 − poeng / tak)), tak 300 som argument og ikke miljøvariabel. Ingen Vakter gir «0 p» og score 100. Ingen terskel, linje eller fargeskifte.
- **Poengmodell (AV-05, K-03):** totalscore = 0,40 × kostnad + 0,20 × timebelastning + 0,15 × ulempescore + 0,25 × preferanse, hver 0–100. Kostnad og timebelastning min–maks over alle Gyldige kandidater (lavest = 100), og alle får 50 når verdiene er identiske, også ved én kandidat. Ulempe har fast skala. Preferanse har fem nivåer (100/75/50/25/0). Kompetanse gir ingen poeng, bare hard regel. Alt beregnes og sorteres uavrundet, og vises med én desimal. Lik uavrundet totalscore gir stigende ansatt-ID. Vektene og taket er navngitte parametere i `domene/regelmotor`.
- **Preferanse før Epic 5 (P-05):** uten `TolketPreferanse` gir faktoren midlertidig 50 poeng, med egen vente-/feilstatus for registrert tekst og «Ingen registrert» når tekst mangler.
- **Visning (SM-3, AV-15):** når beregningen er ferdig vises inntil fem høyest rangerte, mens min–maks regnes over alle Gyldige først, og antall utelukkede per regel. Null gyldige gir tomtilstanden fra Epic 2, og datafeil gir verken rangering eller Godkjenning (P-08).
- **Fasit for #4127 (AV-07, AV-12, KS-02 utført):** Jonas 85,654761… (2 960 kr), Mette 78,654761… (2 960 kr), Thomas 59,0 (2 800 kr), Ingrid 37,0 (3 850 kr, 4 t overtid). Jonas og Mette har like kostnads-, timer- og preferansepoeng, og forskjellen på 7,0 totalpoeng kommer bare fra ulempe (ulempepoeng 40 mot 180, ulempescore 86,67 mot 40,00). Billigste Kandidat (Thomas) skal ikke stå øverst. Med nøytral preferanse for alle: Jonas 79,40, Mette 72,40, Thomas 71,50, Ingrid 24,50. Fasiten er regnet på forhånd og tilpasses aldri koden. Ulempeeksempel: 182 p = kveld 16 t · helg 32 t · natt 34 t.
- **Tester:** ulempe har egen testmodul `tester/regelmotor/test_ulempebelastning.py` (grensene 05:59/06:00, 17:59/18:00, 21:59/22:00, natt over helg og sommertid, vindusgrensen, poeng lik og over taket, annet tak enn 300, gjentatt kjøring). Timer, linje og kostnad dekker ukeskifte, nøyaktig 36 t og begge sommertidsskifter. Grense 32:23/32:24 for linjen.
- **Dokumentasjon:** KI-generert kode logges i `docs/ki-logg/`. Grensesnittet er bare på norsk bokmål.

**Åpne punkter (ikke fyll med antakelser):** (1) endelig skjema for `RangertKandidat` fastsettes i 4.4/5.3. (2) KS-03, kontroll av tidskategorier for alle fire vakttyper, er vedtatt men ikke utført og bør gjøres før 4.7 ferdigstilles. (3) Taket på 300 bygger på regneeksempler (`scripts/ulempe_regneeksempler.py`), ikke en kilde. (4) Eksakt avrunding midt mellom to tideler er ikke avtalt, så følg eksisterende kontrakt og ikke innfør en egen regel. (5) Tidsberegningen i 4.1 og 4.3 må tolkes mot P-02 og ikke tittelen «timer i perioden». (6) Eksakt ventetilstand mens rangeringen beregnes er `[ASSUMPTION]` i UX.

## Technical Decisions

- Beregningene ligger i `domene/regelmotor` som ren Python uten database, nett eller klokke. `RangertKandidat` ligger i `domene/porter`, og bare regelmotoren konstruerer den (AD-1, AD-2). Import-linter-kontrakten dekker nye moduler. Konvertering fra SQLAlchemy skjer i `adaptere/lagring`, og `adaptere/api` komponerer.
- `RangertKandidat` bærer minst kandidat-referanse, Kompetansenivå, kostnadstype og beløp (ordinær/overtid), timebelastning (timer og prosent av terskel), ulempe (poeng, score og timer for kveld, helg og natt), rangeringsplass og eventuell `TolketPreferanse`. Referansesammenligning for Epic 5 (nr. 1 mot nr. 2, øvrige mot nr. 1) leveres separat.
- Tid regnes som faktisk forløpt tid (UTC) i `Europe/Oslo`, ikke etter veggklokka, og alle tidspunkt er tidssonebevisste. Kalenderuke-hjelperne `berørte_uker` og ukestart i `domene/regelmotor/trettifem_timer.py` kan gjenbrukes til timebelastning og kostnad (167/169 t-uker ved sommertid).
- Nye regler og beregninger må ikke bryte datafeil-stoppen (P-08): ugyldig eller manglende grunnlag gir `status: "datafeil"`, aldri en rangering. Kandidatene kan trenge flere vakter enn de bærer i dag, siden `Kandidat` har id, navn, kompetanse og vakter etter Epic 2. Ulempe trenger vakter 672 t bakover. Historikken starter ved `periode_start − 672 t`, og seeden har den (story 1.2).
- API-kontrakt (AD-4): 200-svar med `status` (`ok`, `ingen_gyldige_kandidater`, `datafeil`) og feilform `{kode, melding}`. Frontend viser tekst fra egen tekstliste, aldri `melding`. Tidspunkt som ISO 8601 med offset. Utvidelse av kandidatsvaret med nøkkeltall må beholde skillet mellom statusene.
- Forhåndsgenererte Avveininger (AD-6) lages først etter at 4.7 og `RangertKandidat` er ferdige, fordi hele grunnlaget inngår i identiteten.
- Frontend følger AV-13 (designtokens, ingen rå størrelser eller farger i komponentene) og AV-14 (`max-width: 1180px`). Komponenttestene finner elementer etter rolle og tekster i `src/tekster.ts`, og nye flyter trenger egne tester (OP-16).

## UX & Interaction Patterns

- **Rangeringstabell (UX-DR7, DR8):** kolonnene er rangeringsnummer, kandidat (navn og `meta`-undertekst), Kompetansenivå med tag, kostnad, timebelastning, ulempe, preferanse med tag og en tom kolonne for ekspander-lenken fra Epic 5. Én rad per Gyldig kandidat, `row-alt` på annenhver rad, og nøkkeltallene synlige uten klikk. Rangeringsnummeret er `accent`, fet og 14px. Kompetansenivå er informasjon og påvirker ikke rekkefølgen. Ekskludert-boksen og tomtilstanden fra Epic 2 beholdes.
- **Arbeidsbelastningslinje (UX-DR9):** 110×7px, fylt proporsjonalt, `accent` under 32,4 t og `warn` ved og over. Aldri rød. Viser bare timebelastning.
- **Kostnadsindikator (UX-DR10):** «Ordinær» i `ok`, «Inkluderer overtid» i `warn`, og timer × sats i detaljer.
- **Ulempeindikator (UX-DR28):** kolonne rett etter timebelastning med overskriften «Ulempe». Poengsummen står i `body` («182 p») og fordelingen i `meta` («kveld 16 t · helg 32 t · natt 34 t»). Bruker aldri `warn` eller `danger`. Brukes også på kandidatkortet på Godkjenning og i avviksnotatet.
- **Kandidatkort (UX-DR17):** navn (`heading`), Kompetansenivå, kostnadsindikator, arbeidsbelastningslinje og ulempeindikator. Forklaringspanelet kommer i Epic 5.
- **Avviksnotat (UX-DR18, DR23):** vises bare når valgt ≠ topprangert. Stiplet kant, tittel «Avvik fra anbefalt rangering», teksten «Turnushjelperen anbefaler, den bestemmer aldri selv.» og kostnad, Kompetansenivå, timebelastning og ulempe side om side. Notatet blokkerer ikke godkjenningen og antyder aldri at valget er feil.
- **Smale vinduer (UX-DR24, DR25, AV-17):** mobil og nettbrett er v2. Ved 1080, 960 og 680 px ruller siden aldri vannrett, og ingenting klippes. Brede tabeller ruller i egen beholder, og rangering og navn må være synlige hele tiden, også i ulempekolonnen. Hvordan det løses (fast første kolonne eller opplysninger flyttet inn i raden) avgjøres i 4.6. Valgt vakt, åpne begrunnelser og valgt Kandidat beholdes ved endret bredde. Skjermbilder ved de tre breddene lenkes fra vurderingsmatrisen. Alt kan nås med tab og enter.
- **P-13:** den oppgavebaserte forståelsestesten (nr. 1, annen gyldig kandidat, datafeil mot null gyldige) er et planlagt arbeidsmål før 4.6 ferdigstilles. Én testperson, ett operativsystem og én skjermflate holder, og akseptmålet er alle tre uten hint. Funn og rettinger dokumenteres.

## Cross-Story Dependencies

- Anbefalt rekkefølge: 4.1 → 4.2 → 4.3 → 4.7 → 4.4 → 4.5 → 4.6. Nummeret 4.7 er beholdt for å unngå omnummerering av nøklene i `sprint-status.yaml`.
- 4.4 bruker timer (4.1/4.2), kostnad (4.3) og ulempescore (4.7), og kan ikke ferdigstilles før 4.7. Scenarioet for ulempe krever seeddata fra story 1.2. 4.5 og 4.6 krever 4.4 og 4.7.
- 4.1 bør avklare visningsformat for timer (presisjon som `32:23`, t:mm, siden 4.2 trenger det), hvor tallet legges (midlertidig felt på kandidatsvaret eller begynnelsen av `RangertKandidat`) og at kandidatflaten får kolonner. Det overlapper med tabellen i 4.4/4.6.
- Bygger på Epic 2: filtrerte Gyldige kandidater, `UtelukkelsesOppsummering`, ukehjelperne, datafeil-stoppen og `Kandidatflate.tsx`. Listen er i dag alfabetisk, og 4.4 erstatter den.
- Epic 3: Story 3.1 la godkjenningsflaten, og 3.2 (godkjenning og bemanning) pågikk 2026-11-15 i en egen branch. Både 3.2 og 4.x endrer trolig `backend/adaptere/api/main.py` og `frontend/src/komponenter/Kandidatflate.tsx`, så avtal rekkefølge for merging. Godkjenningen kjører regelkontrollen på nytt, og P-09 (endret grunnlag og forsinkede svar) må utvides når kostnad og belastning blir en del av beslutningsgrunnlaget.
- Nedstrøms: Epic 5 leser `RangertKandidat` og referansefakta for tolkning og Avveining. Feltendringer i 4.7 påvirker 5.3 og 5.7, og ekspander-kolonnen i tabellen fylles der. Epic 5 skal virke også uten KI-svar, og rangeringen gjør aldri et live KI-kall. Lekkasjetesten i 5.6 forutsetter at utelukkede Kandidater aldri når rangeringen.
- Branch med PR anbefales for 4.1 og 4.4, siden de binder gruppa (porter, datamodell og felles oppsett). Ulempescenarioet #4127 og fasiten ovenfor er felles bevis på kvalitetssikring.
