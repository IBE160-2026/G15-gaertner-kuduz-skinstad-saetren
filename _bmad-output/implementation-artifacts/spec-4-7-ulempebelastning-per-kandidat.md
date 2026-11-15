---
title: 'Story 4.7: Ulempebelastning per kandidat'
type: 'feature'
created: '2026-11-15'
status: 'done'
route: 'dispatch'
baseline_commit: '6a7e8713817b199c31fac1df76a5a62a98d53b94'
review_loop_iteration: 0
context:
  - 'docs/beslutninger/ks-03-tidskategorier-2026-11-15.md'
---

<frozen-after-approval reason="Brukeren har uttrykkelig bedt om implementasjon av hele story 4.7">

## Intent

**Problem:** Gyldige kandidater mangler beregnet historisk ulempebelastning, og turnusansvarlig kan ikke se om ubekvemme vakter fordeles skjevt.

**Approach:** Beregn poeng og fast skalert score deterministisk fra kandidatens vakthistorikk, og vis poeng med kategorifordeling på kandidatflaten. Kontroller KS-03 før beregningen.

## Boundaries & Constraints

**Always:** AV-02/09/11 og PRD §4.3: 672 faktiske timer i halvåpent UTC-vindu før vaktstart; klipp kryssende vakter; lokal kategori i Europe/Oslo, natt > helg > kveld > dag; sats 0/1/2/3; tak 300 som navngitt argument; uavrundet poeng og score; hver faktisk arbeidstime én gang. Helligdager følger ukedagen. Beregn bare for gyldige kandidater etter P-08, uten KI. Bruk KS-03-dokumentets uavhengige fasit.

**Never:** Endre dataskjema eller andres 3.2-/4.1-brancher; innfør ikke rangering fra story 4.4 eller time-/kostnadsmodellen fra 4.1–4.3; ingen ny terskel eller varselfarge for ulempe.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Vanlige vakter | Fire vakttyper på hverdag/helg | Kategori, timer og poeng som i KS-03 | Ugyldige tidspunkter stopper vurdering |
| Målevindu | Historisk vakt krysser en av grensene | Bare overlapp i `[start−672t, start)` telles | Manglende datadekning gir datafeil |
| Sommertid | Natt over mars/oktober 2026 | 7/9 faktiske timer; 20/26 poeng | Lokal veggklokke brukes ikke som varighet |
| Uten historikk | Ingen overlappende vakter | 0 poeng, score 100, alle kategorier 0 | Ingen tom visning |
| Tak | 0, 300, >300 poeng, annet positivt tak | Score etter `maks(0,100×(1−poeng/tak))` | Ugyldig tak avvises |

</frozen-after-approval>

## Code Map

- `backend/domene/typer.py`: `Vakt`, `Kandidat.vakter` og `Tidsrom` er rene domenetyper; `RangertKandidat` finnes ennå ikke.
- `backend/domene/regelmotor/vurdering.py`: hard filtrering og P-08-datakontroll; utvid datavinduet for 4.7 uten å gjøre ulempe til hard regel.
- `backend/adaptere/lagring/kandidatgrunnlag.py`: henter allerede historiske vakter og angir `historikkstart` i UTC. Ingen skjemaendring.
- `backend/adaptere/api/main.py`: `KandidatUt` og kandidatendepunktet; send ulempeverdier videre for bare gyldige.
- `frontend/src/api.ts`, `komponenter/Kandidatflate.tsx`, `tekster.ts`, `stil/app.css`: vis tekstkolonne etter timebelastning når den finnes; nåværende liste er enkel og har ennå ingen timekolonne.
- `backend/tester/regelmotor/`, `backend/tester/api/test_kandidater.py`, `frontend/tester/komponenter/kandidatflate.test.tsx`: eksisterende testmønstre.

## Tasks & Acceptance

**Execution:**
- [x] `docs/beslutninger/ks-03-tidskategorier-2026-11-15.md` og `avklaringspunkter.md` – dokumenter uavhengig kontroll og status.
- [x] `backend/domene/regelmotor/ulempebelastning.py` – beregn kategoritimer, poeng og score over faktiske tidsintervaller.
- [x] `backend/domene/regelmotor/vurdering.py` og domenets resultattype – krev komplett 672-timersgrunnlag og gjør ulempeverdier tilgjengelige for senere 4.4.
- [x] `backend/adaptere/api/main.py` og frontendfilene i Code Map – send og vis poeng med kveld/helg/natt uten varselstil.
- [x] `backend/tester/regelmotor/test_ulempebelastning.py`, API- og komponenttester – dekk matrisen, minuttgrenser, fredag–lørdag, søndag–mandag, to like kandidater og gjentatt kjøring.
- [x] `docs/ki-logg/`, `docs/emne/vurderingsmatrise.md` og sesjonsloggen – før sporbar kontroll og kvalitetssikring.

