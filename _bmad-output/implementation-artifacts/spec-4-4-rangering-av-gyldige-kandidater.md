---
title: 'Story 4.4: Rangering av gyldige kandidater'
type: 'feature'
created: '2026-11-15'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '7a04261964851e7f08334067b1322a43f2b64122'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** De gyldige kandidatene vises alfabetisk, så turnusansvarlig må selv veie kostnad, timebelastning, ulempe og preferanse mot hverandre (FR9, SM-3).

**Approach:** Regelmotoren rangerer alle gyldige kandidater deterministisk etter PRD §4.4 og leverer porten `RangertKandidat`. Kandidatflaten viser en rangeringstabell med de fem øverste og «Vis alle gyldige kandidater».

## Boundaries & Constraints

**Always:**
- Totalscore = 0,40 × kostnadspoeng + 0,20 × timebelastningspoeng + 0,15 × Ulempescore + 0,25 × preferansepoeng. Vektene og ulempetaket (300) er navngitte parametere i `domene/regelmotor` og sendes inn som argument (AV-11).
- Kostnad (som `float`, §11) og timer i startuka normaliseres med min–maks over alle gyldige: lavest gir 100, høyest 0. Er alle like, eller bare én er gyldig, gir faktoren 50 (AV-05). Ulempescoren har fast skala.
- Sortering på uavrundet totalscore, og stigende ansatt-ID ved reell likhet (K-03). Visningen avrunder til én desimal.
- **Likhet (vedtatt av Johannes 2026-11-15, spørsmålet fra §11):** Faktorpoeng og totalscore regnes eksakt med `fractions.Fraction` fra `float`-inndataene. Lik betyr eksakt lik `Fraction`, uten toleranse. Verdiene gjøres om til `float` først i porten.
- Preferanse: tolket kategori gir 100/75/50/25/0. Uten tolkning gir den 50 med status `venter_paa_tolkning` eller `kunne_ikke_tolkes`. Uten tekst gir den 50 med `ingen_registrert` (P-05). Kompetanse gir ingen poeng.
- Bare `domene/regelmotor` konstruerer `RangertKandidat`, og bare gyldige kandidater rangeres (AD-1, NFR2).

**Never:** Ingen KI, ingen live tolkning, ingen ny lagring eller tabell, ingen endring av harde regler eller av `beregn_kostnad`. Ingen avviksnotat (4.5) og ingen layout for smale vinduer (4.6).

## I/O & Edge-Case Matrix

| Scenario | Input | Forventet |
|---|---|---|
| #4127, alle 50 i preferanse | seed | Jonas 79,40, Mette 72,40, Thomas 71,50, Ingrid 24,50. Thomas er billigst og havner som nr. 3 |
| #4127, tolket 75/75/0/100 | domenetest | 85,65 / 78,65 / 59,0 / 37,0 (fasiten i `testdata.FASIT`) |
| Jonas mot Mette | ulempe 40 mot 180 p | nøyaktig 7,0 i forskjell (AV-12) |
| Én gyldig eller alle like | kostnad og timer like | 50 for begge faktorene |
| Bare kompetansen er ulik | domenetest | lik totalscore, rekkefølge etter ID |
| Matematisk lik total | `[0,0,0,300/7]` mot `[0,100/7,200/7,100/7]` | regnes som like, rekkefølge etter ID |
| Over fem gyldige | domene- og komponenttest | fem vises, «Vis alle» viser resten |
| Datafeil eller null gyldige | som før | ingen tabell (P-08, P-11) |

</frozen-after-approval>

## Code Map

- `backend/domene/typer.py`: `Kandidat` får `preferanse: str | None`, `stilling` og `ansiennitet`, alle med standardverdi og `compare=False`. `kandidatgrunnlag.py` fyller dem fra `AnsattRad`.
- `backend/domene/porter/` (ny `rangering.py`): `TolketPreferanse` (minimal, med `kategori`), `Tolkestatus` og `RangertKandidat`. De er frosne dataklasser uten logikk, som `utelukkelse.py` (story 2.5). Story 5.1 utvider `TolketPreferanse`. Avviket fra «Pydantic» i arkitekturen følger 2.5-presedensen og føres i KI-loggen.
- `backend/domene/regelmotor/rangering.py` (ny): `Rangeringsparametere` (vektene som `Fraction` og `tak = ulempebelastning.STANDARD_TAK`), `STANDARD_PARAMETERE`, `PREFERANSEPOENG` og `ranger(vurdering, vakt, tolkede={}, feilede=frozenset(), parametere=...)`.
  - Gjenbruk `beregn_kostnad`, `timer_i_startuka`, `timebelastning`, `kompetansenivå` og `vurdering.ulempe_per_kandidat`.
  - Ulempescoren regnes på nytt fra `poeng` med parameterens tak.
  - `RangertKandidat` bærer faktorpoeng, totalscore og plass, men ikke rå minutter.
