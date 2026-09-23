---
title: "IBE160 Turnusprosjekt — addendum"
status: draft
created: 2026-09-08
updated: 2026-09-17
---

# Addendum: IBE160 Turnusprosjekt

Underlagsmateriale som ikke hører hjemme i selve briefen, men som er nødvendig for proposal, kravspesifikasjon, arkitektur og refleksjonsrapport.

> **Gjeldende brief** er `product-brief.md` i repo-roten — gruppens felles versjon fra GitHub (`IBE160-2026/G15-gaertner-kuduz-skinstad-saetren`). `brief.md` i denne mappa er en kopi av den. Endringer i briefen gjøres i `product-brief.md` og deles via GitHub.

## 1. Kilder og faktagrunnlag

Den felles briefen inneholder ingen markedstall eller eksterne kilder. Materialet under ble samlet inn til det tidligere lokale utkastet og kan brukes i proposal og refleksjonsrapport — udokumenterte påstander er en unødvendig svakhet.

### Ressursbruk på turnusarbeid

- Norsk helseregion, 3 000+ ansatte: manuell turnusprosess tok flere dager per måned, opptil 40 timer månedlig per avdeling. Planleggere måtte samtidig ta hensyn til kompetanse, arbeidsbelastning, ansattpreferanser, lovkrav og kontinuitet i pasientbehandlingen.
  [aien.no — AI revolusjonerer turnusplanlegging i helsevesenet](https://www.aien.no/case-studies/healthcare-scheduling)
- Internasjonalt: ett enkelt forfall tilsvarte tradisjonelt rundt 30 minutter med telefonrunder.
  [indeavor.com — Frontline Absence Management](https://www.indeavor.com/blog/frontline-absence-management-best-practices/)

### Konkurrentbildet

| Løsning | Posisjon | Vurdering fra brukere |
|---|---|---|
| [Gat Ressursstyring](https://gatressurs.no/) (Visma) | De facto standard i norsk offentlig helsevesen | Dekker turnus, vaktbytte, godkjenningsflyt og lovkontroll |
| [Quinyx](https://www.capterra.com/p/221040/Quinyx/reviews/) | Nordisk, privat sektor og handel | 4,7 / 5 på 613 anmeldelser (Capterra); 4,3 på G2 |
| [Planday](https://www.g2.com/compare/planday-vs-quinyx) | Nordisk, service og handel | 4,9 / 5 på 498 anmeldelser; 4,5 på G2 |

**Merk:** dette er godt likte produkter. Briefen må ikke antyde at de er dårlige — den påstanden holder ikke, og en sensor vil se det.

Registrert kritikk av Quinyx: for mange klikk for å nå fram, bratt læringskurve i starten, og vanskelig å hente ut riktig informasjon i rapporter. Mønsteret er *tilgjengelighet av informasjon*, ikke manglende funksjonalitet — og det er nettopp gapet prosjektet retter seg mot.

### Helseplattformen som advarsel

Relevant både som markedsargument og som stoff til refleksjonsrapportens etikkdel.

- Riksrevisjonen (2024): planlegging, organisering og innføring vurdert som «sterkt kritikkverdig» — deres strengeste kategori. Helsetilsynet (2023): økt risiko for svikt i pasientbehandlingen.
  [tidsskriftet.no — Helseplattformen, en IT-skandale i Midt-Norge](https://tidsskriftet.no/2023/01/leder/helseplattformen-en-it-skandale-i-midt-norge)
- Ni av ti leger mistet tillit til toppledelsen.
  [aftenposten.no](https://www.aftenposten.no/norge/i/Gyga3q/dette-sier-legene-om-helseplattformen)
- Rapport (2025): systemet gjorde helsepersonell mindre effektive.
  [sykepleien.no](https://sykepleien.no/2025/12/rapport-helseplattformen-har-gjort-helsepersonell-mindre-effektive)
- Kostnad nær 7 mrd. kroner mot planlagte under 4 mrd.
- Kjernen i kritikken: dårlig brukervennlighet — personellet opplevde systemet som tungt og var usikre på om de gjorde ting riktig.
  [dagensmedisin.no](https://www.dagensmedisin.no/e-helse-helseplattformen/brukerne-ikke-ledelsen-avgjor-om-helseplattformen-er-brukervennlig/747172)

## 2. Regelverk — grunnlag for regelmotoren

Verifisert mot arbeidsmiljøloven kapittel 10. **Disse tallene er startpunktet for hvilke harde regler som skal implementeres.** Briefen fastsetter ikke hvilke regler som inngår — den sier «et begrenset sett harde regler, for eksempel kompetanse, kolliderende vakter og noen få definerte arbeidstids-/hviletidsregler» — så det konkrete utvalget må avgjøres i PRD/spec.

| Regel | Hovedregel | Med tariffavtale |
|---|---|---|
| Daglig sammenhengende hvile | 11 timer per 24 t | Ned til 8 timer |
| Ukentlig sammenhengende fri | 35 timer per 7 dager | Ned til 28 timer |
| Maks samlet arbeidstid per døgn | 13 timer | — |
| Maks samlet arbeidstid per uke | 48 timer | — |
| Overtid per 7 dager | 10 timer | 20 timer |
| Overtid per 52 uker | 200 timer | — |
| Skiftarbeid, ukentlig | 38 t (døgnkontinuerlig) / 36 t (helkontinuerlig) | — |

Kilder: [Lovdata, aml. kap. 10](https://lovdata.no/nav/lov/2005-06-17-62/kap10) · [Arbeidsrettsadvokater — hviletid](https://arbeidsrettsadvokater.as/artikler/hvor-mange-timer-hvile-mellom-vakter) · [Delta — arbeidsfri og hviletid](https://www.delta.no/dine-rettigheter/arbeidstid/arbeidsfri-og-hviletid)

**Anbefaling for første versjon:** implementer et lite, godt testet utvalg — 11-timersregelen, 35-timersregelen, kolliderende vakter og kompetansekrav. Fire regler som beviselig fungerer er verdt mer enn tolv som er halvveis. Briefen lover eksplisitt ikke full juridisk etterlevelse, og det løftet må holdes.

## 3. Forkastede alternativer

### Vaktbytte mellom ansatte som kjernefunksjonalitet

**Vurdert og lagt utenfor første versjon.** Utløst av at vaktbytte opprinnelig ble nevnt sidestilt med sykefravær.

| | Sykefravær | Vaktbytte |
|---|---|---|
| Hull som skal fylles | Én vakt | To vakter |
| Hvem må valideres | Kandidatene | Begge ansatte, mot begge vakter |
| Regelsjekk | Én retning | Toveis — A tar B sin vakt *og* B tar A sin |
| Hvem starter prosessen | Turnusansvarlig | Den ansatte |
| Forutsetter | Ingenting nytt | Ansattportal, innlogging, forhandlingsflyt |

**Begrunnelse for å utelate:** vaktbytte er ikke en variant av sykefravær, men et annet problem med en annen bruker og dobbel regelvalidering. Det ville flyttet tyngdepunktet vekk fra primærbrukeren (HR) og innført en forhandlingsflyt som ikke tilfører prosjektets problemstilling noe.

**Status i felles brief:** ansatte er ikke brukere i første versjon. Briefen plasserer hele ansattportalen — både vaktbytte og en lesende oversikt over egne vakter — som mulig stretch goal eller senere versjon. Den lesende oversikten som det tidligere lokale utkastet hadde i v1, er dermed tatt ut.

### Å la KI utføre rangering eller regelsjekk

**Vurdert og forkastet.** Kort begrunnelse: lovkrav og kostnad må være reproduserbare, og en språkmodell gir sannsynlighet der loven krever forutsigbarhet. Se punkt 4 for den fulle argumentasjonen — den hører hjemme i refleksjonsrapporten.

## 4. Argumentasjon til refleksjonsrapporten (30 %)

Rå notater. Skal bearbeides, ikke kopieres.

### «Dette er jo bare en sorteringsalgoritme med en tekstgenerator på toppen»

Forvent innvendingen. Fire linjer å svare langs:

1. **Det var avgjørelsen, ikke en mangel.** Å la en språkmodell beregne hviletid ville vært uforsvarlig — loven krever determinisme, modellen leverer sannsynlighet. Emnets eget læringsutbytte krever evne til å «vurdere når KI-assistert utvikling er hensiktsmessig», og det inkluderer å vite når den ikke er det.
2. **Sortering er ikke det vanskelige.** Det vanskelige er å avgjøre hva det skal sorteres på, og å gjøre avveiningen forståelig nok til at brukeren tør å handle på den. Helseplattformen viser prislappen når det leddet hoppes over.
3. **Ingeniørarbeidet ligger i skjøten.** Hvordan garanteres det at KI aldri kan anbefale en kandidat som er filtrert bort? Strukturert input, validering av modellens output, feilhåndtering når modellen finner på noe. Dette er et konkret, testbart problem.
4. **Enkelhet er strategien.** Et system enkelt nok til at korrektheten kan bevises, er et system der kvalitetssikringen faktisk lar seg dokumentere — som er eksplisitt krav i 70 %-delen. Et mer ambisiøst system ville ikke rukket å bli kvalitetssikret.

### Bias i algoritmen

Prosjektets sterkeste etikkmateriale, og direkte koblet til emnets kunnskapsmål om «risiko for bias i algoritmer»:

- En rangering som vekter «har sagt ja før» favoriserer systematisk dem som alltid sier ja, og straffer indirekte dem med omsorgsansvar.
- Vekting på kostnad favoriserer systematisk lavtlønte og deltidsansatte, som dermed får uforholdsmessig mange ekstravakter.
- Å vekte «lav akkumulert belastning» høyt kan slå motsatt ut for den som ønsker ekstravakter.
- **Poenget:** enhver vekting er et normativt valg. Systemet kan ikke være nøytralt — det kan bare være åpent om hva det vekter. Det er et argument for forklarbarhet, ikke bare et etisk forbehold.

### Eierskap og juridiske forhold ved KI-generert kode

- Hvem eier kode generert av en språkmodell? Lisensiering av treningsdata, opphavsrett til output.
- Hvordan håndteres det at generert kode kan ligne på lisensiert kode i treningsmaterialet?

### Testing av ikke-deterministisk output

Reell metodisk utfordring, og godt stoff:
- Deterministisk lag testes konvensjonelt (enhetstester per regel).
- KI-laget kan ikke testes på eksakt strengmatch. Alternativer: teste invarianter (nevner aldri en filtrert kandidat), teste at alle påkrevde elementer er til stede, teste robusthet ved feilaktig eller tomt svar fra modellen.
- **Konklusjonen er selve poenget:** grensen mellom lagene ble lagt der den ble nettopp fordi det gjør systemet testbart.

## 5. Emnekrav — IBE160 Programmering med KI, høst 2026

15 studiepoeng · Molde · emneansvarlig Bård Inge Austigard Pettersen · gruppe på 4 ± 1
[Emnebeskrivelse](https://www.himolde.no/studier/emner/log/2026/host/ibe160.html)

### Vurdering

| Del | Vekt | Form |
|---|---|---|
| Prosjektkode og funksjonalitet | 70 % | Gruppevis. KI-generert applikasjon. **Dokumentasjon må vise hvordan KI ble brukt og kvalitetssikring av koden.** |
| Refleksjonsrapport | 30 % | Gruppevis. Utviklingsprosess, utfordringer, kritisk vurdering av KIs påvirkning, etiske og teknologiske implikasjoner. |

**Arbeidskrav:** godkjent proposal som beskriver applikasjonen. Hele gruppen får godkjent. Den felles briefen (`product-brief.md`) er grunnlaget for proposalen.

### Sentral tolkning

Emnet handler om at **KI genererer koden** — ikke om at applikasjonen inneholder KI. Læringsutbyttet er å formulere systemkrav i naturlig språk, styre KI-generert kode, og kvalitetssikre og teste resultatet.

**Konsekvenser:**
- KI i selve produktet er et *produktvalg*, ikke et karakterkrav. Beholdes fordi det gir substans til refleksjonsrapporten.
- Brukerautentisering er ikke nevnt i emnebeskrivelsen og er ikke et minstekrav for bestått. Den felles briefen tar likevel enkel innlogging (brukernavn/passord) for turnusansvarlig inn i første versjon som et produktvalg, slik at løsningen ikke er åpen for alle. Flere roller, tilgangsnivåer og SSO er eksplisitt utenfor omfang.
- **Bør bekreftes med faglærer** før proposal leveres. Muntlige føringer i undervisningen veier tyngre enn en lesning av nettsiden.

### Praktiske konsekvenser for arbeidsformen

Fordi kvalitetssikring er eksplisitt vurderingskriterium, må dette etableres fra første commit — ikke rekonstrueres i innleveringsuka:

- Loggfør prompter og resultater underveis.
- Bruk commit-meldinger som skiller KI-generert kode fra manuelt rettet kode.
- Noter hva som måtte rettes i generert kode, og hvorfor.
- Skriv testene for regelmotoren tidlig; de er beviset på at kjernen er korrekt.

## 6. Avvik fra det tidligere lokale utkastet (2026-09-08)

Den felles briefen på GitHub erstattet det lokale utkastet 2026-09-17. Punktene under sto i det lokale utkastet, men er endret eller utelatt i den felles versjonen. Listen finnes slik at ingenting går tapt uten at det er bevisst.

| Tema | Lokalt utkast | Felles brief |
|---|---|---|
| Produktnavn | «Turnushjelperen» | «IBE160 Turnusprosjekt» |
| Ansatte i v1 | Sekundærbruker med lesende oversikt over egne kveld-/natt-/helgevakter | Ikke bruker i v1; ansattportal er stretch goal / senere versjon |
| Innlogging | Åpen avklaring | Enkel innlogging for turnusansvarlig er *innenfor* v1; avansert rollebasert autentisering er utenfor |
| Problemstilling | «… på en måte brukeren forstår og kan stole på» | Kortere formulering uten tillegget |
| Teknisk stack | JavaScript frontend, Python backend, GitHub | Ikke omtalt. Gruppebeslutningen fra 2026-09-08 står fortsatt; `.gitignore` på GitHub er satt opp for Next.js/Node og Python |
| Suksesskriterier | Tre nivåer: produkt, teknisk kvalitet, emnekrav | Kun produktnivå. Kriteriene for teknisk kvalitet (kjører fra rent repo, tester per hard regel, lekkasjetest mot KI-laget, feilhåndtering ved modellfeil) bør tas videre i PRD/spec |
| Markedsargument | Konkurrentbilde, ressurstall, Helseplattformen | Ikke med — ligger i punkt 1 over |
| «En ærlig forutsetning» | Egen seksjon om manglende domeneerfaring | Ikke med |
| «Arbeidsform og KI i utviklingen» | Egen seksjon som dekker 70 %-kravet | Ikke med — se punkt 5 over |
| Åpne avklaringer | Seks punkter | Ikke med. Gjenstående: verifisere med faglærer om KI i produktet er vurderingskrav; konkret utvalg av harde regler; myke faktorer og vekting; detaljnivå i kostnadsmodell; arbeidsdeling og frister |
