# Avklaringspunkter og beslutningsreferat – Turnushjelperen

> **Prosjekt:** IBE160 Programmering med KI – Turnushjelperen  
> **Gruppe:** G15 – Prompt Patrol  
> **Møtedato:** 2026-11-02  
> **Deltakere:** Johannes W. Gaertner, Mithad Kuduz, Kim O. Skinstad og Ragnhild Sætren  
> **Beslutningsgrunnlag:** [IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf](IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf) (oppdatert 2026-10-31, 6 sider)  
> **Dokumentstatus:** Beslutningsreferat; vedtatte beslutninger og åpne oppfølgingspunkter  
> **Sist oppdatert:** 2026-11-07 (OP-10 besvart i spesifikasjonen for Story 1.3 og implementert; fysisk test på macOS/Linux strøket i OP-05, se §2.3, §3 og §11)  
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
| AV-08 | Beslutningssporbarhet | Vedtatt | Navngitte, sporbare gruppevedtak; eksisterende logg- og agentinstruksjoner uendret. | Ikke bestemt |
| AV-09 | Målevindu ulempe | Vedtatt | 672 faktiske timer, halvåpent vindu, lokal kategorisering i Europe/Oslo. | Ikke bestemt |
| AV-10 | Historikk | Vedtatt | Fast, reproduserbar historisk seeddata; ingen turnusgenerator i v1. | Ikke bestemt |
| AV-11 | Ulempmodell | Vedtatt | Vekter 40/20/15/25; 0/1/2/3 poeng/t; tak 300; ingen helligdagsmodell eller innstillingsside. | Ikke bestemt |
| AV-12 | Test av ulempens effekt | Vedtatt | Test kandidater med like øvrige faktorer og ulik ulempe; forventet scoreforskjell dokumenteres. | Ikke bestemt |

### 2.2 Korrigeringer og oppfølging (separat fra AV-01–AV-12)

| ID | Tema | Status | Kort registrering | Ansvarlig |
|---|---|---|---|---|
| K-01 | Feil regneeksempel | Åpent | `22 + 2 × 21 + 3 × 29 = 151`, ikke 136; konkret retting ikke avtalt. | Ikke bestemt |
| K-02 | Høy timebelastning | Åpent | Codex foreslår terskel 32,4 t (90 % av 36); ikke vedtatt. | Ikke bestemt |
| K-03 | Avrunding | Vedtatt | Beregn/sorter uavrundet; vis én desimal. | Ikke bestemt |
| K-04 | `RangertKandidat`/KI-kontrakt | Åpent | Codex anbefaler samordning; konkret endring ikke vedtatt. | Ikke bestemt |
| K-05 | KI-sporbarhet | Prinsipp vedtatt; kontroll åpen | Behold logging uendret; sjekk senere dokumentasjon inkl. tak 300. | Ikke bestemt |
| K-06 | Dokumentkvalitet | Åpent | Codex anbefaler retting av foreldet tekst, lenker og status; ikke vedtatt. | Ikke bestemt |
| OP-01 | Avgrensninger i v1 | Vedtatt | Ingen omfattende tariff-, fraværs-, stillingsprosent-, helligdags- eller juridisk modell. | Ikke bestemt |
| OP-02 | UX og mobil | Vedtatt | Samordne mockuper nå; detaljert UX, mobil og brukerprøving etter fungerende kandidatvisning. | Ikke bestemt |
| OP-03 | KI-feil ved preferansetolkning | Prioritering vedtatt; løsning åpen | Avklar før Story 5.1/5.2 er `done`. | Ikke bestemt |
| OP-04 | Agentoppsett/underagenter | Vedtatt 2026-11-04 | Gjennomgått og godkjent: `bmad-build` kjøres med underagenter, som i AGENTS.md fra PR #5 (§11). | Johannes W. Gaertner (godkjent på vegne av gruppa) |
| OP-05 | Ren klone/plattformtesting | Delvis vedtatt 2026-11-07 | Fysisk test på macOS/Linux strykes: verken sensor eller noen i gruppa har Mac. Koden skrives for å virke på tvers av operativsystem og testes fysisk på Windows. Test fra ren klone er fortsatt ikke avtalt (§11). | Johannes W. Gaertner |
| OP-06 | Arbeidsrekkefølge | Forslag, ikke vedtatt | Codex-rekkefølgen beholdes kun som forslag. | Ikke bestemt |
| OP-07 | PR #4 | Vedtatt | Ragnhild Sætren ansvarlig for oppfølging og retting av PR #4. | Ragnhild Sætren |
| OP-08 | Story 1.2 | Vedtatt | Mithad Kuduz ansvarlig for oppdatering av Story 1.2. | Mithad Kuduz |
| OP-09 | Frist PR-review | Åpent | Ingen frist avtalt. | Ikke bestemt (PR-ansvar: Ragnhild) |
| KS-01 | Åpne punkter ved merge | Vedtatt | K-01/K-02/K-04/K-06 kan være åpne etter merge; øvrige godkjenningskrav gjelder. | Ikke bestemt |
| KS-02 | Kontroller rangeringsformel | Utført for fasiten i Story 1.2 (2026-11-04) | Fasiten for #4127 er kontrollert og godkjent med PR #5 (§11). Gjelder ny fasit på nytt. | Mithad Kuduz (kontroll), Johannes W. Gaertner (godkjenning) |
| KS-03 | Kontroller tidskategorier | Kontroll vedtatt; ikke utført | Kontroller fire vakttyper før implementasjon av Story 4.7 og ferdigstilling av fasit. | Ikke bestemt |
| KS-04 | Kontroller datadekning | Utført 2026-11-04 | Dekket for #4127 og #4189 og låst med test; begrensningen etter 05.10 er godtatt (§11). | Mithad Kuduz (kontroll), Johannes W. Gaertner (godkjenning) |

