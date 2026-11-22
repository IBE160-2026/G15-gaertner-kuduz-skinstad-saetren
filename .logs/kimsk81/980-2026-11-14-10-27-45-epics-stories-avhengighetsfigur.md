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
## 2026-11-15 kl. 17:01 — Kimsk81

### Oppgave
Automatisere synkronisering av figurens status med sprintstatus og legge til CI-kontroll, etter brukerens ønske.

### Plan
- Bruke sprintstatus som kilde, beholde avhengighetsnotater og oppdatere faktiske statustekster.
- Dokumentere kommandoen, teste feil og la en uavhengig agent gjennomgå endringen.

### Resultat
- La til Python-skript og GitHub Actions-kontroll, oppdaterte figuren og dokumenterte bruk i README. Figuren oppgir nå riktig antall stories og ingen foreldet statusdato.
- Fire automatiske tester bestod, inkludert feilformede og dupliserte data samt kontroll- og skrivemodus. Kontroll av faktisk figur mot sprintstatus og git diff --check bestod.
- Den uavhengige gjennomgangen fant mangelfull validering og et testgap; disse ble rettet og testet. Se spesifikasjonen og KI-loggen for detaljer.

### Åpne punkter
Ingen.

## 2026-11-19 kl. 19:38 — Kimsk81

### Oppgave
Oppdatere avhengighetsfiguren etter ferdigstilte stories.

### Plan
- Sammenligne figuren med sprintstatusen, oppdatere statusfarger og kontrollere samsvaret.

### Resultat
Story 4.5 er endret fra gul til grønn i figuren etter at storyen ble satt til `done`. Story 5.1 er fortsatt under arbeid og beholder fargen for gjenstående arbeid. Prosjektets kontroll `python scripts/synkroniser_storyfigur.py --sjekk` og `git diff --check` bestod. Et første forsøk på en egen sammenligningskommando feilet på grunn av feil i søkemønsteret; prosjektets eksisterende kontroll ble brukt i stedet.

### Åpne punkter
Ingen.

## 2026-11-21 kl. 13:25 — Kimsk81

### Oppgave

Oppdatere avhengighetsfiguren etter flettingen av story 5.3.

### Plan

- Kontrollere sprintstatus og spesifikasjon mot gruppas gjennomgang av PR #35.
- Synkronisere figuren og kontrollere status for alle 30 stories.

### Resultat

Sprintstatusen viste fortsatt `review` for 5.3. Ragnhild godkjente endringene etter test på macOS, og PR-en ble flettet. Oppdaterte 5.3 til `done` i sprintstatusen og kjørte `scripts/synkroniser_storyfigur.py`. Bare ruten for 5.3 skiftet farge. [Gjennomgang og fletting av PR #35](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/35)

Skriptets `--sjekk` og `git diff --check` bestod. Opptelling i SVG-en ga 23 ferdige stories og 7 gjenstående.

### Åpne punkter

Ingen.

## 2026-11-22 kl. 11:39 — Kimsk81

### Oppgave

Undersøke og deretter fjerne ordningen for synkronisering av storyfiguren etter brukerens valg.

### Plan

- Undersøke commit `6d2f142` og senere bruk, og vise brukeren hva en tilbakeføring innebærer.
- Fjerne skript, tester og CI-kontroll, men beholde den gjeldende figuren og historisk dokumentasjon.

### Resultat

Fjernet `scripts/synkroniser_storyfigur.py`, tilhørende test og `.github/workflows/storyfigur.yml`. README viser fortsatt til figuren og beskriver manuelt vedlikehold. Figuren er uendret; spesifikasjonen og KI-loggen er beholdt som historikk. `git diff --check` bestod, og søk i aktive filer fant ingen resterende henvisninger til skriptet eller workflowen. Ingen applikasjonstester er kjørt for denne fjerningen.

### Åpne punkter

Ingen.
