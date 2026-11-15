---
title: 'Story 4.1: Timer i perioden per kandidat'
type: 'feature'
created: '2026-11-15'
status: 'done'
baseline_commit: '1e620d32153af6ea93b346ab5a8cd55660d6240a'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatlisten viser ikke hvor mye hver Gyldig kandidat allerede er satt opp på i uken Vakten starter i (FR8, P-02). Uten tallet ser ikke turnusansvarlig hvem som allerede har mye å gjøre, og 4.2 (belastningslinje med terskel 32,4 t) har ikke noe å bygge på.

**Approach:** En ren domenefunksjon summerer faktisk overlapp mellom Kandidatens egne Vakter og kalenderuka Vakten starter i (mandag 00:00 til mandag 00:00, `Europe/Oslo`), uten Vakten som skal bemannes. Tallet sendes med hver Kandidat i kandidatsvaret og vises i kandidatlisten.

## Decisions (Ragnhild 2026-11-15)

1. **Format:** t:mm («32:00», «32:23»). Backend sender `minutter_i_uka` som heltall (hele minutter, avrundet ned); frontend formaterer i `format.ts`. Domenefunksjonen returnerer `timedelta`.
2. **Plassering:** eget felt `minutter_i_uka` på `KandidatUt`, satt i både kandidatruten og godkjenningsgrunnlaget. `RangertKandidat` lages ikke i 4.1; 4.4 flytter tallet dit som Timebelastning.
3. **Struktur:** behold `<ul>`-listen. Hver rad får en kolonnelignende verdi med tabelltall og fast bredde. Verdien skal fungere ved ulike skjermbredder uten overlapping eller avkuttet innhold (AV-17). Avviket fra ordet «kolonne» i AC-en er bevisst.
4. **Sommertid og vintertid** beholdes i tråd med P-02 og epics: uker er mandag 00:00–mandag 00:00 i `Europe/Oslo`, tid regnes faktisk forløpt i UTC, og begge sommertidsskiftene testes.

## Boundaries & Constraints

**Always:** Gjenbruk `berørte_uker` fra `domene/regelmotor/trettifem_timer.py` for ukegrensene; ingen ny tidssonelogikk. Faktisk forløpt tid i UTC (uka har 167 eller 169 t ved sommertidsskifte). Halvåpne intervaller: en Vakt som slutter nøyaktig mandag 00:00 gir 0 t i neste uke. Ingen Vakter i uka gir 0, ikke tom. Domenet er ren Python uten KI (NFR1, AD-1, AD-2).

