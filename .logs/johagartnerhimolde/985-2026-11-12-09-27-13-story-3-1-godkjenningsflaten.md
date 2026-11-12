# Story 3.1: Velge kandidat og se godkjenningsflaten

## 2026-11-12 kl. 09:27 — johagartnerHiMolde

### Oppgave
Starte Story 3.1 med `bmad-build` på egen branch, parallelt med Ragnhilds Story 2.4. Starten skal være synlig for gruppa via en pushet branch. Anbefalingene fra vurderingen av om 3.1 kan gå før 2.4 skal inn i konteksten for byggingen.

### Plan
- Vurdering i forkant: OP-06 gjør rekkefølgen ikke-bindende, og Epic 3 er «ikke blokkert». 3.1 ble anbefalt framfor 2.5 (samme filer som 2.4), 2.6 (avhenger av 2.4 og 2.5) og 4.1 (ville laget ukelogikken fra 2.4 på nytt).
- Oppstartscommit på branchen `story-3.1-godkjenningsflaten`: sprintstatus og melding i avklaringspunktene. Branchen pushes.
- `bmad-build`: kontekst for Epic 3 bygges av en underagent, og en annen underagent undersøker koden. Deretter skrives spesifikasjonen, Johannes besvarer de åpne spørsmålene og godkjenner den, og implementeringen settes i gang i en egen underagent.
- Modell: `docs/modellvalg-stories.md` anbefaler Sonnet for 3.1. Johannes valgte å fortsette på Opus 5.5.
- Spesifikasjonen: [spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md](../../_bmad-output/implementation-artifacts/spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md)

### Resultat
- `c7df2a3` er pushet til `origin/story-3.1-godkjenningsflaten`. Story 3.1 og Epic 3 står som `in-progress` i sprintstatus.
- Avklaringspunktene har fått OP-13 og en oppføring i §11. Den sier at 3.1 går parallelt med 2.4, at testene bruker kandidater som er gyldige også etter 2.4 (Jonas Bakke og Mette Solberg for #4127, ikke Anders Strand), at testen for utelukkede ikke bindes til én regel, og at storyene overlapper i `Kandidatflate.tsx` og `tekster.ts`. Oppføringen har også en merknad om at spesifikasjonen for 2.4 bruker OP-12, som er Mithads melding for 2.3.
- `_bmad-output/implementation-artifacts/epic-3-context.md` er nylaget og har med de samme anbefalingene.
- Spesifikasjonen er godkjent av Johannes:
  - 1A: URL-en er `/vakt/<nr>/godkjenning/<ansatt_id>`.
  - 2A: «Godkjenn erstatning» er aktiv, men viser bare en `meta`-linje fram til 3.2.
  - 3A: Egen tekst ved 404, «Kandidaten kan ikke velges for denne vakten.»
  - Spesifikasjonen er på omtrent 2 900 tokens og beholdes hel.
- Det nye endepunktet `GET /api/vakter/{nr}/kandidater/{ansatt_id}` er lesende. Utelukket og ukjent Ansatt gir samme 404 `ikke_funnet`.
- Implementeringen pågår i en underagent. Spesifikasjonen og kontekstfilen er ikke committet ennå.

### Åpne punkter
- Story 3.1: implementering, uavhengig gjennomgang, nettleserkontroll og PR gjenstår.
- Si fra til Ragnhild at spesifikasjonen for 2.4 bruker OP-12 (Mithads 2.3), og at OP-13 nå er brukt for 3.1. Neste ledige er OP-14.
