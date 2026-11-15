# AGENTS.md faktarettelser

## 2026-11-15 kl. 18:40 — Ragnhild

### Oppgave
Før story 4.2: gjennomgå hele AGENTS.md mot faktisk prosjektstatus, kode og gjeldende beslutninger, finn utdaterte statusbeskrivelser (ikke gjeldende instrukser) og rett bare det som er faktafeil. Behold alle regler og krav. Forslagene ble vist og godkjent før endring. Retting rett på `main` (Policy: avgrenset, lett å etterprøve), og endringen registreres i `avklaringspunkter.md` §11 uten nytt punkt (AV-08).

### Plan
- Sammenlignet AGENTS.md med `sprint-status.yaml`, `backend/domene/`, `backend/adaptere/` (`ki/` er tom), CI-filene, `.env.example`, README, `docs/testing.md` og referatet (OP-04, OP-05, AV-08, AV-13, AV-17, OP-16). Kjørte `pytest`: 468 bestått.
- Forslag ble lagt fram, og «446 av 455» ble endret fra et nytt tall til en formulering uten tall, fordi tallet endrer seg ved hver commit.

### Resultat
- `AGENTS.md`: (1) innledningen beskriver nå stacken som bygget, storyene som er ferdige, alle fire harde regler, timer i perioden og ulempebelastning, og at rangering og KI-laget ikke er bygget; (2) «Ikke drøftet i gruppa ennå» er byttet med godkjenningen 2026-11-04 (OP-04, PR #5), regelen er uendret; (3) «446 av 455 sporede filer» er byttet med «godt over halvparten av de sporede filene» (var 451 av 843).
- `docs/beslutninger/avklaringspunkter.md`: kort oppføring i §11 («Faktarettelser i AGENTS.md», AV-08) uten nytt ID, og «Sist oppdatert» er utvidet.
- Verifisert uten endring: kommandoer, filstier, CI-versjoner, jsdom/vitest, `BEGIN IMMEDIATE`-advarselen og OP-05-tallene (historiske, med dato).
- Ikke verifisert, lar stå: grensen på 20 Luna-kall per minutt og at `main` mangler branchebeskyttelse (krever tilgang til OpenRouter og GitHub).
- Logging: bare sesjonslogg. KI-logg i `docs/ki-logg/` gjelder generert kode, og dette er dokumentasjon. Kvalitetssikringen er forslaget som ble godkjent, diffen og commit-meldingen.
- Commit på `main`, ikke pushet.

### Åpne punkter
- `docs/ki-logg/README.md` linje 24 har samme utdaterte tall («446 rammeverksfiler»). Ikke rørt, utenfor avtalt omfang.
- `_bmad-output/implementation-artifacts/deferred-work.md` har to åpne funn (linje 18 og 46) om at AGENTS.md sa «den første harde regelen». De er nå løst i AGENTS.md. Ikke rørt.
