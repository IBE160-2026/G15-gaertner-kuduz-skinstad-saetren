# Sprintstatus-epicer

## 2026-11-20 kl. 16:56 — johagartnerHiMolde

### Oppgave
Vise sprintstatus (`bmad-sprint-planning`, status) og deretter rette epicstatusene og
tidsstempelet i `sprint-status.yaml`, som Johannes ba om.

### Plan
- Kjøre `sprint_plan.py status`: 21 storyer `done`, 1 `review` (4.6) og 8 `backlog`. Alle
  epicene sto som `in-progress`, og `last_updated` var skrevet som dag-måned, så sjekken av
  om filen er utdatert ble hoppet over.
- Fix-flyten: kjøre `validate`, som fant bare tidsstempelfeilen. Deretter kjøre `generate`
  med `--set epic-1..3=done` mot en kopi og sammenligne med originalen.
- Rette for hånd i stedet, fordi `generate` også ville døpt om nøkkelen for 5.9 (ny
  overskrift med «(P-10B)» i `epics.md`) og brutt om alle handlingspunktene.

### Resultat
- `epic-1`, `epic-2` og `epic-3` er satt til `done`, og `last_updated` er satt til
  `11-20-2026 13:15` (måned-dag), committet i `e531e02` på branchen for 4.6.
  `validate` gir `valid: true`.
- Status etter rettingen: epicene står som 3 `done` og 2 `in-progress`. Skriptet anbefaler
  fortsatt `bmad-code-review` for 4.6, men den gjennomgangen er gjort. Det som gjenstår, er
  godkjenning av PR #32 fra et gruppemedlem.
- Fire åpne handlingspunkter er vist uendret (P-13/OP-02, P-08/KS-04, P-10B og
  versjonslåsing i story 1.1).

### Åpne punkter
- Nøkkelen `5-9-redigere-preferansetekst-etter-kjerneflyt` stemmer ikke lenger med
  overskriften i `epics.md`. Neste `generate` (for eksempel sprintsynkroniseringen i
  `bmad-build`) vil døpe den om til `…-etter-fungerende-kjerneflyt-p-10b`. Gruppa kan
  enten godta det eller fjerne «(P-10B)» fra overskriften.
