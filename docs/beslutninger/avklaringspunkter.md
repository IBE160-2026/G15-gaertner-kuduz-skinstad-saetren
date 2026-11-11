# Avklaringspunkter og beslutningsreferat – Turnushjelperen

> **Prosjekt:** IBE160 Programmering med KI – Turnushjelperen  
> **Gruppe:** G15 – Prompt Patrol  
> **Møtedato:** 2026-11-02  
> **Deltakere:** Johannes W. Gaertner, Mithad Kuduz, Kim O. Skinstad og Ragnhild Sætren  
> **Beslutningsgrunnlag:** [IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf](IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf) (oppdatert 2026-10-31, 6 sider)  
> **Dokumentstatus:** Beslutningsreferat; vedtatte beslutninger og åpne oppfølgingspunkter  
> **Sist oppdatert:** 2026-11-11 (avgrensning og akseptmål for forståelsestesten i P-13 ført i §12; 2026-11-10: P-01–P-13 og E-01/E-02 fra beslutningsgrunnlaget 2026-11-07 ført i §12, dokumentvedtak skilt fra implementasjon og utestående kontroll)
> **Plassering:** `docs/beslutninger/avklaringspunkter.md`

## 1. Formål, status og leseveiledning

Dette dokumentet gjengir beslutningene fra gruppemøtet 2. november 2026 om PR #4, Story 1.2 og førsteversjonen (`v1`) av Turnushjelperen. Det skal gjøre beslutningene tydelige og etterprøvbare for gruppemedlemmene og KI-agentene Codex og Claude. Innholdet er basert på beslutningsgrunnlaget fra 31. oktober 2026 og gruppens etterfølgende, eksplisitte avklaringer.

**Hva statusene betyr:**

- **Vedtatt:** Gruppen har eksplisitt besluttet dette. Skal legges til grunn for videre utviklingsarbeid innenfor eksisterende prosjektinstruksjoner.
- **Åpent:** Ingen endelig løsning eller oppfølging er vedtatt. En anbefaling på et åpent punkt er **ikke** et vedtak.
- **Utsatt:** En konkret avklaring eller aktivitet er flyttet til en senere milepæl. Det betyr ikke at den er ferdigstilt.
- **Forslag, ikke vedtatt:** Kan brukes som innspill i planlegging, men må ikke behandles som bindende beslutning.
- **Kontroll gjenstår:** En beslutning om å kontrollere noe er tatt, men selve kontrollen er **ikke** utført eller dokumentert her.

**Viktig skille:** At alle de 12 nummererte beslutningspunktene er gjennomgått, betyr ikke at alle korrigeringer er utført, at PR #4 er godkjent eller at Story 1.2 er `done`. Repoet er ikke kontrollert mot sitt siste innhold ved utarbeidelsen av dette referatet. Alle konsekvensbeskrivelser må derfor følges opp mot faktiske prosjektfiler før endring.

**Godkjenningstrinn:** Godkjent spesifikasjon av Story 1.2 betyr `ready-for-dev`; `done` forutsetter data, implementasjon og nødvendige tester i samsvar med gjeldende ferdigkriterier. En teknisk mergebar PR er ikke automatisk faglig godkjent. Åpne korrigeringspunkter kan bli stående etter merge (KS-01), men eksisterende PR-godkjenningskrav gjelder fortsatt.

## 2. Beslutningsoversikt

### 2.1 Hovedbeslutninger (nummereringen følger PDF-en)

| ID | Tema | Status | Kort beslutning | Ansvarlig |
|---|---|---|---|---|
| AV-01 | Story 4.7 i v1 | Vedtatt | Behold ulempbelastning i v1. | Ikke bestemt |
| AV-02 | Vakttider | Vedtatt | Dag 07–15, mellom 10–18, kveld 15–23, natt 23–07 neste dag. | Ikke bestemt |
| AV-03 | Visningsperiode | Vedtatt | Vaktens starttid bestemmer visningsperioden. | Ikke bestemt |
| AV-04 | Hvilekontroll | Vedtatt | Avgrenset prototypetolkning: 11 t daglig og 35 t i berørt kalenderuke. | Ikke bestemt |
| AV-05 | Rangering ved like verdier | Vedtatt | Min–maks for kostnad/timer; 50 faktorpoeng hvis alle er like; lik totalscore brytes med stigende ansatt-ID. | Ikke bestemt |
| AV-06 | Tilgjengelighet/preferanser | Vedtatt | Faste demoforutsetninger; opprinnelig ansatt utelukkes; preferanser gjelder demoperioden. | Ikke bestemt |
| AV-07 | Testdata og fasit | Vedtatt | Faste seeddata og eksplisitt fasit for #4127/#4189 og rangering. | Ikke bestemt |
| AV-08 | Beslutningssporbarhet | Vedtatt | Navngitte, sporbare gruppevedtak; logg- og agentinstruksjoner endres bare når endringen registreres i §11 (fra 2026-11-08). | Ikke bestemt |
| AV-09 | Målevindu ulempe | Vedtatt | 672 faktiske timer, halvåpent vindu, lokal kategorisering i Europe/Oslo. | Ikke bestemt |
| AV-10 | Historikk | Vedtatt | Fast, reproduserbar historisk seeddata; ingen turnusgenerator i v1. | Ikke bestemt |
| AV-11 | Ulempmodell | Vedtatt | Vekter 40/20/15/25; 0/1/2/3 poeng/t; tak 300; ingen helligdagsmodell eller innstillingsside. | Ikke bestemt |
| AV-12 | Test av ulempens effekt | Vedtatt | Test kandidater med like øvrige faktorer og ulik ulempe; forventet scoreforskjell dokumenteres. | Ikke bestemt |

### 2.2 Korrigeringer og oppfølging (separat fra AV-01–AV-12)

| ID | Tema | Status | Kort registrering | Ansvarlig |
|---|---|---|---|---|
| K-01 | Feil regneeksempel | Åpent | `22 + 2 × 21 + 3 × 29 = 151`, ikke 136; konkret retting ikke avtalt. | Ikke bestemt |
| K-02 | Høy timebelastning | Vedtatt 2026-11-09 (P-04) | Terskel minst 32,4 t før visningsavrunding. Ingrid beholdes på 32 t og er under grensen; retting av forventning i Story 1.2 er dokumentarbeid, visning/test gjenstår. | Gruppen |
| K-03 | Avrunding | Vedtatt | Beregn/sorter uavrundet; vis én desimal. | Ikke bestemt |
| K-04 | `RangertKandidat`/KI-kontrakt | Produktvalg vedtatt 2026-11-09 (P-06/P-07); kontrakt og tester gjenstår | Strukturerte, faktakontrollerte begrunnelser og én forhåndsberegnet referansekandidat; se §12. | Gruppen |
| K-05 | KI-sporbarhet | Prinsipp vedtatt; kontroll åpen | Behold logging uendret; sjekk senere dokumentasjon inkl. tak 300. | Ikke bestemt |
| K-06 | Dokumentkvalitet | Samordning pågår 2026-11-10 | P-vedtakene føres i planleggingsdokumentene; endelig dokumentkontroll gjenstår. | Gruppen |
| OP-01 | Avgrensninger i v1 | Vedtatt | Ingen omfattende tariff-, fraværs-, stillingsprosent-, helligdags- eller juridisk modell. | Ikke bestemt |
| OP-02 | UX og mobil | Vedtatt | Samordne mockuper nå; detaljert UX, mobil og brukerprøving etter fungerende kandidatvisning. | Ikke bestemt |
| OP-03 | KI-feil ved preferansetolkning | Løsning vedtatt 2026-11-09 (P-05); implementasjon gjenstår | Midlertidig 50 poeng med egen vente-/feilstatus, avgrensede nye forsøk og brukerutløst nytt forsøk. | Gruppen |
| OP-04 | Agentoppsett/underagenter | Vedtatt 2026-11-04 | Gjennomgått og godkjent: `bmad-build` kjøres med underagenter, som i AGENTS.md fra PR #5 (§11). | Johannes W. Gaertner (godkjent på vegne av gruppa) |
| OP-05 | Ren klone/plattformtesting | Delvis vedtatt 2026-11-07 | Fysisk test på macOS/Linux strykes: verken sensor eller noen i gruppa har Mac. Koden skrives for å virke på tvers av operativsystem og testes fysisk på Windows. Test fra ren klone er fortsatt ikke avtalt (§11). | Johannes W. Gaertner |
| OP-06 | Arbeidsrekkefølge | Forslag, ikke vedtatt | Codex-rekkefølgen beholdes kun som forslag. | Ikke bestemt |
| OP-07 | PR #4 | Vedtatt | Ragnhild Sætren ansvarlig for oppfølging og retting av PR #4. | Ragnhild Sætren |
| OP-08 | Story 1.2 | Vedtatt | Mithad Kuduz ansvarlig for oppdatering av Story 1.2. | Mithad Kuduz |
| OP-09 | Frist PR-review | Åpent | Ingen frist avtalt. | Ikke bestemt (PR-ansvar: Ragnhild) |
| KS-01 | Åpne punkter ved merge | Vedtatt | K-01/K-02/K-04/K-06 kan være åpne etter merge; øvrige godkjenningskrav gjelder. | Ikke bestemt |
| KS-02 | Kontroller rangeringsformel | Utført for fasiten i Story 1.2 (2026-11-04) | Fasiten for #4127 er kontrollert og godkjent med PR #5 (§11). Gjelder ny fasit på nytt. | Mithad Kuduz (kontroll), Johannes W. Gaertner (godkjenning) |
| KS-03 | Kontroller tidskategorier | Kontroll vedtatt; ikke utført | Kontroller fire vakttyper før implementasjon av Story 4.7 og ferdigstilling av fasit. | Ikke bestemt |
| KS-04 | Kontroller datadekning | Utført 2026-11-04 | Dekket for #4127 og #4189 og låst med test; begrensningen etter 05.10 er godtatt (§11). Se §11, 2026-11-11 (Story 2.3): vakter som slutter etter 04.10 kl. 13:00 gir nå datafeil. | Mithad Kuduz (kontroll), Johannes W. Gaertner (godkjenning) |

### 2.3 Vedtak etter møtet (ikke i PDF-en)

| ID | Tema | Status | Kort beslutning | Ansvarlig |
|---|---|---|---|---|
| AV-13 | Enhet i designtokens | Vedtatt 2026-11-06 | Skriftstørrelser i `rem`; spacing, kanter, radius, sporing og faste bredder i `px`. Ingen rå størrelser i komponentene (§11). | Johannes W. Gaertner (vedtatt på vegne av gruppa) |
| AV-14 | Layoutbredde | Vedtatt 2026-11-06 | Appbar over hele bredden; innholdet får `max-width: 1180px`. Fast bredde på 1180px forkastes (§11). | Johannes W. Gaertner (vedtatt på vegne av gruppa) |
| OP-10 | Story 1.3 | Vedtatt 2026-11-06; de fire spørsmålene avklart i spesifikasjonen 2026-11-06 | Johannes W. Gaertner tar Story 1.3. Vite-proxy, personlig eller tilfeldig testpassord, PyJWT 2.15.1 og `hashlib.scrypt`, tabellen `bruker`. JWT-nøkkelen lages tilfeldig ved oppstart, avvik fra epics (§11). | Johannes W. Gaertner |
| OP-11 | Story 1.5 | Meldt 2026-11-08 | Mithad Kuduz tar Story 1.5, Vaktoversikt med «Krever handling». Implementeringen starter etter at PR #8 (Story 1.4) er merget (§11). | Mithad Kuduz |
| OP-12 | Story 2.3 | Meldt 2026-11-11 | Mithad Kuduz tar Story 2.3, 11-timersregelen (daglig hvile). Implementeringen starter etter at PR #14 (Story 2.2) er merget, og etter at gruppa har avklart om overlappende vakter også skal telle under 11-timersregelen (§11). | Mithad Kuduz |

