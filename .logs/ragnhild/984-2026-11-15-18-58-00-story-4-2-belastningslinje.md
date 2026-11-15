# Story 4.2 – belastningslinje med terskel

## 2026-11-15 kl. 18:58 — Ragnhild

### Oppgave
Bygge story 4.2 med `bmad-build`: timebelastning som prosent av 36 t og høy belastning fra og med 32,4 t (P-04/K-02), vist som 110×7 px linje i `accent`/`warn`. Kim har startet 4.3, så vi måtte være obs på overlapp.

### Plan
- Spesifikasjonen var ferdig og godkjent: [spec-4-2](../../_bmad-output/implementation-artifacts/spec-4-2-belastningslinje-med-terskel.md).
- Modell: Sonnet 5.5 (anbefalt og faktisk, `docs/modellvalg-stories.md`).
- Implementering med underagent, deretter tre uavhengige gjennomgangsagenter (Blind Hunter, Edge Case Hunter, Verification Gap).

### Resultat
- Backend: `domene/regelmotor/timebelastning.py`, felt `timebelastning_prosent` og `hoy_belastning` på `KandidatUt` (kandidatrute og godkjenningsgrunnlag).
- Frontend: linje i `Kandidatflate.tsx`, tokens `--load-bar-width/height`, tekst «Høy belastning» for skjermleser.
- Tester: grensetester (32:23:59, 32:24:00, 32:25), API-tester, komponenttest. Etter gjennomgangen la jeg til en test av godkjenningsgrunnlaget med `hoy_belastning = True`. Resultat: 488 av 488 backendtester. Frontend (agentens kjøring): bygg, 50 modultester og 27 komponenttester bestod.
- Gjennomgangen ga ett reelt funn (patchet). Resten er avvist med begrunnelse i Review Triage Log, og to er utsatt til `deferred-work.md`.
- Spec satt til `done`, sprintstatus til `review`. KI-logg: `docs/ki-logg/2026-11-15-arbeidsbelastningslinje.md`.
- Kims branch for 4.3 fantes ikke på remote. Konflikt mulig i `KandidatUt` og `Kandidat` i `api.ts`.

### Åpne punkter
- Manuell nettleserkontroll mot ekte backend (OP-16): layout ved 1080/960/680 px (AV-17), farger, tastaturfokus, #4189 uendret.
- Kontrast mellom sporet og fyllet (WCAG 1.4.11) er ikke målt (deferred-work).
- Menneskelig gjennomgang og PR. Kim sin 4.3 kan gi konflikt i `KandidatUt` og `api.ts`.
