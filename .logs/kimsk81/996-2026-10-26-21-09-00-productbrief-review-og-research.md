# Vurdering og research av produktbriefen

## 2026-10-26 kl. 21:09 — Kimsk81

### Oppgave
Brukeren presiserte at `bmad-review` gjaldt produktbriefen og ba også om `bmad-deep-recon` av det som kommer frem i briefen.

### Plan
- Gjennomgå hele `product-brief.md` med adversarial-, edge-case-, struktur- og språklinsene. Sammenholde eksplisitte henvisninger med PRD og arkitektur for å unngå å etterlyse allerede spesifiserte detaljer.
- Bruke uavhengige reviewere slik review-skillen krever. Strukturresultatet går videre til språklinsen.
- Undersøke regler og kandidatbegreper, eksisterende løsninger og rangering/nytte etter godkjenning av deep-recon-planen. Skille eksternt kildebelegg fra prosjektets egne beslutninger.

### Resultat
Første milepæl ble lagret i `15bd5a4`: briefen, addendum, beslutningslogg, PRD, arkitektur, sensorveiledning og vurderingsmatrise ble lest. Briefen har 1 646 ord ifølge BMADs ordtellingsverktøy. Tre uavhengige reviewere vurderte innhold, grensevilkår og struktur; strukturrevieweren gjennomførte deretter den avhengige språklinsen.

Review er ferdig i [rapporten](../../../_bmad-output/planning-artifacts/reviews/product-brief-2026-10-26.md), med seks adversarial-funn, fire edge-case-funn, fire strukturanbefalinger (inkludert bevaring) og én språkpresisering. De ti innholdsfunnene finnes også som JSON. Triage skilte behov for sterkere kriterier fra påstander om feil i implementert kode; eksplisitte henvisninger ble kontrollert mot PRD og arkitektur. Ingen funn ble lagt til for å fylle adversarial-linsens tallkrav.

Funnene gjelder for bredt lovlighetsløfte, tilgjengelighet, tidsavgrensede preferanser, dokumentert brukerforståelse, positive regelkontroller og problemvalidering, samt like faktorverdier/poeng, mislykket live-tolkning og periodens datakanter. Åpne punkter er gruppert i `issues.md`. Eksisterende oppfølgingspunkt om kostnadsukens definisjon ble ikke duplisert; hvilekontrollens datadekning er et eget spørsmål.

Vurderingsmatrisen har fått lenke til reviewen som prosess- og kvalitetsbevis, uten at produktkrav eller brukerforståelse er merket som validert. Dette lukker ikke det tidligere punktet om bevis fra story 1.1.

Research-planen er konkretisert i rapporten og sendt til godkjenning: domain/explore, regler og kandidatbegreper, eksisterende verktøy og rangering/nytte; standard preset, opptil tre agenter, åtte kilder per tema/runde og to runder, normal kontroll. Planbekreftelse er ennå ikke mottatt. Deep-recon krever uttrykkelig «Present as a compact checklist, get approval» i `.agents/skills/bmad-deep-recon/references/run.md`. Ingen nettresearch eller påstander om eksternt kildebelegg er derfor utført, og researchdelen gjenstår. Dette er oppgavestatus, ikke et nytt produktproblem i issues-listen.

Kvalitetssikring: innholdsfunnsfilen parses som JSON og inneholder seks pluss fire funn. `git diff --check` bestod; `git diff -- product-brief.md` er tom. Ingen kode eller tester ble endret. Konfigurasjonslesere og ordtelling ble kjørt med godkjent eskalering etter at uv ble blokkert i sandkassen. Rapporten og vurderingsmatrisen lagres i arbeidstreet; bare logg og issues inngår i lokal loggcommit. Den fra før stagede smoketestfilen holdes utenfor.

### Åpne punkter
- Avklar briefens lovlighetsløfte, tilgjengelighetsforutsetninger og preferansenes gyldighetsperiode (A1–A3).
- Avklar like faktorverdier og poeng, feil i live-preferansetolkning og datadekning for hvilekontroll (E1–E4).
- Styrk belegg og akseptkriterier for brukerproblem, forståelse og positive regelkontroller (A4–A6).

## 2026-10-26 kl. 21:49 — Kimsk81

### Oppgave
Brukeren godkjente den konkrete planen med «start deep-recon». Fortsettelsen fullfører kildeundersøkelsen som reviewen ventet på. Etter leveransen ba brukeren: «Commit og push det vi har gjort»; publiseringen er dokumentert nederst i resultatet.

### Plan
- Opprette et deterministisk navngitt research-område, rapportutkast og memlog med den godkjente planen.
- La tre researchere undersøke regler/tilgjengelighet, eksisterende verktøy og rangering/brukernytte med primærkilder. Researcherne fikk avgrensede oppdragsbriefer og ingen prosjektfiler som eksternt bevis.
- Kontrollere sentrale regel- og forskningspåstander med egne verifikatorer, følge opp Planday-friskheten i én målrettet andre runde, og gjennomføre semantisk kildeaudit og redaksjonell struktur-/språkkontroll.
- Lagre anbefalinger, kildeutdrag, ferskhetskart og en selvstendig HTML-visning uten å vedta produktendringer.