## 3. Detaljerte hovedbeslutninger

### AV-01 – Story 4.7 skal inngå i v1

- **Problemstilling:** Skal ulempbelastning (Story 4.7) implementeres i førsteversjonen eller utsettes?
- **Alternativer:** A: Utsett; enklere v1, opprinnelig vekting 40/35/25. B: Behold; vekting 40/20/15/25 og behov for historikk og tidstester.
- **Codex:** Ny gjennomgang anbefalte A; tidligere gjennomgang anbefalte B. Ingen av dem var gruppevedtak.
- **Gruppens beslutning:** **B. Story 4.7 beholdes i v1.**
- **Begrunnelse:** Gruppen ønsker funksjonaliteten nå og vil videreføre påbegynt arbeid i stedet for å utsette og senere ta opp arbeidet igjen.
- **Teknisk konsekvens:** Rangering og data må støtte ulempbelastning, men dette innebærer **ikke** at Story 4.7 er implementert. Story 1.2 etablerer nødvendige data; selve beregningen implementeres senere i Story 4.7 innenfor v1. Vektingen og metoden er konkretisert i AV-11.
- **Berørte områder:** Product Brief, PRD, epics, arkitektur, DESIGN, EXPERIENCE, sprintstatus, Story 1.2, Story 4.7 og PR #4.
- **Åpent:** Detaljert implementasjonsstatus må avstemmes mot repoet; KS-02 og KS-03 krever kontroll.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-02 – Fire vakttyper, inkludert mellomvakt

- **Problemstilling:** Hvilke standardvakttider brukes i demonstrasjonsgrunnlaget?
- **Alternativer i PDF:** A: Dag 07–15, kveld 15–23, natt 23–07; B: Dag 07–15, kveld 15–22:30, natt 22–07:30. Gruppen vedtok A **med eget tillegg**.
- **Codex:** Ny rapport anbefalte A; eldre rapport B.
- **Gruppens beslutning:** **Dag 07:00–15:00; mellom 10:00–18:00; kveld 15:00–23:00; natt 23:00–07:00 neste dag.** Alle varer åtte timer.
- **Begrunnelse:** Mellomvakten gir flere mulige vaktkombinasjoner når hvilebestemmelsene ellers begrenser valg av erstatter. Eksempel: Etter kveldsvakt til 23:00 gir neste dags dagvakt 07:00 bare 8 timers hvile; mellomvakt 10:00 gir 11 timer (forutsatt at øvrige regler også er oppfylt).
- **Teknisk konsekvens:** Seeddata, testfasit, vaktmaler og mockuper må støtte fire vakttyper. Regelmotoren må kontrollere hvile og kollisjon ut fra faktiske start/sluttidspunkt. Overlapp mellom **forskjellige** ansattes vakter er ikke i seg selv en regelbrudd.
- **Berørte områder:** Story 1.2/1.5, mockuper, DESIGN/EXPERIENCE, scenarioene #4127/#4189, rangerings-/tidsberegning, Story 4.7.
- **Åpent:** Eksakt eksisterende tidskategorisering for ulempoeng må kontrolleres (KS-03).
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-03 – Starttid bestemmer visningsperiode

- **Problemstilling:** Skal vakter vises etter starttid eller etter enhver overlapp med valgt periode?
- **Alternativer:** A: Starttid avgjør; entydig plassering. B: Overlapp avgjør; også vakter som starter før perioden kan vises.
- **Codex:** Anbefalte A, med halvåpent visningsintervall og grensekryssende vakter tilgjengelige som beregningsgrunnlag.
- **Gruppens beslutning:** **A. En vakt vises i perioden som inneholder vaktens starttidspunkt.** Visningsperioden er halvåpen: `[fra, til)`.
- **Begrunnelse:** Unngå økt kompleksitet.
- **Teknisk konsekvens:** Eksempelperioden er `[2026-09-21 00:00, 2026-10-05 00:00)`. En nattvakt som starter 20.09 kl. 23:00, vises ikke i denne perioden selv om den avsluttes 21.09. Den skal likevel kunne brukes til relevant hvile- og historikkberegning.
- **Berørte områder:** Story 1.2/1.5, visningsspesifikasjon, seeddata og tester.
- **Åpent:** Kontroll av nødvendige data ved periodegrensene gjennom KS-04.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-04 – Forenklet hvilekontroll i v1

- **Problemstilling:** Skal kontrollen være en avgrenset prototypetolkning eller en mer omfattende, rullerende regelkontroll?
- **Alternativer:** A: Kontroller 11 timers daglig hvile før/etter og 35 timers sammenhengende hvile innenfor hver berørte kalenderuke. B: Mer omfattende rullerende kontroll.
- **Codex:** Anbefalte A med relevante nabovakter og komplette berørte kalenderuker.
- **Gruppens beslutning:** **A.** Regelmotoren skal håndheve den avgrensede prototypetolkningen: minst 11 timer hvile før og etter aktuell vakt, samt minst 35 timers sammenhengende hvile innenfor hver berørte kalenderuke.
- **Begrunnelse:** Begrense kompleksiteten.
- **Teknisk konsekvens:** Kontrollene skal være deterministiske; KI avgjør ikke om en kandidat er gyldig. Regelmotoren trenger relevante vakter utenfor visningsperioden, inklusive etterfølgende vakter og komplette berørte uker. Kandidater som bryter harde regler, utelukkes før rangering.
- **Berørte områder:** ÅB-5/6, PRD, epics, Story 1.2, regelmotor og tester.
- **Avgrensning:** **Ikke** markedsfør som full juridisk arbeidsmiljølovkontroll. Omfattende lovtolkning er utenfor v1 (OP-01).
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-05 – Min–maks-normalisering og håndtering av like verdier

- **Problemstilling:** Hvordan håndteres identiske faktorverdier og lik totalscore?
- **Alternativer:** A: Min–maks med særregel ved like verdier. B: Fast skala med ny kalibrering.
- **Codex:** Anbefalte A, 50 faktorpoeng hvis alle kandidater har lik verdi, og stigende ansatt-ID ved helt lik totalscore.
- **Gruppens beslutning:** **A.** Bruk min–maks-normalisering for kostnad og timebelastning. Hvis **samtlige kandidater** har identisk verdi for en slik faktor, får alle **50 faktorpoeng** for den faktoren. Ved identisk totalscore sorteres på **stigende ansatt-ID**.
- **Begrunnelse:** Ikke oppgitt.
- **Teknisk konsekvens:** Min–maks er kandidatavhengig. Likeverdissærregelen gjelder per faktor når alle i kandidatsettet har samme verdi. Lik totalscore vurderes på **uavrundet** verdi (K-03), ikke likt visningstall. Bare gyldige kandidater deltar i rangering.
- **Berørte områder:** PRD §4.4, Story 4.4, Story 1.2 og testfasit.
- **Åpent:** Detaljert normalisering for ulempbelastning kontrolleres særskilt (KS-02); AV-05 bestemmer ikke denne formelen.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-06 – Faste tilgjengelighets- og preferanseantakelser

- **Problemstilling:** Bruke enkle demonstrasjonsantakelser eller utvikle fraværsmodell og daterte preferanser?
- **Alternativer:** A: Faste demonstrasjonsdata. B: Fravær og preferanser som varierer over tid.
- **Codex:** Anbefalte A.
- **Gruppens beslutning:** **A.** Den opprinnelig oppsatte ansatte utelukkes fra erstatningslisten. Øvrige ansatte antas tilgjengelige med mindre planlagte vakter eller harde regler utelukker dem. Registrerte preferanser gjelder hele demonstrasjonsperioden.
- **Begrunnelse:** Unngå for kompleks løsning.
- **Teknisk konsekvens:** Ingen separat fraværsmodell eller daterte preferanser i v1. Antatt tilgjengelighet er **ikke** garanti for faktisk tilgjengelighet. Kompetansekrav, hvile og kollisjoner håndheves fortsatt.
- **Berørte områder:** Product Brief, PRD, Story 1.2 og epic-kontekst.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-07 – Faste seeddata og eksplisitt testfasit

- **Problemstilling:** Illustrative eksempler eller faste testdata med kjent fasit?
- **Alternativer:** A: Illustrative eksempler. B: Faste, reproduserbare seeddata med forventede resultater.
- **Codex:** Anbefalte B med scenarioene `#4127` og `#4189`, gyldige/utelukkede kandidater og scenario der billigste ikke rangeres først.
- **Gruppens beslutning:** **B.** Lag faste, reproduserbare seeddata og **eksplisitt, forhåndsberegnet testfasit** for `#4127`/`#4189`, gyldige og utelukkede kandidater, begrunnelser for utelukkelse og forventet rangering. Inkluder ett tilfelle der billigste kandidat **ikke** rangeres først.
- **Begrunnelse:** Sikrere og reproduserbare tester.
- **Teknisk konsekvens:** Data og forventet fasit skal kunne gjenskapes; fasiten må ikke bare kopieres fra programresultatet. Alle fire vakttyper, vedtatte regler og nødvendig historikk må testes. Ulempen kan beregnes/testes i Story 4.7 selv om historikken legges inn i Story 1.2.
- **Berørte områder:** Story 1.2, epics, seeddata, testfasit og tester.
- **Åpent:** Formelverifikasjon (KS-02), tidskategorier (KS-03), datadekning (KS-04).
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-08 – Sporbare vedtak uten å endre logging

