# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G15 – G15-gaertner-kuduz-skinstad-saetren |
| **Product brief** | `product-brief.md` (commit `ee6d798`). Kopien i `_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/brief.md` er identisk, og addendumet i samme mappe er også lest. |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Godt utgangspunkt med justeringer.** Gruppen kan gå videre og innarbeide punktene under.

**Det som er bra:**

1. Problemet er skarpt avgrenset: én vakt i en eksisterende turnus skal bemannes på nytt, ikke en hel turnus som skal genereres. Avgrensningen gjør prosjektet gjennomførbart, og «Ikke inkludert» er tydelig og ærlig (ingen full juridisk etterlevelse, ingen tariffregler, ingen automatisk gjennomføring).
2. Arbeidsdelingen mellom regler og KI er gjennomtenkt: harde regler, arbeidstid og kostnad beregnes deterministisk, mens KI bare tolker myke preferanser og forklarer avveininger. Suksesskriteriene «100 % av kandidatene som bryter en hard regel filtreres bort» og «en utelukket kandidat skal aldri kunne anbefales av KI» er svært gode og testbare.

**De viktigste endringene:**

1. Lås hvilke harde regler som er med i v1. Addendumet anbefaler 11-timersregelen, 35-timersregelen, kolliderende vakter og kompetanse, men briefen sier bare «for eksempel». Skriv utvalget inn i briefen eller PRD-en, slik at testene får en fast fasit.
2. Beskriv de myke faktorene og hvordan de vektes (arbeidsbelastning, kostnad, preferanser). Kriteriet om at «den billigste kandidaten ikke nødvendigvis rangeres høyest» kan bare testes når vektingen er bestemt.
3. Legg inn en plan for hvordan sensor kan kjøre appen uten gruppens Gemini-nøkkel, for eksempel forhåndstolkede preferanser og ferdige forklaringer i testdataene, eller en tydelig mock-modus.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Middels**

**Sammenlignbart med:** 7) Kurs-FAQ-chatbot (middels), men med mer regelbasert domenelogikk. Prosjektet ligger i øvre del av middels og nærmer seg en sterkt avgrenset modul av 3) KI-styrt simulering av prosjektledelse.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | Høy | Hviletid, ukentlig fri, kolliderende vakter, kompetanse, overtidskostnad og rangering må alle stemme. Reglene er likevel konkrete og kan sjekkes mot kjente eksempler. |
| Datamodell – antall entiteter og relasjoner mellom dem | Middels | Ansatt, vakt, turnus, kompetanse, preferanse og godkjenning, med relasjoner mellom vakter og ansatte over tid. |
| Brukere, roller og innlogging | Lav | Én rolle (turnusansvarlig) med enkel innlogging. Ansattportal og flere roller er riktig plassert utenfor v1. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | Middels | Tolking av tekstpreferanser og forklaring av rangeringen. Krever validering av svaret og håndtering av feil eller tomt svar fra modellen. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | Lav | Bare språkmodell-API-et. Ingen integrasjon mot HR- eller lønnssystemer. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | Lav | Én endring om gangen og én bruker. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | Lav | Ikke beskrevet. Fiktiv turnus kan ligge som testdata. |
| Sikkerhet og personvern | Lav | Fiktive data og enkel innlogging. Husk at passord lagres som hash. |

**Hva vanskelighetsgraden betyr for dere:**

