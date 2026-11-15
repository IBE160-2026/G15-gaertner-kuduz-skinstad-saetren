# Story 4.7: Ulempebelastning per kandidat

## 2026-11-15 kl. 14:14 — Kimsk81

### Oppgave

Implementere story 4.7 med bmad-build på egen branch, starte med KS-03, og unngå å ta inn umerget arbeid fra story 3.2 og 4.1. Brukeren ba underveis om å stoppe ved et passende delmål og oppsummere status.

### Plan

- Kontrollerte git-status og fjernbrancher; opprettet og pushet `story-4.7-ulempebelastning` fra `main`.
- Leste AGENTS.md, sensorveiledningen, beslutningsreferatet, PRD §4.3–4.4, story 4.7 og arkitekturen. Brukte bmad-build med egen agent for epic-kontekst og kodekart.
- Gjennomførte KS-03 uavhengig av implementasjonen og skrev [kontrollen](../../docs/beslutninger/ks-03-tidskategorier-2026-11-15.md) og [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-7-ulempebelastning-per-kandidat.md).

### Resultat

- Rent `main` ved start. Story 3.2 er umerget på `story-3.2-godkjenning-bemanning`; story 4.1 på `story-4.1-timer-i-perioden` inneholder planleggingsfiler. Branchen vår bygger på `6a7e8713817b199c31fac1df76a5a62a98d53b94` og er synlig på GitHub. Ingen PR er opprettet.
- KS-03-tabellen dekker fire vakttyper på ukedager og helg, overgangene fredag–lørdag og søndag–mandag og sommertid. Uavhengig regning gir 20 poeng for vårnatten og 26 for høstnatten; ingen motstrid mellom vedtatte kilder ble funnet. Referatet er oppdatert til «utført» med lenke til kontrollen. Dette godkjenner ikke ny kode eller KS-02-fasit.
- Epic 4-kontekst, spesifikasjon og sprintstatus er skrevet. Implementasjonsagenten ble avbrutt etter brukerens stoppbeskjed. Den rakk å endre domenetyper, beregningsmodul, vurdering, API og frontend. Ingen nye tester, KI-logg eller vurderingsmatrise er ferdige. Ingen tester ble kjørt, og kodeendringene er ikke gjennomgått eller committet.

### Åpne punkter

- Fullfør og kontroller story 4.7 fra den uferdige arbeidskopien: domenetester inkludert begge sommertidsskifter og 672-timersgrenser, API-/komponenttester, uavhengig fasitkontroll, review, KI-logg og vurderingsmatrise. Avstem ulempekolonnens plassering når 4.1 gir timekolonnen. Storyen skal ikke merkes ferdig før dette er verifisert.