- **Problemstilling:** Implisitt faglig godkjenning ved merge eller eksplisitte gruppevedtak?
- **Alternativer:** A: Implisitt ved merge. B: Navngitte, etterprøvbare vedtak.
- **Codex:** Anbefalte B med dato, ansvar, bekreftelse av konsekvenser for Story 1.2 og bare faktiske avklaringer lukket.
- **Gruppens beslutning:** **B.** Gruppevedtak dokumenteres eksplisitt og sporbarhet ivaretas gjennom `avklaringspunkter.md`. Registrer beslutnings-ID, innhold, møtedato og ansvarlig der det er avtalt. **Behold eksisterende `AGENTS.md`, `CLAUDE.md`, KI-logging, sesjonslogger og andre loggregler uendret.**
- **Begrunnelse:** Ingen særskilt begrunnelse oppgitt; gruppen presiserte at tidligere avklart logging skal videreføres.
- **Teknisk konsekvens:** PR-er og stories kan vise til beslutnings-ID-er uten å kopiere all teksten. Dokumentet oppretter ikke et parallelt loggsystem og overstyrer ikke andre prosjektinstruksjoner. Motstrid skal meldes til gruppen.
- **Berørte områder:** Beslutningsfil, PR #4, Story 1.2, prosjektstyring (referanser); eksisterende logger beholdes.
- **Ansvarlig/frist:** Ikke bestemt for selve beslutningsdokumentet.
- **Status:** Vedtatt.
- **Oppdatering 2026-11-04:** Regelen om underagenter i `AGENTS.md` (PR #5) er godkjent under OP-04. Dermed er det et vedtatt unntak fra «behold `AGENTS.md` uendret». Loggreglene er ikke endret. Se §11.
- **Oppdatering 2026-11-06:** Nytt vedtatt unntak fra «behold loggreglene uendret»: rene git-operasjoner logges ikke i sesjonsloggen. Endringen gjelder skillen `sesjonslogg` og avsnittet Sesjonslogg i `AGENTS.md`. Se §11.
- **Endring vedtatt 2026-11-08 (foreslått 2026-11-06, godkjent i PR #6, se §11):** Første del av vedtaket står uendret: gruppevedtak dokumenteres sporbart. Andre del, «behold eksisterende `AGENTS.md`, `CLAUDE.md`, KI-logging, sesjonslogger og andre loggregler uendret», erstattes av:
  - Disse filene og reglene kan endres når endringen registreres i §11 med dato, innhold og hvem som godkjente den.
  - Endringer i en branch godkjennes i PR-gjennomgangen.
  - Agenter endrer dem ikke uten uttrykkelig beskjed fra et gruppemedlem.
  - Kravene til KI-logg i `docs/ki-logg/` gjelder fortsatt.
  - **Begrunnelse:** Fryseregelen fikk to unntak på tre dager (OP-04 og sesjonsloggen), og den hindret vanlig vedlikehold, som å rette utdaterte tall og legge inn CI. Sporbarheten er den samme, fordi hver endring fortsatt registreres og gjennomgås. Se §11.

### AV-09 – Målevindu på 672 faktiske timer

- **Problemstilling:** 672 faktiske timer eller 28 lokale kalenderdager for historisk ulempbelastning?
- **Alternativer:** A: 672 faktiske timer. B: 28 lokale kalenderdager (kan bli 671/673 faktiske timer ved sommertidsskifte).
- **Codex:** Anbefalte A, halvåpent intervall og lokal kategorisering i `Europe/Oslo`.
- **Gruppens beslutning:** **A.** Bruk de siste **672 faktiske timene** før starttidspunktet for vakten som skal dekkes. Målevinduet er **halvåpent** `[start, vaktstart)`; lokal kategorisering skjer i `Europe/Oslo`.
- **Begrunnelse:** Unngå økt kompleksitet i v1.
- **Teknisk konsekvens:** Beregn vinduet fra faktiske tidspunkter, ikke ved å anta konstant lokal klokketid gjennom sommertidsskifter. Tell bare **overlappende del** av historiske vakter som krysser målevinduets grenser. Visningsperiode (AV-03) og beregningsvindu (AV-09) er forskjellige.
- **Berørte områder:** PRD, Story 1.2/4.7, seedhistorikk og tidstester.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-10 – Fast, reproduserbar historikk

- **Problemstilling:** Fast historikk i seeddata eller automatisk turnusgenerator?
- **Alternativer:** A: Fast seedhistorikk. B: Automatisk realistisk turnusgenerator.
- **Codex:** Anbefalte A, gjerne samme seedkommando som øvrige demodata, og historikk etablert før Story 1.2 blir `done`.
- **Gruppens beslutning:** **A.** Bruk et fast, forhåndsdefinert og reproduserbart sett med historiske vakter. **Ingen automatisk turnusgenerator for historikk i v1.**
- **Begrunnelse:** Reproduserbarhet og forenkling.
- **Teknisk konsekvens:** Historiske vakter må være gjenskapbare og dekke nødvendig målevindu, også delvis overlappende vakter. Gjenbruk av eksisterende seedkommando er **Codex sin implementasjonsanbefaling**, ikke et særskilt vedtatt teknisk valg. Story 1.2 må ha data på plass før `done`; Story 4.7 implementerer senere ulempberegningen.
- **Berørte områder:** Story 1.2, seeddata, testfasit og sprintstatus.
- **Åpent:** Datadekning kontrolleres i KS-04.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-11 – Behold eksisterende ulempmodell i v1

- **Problemstilling:** Beholde poengmodell 0/1/2/3 med tak 300 eller utvikle en mer fleksibel modell?
- **Alternativer:** A: Beholde foreslått modell. B: Mer fleksibel modell som krever ny spesifikasjon og tester.
- **Codex:** Anbefalte A.
- **Gruppens beslutning:** **A.** Vekter: **40 % kostnad, 20 % timebelastning, 15 % ulempbelastning, 25 % preferanser**. Ulempbelastning: **0/1/2/3 poeng per time** etter gjeldende tidskategorier, med **beregningstak 300**. Helligdager behandles som vanlige ukedager i v1. **Ingen innstillingsside** for vekter/poengsatsene.
- **Begrunnelse:** Ikke oppgitt.
- **Teknisk konsekvens:** Regelmotoren beregner poengene deterministisk; KI forklarer resultater. Taket innebærer at råbelastning over 300 ikke skilles videre av denne beregningsverdien. Eksakt mapping fra klokkeslett/dager til 0/1/2/3 og eksakt normaliseringsformel er **ikke fullstendig angitt i PDF-en** og må kontrolleres mot faktisk PRD/Story 4.7 (KS-02/KS-03), ikke oppfinnes her.
- **Berørte områder:** PRD, ÅB-1/3, Story 4.7, Story 4.4, arkitektur, memlog og KI-input.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

### AV-12 – Isoler effekten av ulempbelastning i testfasit

- **Problemstilling:** Hvordan dokumentere at ulempfaktoren faktisk påvirker rangering?
- **Alternativer:** A: «Nesten like» kandidater. B: Like øvrige faktorer og ulik ulempe.
- **Codex:** Anbefalte B, for eksempel 100 ulempoeng i forskjell og mulig utslag på 5 totalpoeng ved 15 % vekt og 300 som tak.
- **Gruppens beslutning:** **B.** Et reproduserbart testscenario skal ha minst to **gyldige** kandidater med identisk kostnad, timebelastning og preferansepoeng, men ulik historisk ulempbelastning. **Forventet totalscoreforskjell skal beregnes på forhånd og dokumenteres.**
- **Begrunnelse:** Ikke oppgitt.
- **Teknisk konsekvens:** Testen skal isolere ulempfaktorens effekt. Dersom faktoren omregnes lineært fra 0–300 til 0–100, vil 100 poeng forskjell gi `100 / 300 * 100 * 0,15 = 5` totalpoeng. **Dette er et betinget regneeksempel, ikke bekreftet testfasit:** KS-02 krever kontroll av faktisk formel først. Like øvrige verdier må behandles konsekvent med AV-05 og K-03.
- **Berørte områder:** PRD, Story 1.2/4.4/4.7, seeddata og testfasit.
- **Ansvarlig/frist:** Ikke bestemt.
- **Status:** Vedtatt.

## 4. Korrigeringspunkter (K-01–K-06)

Disse punktene kommer fra teknisk opprydding på side 5 av PDF-en. At de er **registrert**, betyr ikke at de er rettet. KS-01 tillater at K-01, K-02, K-04 og K-06 står åpne etter merge, **men** fraviker ikke eksisterende krav til PR-godkjenning.

### K-01 – Bekreftet regnefeil

- **Funn:** `22 + 2 × 21 + 3 × 29 = 151`, **ikke 136**.
- **Status:** Åpent. Det er ikke avtalt ansvarlig, frist eller konkret retting.
- **Codex-/faglig kontrollbehov:** Undersøk hvor 136 brukes i PR #4, PRD, Story 4.7, eksempler og eventuell fasit; vurder konsekvens av feilverdien.
- **Ikke vedtatt:** Ingen automatisk retting eller ny merge-blokkering er besluttet gjennom K-01.

### K-02 – Terskel for høy timebelastning

**Senere vedtak 2026-11-09 (P-04, gjeldende status):** Minst 32,4 timer før visningsavrunding. Ingrid beholdes på 32 timer og ligger under grensen. Story 1.2s dokumentforventning er rettet 2026-11-10; implementert visning og grensetester gjenstår. Linjene nedenfor gjengir den historiske statusen fra 02.11.

- **Funn:** Codex anbefaler nøyaktig `0,90 × 36 = 32,4 timer`; Ingrid med 32 timer ligger under **den anbefalte** terskelen.
- **Status:** Åpent. **32,4 timer er en Codex-anbefaling, ikke et gruppevedtak.**
- **Kontrollbehov:** Avklar om feilen gjelder eksempel, visning eller faktisk beregningslogikk. Ikke gjør «høy belastning» til en ekstra hard regel uten vedtak.
- **Ansvarlig/frist:** Ikke bestemt.

### K-03 – Avrunding

- **Status:** Vedtatt.
- **Gruppens beslutning:** Beregn faktorpoeng og totalscore og sorter kandidater ut fra **uavrundede** verdier; avrund **kun til visning**, med **én desimal**.
- **Konsekvens:** Lik visningsscore er ikke nødvendigvis lik uavrundet totalscore. Stigende ansatt-ID (AV-05) brukes kun ved reelt lik totalscore. Testfasit må kontrollere dette.
- **Åpent teknisk detaljspørsmål:** Eksakt avrundingsregel ved verdier midt mellom to tideler er ikke uttrykkelig avtalt. Følg eksisterende prosjektkontrakt eller forelegg motstrid for gruppen; ikke oppfinn en ny produktregel.
- **Ansvarlig/frist:** Ikke bestemt.

### K-04 – Datakontrakten `RangertKandidat` og KI-input

**Senere vedtak 2026-11-09 (P-06/P-07, gjeldende status):** Produktkravene om strukturerte, faktakontrollerte begrunnelser og én forhåndsberegnet gyldig referanse er fastsatt. Kontrakt og negative tester gjenstår i story 5.3/5.4. Linjene nedenfor er historisk status fra 02.11.

- **Status:** Åpent; ingen konkret endring godkjent.
- **Codex-anbefaling:** Samordne `RangertKandidat` i epics, arkitektur og KI-input med vedtatt rangeringsmodell og ulempfelt. Domenet/regelmotoren beregner faktor- og totalscore, KI forklarer.
- **Kontrollbehov:** Finn faktiske forskjeller før forslag til retting legges frem. Ingen agent får gjennom K-04 alene mandat til å endre kontrakten eller lage ny funksjonalitet.
- **Ansvarlig/frist:** Ikke bestemt.

### K-05 – Sporbarhet og eksisterende KI-logging

- **Status:** Prinsipp vedtatt; dekning skal kontrolleres senere.
- **Gruppens beslutning:** **Ingen endring** i eksisterende logging, `AGENTS.md`, `CLAUDE.md` eller andre loggregler. Kontroller senere om eksisterende logg/dokumentasjon ivaretar prompt-, rettings-, review- og kontrollsporbarhet, inklusive grunnlag for tak på 300.
- **Konsekvens:** Rapporter eventuelle mangler uten automatisk å opprette parallelle logger eller nye rutiner.
- **Ansvarlig/frist:** Ikke bestemt.

### K-06 – Dokumentkvalitet og status

**Oppfølging 2026-11-10:** De identifiserte P-vedtakene er samordnet i PRD og berørte dokumenter, med [valideringsrapport](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/validation-report-2026-11-10.md). Dette lukker ikke generell dokumentkontroll ved senere implementasjon. Linjene nedenfor beskriver status 02.11.

- **Status:** Åpent; Codex-anbefalingen er **ikke** et gruppevedtak om korrigering.
- **Codex-funn:** Utdatert beskrivelse av kostnadsmodell, feil lenker og misvisende status som «løst» uten godkjenning.
- **Kontrollbehov:** Finn konkrete forekomster, skill åpenbar retting fra kravendring, og legg frem konflikter. Ikke merk uavklarte punkter som løst.
- **Ansvarlig/frist:** Ikke bestemt.

## 5. Oppfølgingspunkter (OP-01–OP-09)

### OP-01 – Eksplisitt avgrensning av v1

- **Status:** Vedtatt.
- **Beslutning:** V1 skal **ikke** omfatte omfattende tariffmodell, separat fraværsmodell, utvidet modell for stillingsprosenter, særskilt helligdagsmodell eller omfattende juridisk kontroll.
- **Konsekvens:** Disse er utenfor v1; senere utvikling krever ny prioritering. Eksisterende kompetanse-, kollisjons-, hvile- og kostnadsregler oppheves ikke.
- **Ansvarlig/frist:** Ikke bestemt.

### OP-02 – UX, mobil og mockuper

- **Status:** Vedtatt.
- **Beslutning:** Samordne relevante mockuper og grensesnittbeskrivelser med **fire vakttyper nå**. Detaljert UX, mobiltilpasning og brukerprøving prioriteres etter at en fungerende kandidatvisning finnes.
- **Konsekvens:** Grunnleggende forståelig kandidatvisning er fortsatt del av kjerneflyten; dette innebærer ikke å utsette hele grensesnittet.
- **Ansvarlig/frist:** Ikke bestemt; senere milepæl er fungerende kandidatvisning.

### OP-03 – KI-feilhåndtering ved preferansetolkning

**Senere vedtak 2026-11-09 (P-05, gjeldende status):** Venting/feil for registrert tekst gir midlertidig 50 poeng med egen status; avgrensede automatiske forsøk og brukerutløst nytt forsøk er valgt. Implementasjon/test gjenstår før story 5.1/5.2 kan være ferdige. Linjene nedenfor er historisk status fra 02.11.

- **Status:** Prioritering vedtatt; teknisk løsning åpen.
- **Beslutning:** Detaljert håndtering kan utsettes, **men skal være avklart før Story 5.1 og 5.2 er `done`**.
- **Konsekvens:** Ingen bestemt fallback eller feilrespons vedtas nå; manglende svar, feil format og feil tolking er aktuelle forhold å avklare senere.
- **Ansvarlig:** Ikke bestemt. **Frist:** Før `done` for Story 5.1/5.2; ingen kalenderdato.

### OP-04 – Agentoppsett og underagenter

- **Status:** Prinsipp vedtatt; gjennomgang gjenstår.
- **Beslutning:** Behold agentoppsett og prosjektinstruksjoner **uendret**. Gjennomgå agentpraksis, eventuelle underagenter og bevaring av reviewfunn **før neste `bmad-build`**; ikke endre oppsett automatisk.
- **Ansvarlig:** Ikke bestemt. **Frist:** Før neste `bmad-build`; ingen kalenderdato.
- **Oppdatering 2026-11-04 – Vedtatt:** Agentoppsettet er gjennomgått og godkjent av Johannes W. Gaertner på vegne av gruppa, sammen med PR #5. `bmad-build` kjøres med underagenter: én samler epic-konteksten, og egne agenter gjennomgår koden uten å ha sett implementeringen. Regelen står i `AGENTS.md`. Reviewfunnene bevares i spesifikasjonens Review Triage Log. Se §11.

### OP-05 – Ren klone og plattformtesting

- **Status:** Delvis vedtatt 2026-11-07 (§11). Fysisk test på macOS/Linux er strøket. Test fra ren klone er fortsatt ikke avtalt.
- **Codex-anbefaling (ikke vedtak):** Test fra ren GitHub-klone, Python 3.12 og macOS/Linux før Story 1.2 er `done`; oppdater vurderingsmatrise ved milepæler.
- **Konsekvens:** OP-05 innfører **ingen nye** ferdigkriterier. Eksisterende tester og vedtatte AV-/KS-krav gjelder fortsatt.
- **Ansvarlig/frist:** Ikke bestemt.

### OP-06 – Arbeidsrekkefølge

- **Status:** **Forslag, ikke vedtatt.**
- **Codex-forslag:** 1) Avklar A/B og vakttider; 2) avklar øvrige beslutninger; 3) samordne PR #4 og testfasit; 4) ny PR-review før eventuell merge; 5) klargjør Story 1.2 til `ready-for-dev`, implementer seeddata/tester; 6) bygg kjerneflyt og Story 4.7.
- **Gruppens avklaring:** Listen skal **kun** dokumenteres som forslag. Den etablerer ikke bindende plan, ny frist eller automatisk godkjenning av åpne K-punkter. De 12 beslutningene er gjennomgått; gjennomført kode-/PR-arbeid er ikke bekreftet.
- **Ansvarlig/frist:** Ikke bestemt.

