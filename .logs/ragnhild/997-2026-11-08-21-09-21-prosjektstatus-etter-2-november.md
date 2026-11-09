# Prosjektstatus etter 2. november

## 2026-11-08 kl. 21:09 — Ragnhild

### Oppgave
Få oversikt etter mange dager med aktivitet: hvilke PR-er som er merget og hvilke som er åpne, hva som er endret siden 2. november, hva appen faktisk kan, status på stories og avklaringspunkter, konflikter og overlapp, og hvilke oppgaver jeg kan ta videre på egen hånd.

### Plan
- Hente PR-er og brancher med `gh pr list --state all`, `gh pr view 9` og `git log origin/main..<branch>`.
- Lese `sprint-status.yaml`, `docs/beslutninger/avklaringspunkter.md` (§2, §4–§8, §11), `prd-beslutningsgrunnlag-2026-11-07.md`, `deferred-work.md` og `issues.md` for alle fire.
- Kartlegge API-endepunktene i `backend/adaptere/api/main.py`, frontendflatene, domenelaget og antall tester.
- Søke etter K-01 («136») og K-02 («32,4») i dokumentasjonen.
- Lese kriterium 1–3 i `docs/emne/sensorveiledning-del-1.md` og statusen i vurderingsmatrisen.

### Resultat
- **PR-er:**
  - Merget siden 2. november: #4 (ÅB-3, 02.11), #5 (story 1.2, 04.11), #7 (story 1.3, 07.11), #6 (speiling av skills i CI, 08.11), #8 (story 1.4, 08.11) og #10 (story 1.5, 08.11).
  - Åpen da rapporten ble skrevet: #9 (backend- og frontendtester i CI, Johannes). Den var godkjent av Mithad og kunne merges uten konflikter. Den ble merget senere samme kveld (`db8c295`), se seksjonen kl. 22:14.
  - Ingen GitHub-issues.
  - `story-1.1-prosjektoppsett` og `story-1.2-fiktiv-turnus` ligger fortsatt på origin, uten commits som ikke er merget. Johannes har satt opp sletting rundt 11.11.
- **Implementert:**
  - Innlogging for turnusansvarlig med JWT i HttpOnly-cookie og scrypt-hash.
  - Beskyttede flater, utløpt sesjon og utlogging.
  - Fiktiv turnus med 25 ansatte og vakthistorikk, lagret i SQLite.
  - Vaktoversikt med «Krever handling».
  - Endepunkter: `/api/helse`, `/api/innlogging`, `/api/meg`, `/api/vaktoversikt`, `/api/utlogging` og `/api/innloggingsinfo`.
  - Tester: 88 backendtester (`def test_`, før parametrisering) og 16 frontendtester.
  - Domenelaget er tomt: `backend/domene/regelmotor/`, `porter/`, `adaptere/ki/` og `tester/regelmotor/` har bare tomme `__init__.py`. Ingen harde regler, ingen rangering og ingen KI i appen ennå.
