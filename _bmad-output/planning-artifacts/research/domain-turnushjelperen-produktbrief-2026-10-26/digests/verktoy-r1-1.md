# Verktøydigest: dekke én ledig vakt

Dato og accessed for alle kilder: 2026-10-26. Første runde. Research-assistenten har bare brukt oppdragsbriefen og offentlige nettkilder; ingen prosjektfiler eller andre digests er lest.

## Beslutningsrelevant funn

Det er ikke forsvarlig å beskrive kvalifikasjonsmatching, ledige vakter, rangering eller forklaring som unike funksjoner for en skoleprototype. Planday dokumenterer uttrykkelig både filtrering, rangering og korte forklaringsnoter per kandidat (K5). Quinyx dokumenterer relevanssortering og synlige opplysninger om timer, kompetanse og tilgjengelighet (K1–K2). Gat dokumenterer søknad på ledige vakter og ledergodkjenning (K7–K8).

En ærlig mulig posisjonering er derfor: «En avgrenset skoleprototype som gjør beslutningen om én ledig vakt etterprøvbar gjennom synlige vurderingsgrunnlag og dokumentert kvalitetssikring.» Dette er en anbefalt formulering av ambisjon/avgrensning, ikke et verifisert utsagn om eksisterende prototype eller et påvist konkurransefortrinn. Funksjoner og kvalitet må dokumenteres i prosjektets egne tester før de omtales som leverte. Det er ikke nødvendig å bygge flere moduler for å kunne bruke en slik beskrivelse.

## Evidens og konfidens

Alle featurefunn nedenfor er **medium**: hjelpedokumentasjon viser leverandørens dokumenterte virkemåte, men ingen produktdemo, kontotest eller uavhengig funksjonsverifisering er gjennomført. Produktmarkedsføring bekrefter kun tilbudsbeskrivelsen. Ingen effekt, markedsandel, pris eller spart tid konkluderes. «Ikke undersøkt» eller «ikke dokumentert i utvalget» betyr aldri at funksjonen mangler.

`class` skiller `leverandørdokumentasjon`, `leverandørmarkedsføring` og `tolkning/anbefaling`. Pub_date er dato på siden; oppdateringsdato oppgis særskilt. Crawl-dato er ikke publiseringsdato eller garanti for funksjonsfriskhet.

## Claims med kilder

### K1 — Quinyx: rangering og grunnlag ved tildeling

- claim: Når leder oppretter eller endrer en vakt, dokumenteres en ansattliste sortert etter relevans. Logikken bruker registrert tilgjengelighet, hjemme-/annen enhet og antall matchende ferdigheter; like kandidater sorteres alfabetisk. Listen viser også planlagte timer og tilgjengelighetssignaler. Vakten kan omfordeles ved å velge en annen ansatt. Opplysningene beskriver beslutningsstøtte, ikke dokumentert optimalitet eller en garanti om at alle viste kandidater er gyldige.
- source URL: https://help.quinyx.com/help-centre/docs/shifts
- publisher: Quinyx Help Centre
- pub_date: 2026-07-29; updated 2026-08-06
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Oppdatert for under tre måneder siden. Ingen garanti for at alle kundekontoer/konfigurasjoner følger siden.
- kort utdrag: «If employees meet the exact same criteria, they are sorted in alphabetically ascending order.»
- sted: “Assign an employee to a shift”, “What does Sorted by relevance mean?”, “Smart lists”.

### K2 — Quinyx: kompetansekrav kan utløse overstyrbart varsel

- claim: Ferdigheter kan knyttes til ansatte og vakttyper, med utløpsdato på ansattes ferdigheter. Hjelpen beskriver varsel når ansatt mangler en ferdighet som vakttypen krever, og at lederen kan velge å legge til vedkommende likevel. Varslet kan angi hvilken ferdighet som mangler. Dette bør ikke omtales som ubetinget hard eksklusjon i alle Quinyx-oppsett.
- source URL: https://help.quinyx.com/help-centre/docs/skills
- publisher: Quinyx Help Centre
- pub_date: 2026-07-29; updated 2026-08-18
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Oppdatert for under tre måneder siden.
- kort utdrag: «You can choose to add that employee anyway or select no to find another employee with the required skill type.»

### K3 — Planday: krav til ferdigheter og gyldighet

- claim: Skills beskrives som valgfri funksjon som er avslått som standard og må aktiveres via støtte; siden oppgir Pro-plan. Ved ferdighetskrav kan bare ansatte med den aktuelle ferdigheten tildeles vakten eller søke på en åpen vakt. Utløpt ferdighet hindrer tildeling til en vakt som krever den. Det viser at kvalifikasjonsfiltrering i seg selv ikke er et troverdig unikt særpreg.
- source URL: https://help.planday.com/en/articles/30445-how-to-set-up-and-use-skills
- publisher: Planday Help Center, Saad Saeed
- pub_date: ukjent; siden sier «Updated over 2 weeks ago»
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Eksakt oppdateringsdato ukjent; relativ tekst er ikke tilstrekkelig til sikkert å plassere hele innholdet innen tre måneder.
- kort utdrag: «If an Open shift has a required Skill, only employees with that Skill can request the shift.»

