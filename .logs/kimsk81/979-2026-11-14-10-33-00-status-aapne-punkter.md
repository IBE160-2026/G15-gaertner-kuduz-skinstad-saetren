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

## 2026-11-22 kl. 10:25 — Kimsk81

### Oppgave

Gå gjennom alle åpne avkryssinger i Kims punktliste, også underpunkter, og finne hvilke som kan lukkes på dokumentert grunnlag.

### Plan

- Hent siste referanser fra origin og sammenhold punktene med vedtak, sprintstatus, spesifikasjoner, testkode og gruppemedlemmenes kontrollresultater.
- Bevar historikken og presiser restarbeidet når bare deler av et punkt er avklart.

### Resultat

Kontrollgrunnlaget er `main` ved `1e1a57b`, som også var siste commit på `origin/main` etter fetch. Av 26 åpne avkryssinger, inkludert to underpunkter, ble 11 lukket og 15 beholdt åpne. Hver av de 26 fikk en datert begrunnelse og en kilde i [punktlisten](issues.md).

| Område | Punkter lukket | Dokumentert grunnlag |
| --- | ---: | --- |
| Godkjenningsflaten og Vaktvalg | 3 | Komponenttesten fra PR #16, gjennomgangen av timeetikett, fasit, sammenligning og endret rangering i PR #31, samt rettelsen i AGENTS.md etter PR #10. |
| Kostnad, belastning og ulempe | 4 | Ragnhilds visuelle kontroll og gjennomgang av PR #24. Johannes’ vurdering av lønnsfeil og nye POST-test, integrasjonen av 4.2/4.3 og komponenttesten av alle varselkombinasjoner i PR #28. |
| Skjermleser | 2 | Oppfølgingen av timeetiketten ble avgrenset bort i v1 uten ny opplesing. Kim bekreftet at Windows Skjermleser leste «Høy belastning» riktig i Edge. Ragnhild avsluttet VoiceOver-punktet. |
| Preferansetolkning og rangering | 2 | AV-19 og OP-03 avklarer feilkontrakten i 5.1. AV-05/K-03, periodetestene og kontrollen nedenfor dekker E1–E4 fra briefen. |

Kjørte 53 backendtester på nytt. Hele [rangeringsmodulen](../../backend/tester/regelmotor/test_rangering.py), kandidatlistens test for vakter 04.10, godkjenningsgrunnlagets datafeiltest og POST-testen for endret lønn bestod. Testene brukte testmiljøet. Tidligere resultater fra nettleser, skjermleser og frontend er hentet fra de lenkede prosjektloggene.

**Kontroll av kandidatavhengig rangering.** Brukte `kandidat`, `vurder` og `VAKT` fra rangeringsmodulens tester, og kjørte domenets `ranger` med standardvektene. A hadde 300 kr/t og 20 timer i startuka, B hadde 310 kr/t og 0 timer, og C hadde 400 kr/t og 20 timer. Øvrige faktorer var like. Med A og B fikk A 67,5 og B 47,5. Med C i vurderingen fikk B 83,5, A 67,5 og C 27,5. B fikk flere kostnadspoeng da høyeste kostnad økte. Begge rekkefølgene og alle fem poengverdiene ble kontrollert mot forhåndsberegnede forventninger. Dette var en engangskontroll.

### Åpne punkter

De 15 gjenværende avkryssingene er oppdatert i [issues.md](issues.md).

- Fire gjelder nettleseren. Kontroller kontrast og returknapp i godkjenningsflyten, tom- og feiltilstand i Vaktvalg, kostnadsraden med begge varsler og story 4.6 i vanlig Chrome med rullefelt ved 680 px. For 4.6 gjenstår også designvalget om totalscore på to linjer.
- Fire gjelder produktbevis og levering. Det gjenstår lokal problemvalidering, P-13-prøven med designvurdering, sammenligning med godkjent proposal ved innlevering og gruppas valg av sensornøkkel, betaling og kreditt.
- Fire gjelder gruppevalg og dokumentasjon. Det gjenstår sluttdato for nattevakter, generell versjonslåsing, presisering av «åtte timer» i AV-02 og samordning av epic 4-konteksten.
- Tre gjelder KI og datagrunnlag. Disse er betinget støtte for flere serverprosesser og A–B–A ved tekstredigering, om 5.9 skal leveres eller utsettes, og restkontrollene for P-06/P-08. KS-03s 16 tidskategoriruter og #4127-fasiten er allerede dekket.

## 2026-11-22 kl. 10:41 — Kimsk81

### Oppgave

Bruk BMAD til å prioritere handlinger som kan lukke flere punkter, og gi konklusjonen som en instruks til en ny chat.

### Plan

- Bruk bmad-help, den installerte katalogen, sammenslått konfigurasjon, punktlisten, sprintstatus og OP-16-sjekklisten til å velge passende arbeidsflyter.
- Prioriter kontroller og dokumentrettelser som kan utføres nå, og beskriv hvilke rester som trenger testperson eller gruppevalg.

### Resultat

Anbefalte først nettleserkontroll av godkjenningsflyt, Vaktvalg, begge varselmerker og 4.6, deretter dokumentrettelser i epic 4-kontekst og AV-02, og samlet kontroll av P-08 og KI-språk. OP-16 sier at automatisert dekkede funksjonsflyter slipper samme manuelle kontroll. Ny chat bør derfor vurdere om de gamle funksjonstestkravene kan avsluttes med eksisterende bevis, samtidig som layout, kontrast og synlig fokus undersøkes i nettleser.

Instruksen peker til bmad-help [BH], Sprint Status [SS] med handling status, Walkthrough [WT] for menneskelig gjennomgang og Build [BD] ved nødvendige kode- og testendringer. Build følger prosjektets krav om underagenter. Gruppevalg om nattevaktdato, versjonslåser, 5.9 og sensorbetaling må avklares med brukeren. P-13 krever en faktisk testperson og kan kombineres med innsamling av lokal problemvalidering. E-02 kan forberedes nå og sluttføres ved innlevering. Støtte for flere serverprosesser er fortsatt betinget av fremtidig driftsbehov.

BMAD-konfigurasjonen ble løst med backendens Python etter at uv ble stoppet av tilgang til sin cache. Katalogen og eksisterende prosjektbevis ble lest. Ingen nye apptester ble kjørt i denne planleggingsoppfølgingen.

### Åpne punkter

De eksisterende 15 punktene i issues.md videreføres. Ingen nye punkter.