- **Stories:** Epic 1 er ferdig til og med 1.5. 1.6 og hele Epic 2–5 står i `backlog`, og ingen har meldt seg på 1.6 eller Epic 2. OP-10 anbefalte at noen starter domenedelen av story 2.1 parallelt.
- **Funn som bør avklares:**
  - K-01 står som «Åpent», men regneeksempelet ble rettet 02.11 i ÅB-3 (PR #4, se `.memlog.md` og `docs/ki-logg/2026-11-02-ab-3-ulempebelastning.md`). «136 p» finnes ikke lenger i PRD, epics eller DESIGN.
  - OP-09 (ny review av PR #4) står åpent, men PR #4 er merget etter Mithads gjennomgang.
  - Oversiktstabellen i §2.2 sier at KS-02 og KS-04 er utført, mens overskriftene i §6 fortsatt sier «kontroll ikke gjennomført».
  - OP-05 og AGENTS.md sier at ingen i gruppa har Mac, men jeg kjører macOS (Darwin 25.6).
  - I vurderingsmatrisen står det at story 1.4 er `in-review` og ikke `done`, men PR #8 er merget og sprintstatusen sier `done`.
  - Synspunktene mine (og Mithads) i `prd-beslutningsgrunnlag-2026-11-07.md` er tomme for P-01–P-13, E-01 og E-02. Det holder igjen behandlingen av PRD.
  - Motstriden mellom FR-9 (inntil fem kandidater) og UX-DR7 (alle gyldige) er fortsatt åpen hos Johannes, og må avklares før rangeringstabellen.
  - PR #8 er merget, så `--if-present` i PR #9 kan fjernes.
  - Det er fortsatt åpent om laveste Node-versjon skal heves og om versjonene skal låses eksakt.
  - Forfatternavnene i git er ikke ensartet: Kimsk81/kimsk81, johagartnerHiMolde/Johannes Waatevik Gärtner og Ragnhild/Ragnhild Sætren.
- **Forslag til egne oppgaver:** skrive synspunkter i beslutningsgrunnlaget, rydde i K-01 og OP-09 og føre det i §11, gjøre KS-03 før story 4.7, teste fra ren klone på macOS (OP-05), og melde meg på en hard regel i Epic 2 eller beregningen i story 4.7. Alt er lagt fram for meg; ingenting er avtalt med gruppa.
- Ingen prosjektfiler ble endret i økten.

### Åpne punkter
- Skrive synspunktene mine i `docs/beslutninger/prd-beslutningsgrunnlag-2026-11-07.md` (P-01–P-13, E-01, E-02).
- K-01 og OP-09 i `avklaringspunkter.md` er i realiteten løst gjennom PR #4, men står som åpne. Det må registreres i §11 med kilde (OP-07, mitt ansvar).
- OP-05 og AGENTS.md sier at ingen i gruppa har Mac, men jeg har Mac. Ta det opp med Johannes og tilby å teste fra ren klone på macOS.

## 2026-11-08 kl. 22:14 — Ragnhild

### Oppgave
Kontrollere at synspunktene jeg skrev inn i beslutningsgrunnlaget for PRD er lagret, og at jeg ikke har overskrevet endringer fra andre. Hente siste versjon av `main` uten å miste lokale endringer, og committe og pushe.

### Plan
- `git diff -U0` på beslutningsgrunnlaget: kontrollere at bare linjene `Ragnhild: __` er endret.
- `git fetch` og `git diff HEAD...origin/main` på filene jeg har endret, før pull.
- `git pull --rebase --autostash`, og deretter kontrollere at endringene er intakte og at stashen er tom.

### Resultat
- **Synspunktene:** alle 15 feltene (P-01–P-13, E-01, E-02) er fylt inn. Diffen består av nøyaktig 15 fjernede `Ragnhild: __` og 15 nye linjer; ingen andres tekst er endret. Jeg rettet to skrivefeil på P-10 og E-01 selv. Agenten satte inn ett manglende mellomrom («forslag om») på P-10. Committet i `bf16bbd`.
- **Henting:** 14 nye commits på `origin/main`. Ingen av dem endret beslutningsgrunnlaget, `.logs/ragnhild/` eller `.gitignore`, og rebasen gikk uten konflikt.
- **Rettet i rapporten over:**
  - PR #9 er merget (`db8c295`), og `--if-present` er fjernet fra frontend-CI.
  - Laveste Node-versjon er hevet fra 20.19 til 22.12 (`bf304d9`).
  - Spørsmålet om Node-versjonen i statusrapporten er dermed avgjort.
- **Åpne punkter:** K-01, OP-09 og Mac/OP-05 står fortsatt åpne etter mitt ønske, fordi jeg ikke har tatt stilling til dem ennå.
- **KI-logg:** ingen ny fil i `docs/ki-logg/`, fordi økten ikke genererte kode (README-en for KI-loggen).

### Åpne punkter
Ingen nye. Punktet om synspunktene i beslutningsgrunnlaget er lukket i `issues.md`.
