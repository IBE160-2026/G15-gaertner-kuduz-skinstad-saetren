# Story 5.1 – preferansetolkning med KI

## 2026-11-16 kl. 19:05 — Mithad Kuduz

### Oppgave
Sette opp skoleprosjektet på laptopen og bygge story 5.1: KI tolker de ansattes preferansetekster til en av fem kategorier, lagrer resultatet og gir det til rangeringen. Arbeidet skal i en PR som gruppa går gjennom.

### Plan
- Klonet repoet til laptopen, installerte backend (`.venv`, Python 3.14.6) og frontend (`npm ci`, Node 26.7). Alle tester bestod før arbeidet startet.
- Laget branchen `story/5-1-preferansetolkning` fra `origin/story/4-4-rangering`, fordi 4.4 allerede har `TolketPreferanse`, `Tolkestatus` og preferansetaggen. Branchen må rebases på `main` når 4.4 er merget.
- Kjørte `bmad-build` med underagenter (OP-04) på Opus, som `docs/modellvalg-stories.md` anbefaler for 5.1:
  - Epic-konteksten: [epic-5-context.md](../../_bmad-output/implementation-artifacts/epic-5-context.md).
  - Spesifikasjonen: [spec-5-1](../../_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md), gjennomgått av en egen agent før godkjenning (12 funn, alle innarbeidet).
  - Implementering av egen agent, deretter blind gjennomgang, grensetilfeller og testhull (20 funn: 8 rettet, 2 utsatt, resten avvist med begrunnelse i Review Triage Log).
- Mine valg (forslag, ikke gruppevedtak): ved 5xx og nettverksfeil 3 nye forsøk etter 2, 4 og 8 s, 90 s budsjett per tekst, sluttstatus `kunne_ikke_tolkes` med feiltype. Tolkningen starter i bakgrunnen når backend starter. «Prøv igjen»-knappen er utsatt. Backend leser fortsatt ikke `.env`.

### Resultat
- Committet i `77427c5` (23 filer). Nytt: `backend/adaptere/ki/` (`openrouter.py`, `begrenser.py`), `backend/adaptere/lagring/preferansetolkning.py`, seks kolonner på `ansatt`, `tolk_ventende` og `lifespan` i `adaptere/api/main.py`, `tester/conftest.py` og nye tester i `tester/ki/`, `tester/lagring/` og `tester/api/`.
- `pytest` 671 bestått (562 før), `npm run test` 52 + 37 bestått. Alle 12 rader i feiltabellen og alle akseptkriterier har tester. Ingen ekte OpenRouter-kall er gjort.
- KI-logg: [2026-11-16-preferansetolkning.md](../../docs/ki-logg/2026-11-16-preferansetolkning.md). README, AGENTS.md, `.env.example` og `docs/testing.md` er oppdatert. Sprintstatus: 5.1 `review`.
- Git på laptopen er satt til «Mithad Kuduz <mithad.kuduz@himolde.no>» for dette repoet (ikke globalt).
- En eldre lokal database må slettes og testdataene lastes på nytt etter denne endringen.

### Åpne punkter
- Gruppa må vedta feilreglene for preferansetolkning (P-05/OP-03, PRD §8) før 5.1 kan bli `done`. Ført i `deferred-work.md`.
- «Prøv igjen» for feilet tolkning er utsatt og må leveres, eller utsettelsen godtas av gruppa, før 5.1 kan bli `done`.
- Push branchen og lag PR mot `story/4-4-rangering` (eller `main` etter at 4.4 er merget), og få gjennomgang fra et annet gruppemedlem.
- Valgfri live-kontroll mot Luna (19 betalte kall): slett databasen, last testdata, start backend med nøkkel og se at taggene for #4127 blir kategorier.
- Foreslå for gruppa i PR-en at backend kan lese `OPENROUTER_API_KEY` fra `.env`.
