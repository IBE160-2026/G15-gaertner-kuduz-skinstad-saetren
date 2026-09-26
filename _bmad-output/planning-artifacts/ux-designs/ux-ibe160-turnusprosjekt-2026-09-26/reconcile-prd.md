---
title: "Reconciliation: UX spine (DESIGN.md/EXPERIENCE.md) vs. PRD"
created: 2026-09-26
scope: >
  Cross-check of DESIGN.md and EXPERIENCE.md against prd.md (FR-1..FR-13,
  §3 Ordliste, §5 Ikke-mål, UJ-1). Method: read all three source files in full,
  mapped each FR to its IA row / Component Pattern / State Pattern, checked
  every §5 non-goal against DESIGN/EXPERIENCE claims, and diffed glossary
  terms against the vocabulary actually used in the UX spine.
---

# Reconciliation: UX spine vs. PRD

## 1. FR coverage matrix

| FR | Krav | Representert i UX? | Hvor |
|---|---|---|---|
| FR-1 | Velge vakt | Ja | IA "Vaktvalg"; Component "Varselboks"; Key Flow steg 1–3 |
| FR-2 | Filtrer kompetanse-minstekrav | Ja | Component "Ekskludert-boks" (eksempel: "9 under kompetanse-minstekrav") |
| FR-3 | Filtrer kolliderende vakt | Ja | Component "Ekskludert-boks" (eksempel: "7 kolliderende vakt") |
| FR-4 | Filtrer 11-timersregelen | Delvis — se Gap 1 | Kun nevnt generisk i Key Flow-prosa ("hviletids-/arbeidstidsregler"), ikke som egen kategori i Ekskludert-boks-eksempelet eller State Patterns |
| FR-5 | Filtrer 35-timersregelen | Delvis — se Gap 1 | Samme som FR-4: slått sammen med FR-4 i generisk frase, ikke egen kategori |
| FR-6 | Vise "ingen gyldige kandidater" | Ja, godt dekket | State Patterns rad 1; Voice and Tone; DESIGN "empty-state" |
| FR-7 | Forenklet kostnad per kandidat | Ja | Component "Kostnadsindikator" |
| FR-8 | Vise arbeidsbelastning | Ja | Component "Arbeidsbelastningslinje" |
| FR-9 | Rangere gyldige kandidater | Ja (hovedmekanikk); kompetansenærhet-tiebreak ikke synlig — se Gap 4 | Component "Rangeringstabell", "rank-badge" |
| FR-10 | Tolke tekstbaserte ansattpreferanser | Ja | Component "Tag" (preferanse-kolonne), Rangeringstabell |
| FR-11 | Generere forklaring per kandidat | Ja, godt dekket inkl. feilhåndtering | Component "Forklaringsrad/-panel"; State Patterns rad "KI-forklaring feilet/tom/ubrukelig" |
| FR-12 | Godkjenne valgt kandidat | Ja, godt dekket | IA "Godkjenning"; Component "Bekreftelsesboks", "Avviksnotat"; Interaction Primitives |
| FR-13 | Logge inn | Ja | IA "Logg inn"; Component "Innloggingsskjema"; DESIGN "login-card" |

## 2. Non-goal (§5) check

Gjennomgått alle ni punkter i §5 mot DESIGN.md/EXPERIENCE.md. **Ingen direkte motsigelser funnet.** Spesifikt verdt å merke (som styrker, ikke svekker, samsvaret):

- EXPERIENCE.md Interaction Primitives noterer eksplisitt at automatisk SMS-/varslingsutsendelse ble "foreslått og deretter trukket tilbake" — viser bevisst årvåkenhet mot scope-kryp, ikke en selvmotsigelse.
- Ingen sidemeny/fanenavigasjon, kun én vakt om gangen i flyten — konsistent med "ikke håndtere flere turnusendringer samtidig" og "ikke generere en full turnus".
- Fiktive navn (Kari, Ingrid Dahl, Jonas Bakke, Silje Amundsen, Mette Solberg) — konsistent med "ingen ekte personopplysninger".
- Ett-rolle-system (kun Turnusansvarlig logger inn) — konsistent med "ingen full ansattportal, ingen avansert rollebasert autentisering".
- To-stegs Godkjenning med eksplisitt statuslinje "ikke gjennomført" — konsistent med "ikke automatisk gjennomføre KI-forslag uten Godkjenning".

## 3. Terminologi vs. §3 Ordliste

| PRD-term | Brukt i UX-spine? | Merknad |
|---|---|---|
| Vakt, Kandidat, Gyldig kandidat, Turnusansvarlig, Rangering, Godkjenning | Ja, konsekvent | Ingen drift |
| Kompetansenivå | Delvis | DESIGN.md bruker "kompetansenivå-tekst" én gang (Tag-komponent); IA-tabellen og Component Patterns bruker gjennomgående forkortet "kompetanse" — se Gap 5 |
| Ansattpreferanse | Forkortet til "preferanse" gjennomgående | Lav risiko, meningen er uendret |
| Myk faktor | Ikke brukt som term noe sted | Internt PRD-begrep; sannsynligvis ikke ment å være brukervendt tekst, lav risiko |
| Hard regel | Ikke brukt som term (kun beskrevet ved atferd: filtrering, "utelukket") | Samme som over — sannsynligvis internt begrep, lav risiko |
| **Avveining** | **Ikke brukt noe sted** | PRD §3 definerer "Avveining" spesifikt som *KI-generert forklaring av hvorfor én Kandidat rangeres over en annen*. UX-spinen bruker konsekvent "begrunnelse"/"forklaring"/"explain-panel" for nøyaktig dette konseptet, uten noen gang å bruke ordet «Avveining» — se Gap 2 |

