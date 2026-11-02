# Avklaringspunkter mot styringsdokumenter

## 2026-11-02 kl. 23:20 — Kimsk81

### Oppgave
Lese `docs/beslutninger/avklaringspunkter.md` og undersøke om beslutningsreferatet kommer i konflikt med andre styrende filer i prosjektet.

### Plan
- Lese referatet og kontrollere relevante krav mot AGENTS.md, CLAUDE.md, produktbrief, PRD, epics, arkitektur, UX, sprintstatus og sensorveiledning/vurderingsmatrise.
- Skille innholdskonflikter, statusavvik og manglende spesifikasjon fra nye presiseringer og uendrede prosjektinstruksjoner.
- Dokumentere funn uten å endre referatet eller kravdokumentene.

### Resultat
Kontrollen gjelder lokal `main` på `3811a38`. Beslutningsfilen var usporet før undersøkelsen. Innhold i PR #4, møteunderlagets PDF og faktisk godkjenning av møtevedtakene er ikke selvstendig verifisert. Ingen produktkode er endret, og kjøretidstester var ikke relevante for denne dokumentkontrollen.

Funn kontrollert mot konkrete tekststeder:

- **Direkte kravkonflikt:** AV-01/AV-11 vedtar fire faktorer med vekter 40/20/15/25 og ulempbelastning. `product-brief.md:124`, PRD §4.4 (linje 168–177), `epics.md:30,110,745` og `ARCHITECTURE-SPINE.md:193` har fortsatt tre faktorer og 40/35/25.
- **Manglende spesifikasjonsgrunnlag:** Referatet omtaler eksisterende Story 4.7, ulempmodell 0/1/2/3, tak 300 og verifikasjon mot PRD/Story 4.7. Lokal epics og sprintstatus har bare Story 4.1–4.6; lokal PRD har ingen ulempmodell. KS-02/KS-03 kan derfor ikke ferdigstilles mot disse filene alene. Dette kan ligge i PR #4; kontrollen fastslår bare lokal tilstand.
- **Vakttypekonflikt:** AV-02 krever fire vakttyper, mens Story 1.2 i `epics.md:248` angir dag, kveld eller natt uten mellomvakt.
- **Tidskonflikt:** AV-02 sier at alle vaktene varer åtte timer. Story 4.1 (`epics.md:675–676`) krever faktisk forløpt tid og tester begge sommertidsoverganger. Natt 23–07 er normalt åtte timer, men sju/ni faktiske timer ved slike overganger. Ordlyden bør avgrenses til normale døgn/demoperioden; faste åtte beregningstimer ville kreve en endret regel. Ingen ny regel er vedtatt her.
- **Hvile: statusavvik og ordlyd:** AV-04 bekrefter de midlertidige tolkningene i Story 2.3/2.4. ÅB-5/ÅB-6 står fortsatt åpne i epics, og PRD FR-4/FR-5 sier «per 24 timer»/«per 7 dager» uten referatets avgrensning. Samordning trengs; dette er ikke en konflikt med de konkrete midlertidige story-reglene.
- **Prosesspresisering:** OP-05 og §8.4 omtaler ren klone, Python 3.12, macOS/Linux og vurderingsmatrise som ikke vedtatte/åpne. Oppfølging av ren klone og Python 3.12 er allerede registrert i sprintstatus, og AGENTS.md krever oppdatering av vurderingsmatrisen ved milepæler. Referatet bevarer eksisterende krav og opphever dem dermed ikke, men teksten kan skape inntrykk av at alt dette er nye forslag.
- **Ingen påvist overordnet instruksjonskonflikt:** AV-08, K-05 og §9 viderefører eksisterende logging, prosjektprosess og deterministisk regelmotor. §9.9 gir ikke ny fullmakt til repo-operasjoner, men er ikke et forbud mot eksisterende loggcommit-krav. KS-01 bevarer eksisterende godkjenningskrav. OP-02 utsetter UX-arbeid til en milepæl og fjerner ikke mobilkravene i Story 4.6.
- **Presiseringer:** AV-03/05/06/09 og K-03 gir konkrete beslutninger om periodeplassering, likhet, tilgjengelighet, preferansegyldighet, målevindu og avrunding; flere av disse fyller tidligere åpne spørsmål fremfor å motsi konkrete regler. 32,4 timer er fortsatt ikke vedtatt. Foreslått dokumentsti `docs/avklaringspunkter.md` avviker fra faktisk plassering `docs/beslutninger/avklaringspunkter.md`.

Ingen kravdokumenter, agentinstruksjoner eller beslutningsstatuser er endret. Eksisterende samlepunkter i issues.md er beholdt åpne fordi de også inneholder uavklarte spørsmål; delavklaringer er tilføyd og ett nytt samordningspunkt er registrert. Dokumentkontrollen har ikke verifisert implementasjon eller oppfylt en produktmilepæl; vurderingsmatrisen er ikke oppdatert.

### Åpne punkter
- Samordne referatets vedtatte rangeringsmodell og vakttyper med lokale kravfiler; finn grunnlaget for Story 4.7 og presiser åttetimersordlyd, hvilestatus, eksisterende kontrollkrav og faktisk dokumentsti. Kontroller relevante filer i PR #4 før konkrete kravendringer. Se nytt punkt i issues.md; øvrige åpne spørsmål videreføres der.
