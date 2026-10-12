# Sensorveiledning IBE160 – Del 1 applikasjon og prosess

Kilde: [Original PDF](sensorveiledning-del-1.pdf), høst 2026, sju sider.

Dette er en tekstgjengivelse for søk og bruk av KI-agenter, kontrollert mot tekstinnholdet på alle sju sider 2026-10-12. Overskrifter, lister og tabeller er tilpasset Markdown; sidene er merket nedenfor. Original PDF er autoritativ ved avvik. Nummereringen i sensors fremgangsmåte er beholdt fra kilden (to punkter merket 1).

Prosjektets tiltak og status ligger i [vurderingsmatrisen](vurderingsmatrise.md) og er gruppens tolkning, ikke del av sensorveiledningen.

<!-- PDF-side 1 -->

### Kildeside 1

Sensorveiledning – Del 1
IBE160 Programmering med KI – Applikasjon og prosess (70 %)
Høst 2026 · Utfyller den overordnede sensorveiledningen

## 1. Formål

Denne veiledningen utdyper hvordan sensor vurderer del 1 av mappen, Prosjektkode og
funksjonalitet, som teller 70 % av den samlede karakteren. Del 1 vurderer applikasjonen og repoet
som helhet: hva gruppen har laget, hvordan de har laget det, og om andre kan forstå, kjøre og
videreutvikle det.
Emnet handler om å styre KI-assistert utvikling. Derfor vurderes ikke bare sluttproduktet, men i like
stor grad sporene av prosessen: planlegging, prompts, iterasjoner, kvalitetssikring og beslutninger.
Emnebeskrivelsen krever at mappen dokumenterer en realistisk utviklingsprosess, og at
dokumentasjonen viser hvordan KI ble brukt og hvordan koden er kvalitetssikret.
Veiledningen er et støtteverktøy for faglig skjønn, ikke en mekanisk sjekkliste. Kravene må ses i
forhold til oppgaven og ambisjonsnivået gruppen har valgt.

## 2. Vurderingskriterier og veiledende vekting

Del 1 vurderes ut fra sju kriterier. Vektene er veiledende og brukes til å gi en begrunnet delkarakter
for del 1. Prosess og KI-styring har størst vekt fordi det er kjernen i emnets læringsutbytte.

| Nr. | Kriterium | Kort beskrivelse | Vekt |
|---|---|---|---:|
| 1 | Prosess og KI-styring | Sporbar vei fra plan til kode: commits, prompts, iterasjoner og beslutninger | 30 % |
| 2 | Funksjonalitet og omfang | Hva appen gjør, sett mot proposal og valgt oppgave | 20 % |
| 3 | Kvalitetssikring og testing | Tester, kodegjennomgang og retting av KI-generert kode | 15 % |
| 4 | Design og brukeropplevelse | Visuelt uttrykk, konsistens, brukervennlighet og tilgjengelighet | 10 % |
| 5 | Kodekvalitet og arkitektur | Lesbar, strukturert og sammenhengende kode | 10 % |
| 6 | README og kjørbarhet | Tydelig beskrivelse av hvordan appen installeres og kjøres | 10 % |
| 7 | Ryddighet i repoet | Struktur, riktige filer, ingen hemmeligheter eller byggeartefakter | 5 % |

Kriterium 1, 6 og 7 handler om prosess og etterprøvbarhet og utgjør til sammen 45 %. Kriterium 2–5
handler om produktet og utgjør 55 %.

## 3. Fremgangsmåte for sensor

Gå gjennom hver gruppe i samme rekkefølge, slik at vurderingene blir konsekvente og
etterprøvbare. Sett av tid til å kjøre appen selv.

---

<!-- PDF-side 2 -->

### Kildeside 2

1. Forbered. Les gruppens godkjente proposal og eventuell product brief, slik at du vet hva
gruppen har lovet å lage.
1. Hent repoet ved fristen. Klon gruppens repo i IBE160-2026 og sjekk ut siste commit før
innleveringsfristen. Se bort fra senere endringer.
2. Følg README. Installer og start appen på en ren maskin eller i et rent miljø, kun etter
oppskriften i README.md. Noter hvert steg som mangler, er uklart eller feiler.
3. Test appen. Gå gjennom kjerneflytene som proposal og README beskriver. Prøv også feil
input og uventet bruk.
4. Vurder design. Se på helhet, konsistens og brukervennlighet, og prøv gjerne ulike
skjermstørrelser hvis det er relevant for appen.
5. Gå gjennom historikken. Se på commit-historikken (for eksempel med git log og GitHub
Insights): fordeling over tid, commit-meldinger, branches, pull requests og issues.
6. Les prosessdokumentasjonen. Planleggingsdokumenter fra BMAD, prompts og KI-økter,
beslutninger og dokumentasjon av kvalitetssikring. Kontroller at dokumentene henger
sammen med koden.
7. Kjør testene. Kjør testene slik README beskriver, og vurder hva de faktisk tester.
8. Les koden. Stikkprøv sentrale deler av koden og vurder struktur og lesbarhet.
9. Fyll ut vurderingsskjemaet (kapittel 6) med karakter og kort begrunnelse per kriterium.
Bruk rimelig innsats på å få appen til å kjøre (veiledende inntil 15–20 minutter). Mangler som en
vanlig bruker ikke kan løse ved hjelp av README, regnes som mangler ved README, ikke som sensors
problem. Dersom appen ikke lar seg kjøre, vurderes funksjonalitet ut fra kode, tester, skjermbilder og
video i repoet, men det trekker tydelig ned på kriterium 6 og begrenser hvor høyt kriterium 2 kan
vurderes.