### OP-07 – Ansvar for PR #4

- **Status:** Vedtatt.
- **Beslutning:** **Ragnhild Sætren** har ansvar for oppfølging og retting av PR #4.
- **Avgrensning:** Dette tildeler henne ikke automatisk ansvar for alle K-punkter eller alle konkrete endringer.
- **Frist:** Ikke avtalt.

### OP-08 – Ansvar for Story 1.2

- **Status:** Vedtatt.
- **Beslutning:** **Mithad Kuduz** er ansvarlig for oppdatering av Story 1.2.
- **Avgrensning:** Ingen nye oppgaver eller frister er tildelt gjennom dette punktet alene.
- **Frist:** Ikke avtalt.

### OP-09 – Ny review av PR #4

- **Status:** Åpent.
- **Møteopplysning:** **Ingen frist ble avtalt** for ny review av PR #4. Dette betyr ikke at review er unødvendig.
- **Konsekvens:** Ingen kalenderfrist innføres; eksisterende godkjenningskrav gjelder.
- **Ansvarlig:** Ikke bestemt for review; Ragnhild er ansvarlig for oppfølging av PR #4 (OP-07).

## 6. Konsistenskontroller (KS-01–KS-04)

### KS-01 – Åpne korrigeringer ved merge

- **Status:** Vedtatt.
- **Beslutning:** K-01, K-02, K-04 og K-06 **kan forbli åpne etter merge** av PR #4, **underlagt gjeldende PR-godkjenningskrav**.
- **Konsekvens:** Åpen status betyr ikke «løst», «akseptert feil» eller «godkjent kode». Hvis en kjent feil hindrer oppfyllelse av eksisterende krav, må den håndteres etter disse kravene. Dette er ikke et vedtak om at alle feil må lukkes før merge.
- **Ansvarlig/frist:** Ikke bestemt.

### KS-02 – Verifiser formel før testfasit godkjennes

- **Status:** Kontrollkrav vedtatt; kontroll ikke gjennomført.
- **Beslutning:** Kontroller eksisterende rangeringsformel mot **PRD og Story 4.7** før relevant testfasit godkjennes. Motstrid legges frem for gruppen før endringer.
- **Konsekvens:** 100 ulempoeng → 5 totalpoeng er bare et betinget eksempel frem til omregningen er verifisert. Ikke endre AV-11/AV-12 for å få kode og fasit til å stemme.
- **Ansvarlig:** Ikke bestemt. **Frist:** Før godkjenning av relevant testfasit.
- **Oppdatering 2026-11-04 – Utført for Story 1.2:** I spesifikasjonen for Story 1.2 står det at rangeringsfasiten for #4127 er kontrollert mot PRD §4.4 etter KS-02. Totalscorene er regnet for hånd på nytt med min–maks (AV-05) og vektene 40/20/15/25, og de stemmer: Jonas 85,65, Mette 78,65, Thomas 59,0 og Ingrid 37,0. Fasiten er godkjent med PR #5. Kontrollen gjelder bare denne fasiten. Ny eller endret fasit, blant annet i Story 4.4 og 4.7, må kontrolleres på nytt. Se §11.

### KS-03 – Verifiser tidskategorier for alle fire vakttyper

- **Status:** Kontrollkrav vedtatt; kontroll ikke gjennomført.
- **Beslutning:** Kontroller eksisterende tidskategorier og 0/1/2/3-regler for **dag, mellom, kveld og natt** før **implementasjon av Story 4.7** og ferdigstilling av tilhørende fasit. Legg frem mangler og motstrid for gruppen.
- **Konsekvens:** Ingen nye klokkeslett, poengsatser eller kategorier er vedtatt her. Se AV-02/AV-09/AV-11.
- **Ansvarlig:** Ikke bestemt. **Frist:** Nevnte milepæler; ingen kalenderdato.

### KS-04 – Datadekning ved periodegrenser

- **Status:** Kontrollkrav vedtatt; kontroll ikke gjennomført.
- **Beslutning:** Før Story 1.2 er `done`, kontroller at seeddata dekker **nødvendig historikk**, **relevante nabovakter før og etter** og **komplette berørte kalenderuker** for vedtatte beregninger og hvilekontroller. Mangler forelegges gruppen.
- **Konsekvens:** 672 timer historikk for ulempe er ikke nødvendigvis nok for hvilekontroll; det kan også trenges etterfølgende planlagte vakter. Kontrollen gjelder relevante demonstrasjonsscenarioer og introduserer ingen turnusgenerator. Story 4.7 trenger ikke være ferdig bare fordi Story 1.2 skal bli `done`.
- **Ansvarlig:** Ikke bestemt. **Frist:** Før Story 1.2 markeres `done`.
- **Oppdatering 2026-11-04 – Utført:** Mithad Kuduz har kontrollert datadekningen i PR #5 (commit `d00d557`). Den er låst med `test_datadekning_ved_periodegrensene_ks04` i `backend/tester/lagring/test_testdata.py`, for #4127 og #4189. Kjent begrensning: det finnes ingen vakter etter natten 04.–05.10, så en vakt helt sist i perioden får ikke full kontroll av hvilen etterpå. Begrensningen er godtatt av Johannes W. Gaertner på vegne av gruppa. Se §11.

## 7. Samlede konsekvenser for prosjektfiler og funksjoner

**Historisk endrings-/kontrolloversikt fra 02.11, ikke gjeldende status.** Senere vedtak og kontroller er ført i §11–§12. Tabellen er beholdt for å vise hva gruppen skulle undersøke på møtet; kontroller filnavn, faktiske stier og nåværende innhold før gjennomføring.

| Område | Må samsvare med vedtak/kontroller | Status og merknad |
|---|---|---|
| **PR #4** | AV-01/02/11, øvrige relevante AV-er, K-01/02/04/06 og KS-01 | Ragnhild følger opp. Review/merge skjer etter eksisterende prosess. Åpne K-punkter kan bli stående etter merge. |
| **Story 1.2** | Fire vakttyper, visningsperiode, hvileantakelser, seeddata, tilgjengelighet, historikk, testfasit | Mithad følger opp spesifikasjonsoppdatering. `ready-for-dev` er ikke `done`; KS-04 må kontrolleres før `done`. |
| **Story 1.5** | AV-02/03: vakttider, starttidsbasert periodevisning | Kontroller mot eksisterende innhold. |
| **PRD / Product Brief** | Scope (AV-01, OP-01), vaktmaler, visnings-/hvilekontroll, vekter og rangeringsregler | Motstrid må avklares; ikke anta at tidligere dokumenttekst er gjeldende vedtak. |
| **Epics og øvrige stories** | Story 4.4/4.7: rangering og ulempe; Story 5.1/5.2: feilhåndtering før `done` | Ikke marker stories som `done` bare fordi vedtak finnes. |
| **Arkitektur / datakontrakt** | Skille mellom deterministisk regelmotor og KI-forklaring; `RangertKandidat` | K-04 står åpent; konkreter må verifiseres og eventuelt forelegges gruppen. |
| **DESIGN / EXPERIENCE / mockuper / UX** | Fire vakttyper; forståelig kjerneflyt og kandidatvisning | Samordne vakttidene nå; detaljert UX, mobil og brukerprøving senere (OP-02). |
| **Seeddata og testfasit** | #4127/#4189, gyldige/utelukkede kandidater, ikke-billigste-først, min–maks/tie-break, ulempe, grensekryssing | KS-02/03/04 krever kontroll. Fast og reproduserbart, ikke generator. |
| **KI-logging / memlog / sesjonslogger** | Historikk over KI-arbeid og kontrollgrunnlag | Ingen endring i loggregler (AV-08/K-05). Undersøk senere om sporbarhet dekker tak 300. |
| **Prosjektstyring / issues.md / sprintstatus** | Henvisninger til vedtak og åpne oppgaver, ansvar, reell story-/PR-status | Oppdater ved faktisk arbeid; ikke lukk punkter uten avklaring. OP-06 er ikke vedtatt plan. |