### K4 — Planday: åpne vakter og ledervalg

- claim: Åpne vakter opprettes uten tildelt ansatt. Ansatte som oppfyller relevante gruppe-/posisjonskrav kan søke; vakten forblir åpen til leder eller administrator godkjenner. Kvalifiserende forhold som tilgjengelighet og fravær av kolliderende vakt omtales ved pushvarsling. Leder kan velge fra søkerlisten. Siden beskriver også bytte og overlevering mellom ansatte. Dette dokumenterer en arbeidsflyt for å fylle en enkelt vakt, ikke målt effekt.
- source URL: https://help.planday.com/en/articles/30399-open-shifts-shift-requests-and-shift-swaps-for-schedule-managers
- publisher: Planday Help Center, Saad Saeed
- pub_date: ukjent; siden sier «Updated this week»
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Relativ oppdatering innen en uke; ingen eksakt dato.
- kort utdrag: «they remain open until approved by an admin or Schedule manager.»

### K5 — Planday: rangering MED forklaringsnote

- claim: Intelligent shift assignment dokumenteres for Plus/Pro. Kandidater filtreres på avdeling, gruppe og ferdigheter; sorteringsvalg omfatter enkel prioritet, regelbasert matching og Smart Recommendations. Regelbasert matching omtaler tilgjengelighet, kontraktstimer, arbeidstidsregler, ferdigheter og godkjent fravær. Smart Recommendations beskrives som læring fra planleggingsmønstre, regler og preferanser. Hver ansatt har en kort note som forklarer anbefalingen. Leder velger endelig tildeling. Siden er ikke bevis for friteksttolkning av ansattønsker eller generativ sammenligning av kandidatpar.
- source URL: https://help.planday.com/en/articles/572390-how-planday-suggests-employees-for-shifts
- publisher: Planday Help Center, Vanessa H
- pub_date: 2026-07-22; ingen nyere oppdateringsdato vist
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Litt eldre enn tre måneder. Må kontrolleres på nytt før en kritisk påstand om nåværende konkurranseforskjell.
- kort utdrag: «Each employee includes a short note to explain the recommendation»
- dokumentasjonsforbehold: Teksten sier både at bare eksplisitt tilgjengelige ansatte vises og omtaler utilgjengelighet som varselstatus. Ingen praktisk kontotest avgjør hvordan disse avsnittene henger sammen.

### K6 — Planday: lønnskostnad i planen, ikke dokumentert kostnadsrangering

- claim: Planvisningen kan vise lønnskostnader, med filtre per ansatt eller vakttype. Åpne vakters kostnader kan inkluderes basert på standardlønn for ansattgruppen. Siden omtaler lønnssatser, enkelte tillegg og flere eksplisitte avgrensninger. Kostnadsvisning er derfor dokumentert; denne siden dokumenterer ikke rangering av erstatningskandidater etter marginalkostnad eller komplett norsk tariffberegning.
- source URL: https://help.planday.com/en/articles/79054-payroll-costs-in-the-schedule-faqs-and-troubleshooting
- publisher: Planday Help Center, Maud
- pub_date: 2026-08-21
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Datert innen tre måneder.
- kort utdrag: «These costs are based on the Employee groups' default wages.»

### K7 — Gat: navn, tilbudsbeskrivelse og tilgjengelighet

- claim: Produktet presenteres fremdeles offentlig som Gat på en side med Visma Enterprise AS som avsender og Visma Group-lenke. MinGat omtales som portal der ansatte kan søke ledige vakter; GatGo beskrives med registrering av egen tilgjengelighetsstatus og vaktsøknad. Siden markedsfører også kostnadskontroll og Optur Plus som planlegging med ansattinnspill. Dette identifiserer offentlig produkt-/leverandørnavn, men er ingen separat undersøkelse av juridisk eierskap eller alle moduler.
- source URL: https://gatressurs.no/
- publisher: Visma Enterprise AS
- pub_date: ukjent; copyright 2026 er ikke publiseringsdato
- accessed: 2026-10-26
- confidence: medium
- class: leverandørmarkedsføring
- funksjonsfriskhet: Ukjent. Tilgjengelig side kontrollert i denne runden.
- kort utdrag: «Her kan den ansatte også søke på ledige vakter»
- kildekritikk: Sidens spørsmål/svar er merket som KI-generert; funnene her bygger på hovedtekst og avsenderfelt, ikke den genererte FAQ-en. Kostnadspåstandens mekanikk er ikke verifisert i hjelpedokumentasjon.

### K8 — Gat/MinGat: JaTakk og kollisjonssperre

