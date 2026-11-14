# Status åpne punkter

## 2026-11-14 kl. 10:33 — Kimsk81

### Oppgave
Gå gjennom `.logs/kimsk81/issues.md` og avgjøre hvilke åpne punkter som har tilstrekkelig dokumentert grunnlag for å lukkes.

### Plan
- Lese sesjonslogg-reglene og sensorveiledningen.
- Kontrollere statusnotatene for PR #16 mot spesifikasjonen, review-loggen, testresultater og utsatt arbeid.
- Lukke ferdigbehandlede punkter og beholde beslutninger/arbeid som fortsatt gjenstår.

### Resultat
Lukket PR #16-punktet om #4189-testen, dokumentkonfliktene og verifikasjon etter sammenslåing. Kildene viser rettet test (`f59f69b`), løste konflikter, 412 backendtester, 48 frontendtester og vellykket bygg. Lukket også spørsmålet om «Avbryt uten kall»: PR5 presiserer at det betyr uten skrivekall; GET-kallene ved ny visning er tilsiktet etter P-09.

Delte det sammensatte punktet om godkjenningstekst/nattevakt: PR3s tekstinnvending er avvist med begrunnelse i review-loggen, mens gruppens beslutning om sluttdato for nattevakter på alle flater gjenstår. Delte også punktet om «Avbryt» og komponenttest; komponenttesten er fortsatt utsatt i `deferred-work.md`/VG1 og står derfor fortsatt åpen.

Ny gjennomgang etter brukerens oppfølgingsspørsmål: Lukket de ferdige delene av BMAD-statuspunktet. Valg av startuke, Python 3.12 og test fra ren klone på macOS er dokumentert i beslutningsreferatet (OP-05) og sprintstatus; generell beslutning om eksakte versjonslåser står igjen som eget åpent delpunkt. Lukket dokumentpunktet fra PR #18: AV-15/16, gjeldende PRD §§4.5, 4.7, 5, 7 og 8, og mergecommit `1d31ea7` viser at alle de nevnte dokumentavklaringene og konflikten ble håndtert. Åpne produktvalg er ført i egne punkter. Gikk gjennom resten av åpne punkter: de krever fortsatt nettleserkontroll, komponenttest, arbeid i AGENTS.md, implementasjon/test, gruppens beslutning eller kontroll ved innlevering. Ingen ytterligere punkt ble lukket uten slikt bevis.

Ingen tester kjørt; dette var en dokumentkontroll. Arbeidskopien var ren før endringene.

### Åpne punkter
- Avklar med gruppa om sluttdato skal vises for nattevakter på alle relevante flater.
- Følg opp utsatt komponenttest av godkjenningsflaten.
- Avklar gruppens generelle valg om eksakte versjonslåser.