### Resultat
[Researchrapporten](../../../_bmad-output/planning-artifacts/research/domain-turnushjelperen-produktbrief-2026-10-26/research.md) er fullført med [HTML-visning](../../../_bmad-output/planning-artifacts/research/domain-turnushjelperen-produktbrief-2026-10-26/research-briefing.html). Samme mappe har seks research-/verifikasjonsdigester, en semantisk audit, `.memlog.md`, `claims.json`, `staleness.json` og verktøyets escaped kildetabell. Rapporten refererer 18 kilder. Tre av ti registrerte nøkkelpåstander er uavhengig bekreftet; sju beholdes som uverifisert i strengere forstand, blant annet aktuelle leverandørfunksjoner og overføring av metode/studier. Dette er ikke en kvalitetsprosent for produktet.

Kildene støtter å beholde skoleprototypens omfang og presisere løftene: 11/35 er hovedregler med unntak, 36 timer og faktor 1,5 er scenarioforutsetninger, tilgjengelighet er ikke det samme som modellgyldighet, og eksisterende verktøy dokumenterer allerede forslag/forklaringer. Ingen empirisk gevinst i norsk bemanning er dokumentert. Vektene 40/35/25 er ikke eksternt validert. Ingen konkret tariff- eller full betalingsrett er avgjort.

Et eget syntetisk regneeksempel ble verifisert direkte med JavaScript: A/B har totalscore 52,5/47,5; når C tilkommer, får A/B/C 52,5/83,5/35. Den nye kandidaten er sist, men min–maks-skalaen endrer A/B-rekkefølgen. Dette bryter ikke determinismen; det er en modelloppførsel gruppen bør ta stilling til og teste. Eksisterende oppfølgingspunkt om rangering er utvidet med dette, uten nytt duplikatpunkt.

Kildeaudit åpnet alle 18 referanser og fant ingen vesentlig feilattribusjon. Etiketten over originalstudiene ble presisert: korrekt gjengivelse er ikke uavhengig replikasjon. Nullfunn og CheckList-retningstester er gjengitt med eksplisitte begrensninger. Redaksjonell kontroll flyttet anbefalingstabellen frem, fjernet gjentatt hentedato fra tabellen og presiserte to formuleringer. Planday-kilden fra 22. juli ligger utenfor tremånedersvinduet; andre runde ga ikke ferskere uavhengig bekreftelse. Fristen 22. oktober er ført som allerede forfalt; neste daterte funksjonsfrist er Quinyx 6. november. Regulatoriske påstander må kontrolleres ved ny anvendelse, og udaterte kilder har ingen oppdiktet publiseringsdato.

Maskinkontroller: `citations` bestod med alle 18 henvisninger og ingen manglende/ubrukte kilder. `tally` ga 3 verified og 7 unverified; `staleness` ga forventet exit 1 for én for gammel funksjonsbeskrivelse. HTML-kontroll avdekket først skadet norsk tekst ved stdout-overføring; eksplisitt UTF-8 rettet feilen. Sluttkontroll: null manglende Markdown-linjer i HTML, null manglende ankermål, 18 kildeankre, null eksterne ressurser og ingen erstatningstegn. `git diff --check` bestod. HTML er ikke visuelt kontrollert i nettleser. Ingen app-tester, live modellkall eller brukerprøver ble kjørt.

Vurderingsmatrisen lenker nå til ferdig research og [KI-loggen](../../../docs/ki-logg/2026-10-26-productbrief-review-research.md). Reviewrapportens ventestatus er erstattet med den gjennomførte undersøkelsen. Brief, PRD, arkitektur, vekter og implementasjonsstatus er uendret. Tidligere punkt om bevis fra story 1.1 er ikke løst av denne dokumentgjennomgangen. Ved researchleveransen lå rapportene og matrisen i arbeidstreet; bare sesjonslogg og issues inngikk i loggcommiten, og ingenting var pushet da.

Neste dokumentsteg etter BMADs hjelpekatalog er å behandle aksepterte presiseringer med `bmad-product-brief` i en ny kontekst, deretter eventuelle konkrete PRD-presiseringer med `bmad-prd`. Det er en anbefaling, ikke en automatisk igangsatt endring av godkjent plan eller krav.

#### Commit og push etter brukerens bestilling

Etter `git fetch origin` var `main` null commits bak og fem loggcommits foran `origin/main`. De 17 filene fra dokumentarbeidet ble committet som `21453f4` — «Dokumenter review og kildeundersøkelse av produktbriefen». Commit-brødteksten forklarer hvorfor den tidligere vurderingsmatrisen oppdateres, og dokumenterer rettingen av generert HTML og presiseringen etter kildekontroll. Fire JSON-filer ble parset på nytt; arbeids- og staged diffkontroll bestod. Ingen apptester ble kjørt for denne dokumentasjonscommiten.

`git push origin main` lyktes og flyttet GitHub-grenen fra `5b2c1ec` til `21453f4`, inkludert de fem tidligere lokale loggcommittene. Den allerede stagede `docs/ki-logg/modelltest-resultater/gpt6-luna-smoke-20261016T204001529213Z.json` var fra før dette dokumentarbeidet og ble holdt utenfor med eksplisitt path-begrenset commit; den forblir staget. Ingen andre arbeidsendringer gjensto. Denne loggoppdateringen committes separat og pushes som del av samme bestilling. `issues.md` er kontrollert og har ingen nye eller løste produktpunkter fra publiseringen.

### Åpne punkter
- De tre eksisterende reviewgruppene i `issues.md` gjenstår: begreper/forutsetninger, grensevilkår/modelloppførsel og lokal validering/testbevis. Ingen av dem er løst bare ved ekstern research.
