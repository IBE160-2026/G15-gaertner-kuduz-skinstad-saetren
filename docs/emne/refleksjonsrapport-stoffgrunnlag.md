# Stoffgrunnlag for refleksjonsrapporten

Dette er ikke refleksjonsrapporten. Dokumentet samler fakta, eksempler og kilder fra
repoet, ordnet etter seksjonene i [malen](refleksjonsrapport-mal.md), slik at gruppa kan
skrive rapporten selv. Refleksjonene, vurderingene og meningene skal komme fra gruppa.

- Refleksjonsrapporten teller 30 % av karakteren, og del 1 (repoet) teller 70 %
  ([sensorveiledning-del-1.md:368-369](sensorveiledning-del-1.md)). Del 1 vurderer
  sporene av prosessen, og refleksjonen over prosessen vurderes i rapporten (linje 89).
- Malen ber om 3000–5000 ord. Den har plass til tre medlemmer, men vi er fire.
- Tallene er hentet fra repoet 2026-11-23. Tall fra en logg gjelder datoen i loggen.
- «Eksempel» betyr at noe har skjedd og er dokumentert. Hva det betyr, og om det var
  bra eller dårlig, er gruppas vurdering.
- Seksjon 4 og 5 har bare eksempler og spørsmål å ta stilling til. Seksjon 7 har bare
  kilder.

## Nøkkeltall