## 4. Kriteriene i detalj

### 1. Prosess og KI-styring (30 %)

Kriteriet vurderer om repoet viser en realistisk, iterativ utviklingsprosess der gruppen har styrt KI
bevisst – fra krav og plan, via implementering, til testing og forbedring. Det er sporene av prosessen i
repoet som vurderes her; refleksjonen over prosessen vurderes i del 2.

#### Sensor ser etter

- Planlegging: BMAD-dokumenter (for eksempel product brief, PRD, arkitektur, epics og stories)
som faktisk er brukt og oppdatert, ikke bare generert én gang.

- Sammenheng plan–kode: at funksjoner i koden kan spores tilbake til krav og stories, og at
avvik fra planen er forklart.

- Commit-historikk: jevn utvikling over tid fremfor én stor commit før fristen; små, avgrensede
commits med beskrivende meldinger.

- Arbeidsflyt: bruk av branches, pull requests, issues eller tilsvarende for å organisere arbeidet.

- Sporbar KI-bruk: lagrede prompts og KI-økter, og eksempler på at gruppen har presisert krav,
avvist, rettet eller forbedret KI-forslag.

- Beslutninger: dokumenterte valg av teknologi, arkitektur og løsninger, med begrunnelse.

- Samarbeid: at historikken viser at arbeidet er utført av gruppen over tid. Ujevn fordeling i
commit-statistikk alene er ikke grunnlag for trekk, siden par- og mobprogrammering er vanlig.

---

<!-- PDF-side 3 -->

### Kildeside 3

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Prosessen kan følges tydelig fra plan til ferdig app. Historikken viser jevn, iterativ utvikling. Prompts og beslutninger er dokumentert og koblet til konkrete endringer. Det finnes flere tydelige eksempler på at gruppen har vurdert, korrigert og styrt KI kritisk. |
| C | Prosessen er i hovedsak sporbar. Planleggingsdokumenter og prompts finnes, men koblingen til koden er delvis implisitt. Historikken viser utvikling over tid, med noen store eller lite beskrivende commits. |
| D–E | Prosessen er bare delvis synlig. Planleggingsdokumenter fremstår som generert én gang og ikke brukt videre. Få prompts er lagret, og historikken er konsentrert til få perioder eller noen få store commits. |
| F | Ingen troverdig prosess er dokumentert: mangler planlegging og prompts, eller historikken består i praksis av én eller noen få opplastinger av ferdig kode. |

### 2. Funksjonalitet og omfang (20 %)

Kriteriet vurderer hva appen faktisk gjør og hvor godt den løser problemet som er beskrevet i
proposal, sett i forhold til ambisjonsnivået i valgt oppgave.

#### Sensor ser etter

- At kjerneflytene fra proposal og README fungerer fra start til slutt.

- Omfang og kompleksitet i forhold til oppgaven, for eksempel datalagring, flere brukerroller,
integrasjoner eller ikke-trivielle regler.

- Stabilitet: at appen tåler vanlig bruk, feil input og gjentatte handlinger uten å krasje.

- At det som er utelatt eller endret fra proposal, er beskrevet og begrunnet.

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Kjernefunksjonaliteten er komplett og stabil. Appen løser problemet godt og har et omfang som svarer til eller overgår ambisjonen i proposal. |
| C | De viktigste funksjonene virker, men noen er ufullstendige eller har feil i mindre vanlige tilfeller. Omfanget er rimelig for oppgaven. |
| D–E | Appen virker bare delvis. Sentrale funksjoner mangler eller feiler, eller omfanget er klart mindre enn proposal tilsier uten god begrunnelse. |
| F | Appen fungerer ikke, eller gjør så lite at oppgaven i praksis ikke er løst. |

### 3. Kvalitetssikring og testing (15 %)

Kriteriet vurderer hvordan gruppen har kontrollert at KI-generert kode gjør det den skal, og hvordan
feil er funnet og rettet.

---

