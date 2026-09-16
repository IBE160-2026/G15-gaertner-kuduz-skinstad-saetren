---
title: "Product Brief: IBE160 Turnusprosjekt"
status: draft
created: 2026-09-15
updated: 2026-09-16
---

# Product Brief: IBE160 Turnusprosjekt

## Sammendrag

Endringer i en eksisterende turnus kan være tidkrevende å håndtere. Når en planlagt vakt plutselig må dekkes av en annen ansatt, må den turnusansvarlige finne personer som både er tilgjengelige og kvalifiserte, samtidig som definerte krav til arbeidstid og hviletid må overholdes. Blant de ansatte som faktisk kan ta vakten, kan det i tillegg være forskjeller i kostnad, arbeidsbelastning og individuelle ønsker.

Prosjektet skal utvikle en prototype av en web-app som fungerer som et beslutningsstøtteverktøy og hjelper en turnusansvarlig med å finne gode alternativer når én konkret vakt i en eksisterende turnus må endres. Løsningen skal ikke lage en komplett turnus fra bunnen av. Den skal filtrere bort kandidater som ikke oppfyller nødvendige krav, rangere gyldige kandidater etter et begrenset sett kriterier og presentere et forståelig beslutningsgrunnlag.

Generativ KI gjør det mulig å kombinere kontrollerbar, regelbasert programmering med støtte for mer ustrukturerte og menneskelige hensyn. I denne løsningen skal faste regler avgjøre hva som er lovlig og mulig, mens KI brukes til å tolke og forklare mykere forhold, som ansattpreferanser og avveininger mellom aktuelle kandidater. KI skal ikke kunne overstyre absolutte regler eller gjennomføre endringer på egen hånd. Den endelige beslutningen tas alltid av brukeren.

## Problemet

Når en ansatt ikke kan gjennomføre en planlagt vakt, må den turnusansvarlige finne en egnet erstatter. Det krever ofte flere vurderinger samtidig:

- Hvem er tilgjengelig?
- Hvem har nødvendig kompetanse?
- Oppfyller kandidaten definerte krav til arbeidstid og hviletid?
- Hvor mye har personen allerede arbeidet?
- Vil vakten medføre overtid eller andre ekstra kostnader?
- Har den ansatte registrerte ønsker eller begrensninger som bør tas hensyn til?

I mange virksomheter håndteres slike situasjoner ved at den ansvarlige manuelt går gjennom turnusplaner, arbeidslister og informasjon om ansatte, og eventuelt kontakter aktuelle personer. En del av vurderingen kan også være basert på den turnusansvarliges egen kjennskap til medarbeiderne.

Denne arbeidsformen kan være tidkrevende og gjør det vanskelig å vurdere alle aktuelle kandidater på en lik og systematisk måte. Gode alternativer kan bli oversett, enkelte ansatte kan få en uforholdsmessig stor belastning, og virksomheten kan pådra seg unødvendige kostnader gjennom for eksempel overtid.

Prosjektets overordnede problemstilling er derfor:

> Hvordan kan regelbasert programmering og kunstig intelligens brukes sammen for å hjelpe en turnusansvarlig med å finne en egnet erstatter når én eksisterende vakt må endres?

## Løsningen

Brukeren tar utgangspunkt i en eksisterende turnus og velger vakten som må bemannes på nytt, i en web-app.

Løsningen identifiserer først hvilke ansatte som faktisk kan vurderes. Kandidater som ikke oppfyller definerte absolutte krav, blir utelukket. Deretter sammenlignes de gjenværende kandidatene ut fra et begrenset antall relevante hensyn, blant annet arbeidsbelastning, kostnad og ansattpreferanser.

Brukeren får presentert en rangert liste over de mest aktuelle kandidatene. For hvert alternativ skal systemet vise:

- hvorfor kandidaten kan ta vakten
- hvilke forhold som trekker opp
- hvilke forhold som trekker ned
- en enkel kostnadsvurdering
- eventuelle relevante ansattpreferanser

KI skal brukes til å tolke myke, tekstbaserte preferanser og til å forklare avveiningene mellom gyldige kandidater på en forståelig måte. Beregning av harde regler, arbeidstid og kostnad skal ikke overlates til KI.

Systemet skal være beslutningsstøtte, ikke en automatisk beslutningstaker. Brukeren velger selv hvilken kandidat som eventuelt skal settes inn i vakten.

## Hva gjør dette annerledes

En enkel digital turnusløsning kan vise hvem som er ledig. En regelbasert løsning kan i tillegg filtrere bort ansatte som ikke oppfyller bestemte krav. Prosjektet går ett steg videre ved også å hjelpe brukeren med å sammenligne de gyldige kandidatene og forstå konsekvensene av valget.

Løsningens særpreg ligger derfor ikke i en unik teknologi, men i kombinasjonen av:

**kontrollerbare regler + enkel kostnadsberegning + ansattpreferanser + forklarbar KI-støtte + menneskelig sluttbeslutning.**

Denne tilnærmingen gjør det mulig å bruke KI der den er nyttig, uten å overlate absolutte krav eller kritiske beregninger til en språkmodell.

## Hvem dette er for

