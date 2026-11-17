# Oppdater lokal testdatabase

## 2026-11-17 kl. 20:57 — Kimsk81

### Oppgave
Opprett lokal database og testdata på nytt etter skjemaendringen i story 5.1.

### Plan
- Stopp backendprosessen som holder databasefilen åpen, slett den lokale databasen og kjør testdataoppsettet.
- Kontroller resultatet og databasens integritet.

### Resultat
Den gamle lokale `backend/turnushjelperen.db` ble slettet og opprettet på nytt med `python -m adaptere.lagring.testdata` fra backendens virtuelle miljø. Oppsettet rapporterte én turnus, 25 ansatte, 506 vakter og én bruker. Et nytt tilfeldig testpassord ble generert og oppgitt til brukeren. SQLite `integrity_check` svarte `ok`. Backendprosessen på port 8000 ble stoppet for å frigjøre databasefilen.

### Åpne punkter
Ingen.
