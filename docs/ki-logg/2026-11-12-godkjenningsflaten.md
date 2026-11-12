# KI-logg: Story 3.1 – velge kandidat og se godkjenningsflaten

Dato: 2026-11-12. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md), [Epic 3-konteksten](../../_bmad-output/implementation-artifacts/epic-3-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (FR12, NFR2, AD-4, AD-5, P-08, P-09, UX-DR3, UX-DR17, UX-DR19, UX-DR22–24, OP-13). Arbeidet ble gjort av Claude Code (Opus 5.5) i `bmad-build`, på branchen `story-3.1-godkjenningsflaten`. `docs/modellvalg-stories.md` anbefaler Sonnet for 3.1, men Johannes valgte Opus.

## Oppgave og prompt

- **Hovedøkten:**
  - Johannes ba om å starte 3.1 parallelt med Ragnhilds 2.4, gjøre starten synlig for gruppa med en pushet branch og ta anbefalingene for 3.1 inn i konteksten.
  - En underagent bygde `epic-3-context.md`, og en annen undersøkte koden.
  - Hovedøkten skrev spesifikasjonen. Johannes besvarte tre åpne spørsmål:
    - 1A: URL-en er `/vakt/<nr>/godkjenning/<ansatt_id>`.
    - 2A: «Godkjenn erstatning» er aktiv, men viser bare en `meta`-linje fram til 3.2.
    - 3A: Ved 404 vises den egne teksten «Kandidaten kan ikke velges for denne vakten.»
  - Johannes beholdt spesifikasjonen hel, på omtrent 2 900 tokens, og godkjente den.
- **Instruksjonen til implementeringsagenten:** «Read …/spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **Backend** (`backend/adaptere/api/main.py`): `GodkjenningsgrunnlagUt` og `GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id}`.
  - Ruten vurderer hele grunnlaget med `vurder_kandidater` og slår opp id-en blant de gyldige.
  - Datafeil besvares før oppslaget.
  - Utelukket, ukjent eller opprinnelig oppsatt Ansatt gir samme 404 `ikke_funnet` (NFR2), og det samme gjør en vakt som ikke mangler bemanning.
  - Ruten er bare lesende og har ingen `POST`.
- **Frontend:**
  - `navigasjon.ts` har fått `godkjenningFraSti`, `godkjenningssti` og `kandidatsti`.
  - `api.ts` har fått `hentGodkjenningsgrunnlag`.
  - `godkjenning.ts` er ny og har tilstandene og vernet mot sene svar etter mønsteret i `kandidater.ts`.
  - `Godkjenningsflate.tsx` er ny.
  - `Kandidatflate.tsx` har fått «Velg» per rad.
  - `TEKSTER.godkjenning` er en egen blokk, så endringene ikke blandes med det 2.4 endrer.
  - `format.ts` har fått `vaktlinje` og `datoOgTidsrom`.
  - `app.css` har fått stil som bare bruker tokens.
  - README er oppdatert.
- **Tester:**
  - `backend/tester/api/test_godkjenningsgrunnlag.py` (22).
  - `frontend/tester/godkjenning.test.mjs` (12).
  - Én ny test i `frontend/tester/format.test.mjs`.

## Korrigering og kvalitetssikring

- **Nettleserkontroll ved implementeringsagenten:** kjørt mot en egen testdatabase i scratchpad. `backend/turnushjelperen.db` ble ikke rørt. Kontrollen dekket:
  - «Velg» for Mette, som åpnet `/vakt/4127/godkjenning/5`.
  - Tastatur: Tab og Enter på «Godkjenn erstatning» viste `meta`-linjen, og Shift+Tab og Enter på «Avbryt» gikk tilbake.
  - Tilbakeknappen.
  - `/vakt/4127/godkjenning/1` (Silje) viste teksten fra 3A.
  - `/godkjenning/05` viste «Fant ikke siden».
  - Vaktvalg var uendret etterpå.
- **Hovedøkten** leste hele diffen mot spesifikasjonen og kjørte testene selv.
- **Uavhengige gjennomganger:** Blind Hunter, Edge Case Hunter og Verification Gap, alle på Opus og uten kjennskap til implementeringen. De ga 20 funn. To av dem var det samme funnet, så det ble 19 rader i spesifikasjonens Review Triage Log:
  - 7 rettet.
  - 2 utsatt til `deferred-work.md`: koblingen i komponentene er bare kontrollert manuelt fordi det mangler en komponentrigg, og brødsmulestien har ikke lenker.
  - 10 avvist med begrunnelse.
- **Rettet etter gjennomgangen:**
  1. Den regeluavhengige 404-testen gikk over `range(1, 26)`. Den går nå over alle Ansatte i `ANSATTE`, så nye testdata ikke blir hoppet over.
  2. Lekkasjetesten hadde regelnavnene skrevet inn for hånd. Den håndskrevne listen hadde «kolliderende», mens den faktiske årsaken er «kolliderende vakt». Navnene hentes nå fra `REGLER`, så 2.4 dekkes automatisk. En påstand om Silje som ikke hørte til testen, er fjernet.
  3. Docstringen for `GodkjenningsgrunnlagUt` nevnte ikke den som opprinnelig var satt opp.
  4. Oslo-testen for `vaktlinje` og `datoOgTidsrom` er flyttet til `format.test.mjs`, så den også kjøres med `TZ=America/New_York`.
  5. Den tilgjengelige etiketten «Velg <navn>» er testet.
  6. README-listen over testfiler er oppdatert.
  7. Denne KI-loggen og vurderingsmatrisen manglet.
- **Resultater etter rettingene:** `pytest` i `backend/` ga **359 bestått**, inkludert import-linter. `npm.cmd test` ga **39 bestått**, og `npm.cmd run build` bestod.

## Nettleserkontroll ved Johannes

Johannes gjorde nettleserkontrollen 2026-11-12 og godkjente den. Knappene oppførte seg som forventet, og flaten så bra ut.

## Gjenstår

- PR-gjennomgang av et annet gruppemedlem. Den som merger sist av 3.1 og 2.4, løser konflikten i `Kandidatflate.tsx` og `tekster.ts`.