## 8. Prioritert oppfølgingsliste

Prioritetskategoriene nedenfor skiller **allerede vedtatte krav** fra **forslag om prioritering**. En anbefalt kategori skaper ikke i seg selv en ny merge-/ferdigblokkering. Ingen dato eller person er lagt til uten vedtak.

### 8.1 Kritisk før merge – kontroller etter gjeldende godkjenningskrav

| Oppgave | Grunnlag | Forpliktelse/status | Ansvar |
|---|---|---|---|
| Avstem PR #4 mot AV-01–AV-12 og eksisterende review-/godkjenningskrav. | AV-08, OP-07, KS-01, PDF side 1 og 5 | **Gjeldende godkjenningskrav består.** Ikke påstå at PR er godkjent. | Ragnhild: overordnet PR-oppfølging |
| Gjennomgå betydning av feil/motstrid i K-01, K-02, K-04 og K-06 for PR-en. | K-01/02/04/06, KS-01 | **Anbefalt kontroll**, ikke vedtatt krav om å lukke punktene før merge. Punktene kan være åpne etter merge. | Ikke fordelt per K-punkt |
| Sikre sporbarhet til beslutninger når PR faktisk revideres. | AV-08 | Vedtatt dokumentasjonsprinsipp; følg eksisterende PR-regler. | Ikke separat fordelt |

### 8.2 Må gjøres før `ready-for-dev` – eksisterende spesifikasjonskrav

| Oppgave | Grunnlag | Forpliktelse/status | Ansvar |
|---|---|---|---|
| Samordne Story 1.2-spesifikasjonen med vedtakene om vaktmaler, perioder, hvile, tilgjengelighet, seeddata og fasit. | AV-02–AV-07, AV-09–AV-10 | Må være tilstrekkelig avklart for eksisterende `ready-for-dev`-kriterier; ingen kode ferdig ved dette steget. | Mithad: Story 1.2-oppdatering |
| Gjør faktiske uavklarte spesifikasjonskonflikter synlige før godkjenning. | AV-08, K-04/K-06 | Agentene skal ikke finne på løsninger eller lukke åpne punkter på egen hånd. | Ikke særskilt fordelt |

### 8.3 Må gjøres før `done` / relevante godkjenninger

| Oppgave | Grunnlag | Når | Ansvar |
|---|---|---|---|
| Etabler og test reproduserbare seeddata/historikk og avtalte scenarioer. | AV-07, AV-10 | Før Story 1.2 er `done` i samsvar med prosjektets øvrige kriterier. | Mithad: Story 1.2-oppdatering; implementeringsansvar ellers ikke bestemt |
| Kontroller datadekning for historikk, nabovakter og kalenderuker. | KS-04 | **Før Story 1.2 er `done`.** Utført 2026-11-04 (§11). | Ikke særskilt fordelt |
| Kontroller tidskategorier for fire vakttyper. | KS-03 | **Før implementasjon av Story 4.7** og ferdigstilling av tilhørende fasit. | Ikke bestemt |
| Verifiser rangeringsformelen mot PRD/Story 4.7. | KS-02 | **Før godkjenning av relevant testfasit.** Utført for fasiten i Story 1.2 2026-11-04 (§11); ny fasit kontrolleres på nytt. | Ikke bestemt |
| Implementer/test ulempmodell etter vedtakene uten å endre dem. | AV-01, AV-09, AV-11/12 | Som del av Story 4.7 i v1, etter gjeldende story-kriterier. | Ikke bestemt |
| Avklar relevant KI-feilhåndtering ved preferansetolkning. | OP-03 | **Før Story 5.1 og 5.2 er `done`.** | Ikke bestemt |

### 8.4 Kan vente / ikke tidfestet

| Oppgave | Grunnlag | Status/avgrensning |
|---|---|---|
| Kontrollér om eksisterende logging dekker sporbarhet og begrunnelse for tak 300. | K-05 | Kontroll åpen; ingen loggendringer vedtatt. |
| Gjennomgå agentpraksis/underagenter og bevar reviewfunn. | OP-04 | Gjennomført og godkjent 2026-11-04; regelen om underagenter står i `AGENTS.md` (§11). |
| Detaljert UX, mobiltilpasning og brukerprøving. | OP-02 | Etter fungerende kandidatvisning; mockuper med fire vakttyper samordnes nå. |
| Avklar ren klone, Python 3.12, macOS/Linux og vurderingsmatrise. | OP-05 | macOS/Linux strøket 2026-11-07; ren klone fortsatt åpen. Python 3.12 er verifisert på Windows 2026-11-04 (sprint-status). |
| Fastsett eventuell bindende arbeidsrekkefølge. | OP-06 | Codex-rekkefølgen er kun et forslag. |
| Avtal frist for ny PR-review. | OP-09 | Ingen frist vedtatt. |
| Eventuell videreføring av tariff-, fraværs-, stillingsprosent-, helligdags- og omfattende lovmodell. | OP-01 | **Utenfor v1**; krever nytt vedtak før eventuell utvikling. |

## 9. Instruksjoner til Codex, Claude og andre KI-agenter

1. **Les før relevante endringer:** Bruk dette dokumentet sammen med gjeldende PRD, stories og repoets eksisterende `AGENTS.md`, `CLAUDE.md` og loggregler. Filer må ikke antas å ha samme navn/sted som i PDF-en uten kontroll.
2. **Ikke overstyr agentinstruksjoner:** `avklaringspunkter.md` dokumenterer gruppevedtak, men gir **ikke** tillatelse til å overstyre `AGENTS.md`, `CLAUDE.md`, sikkerhetsregler eller gjeldende prosjektprosess. Ved konflikt: rapporter fil, punkt og foreslått løsning; be gruppen om avklaring.
3. **Skill beslutning fra anbefaling:** «Vedtatt» er bindende innenfor gyldig scope. «Åpent», «Forslag» og «Kontroll gjenstår» er ikke godkjente tekniske løsninger. Ikke merk åpne punkter som løst uten dokumentert godkjenning.
4. **Ingen nye krav på eget initiativ:** Ikke endre vekter, ulempoeng, tidskategorier, vakttyper, hviletolkning eller annet sentralt prosjektvalg uten å legge frem konsekvensene og innhente beslutning.
5. **Bevar sporbarhet:** Henvis til konkrete ID-er (`AV-xx`, `K-xx`, `OP-xx`, `KS-xx`) i PR/story når relevant. Følg **eksisterende** KI-logging, sesjonslogger og reviewpraksis. Ikke dupliser hele referatet i andre dokumenter.
6. **Regelmotor før KI:** Hardregelkontroll og rangering er deterministisk. KI forklarer beregnede resultater og må ikke innføre ugyldige kandidater eller egen rangering.
7. **Fremlegg motstrid og usikkerhet:** Særlig gjelder dette `RangertKandidat` (K-04), formel/normalisering (KS-02), tidskategorier (KS-03), datadekning (KS-04), terskel 32,4 (K-02) og dokumentfeil (K-06). Ikke fyll hull med antakelser som presenteres som vedtak.
8. **Respekter godkjenningstrinn:** `ready-for-dev` er ikke `done`; merge av PR er ikke automatisk faglig godkjenning. KS-01 tillater fortsatt åpne K-punkter, men opphever **ikke** eksisterende godkjenningskrav.
9. **Ingen uønskede repo-operasjoner:** Dette referatet autoriserer ingen automatisk commit, push, merge, oppdatering av agentinstruksjoner eller endring av øvrige filer. Gjennomføring skjer etter egen oppgave og gjeldende prosjektpraksis.

### Forslag til korte referanser fra agentinstruksjoner (ikke utført)

Dersom gruppen senere ønsker å gjøre dokumentet enklere å oppdage, kan en **kort lenke** legges inn i `AGENTS.md` eller `CLAUDE.md` *etter særskilt godkjenning* – ikke kopier hele dokumentet:

```md
Prosjektbeslutninger fra gruppemøtet 2026-11-02: se docs/beslutninger/avklaringspunkter.md.
Respekter dokumentets statusmarkeringer; ved konflikt med øvrige prosjektinstruksjoner, meld fra og be om avklaring.
```

> Dette er kun et **forslag** til fremtidig referanse. AV-08 og OP-04 innebærer at eksisterende agentinstruksjoner **foreløpig beholdes uendret**. Dersom faktisk lagringssted blir et annet, må lenken tilpasses.
>
> **Oppdatering 2026-11-04:** OP-04 er vedtatt, og regelen om underagenter i `AGENTS.md` er godkjent (§11).

## 10. Kilder og gyldighet

- **Hovedgrunnlag:** [IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf](IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf), oppdatert 2026-10-31, seks sider. PDF-en bygger på to Codex-analyser og var et **forslag til beslutningsgrunnlag**, ikke en registrering av vedtak.
- **Faktiske gruppevedtak:** Formidlet fra møtet 2026-11-02 og bekreftet punkt for punkt av gruppens representant i den påfølgende samtalen. Der gruppen ikke oppga begrunnelse, ansvar eller frist, står det eksplisitt «ikke oppgitt»/«ikke bestemt».
- **Kontrollbegrensning:** Dette dokumentet er **ikke** en gjennomgang av nåværende kildekode eller repository-innhold. Verken PR #4 eller Story 1.2 er endret gjennom utarbeidelsen av denne filen. Ingen tester, merges, commits eller pushes er utført.

## 11. Oppdateringer etter møtet

### 2026-11-04 – Godkjenning av PR #5 (Story 1.2)

- **Hvem:** Johannes W. Gaertner, som har godkjent på vegne av gruppa.
- **Grunnlag:** Gjennomgang av PR #5, «Story 1.2: Fiktiv turnus med ansatte og vakter». Installasjonen virket, testdata-kommandoen ga samme resultat to ganger, og `pytest` ga 35 av 35 bestått. Rangeringsfasiten for #4127 er regnet for hånd på nytt. Detaljer: `.logs/johagartnerhimolde/998-2026-11-04-09-45-04-status-og-pr-5.md`.
- **Godkjent:**
  - PR #5 som helhet.
  - **OP-04:** Agentoppsettet med underagenter i `bmad-build`. Regelen i `AGENTS.md` fra PR #5 står, og AV-08 har fått en henvisning til dette unntaket.
  - **AV-10:** Radene ble skrevet ut med kladdeskript utenfor appen, og kladdeskriptene ligger i `docs/ki-logg/2026-11-03-testdata/`. Repoet har bare de faste radene, og det oppfyller AV-10. Det er fortsatt ingen turnusgenerator i appen.
  - **KS-04:** Kontrollen av datadekningen er godtatt, med den kjente begrensningen etter 05.10. Se §11, 2026-11-11 (Story 2.3): vakter som slutter etter 04.10 kl. 13:00 gir nå datafeil.
  - **KS-02:** Fasiten for #4127 er godkjent etter kontrollen som er beskrevet under KS-02.
  - **Valg spesifikasjonen ikke avgjorde:** Andre vakter har minstenivå 2, Eirik har ingen vakter i uke 40, og helgen 26.–27.09 er tynt bemannet.
