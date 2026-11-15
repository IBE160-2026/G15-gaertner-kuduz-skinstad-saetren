---
title: 'Story 4.4: Rangering av gyldige kandidater'
type: 'feature'
created: '2026-11-15'
status: 'done'
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
- [x] `backend/domene/` og `kandidatgrunnlag.py`: porter, parametere og `ranger`. Testene dekker hver rad i matrisen, vektvariasjon via parameter, alle fire tolkestatuser, at utelukkede aldri rangeres, og determinisme med stokket inndata. Fasiten regnes for hånd (KS-02), ikke ved å kopiere programmets resultat.
- [x] `backend/adaptere/api/main.py` og API-tester: rangert svar for #4127 med totaler, plass og status. #4189 og datafeil er uendret.
- [x] `frontend/src/` og tester: tabellen, de fem øverste, «Vis alle» med fokus, taggene, `rank-badge` og `row-alt` (OP-16).
- [x] Dokumentasjon: `docs/ki-logg/2026-11-15-rangering.md`, flytlisten i `docs/testing.md`, `docs/emne/vurderingsmatrise.md`, `sprint-status.yaml` og statuslinjen i `AGENTS.md`.

**Acceptance Criteria:**
- Gitt et komplett grunnlag: når kandidatene lastes etter vaktvalg, viser tabellen kolonnene rangeringsnummer, kandidat (navn og stilling · ansiennitet i `meta`), Kompetansenivå-tag, kostnad, timebelastning, ulempe og preferanse-tag. Tallene står i raden uten klikk.
- Gitt samme input i ulik rekkefølge: når rangeringen kjører to ganger, blir plassene og totalene identiske.
- Gitt at «Vis alle gyldige kandidater» brukes: når listen utvides, vises alle i rangert rekkefølge, og Velg virker for hver av dem.

## Review Triage Log

Første gjennomgang 2026-11-15 med tre uavhengige agenter på Opus: Blind Hunter (B), Edge Case Hunter (E) og Verification Gap (V).

| Funn | Verdikt og bevis | Tiltak |
|---|---|---|
| B1: likhetsvedtaket står bare i spesifikasjonen. §11 i referatet og `epic-4-context.md` kaller det fortsatt «ikke vedtatt» | medium: AV-08 krever sporbare vedtak i referatet, og sensor leser dokumentasjonen | patch: ny §11-oppføring og rettet epic-kontekst |
| B2/E4/V-andre: `rangert_ut` regner kostnad, timer og ulempe en gang til, uavhengig av porten. Ulempescoren finnes i to utgaver (`float` og `Fraction`) | medium: epic 5 forklarer porten, mens tabellen viser egne tall, og ingen test sjekker at de er like | patch: test som sammenligner portfeltene med API-feltene for #4127 |
| V1: `kostnadstype == "ordinær"` og kveld-, helge- og nattetimer i porten testes ikke | medium: en byttet fordeling eller `>= 0` i stedet for `> 0` består alle testene (forhåndsverifisert av V) | patch: utvidet porttest for alle fire kandidatene på #4127 |
| E6: `ulempeOverskrift` i `tekster.ts` er ikke lenger i bruk | low: verifisert med grep, ingen bruker igjen | patch: slettet |
| B6: «p» betyr «verre» i ulempekolonnen og «bedre» i preferansekolonnen | low: står side om side og kan misforstås. Én desimal er riktig etter K-03 | patch: preferansepoeng vises som «poeng» |
| B3: docstringen til `RangertKandidat` beskriver forholdet mellom `float` og sortering feil | low: villedende for 4.5 og epic 5 | patch: docstringen er rettet |
| B11: statuslinjen i AGENTS.md er feil etter merge | low: krever endring i en agentkontekstfil | defer |
| E1/E2: ukjent `tolkestatus`, eller `tolket` uten kategori, gir en tom tagg | low: krever kontraktsbrudd fra API-et (`Literal`), og retting krever en ny vakt | avvist |
| E3: `tak = 10**400` gir `OverflowError`, ikke `ValueError` | low: urealistisk inndata, retting krever en ny vakt | avvist |
| E5/B12/V-andre: regex-testen for AD-1 fanger ikke `replace()` eller alias | low: slike omveier er usannsynlige i hverdagen, og en AST-sjekk gir mer kompleksitet | avvist |
| B4: testdataene i frontend har lik totalscore og plass = id | low: komponenten viser rekkefølgen fra API-et, og ingen frontendtest sjekker sorteringen | avvist |
| B5: ingen test binder kategorinøklene i backend og frontend sammen | low: stien `tolket` kan ikke nås før epic 5. Tas i 5.1/5.2 | avvist |
| B7: totalscore vises under Nr. uten at UX-DR sier det | low: PRD §4.4 forutsetter visning med én desimal. Johannes valgte 2026-11-15 å beholde totalscoren under plassnummeret | avvist, beholdes etter brukerens valg |
| B8: AV-12-testen bruker `== 7.0` på `float` | low: data og formel er deterministiske, og en rød test ville selv vært et nyttig signal. Domenetesten har eksakt brøkfasit | avvist |
| B9: sesjonslogg og `issues.md` mangler | false: loggføres i steg 05 før sluttsvaret, etter AGENTS.md | avvist |
| B10: kriterienumrene i vurderingsmatrisen kan ikke spores | false: numrene viser til kriteriekolonnen i matrisen (sensorveiledningen), som i alle tidligere milepæler | avvist |
| B13: typehintet `float` på `tak`, og stille standardverdier for `stilling` og `ansiennitet` | low: `AnsattRad` har begge som NOT NULL, og standardverdiene brukes bare i testene | avvist |

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