- claim: Offentlig tilgjengelig MinGat-hjelp v2025.1 beskriver at ansatte kan velge ledige/vakante vakter og sende JaTakk til leder, som godkjenner eller avviser. Det kan ikke registreres JaTakk på en vakt som overlapper en allerede registrert/planlagt vakt. Ansatt kan legge inn kommentar og ønske om avspasering. Dette underbygger søknadsflyten i K7, men sier ikke hvilke regler eller hvilken kandidatrangering lederens Gat-installasjon bruker.
- source URL: https://mingat.v-man.no/fer/help/jatakk.html
- publisher: MinGat Hjelp; leverandørdokumentasjon på offentlig installasjonsdomene, ikke uavhengig produkttest
- pub_date: ukjent; versjon v2025.1
- accessed: 2026-10-26
- confidence: medium
- class: leverandørdokumentasjon
- funksjonsfriskhet: Eldre versjon; nåværende funksjonsfriskhet ukjent. Ikke tilstrekkelig som fersk sammenligning alene.
- kort utdrag: «Det vil ikke være mulig å registrere JaTakk på en vakt som overlapper med en allerede registrert/planlagt vakt.»

## Sammenligning innen det undersøkte utvalget

| Tema | Gat | Quinyx | Planday |
|---|---|---|---|
| Én vakt | Søknad/godkjenning, K7–K8 | Tildeling/omfordeling, K1 | Åpen vakt/søknad/ledervalg, K4 |
| Kvalifikasjoner | Ikke verifisert i de to leste Gat-kildene | Ferdighetskrav og overstyrbart varsel, K2 | Skills-krav med tildelingsbegrensning, K3 |
| Ansattønsker | Tilgjengelighetsstatus og kommentar, K7–K8 | Registrert tilgjengelighet, K1 | Vaktønske, tilgjengelighet og anbefalingspreferanser, K4–K5 |
| Kostnad | Overordnet tilbudsbeskrivelse, K7 | Ikke undersøkt tilstrekkelig | Planlagt lønnskostnad, K6 |
| Rangering | Ikke avklart i leste kilder | Relevanssortering, K1 | Flere sorteringsmåter, K5 |
| Forklaring | Ikke avklart i leste kilder | Synlige kompetanse-/tilgjengelighetsgrunnlag, K1–K2 | Kort forklaringsnote per kandidat, K5 |

Denne tabellen er ikke en full funksjonsmatrise. Forskjell mellom et varsel og en sperre er spesifikt beskrevet for K2/K3, men kan ikke generaliseres til hele produktene eller alle konfigurasjoner.

## Hva offentlig dokumentasjon her ikke avgjør

- Om generative språkmodeller brukes til forklaringene, om fritekst fra ansatte tolkes, eller om kandidatavveininger forklares med sporbar kobling til beregnet kostnad.
- Om anbefalingene er korrekte, rettferdige eller forståelige for norske turnusansvarlige i praksis.
- Dekning av norsk arbeidsmiljølov, tariffavtaler og lokale unntak; dette krever særskilt dokumentasjon og oppsett/tester.
- Om synlige statuser er fullstendig konsistente med rangering eller hvilke regler som kan overstyres i en bestemt konto.
- Hvilke funksjoner som er tilgjengelige i norske abonnementer/kundekonfigurasjoner akkurat nå. Planangivelser er leverandørens sideopplysninger, ingen pristest.
- Verktøyenes utbredelse, brukerpreferanser, tidsbesparelse, totalpris eller skoleprototypens praktiske merverdi. Ingen av disse spørsmålene er besvart.

## Leads ved eventuell andre runde

1. Behandle Plandays forklaringsfunksjon som konkret moteksempel til en unikhetsclaim. Finn ferskere produktoppdatering eller uavhengig faktisk brukertest av funksjonen; datert side er fire dager utenfor tremånedersvinduet.
2. Quinyx “Auto Assign”, “Availability” og “Open shifts”: sjekk konkret én-vakt-arbeidsflyt, kostnadsprioritering og eventuell generativ forklaring. Søket ga leads, men disse ble ikke åpnet som selvstendige kilder og er ikke brukt som dokumentert featureevidens.
3. Gat: oppdatert leder-/vaktbokdokumentasjon for kandidatutvalg og kostnads-/kompetansevisning, samt versjonsrelevans hos faktisk bruker. Offentlig eldre MinGat-hjelp kan ikke avgjøre dette.
4. Dersom særpreg skal beskrives som bedre forståelighet eller etterprøvbarhet: en avgrenset brukeroppgave med dokumenterte vurderingskriterier kan teste prosjektets egen løsning. Det gir ikke automatisk sammenligningsbelegg mot kommersielle produkter.

## Dekning og stoppgrunn

Tre leverandører; åtte unike kilder åpnet og undersøkt, hvorav sju hjelpedokumenter og én produktside. Seks webkall (tre søk, to batchåpninger, ett søk i åpnet side). Søkeresultat-snutter utover de åtte er bare brukt til å velge kilder/leads, ikke som selvstendige bevis i claims. Ingen uavhengig verifikasjon av differensieringsrelevante features ble oppnådd innen kildegrensen; derfor medium konfidens. Stoppet ved avtalt åtte-kildersgrense fordi nok dokumentasjon er funnet til å avvise ubetingede unikhetspåstander, mens videre konkurransedetaljer ikke er nødvendige for å anbefale en ærlig, smal prosjektbeskrivelse.
