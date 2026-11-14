# Frontend-komponenttester

## 2026-11-14 kl. 11:01 — johagartnerHiMolde

### Oppgave
Innføre automatiske komponenttester for frontend etter [handoffen](../../_bmad-output/implementation-artifacts/handoff-frontendtesting-2026-11-14.md). Testene skal erstatte mest mulig av den manuelle nettleserkontrollen og dokumentere testingen bedre for kriterium 3 i sensorveiledningen. Arbeidet gjøres i en branch med PR.

### Plan
- Branch: `frontend-komponenttester`, laget fra `main` (`5a71652`).
- Beslutninger fra Johannes:
  - DOM-miljøet er jsdom 28.1.0.
  - De 48 `node:test`-testene flyttes ikke, og `npm run test` kjører begge testsettene.
  - Alle fem utsatte punkter dekkes (1.5, 2.1, 2.4, 2.5 og 3.1).
  - Testoversikten og den manuelle sjekklisten ligger i én fil, `docs/testing.md`.
  - Spesifikasjonen holdes samlet, selv om den er på rundt 2 600 tokens.
  - Alternativ A: manuell kontroll trengs bare når testene ikke kan kontrollere det aktuelle. Regelen legges i `_bmad/custom/bmad-build.toml`.
- Arbeidsmåte: `bmad-build` med underagenter. Én kartla koden, én implementerer fra spesifikasjonen, og egne agenter gjennomgår uten å ha sett implementeringen.
- Spesifikasjon: [spec-frontend-komponenttester.md](../../_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md).

### Resultat
Milepæl: spesifikasjonen er godkjent ved sjekkpunkt 1, og implementeringen har startet. Loggen oppdateres når arbeidet er gjennomgått.

### Åpne punkter
- Implementering, gjennomgang og PR gjenstår (pågår i økten).
