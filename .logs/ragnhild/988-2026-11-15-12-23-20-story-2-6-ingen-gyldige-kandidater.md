# Story 2.6: Ingen gyldige kandidater

## 2026-11-15 kl. 12:23 — Ragnhild

### Oppgave
Bygge story 2.6 med `bmad-build`: tydelig tomtilstand når alle kandidater er utelukket (FR6, UX-DR16, P-11), slik at den ikke kan forveksles med lasting, feil eller datafeil.

### Plan
- Spesifikasjon: [spec-2-6](../../_bmad-output/implementation-artifacts/spec-2-6-tydelig-melding-nar-ingen-kandidater-er-gyldige.md), allerede godkjent (`ready-for-dev`).
- Modellvalg: Sonnet anbefalt (UI), økten kjørte Sonnet 5.5, så ingen bytte.
- Implementering i underagent uten forkunnskap, deretter gjennomgang mot diffen (baseline `d53be97`) med tre uavhengige lag: Blind Hunter, Edge Case Hunter og Verification Gap.

### Resultat
- Backend: nytt svar `ingen_gyldige_kandidater` (HTTP 200, tom liste, utelukkelser) i `backend/adaptere/api/main.py`. #4189 gir det nye svaret, #4127 er uendret. Datafeil og godkjenningsendepunktet er uendret.
- Frontend: ny tilstand `ingen_gyldige`; `ok` med tom liste behandles som kontraktsbrudd og vises som feil med `RESERVETEKST`. Tomtilstanden har «!»-ikon, full tekst, Ekskludert-boks og innleietekst uten knapp. Modifikatorklasser på alle fire tilstander.
- Tester: `pytest` 415 bestått (kjørt på nytt av meg etter gjennomgangen). Underagenten rapporterte `npm run build` og `npm run test` bestått (49 node-tester, 14 komponenttester); jeg kjørte ikke frontend på nytt selv.
- Retting av generert kode: testen `test_uke_som_slutter_ved_datagrensen_vurderes` forventet `ok` for #4189 og ble rettet til ny status. Fasiten er uendret (AV-07).
- Gjennomgang: ingen funn ble patch, bad_spec eller intent_gap. Verdiktene står i spesifikasjonens Review Triage Log. Ingenting utsatt til `deferred-work.md`.
- Dokumentasjon: README, `docs/testing.md`, vurderingsmatrisen, `epic-2-context.md` og KI-logg `docs/ki-logg/2026-11-15-ingen-gyldige-kandidater.md`. Sprintstatus satt til `review`, spesifikasjonen til `done`.

### Åpne punkter
- Manuell kontroll mot ekte backend (OP-16) er ikke gjort: #4189 viser tomtilstanden og #4127 er uendret, layout ved ca. 800 og 1024 px (AV-17), ikonfarge i `danger`, tastaturfokus på «Vis full liste».
- Gjennomgangen rapporterte lav-alvorlige testhygienefunn som ble avvist (blant annet at fixturen `UTELUKKET_4189` har `totalt` 24 men bare to rader, og at fire-tilstander-testen mangler `finally` rundt `cleanup()`). Se Review Triage Log.