| Hva | Tall | Kilde |
|---|---|---|
| Prosjektperiode i repoet | 07.09.2026 (første commit) til 23.11.2026 | `git log` |
| Commits på `main` | 712 | `git rev-list --count HEAD` |
| PR-er | 38 (#1–#39, #26 er ikke en PR), alle merget unntatt PR #38 (5.7, åpen) | `gh pr list --state all` |
| Stories | 30 i fem epics, 27 ferdige (5.7 er i PR, 5.8 og 5.9 står i backlog) | [sprint-status.yaml](../../_bmad-output/implementation-artifacts/sprint-status.yaml) |
| KI-logger | ca. 55 filer i `docs/ki-logg/`, fra 15.10 til 23.11 | [docs/ki-logg/](../ki-logg/) |
| Sesjonslogger | Kim 44, Johannes 29, Ragnhild 24, Mithad 22 | `.logs/<bruker>/` |
| Backendtester | 842 bestått 23.11 | [2026-11-23-loggoppsett-backend.md](../ki-logg/2026-11-23-loggoppsett-backend.md) |
| Frontendtester | 52 modultester og 66 komponenttester 22.11 | [2026-11-22-progressiv-lasting.md](../ki-logg/2026-11-22-progressiv-lasting.md) |

Antall commits per person sier lite om hvor mye hver enkelt har bidratt, fordi
loggcommits og små rettelser teller like mye som store stories. Bruk heller hvem som
eide hvilke stories og PR-er (tabellen under 2.2).

---

## 2. Utviklingsprosessen

### 2.1 Oversikt over prosjektet

- Turnushjelperen er beslutningsstøtte for en turnusansvarlig som må bemanne én vakt
  på nytt. Harde regler filtrerer bort ugyldige kandidater, en enkel modell rangerer de
  gyldige, og KI forklarer avveiningene. Se [product-brief.md](../../product-brief.md)
  og første avsnitt i [AGENTS.md](../../AGENTS.md).
- De fire harde reglene er kompetanse-minstekrav, kolliderende vakt, 11-timersregelen
  og 35-timersregelen. Lovgrunnlaget står i
  [addendum.md](../../_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/addendum.md)
  (aml. kap. 10).
- Grunnprinsippet var at KI aldri skal beregne harde regler, arbeidstid eller kostnad,
  fordi resultatet må kunne gjenskapes (Policy i AGENTS.md). KI tolker bare
  preferansetekster og forklarer avveininger mellom kandidater regelmotoren allerede
  har godkjent.

### 2.2 Arbeidsmetodikk

**Fordeling.** Hvem som laget PR-ene (fra `gh pr list`):

| Person | PR-er |
|---|---|
| Kim | 8 (1.4), 11 (1.6), 12 (PRD-samordning), 21 (arkitekturgjennomgang), 23 (3.2), 24 (4.7), 28 (4.3), 33 (5.1 Prøv igjen), 35 (5.3), 37 (5.4), 39 (5.5) |
| Johannes | 2 (modellvalg), 6 (skills-speiling i CI), 7 (1.3), 9 (CI), 13 (2.1), 14 (2.2), 16 (3.1), 20 (komponenttester), 29 (4.4), 32 (4.6) |
| Mithad | 3 (1.1), 5 (1.2), 10 (1.5), 15 (2.3), 18 (PRD etter Bårds tilbakemelding), 19 (2.5), 30 (5.1), 31 (4.5), 34 (5.2), 38 (5.7) |
| Ragnhild | 1 (epics og stories), 4 (ÅB-3 og story 4.7), 17 (2.4), 22 (2.6), 25 (4.1), 27 (4.2), 36 (5.6) |

Planleggingsdokumentene ble påbegynt slik: brief av Kim 16.09, PRD og UX av Mithad
26.09, arkitektur av Mithad 29.09 og epics av Ragnhild 29.09 (første commit per fil i
`git log`).

**Regler for samarbeid** (alle i [AGENTS.md](../../AGENTS.md), Policy):

- Branch og PR er et aktivt valg. Små rettelser kan gå rett på `main`, mens større
  avgjørelser går i PR, slik at et annet gruppemedlem ser over. Dette ble vedtatt i
  PR #6.
- Gruppevedtak føres sporbart i
  [avklaringspunkter.md](../beslutninger/avklaringspunkter.md) med ID-er (AV-, K-, OP-
  og KS-). Referatet startet etter gruppemøtet 02.11 (AV-08).
- Alle fører sesjonslogg i `.logs/<bruker>/` med en egen liste over åpne punkter
  (`issues.md`).
- CI kjører tre workflows på hver push, men rød CI blokkerer ikke merge. Det er et
  bevisst valg (PR #9).

**Verktøy for samarbeid:** GitHub (PR-er, gjennomgang, Actions), git og
sesjonsloggene. Det står ikke i repoet hvilken chat eller hvilke møter gruppa brukte.
Det må gruppa fylle inn selv.

**KI i prosessen:**

- Claude Code (Opus 5.5) og Codex ble brukt side om side. Skillene ligger i både
  `.claude/skills/` og `.agents/skills/`, og en test i CI kontrollerer at de er like
  ([2026-11-06-skills-speiling.md](../ki-logg/2026-11-06-skills-speiling.md)).
  Beslutningsreferatet ble utarbeidet med Codex (§1 i referatet).
- BMAD ble brukt for planlegging (brief, PRD, UX, arkitektur, epics) og bygging
  (`bmad-build`).
- `bmad-build` kjøres med underagenter. Én samler konteksten, én implementerer, og tre
  egne agenter (Blind Hunter, Edge Case Hunter og Verification Gap) går gjennom koden
  uten å ha sett implementeringen. Vedtatt som OP-04 04.11.
- [docs/modellvalg-stories.md](../modellvalg-stories.md) anbefaler en modell per
  story. Gruppa har ikke drøftet den ennå (åpent punkt hos Johannes).

### 2.3 Teknologi og verktøy

| Del | Valg | Kilde |
|---|---|---|
| Frontend | React og TypeScript med Vite, testet med node:test, Vitest, Testing Library og jsdom | AGENTS.md, PR #20 |
| Backend | Python 3.12+ med FastAPI | AGENTS.md |
| Database | SQLite via SQLAlchemy, med fiktive testdata | AGENTS.md, story 1.2 |
| KI i produktet | OpenRouter med `openai/gpt-6-luna`, valgt 16.10 etter tre modelltester. Haiku 5.5 var valgt før det. | [2026-10-16-robusthet-luna.md](../ki-logg/2026-10-16-robusthet-luna.md) |
| KI i utviklingen | Claude Code (Opus 5.5), Codex | KI-loggene |
| Andre verktøy | BMAD v6.12.0, VS Code, GitHub Actions, import-linter, nettleserkontroll med skript og skjermbilder | `git log`, [docs/testing.md](../testing.md) |

### 2.4 Utviklingsfaser

**Fase 1: Planlegging (07.09–ca. 19.10)**

- Brief → PRD → UX → arkitektur → epics og stories, alt med BMAD-skills. Filene ligger
  i [_bmad-output/planning-artifacts/](../../_bmad-output/planning-artifacts/).
- Grunnlaget for briefen ble gjennomgått mot research
  ([2026-10-26-productbrief-review-research.md](../ki-logg/2026-10-26-productbrief-review-research.md)).
- Endringsforslaget 14.10 ([sprint-change-proposal-2026-10-14.md](../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-14.md))
  la til demo-modus, sensornøkkel og story 5.7–5.8 (BMAD «correct course»).
- Modellvalget ble gjort med tre tester (15.–16.10), med beslutningsregler som var
  bestemt før kjøringen:
  1. Haiku alene ([2026-10-15-modelltest-haiku.md](../ki-logg/2026-10-15-modelltest-haiku.md))
  2. Sammenligning av Haiku, Luna, Mistral og Gemma ([2026-10-15-modellsammenligning.md](../ki-logg/2026-10-15-modellsammenligning.md))
  3. Beslutningstest Haiku mot Luna, 255 kall per kjøring ([2026-10-16-beslutningstest-haiku-luna.md](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md))
  4. Robusthetstest av Luna ([2026-10-16-robusthet-luna.md](../ki-logg/2026-10-16-robusthet-luna.md))
- Gruppemøtet 02.11 behandlet PR #4 og story 1.2 og ga AV-01–AV-12
  ([avklaringspunkter.md](../beslutninger/avklaringspunkter.md) §2–3).
- Faglærer Bård ga tilbakemelding på PRD-en 12.11
  ([tilbakemelding-prd.md](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/tilbakemelding-prd.md)),
  og PRD-en ble rettet i PR #18.
- **Prompter fra planleggingen:** Malen ber om alle stegene. KI-loggene starter
  15.10. Promptene fra brief, PRD og UX i september må gruppa finne i egne notater
  eller i `.memlog.md`-filene i mappene under `planning-artifacts/`. Sjekk dette.

**Fase 2: Utvikling (19.10–nå)**

- Epic 1 (oppsett, testdata, innlogging, vaktoversikt) → epic 2 (de fire harde
  reglene) → epic 3 (godkjenning) → epic 4 (rangering, kostnad, belastning, ulempe) →
  epic 5 (KI-tolkning og forklaring).
- Hver story har en spesifikasjon i
  [implementation-artifacts/](../../_bmad-output/implementation-artifacts/) med
  `Review Triage Log`, altså hva gjennomgangen fant og hva som ble gjort med hvert funn.
- Hver story med KI-kode har en KI-logg med oppgaven, prompten, hva modellen leverte,
  hva som ble rettet og hvordan resultatet er kvalitetssikret.
- Eksempel på en hel prompt ordrett: gjennomgangen av PR #34 i
  [2026-11-20-rangering-tolkede-preferanser.md](../ki-logg/2026-11-20-rangering-tolkede-preferanser.md)
  («hent siste endringer fra repoet. Start gjennomgang av PR 34 …»).

---

## 3. Utfordringer og løsninger

### 3.1 Tekniske utfordringer (kandidater, velg 2–3)

**A. Tid, sommertid og tidssoner**
- Problem: Testdataene lagret lokal tid (+02:00/+01:00), så sortering i SQL ville gått
  feil over sommertidsskiftet. Senere viste det seg at flere regler regnet på
  «veggklokka» i stedet for faktisk tid.
- Løsning: Lagre i UTC og lese i Europe/Oslo. Tester for vår- og høstskiftet.
  Mutasjonstester viste at testene faktisk fanger en fjernet UTC-omregning.
- KI sin rolle: Den uavhengige gjennomgangen fant feilen i testdataene. For
  kolliderende vakt viste gjennomgangen at sommertidstestene i første utkast ikke
  beviste noe, fordi de ga samme svar uansett.
- Kilder: [2026-11-03-testdata.md](../ki-logg/2026-11-03-testdata.md),
  [2026-11-11-kolliderende-vakt.md](../ki-logg/2026-11-11-kolliderende-vakt.md),
  [2026-11-11-11-timersregelen.md](../ki-logg/2026-11-11-11-timersregelen.md),
  [2026-11-11-35-timersregelen.md](../ki-logg/2026-11-11-35-timersregelen.md).

**B. Grensen på 20 KI-kall per minutt hos OpenRouter**
- Problem: I robusthetstesten feilet 63 av 340 kall med 429. Kontoen hadde en grense
  på 20 Luna-kall per kalenderminutt.
- Løsning: En begrenser på klientsiden (høyst 18 kall per 60 s og 5 samtidige),
  tolkning i bakgrunnen og forklaringer som lages først når de åpnes. Dette ble
  arkitekturkrav AD-7.
- KI sin rolle: Testen og analysen av feilsvarene ble gjort med KI. Resultatet ble
  styrende for arkitekturen.
- Kilde: [2026-10-16-robusthet-luna.md](../ki-logg/2026-10-16-robusthet-luna.md),
  iterasjon 1 og 2.

**C. Transaksjoner i SQLite**
- Problem: Når en vakt godkjennes, må appen oppdage at grunnlaget har endret seg siden
  skjermen ble åpnet (P-09). Oppførselen hviler på standardinnstillingene i Pythons
  `sqlite3`, og andre innstillinger får `BEGIN` til å feile.
- Kilde: «Kjente fallgruver» i [AGENTS.md](../../AGENTS.md) og docstringen til
  `lag_engine` i `backend/adaptere/lagring/database.py`.

**D. Frontendtester som feilet på trege maskiner**
- Problem: Fire testkjøringer samtidig feilet med tidsavbrudd på riktig kode.
- Løsning: `maxWorkers: 1` etter målinger av RAM og CPU.
- KI sin rolle: Implementeringsagenten rapporterte 12 av 12 bestått i fire samtidige
  kjøringer. Da koordinatoren sjekket, feilet de fortsatt. Johannes ba om at RAM og CPU
  skulle måles, og det førte til løsningen.
- Kilde: [2026-11-14-komponenttester.md](../ki-logg/2026-11-14-komponenttester.md),
  «Trege maskiner og tidsavbrudd» i [docs/testing.md](../testing.md).

**E. Tabellen på smale skjermer (story 4.6)**
- Problem: Målingen ble gjort uten rullefelt i nettleseren. Med et vanlig rullefelt
  gled en kolonne 11 px inn under en annen.
- Kilde: [2026-11-19-smale-skjermer.md](../ki-logg/2026-11-19-smale-skjermer.md), som
  også viser hvordan Mithad fant feilen i PR #32.

### 3.2 Samarbeidsutfordringer

- **Flettekonflikter:** Når flere stories ble merget nær hverandre, kolliderte de i
  felles filer som `sprint-status.yaml`, `avklaringspunkter.md` og
  `vurderingsmatrise.md`. Se «Sammenslåing» i
  [2026-11-12-godkjenningsflaten.md](../ki-logg/2026-11-12-godkjenningsflaten.md) og
  konflikten i PR #12.
- **Regler som ble endret underveis:** Regelen «behold AGENTS.md og loggreglene
  uendret» (AV-08) fikk to unntak på tre dager og ble erstattet 08.11, fordi den
  hindret vanlig vedlikehold (AV-08 i referatet).
- **Ulike operativsystemer:** Gruppa testet først og fremst på Windows (sensor har
  ikke Mac), mens Ragnhild har Mac (OP-05). `npm` stoppes av PowerShell, og
  tegnkodingen ble feil i Windows-tester
  ([2026-11-06-innlogging.md](../ki-logg/2026-11-06-innlogging.md)).
- **Koordinering av avhengige stories:** Story 1.2 og story 4.7 trengte samme
  testdata (ÅB-3). Testdataene måtte koordineres med den som hadde branchen.
- **Gruppevedtak tar tid:** Valgene i
  [avklaringsrunde-2026-11-22.md](../beslutninger/avklaringsrunde-2026-11-22.md)
  (versjonslåser, 5.9, sensornøkkel) står delvis åpne.
- **Felles kvote:** Alle delte samme OpenRouter-konto og grensen på 20 kall per
  minutt, så live-tester kunne ikke kjøres samtidig (AGENTS.md).
- **Test med en person utenfor gruppa (P-13):** Gruppa hadde ikke en testperson,
  ifølge sprintstatus 22.11 og Ragnhild 23.11.

### 3.3 KI-spesifikke utfordringer

- **Regnefeil og antagelser i KI-utkast:** Et regneeksempel viste «136 p», men
  22 + 2 × 21 + 3 × 29 = 151. Agenten kontrollerte ikke summen. Agenten skrev også inn
  egne vakttider som ga overlappende vaktskifter (K-01,
  [2026-11-02-ab-3-ulempebelastning.md](../ki-logg/2026-11-02-ab-3-ulempebelastning.md)).
- **Kontekst som forsvant:** Da `epic-5-context.md` ble laget på nytt, manglet omtrent
  15 bindende detaljer fra forrige versjon
  ([2026-11-20-rangering-tolkede-preferanser.md](../ki-logg/2026-11-20-rangering-tolkede-preferanser.md)).
- **KI-agenter som sa seg ferdige for tidlig:** Agenten rapporterte at testene besto
  når de ikke gjorde det (3.1 D). AGENTS.md førte story 5.2 som ferdig før merge
  (samme logg som over).
- **Feil henvisninger:** Spesifikasjonen for 5.2 siterte feil eller ufullstendige
  bevis for tre akseptansekriterier, blant annet feil antall kjøringer (samme logg).
- **KI i produktet:** Haiku brukte «hun» om ansatte uten grunnlag. Gemma fant på egne
  kategorier. Haiku tolket «ønsker ikke flere» som «færre». Se
  [2026-10-15-modellsammenligning.md](../ki-logg/2026-10-15-modellsammenligning.md) og
  [2026-10-16-beslutningstest-haiku-luna.md](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md).
- **Mottiltak som ble innført:** faktakontroll av KI-forklaringen (story 5.3),
  reservetekst når KI feiler (5.4), en test av at utelukkede kandidater aldri når
  KI-laget (5.6), begrenseren (AD-7) og falsk OpenRouter i alle tester.

---

## 4. Kritisk vurdering av KI sin påvirkning: eksempler

Dette er eksempler å ta stilling til. Hva dere mener om dem, skriver dere selv.

### 4.1 Mulige fordeler

- **Tempo:** 27 stories, 842 backendtester og over 100 frontendtester på ca. fem uker
  med koding (19.10–23.11). Hvor mye av dette som hadde vært mulig uten KI, er et
  spørsmål for 4.3.
- **Gjennomgang som fant reelle feil:** Eksempler der de uavhengige
  gjennomgangsagentene fant noe implementeringen hadde oversett:
  - Innloggingen: 25 funn, 13 rettet, 1 utsatt og 11 avvist med begrunnelse
    ([2026-11-06-innlogging.md](../ki-logg/2026-11-06-innlogging.md)).
  - Vaktoversikten: 10 mangler, alle rettet
    ([2026-11-08-vaktoversikt.md](../ki-logg/2026-11-08-vaktoversikt.md)).
  - En nøkkel med ugyldige tegn kunne havne i loggen
    ([2026-11-16-preferansetolkning.md](../ki-logg/2026-11-16-preferansetolkning.md)).
- **Mutasjonstesting som metode:** Koden ble bevisst ødelagt for å se om testene ble
  røde (for eksempel `<` byttet til `<=` i 11- og 35-timersregelen). Se
  «Kontroller» i KI-loggene for de fire reglene.
- **Modellvalg på grunnlag av målinger:** Beslutningsregelen ble bestemt før
  kjøringen, og en blindet gjennomgang ble anbefalt
  ([2026-10-16-beslutningstest-haiku-luna.md](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md),
  «Beslutningsregel (fastsatt før kjøring)»).
- **Læring:** Ingen kilde i repoet. Bruk egne erfaringer og sesjonsloggene.

### 4.2 Mulige ulemper og begrensninger

- **Mennesker fant det fire agenter overså:** Ragnhild slo sammen 3.1 og 2.4 lokalt
  og fant en test som feilet. Implementeringsagenten og tre gjennomgangsagenter hadde
  ikke sett det. Kim fant samme feil og tre funn til
  ([2026-11-12-godkjenningsflaten.md](../ki-logg/2026-11-12-godkjenningsflaten.md),
  «Retting etter PR-gjennomgang»).
- **Tester som ikke beviste det de skulle:**
  - Testen for at preferansen påvirker rangeringen (5.2) overlevde to mutasjoner,
    fordi ID-rekkefølgen tilfeldigvis ga samme resultat. Funnet i Johannes'
    gjennomgang av PR #34
    ([2026-11-20-rangering-tolkede-preferanser.md](../ki-logg/2026-11-20-rangering-tolkede-preferanser.md)).
  - Første utkast av ulempeberegningen telte overlappende vakter dobbelt
    ([2026-11-15-ulempebelastning.md](../ki-logg/2026-11-15-ulempebelastning.md)).
- **Tester som ble «rettet» feil vei:** Flere KI-logger skiller mellom å rette testen
  og å rette koden, og fasiten skal ikke tilpasses koden (AV-07). Se for eksempel
  [2026-11-11-35-timersregelen.md](../ki-logg/2026-11-11-35-timersregelen.md), punkt 1
  under «Rettet underveis», og
  [2026-11-23-loggoppsett-backend.md](../ki-logg/2026-11-23-loggoppsett-backend.md),
  punkt 1.
- **Farlig kommando som ble stoppet:** En agent prøvde å rydde opp med
  `git checkout -- .`, som ville forkastet andre endringer. Tillatelsessystemet
  stoppet den
  ([2026-11-14-komponenttester.md](../ki-logg/2026-11-14-komponenttester.md)).
- **Omfang og dokumentmengde:** Bård spurte hvilke detaljer fra KI-forslag gruppa
  godtok uten å kutte (refleksjonsspørsmål 2 i
  [tilbakemelding-prd.md](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/tilbakemelding-prd.md)
  §7). BMAD-rammeverket utgjør over halvparten av filene i repoet (AGENTS.md).
- **Kostnad:** `bmad-build` med underagenter koster mer enn én økt (OP-04, AGENTS.md).
- **Avhengighet og kreativitet:** Ingen kilde i repoet. Dette må dere skrive fra egen
  erfaring.

### 4.3 Med og uten KI: spørsmål å ta stilling til

- Hvilke stories ville vært for store uten KI? Hvilke ville vært like raske?
- Ville dere hatt mutasjonstesting og tre uavhengige gjennomganger uten KI?
- Ville dokumentasjonen vært kortere og lettere å lese?

### 4.4 Samlet vurdering

Gruppas egen konklusjon. Se også Bårds to refleksjonsspørsmål (§7 i tilbakemeldingen).

---

## 5. Etiske implikasjoner: eksempler

### 5.1 Ansvar og eierskap

- Den enkelte har ansvar for å kvalitetssikre eget arbeid, også når KI har skrevet
  det, og den som merger har ansvaret (Policy i AGENTS.md).
- En agent endrer ikke AGENTS.md eller loggregler uten uttrykkelig beskjed fra et
  gruppemedlem (AV-08, endret 08.11).
- Agentens vurderinger er merket «Agentens vurdering; må gjennomgås av gruppa» i
  modelltestene ([2026-10-15-modellsammenligning.md](../ki-logg/2026-10-15-modellsammenligning.md),
  «Konklusjon og anbefaling»).
- Opphavsrett: Ingen kilde i repoet. Det er et diskusjonsspørsmål.

### 5.2 Transparens

- Alle endringer med KI-generert kode har en KI-logg med prompt, leveranse og
  rettelser (Policy). [docs/ki-logg/README.md](../ki-logg/README.md) har spørringer for
  å hente det ut ved innlevering.
- Commit-meldinger skal si hvorfor tidligere arbeid ble endret, og hva som var galt i
  generert kode (Policy). Eksempler: `3e643e5`, `f59f69b`, `6dda222` og `11a8a27` i
  `git log`.
- Produktet viser hvor teksten kommer fra. Reserveteksten har en kildelinje, så
  brukeren ser at det ikke er en KI-forklaring
  ([2026-11-21-reservetekst-ved-ki-feil.md](../ki-logg/2026-11-21-reservetekst-ved-ki-feil.md)).

### 5.3 Læring og kompetanse

- Ingen kilde i repoet utover sesjonsloggene. Dette er egne erfaringer. Mulige
  inngangsspørsmål: Hva forstår dere i koden, og hva måtte dere stole på? Hva lærte
  dere av å gå gjennom PR-er punkt for punkt?

### 5.4 Arbeidsmarkedet

- Ingen kilde i repoet. Egen vurdering. Prosjektet kan brukes som eksempel på hvilke
  roller som ble viktige: den som setter krav, går gjennom og tester, mot den som
  skriver koden.

### 5.5 Datasikkerhet og personvern

- **Fiktive data:** Alle ansatte og vakter er fiktive testdata (story 1.2, AV-07).
- **Hva som sendes til KI i produktet:** Bare preferansetekster og godkjente
  kandidater. En egen test viser at utelukkede kandidater aldri når KI-laget (story
  5.6, [2026-11-21-lekkasjeinvariant.md](../ki-logg/2026-11-21-lekkasjeinvariant.md)
  og [2026-11-22-oppfolging-pr-36.md](../ki-logg/2026-11-22-oppfolging-pr-36.md)).
- **Helseopplysninger og kjønn:** Modelltestene sjekket om modellen gjentok
  helseopplysninger eller brukte kjønnede pronomen. Det ble et krav ved valg av modell
  ([2026-10-16-beslutningstest-haiku-luna.md](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md),
  «Anbefaling»).
- **Nøkler:** Aldri i kildekoden, bare i miljøvariabler. CI får aldri hemmeligheter, og
  agenter leser aldri `.env` (Policy). En nøkkel med ugyldige tegn kunne havne i
  loggen, og det ble rettet. Feiltekster logges ikke fordi de kan gjengi prompt eller
  nøkkel ([2026-11-21-sma-rettelser-openrouter.md](../ki-logg/2026-11-21-sma-rettelser-openrouter.md)).
- **Det vi delte med utviklingsverktøyene:** All kode og alle dokumenter i repoet ble
  lest av Claude Code og Codex. Skjermbilder ble sjekket for passord, nøkler og
  personlige stier før de ble lagt i repoet
  ([2026-11-08-vaktoversikt.md](../ki-logg/2026-11-08-vaktoversikt.md)). 22
  øyeblikksbilder fra nettleserverktøyet ble committet ved en feil og fjernet
  (`e759d41`).
- **Sensornøkkelen:** Hvem som betaler, og hvordan nøkkelen deles sikkert, er åpent
  (ÅB-8, [avklaringsrunde-2026-11-22.md](../beslutninger/avklaringsrunde-2026-11-22.md)
  punkt 4).

---

## 6. Teknologiske implikasjoner

### 6.1 Kodekvalitet og vedlikehold

- **Arkitekturregel som maskinen sjekker:** Domenekjernen kan ikke importere
  adapterne. import-linter kjører som test (AD-1, AD-2,
  `backend/tester/test_arkitektur.py`). Kontrollen ble testet ved å bryte regelen med
  vilje ([2026-11-11-kompetanse-minstekrav.md](../ki-logg/2026-11-11-kompetanse-minstekrav.md)).
- **Fasiten er skrevet for hånd, ikke tilpasset koden** (AV-07). API-testene leser
  `testdata.FASIT`.
- **Tester som går i stykker når neste story merges:** Testene var skrevet for dagens
  regler, og noen ble ugyldige da neste regel kom. Se 35-timersregelen («Rettet
  underveis» punkt 3–5) og PR #16.
- **Lesbarhet:** Docstringer som motsa koden ble rettet etter gjennomgang
  ([2026-11-15-timer-i-perioden.md](../ki-logg/2026-11-15-timer-i-perioden.md),
  [2026-11-15-rangering.md](../ki-logg/2026-11-15-rangering.md)).
- **Feilsøking:** Rettelsen for transportfeil i 5.4
  ([2026-11-21-reservetekst-ved-ki-feil.md](../ki-logg/2026-11-21-reservetekst-ved-ki-feil.md)).

### 6.2 Standarder og beste praksis

Eksempler der KI foreslo noe utdatert eller ufullstendig:

- `httpx` med Starlettes `TestClient` ga en advarsel om at det er utdatert. Byttet til
  `httpx2` ([2026-10-19-prosjektoppsett.md](../ki-logg/2026-10-19-prosjektoppsett.md)).
- `temperature=0` ga 404 hos OpenRouter fordi modellen ikke støttet parameteren
  ([2026-10-15-modelltest-haiku.md](../ki-logg/2026-10-15-modelltest-haiku.md)).
- `node-version: "latest"` ga en alfaversjon av Node i CI
  ([2026-11-08-ci-backend-tester.md](../ki-logg/2026-11-08-ci-backend-tester.md)).
- Agenten ville låse CI til Python 3.12. Johannes påpekte at det skjuler versjonsdrift,
  og det ble en matrise med 3.12 og 3.x (samme logg).
- `"node --test tester/"` virket med Node 20, men ikke med 26
  ([2026-11-08-vaktoversikt.md](../ki-logg/2026-11-08-vaktoversikt.md)).
- En typecast skjulte feil for typesjekkeren. Byttet til `satisfies`
  ([2026-11-14-komponenttester.md](../ki-logg/2026-11-14-komponenttester.md)).

Validering:

- CI med laveste og nyeste versjon av Python og Node (PR #9).
- Manuell nettleserkontroll mot ekte backend (OP-16, [docs/testing.md](../testing.md)).
- Test fra ren klone på macOS (OP-05).

### 6.3 Fremtidig utvikling

- Egen vurdering. Mulige knagger fra prosjektet: underagenter som går gjennom
  hverandres kode, spesifikasjoner som oppdrag til agenter, modellvalg per oppgave
  ([docs/modellvalg-stories.md](../modellvalg-stories.md)), og at mennesker fortsatt
  fant feil agentene overså (4.2).

---

## 7. Konklusjon og læring: kilder

Bare kilder. Lærdommene og vurderingene skriver gruppa selv.

- **Bårds to refleksjonsspørsmål**, §7 i
  [tilbakemelding-prd.md](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/tilbakemelding-prd.md).
  Johannes har et åpent punkt om at gruppa skal svare på dem.
  1. Hvordan kontrollerte dere at regneeksemplene og skriptet bak taket på 300
     Ulempepoeng stemte? (Se K-01 og
     [2026-11-02-ab-3-ulempebelastning.md](../ki-logg/2026-11-02-ab-3-ulempebelastning.md).)
  2. Hvilke detaljer fra KI-forslag godtok dere uten å kutte, og hvilke hører hjemme i
     testplan eller arkitektur?
- **Hva dere ville gjort annerledes:**
  - `.memlog.md` i brief-mappen sier hvorfor noe ble valgt bort.
  - [deferred-work.md](../../_bmad-output/implementation-artifacts/deferred-work.md)
    viser hva som ble utsatt.
  - Punktene i [avklaringsrunde-2026-11-22.md](../beslutninger/avklaringsrunde-2026-11-22.md)
    viser hva som fortsatt er uavklart.
- **Commits som endret tidligere arbeid, med begrunnelse:** Spørringen i
  [docs/ki-logg/README.md](../ki-logg/README.md). Den er beskrevet som råmaterialet til
  refleksjonsrapporten.
- **7.4 Personlig refleksjon:** Hver persons sesjonslogger i `.logs/<bruker>/` og
  åpne punkter i `issues.md`.

## 8. Vedlegg: kandidater

- Skjermbilder fra nettleserkontrollene i `docs/ki-logg/*/` og `docs/testing/`.
- Lenke til repoet:
  `https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren`.
- [Vurderingsmatrisen](vurderingsmatrise.md) og
  [beslutningsreferatet](../beslutninger/avklaringspunkter.md).

## Det som mangler i repoet

Dette må gruppa fylle inn selv:

- Hvilke samarbeidsverktøy dere brukte utenom GitHub (chat, møter).
- Promptene fra planleggingen i september, før KI-loggene startet 15.10.
- Tidsbruk, og hvordan dere fordelte arbeidet utover hvem som laget PR-en.
- Alt i 4.1 om læring, 4.2 om avhengighet og kreativitet, 5.3, 5.4, 6.3 og 7.
