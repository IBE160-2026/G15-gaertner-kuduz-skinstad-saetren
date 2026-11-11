# Story 2.1: Gyldige kandidater filtrert på kompetanse-minstekrav

## 2026-11-11 kl. 13:47 — johagartnerHiMolde

### Oppgave
Bygge story 2.1 med `bmad-build`: den første harde regelen (kompetanse-minstekrav), domenekjernen, import-linter, API for kandidatlisten og kandidatlisten i frontend. Arbeidet ligger på en egen branch, og branchen ble pushet tidlig slik at gruppa ser at storien er påbegynt.

### Plan
- Modellvalg: 2.1 er anbefalt Opus i `docs/modellvalg-stories.md`, og økten kjører Opus 5.5.
- Branchen `story-2.1-kompetanse` ble opprettet fra `main` (`75f260f`) og pushet til origin.
- En underagent samlet epic-konteksten i `_bmad-output/implementation-artifacts/epic-2-context.md`, og en annen kartla koden.
- Spec: [spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md](../../_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md). Den er godkjent av Johannes.
- Johannes avgjorde fire spørsmål:
  - P-08 (datafeil) bygges i 2.1, med datagrense `turnus.periode_slutt`.
  - Datafeil er et 200-svar med `status: "datafeil"`, `kode` og `datagrense`. Valget binder 2.6.
  - En midlertidig merknad sier at bare kompetanseregelen er aktiv. Den fjernes i 2.4.
  - Spec-en beholdes hel, selv om den er over 1600 tokens.
- Implementeringen gjøres av en underagent uten samtalekontekst. Etterpå gjennomgår uavhengige agenter koden.

### Resultat
Storien er implementert, gjennomgått og committet lokalt i `61c8dd0` på `story-2.1-kompetanse`. Den er ikke pushet.

- **Domene:** `backend/domene/typer.py`, `regelmotor/kompetanse.py` og `regelmotor/vurdering.py`. Regellisten samler alle årsaker, datafeil stopper vurderingen (P-08), og sorteringen er norsk alfabetisk.
- **Lagring og API:**
  - `adaptere/lagring/kandidatgrunnlag.py`.
  - Felles filter `finn_ubemannet_vakt` i `vaktdetaljer.py`.
  - Endepunktet `GET /api/vakter/{nr}/kandidater`, som logger årsaken når det svarer med datafeil.
- **Import-linter 2.16:** kontrakten dekker hele `domene` og kjøres i `pytest` (`tester/test_arkitektur.py`).
- **Frontend:** `src/kandidater.ts` og `Kandidatliste` i `Kandidatflate.tsx`, med «Nivå N/4», lasting, feil, datafeil, merknad og P-09-vern.
- **Dokumentasjon:**
  - AD-4 i `ARCHITECTURE-SPINE.md` beskriver nå datafeilformen.
  - README og vurderingsmatrisen er oppdatert.
  - KI-loggen er `docs/ki-logg/2026-11-11-kompetanse-minstekrav.md`.
  - `deferred-work.md` har to nye punkter.
- **Kvalitetssikring:**
  - 229 backendtester og 26 frontendtester består, og bygget går gjennom.
  - Import-linter og P-09-vernet ble kontrollert med bevisste feil.
  - Tre gjennomgangsagenter (Opus) fant til sammen 25 funn. 12 er rettet som patcher, 2 er utsatt og 11 er avvist med begrunnelse, se Review Triage Log i spec-en.
- **Status:** spec-en står som `done`. I sprintstatus står 2.1 som `review`, i påvente av PR-gjennomgangen.

### Åpne punkter
- Nettleserkontroll av 2.1: logg inn, velg #4127 og #4189, og kontroller listene (16 og 21, uten Silje og Eirik), taggen «Nivå N/4» og merknaden. Den ble ikke gjort, fordi agenten ikke fikk starte utviklingsserverne.
- Gruppa gjennomgår PR-en for 2.1. Sett storien til `done` i sprintstatus etterpå.
- AGENTS.md sier fortsatt «ingen domenelogikk ennå» og nevner ikke `tester/regelmotor/` eller arkitekturtesten. Det er en agentkontekstfil (AV-08), så et gruppemedlem må velge å endre den.
- Story 2.3: at overlappende vakter bare teller som kollisjon og ikke under 11-timersregelen, er en tolkning fra testhjelperne i story 1.2, ikke et gruppevedtak. Det må avklares med gruppa før 2.3.
- Datafeilformen (200 med `status: "datafeil"`) er ført i AD-4, men ikke i referatet. Den føres der når PR-en er gjennomgått.