- **Ikke endret:** Ingen andre AV-, K-, OP- eller KS-punkter. Ragnhilds åpne punkt om gamle vakttider i spesifikasjonen for Story 1.2 er løst i PR #5, men lukkes i hennes egen `issues.md`.

### 2026-11-06 – Rene git-operasjoner logges ikke i sesjonsloggen

- **Hvem:** Gruppa, etter anbefaling fra faglærer. Formidlet av Johannes W. Gaertner.
- **Grunnlag:** Faglærer: «Egne gitoperasjoner er ikke nødvendig å logge. Det ligger i git historikken uansett.» Sesjonsloggen skal dokumentere arbeidsprosessen, og det trengs ingen logg når ingenting i prosjektet endres, for eksempel når repoet oppdateres lokalt.
- **Vedtatt:**
  - Commit, pull, fetch, push, merge, rebase og opprettelse eller sletting av brancher logges ikke. Hører de til en større oppgave, nevnes de bare som faktum i Resultat.
  - Avgrensningen fra 2026-11-02, som bare gjaldt pull, fetch og push, er utvidet til alle rene git-operasjoner.
  - Logger som bare dokumenterer git-operasjoner, er fjernet. Med faglærerens uttrykkelige tillatelse for dette tilfellet ble alle loggmappene gjennomgått. Bare én fil var en ren git-logg, og den lå i Johannes' mappe. De andre filene inneholder også annet arbeid og er beholdt.
- **Endret:** `.claude/skills/sesjonslogg/SKILL.md`, beskrivelsen i `.agents/skills/sesjonslogg/SKILL.md`, avsnittet Sesjonslogg i `AGENTS.md` og AV-08.
- **Ikke endret:** KI-loggingen i `docs/ki-logg/` og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-06 – Automatisk kontroll av speilingen, ny ordlyd i AV-08 og ny regel for branch og PR (foreslått, vedtatt 2026-11-08)

- **Hvem:** Foreslått av Johannes W. Gaertner. Gjelder når PR-en fra branchen `ci-skills-speiling` er godkjent av gruppa. Vedtatt 2026-11-08, se «Godkjenning av PR #6» under.
- **Grunnlag:** `.agents/skills` (Codex) og `.claude/skills` (Claude Code) holdes like bare av en skriftlig regel i `AGENTS.md`. En gjennomgang 2026-11-06 viste at de var like, bortsett fra det vedtatte unntaket `sesjonslogg`. Ingen hook, CI eller test fanget opp avvik.
- **Foreslått:**
  - Testen `scripts/test_skills_speiling.py` og workflow-filen `.github/workflows/skills-speiling.yml` sjekker speilingen ved hver push. Dette er prosjektets første CI.
  - I `AGENTS.md` er TODO-en om CI erstattet med en beskrivelse av hva CI kjører. Tallet «214» i fallgruven om linjeskift er fjernet.
  - AV-08 får ny ordlyd i andre del (se AV-08).
  - **Regelen for branch og PR i `AGENTS.md` (Policy):** «Utvidelser av funksjonalitet går i egen branch» erstattes av en menneskelig vurdering.
    - Den enkelte avgjør aktivt om arbeidet skal i branch og PR, ut fra hvor stort det er og hvor mange definerende avgjørelser det inneholder.
    - Avgrensede endringer kan gå rett på `main`. Større endringer, og avgjørelser som binder gruppa, bør gjennomgås av et annet gruppemedlem i en PR.
    - Agenter foreslår, men oppretter ikke branch eller PR uten at brukeren har valgt det.
    - Kvalitetssikringen må kunne spores uansett vei: PR-gjennomgangen, eller commit-meldingen og KI-loggen.
    - **Begrunnelse:** Gruppa stoler på hverandre. En maskinell regel sendte også små endringer til PR. Sensorveiledningen godtar «branches, pull requests, issues eller tilsvarende» og beskrivelser av rettede KI-feil som spor av gjennomgang.
- **Ikke endret:** Første del av AV-08 og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-06 – Designtokens, layoutbredde og Story 1.3 (AV-13, AV-14, OP-10)

- **Hvem:** Johannes W. Gaertner, som har vedtatt på vegne av gruppa.
- **Grunnlag:** Antakelsesgjennomgang og beslutningsforslag (Assumption Audit og Architecture Decision Records i `bmad-advanced-elicitation`) av anbefalingen om neste steg. Begge spørsmålene var åpne punkter fra UX-vurderingen samme dag og kom til forfall fordi Story 1.3 er første story som bygger designtokens og appbar. Detaljer: `.logs/johagartnerhimolde/994-2026-11-06-17-05-00-ux-vedtak-og-story-1-3.md`.
- **AV-13 – Skriftstørrelser i `rem`:**
  - Typografitokenene skrives i `rem` med 1rem = 16px, og `px`-verdien fra DESIGN.md står i en kommentar (for eksempel `--font-body: 0.78125rem; /* 12.5px */`). DESIGN.md beholder `px` som kilde.
  - Spacing, kantlinjer, radius, sporing og faste bredder (`login-card` 360px, belastningslinja 110×7px) er i `px`.
  - Ingen komponent bruker rå størrelser utenfor tokenene. Faste mål som 360px og 110×7px blir egne tokens.
  - Tekstbeholdere har ikke fast høyde, slik at teksten ikke klippes når skrifta vokser.
  - Kontroll: manuell test med nettleserens standard skriftstørrelse satt til 20px, dokumentert i storyen som innfører tokenene.
  - Begrunnelse: Tekst på 10,5–12,5px følger da brukerens skriftinnstilling, mens tabelltettheten og skarpe kanter beholdes. Zoom virket allerede med `px`. Forkastet: alt i `px` (ignorerer skriftinnstillingen) og alt i `rem` (spacingen vokser, tabellen mister tettheten, og kanter gir brøkpiksler).
- **AV-14 – Layoutbredde:**
  - Appbaren går over hele bredden. Innholdsflaten får `max-width: 1180px`, `margin-inline: auto` og `padding-inline` lik `content-padding` (22px).
  - `login-card` får `width: min(360px, 100% - 32px)`.
  - Under 1180px ruller brede tabeller vannrett inne i sin egen beholder fram til Story 4.6. Breakpoints og stabling er fortsatt utsatt (OP-02).
  - Begrunnelse: 1180px er bredden på `.browser`-rammen i mockupene (`key-innlogging.html:30–31`), en presentasjonsramme som skyggen DESIGN.md beskriver, og aldri en designbeslutning. Forkastet: fast 1180px (gir vannrett rulling av hele siden) og helt flytende (for brede tabeller på store skjermer).
- **OP-10 – Story 1.3:**
  - Johannes W. Gaertner tar Story 1.3.
  - Anbefalt, ikke tildelt: et annet gruppemedlem kan starte domenedelen av Story 2.1 parallelt, på testdataene fra Story 1.2. Rekkefølgen er fortsatt ikke bindende (OP-06).
  - Avklares i spesifikasjonen for Story 1.3, ikke vedtatt her: (1) hvordan cookien når API-et, med Vite-proxy for `/api` eller CORS med credentials; (2) hvordan sensor får en testbruker fra en ren klone, og hva som skjer når passord- eller nøkkelvariabelen mangler; (3) bibliotek for JWT og passordhashing, sett opp mot det åpne punktet om eksakte versjonslåser; (4) ny brukertabell i skjemaet.
- **Endret:** DESIGN.md (Typography, Layout & Spacing), EXPERIENCE.md (Responsive & Platform), UX-DR1, UX-DR4 og Story 1.3 i `epics.md`.
- **Ikke endret:** OP-02, OP-06 og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-06 – OP-10 avklart i spesifikasjonen for Story 1.3

- **Hvem:** Johannes W. Gaertner, i spesifikasjonen `_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md` (Beslutninger). Implementert på branchen `story-1.3-innlogging` 2026-11-07. KI-logg: `docs/ki-logg/2026-11-06-innlogging.md`.
- **Svarene på de fire spørsmålene:**
  1. Cookien når API-et gjennom Vite-proxy for `/api` til `http://127.0.0.1:8000`. Samme opphav gir `SameSite=Strict` og ingen CORS.
  2. Testbrukeren `kari.vestby` lages av testdatakommandoen. Er `TURNUSHJELPEREN_PASSORD` satt, er passordet personlig (varianten ved innlevering, valgt av den som installerer). Mangler den, lages et tilfeldig testpassord som skrives ut og gjelder til neste kjøring (varianten når gruppa tester). Utløpstiden er 480 minutter når `TURNUSHJELPEREN_JWT_MINUTTER` mangler. En ugyldig verdi stopper API-et.
  3. PyJWT 2.15.1, låst eksakt som de andre pakkene, med HS256. Passordhash med `hashlib.scrypt` fra standardbiblioteket og tilfeldig salt per bruker.
  4. Tabellen `bruker` med `id`, `brukernavn` (unik), `navn`, `passord_hash`, `passord_kilde` og `turnus_id`.
- **Avvik fra epics:** JWT-nøkkelen leses ikke fra miljøet, slik akseptansekravet i epics sa. Den lages tilfeldig (`secrets.token_bytes(32)`) ved hver oppstart og holdes bare i minnet. Begrunnelse: en fast nøkkel gir bare at sesjonen overlever en omstart, og en nøkkel som aldri skrives ned, kan ikke lekke. Konsekvens: alle logges ut når API-et starter på nytt, også ved `--reload`.
- **Endret:** Story 1.3 i `epics.md`, `ARCHITECTURE-SPINE.md` (miljøvariablene og den utsatte beslutningen om utløpstid) og `epic-1-context.md`.
- **Ikke endret:** Eksakte versjonslåser generelt er fortsatt ikke drøftet i gruppa; PyJWT er låst eksakt fordi de andre pakkene er det. De andre AV-, K-, OP- og KS-punktene.

### 2026-11-07 – Fysisk test på macOS/Linux strøket (OP-05)

- **Hvem:** Johannes W. Gaertner, under den manuelle testen av Story 1.3.
- **Beslutning:** Fysisk test på macOS/Linux strykes. Verken sensor eller noen i gruppa har Mac. Koden skrives likevel etter god programmeringsskikk for å virke på tvers av operativsystem, og README beholder kommandoene for macOS/Linux. Regelen står under «Konvensjoner» i `AGENTS.md`.
- **Kontrollert i stedet:** bash-kommandoene for passordvariantene i README er kjørt i Git Bash på Windows 2026-11-07, mot en midlertidig database. `IFS= read -rsp` beholdt mellomrom først og sist i passordet, og innloggingen virket med det. Variant B ga et tilfeldig passord på 12 tegn.
- **Fortsatt åpent i OP-05:** om og når det skal testes fra en ren klone.
- **Endret:** `AGENTS.md`, `README.md`, vurderingsmatrisen, KI-loggen for Story 1.3 og handlingspunktet for PR #3 i `sprint-status.yaml`.

### 2026-11-08 – Godkjenning av PR #6 (speiling av skills i CI, AV-08 og regelen for branch og PR)

