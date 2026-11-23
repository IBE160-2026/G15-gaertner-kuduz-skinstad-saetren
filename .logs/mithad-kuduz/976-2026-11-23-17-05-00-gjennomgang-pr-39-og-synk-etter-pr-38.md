# Gjennomgang av PR #39 og synk etter PR #38

## 2026-11-23 kl. 17:05 — Mithad Kuduz

### Oppgave

To relaterte oppgaver i samme økt: (1) gå grundig gjennom Kims PR #39 (story 5.5,
progressiv lasting) før godkjenning, siden brukeren ba om en dyp gjennomgang; (2)
etter at PR #38 (min egen story 5.7) var godkjent og merget av Kim, pulle main og gå
gjennom hva som faktisk kom inn, siden Kim fant og rettet reelle feil i mitt arbeid
etter min egen PR-åpning.

### Plan

- PR #39: lest PR-beskrivelsen og spesifikasjonens Review Triage Log, sjekket CI,
  bygget et eget `git worktree` og kjørt build/testene selv (ikke bare stolt på
  PR-tallene), stikkprøvd nøkkelmekanismen (`AvveiningerForVakt`) og flere av
  testene som dekker den interne gjennomgangens funn, skannet diffen for
  debug-rester/hemmeligheter. Godkjente og merget etter brukerens eksplisitte
  «godkjenn, merge til main», slettet branchen på GitHub etter eksplisitt «ja».
- Etter `git pull` på `main`: lest Kims oppfølgingslogg
  (`.logs/kimsk81/961-2026-11-22-21-55-39-gjennomgang-pr-38.md`), lest den nye
  `backend/adaptere/forklaringsgrunnlag.py` og endringene i `demo.py`/`main.py` for
  å forstå og verifisere fiksen selv, kjørt hele backend- og frontend-testsuiten på
  oppdatert `main`, og rettet opp sprint-status.yaml og min egen `issues.md` som
  hadde blitt liggende med utdaterte punkter.

### Resultat

**PR #39 (story 5.5):** Godkjent (review postet på GitHub) og merget med
`--merge` til `main`, merge-commit `d0598bd`. Branchen
`story/5-5-progressiv-lasting` slettet på GitHub etter brukerens bekreftelse (fantes
ikke lokalt). Egen verifisering: build OK, 52 modultester + 70 komponenttester
bestod i et isolert worktree, ingen debug-rester eller hemmeligheter i diffen.

**Synk etter PR #38 (story 5.7):** PR #38 ble godkjent og merget av Kim 2026-11-23
(`8a9bdfc`), ikke av meg. Kims egen gjennomgang (se hans logg) fant to reelle feil
utover de sju jeg allerede hadde rettet før push:

1. Et reelt AD-6-brudd: identitetsnøkkelen min, `(kandidat_id, referanse_id)`,
   fanget ikke opp at *referansens* underliggende tall kunne endre seg mens
   kandidat-/referanse-ID-paret og retningen på påstandene holdt seg like — Kim
   viste dette ved å øke referansens timelønn i en midlertidig database og
   observerte at API-et fortsatt rapporterte `ki_kilde: "forhandsgenerert"`. Dette
   motbeviser direkte begrunnelsen jeg skrev i spesifikasjonens Implementation
   Notes for hvorfor den enklere nøkkelen var trygg nok.
2. Frontend manglet kildemerking (UX-DR27) i appbar og panel for demo-modus — det
   kjente, allerede loggførte gapet fra min egen `deferred-work.md`-oppføring.

Begge rettet av Kim, committet `ca2381a` på samme branch før merge. Fiksen for (1)
er en ny, mer robust mekanisme: `backend/adaptere/forklaringsgrunnlag.py` definerer
`forklaringsnøkkel(vakt, kandidat, rangert, referanse)`, en SHA-256-hash over hele
det serialiserte faktagrunnlaget (ikke bare IDer), med `KONTRAKTSVERSJON = 2`.
`DemoKiAdapter` fikk en ny protokoll `DemoOppslag.forklar_med_oppslag(kandidat,
referanse, oppslagsnøkkel)` ved siden av den vanlige `forklar()` (som fortsatt
virker, men uten oppslag), og `main.py`s `avveining()`-rute bruker
`isinstance(ki, DemoOppslag)` til å beregne og sende riktig nøkkel bare for
demo-adapteren. Live-porten (`OpenRouterKiAdapter.forklar`) er uendret. Jeg leste
koden selv og er enig i at dette faktisk lukker gapet, siden hele faktagrunnlaget nå
inngår i identiteten i stedet for bare IDene. To ytterligere uavhengige
gjennomganger (per Kims logg) fant og rettet manglende grunndata i avtrykket og feil
kilde ved ugyldige metadata før merge.

Egen verifisering på oppdatert `main` (ikke bare Kims tall): `pytest` i `backend/`
ga **891 av 891** bestått (opp fra de 877 jeg selv målte før push — de ekstra
kommer dels fra Kims rettinger, dels fra Ragnhilds `test_terminallogg.py`, se under).
Frontend: `npm run build` OK, `npm run test` ga **74 av 74** bestått
(vitest/komponenttester; node-testene inngår i samme kjøring).

Oppdaterte selv (ingen kodeendring, bare sporing):
- `_bmad-output/implementation-artifacts/sprint-status.yaml`: `5-7-demo-modus-uten-api-nøkkel` fra `review` til `done`, med kommentar om PR #38 og Kims oppfølging.
- `.logs/mithad-kuduz/issues.md`: lukket fire punkter som var blitt stående åpne fra før denne økten startet (PR #34 var allerede merget 2026-11-20, frontend-kildelinjegapet er løst av Kim, PR #38-åpning og -gjennomgang er fullført), og lagt til et nytt, lukket punkt som dokumenterer Kims to funn og retting.

**Annet som kom inn med samme pull** (ikke gjort av meg, bare observert):
Ragnhild har levert en egen story for terminallogging (`spec-loggoppsett-backend.md`,
`docs/ki-logg/2026-11-23-loggoppsett-backend.md`, ny `backend/tester/api/test_terminallogg.py`)
— dette ser ut til å løse det gamle, loggførte problemet med at fremdriftsmeldinger
fra `tolk_ventende` ikke vises i terminalen (opprinnelig fra story 5.1, se
`deferred-work.md`). Ragnhild har også levert en refleksjonsrapport
(`docs/emne/refleksjonsrapport-mal.md`, `docs/emne/refleksjonsrapport-stoffgrunnlag.md`)
og en gjennomgang mot sensorveiledningen. Jeg har ikke lest disse i detalj i denne
økten.

### Åpne punkter

- Jeg har ikke selv lest Ragnhild sin `loggoppsett-backend`-leveranse eller
  refleksjonsrapporten i detalj — bare observert at de kom inn med pullen.
- Epic 5 gjenstår: 5-8 (sensor kan kjøre live KI) og 5-9 (redigere preferansetekst)
  er fortsatt `backlog`.
