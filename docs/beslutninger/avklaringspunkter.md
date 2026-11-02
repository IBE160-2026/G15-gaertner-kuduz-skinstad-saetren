# Avklaringspunkter og beslutningsreferat – Turnushjelperen

> **Prosjekt:** IBE160 Programmering med KI – Turnushjelperen  
> **Gruppe:** G15 – Prompt Patrol  
> **Møtedato:** 2026-11-02  
> **Deltakere:** Johannes W. Gaertner, Mithad Kuduz, Kim O. Skinstad og Ragnhild Sætren  
> **Beslutningsgrunnlag:** `IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf` (oppdatert 2026-10-31, 6 sider)  
> **Dokumentstatus:** Beslutningsreferat; vedtatte beslutninger og åpne oppfølgingspunkter  
> **Sist oppdatert:** 2026-11-02  
> **Foreslått plassering:** `docs/avklaringspunkter.md` (kontroller mot faktisk repostruktur før innlegging)

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
| OP-04 | Agentoppsett/underagenter | Prinsipp vedtatt; kontroll åpen | Behold oppsett uendret; gjennomgå før neste `bmad-build`. | Ikke bestemt |
| OP-05 | Ren klone/plattformtesting | Åpent | Testomfang/tidspunkt ikke avtalt; Codex-forslag ikke vedtatt. | Ikke bestemt |
| OP-06 | Arbeidsrekkefølge | Forslag, ikke vedtatt | Codex-rekkefølgen beholdes kun som forslag. | Ikke bestemt |
| OP-07 | PR #4 | Vedtatt | Ragnhild Sætren ansvarlig for oppfølging og retting av PR #4. | Ragnhild Sætren |
| OP-08 | Story 1.2 | Vedtatt | Mithad Kuduz ansvarlig for oppdatering av Story 1.2. | Mithad Kuduz |
| OP-09 | Frist PR-review | Åpent | Ingen frist avtalt. | Ikke bestemt (PR-ansvar: Ragnhild) |
| KS-01 | Åpne punkter ved merge | Vedtatt | K-01/K-02/K-04/K-06 kan være åpne etter merge; øvrige godkjenningskrav gjelder. | Ikke bestemt |
| KS-02 | Kontroller rangeringsformel | Kontroll vedtatt; ikke utført | Verifiser mot PRD og Story 4.7 før testfasit godkjennes. | Ikke bestemt |
| KS-03 | Kontroller tidskategorier | Kontroll vedtatt; ikke utført | Kontroller fire vakttyper før implementasjon av Story 4.7 og ferdigstilling av fasit. | Ikke bestemt |
| KS-04 | Kontroller datadekning | Kontroll vedtatt; ikke utført | Kontroller historikk, nabovakter og berørte uker før Story 1.2 er `done`. | Ikke bestemt |

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

### OP-05 – Ren klone og plattformtesting

- **Status:** Åpent; ingen testomfang eller tidspunkt vedtatt.
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
| Kontroller datadekning for historikk, nabovakter og kalenderuker. | KS-04 | **Før Story 1.2 er `done`.** | Ikke særskilt fordelt |
| Kontroller tidskategorier for fire vakttyper. | KS-03 | **Før implementasjon av Story 4.7** og ferdigstilling av tilhørende fasit. | Ikke bestemt |
| Verifiser rangeringsformelen mot PRD/Story 4.7. | KS-02 | **Før godkjenning av relevant testfasit.** | Ikke bestemt |
| Implementer/test ulempmodell etter vedtakene uten å endre dem. | AV-01, AV-09, AV-11/12 | Som del av Story 4.7 i v1, etter gjeldende story-kriterier. | Ikke bestemt |
| Avklar relevant KI-feilhåndtering ved preferansetolkning. | OP-03 | **Før Story 5.1 og 5.2 er `done`.** | Ikke bestemt |

### 8.4 Kan vente / ikke tidfestet

| Oppgave | Grunnlag | Status/avgrensning |
|---|---|---|
| Kontrollér om eksisterende logging dekker sporbarhet og begrunnelse for tak 300. | K-05 | Kontroll åpen; ingen loggendringer vedtatt. |
| Gjennomgå agentpraksis/underagenter og bevar reviewfunn. | OP-04 | Før neste `bmad-build`; agentinstrukser beholdes. |
| Detaljert UX, mobiltilpasning og brukerprøving. | OP-02 | Etter fungerende kandidatvisning; mockuper med fire vakttyper samordnes nå. |
| Avklar ren klone, Python 3.12, macOS/Linux og vurderingsmatrise. | OP-05 | Åpent; ingen nye testkrav vedtatt. |
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
Prosjektbeslutninger fra gruppemøtet 2026-11-02: se docs/avklaringspunkter.md.
Respekter dokumentets statusmarkeringer; ved konflikt med øvrige prosjektinstruksjoner, meld fra og be om avklaring.
```

> Dette er kun et **forslag** til fremtidig referanse. AV-08 og OP-04 innebærer at eksisterende agentinstruksjoner **foreløpig beholdes uendret**. Dersom faktisk lagringssted blir et annet, må lenken tilpasses.

## 10. Kilder og gyldighet

- **Hovedgrunnlag:** `IBE160_Beslutningsgrunnlag_PR4_Story12_OPPDATERT.pdf`, oppdatert 2026-10-31, seks sider. PDF-en bygger på to Codex-analyser og var et **forslag til beslutningsgrunnlag**, ikke en registrering av vedtak.
- **Faktiske gruppevedtak:** Formidlet fra møtet 2026-11-02 og bekreftet punkt for punkt av gruppens representant i den påfølgende samtalen. Der gruppen ikke oppga begrunnelse, ansvar eller frist, står det eksplisitt «ikke oppgitt»/«ikke bestemt».
- **Kontrollbegrensning:** Dette dokumentet er **ikke** en gjennomgang av nåværende kildekode eller repository-innhold. Verken PR #4 eller Story 1.2 er endret gjennom utarbeidelsen av denne filen. Ingen tester, merges, commits eller pushes er utført.

---

**Dokumentvedlikehold:** Endre status til «Vedtatt», «Utsatt» eller «Løst» for et åpent punkt **bare etter faktisk avklaring**, med dato, beslutning og kilde/henvisning. Behold opprinnelig beslutnings-ID for sporbarhet. Nye punkter gis nye ID-er uten å omskrive historiske vedtak.