- `backend/adaptere/api/main.py`: kandidatruten kaller `ranger` og returnerer `RangertKandidatUt` (alle felt i `KandidatUt` + plass, totalscore, faktorpoeng, preferansepoeng, tolkestatus, stilling, ansiennitet), sortert etter plass. `KandidatUt` og godkjenningsruten er uendret.
- `frontend/src/api.ts` og `kandidater.ts`: ny type og `synligeKandidater(kandidater, visAlle)`, som gir de fem første eller alle.
- `frontend/src/komponenter/Kandidatflate.tsx`: `<table>` i rullebeholder erstatter `ul.kandidatliste`. Gjenbruk `Kostnadsvisning`, `Varselmerke`, belastningslinjen og ulempecellen. Velg-knappen står i siste kolonne, der ekspanderen fra epic 5 kommer.
- `frontend/src/tekster.ts` og `stil/app.css`: kolonneoverskrifter, tagger for tolkestatus og kategori, `rank-badge` og `row-alt` med tokens (AV-13).
- Tester: `backend/tester/regelmotor/test_rangering.py` (ny), `tester/api/test_kandidater.py`, `frontend/tester/kandidater.test.mjs` og `tester/komponenter/kandidatflate.test.tsx`.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/domene/` og `kandidatgrunnlag.py`: porter, parametere og `ranger`. Testene dekker hver rad i matrisen, vektvariasjon via parameter, alle fire tolkestatuser, at utelukkede aldri rangeres, og determinisme med stokket inndata. Fasiten regnes for hånd (KS-02), ikke ved å kopiere programmets resultat.
- [ ] `backend/adaptere/api/main.py` og API-tester: rangert svar for #4127 med totaler, plass og status. #4189 og datafeil er uendret.
- [ ] `frontend/src/` og tester: tabellen, de fem øverste, «Vis alle» med fokus, taggene, `rank-badge` og `row-alt` (OP-16).
- [ ] Dokumentasjon: `docs/ki-logg/2026-11-15-rangering.md`, flytlisten i `docs/testing.md`, `docs/emne/vurderingsmatrise.md`, `sprint-status.yaml` og statuslinjen i `AGENTS.md`.

**Acceptance Criteria:**
- Gitt et komplett grunnlag: når kandidatene lastes etter vaktvalg, viser tabellen kolonnene rangeringsnummer, kandidat (navn og stilling · ansiennitet i `meta`), Kompetansenivå-tag, kostnad, timebelastning, ulempe og preferanse-tag. Tallene står i raden uten klikk.
- Gitt samme input i ulik rekkefølge: når rangeringen kjører to ganger, blir plassene og totalene identiske.
- Gitt at «Vis alle gyldige kandidater» brukes: når listen utvides, vises alle i rangert rekkefølge, og Velg virker for hver av dem.

## Design Notes

`Fraction(float)` er eksakt for verdien `float` faktisk har. Min–maks og vektene (`Fraction(2, 5)` osv.) gir da nøyaktig like summer for matematisk like totaler, som i eksempelet fra §11 (75/7). `float()` gjøres først i porten. Forkastet: `round(total, 9)` i nøkkelen, som kan skille like verdier ved en avrundingsgrense, og `math.isclose`, som ikke er transitiv.

Spesifikasjonen er på ca. 2000 tokens, over grensen på 1600. Johannes valgte 2026-11-15 å beholde den samlet, fordi rangering og tabell utgjør ett mål med felles akseptansekriterier.

## Verification

**Commands:**
- `backend/.venv/Scripts/python -m pytest` (fra `backend/`): alle tester består, også arkitekturtesten.
- `npm.cmd run build` og deretter `npm.cmd run test` (fra `frontend/`, etter hverandre): begge består.

**Manual checks:**
- Ekte backend med seed for #4127: rekkefølgen er Jonas, Mette, Thomas, Ingrid, og plassnummeret er i `accent`, fett, 14px.
- Ved 1080 og 1600 px: tabellen ruller i sin egen beholder, ikke siden (AV-14). Fokusmarkering på Velg og «Vis alle» er synlig.
