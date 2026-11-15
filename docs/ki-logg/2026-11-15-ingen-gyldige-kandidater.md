# KI-logg: Story 2.6 – Tydelig melding når ingen kandidater er gyldige

Dato: 2026-11-15. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-6-tydelig-melding-nar-ingen-kandidater-er-gyldige.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md`, [avklaringspunktene](../beslutninger/avklaringspunkter.md) og [testplanen](../testing.md). Arbeidet ble gjort av Claude Code (Sonnet 5.5) som implementeringsagent, på branchen `story-2.6-ingen-gyldige-kandidater`.

## Oppgave og prompt

Instruksjonen: «Read …/spec-2-6-tydelig-melding-nar-ingen-kandidater-er-gyldige.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **Backend** (`adaptere/api/main.py`): ny `IngenGyldigeUt`. `kandidater()` svarer `status: "ingen_gyldige_kandidater"` med tom liste og `utelukkelser` når `vurdering.gyldige` er tom. Datafeil og godkjenningsendepunktet er uendret.
- **Frontend**: `Kandidatsvar` og `Kandidattilstand` har ny variant. `tilstandFraSvar` gjør `ok` med tom liste til feil med `RESERVETEKST`. `Kandidatflate.tsx` har tomtilstanden (`.alert-icon`, tekst, Ekskludert-boks, innleietekst uten knapp) og modifikatorklasser på alle fem paneler. `.tomtilstand-*` i `app.css` bruker bare tokens.
- **Tester**: backend (4189 gir ny status og fasit, invarianter, datafeil blir aldri «ingen gyldige»), `kandidater.test.mjs` og `kandidatflate.test.tsx` (tomtilstand, `ok` med tom liste, fire-tilstander-test).

## Korrigering og kvalitetssikring

- `test_uke_som_slutter_ved_datagrensen_vurderes` hevdet `status == "ok"` for #4189 og feilet etter endringen. Det er en følge av ny kontrakt, ikke en regelendring. Rettet til `ingen_gyldige_kandidater`. Fasiten er ikke endret (AV-07).
- Fire-tilstander-testen sammenligner tekst, panelklasse og kombinasjonen av rolle, ikon og knapp, og sjekker i tillegg de forventede kombinasjonene hver for seg.
- Kjørt: `pytest` 415 bestått (inkl. import-linter), `npm run build` bestått, `npm run test` 49 `node:test` og 14 komponenttester bestått.
- Manuell nettleserkontroll mot ekte backend (OP-16) er gjort av Ragnhild 2026-11-15: #4189 og #4127 som forventet, layout bestått ved 1024×800 px, og feiltilstanden med backend nede er ulik tomtilstanden. Se spesifikasjonens Verification.
- Ikke gjort: ingen mutasjonstest er kjørt for de nye komponenttestene.
