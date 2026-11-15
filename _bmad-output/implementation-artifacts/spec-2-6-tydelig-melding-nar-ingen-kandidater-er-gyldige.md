---
title: 'Story 2.6: Tydelig melding når ingen kandidater er gyldige'
type: 'feature'
created: '2026-11-15'
status: 'done'
baseline_commit: 'd53be97f98118fc3bf47234f805f0e615e986891'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når alle Kandidater er utelukket (#4189), viser flaten bare en nøytral `meta`-linje (story 2.4, beslutning B), og API-et svarer `status: "ok"` med tom liste. Turnusansvarlig kan ta det for en feil eller treg lasting (FR6).

**Approach:** API-et svarer 200 med `status: "ingen_gyldige_kandidater"`, en tom `kandidater`-liste og utelukkelsesoppsummeringen. Flaten viser en egen tomtilstand (UX-DR16, P-11) med Ekskludert-boksen under, visuelt og tekstlig ulik lasting, feil og datafeil.

## Boundaries & Constraints

**Always:**
- Svaret ved null Gyldige er `{status: "ingen_gyldige_kandidater", kandidater: [], utelukkelser}`, HTTP 200 (AD-4). `kandidater` er alltid med i svar fra en fullført vurdering (`ok` og `ingen_gyldige_kandidater`); bare `datafeil` har ingen liste, fordi ingen Kandidat er vurdert (story 2.1). Invarianter: `ok` har alltid minst én Kandidat, og `ingen_gyldige_kandidater` har alltid tom liste. Datafeil blir aldri «ingen gyldige».
- Tomtilstanden har sirkulært «!»-ikon (`.alert-icon`, `danger`-toner, `aria-hidden`) og teksten «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» Under den står Ekskludert-boksen (uendret fra 2.5, vist når `totalt > 0`), og under den «Innleie av personell kan vurderes» som ren tekst, uten knapp eller lenke (P-11).
- Kandidatflatens fire tilstander er tydelig ulike, uten nye farger (`warn` og `danger` har faste betydninger i DESIGN.md): **laster** har `role="status"`, `.meta`-tekst, ikon og knapp mangler; **feil** har `role="alert"` og «Prøv igjen»-knapp, uten ikon; **datafeil** har `role="alert"`, nøytral venstrekant (`.datafeil`) og datagrense, uten knapp og ikon; **ingen gyldige** har `role="status"`, «!»-ikon, Ekskludert-boks og innleietekst. Hver har egen modifikatorklasse på panelet. En komponenttest rendrer alle fire og sjekker at ingen to har lik tekst, lik panelklasse eller lik kombinasjon av rolle, ikon og knapp.
- `danger` bare på ikonet; panelkanten følger ellers vanlig panel. Bare designtokens (AV-13). Teksten uten utropstegn, og antyder aldri at systemet har valgt noe.
- Fasiten tilpasses aldri koden (AV-07): #4127 er uendret (4 gyldige, `ok`), #4189 gir `ingen_gyldige_kandidater` med 24 utelukket (3/2/18/1).

**Never:** Endre regler, hvem som er Gyldig, rangering, KI, skjema eller testdata. Innleieknapp eller innleiefunksjon. Å vise grunnene bak datafeil. Å la `ingen_gyldige_kandidater` nå Godkjenning (`/godkjenning`-endepunktet er uendret og gir fortsatt 404 for utelukkede).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| #4189 | seed, 0 gyldige | 200 `ingen_gyldige_kandidater`; tomtilstand med ikon, tekst, boks «24 utelukket …» og innleietekst | — |
| #4127 | seed, 4 gyldige | uendret: `ok`, liste, boks | — |
| Datafeil | #4261-lignende grunnlag | `datafeil`, egen tekst, ingen innleietekst | — |
| `ok` med tom liste | kontraktsbrudd | frontend viser feiltilstand med `RESERVETEKST`, aldri en tom liste (samme regel som ukjent status) | — |
| Ukjent status | ny status fra API | feiltilstand (som i dag) | — |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py` — ny `IngenGyldigeUt(status: Literal["ingen_gyldige_kandidater"], kandidater: list[KandidatUt], utelukkelser: UtelukkelsesOppsummeringUt)` med `kandidater=[]`. `kandidater()` (l.268): etter oppsummeringen, `if not vurdering.gyldige: return IngenGyldigeUt(...)`. `response_model=KandidaterUt | IngenGyldigeUt | DatafeilUt`. Oppdater docstring på `KandidaterUt`. Ikke endre godkjenningsendepunktet.
- `backend/tester/api/test_kandidater.py` — modulens docstring og tester som leser `svar["kandidater"]` for 4189 (l.43 `test_gyldige_stemmer_med_fasiten`, l.81–140): 4189 gir nå `status == "ingen_gyldige_kandidater"`, `kandidater == []` og nøklene `{"status","kandidater","utelukkelser"}`, så NFR2-testene (ingen utelukket i listen, ingen lekkasje) kjører uendret for begge vakter. Test av `test_4189_gir_tom_liste_med_status_ok_til_story_2_6` (l.107) skrives om til ny status og fasit. Legg til: datafeil gir fortsatt `datafeil` uten `kandidater`, og invariantene `ok` ⇒ ikke tom og `ingen_gyldige_kandidater` ⇒ tom for begge vakter.
- `frontend/src/api.ts` — `Kandidatsvar` får variant `{ status: "ingen_gyldige_kandidater"; kandidater: Kandidat[]; utelukkelser: UtelukkelsesOppsummering }`.
- `frontend/src/kandidater.ts` — `Kandidattilstand` får `{ type: "ingen_gyldige"; utelukkelser }`. `tilstandFraSvar`: ny status → `ingen_gyldige`; `ok` med tom liste → `{type:"feil", tekst: RESERVETEKST}`, i tråd med den eksisterende regelen om at ukjent status vises som feil, aldri som tom liste (AD-4: frontend styrer av `status`, og `ok` skal aldri gi en tom liste, FR6).
- `frontend/src/komponenter/Kandidatflate.tsx` — i `Kandidatliste` erstattes grenen `kandidater.length === 0` (l.143) av `tilstand.type === "ingen_gyldige"`: panel med klasse `kandidater tomtilstand`, ikon, tekst, `EkskludertBoks`, innleietekst. Gjenbruk `.alert-icon` og mønsteret fra `Vaktvalg.tsx:122`.
- `frontend/src/tekster.ts` — `kandidatflate.ingenGyldige` får den fulle teksten (UX-DR16); ny `innleie: "Innleie av personell kan vurderes"`. Fjern kommentaren «Story 2.6 erstatter den».
- `frontend/src/stil/app.css` — `.tomtilstand` (flex med ikon og tekst, tokens). Ikke bruk `.datafeil`-stilen. Modifikatorklassene `kandidater-laster` og `kandidater-feil` settes på de to eksisterende panelene i `Kandidatflate.tsx` (l.117, l.123) uten ny styling.
- `frontend/tester/komponenter/hjelpere.ts` — `INGEN_GYLDIGE` blir `{status: "ingen_gyldige_kandidater", kandidater: [], utelukkelser: …}` med 4189-tallene; ny `OK_MED_TOM_LISTE` for kontraktsbruddet.
- `frontend/tester/komponenter/kandidatflate.test.tsx` — testen «tom liste» fra 2.4 oppdateres til tomtilstanden. Nye: tomtilstanden viser full tekst, ikon, boks og innleietekst, og ingen knapper utenom «Vis full liste»; fire-tilstander-testen etter «Always»-punktet; `ok` med tom liste gir feiltilstand med `RESERVETEKST` og «Prøv igjen». Ekskludert-boksens skjuling ved 0 utelukkede er allerede dekket av testen fra 2.5 og gjentas ikke.
- `frontend/tester/kandidater.test.mjs` — `tilstandFraSvar` for ny status. Testen «tom liste fra API-et blir klar med tom liste» (l.127) hevder det motsatte av ny kontrakt og skrives om til `ok`+tom → `feil`. Tekstsammenligningen (l.111) tas med den nye `ingenGyldige`-teksten, og kontrollen `flate.includes("t.ingenGyldige")` (l.123) beholdes.
- Dokumentasjon: `README.md` (l.185), `docs/testing.md` (tabell, 2.6), `docs/emne/vurderingsmatrise.md`, `epic-2-context.md`, `docs/ki-logg/2026-11-15-ingen-gyldige-kandidater.md`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py` + `backend/tester/api/test_kandidater.py` — ny status og tester (FR6, AD-4).
- [x] `frontend/src/api.ts`, `kandidater.ts`, `tekster.ts` — typer, tilstand, tekster.
- [x] `frontend/src/komponenter/Kandidatflate.tsx`, `stil/app.css` — tomtilstanden.
- [x] `frontend/tester/**` — komponent- og enhetstester inkl. fire-tilstander-testen.
- [x] Dokumentasjon og KI-logg (se Code Map).

**Acceptance Criteria:**
- Given #4189, when kandidatflaten lastes, then API-et svarer 200 `ingen_gyldige_kandidater`, og flaten viser ikon, full tekst, boks med 24 utelukket og «Innleie av personell kan vurderes» uten knapp.
- Given lasting, feil, datafeil og ingen gyldige, when de vises, then ingen to har lik tekst eller klasse.
- Given hele testpakken, when `pytest`, `npm run build` og `npm run test` kjøres, then alt består.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Gjennomgang 1 (Blind Hunter, Edge Case Hunter, Verification Gap). Ingen funn ble patch, bad_spec eller intent_gap.

| Funn | Verdikt | Begrunnelse |
|---|---|---|
| BH: «lastefeil»/«regelmotoren» er utviklerspråk | false | Teksten er ordrett UX-DR16/P-11 og frosset i spesifikasjonen |
| BH: `role="status"` er lik for laster og ingen gyldige | false | Spesifikasjonen krever det; tilstandene skilles på ikon, knapp, tekst og klasse, og fire-tilstander-testen sjekker kombinasjonen |
| BH: `IngenGyldigeUt` dupliserer `KandidaterUt`, `kandidater` ikke `never[]` | low, avvist | Ingen konkret skade; fiks krever ny validering/typer utover direkte korreksjon. Backend kan ikke gi annet enn tom liste |
| BH: manglende exhaustiveness-sjekk i `tilstandFraSvar` | low, avvist | Eksisterende mønster; ukjent status gir allerede feil |
| BH: invariant-test grener på svaret; lasting-mock dobbel; fixture `totalt` 24 mot 2 rader; magisk dato | low, avvist | Testhygiene uten påvist feil; invariantene dekkes også av de strengere testene |
| BH: Innleie uten handling | false | P-11 sier ren tekst uten knapp eller lenke |
| BH: ingen flex-shrink/smal skjerm | low, avvist | Dekkes av manuell kontroll (AV-17) i Verification |
| BH: dokumentasjon/commit-begrunnelse ikke i diffen | false | Dokumentasjon og KI-logg er endret; commit-begrunnelsen skrives ved commit |
| BH: brudd på API-kontrakt, godkjenning | false | Godkjenningsendepunktet er uendret; frontendens `godkjenning.ts` bruker eget svar |
| EC: `ingen_gyldige_kandidater` med ikke-tom liste skjules stille | low, avvist | Backend kan ikke produsere det; ekstra gren uten påvist vei dit |
| EC: null gyldige og `totalt` 0 gir melding uten boks | false | Spesifikasjonen sier uttrykkelig at boksen bare vises ved `totalt > 0` |
| EC: fixture inkonsistent, dobbel mock, cleanup uten finally, klassetest sjekker bare ulikhet | low, avvist | Samme som over: testhygiene uten påvist skade |
| VG: ingen hull | — | Ingen funn |

## Design Notes

- Tomtilstanden er eget svar, ikke `ok` med tom liste, slik at frontend aldri må gjette på tom liste (laster/feil/tom). `ok`+tom behandles som kontraktsbrudd.
- `ok` med tom liste kan ikke oppstå fra backend etter denne storyen. Frontendregelen beskytter FR6 mot en senere regresjon i backend, og er dekket av én ren test i `kandidater.test.mjs` pluss én komponenttest. Feiltilstand er valgt framfor å vise tomtilstanden, slik at et brutt API ikke forkledes som et regelmotorresultat.
- Ikonet er dekorativt (`aria-hidden`); teksten bærer meningen og har `role="status"`.

## Verification

**Commands:**
- `backend/`: `.venv/bin/python -m pytest` -- expected: alt består, også import-linter
- `frontend/`: `npm run build` og `npm run test` -- expected: begge består

**Manual checks (docs/testing.md, OP-16):**
- Ekte backend: #4189 viser tomtilstanden, #4127 uendret. Layout ved smale datamaskinvinduer (AV-17, ca. 800 og 1024 px), farger (ikon i `danger`), fokus på «Vis full liste» med tastatur.

**Manuell kontroll (docs/testing.md):** Ragnhild, 2026-11-15, macOS, story 2.6. Nettleser og versjon er ikke notert.
1. Layout: bestått ved 1024×800 px. Andre bredder (1080, 960, 680, 1600) er ikke kontrollert.
2. Tastatur og fokus: meldt som forventet resultat; ikke notert separat.
3. Farger (ikon i `danger`): meldt som forventet resultat; ikke notert separat.
4. Større skrift: ikke kontrollert.
5. Ekte backend: bestått. #4189 viser tomtilstanden og #4127 er uendret, etter innlogging gjennom Vite-proxyen.
Målrettet kontroll: med backend stoppet viste flaten «Får ikke kontakt med serveren» med «Prøv igjen» og uten «!»-ikon, og flaten kom tilbake etter at backend var startet igjen.
