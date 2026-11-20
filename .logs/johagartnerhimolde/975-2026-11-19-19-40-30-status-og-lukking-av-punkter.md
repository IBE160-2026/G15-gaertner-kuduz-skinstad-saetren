# Status og lukking av punkter

## 2026-11-19 kl. 19:40 — johagartnerHiMolde

### Oppgave
Hente de siste endringene, gi en status for prosjektet og lukke de punktene i Johannes'
`issues.md` som allerede er løst. Kim lukker det som gjenstår for story 4.5.

### Plan
- `git fetch --prune` og fast-forward av `main` (30 commits, PR #31 med story 4.5).
- Lese sprintstatus, åpne PR-er og alle fire `issues.md` for å lage statusen.
- Kontrollere hvert åpent punkt i egen tracker mot repoet og GitHub før lukking: AGENTS.md,
  reviewene på PR #24, #25 og #29, koden i 5.1 og Ragnhilds logg for PR #24.

### Resultat
- **Status:** Epic 1–3 er ferdige. I epic 4 er 4.1–4.4 og 4.7 ferdige, 4.5 er merget
  (PR #31, 2026-11-17), men står fortsatt som `review` i `sprint-status.yaml` og som
  `in-review` i spesifikasjonen. Kim retter dette. 4.6 står i backlog. 5.1 står som
  `in-progress`, og «Prøv igjen» gjenstår. 5.2–5.9 står i backlog. Det er ingen åpne PR-er.
  `origin/story/4-4-rangering` og `origin/story/5-1-preferansetolkning` er merget, men ikke slettet.
- **Lukket i `issues.md` (fem punkter):**
  - AGENTS.md beskriver bare kompetanse-minstekrav: den beskriver nå alle fire harde regler.
  - Merge-rekkefølgen for 4.1 og 4.7: Ragnhild løste konfliktene i `73c9dfc`, kjørte
    testene og kontrollerte kolonnene i nettleseren. PR #24 er merget i `b654786`.
  - Menneskelig gjennomgang av 4.4: Ragnhild godkjente PR #29, som er merget i `908ab83`.
  - 5.1 må bruke nøklene i `PREFERANSEPOENG`: 5.1 importerer dem i `adaptere/ki` og
    `adaptere/lagring` og bruker dem som enum i JSON-skjemaet, og tester i `tester/ki/` og
    `tester/api/` binder dem.
  - Statuslinjen for 4.4 i AGENTS.md: den sier nå at 4.4 er ferdig.
- **Delvis:** Bindingen av lagret tolkning til modellen. 5.1 lagrer `tolket_modell`, men en
  lagret tolkning er fortsatt gyldig etter bytte av `OPENROUTER_MODEL`. Ingen avgjørelse
  er funnet i spesifikasjonen, KI-loggen eller referatet, så punktet er fortsatt åpent.
- **Ikke lukket:** Punktene om gruppevedtak (innleveringstekst, modellanbefaling,
  sluttdato for nattevakter, Bårds spørsmål, kontrollbreddene i 4.6), fristen 2026-12-15
  i en sporet planfil og to nettleserkontroller (PR #23 og PR #28). Ingen av dem er
  dokumentert som løst.
- Bare `issues.md` og denne loggen er endret. Ingen kode og ingen tester er endret.

### Åpne punkter
- Etikettene for preferansekategoriene i `frontend/src/tekster.ts` er ikke bundet til
  `PREFERANSEPOENG` i backend av noen test. Hvis en nøkkel endres i backend, viser
  `preferansetekst` i `frontend/src/kandidater.ts` den rå nøkkelen, og ingen test feiler.
