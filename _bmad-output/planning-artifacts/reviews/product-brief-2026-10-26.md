---
title: Vurdering av produktbriefen
date: 2026-10-26
scope: product-brief.md, hele dokumentet
method: bmad-review
status: complete
---

# Vurdering av produktbriefen

Briefen gir en tydelig retning for en avgrenset skoleprototype: én vakt, fire harde regler, deterministisk rangering og KI som tolker og forklarer. Demo uten API-nøkkel og eksplisitt utelatelse av full juridisk etterlevelse gjør omfanget etterprøvbart. Formuleringen «lovlig og mulig» i sammendraget lover likevel mer enn dette omfanget. Tilgjengelighet, preferansenes gyldighetsperiode og håndtering av enkelte rangeringsgrenser trenger avklaring. Den påståtte brukernytten mangler en beskrevet forståelsestest.

Dette er en vurdering av dokumentets løfter og spesifikasjon, ikke en påstand om feil i implementert domenekode. Briefen ble ikke endret. PRD §4.2–4.5 og arkitektur AD-1/AD-6/AD-7 ble brukt til å kontrollere at funn ikke bare etterlyser detaljer som allerede er delegert dit. Forslag om flere harde regler, ansattportal eller full tariffmodell er holdt utenfor.

## Metode og avgrensning

- Tre uavhengige reviewere vurderte adversarial, edge-case og struktur; språklinsen fulgte strukturresultatet.
- Sensorveiledningen og vurderingsmatrisen ble lest. Relevante kriterier er særlig sporbar prosess, testbevis og forståelig brukeropplevelse. Det er ikke gitt karakter eller foretatt en full vurdering av prosjektet.
- Briefen har 1 646 ord etter `word_metrics.py`. Ingen lengdegrense er satt.
- De eksterne forutsetningene er ikke bekreftet gjennom denne reviewen; de er spørsmål for separat research.
- Adversarial-linsen ber om minst ti punkter. Revieweren fant seks konkrete punkter; listen er ikke fylt med generiske forbedringsønsker.

## Adversarial

**A1 — Sammendraget, linje 16.** «Lovlig og mulig» står i konflikt med at full juridisk etterlevelse og flere arbeidstidskontroller er utenfor omfang. Presiser at kandidatene oppfyller de fire implementerte kravene i prototypen. Ellers kan regelkontrollen tolkes som fullstendig grunnlag for tildeling.

**A2 — Tilgjengelighet, linje 12–22 og Omfang.** De fire filtrene avklarer ikke annet fravær eller utilgjengelighet uten kolliderende vakt. Beskriv hvordan den ansatte som erstattes og andre utilgjengelige holdes utenfor grunnlaget. En tydelig forutsetning for fiktive testdata kan løse dette uten ny fraværsmodul. Ellers kan en regelmessig gyldig kandidat bli presentert som realistisk erstatter på feil grunnlag.

**A3 — Ansattpreferanser.** Tekster som «denne uken» har en gyldighetsperiode som ikke følger av poengkategorien. Avgrens preferansene til demonstrasjonsperioden, eller knytt dem eksplisitt til perioden for vakten. Ellers kan et tidligere ønske gi 0 eller 100 poeng på feil tidspunkt.

**A4 — Suksesskriterier.** At forklaringer finnes viser ikke at brukeren forstår dem. Legg til en liten oppgavebasert vurdering der en person velger erstatter og forklarer forskjellen mellom to kandidater, med kriterier bestemt på forhånd. Ellers kan alle funksjonspunktene bestås uten at brukerproblemet er løst.

**A5 — Suksesskriteriet for harde regler.** «100 % av regelbrudd filtreres bort» må suppleres med forventet gyldige kandidater som skal beholdes, inkludert grenseverdier. Ellers kan overfiltrering bestå det isolerte kriteriet. Dette er et forslag til sterkere akseptbevis, ikke en påstand om at prosjektets generelle krav til grensetester mangler.

**A6 — Problemet.** Arbeidspraksis og konsekvenser presenteres uten kilde eller tydelig merking som problemhypotese. Merk antakelsen eller lenk til relevant brukerinnsikt. Ellers fremstår behovet mer validert enn briefen viser. Fravær av dokumentert innsikt betyr ikke at problemet er motbevist.

## Edge-case

**E1 — PRD §4.4, referert fra Løsningen.** Én kandidat eller like verdier gir samme minimum og maksimum, mens endepunktene i poengskalaen er 100 og 0. Definer en felles poengverdi når maksimum = minimum, og test én kandidat. Ellers er modellen udefinert for en forventet situasjon.

**E2 — PRD §4.4, referert fra Løsningen.** Lik totalscore, særlig på femte/sjette plass, mangler en spesifisert sekundærsortering. Velg en stabil regel, eksempelvis kandidat-ID. Ellers er rekkefølgen og den første listen ikke entydig spesifisert.

**E3 — Ansattpreferanser / PRD §4.5.** En ugyldig eller mislykket live-tolkning av preferansen trenger en egen definert tilstand. Reservetekst for forklaringen fastsetter ikke kategori eller poeng. AD-1 beskriver lagret tolkning, og AD-6 gir demohåndtering, men løser ikke eksplisitt dette live-tilfellet. Avklar om siste gyldige tolkning brukes, rangering utsettes eller en merket standard brukes. Ellers mangler rangeringen gyldig input.

