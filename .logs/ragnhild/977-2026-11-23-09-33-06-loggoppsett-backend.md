# Loggoppsett for backend

## 2026-11-23 kl. 09:33 — Ragnhild

### Oppgave
Ragnhild ville vite hva det åpne punktet om loggoppsett for backend går ut på, hvorfor det ikke er gjort før, og hvilke konflikter PR #38 (story 5.7) kan gi. Deretter skulle det planlegges med `bmad-build`. Implementeringen tas i en ny økt.

### Plan
- Les funnet i `deferred-work.md` og tidligere logger (982, 979) for å se hvorfor punktet ble utsatt.
- Prøveflett PR #38 mot `main` med `git merge-tree` og sammenlign diffene i `main.py` og `README.md`.
- Planlegg med `bmad-build` (fritt løp, ikke epic-story) og skriv spesifikasjonen: [spec-loggoppsett-backend.md](../../_bmad-output/implementation-artifacts/spec-loggoppsett-backend.md).

### Resultat
- Hvorfor utsatt: 16.11 ble funnet gjort under gjennomgangen av PR #30, uten kodeendringer. 21.11 ble halvdelen om nettverksfeil rettet, men loggoppsettet ble stående uten at grunnen er skrevet ned. `ARCHITECTURE-SPINE.md` (linje 116 og 215) setter runtime-logging som ikke besluttet, og det forklarer trolig hvorfor punktet het «avklare».
- PR #38 kolliderer allerede med `main` i `sprint-status.yaml` og `vurderingsmatrise.md` etter mergen av PR #39 (gjelder også mot `d0598bd`, før dagens commits). Loggoppsettet gir liten risiko for konflikt: PR #38 endrer `ki_fra_miljo()` og README fra linje 193, mens loggoppsettet legges over `main.py:665` og i README 160–176. Samvirkning: PR #38 legger til en INFO-melding for `KI_MODUS=demo`, som blir synlig med loggoppsettet. Kim bør få vite det.
- Spesifikasjonen er godkjent som `ready-for-dev`, med Ragnhilds valg C: arkitekturdokumentet røres ikke, og endringen går rett på `main` som en feilretting. En merknad i `deferred-work.md` om senere oppdatering av spinen er en del av oppgavene. README-rettingene omfatter også en avbrutt setning (linje 169) og den utdaterte påstanden om at «Prøv igjen» mangler.
- Modell: tabellen sier Sonnet for denne typen endring, men økten kjørte Opus etter Ragnhilds faste valg.
- Ingen kode er endret. Spesifikasjonen er ikke committet i denne økten.

### Åpne punkter
- Implementere loggoppsettet i en ny `bmad-build`-økt fra `spec-loggoppsett-backend.md` (`ready-for-dev`).
- Oppdatere `ARCHITECTURE-SPINE.md` (linje 116 og 215) om runtime-logging ved neste arkitekturgjennomgang eller i retrospektiven for epic 5 (valg C).
- Si fra til Kim at loggoppsettet gjør INFO-meldingen for `KI_MODUS=demo` i PR #38 synlig.
