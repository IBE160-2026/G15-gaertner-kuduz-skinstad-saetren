# Story 1.4 – beskyttede flater

## 2026-11-08 kl. 00:05 — Kimsk81

### Oppgave
Brukeren ba om «bmad-build story 1.4». Målet er beskyttede flater, utløpt sesjon og utlogging.

### Plan
- Kjørte BMAD-rendereren og leste arbeidsflytens avklarings- og planleggingssteg, sensorveiledning og relevante vedtak.
- Én underagent regenererte epic-konteksten fra planfilene; én undersøkte API, frontend og UX uten å endre kode.
- Leste ferdig story 1.3 og laget [spesifikasjonen](../../../_bmad-output/implementation-artifacts/spec-1-4-beskyttede-flater-og-utlopt-sesjon.md).

### Resultat
Planlegging fullført til BMADs checkpoint 1. Spesifikasjonen er `draft`, storyen fortsatt `backlog`; ingen implementering eller tester utført. Feature-branch `story-1.4-beskyttede-flater` opprettet fra ren main. Epic-konteksten var foreldet og er regenerert og lest. Undersøkelsen identifiserte eksisterende HTTP-wrapper, sesjonshjelpere, testdatabase og UX-URL-er som gjenbrukes. Planen dekker felles standardvern, tre offentlige metode/sti-par, sentral 401-håndtering, History API, utlogging og forsinkede svar. Ingen uløste produktspørsmål funnet.

Kvalitetssikring: spesifikasjonen kontrollert mot story 1.4, kontinuiteten fra 1.3, OP-10, AV-13/14 og sensorveiledningen. Eldre NFR7-sammendrag i epics krever nøkkel fra miljøet, mens OP-10, story 1.3 og arkitekturen uttrykkelig fastsetter tilfeldig oppstartsnøkkel; planen bevarer OP-10 og endrer ikke nøkkeloppsettet. Dette er dokumentert samordningsrest, ikke nytt produktvedtak. Ingen funksjonalitet er merket ferdig. Vurderingsmatrisen har fått lenke til planleggingsbeviset. Eksisterende issues lest; ingen nye produktpunkter eller tidligere punkter løst.

Sandkassen blokkerte først uv og lesing av genererte steg; eskalerte kommandoer lyktes. Brukerens godkjenning av spesifikasjonen er neste arbeidsflytsteg.

### Review av spesifikasjonen samme dag
Brukeren valgte «review spec». Fire uavhengige BMAD-linser ble brukt: adversarial, edge-case-hunter, struktur og prose. De fant særlig motstrid om 401 versus 404/405 for ukjente API-stier, forsinkede svar på tvers av sesjoner, feil utløpsmelding ved første besøk, uklare direkte URL-er og tvetydig utloggingsfeil. Spesifikasjonen er revidert med beslutning om 401 før ruting uten sesjon, sesjonsgenerasjon, tydelige URL-tilstander og systemnivå akseptansekriterier. Alle funn er triagert i spesifikasjonens Review Triage Log. Fortsatt `draft`; ingen implementering eller testkjøring.

### Åpne punkter
Ingen nye. Eksisterende dokumentsamordning følges i `issues.md`.

