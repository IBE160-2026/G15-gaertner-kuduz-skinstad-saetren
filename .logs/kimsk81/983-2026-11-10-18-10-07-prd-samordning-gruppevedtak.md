# PRD-samordning med gruppevedtak

## 2026-11-10 kl. 18:10 — Kimsk81

### Oppgave

Samordne beslutningsreferat, PRD og berørte planleggingsdokumenter med P-01–P-13 og E-01/E-02. Bevar FR-ID-er, #4127/#4189-fasit, KS-04s avgrensede godkjenning og historiske reviews. Arbeidet skal ligge i egen branch uten push eller PR før gjennomgang.

### Plan

- Lese bmad-prd/validate, sesjonslogg, sensorveiledning, PRD-beslutningsgrunnlag og relevante AV-/K-/OP-/KS-punkter.
- Føre vedtak i referatet, deretter oppdatere PRD, stories, arkitektur, UX/mockuper, produktbrief og sprintstatus der de var misvisende.
- Kontrollere fasit, status og lenker, kjøre rubrikkgjennomgang og dokumentere åpne punkter. [Valideringsrapport](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/validation-report-2026-11-10.md).

### Resultat

- Branchen `docs-samordne-prd-vedtak-2026-11-10` ble opprettet fra rent `main`. Ingen push eller PR ble gjort.
- Referat §12 skiller P-vedtakene fra implementasjon og kontroller. P-10 er løst fra kildenes status: Johannes' individuelle ønske endret ikke Kims senere gruppeavklaring; P-10B er story 5.9 etter fungerende kjerneflyt. P-07s valgfrie sammenligning er strekkmål; P-12B er ikke v1-krav.
- PRD FR-1–FR-14 beholdt ID-ene og fikk testbare konsekvenser for merkostnad/ukefordeling, 32,4-timersgrense, datastopp, preferansefeil, KI-faktakontroll, ny bekreftelse og tomtilstand. PRD-memloggen ble oppdatert med bmad-prd-skriptet. Historiske reviews og modelltestresultater er urørt.
- Epics, Story 1.2-spesifikasjonen, arkitektur, DESIGN/EXPERIENCE, godkjenningsmockup, brief og sprintstatus ble samordnet. Ingrid har fortsatt 32 timer og skal ikke merkes høy belastning. Den tidlige `direction-a-fagsystem.html` er merket som historisk visuell utforskning. Vurderingsmatrisen fikk en dokumentmilepæl uten å påstå implementasjon.
- bmad-prd-rubrikkgjennomgangen fant seks dokumentfunn; alle ble rettet og oppfølgingskontrollen vurderte dokumentet Excellent. FR-1–FR-14 er unike, P-01–P-13/E-01/E-02 finnes i referatet, relative lenker i endrede Markdown-filer peker til eksisterende filer, og `git diff --check` er ren. Eksisterende seeddata-testfil ga 39 beståtte tester. Dette verifiserer gjeldende seeddata/fasit, ikke nye appkrav.
- Tidligere åpne dokumentpunkter om briefens lovlighetsløfte, PRD-kostnad/terskel, hvilestatus og mangelfulle data/KI-fakta/gamle svar ble lukket i `issues.md` som dokumentarbeid. Nye implementerings- og sluttkontrollpunkter er ført der.

### Åpne punkter

- Implementasjon og tester for P-01–P-09/P-11 gjenstår, særlig P-08 ved #4261–#4265; KS-03s tidskategorikontroll er fortsatt ikke dokumentert. #4127/#4189 og KS-04s avgrensning må bevares.
- P-13s mobil-/nettbrettavklaring og oppgavebaserte forståelsestest gjenstår før story 4.6 ferdigstilles.
- P-10B er backlog-story 5.9 etter kjerneflyten; dokumenter den som utsatt hvis tiden ikke rekker. P-07s valgfrie sammenligning er strekkmål og P-12B er ikke v1-krav.
- E-02s avviksliste må kontrolleres mot faktisk levert app ved innlevering. E-01s muntlige faglæreruttalelse har ukjent forelesningsdato.