- **Hvem:** Mithad Kuduz godkjente PR #6 på GitHub 2026-11-08. Han skrev at godkjenningen gjelder begge forslagene, slik PR-beskrivelsen sier. Johannes W. Gaertner, som foreslo endringene, merget PR-en samme dag (`9939cfa`) og registrerte vedtaket.
- **Grunnlag:** Mithad kjørte speilingstesten, og den ga 3 av 3 OK både på branchen og mot `main`. CI-kjøringene var grønne, workflowen har bare `contents: read` og bruker ingen nøkler eller modellkall, og testen feilet i de tre bruddene som var laget med vilje. Konfliktene med `main` ble løst før merge, slik han ba om (`a2a79b1`), og CI-kjøringen [42474560746](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42474560746) var grønn etterpå.
- **Vedtatt:**
  - Den nye ordlyden i andre del av AV-08 (se AV-08).
  - Regelen for branch og PR i `AGENTS.md` (Policy), slik den står i oppføringen 2026-11-06 over.
  - Speilingstesten og CI-workflowen `.github/workflows/skills-speiling.yml`.
- **Forslag, ikke vedtatt:** Mithad foreslo at CI også kjører backend-testene (`pytest`). Det er ført som åpent punkt i `.logs/johagartnerhimolde/issues.md`.
- **Ikke endret:** Første del av AV-08 og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-08 – Backend- og frontendtestene i CI, og CI får ingen hemmeligheter (foreslått, vedtatt 2026-11-08)

- **Hvem:** Foreslått av Mithad Kuduz i gjennomgangen av PR #6, utredet og implementert med Claude Code for Johannes W. Gaertner på branchen `ci-backend-tester` (PR #9). Gjelder når PR-en er godkjent av gruppa.
- **Grunnlag:** Forslaget ble vurdert med pre-mortem, red team og feilmodusanalyse (`bmad-advanced-elicitation`). Største fordel er at CI blir den eneste kjøringen av backend utenfor Windows etter OP-05. Reelle risikoer er at Python-versjonen endrer seg, og at noen senere legger modellnøkkelen inn i CI. Detaljer: `docs/ki-logg/2026-11-08-ci-backend-tester.md`.
- **Foreslått:**
  - Workflowen `.github/workflows/backend-tester.yml` kjører `pytest` i `backend/` ved hver push, med Python 3.12 og nyeste stabile 3.x. Den er adskilt fra speilingstesten, slik at en installasjonsfeil ikke skjuler resultatet av den.
  - Testen mot nyeste 3.x er med fordi en ren lås til 3.12 også er en risiko over tid. Den skjuler versjonsdrift, som da kommer samlet senere. Rød 3.x rettes som vanlig vedlikehold. Presisert av Johannes.
  - **Ny regel i `AGENTS.md` (Policy):** CI får aldri `OPENROUTER_API_KEY` eller andre hemmeligheter, og tester mot KI-porten bruker en falsk OpenRouter.
  - Workflowen `.github/workflows/frontend-tester.yml` kjører `npm ci`, `npm run build` og `npm run test` i `frontend/` med Node 20.19 og nyeste LTS. Anbefalt av Johannes etter at stegene ble målt til ca. 12 s lokalt. `npm run test` har `--if-present` til PR #8 (story 1.4) med testskriptet er merget.
  - **Rød CI blokkerer ikke merge.** `main` får ingen branchebeskyttelse. Den som merger, ser resultatet i PR-en og tar ansvaret. Avgjort av Johannes.
  - CI-avsnittet i `AGENTS.md` sier hva CI ikke dekker, og at rød CI ikke blokkerer merge.
- **Ikke endret:** De andre AV-, K-, OP- og KS-punktene.

### 2026-11-08 – Godkjenning av PR #9 (backend- og frontendtestene i CI)

- **Hvem:** Mithad Kuduz godkjente PR #9 på GitHub 2026-11-08 og svarte på de tre forslagene i PR-beskrivelsen. Johannes W. Gaertner, som foreslo endringene, merget PR-en samme dag og registrerte vedtaket.
- **Grunnlag:** Mithad kontrollerte at begge workflowene bare har `contents: read`, ingen secrets og ingen modellkall, og at matrisene og cachen er riktige. CI var grønn etter at `main` ble merget inn. Han løste konflikten i denne filen i branchen (`2796fc1`), og begge oppføringene i §11 står uendret.
- **Vedtatt:**
  - Workflowene `.github/workflows/backend-tester.yml` og `.github/workflows/frontend-tester.yml`, slik oppføringen over beskriver dem.
  - Regelen i `AGENTS.md` (Policy) om at CI aldri får `OPENROUTER_API_KEY` eller andre hemmeligheter. Mithad: «enig».
  - Rød CI blokkerer ikke merge, og `main` får ingen branchebeskyttelse. Mithad: «enig. Den som merger, ser resultatet og tar ansvaret.»
  - CI-avsnittet i `AGENTS.md`, som beskriver de tre workflowene.
- **Endret etter godkjenningen, slik Mithad ba om:** `--if-present` er fjernet fra `npm run test` i `frontend-tester.yml`, fordi testskriptet kom med PR #8. Et manglende testskript gir nå rød CI i stedet for å bli hoppet over. README har fått et avsnitt om CI under Tester.
- **Ikke vedtatt, egen sak:** Om laveste Node-versjon skal heves fra 20.19. Mithad: «la det stå. Jeg foreslår at vi tar det som en egen sak.» Behandlet i oppføringen under.
- **Ikke endret:** De andre AV-, K-, OP- og KS-punktene.

### 2026-11-08 – Laveste Node-versjon løftes fra 20.19 til 22.12

- **Hvem:** Avgjort av Johannes W. Gaertner etter merge av PR #9 (`db8c295`). Gjort rett på `main` etter regelen for branch og PR, fordi endringen er liten og lett å etterprøve. Gruppa kan ta det opp igjen.
- **Grunnlag:** Node 20 gikk ut av vedlikehold i april 2026 og får ikke sikkerhetsrettinger. Å love en versjon uten vedlikehold er en unødvendig risiko. Node 22 har vedlikehold til april 2027, gjennom semesteret og sensuren. 22.12 er laveste 22-versjon Vite 8 støtter (`engines`: `^20.19.0 || >=22.12.0`). Node 24 ble vurdert, men ville tvunget den som har Node 22, til å oppgradere uten at det gir noe for prosjektet.
- **Endret:** README (krav og CI-avsnittet), `AGENTS.md` (Frontend og CI-avsnittet) og CI-matrisen i `.github/workflows/frontend-tester.yml`, som nå tester 22.12 og nyeste LTS.
- **Ikke endret:** `frontend/package.json` har ingen `engines`-felt, og det er ikke lagt til. De andre AV-, K-, OP- og KS-punktene.

---
### 2026-11-08 – Story 1.5 (OP-11)

- **Hvem:** Mithad Kuduz meldte 2026-11-08 at han tar Story 1.5. Det er en melding om ansvar, ikke et gruppevedtak. Gruppa kan si fra hvis noen allerede er i gang.
- **OP-11 – Story 1.5, Vaktoversikt med «Krever handling»:**
  - Mithad Kuduz er ansvarlig.
  - Implementeringen starter etter at PR #8 (Story 1.4, beskyttede flater og utløpt sesjon) er merget, fordi 1.5 bygger på tilgangskontrollen og navigasjonen derfra.
  - Kjent fallgruve: PR #8 korter ned `epic-1-context.md`, og detaljene om Vaktvalg forsvinner. Det gjelder alert-boksen, tabellkolonnene, fotnoten og teksten når ingen vakter krever handling. Ved oppstart av 1.5 lages konteksten på nytt fra planleggingsdokumentene, ellers leser spesifikasjonen EXPERIENCE.md og `mockups/key-vaktvalg.html` direkte.
- **Grunnlag:** `.logs/mithad-kuduz/993-2026-11-08-13-12-18-gjennomgang-pr-8.md`.
- **Ikke endret:** OP-06 (rekkefølgen er fortsatt ikke bindende) og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-11 – Story 2.3 (OP-12)

- **Hvem:** Mithad Kuduz meldte 2026-11-11 at han tar Story 2.3. Det er en melding om ansvar, ikke et gruppevedtak. Gruppa kan si fra hvis noen allerede er i gang.
- **OP-12 – Story 2.3, 11-timersregelen (daglig hvile):**
  - Mithad Kuduz er ansvarlig.
  - Implementeringen starter etter at PR #14 (Story 2.2, kolliderende vakt) er merget. 2.3 legges inn som regel nummer tre i `REGLER` og bruker `Kandidat.vakter` fra 2.2.
  - 2.3 bygger også vinduet per regel og avgrenser datafeilsjekken for Kandidatens vakter til vinduet, etter Johannes' vedtak A5 (alternativ B) i PR #14.
