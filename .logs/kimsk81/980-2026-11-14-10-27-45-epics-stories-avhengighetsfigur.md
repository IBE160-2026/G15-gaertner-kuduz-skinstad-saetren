# Epics-stories-avhengighetsfigur

## 2026-11-14 kl. 10:27 — Kimsk81

### Oppgave
Lage en SVG-figur over alle epics og stories med avhengigheter, der forbindelsene er lette å følge med fargekoder.

### Plan
- Hente epic/story-listen og status fra planleggingsdokumentene.
- Lage SVG med piler, avhengighetsfarger og status.
- Hente `origin/main`, commite og pushe oppgaven etter brukerens instruks.

### Resultat
- Opprettet `docs/epics-stories-avhengigheter.svg` med alle fem epics og 25 stories, status og fargekodede avhengighetspiler.
- Korrigerte usynlige forbindelser ved å gi linjene eksplisitt strekfarge og fargeklasse.
- Kontrollerte SVG-kilden; ingen separat SVG-renderer var tilgjengelig for visuell kontroll.
- `git pull --ff-only origin main` hentet inn `589aba5` uten konflikt.

### Åpne punkter
Ingen.

## 2026-11-14 kl. 10:30 — Kimsk81

### Oppgave
Flytte avhengighetsfiguren til en egen mappe under `docs/` og publisere flyttingen på `main`.

### Plan
- Opprette `docs/figurer/` og flytte SVG-filen dit.
- Committe og pushe flyttingen.

### Resultat
- Flyttet figuren til `docs/figurer/epics-stories-avhengigheter.svg`.
- Committet og pushet flyttingen til `main`.

### Åpne punkter
Ingen.

## 2026-11-15 kl. 16:53 — Kimsk81

### Oppgave
Oppdatere fargene for fullførte stories i avhengighetsfiguren, undersøke status for 4.1 og oppdatere sprintstatus etter gjennomgang og merge.

### Plan
- Sammenligne figuren med sprintstatus, spesifikasjon, gjennomgangslogg og git-historikk.
- Endre kun statusfargene i figuren og sette 4.1 til done i sprintstatus.
- Kontrollere diffen og dokumentere arbeidet før commit og push.

### Resultat
- Story 2.6, 3.1, 3.2 og 4.1 er markert grønne i figuren. Tekstene er beholdt etter brukerens avgrensning, også «Gjenstår» under 2.6 og 4.1.
- Story 4.1 sto som review i sprintstatus selv om spesifikasjonen var done og PR #25 ble gjennomgått og merget i a98d28a. Ingen begrunnelse for avviket ble funnet. Sprintstatus er nå done.
- Kontrollert status mot spesifikasjonen, gjennomgangsloggen og git-historikken; diffen er kontrollert. Dette er dokumentasjonsendringer, så apptester er ikke kjørt.

### Åpne punkter
- Den eksisterende oppfølgingen av faktisk skjermleseropplesing står i issues.md under gjennomgang av PR 25.