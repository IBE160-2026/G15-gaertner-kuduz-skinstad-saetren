# Installer Impeccable for Codex

## 2026-11-09 kl. 17:46 — Kimsk81

### Oppgave
Brukeren ba om å søke på nettet og installere Impeccable design-skill for Codex.

### Plan
- Finne den offisielle kilden og Codex-skillens plassering.
- Kjøre Codex' skill-installer mot prosjektets GitHub-repo og kontrollere installasjonen.

### Resultat
- Fant offisiell dokumentasjon på `https://impeccable.style/docs/` og kilde i `pbakaus/impeccable`.
- Installert `.agents/skills/impeccable` fra GitHub til `C:\Users\krh\.codex\skills\impeccable` med Codex' `install-skill-from-github.py`. Første forsøk med `python` feilet fordi kommandoen ikke finnes på PATH; nytt forsøk med `backend/.venv/Scripts/python.exe` lyktes.
- Kontrollert at installasjonen inneholder `SKILL.md`, `reference/`, `agents/` og `scripts/impeccable.cmd`. Arbeidstreet var uendret før sesjonsloggen.

### Åpne punkter
Ingen.