- **Åpent spørsmål som må avklares før start:** Skal en vakt som overlapper Vakten også telle som brudd på 11-timersregelen, eller bare som kolliderende vakt? Fasiten fra Story 1.2 forutsetter at overlapp bare teller som kolliderende vakt. For #4127 er det 7 kolliderende og 4 med elleve-timer. Mithads anbefaling er at overlapp bare teller som kolliderende vakt. Det er da ingen hvileperiode å måle, Ekskludert-boksen (2.5) får ikke to årsaker for samme forhold, og fasiten (AV-07) står seg. Det er ikke vedtatt.
- **Grunnlag:** `.logs/mithad-kuduz/` (gjennomgangen av PR #14) og [modellvalg-stories.md](../modellvalg-stories.md), som anbefaler Opus for 2.3.
- **Ikke endret:** OP-06 (rekkefølgen er fortsatt ikke bindende) og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-11 – Godkjenning av PR #13 (Story 2.1): datafeilformen og AGENTS.md

- **Hvem:** Johannes W. Gaertner godkjente PR #13 på vegne av gruppa og merget den 2026-11-11 (`bdfd1a4`). Et annet gruppemedlem går gjennom PR-en i etterkant, slik det ble gjort for PR #11. Johannes avgjorde datafeilformen da spesifikasjonen ble godkjent.
- **Grunnlag:**
  - Tre uavhengige gjennomgangsagenter gikk gjennom koden. Funnene står i Review Triage Log i [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md).
  - Johannes gjorde nettleserkontrollen manuelt.
  - 229 backendtester og 26 frontendtester bestod, og CI var grønn.
  - KI-loggen er [2026-11-11-kompetanse-minstekrav.md](../ki-logg/2026-11-11-kompetanse-minstekrav.md).
- **Vedtatt:**
  - **Datafeilformen (P-08, AD-4):** når kandidatvurderingen stopper med datafeil, svarer API-et 200 med `status: "datafeil"`, `kode: "mangler_turnusgrunnlag"` og `datagrense` (ISO 8601 med offset), uten kandidatliste. Feilformen `{kode, melding}` er uendret. Datafeilen holdes atskilt fra `ingen_gyldige_kandidater`, og valget binder story 2.6. Det er også ført inn i P-08/P-09-presiseringen under AD-4 i `ARCHITECTURE-SPINE.md`.
  - **Datagrensen i 2.1** er `turnus.periode_slutt` (05.10.2026 kl. 00:00 i seeden). Story 2.3 og 2.4 utvider sjekken til nabovakter og hele uker og avgjør da hvor historikken starter.
  - **`AGENTS.md`** (AV-08), endret 2026-11-11 på oppdrag fra Johannes:
    - Prosjektbeskrivelsen sier ikke lenger «ingen domenelogikk ennå». Den nevner nå domenekjernen i `backend/domene/`.
    - Testavsnittet for backend nevner nå `tester/regelmotor/` og arkitekturtesten med import-linter.
- **Ikke vedtatt, egen sak:** At overlappende vakter bare teller som kolliderende vakt og ikke under 11-timersregelen, er en tolkning fra testhjelperne i Story 1.2. Gruppa må avklare det før Story 2.3.
- **Ikke endret:** De andre AV-, K-, OP- og KS-punktene.

### 2026-11-11 – PR #14 (Story 2.2): hvor mye historikk datafeilsjekken skal dekke

- **Hvem:** Johannes W. Gaertner vedtok på vegne av gruppa 2026-11-11, etter at Opus-gjennomgangen av story 2.2 (funn A5) løftet spørsmålet. Valget ble lagt fram i PR #14.
- **Spørsmål:** Skal én ugyldig tildelt vakt hos én Ansatt gi datafeil for alle kandidatlister, også når vakten ligger langt unna og ikke kan påvirke noen regel? P-08 sier at vurderingen stoppes når *nødvendig* grunnlag er ukjent eller ugyldig.
- **Vedtatt (alternativ B):** Datafeilsjekken for Kandidatens vakter gjelder bare vakter som kan påvirke reglene, det vil si vakter innenfor et vindu rundt Vakten som hver regel definerer. Det gjelder overlapp for kolliderende vakt, ±11 t for 11-timersregelen og hele berørte kalenderuker for 35-timersregelen. Ugyldig historikk innenfor vinduet er fortsatt ikke fri tid og gir datafeil.
- **Gjennomføring:** Story 2.3 bygger vinduet og retter datafeilsjekken, med grensetester. Story 2.2 beholder inntil da at all tildelt historikk valideres (alternativ A). Det er strengere enn vedtaket, og gir aldri en falsk Gyldig kandidat.
- **Ikke endret:** Selve P-08 (ukjent historikk er ikke fri), datafeilformen og de andre AV-, K-, OP- og KS-punktene.

### 2026-11-11 – Story 2.3 (OP-12): beslutning 1A og 2A, og vakter ved periodeslutt

- **Hvem:** Mithad Kuduz avgjorde 2026-11-11 de to spørsmålene som sto åpne før Story 2.3, som eier av storyen (OP-12). Det er avgjørelser i storyen, ikke gruppevedtak. Gruppa kan ta dem opp igjen.
- **1A – Overlapp og 11 t:** En egen vakt som overlapper Vakten, teller bare som kolliderende vakt. 11-timersregelen ser bare på vakter som ikke overlapper, og nærmeste slutt før og nærmeste start etter avgjør, som testhjelperen `bryter_elleve_timer` fra Story 1.2. Hver Ansatt får én årsak for samme forhold, og fasiten (AV-07) står seg. Dette svarer på det åpne spørsmålet under «Story 2.3 (OP-12)» over.
- **2A – Historikkstart:** Datadekningen starter ved `turnus.periode_start − 672 t` (24.08.2026 kl. 00:00 i seeden), samme vindu som ulempemålingen i AV-09. Adapteren beregner verdien i UTC, og skjemaet endres ikke.
- **Endring mot KS-04:** Med vinduet `[start − 11 t, slutt + 11 t)` gir alle vakter som slutter etter 04.10 kl. 13:00, nå datafeil, fordi `slutt + 11 t` havner etter datagrensen 05.10 kl. 00:00. Det gjelder blant annet #4261–#4265 og kvelds- og nattevakten 04.10. KS-04 godtok tidligere at hvilen etter vakter ved periodeslutt ikke ble kontrollert fullt ut. Endringen følger P-08: ukjent historikk er ikke fri. #4127 og #4189 ligger fortsatt innenfor dekningen.
- **Kjente begrensninger, godtatt av Mithad 2026-11-11:** `datagrense` i datafeilsvaret er `turnus.periode_slutt` også når det er historikkstarten som ikke holder, og en egen vakt som starter før historikkstarten og slutter etter den, regnes som kjent data. Ingen vakt i perioden treffer den nedre grensen.
- **Grunnlag:** [spesifikasjonen for Story 2.3](../../_bmad-output/implementation-artifacts/spec-2-3-filtrere-pa-11-timersregelen-daglig-hvile.md) og [KI-loggen](../ki-logg/2026-11-11-11-timersregelen.md).
- **Ikke endret:** Vedtak A5 og P-08 (gjennomført, ikke endret), datafeilformen og de andre AV-, K-, OP- og KS-punktene.

---

**Dokumentvedlikehold:** Endre status til «Vedtatt», «Utsatt» eller «Løst» for et åpent punkt **bare etter faktisk avklaring**, med dato, beslutning og kilde/henvisning. Behold opprinnelig beslutnings-ID for sporbarhet. Nye punkter gis nye ID-er uten å omskrive historiske vedtak.

## 12. PRD-vedtak 2026-11-09 og status ved dokumentsamordning

Kilde: [PRD-beslutningsgrunnlaget](prd-beslutningsgrunnlag-2026-11-07.md), med skriftlige svar fra alle fire og Kims bekreftelse på vegne av gruppen 2026-11-09. Tabellen registrerer **produktvedtak**, ikke implementasjon eller beståtte tester. Tidligere formuleringer i §3–§11 er historikk; ved motstrid om disse temaene gjelder vedtakene nedenfor. KS-02s fasit for #4127 og KS-04s avgrensede godkjenning av datadekning for #4127/#4189 består.

| ID | Vedtatt krav eller avgrensning | Dokument-/implementasjonsstatus og gjenstående kontroll |
|---|---|---|
| P-01 | Rangeringen bruker modellert **merkostnad ved tildeling** over berørte uker, uten fratrekk for opprinnelig ansatt. | Krav skal inn i FR-7/FR-9 og story 4.3/4.4; beregning og grensetester gjenstår. |
| P-02 | Fordel faktisk forløpt tid fra både eksisterende og ny vakt på kalenderuker i `Europe/Oslo`; 36-timersgrensen gjelder hver berørt uke. FR-8 viser eksisterende timer i startuken. | Ukeskifte, nøyaktig 36 t og begge sommertidsskifter må testes i domenekoden. |
| P-03 | Vis total vaktkostnad med to desimaler, «Ordinær» eller «Inkluderer overtid», og timer × satser i detaljer. Rangering regnes uavrundet. | Kostnadsvisning og samsvar med beregning må testes. |
| P-04 / K-02 | «Høy belastning» begynner ved minst 32,4 t før avrunding. Ingrid har fortsatt 32 t i seeddata og skal ikke merkes høy. | Story 1.2s forventning må rettes; UI og grense 32:23/32:24 må testes. #4127-fasiten endres ikke. |
| P-05 / OP-03 | Ventende eller feilet tolkning av registrert tekst gir midlertidig 50 preferansepoeng med egen status og beholdt råtekst. Avgrensede automatiske forsøk ved forbigående feil; brukeren kan prøve igjen etter endelig feil. Ny tolkning oppdaterer rangeringen før bekreftelse. | Skill manglende tekst, nøytral tolkning, venting og feil i story 5.1/5.2 og tester. KI-feil utelukker ikke kandidaten. |
| P-06 | KI foreslår strukturerte begrunnelser; koden validerer referanser og retning mot beregnede fakta og setter inn navn/tall. Ugyldig påstand gir tydelig merket reservetekst. | KI-kontrakt, falsk-OpenRouter-tester og manuell språkkontroll gjenstår. |
| P-07 / K-04 | Forklaring kan sammenligne med én forhåndsberegnet, gyldig referanse: nr. 1 mot nr. 2, øvrige mot nr. 1; én gyldig kandidat får ingen referanse. | Kontrakt og kontrollerte sammenligninger gjenstår. Valgfri sammenligning av to merkede kandidater er strekkmål **etter** fungerende v1. |
| P-08 | Stopp vurdering og godkjenning når nødvendig turnusdekning, tid, vaktkrav eller kostnadsgrunnlag er ukjent/ugyldig. Dokumentert fri er null timer; ukjent historikk er ikke det. | #4127/#4189 beholder KS-04-godkjenningen. Ved ny vurdering av #4261–#4265 må appen opplyse om seeddata-grensen 2026-10-05 kl. 00:00 og ikke vise rangering/godkjenning. Denne og andre periodekanter må testes. Story 2.1 (PR #13, 2026-11-11): datafeilen stopper kandidatvurderingen ved ugyldig vakt- eller kompetansegrunnlag, eller når vakten slutter etter `turnus.periode_slutt`. Svaret er 200 med `status: "datafeil"` og `datagrense` (se §11). Det er testet i domenet og med en endret testdatabase. Nabovakter og hele uker kommer i 2.3/2.4, og godkjenningen i Epic 3. Story 2.2 (PR #14, 2026-11-11): vedtatt at datafeilsjekken for Kandidatens vakter bare gjelder vakter i et vindu per regel (alternativ B, se §11). Bygges i 2.3. |
| P-09 | Forkast forsinkede svar for tidligere vakt/kandidat. Ved endret beslutningsgrunnlag vises nye beregninger og kreves ny bekreftelse før lagring. | Klientflyt og kontroll ved godkjenning gjenstår. |
| P-10 | Kjerneflyten bruker faste preferanser i testdata. **P-10B planlegges som egen story etter fungerende kjerneflyt**: turnusansvarlig kan redigere tekst, med lagring, tilgangskontroll, ugyldiggjøring av gammel tolkning/forklaring og ny rangering. | B er planlagt v1-tillegg, ikke forutsetning for kjerneflyten; dokumenter som utsatt hvis tiden ikke rekker. Manuell kategori-overstyring er ikke valgt. Johannes' individuelle ønske om høyere prioritet i kilden endrer ikke Kims senere gruppeavklaring. |
| P-11 | Ved null gyldige vises egen tomtilstand, utelukkelsesoppsummering og teksten «Innleie av personell kan vurderes», uten innleieknapp. | Skill tomtilstanden fra datafeil og lasting i UI-test. |
| P-12 | Godkjenning lagres varig; vist forklaring lagres ikke historisk i kjerneversjonen. | Historisk forklaringslagring er **ikke v1-krav**. Eventuelt senere valg krever egen story for forklaring og beregningsgrunnlag. |
| P-13 / OP-02 | Desktop og gjeldende tilgjengelighetskrav er bindende nå. Gruppen avklarer mobil/nettbrett etter fungerende kandidatvisning og før story 4.6 er ferdig. | Felles ansvar: dokumenter en enkel oppgavebasert forståelsestest der testpersonen uten hint forklarer nr. 1, finner annen gyldig kandidat og skiller datafeil fra null gyldige. **Avgrensning:** én testperson og ett operativsystem og én skjermflate holder; mobil-/nettbrettavklaringen krever ingen egen forståelsestest. **Akseptmål:** testpersonen løser alle tre oppgavene uten hint. Står hen fast på én, rettes det som skapte misforståelsen, og funnet og rettingen noteres. Dokumenter testperson, operativsystem og skjermflate, svar per oppgave og eventuelle rettinger. Presisert av Johannes 2026-11-11 i godkjenningen av PR #12. Testen er ikke utført. |
| E-01 | Faglærers muntlige opplysning er gjengitt: KI i produktet er ikke et formelt emnekrav; KI beholdes som valgt produktscope. | Lukket som dokumentasjonspunkt 2026-11-08; forelesningsdato er ukjent. |
| E-02 | Commit `ee6d798` er identifisert som godkjent proposal; planavvikene er listet i beslutningsgrunnlaget. | Avklart som dokumentpunkt 2026-11-09. Kontroller faktisk levert app mot proposal og forklar avvik ved innlevering. |

**Status 2026-11-10:** Beslutningene er ført her. PRD og nedstrøms dokumenter samordnes i egen branch. Dette er ingen påstand om at P-01–P-13 er implementert, at KS-03 er utført, eller at P-13s brukerprøve er gjennomført.