- _Middels:_ Et godt balansert valg. Pass på at kjerneflyten – velg vakt, filtrer kandidater, ranger, vis begrunnelse, godkjenn – blir ferdig og stabil før dere legger til KI-forklaringer og andre forbedringer. Regelmotoren er hjertet i appen og bør testes først.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Én turnusendring om gangen med 20–30 fiktive ansatte er et realistisk omfang. Dere har allerede PRD, arkitektur og epics, så dere ligger godt an. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | OK | Briefen har båret videre til PRD og om lag 26 stories. Hold antallet nede ved å vente med stretch goals til kjerneflyten virker. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Arkitekturen bruker FastAPI, SQLite og React, som Claude Code håndterer godt. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | Risiko | Arbeidstidsreglene er lette å feiltolke (døgnskifte, vakter over midnatt, hvileperioder over ukeskifte). Lag håndregnede eksempler med fasit for hver regel før Claude Code implementerer dem. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | OK | Harde regler, kostnad og reproduserbarhet («samme input gir samme resultat») er svært godt egnet for automatiske tester. KI-laget kan testes på invarianter, slik addendumet beskriver. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | Risiko | Gemini krever nøkkel. Sørg for at kjerneflyten (filtrering, rangering, kostnad) virker uten nøkkel, og at KI-delen enten har mock-svar eller en tydelig oppskrift i README. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | Risiko | Gemini har gratisnivå, men det kan endres og krever konto. Arkitekturens caching av tolkede preferanser er et godt grep. Bygg videre på det med ferdig tolkede testdata. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart med justert omfang.** Se forslagene under.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Begrens v1 til de fire harde reglene addendumet anbefaler, og legg flere arbeidstidsregler (13 t per døgn, 48 t per uke, overtidsgrenser) i et senere trinn når de fire er testet.
2. Bygg og test regelmotor og rangering ferdig uten KI først. Legg KI-tolking og KI-forklaring på som et eget trinn med mock-modus, slik at appen fungerer også når modellen svarer feil eller ikke svarer.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | OK | Sammendraget sier tydelig at appen er beslutningsstøtte for én vakt som må bemannes på nytt, og at KI ikke kan overstyre regler. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Spørsmålslisten (tilgjengelighet, kompetanse, hviletid, overtid, ønsker) gjør problemet konkret. Kildene i addendumet kan gjerne løftes inn med én setning. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | OK | Beskriver hva brukeren ser for hver kandidat: hvorfor den kan ta vakten, hva som trekker opp og ned, kostnad og preferanser. |
| What Makes This Different – er vurderingen ærlig og realistisk? | OK | Ærlig om at særpreget er kombinasjonen, ikke en unik teknologi. Addendumet viser at dere kjenner Gat, Quinyx og Planday. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | OK | Turnusansvarlig er tydelig primærbruker, og ansatte er bevisst skjøvet til en senere versjon. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Juster | De fleste er testbare. «KI skal kunne tolke minst noen definerte preferanser» og «kort liste» bør presiseres, for eksempel «minst fem definerte preferansetekster» og «topp fem kandidater». |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Juster | Godt skille mellom inn og ut, men «et begrenset sett harde regler» og «noen få myke faktorer» er for åpent. Navngi dem. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Ansattportal og KI-assistent ligger tydelig i visjonen og ikke i v1. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | OK | Briefen er allerede brukt videre i PRD, arkitektur og epics, og addendumet dokumenterer forkastede alternativer. Det er gode prosesspor. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | OK | Tydelig kjerneflyt med reell domenelogikk. Nok innhold uten å bli for stort. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Juster | Svært gode kriterier for harde regler. Testscenarioene trenger en fast regelliste og vekting for å kunne skrives. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | OK | Kandidatlisten med «trekker opp / trekker ned» gir et tydelig utgangspunkt for skjermbildene, og dere har allerede UX-arbeid. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Briefen nevner ikke stack, noe som er riktig. Skillet mellom regelmotor og KI-adapter gir en ryddig arkitektur. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | Avhengig av Gemini-nøkkel. Planlegg mock-modus og en ferdig fiktiv turnus som lastes ved oppstart. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Dere har nå briefen både i roten og i `_bmad-output`. Velg ett sted, og planlegg `.env.example` og en egen mappe for fiktive testdata. |

## 3. Neste steg for gruppen

1. Skriv inn de konkrete harde reglene og de myke faktorene med vekting i brief eller PRD, og lag håndregnede testscenarioer med fasit for hver regel.
2. Planlegg og beskriv en mock-modus for KI-delen, slik at kjerneflyten kan kjøres og testes uten Gemini-nøkkel.
3. Rydd i dupliseringen av briefen (rot og `_bmad-output`), slik at det er tydelig hvilken fil som gjelder.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