**Never:** Ingen terskel, farge eller belastningslinje (4.2). Ingen kostnad (4.3), rangering (4.4) eller ulempe (4.7). Ikke vis timer for utelukkede. Ikke endre regelmotorens vurdering av hvem som er gyldig. Ikke lagre tallet.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ingrid i #4127 | Startuke 21.–28.09.2026, fasit 32 t | 32:00 | N/A |
| Ingen vakter i uka | Kandidat uten andre Vakter | 0:00 | N/A |
| Nattevakt over ukeskifte, startuka er uka etter | Kandidatens natt søndag 23:00–mandag 07:00, Vakten starter mandag eller senere i uka | 7 t (bare delen etter mandag 00:00) | N/A |
| Nattevakt over ukeskifte, startuka er uka før | Samme natt, Vakten starter tidligere i uka | 1 t (bare delen før mandag 00:00) | N/A |
| Slutter nøyaktig mandag 00:00 | Vakt rett før startuka | 0 t | N/A |
| Sommertid vår og høst | Natt lørdag 23:00–søndag 07:00 i skiftehelgen | 7 t (mars) og 9 t (oktober) | N/A |
| Vakt i neste uke | Vakt etter ukeslutt | Telles ikke | N/A |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/trettifem_timer.py` -- `berørte_uker`, `_mandag_i_uka`, `_mandag_kl_null`, `lengste_fri`: ukegrenser i Oslo-tid som UTC. Gjenbrukes, endres ikke.
- `backend/domene/typer.py` -- `Kandidat.vakter: tuple[Tidsrom, ...]` er alle tildelte Vakter uavhengig av periode; `Vakten` som bemannes er aldri med (`kandidatgrunnlag.py`).
- `backend/domene/regelmotor/` -- ny modul `timer_i_uka.py` med funksjon på Kandidat og Vakt. Faller inn under import-linter-kontrakten.
- `backend/adaptere/api/main.py` -- `KandidatUt` (linje ~122) og de to stedene den bygges: kandidatruten (~303) og `godkjenningsgrunnlag` (~334). Hold endringen til felt og to linjer (3.2 pågår).
- `frontend/src/api.ts` -- `Kandidat`-typen (linje ~49) får feltet.
- `frontend/src/format.ts` -- ny ren funksjon for t:mm.
- `frontend/src/komponenter/Kandidatflate.tsx` -- `<li>` i `Kandidatliste` (~161). Hold endringen liten (3.2 pågår).
- `frontend/src/tekster.ts`, `frontend/src/stil/app.css` -- tekst og stil for verdien. Rå størrelser bare i `tokens.css` (AV-13).
- `backend/tester/regelmotor/test_35_timersregelen.py` -- mønster for grensetester på uke og sommertid.
- `frontend/tester/komponenter/kandidatflate.test.tsx`, `frontend/tester/format.test.mjs` -- mønster for komponent- og formattester.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/domene/regelmotor/timer_i_uka.py` -- funksjon som summerer overlapp med startuka (union av vaktene, som i 2.4) -- FR8, P-02
- [ ] `backend/tester/regelmotor/test_timer_i_uka.py` -- alle rader i I/O-matrisen, Ingrid 32:00 og gjentatt kjøring gir samme resultat -- grensetester er beviset (AGENTS.md)
- [ ] `backend/adaptere/api/main.py` -- felt `minutter_i_uka` på `KandidatUt`, satt i begge kallstedene -- liten endring
- [ ] `backend/tester/api/` -- test at kandidatsvaret for #4127 gir Ingrid 1920 minutter og at godkjenningsgrunnlaget har feltet
- [ ] `frontend/src/` -- `api.ts`-type, `format.ts`-funksjon og verdi i `Kandidatflate.tsx` etter beslutningene over
- [ ] `frontend/tester/` -- formattest (0:00, 32:23, 32:24, over 40 t) og komponenttest som viser 0:00 for kandidat uten vakter

**Acceptance Criteria:**
- Given kandidatlisten for #4127, when den vises, then hver Gyldig kandidat har timer i startuka uten Vakten som bemannes, og Ingrid viser 32:00.
- Given en Vakt som begynte forrige søndag eller krysser sommertid, when timene beregnes, then summen er faktisk overlapp med startuka.
- Given en Kandidat uten andre Vakter i uka, when timene vises, then verdien er 0:00, ikke tom.
- Given kandidatflaten i smale og brede nettleservinduer, when raden vises, then navn, nivåtag, timer og «Velg» ligger uten overlapping og uten avkuttet tekst (brytes til neste linje ved behov).

## Implementation Notes

## Spec Change Log

## Review Triage Log

