- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md`
  summary: Ingen test binder frontendens `FEILTEKSTER` i `frontend/src/tekster.ts` til feilkodene fra backend (`MELDINGER` i `backend/adaptere/api/main.py`), og ingen test viser at 401 fra `/api/meg` ikke gir melding.
  evidence: Verification Gap 2026-11-07: en skrivefeil i en nøkkel, for eksempel `feil_inlogging`, består `npm run build` og alle pytest-testene og gir reserveteksten ved feil passord. Story 1.3 utelukker frontendtester i Never-lista. Ta det opp når frontend får testverktøy, senest i story 1.4.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: Feil-, prøv-igjen- og 401-tilstandene i Vaktvalg har ingen automatisk test, og feiltilstanden er ikke kontrollert i nettleser.
  evidence: Frontend har ingen testrigg for komponenter (bare Node-tester av rene funksjoner). Det ville vært medium, men er ikke verifisert. Avgjøres av en komponenttest (for eksempel med jsdom) eller en manuell kontroll der `/api/vaktoversikt` feiler mens `/api/meg` svarer.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: Innledningen og «Kjøring og verifisering» i AGENTS.md nevner ikke vaktoversikten fra 1.5 eller `npm run test`.
  evidence: AGENTS.md er agentkontekst. Etter AV-08 endres den med registrering i §11 eller i egen PR, ikke som en del av denne storien.