<!-- PDF-side 4 -->

### Kildeside 4

#### Sensor ser etter

- Automatiserte tester (enhets-, integrasjons- eller ende-til-ende-tester) som kan kjøres etter
beskrivelsen i README, og som tester meningsfull logikk.

- Dokumenterte manuelle tester eller testplaner der automatiske tester ikke er hensiktsmessige.

- Spor av kodegjennomgang, for eksempel kommentarer i pull requests eller beskrivelser av feil
som ble funnet i KI-generert kode og hvordan de ble rettet.

- Grunnleggende feilhåndtering, validering av input og bevissthet om sikkerhet, for eksempel at
hemmeligheter ikke ligger i koden.

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Testene er relevante, kjører uten feil og dekker sentral logikk. Kvalitetssikringen er systematisk og dokumentert, med konkrete eksempler på feil som ble avdekket og rettet. |
| C | Det finnes tester og noe dokumentert kvalitetssikring, men dekningen er ujevn eller testene er overfladiske. |
| D–E | Lite testing. Testene er få, feiler eller tester bare trivielle ting, og kvalitetssikringen er knapt dokumentert. |
| F | Ingen spor av testing eller kvalitetssikring av KI-generert kode. |

### 4. Design og brukeropplevelse (10 %)

Kriteriet vurderer om appen er gjennomtenkt utformet for brukerne den er laget for. Design
omfatter både visuelt uttrykk og hvor lett appen er å forstå og bruke. Vurderingen tilpasses typen
app; et kommandolinjeverktøy vurderes for eksempel ut fra tydelige meldinger og god struktur i
utdata.

#### Sensor ser etter

- Helhetlig og konsistent visuelt uttrykk: farger, typografi, avstand og komponenter.

- Tydelig navigasjon og informasjonsstruktur; brukeren forstår hva som kan gjøres og hva som
skjer.

- Forståelige tilbakemeldinger, feilmeldinger og tomtilstander.

- Grunnleggende tilgjengelighet (universell utforming): lesbar kontrast, tastaturnavigasjon,
alternativtekst og fornuftige skjemaetiketter.

- Tilpasning til relevante skjermstørrelser.

- Spor av designarbeid i prosessen, for eksempel skisser, wireframes eller UX-beskrivelser i
planleggingsdokumentene.

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Appen fremstår gjennomarbeidet, konsistent og intuitiv. Designvalg er bevisste og tilpasset målgruppen, og grunnleggende tilgjengelighet er ivaretatt. |
| C | Ryddig og brukbar, men med noen inkonsistenser eller uklarheter i flyt og tilbakemeldinger. |

---

<!-- PDF-side 5 -->

### Kildeside 5

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| D–E | Fungerer, men fremstår lite gjennomtenkt: uoversiktlig, inkonsistent eller vanskelig å bruke uten forklaring. |
| F | Så uoversiktlig eller ufullstendig at appen i praksis ikke kan brukes som tiltenkt. |

### 5. Kodekvalitet og arkitektur (10 %)

Kriteriet vurderer om koden er forståelig og vedlikeholdbar. Studentene skal ikke ha skrevet koden
selv, men de har ansvar for at KI-generert kode utgjør en sammenhengende og ryddig helhet.

#### Sensor ser etter

- Logisk mappe- og modulstruktur som samsvarer med arkitekturen som er beskrevet.

- Lesbar kode med beskrivende navn og fornuftige kommentarer der det trengs.

- Lite duplisering, død kode og utkommenterte rester fra tidligere KI-forsøk.

- Konsekvent stil, gjerne støttet av linter eller formatterer.

- Fornuftig håndtering av konfigurasjon og avhengigheter.

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Koden er godt strukturert, lesbar og konsekvent. Arkitekturen er tydelig og samsvarer med dokumentasjonen. |
| C | Koden er i hovedsak ryddig, men med noe duplisering, uklare navn eller deler som ikke passer inn i strukturen. |
| D–E | Koden er vanskelig å følge, med mye duplisering, død kode eller uklar struktur. |
| F | Koden er så uoversiktlig eller ufullstendig at den ikke kan vurderes som en sammenhengende løsning. |

### 6. README og kjørbarhet (10 %)

README.md er døra inn til prosjektet. Kriteriet vurderer om en person som ikke kjenner prosjektet,
kan forstå hva appen gjør og få den til å kjøre ved å følge README – uten å spørre gruppen.

#### Sensor ser etter

- Kort beskrivelse av hva appen gjør og hvem den er for, gjerne med skjermbilde.

- Forutsetninger med versjoner, for eksempel Node.js, Python eller database.

- Steg-for-steg installasjon og oppstart med eksakte kommandoer som kan kopieres.

- Konfigurasjon: hvilke miljøvariabler som trengs, med en eksempelfil (for eksempel
.env.example) uten ekte hemmeligheter.