| Funn | Lag | Verdikt | Rute | Bevis |
|---|---|---|---|---|
| Formattesten for `timerOgMinutter` lå i New York-grenen med ødelagt innrykk | Blind, Edge, Gap | medium | patch | Testen kjørte bare i underprosessen; flyttet ut av `if`. Rettet. |
| Komma inne i kommentaren i `test_godkjenningsgrunnlag.py` | Blind, Gap | low | patch | Dict brutt over flere linjer. Rettet. |
| Testnavn `…bare_id_navn_og_nivå` stemte ikke med fire felt | Blind | low | patch | Omdøpt til `…bare_kontraktsfeltene`. |
| Docstring for `timerOgMinutter` motsa koden | Blind | low | patch | Docstring rettet; tester for brøk, negativ og NaN lagt til. |
| Mangler test når Vakten selv starter søndag natt / mandag 00:00 | Blind | medium | patch | Begge tester lagt til i `test_timer_i_uka.py`. |
| Avrunding til hele minutter utestet | Blind | low | patch | Test for 59 sekunder og 0 lagt til. |
| Vakten som bemannes er ikke eksplisitt ekskludert | Edge | false | – | `kandidatgrunnlag.py` tar aldri med Vakten (Code Map); spec-beslutning 2. |
| Manglende/ugyldig `minutter_i_uka` vises som 0:00 | Edge | false | – | Backend sender alltid heltall (Pydantic `int`); ingen vei til undefined. |
| Ugyldige vakter og startuke utenfor datagrensen undertelles stille | Blind | false | avklart | Rettet etter første triage: 35-timersregelens vindu er hele startuka, og `vurder_kandidater` gir `Datafeil` for ugyldige vakter og for vindu utenfor `[historikkstart, datagrense]` før `minutter_i_uka` beregnes. Docstringen sier nå at kalleren må ha vurdert grunnlaget. Se deferred-work (AVKLART). |
| Layout uten test ved smale vinduer | Edge | maybe-false | – | Dekkes av «Manual checks» (AV-17); ikke utført ennå. |
| Duplisert klipping mot `lengste_fri` | Blind | low | avvist | Refaktorering av regelmotoren, ikke direkte retting. |
| «t i uka»-tekst, aria, token-plassering, `overflow-wrap` | Blind | low | avvist | Tekstvalget er Ragnhilds beslutning 3; resten er smak uten navngitt skade. |
| Feltet brukes ikke i godkjenningsflaten | Blind | false | – | Spec-beslutning 2 krever feltet der; 4.4 flytter tallet. |
| docs/testing.md, KI-logg, AGENTS.md-status mangler | Blind | medium | oppfølging | Prosesskrav, ikke kode; gjøres ved avslutning (se presentasjon). |

## Design Notes

En nattevakt søndag 23:00 til mandag 07:00 deles på ukeskiftet: 1 t i uka som slutter og 7 t i neste. Hvilken del som telles, avgjøres av hvilken uke Vakten som bemannes starter i, ikke av Kandidatens vakt. Sommertidsskiftet er søndag kl. 02/03, så natten lørdag 23:00–søndag 07:00 ligger helt i én uke og varer 7 t i mars og 9 t i oktober. Uka med skiftet har 167 eller 169 t (se `test_35_timersregelen.py`), men det påvirker bare summen, ikke ukegrensene. Bare Kandidatens eksisterende vakter telles; den vurderte Vakten fordeles først i 4.3 (P-02).

## Verification

**Commands:**
- `cd backend && .venv/bin/python -m pytest` -- expected: alle tester består
- `cd frontend && npm run build && npm run test` -- expected: bygg og tester består (én kjøring om gangen, se AGENTS.md)

**Manual checks (if no CLI):**
- Layout ved flere vindusbredder, også smale (AV-17), med lange navn og verdier som 40:00, tastaturfokus på «Velg» og at verdien leses riktig av skjermleser. Ekte backend: #4127 viser Ingrid 32:00, #4189 er uendret (OP-16).

**Manuell kontroll (docs/testing.md):** Ragnhild, 2026-11-15, Safari 26.6.2 (21624.5.1.11.3) på macOS, story 4.1, ekte backend med testdata i egen database
1. 1080, 960, 680 og 1600 px: bestått (oppgitt samlet: «alle funksjoner fungerte som forventet»)
2. Tastatur og fokus: bestått. «Velg» med Enter på Ingrid Dahl for #4127 godkjente og bemannet vakten
3. Farger: bestått
4. Større skrift: bestått, men først etter at testdataene ble tilbakestilt (vakten var bemannet av punkt 2)
5. Ekte backend: bestått. #4127 viser Ingrid med 32:00, vakten var ubemannet etter tilbakestilling
Målrettet kontroll av flyt uten komponenttest: ikke relevant
Skjermleser (valgfri): observasjon, ikke avvik mot akseptkriteriene. «32:00 t i uka» ble lest som «32 uka», altså uten «t» og uten minuttene. Ikke utbedret i 4.1 etter Ragnhilds valg; se issues.md.
Merknad: resultatene per punkt er oppgitt samlet av Ragnhild, ikke avkrysset enkeltvis.