**Acceptance Criteria:**
- Given en gyldig kandidat, when kandidatlisten lastes, then vises ulempepoeng og fordeling for denne kandidaten, også 0 p, uten at utelukkede får beregning.
- Given samme fullstendige grunnlag, when beregningen kjøres på nytt, then er uavrundet resultat identisk og uavhengig av øvrige kandidater.
- Given poeng og fordeling, when resultatet kontrolleres, then er poeng = kveld + 2×helg + 3×natt og score følger parameterisert tak.

## Implementation Notes

Overlappende og dupliserte intervaller slås sammen før tidskategorisering.
Timekolonnen fra parallell story 4.1 finnes ikke ennå; rekkefølgen må
kontrolleres ved integrasjon. Nettleserkontroll og menneskelig gjennomgang
gjenstår; storyen står derfor `review`.

## Spec Change Log

## Review Triage Log

Tre uavhengige lag gjennomgikk diffen mot `6a7e871`; kontrollene er vurdert
enkeltvis. Verifikasjonslaget rapporterte ingen funn.

| Funn | Vurdering og behandling |
| --- | --- |
| B1: Målevindu er ikke forklart i flaten | Medium: leseren kan misforstå perioden. Rettet med tekst om 672 timer. |
| B2: Svært små verdier vises som null | Low: mulig ved minuttoppløsning, men K-03 krever én desimal. Visningen sier nå at tallene er avrundet. |
| B3: Viste avrundede kategorier summerer ikke alltid til vist poengsum | Low: separat avrunding gir dette; avrundingsmerknaden forklarer hvorfor. Beregningen forblir uavrundet. |
| B4: Test av like kandidater og gjentakelse mangler | Medium: eksplisitt storykrav; målrettet domenetest tilføyes. |
| B5: Klippetesten kontrollerer bare sum | Medium: feil kategori ved grensen kan skjules; forventede kategorier og poeng testes. |
| B6: Standardtaket 300 og over 300 er ikke prøvd direkte | Medium: eksplisitt storykrav; test med faktiske poengverdier tilføyes. |
| B7: Ingen test viser at utelukkede ikke beregnes | Medium: observerte kall testes på vurderingsnivå. |
| B8: Spesifikasjonens testpåstander mangler konkret resultat | Medium: verifikasjonsseksjonen oppdateres etter faktisk kjøring. |
| B9: KI-loggen har plassholdere | Medium: loggen fullføres etter test og gjennomgang. |
| E1: Start mindre enn 672 timer etter datetimes minimum | Low: domenet mangler generell støtte for slike ekstreme datoer; eksisterende hvilevinduer har lignende begrensning. Ingen kjent praktisk dato i turnusen påvirkes; ekstra håndtering avvises som uforholdsmessig. |
| E2: Historikk i siste time av år 9999 | False: historikk klippes før vaktstart, og en gyldig vurdert vakt må ha slutt etter start; slik historikk kan ikke nå den aktuelle løkken. |
| E3: Tak er et enormt heltall | Low: et kunstig tall utenfor flyttallsområdet kan gi OverflowError. Standardtaket og praktisk parameterbruk berøres ikke; ekstra håndtering er ikke nødvendig for storyen. |

## Verification

**Commands:**
- 2026-11-15: `backend/.venv/Scripts/python -m pytest -q` – 438 bestått.
- 2026-11-15: `npm.cmd run build` og `npm.cmd run test` fra `frontend/` – bygg bestått, 49 Node-tester og 15 komponenttester bestått. Vitest varslet om fremtidig endring i Vites config-loader.
- 2026-11-15, etter at `main` med story 4.1 og 3.2 var slått inn: `backend/.venv/bin/python -m pytest -q` – 468 bestått. `npm run build` og `npm run test` fra `frontend/` – bygg bestått, 50 Node-tester og 26 komponenttester bestått. Testen «hver rad viser timer i uka» fra 4.1 måtte få `ulempebelastning`, fordi typen krever feltet.

**Manuell kontroll (Ragnhild Sætren, 2026-11-15):** ekte backend med testdata, vakt #4127 og #4189. Ulempeblokken står etter timekolonnen. Ved smale vinduer klippes ingenting, og siden rulles ikke vannrett. Godkjenningsflaten er uendret (den viser bare navn og nivå; nøkkeltallene hører til story 4.5), og #4189 viser fortsatt «Ingen gyldige kandidater». Skjermleser er ikke kontrollert for ulempeblokken.