## 4. Gaps

### Gap 1 — FR-4/FR-5 ikke representert som egne ekskluderingskategorier
**Severity: Medium**
**PRD-passasje:** FR-4 (§4.2, 11-timersregelen) og FR-5 (§4.2, 35-timersregelen) er to separate, testbare Harde regler med egne "Konsekvenser (testbare)"-avsnitt.
**Mangler i UX:** EXPERIENCE.md Component Patterns' "Ekskludert-boks"-rad og eksempelteksten ("9 under kompetanse-minstekrav · 7 kolliderende vakt", gjentatt i DESIGN.md) viser kun FR-2 og FR-3 som eksplisitte utelukkelseskategorier. FR-4 og FR-5 nevnes kun samlet og generisk i Key Flow-prosaen ("eller som ville brutt hviletids-/arbeidstidsregler") — aldri som egen kategori i noen Component- eller State Pattern-tabell. Risiko: en utvikler som bygger Ekskludert-boksen fra spine-tabellene alene kan ende med kun to kategorier i stedet for fire.

### Gap 2 — Glossary-begrepet «Avveining» mangler helt i UX-spinen
**Severity: Medium**
**PRD-passasje:** §3 Ordliste: "**Avveining** — KI-generert forklaring av hvorfor én Kandidat rangeres over en annen."
**Mangler i UX:** Verken DESIGN.md eller EXPERIENCE.md bruker ordet «Avveining» noe sted, til tross for at dette er det navngitte PRD-begrepet for nøyaktig det konseptet UX-spinen kaller "KI-begrunnelse"/"forklaring"/`explain-panel`. Dette er ikke en funksjonell motsigelse (samme atferd er beskrevet), men en navnedrift mellom PRD og UX som kan gi inkonsistent navngivning videre i arkitektur/kode (f.eks. felt/komponentnavn som ikke gjenkjennes mot PRD-ordlisten).

### Gap 3 — Ekskludert-boks-eksempel dekker ikke alle fire regler samtidig
**Severity: Low** *(relatert til Gap 1, men separat observasjon)*
**PRD-passasje:** §4.2, MVP-omfang §6.1: "Filtrering av Kandidater på fire Harde regler."
**Mangler i UX:** Selv som illustrativt eksempel demonstrerer verken DESIGN.md eller EXPERIENCE.md et scenario med alle fire regel-kategoriene samtidig utelukket, noe som gjør det vanskeligere å verifisere at UX-designet faktisk er tenkt til å skalere til fire kategorier fremfor to.

### Gap 4 — FR-9s kompetansenærhet-tiebreak er ikke synlig i UX-spinen
**Severity: Low**
**PRD-passasje:** FR-9, andre testbare konsekvens: "Når ingen Gyldig kandidat har full kvalifisering for vakttypen, rangeres Kandidaten med Kompetansenivå nærmest full kvalifisering høyere enn de som er lenger unna..." (Jonas-eksempelet).
**Mangler i UX:** Component Patterns og State Patterns nevner en generisk "kompetanse (+ tag)"-kolonne, men ingen egen tilstand/komponentregel for scenarioet "ingen kandidat er fullt kvalifisert, nærmeste vinner". Dette er en ren rangeringsalgoritme-detalj, så det er rimelig at UX ikke viser en egen tilstand for den — men siden PRD eksplisitt gir den et testbart, illustrert eksempel, er fraværet verdt å notere som lav-alvorlighets sporingshull, ikke en motsigelse.

### Gap 5 — "Kompetansenivå" forkortes gjennomgående til "kompetanse"
**Severity: Low**
**PRD-passasje:** §3 Ordliste definerer "Kompetansenivå" som presist begrep (delvis opplært → fullt kvalifisert).
**Mangler i UX:** IA-tabellen og Component Patterns-tabellen i EXPERIENCE.md bruker konsekvent den forkortede formen "kompetanse" fremfor "Kompetansenivå". DESIGN.md bruker riktig form kun én gang (i Tag-komponentens beskrivelse). Ren navnedrift, ingen semantisk endring.

## 5. Konklusjon

Ingen kritiske eller høy-alvorlighetsgap funnet. Alle 13 FR-er har en identifiserbar representasjon i IA/Component Patterns/State Patterns, og ingen del av DESIGN.md eller EXPERIENCE.md motsier et §5 Ikke-mål. De fem gapene som er funnet er alle av typen "underspesifisert" eller "navnedrift" (medium/low), ikke motsigelse av funksjonalitet — dvs. UX-spinen er i det store og hele et tro, men ikke fullstendig presist, derivat av PRD-en.
