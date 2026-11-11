# GitHub CLI-innlogging

## 2026-11-11 kl. 21:57 — Kimsk81

### Oppgave

Hjelp brukeren å gjenopprette innloggingen i GitHub CLI (`gh`) etter at den lagrede tokenen ble ugyldig.

### Plan

- Kontroller `gh auth status`.
- Start GitHubs enhetsinnlogging med `gh auth login -h github.com -p https --web`, la brukeren fullføre den i egen nettleser, og verifiser kontoen etterpå.

### Resultat

- GitHub CLI meldte først ugyldig token for `kimsk81`. Brukeren fullførte enhetsinnloggingen i GitHub. CLI meldte `Authentication complete` og `Logged in as kimsk81`.
- `gh auth status -h github.com` utenfor sandkassen viser gyldig innlogging via nøkkelringen, og `gh api user --jq .login` returnerer `kimsk81`. Ingen tokenverdi er lest eller lagret i prosjektet.
- Kontroller inne i sandkassen ser fortsatt den gamle ugyldige tokenen. GitHub-kommandoer i denne agentøkten må derfor kjøres utenfor sandkassen for å bruke den nye innloggingen.
- Ingen PR ble godkjent, merget eller endret i denne oppgaven.

### Åpne punkter

Ingen.
