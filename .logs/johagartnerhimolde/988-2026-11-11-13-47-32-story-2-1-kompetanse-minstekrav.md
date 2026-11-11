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
Milepæl: planleggingen er ferdig, og implementeringen pågår.
- `epic-2-context.md` er laget.
- Spec-en er laget og står som `in-progress`, med `baseline_commit` `75f260f`.
- I sprintstatus står `epic-2` og 2.1 som `in-progress`.
- Ingen kode er committet ennå. Loggen oppdateres når storien er implementert og gjennomgått.

### Åpne punkter
- Story 2.3: at overlappende vakter bare teller som kollisjon og ikke under 11-timersregelen, er en tolkning fra testhjelperne i story 1.2, ikke et gruppevedtak. Det må avklares med gruppa før 2.3.
- Gruppa må kjenne til valget av datafeilform (200 med `status: "datafeil"`) før 2.6. Det utvider statusene i AD-4 og bør føres i referatet når PR-en for 2.1 er gjennomgått.