- Testdata eller testbrukere ved behov, og hvordan testene kjøres.

- Oversikt over mappestrukturen og lenker til planleggings- og prosessdokumentasjonen.

- At README er tilpasset prosjektet og oppdatert, ikke en uendret mal eller generert tekst som
ikke stemmer med koden.

---

<!-- PDF-side 6 -->

### Kildeside 6

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Sensor får appen til å kjøre ved å følge README uten avvik. README er tydelig, komplett og oppdatert, og gir god oversikt over prosjektet. |
| C | Appen lar seg kjøre etter README, men med små hull som en erfaren bruker kan løse selv. |
| D–E | README er mangelfull eller delvis feil, slik at det krever betydelig innsats å få appen til å kjøre. |
| F | README mangler, eller appen kan ikke kjøres ut fra beskrivelsen. |

### 7. Ryddighet i repoet (5 %)

Kriteriet vurderer om repoet er organisert slik at andre lett finner frem, og om det bare inneholder
filer som hører hjemme der.

#### Sensor ser etter

- Oversiktlig mappestruktur med tydelig skille mellom kode, dokumentasjon og eventuelle
ressurser.

- En .gitignore som holder byggeartefakter, avhengigheter (for eksempel node_modules eller
venv) og lokale filer ute av repoet.

- Ingen hemmeligheter i repoet eller historikken, som API-nøkler, passord eller .env-filer.

- Ingen løse testfiler, sikkerhetskopier, gamle versjoner eller tilfeldige filer i rotmappen.

- Fornuftige fil- og mappenavn.

#### Kjennetegn

| Nivå | Kjennetegn |
|---|---|
| A–B | Repoet er ryddig og logisk organisert. Kun relevante filer er versjonert, og det finnes ingen hemmeligheter. |
| C | I hovedsak ryddig, men med enkelte overflødige filer eller noe uklar struktur. |
| D–E | Rotete: mange overflødige filer, byggeartefakter eller avhengigheter i repoet, og uklar struktur. |
| F | Repoet er så uoversiktlig at det er vanskelig å finne frem, eller det inneholder ekte hemmeligheter som ikke er håndtert. |

## 5. Typiske varseltegn

Følgende forhold bør undersøkes nærmere og omtales i begrunnelsen dersom de påvirker
karakteren:

- Hele eller nesten hele koden er lagt inn i én eller noen få commits rett før fristen.

- Planleggingsdokumentene beskriver en annen app enn den som er levert, eller er tydelig
generert i etterkant.

- README er en uendret mal, eller kommandoene i README virker ikke.

---

<!-- PDF-side 7 -->

### Kildeside 7

- API-nøkler, passord eller .env-filer er committet.

- node_modules, venv, build-mapper eller store binærfiler ligger i repoet.

- Testene feiler, eller tester bare trivielle ting.

- Store mengder død kode, dupliserte filer eller rester fra forkastede KI-forsøk.

- Dokumentasjonen av KI-bruk er generell og kan ikke knyttes til konkrete endringer i repoet.

## 6. Vurderingsskjema og delkarakter for del 1

Gi en bokstavkarakter per kriterium. Regn om til tall (A = 5, B = 4, C = 3, D = 2, E = 1, F = 0),
multipliser med vekten og summer. Bruk samme terskelverdier som i den overordnede veiledningen:
A ≥ 4,5 · B ≥ 3,5 · C ≥ 2,5 · D ≥ 1,5 · E ≥ 0,5 · F < 0,5.

| Kriterium | Vekt | Karakter | Begrunnelse |
|---|---:|---|---|
| 1. Prosess og KI-styring | 0,30 | | |
| 2. Funksjonalitet og omfang | 0,20 | | |
| 3. Kvalitetssikring og testing | 0,15 | | |
| 4. Design og brukeropplevelse | 0,10 | | |
| 5. Kodekvalitet og arkitektur | 0,10 | | |
| 6. README og kjørbarhet | 0,10 | | |
| 7. Ryddighet i repoet | 0,05 | | |
| Vektet skår / delkarakter del 1 | 1,00 | | |

Eksempel: Kriteriene 1–7 vurderes til (B, C, C, A, C, B, D) → (4, 3, 3, 5, 3, 4, 2). Skår = 0,30·4 + 0,20·3 +
0,15·3 + 0,10·5 + 0,10·3 + 0,10·4 + 0,05·2 = 3,55 → B.
Delkarakteren for del 1 inngår deretter med 70 % i den samlede karakteren, sammen med
refleksjonsrapporten (30 %).
Beregningen er et hjelpemiddel for konsistens. Sensor kan avvike fra den beregnede delkarakteren
når helhetsinntrykket tilsier det, men avviket skal begrunnes kort.