**Primærbruker**

Primærbrukeren er en turnusansvarlig, ressursplanlegger eller leder som må håndtere endringer i en allerede oppsatt bemanningsplan.

Brukeren trenger raskt å kunne gå fra:

> «Denne vakten mangler bemanning»

til:

> «Dette er de mest aktuelle kandidatene, dette koster de ulike alternativene, og dette er hvorfor de rangeres forskjellig.»

Suksess for primærbrukeren betyr å kunne identifisere realistiske kandidater uten å måtte kontrollere alle ansatte manuelt, samtidig som beslutningsgrunnlaget er forståelig.

**Sekundærbruker**

Ansatte kan være sekundærbrukere i en senere versjon, for eksempel ved å kunne registrere preferanser eller undersøke muligheter for vaktbytte. Dette inngår ikke i kjerneløsningen for første versjon.

## Suksesskriterier

Førsteversjonen regnes som vellykket dersom den kan demonstrere en komplett og forståelig prosess fra en eksisterende turnus til et begrunnet forslag til erstatter. Løsningen skal kunne demonstrere følgende:

- En fiktiv turnus med omtrent 20–30 ansatte kan behandles.
- Brukeren kan velge én eksisterende vakt som må bemannes på nytt.
- I definerte testscenarioer skal 100 % av kandidatene som bryter en implementert hard regel bli filtrert bort.
- En kandidat som er utelukket av en hard regel, skal aldri kunne bli anbefalt av KI.
- Brukeren skal få presentert en kort liste over de mest aktuelle kandidatene uten å måtte kontrollere alle 20–30 ansatte manuelt.
- Systemet skal forklare hvilke faktorer som påvirker rangeringen av hver kandidat.
- Samme strukturerte input skal gi samme resultat for harde regler og kostnadsberegninger hver gang.
- Systemet skal demonstrere minst ett scenario der den billigste kandidaten ikke nødvendigvis rangeres høyest, fordi andre hensyn samlet sett gjør en annen kandidat bedre.
- KI skal kunne tolke minst noen definerte tekstbaserte ansattpreferanser og bruke disse i forklaringen av kandidatene.
- Brukeren skal alltid være den som tar den endelige beslutningen.

## Omfang

**Inkludert (in scope)**

Førsteversjonen skal demonstrere håndtering av én turnusendring om gangen i en eksisterende, fiktiv turnus med omtrent 20–30 ansatte. Løsningen skal:

- bruke et begrenset sett harde regler, for eksempel kompetanse, kolliderende vakter og noen få definerte arbeidstids-/hviletidsregler
- sammenligne gyldige kandidater ut fra noen få myke faktorer
- bruke en forenklet økonomisk modell, for eksempel ordinær kostnad kontra overtidskostnad
- ta hensyn til et begrenset sett ansattpreferanser
- bruke KI til å tolke og forklare myke forhold
- presentere en rangert kandidatliste med begrunnelse
- kreve menneskelig godkjenning før en endring anses som valgt
- tilby enkel innlogging for turnusansvarlig, slik at løsningen ikke er åpen for alle

**Ikke inkludert (out of scope)**

Førsteversjonen skal ikke:

- generere en komplett turnus fra bunnen av
- optimalisere en hel turnus automatisk
- garantere full juridisk etterlevelse av arbeidsmiljøloven
- implementere komplette tariff-, lønns- eller overtidsregler
- beregne full lønnskostnad med alle tillegg og avgifter
- bruke ekte personopplysninger
- integreres mot reelle HR-, lønns- eller turnussystemer
- håndtere flere kompliserte turnusendringer samtidig
- automatisk gjennomføre KI-forslag
- inneholde full ansattportal eller avansert rollebasert autentisering (flere roller, tilgangsnivåer, SSO e.l.)
- inneholde en generell KI-chat for ansatte

Ansattportal og mer avansert autentisering/KI-funksjonalitet behandles som mulige stretch goals dersom kjerneløsningen er ferdig og stabil. Førsteversjonen skal likevel ha enkel innlogging (for eksempel brukernavn/passord) for turnusansvarlig.

## Visjon

Dersom konseptet lykkes, kan løsningen i løpet av 2–3 år utvikles fra en prototype for enkeltstående turnusendringer til et bredere beslutningsstøttesystem for bemanningsplanlegging.

En videreutviklet løsning kan håndtere større turnusplaner, flere samtidige endringer og et mer omfattende regelverk. Den kan integreres med eksisterende HR-, lønns- og turnussystemer og benytte faktiske kostnadsdata.

Ansatte kan få egne brukerkontoer og bruke en KI-assistent til spørsmål som:

- «Hvem kan jeg bytte vakt med på tirsdag?»
- «Hvilke ledige vakter kan jeg ta?»
- «Hvor mye overtid har jeg denne måneden?»

Turnusansvarlige kan samtidig få mer avansert analyse, scenarioevaluering og støtte ved større bemanningsendringer.

Den langsiktige visjonen er et system der KI gjør kompleks bemanningsinformasjon lettere å forstå og bruke, mens faste regler og menneskelig kontroll sørger for at kritiske krav og beslutninger ikke overlates til KI alene.
