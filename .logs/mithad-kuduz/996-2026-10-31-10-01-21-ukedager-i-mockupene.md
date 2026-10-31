# Ukedager i mockupene

## 2026-10-31 kl. 10:01 — Mithad Kuduz

### Oppgave

Mithad ba om å rette mockupene så ukedagene stemmer med 2026-kalenderen. Først kom spørsmålet om pushen fra 30.10 faktisk lå på GitHub.

### Plan

- Sjekke GitHub: `story-1.2-fiktiv-turnus` står på `f13bf59`, det samme som lokalt. Pushen er der, men i en branch uten PR, så den vises ikke på forsiden.
- Finne alle ukedag og dato for 27.–29.09 i planleggingsdokumentene, og sammenligne med det PR #4 allerede retter.
- Ta de samme endringene som PR #4 som småendring rett på `main`, ordrett like, og prøvemerge mot PR #4 og story-1.2-branchen.

### Resultat

- Commit `f6b520409bc8e95ab9770f0dcc1fb5cd81a70d4f` på `main`:
  - Ukedagene er rettet til søndag 27.09, mandag 28.09 og tirsdag 29.09.
  - Filene er `key-vaktvalg.html`, `key-godkjenning.html`, `direction-a-fagsystem.html` og story 1.5 i `epics.md` (eksempelet i UX-DR5-linjen).
- De tre mockupene er hentet uendret fra `origin/ab-3-ulempbelastning`. Der er bare ukedagsordene endret, og det er kontrollert med diff.
- `.working/direction-b-rolig.html` hadde «lørdag 27.09», og det er rettet. PR #4 dekker ikke den filen.
- Kvalitetssikring:
  - Et søk etter ukedag + dato for 27.–29.09 finner ingen feil igjen.
  - `git merge-tree` mot `origin/ab-3-ulempbelastning` og mot `story-1.2-fiktiv-turnus` gir ingen konflikt.
- Vakttidene i mockupene (15–23 og 23–07) er bevisst ikke endret. De venter på at gruppa avgjør vakttidene i PR #4.
- Pushet til `origin/main` (`951fdd5..f05ec63`) etter at Mithad ba om det.

### Åpne punkter

Ingen.
