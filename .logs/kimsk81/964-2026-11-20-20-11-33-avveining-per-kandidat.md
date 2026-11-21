# Avveining per kandidat

## 2026-11-20 kl. 20:11 — Kimsk81

### Oppgave
Gjennomfør story 5.3 med bmad-build på egen branch, med faktakontroll, gyldig referanse og vern mot foreldede forklaringer.

### Plan
- Kontrollerte siste main, PRD, epic, arkitektur, beslutningsreferat, sensorveiledning og forrige story. Tre underagenter undersøkte vedtakene og koblingene til backend og frontend.
- Samlet kontrakt, grensetilfeller og verifisering i [utkastet for 5.3](../../_bmad-output/implementation-artifacts/spec-5-3-avveining-per-kandidat.md).

### Resultat
Branchen er publisert fra 1bfbee4dd6fe2ba53b1dfbe089f5989708c8dc83. Offisiell rendering lyktes med prosesslokal fjerning av foreldet VIRTUAL_ENV og godkjent lesetilgang til manifestet. Story 5.2 står som ferdig. Gjennomgangen fant at ulike brøker kan bli like etter konvertering til float, og at kandidatlisten trenger et merke fra samme lesing som rangeringen. Begge inngår i de planlagte regresjonstestene. Arbeidet er ved spesifikasjonssteget. Produksjonskode og tester gjenstår.

Kim valgte B. Spesifikasjonen måler egne faktorpoeng mot kandidatens eksakte totalscore. Akseptansematrisen dekker 60 mot 80 og én kandidat med alle faktorpoeng lik totalscoren. Kontrollert mot FR-11s krav til reservetekst. Spesifikasjonen er klar til godkjenning i bmad-build.

### Åpne punkter
Ingen.

### Gjennomgang av spesifikasjonen
En uavhengig underagent leste spesifikasjonen mot epic, arkitektur og kode. Vi kontrollerte at eksisterende godkjenningsmerke inkluderer kandidat-ID, at faktorpoeng og råbeløp har ulik betydning, og at rangeringsparametrene tillater nullvekt. Utkastet angir nå merke per kandidatrad fra samme lesetransaksjon, regresjonstester for forsinkede svar på begge flater, kildelinje styrt av faktisk kilde og avvisning av retningspåstander om faktorer uten vekt. Disse funnene er kontrollert ved dokument- og kodelesing. Implementering, testkjøring og uavhengig kodegjennomgang hører til neste fase etter godkjenning av spesifikasjonen.

### Statuskontroll etter avbruddet kl. 22:56

Kontrollerte utkastet, sprintstatus, arbeidskopi, commit-historikk, stash og registrerte arbeidstrær. Ved kontrollstart var de tre commitene siden forgreningen fra main loggendringer. Spesifikasjonen lå usporet i arbeidsmappen med status `draft` og seks åpne oppgaver. Sprintstatus viste `backlog`. Det var ingen lagrede kode- eller testendringer for 5.3 i branchen eller en egen stash. Siste dokumenterte steg var gjennomgangen av utkastet. Arbeidet kan gjenopptas ved godkjenningen av spesifikasjonen.

### Godkjent for implementering

Kim godkjente spesifikasjonen og ba om å fortsette med underagenter. Vi registrerte utgangspunktet for kodegjennomgangen, satte storyen i arbeid og ga implementeringen til en egen agent. En separat agent kontrollerte epic-konteksten og akseptansekriteriene mot PRD, vedtak og arkitektur.

## 2026-11-21 kl. 07:39 — Kimsk81

### Oppgave
Finn hvor story 5.3 stoppet, og fortsett arbeidet med underagenter.

### Plan
En underagent kontrollerte epic-kontekst og vedtak mot den godkjente spesifikasjonen. Vi gjenopptok arbeidet fra de lagrede kodeendringene og nettleserresultatene i KI-loggen.

### Resultat
Frontendbygget og de 52 modultestene bestod. To eldre komponenttester feilet etter at avveiningspanelet kom inn. Navigasjonstesten må vente på første forklaring før den teller API-kall, og testen av kandidatkortet må finne ulempeetiketten i kortets egne nøkkeltall. Begge kontrollene er justert.

Tre uavhengige underagenter fant feil ved kø og tidsfrist, avrunding, duplikatnøkler og tilgang til panelknappene fra skjermleserens knappeliste. Vi rettet funnene og styrket testene for modellskjema, eksakte brøker og retningsvisning per faktor. Backendmiljøet for Windows er gjenopprettet med prosjektets låste pakker. Dette løser miljødelen av oppfølgingspunktet fra 5.1.

Sluttkjøringen ga 717 beståtte backendtester, bestått frontendbygg og 52 + 57 beståtte frontendtester. En underagent gjentok nettlesertesten ved 680 × 700 px med ekte backend, reservetekst og lokal testtransport. Arbeidet er lagret i `7baa427`, med sprintstatus `review`. [KI-loggen](../../docs/ki-logg/2026-11-20-avveining-per-kandidat.md) inneholder testresultatene og lenker til gjennomgangen.

### Åpne punkter
Ingen.