**E4 — Omfang / PRD §4.2.** Vakten kan ligge nær dataperiodens kant. Definer nødvendig dekning før og etter vakten og skill utilstrekkelig datagrunnlag fra bestått kontroll. Ellers kan manglende vakter behandles som fri. Dette gjelder hvilekontrollens datagrunnlag, og er en annen avklaring enn hvilket ukeintervall kostnad og belastning bruker.

## Struktur og språk

Dokumentet skal hjelpe prosjektgruppen og faglærer å forstå brukerbehovet, produktideen og avgrensningen av førsteversjonen. Strukturmodell: Strategic/Context (Pyramid). Innholdet er bevart; forslagene gjelder organisering og uttrykk.

| Pass | Original Text | Revised Text | Changes |
|---|---|---|---|
| structure | Hvem dette er for — 99 ord etter løsning og særpreg | MOVE etter Problemet, før Løsningen | Brukerens mål kommer før poengmodellen. Ordvirkning 0. |
| structure | Hva gjør dette annerledes — 94 ord | CONDENSE til ett avsnitt på ca. 40 ord med kombinasjonen av regler, kostnad, preferanser, forklaring og menneskelig valg | Anslått reduksjon 54 ord; behold at teknologien ikke hevdes unik. |
| structure | Omfang — 291 ord; avslutningen gjentar listene | CONDENSE siste avsnitt til: «Ansattportal og mer avansert autentisering/KI-funksjonalitet er mulige stretch goals når kjerneløsningen er ferdig og stabil.» | Anslått reduksjon 20 ord. Innlogging og autentiseringsavgrensning står allerede i listene. |
| structure | Kompetanseeksempel; Ansattpreferanser — 160 ord | PRESERVE eksempel, tabell og skillet mellom manglende og uttrykt nøytral preferanse | Konkrete holdepunkter hjelper menneskelige lesere selv om PRD også beskriver dem. Ordvirkning 0. |
| prose | «Faktorene får 0–100 poeng og vektes med henholdsvis 40 %, 35 % og 25 %, i samsvar med PRD §4.4.» | «Hver kandidat får 0–100 poeng for hver faktor. Poengene vektes med henholdsvis 40 %, 35 % og 25 %, i samsvar med PRD §4.4.» | Presiserer at poengene gjelder per kandidat; skiller faktorpoeng fra vekter. |

Fire strukturanbefalinger inkludert én uttrykkelig bevaring, og én språkpresisering. Strukturforslagene gir anslått reduksjon på 74 ord, ca. 4,5 % av 1 646, uten å kutte eksemplet eller tabellen. Språkforslaget legger til ni ord, slik at samlet anslått netto reduksjon blir 65 ord, ca. 3,9 %.

## Funn som maskinlesbare data

De ti innholdsfunnene er samlet i [product-brief-2026-10-26.json](product-brief-2026-10-26.json). Overlapp mellom begrepsavklaring og grensevilkår beholdes som forskjellige signaler; ingen funn er rangert eller gitt alvorlighetsgrad.

## Deep-recon — godkjent og gjennomført

Beslutningsspørsmål: Hvilke løfter, antakelser og begreper bør presiseres for at briefen skal gi et etterprøvbart grunnlag for v1, uten å utvide prototypen?

Foreslått type er domain, med begrenset kontroll av eksisterende løsninger. Tre uavhengige temaer gir breadth-first-topologi:

1. Arbeidstids- og hvilebegreper, datagrunnlag og skillet mellom regelmessig gyldighet, faktisk tilgjengelighet og ansattes aksept. Oppdatert primærkilde er nødvendig for juridiske påstander; det skal ikke gis råd om konkret bemanning i en reell virksomhet.
2. Dagens turnusverktøy: Hva finnes allerede av erstatningsforslag, kostnad, preferanser og forklaring? Skille leverandørens markedsføring fra dokumenterte funksjoner. Ingen markedsandel eller tidsbesparelse uten belegg.
3. Rangering og nytte: Vekting, skalering, preferansetolkning og menneskelig kontroll. Lete etter original forskning om beslutningsstøtte og testbar forståelse, og skille demonstrasjonsvalg fra dokumentert optimalitet.

Standard preset: opptil tre parallelle researchere, åtte kilder per tema per runde og to runder, normal validering med uavhengig kontroll av sentrale påstander. Åpne nettkilder er tilgjengelig søkeflate; ingen særskilt research-connector er funnet. Estimat 10–20 minutter. Ingen workflow-orchestrator er tilgjengelig; agentene kan kjøres direkte. Prosjektets dokumenter definerer spørsmålene, men brukes ikke som bevis for eksterne påstander. Kilder, digestfiler, memlog og rapport skal lagres under `_bmad-output/planning-artifacts/research/` etter godkjenning.

Brukeren godkjente planen med «start deep-recon» 2026-10-26. Kildeundersøkelsen er gjennomført i [researchrapporten](../research/domain-turnushjelperen-produktbrief-2026-10-26/research.md), med kildeutdrag, påstandsregister og ferskhetskontroll. Briefen er fortsatt uendret; researchanbefalinger er ikke automatisk vedtatte produktendringer.
