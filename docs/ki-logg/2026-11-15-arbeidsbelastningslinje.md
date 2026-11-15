# KI-logg: Story 4.2 – arbeidsbelastningslinje med terskel

Dato: 2026-11-15. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-2-belastningslinje-med-terskel.md), [Epic 4-konteksten](../../_bmad-output/implementation-artifacts/epic-4-context.md), `AGENTS.md` og [gruppevedtakene](../beslutninger/avklaringspunkter.md) (FR8, P-04/K-02, AV-13, AV-17, OP-16). Implementeringsagenten kjørte Claude Sonnet 5.5.

## Oppgave og prompt

Implementer story 4.2 etter spesifikasjonen. Agenten fikk denne instruksen:

> Read …/spec-4-2-belastningslinje-med-terskel.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start.

## Modellens leveranse

- `backend/domene/regelmotor/timebelastning.py`: konstantene 36 t og 1944 minutter (heltall) og `timebelastning(timedelta)` som gir prosent av 36 t (uavrundet, ikke kuttet) og `høy` fra eksakt `timedelta`-sammenligning.
- `KandidatUt` har `timebelastning_prosent` og `hoy_belastning`, satt i kandidatruten og godkjenningsgrunnlaget via `belastning()`. `minutter_i_uka` og `ulempebelastning` er uendret.
- Frontend: typen `Kandidat`, linja (`.belastningslinje` 110×7 px, `.belastningsfyll` i `accent`, `.hoy` i `warn`, bredde kuttet ved 100 %), tokens `--load-bar-width` og `--load-bar-height`, og skjult tekst «Høy belastning» for skjermleser.
- Tester: `tester/regelmotor/test_timebelastning.py` (hele matrisen, 32:23:59, 32:24:00, én sekund under og på grensen, gjentatt kjøring), tre API-tester (Ingrid 88,9 % ikke høy; 32:23, 32:24 og 32:25 ved å forlenge Ingrids første vakt i uke 39), utvidede kontraktstester, og en komponenttest for fargeklasse og bredde under, på og over grensen.

## Retting og kvalitetssikring

Ingen kode måtte rettes etter første kjøring. Eksisterende fixtures (`hjelpere.ts`, 4.1-testen) og kontraktstestene fikk de to nye feltene fordi typen og API-et krever dem. Resultat: **486 av 486 backendtester**, frontendbygg (inkl. typesjekk av tester), 50 modultester og 27 komponenttester bestod. Ingen tester gjør KI-kall.

## Uavhengig gjennomgang (bmad-build steg 4)

Tre gjennomgangsagenter (Blind Hunter, Edge Case Hunter og Verification Gap) kjørte på Sonnet 5.5, uten å ha sett implementeringen. Alle funn og verdikt står i Review Triage Log i spesifikasjonen. Ett funn ble rettet: godkjenningsgrunnlaget ble aldri testet med `hoy_belastning = True`. Jeg la til `test_timebelastning_i_godkjenningsgrunnlaget_følger_32_24_grensen` (32:23 og 32:24 via Ingrid). Resten ble avvist som falske eller ubetydelige, og to ble utsatt til manuell kontroll (kontrast mot sporet og fast bredde 110 px ved smale vinduer).

Manuell kontroll (OP-16) er gjort 2026-11-15 av Ragnhild i Safari på macOS, resultat i spesifikasjonens Verification. Ingen avvik. Funn: appen har ingen mørk drakt (DESIGN.md), så kontrollen i mørk drakt var ikke relevant. VoiceOver-opplesing av «Høy belastning» er ikke avgjort.