### 2.3 Vedtak etter møtet (ikke i PDF-en)

| ID | Tema | Status | Kort beslutning | Ansvarlig |
|---|---|---|---|---|
| AV-13 | Enhet i designtokens | Vedtatt 2026-11-06 | Skriftstørrelser i `rem`; spacing, kanter, radius, sporing og faste bredder i `px`. Ingen rå størrelser i komponentene (§11). | Johannes W. Gaertner (vedtatt på vegne av gruppa) |
| AV-14 | Layoutbredde | Vedtatt 2026-11-06 | Appbar over hele bredden; innholdet får `max-width: 1180px`. Fast bredde på 1180px forkastes (§11). | Johannes W. Gaertner (vedtatt på vegne av gruppa) |
| OP-10 | Story 1.3 | Vedtatt 2026-11-06; de fire spørsmålene avklart i spesifikasjonen 2026-11-06 | Johannes W. Gaertner tar Story 1.3. Vite-proxy, personlig eller tilfeldig testpassord, PyJWT 2.15.1 og `hashlib.scrypt`, tabellen `bruker`. JWT-nøkkelen lages tilfeldig ved oppstart, avvik fra epics (§11). | Johannes W. Gaertner |

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

**Dette er en endrings-/kontrolloversikt, ikke en påstand om hvilke endringer som allerede er gjort i repoet.** Kontroller filnavn, faktiske stier og nåværende innhold før gjennomføring. Betegnelsene under følger møteunderlaget.

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
  - **KS-04:** Kontrollen av datadekningen er godtatt, med den kjente begrensningen etter 05.10.
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

---

**Dokumentvedlikehold:** Endre status til «Vedtatt», «Utsatt» eller «Løst» for et åpent punkt **bare etter faktisk avklaring**, med dato, beslutning og kilde/henvisning. Behold opprinnelig beslutnings-ID for sporbarhet. Nye punkter gis nye ID-er uten å omskrive historiske vedtak.
