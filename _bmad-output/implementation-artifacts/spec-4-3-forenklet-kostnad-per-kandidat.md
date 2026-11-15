---
title: 'Story 4.3: Forenklet kostnad per kandidat'
type: 'feature'
created: '2026-11-15'
status: 'done'
baseline_commit: 'a677020d14eb8b3dfe3b0343c7c041a67470d502'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Turnusansvarlig ser ikke modellert merkostnad for gyldige kandidater. Uten den mangler grunnlaget for sammenligning og senere rangering (FR7, P-01–P-03).

**Approach:** Beregn deterministisk kostnadsforskjellen ved å tildele vakten og vis total og ordinær/overtidsfordeling for hver gyldig kandidat.

## Boundaries & Constraints

**Always:** Individuell timelønn; 36 timer per kalenderuke i Europe/Oslo til ordinær sats, deretter 150 %. Faktisk forløpt tid i UTC og halvåpne intervaller. Beregn hver berørt uke separat og summer uten tidlig avrunding; trekk ikke fra opprinnelig ansatt. Vis to desimaler og timer × satser. Eksisterende overlapp telles som union. Ugyldig lønn eller utilstrekkelig grunnlag gir datafeil (P-08), ikke rangering eller godkjenning. Kostnaden må inngå i konsistent godkjenningsgrunnlag (P-09).

**Never:** Ingen KI, tarifftillegg, lagret overtidssats, rangering eller endring av harde regler. Ingen én sats som fremstilles som gjeldende for en blandet vakt.

## I/O & Edge-Case Matrix

| Scenario | Input | Forventet |
|---|---|---|
| Blandet | 32 + 8 t, 300 kr/t | 4 t ordinær + 4 t overtid, 3 000 kr |
| Overtid | 40 + 8 t, 300 kr/t | 8 t overtid, 3 600 kr |
| Grense | 28 + 8 t | Ingen overtid |
| Ukeskifte | søndag 23–mandag 07, 36/20 t før, 300 kr/t | 1 t overtid + 7 t ordinær, 2 550 kr |
| Sommertid | vår- og høstskifte | Faktisk tid, henholdsvis 7 og 9 timer for natt 23–07 |
| Manglende eller ugyldig lønn | grunnlag kan ikke beregnes | datafeil, ingen kandidater |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/timer_i_uka.py` summerer unionsoverlapp; `trettifem_timer.py` leverer Oslo-ukegrenser og valideringsvindu. Gjenbruk, også for andre berørte uker.
- `backend/domene/typer.py` og `backend/adaptere/lagring/kandidatgrunnlag.py`: overfør individuell `AnsattRad.timelønn`; `vurdering.py` stopper ugyldig grunnlag før beregning. `grunnlagsmerke` dekker ansattkolonnene.
- `backend/adaptere/api/main.py`: `KandidatUt` bygges i kandidatrute og godkjenningsgrunnlag; samme kostnadsdata begge steder.
- `frontend/src/api.ts`, `komponenter/Kandidatflate.tsx`, `format.ts`, `tekster.ts` og `stil/`: kandidatlisten viser verdier med tokens. 4.2 utvikles samtidig i flere av de samme filene.
- `backend/tester/regelmotor/`, `backend/tester/api/` og `frontend/tester/` dekker domene, API og radvis visning.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/` og `backend/adaptere/lagring/kandidatgrunnlag.py` — implementer ren beregning og valider lønn og datadekning; test alle matriserader, brøktimer, overlapp og determinisme.
- [x] `backend/adaptere/api/main.py` og API-tester — lever identiske kostnadsdata i begge kandidatsvar; test datafeil og fasit #4127.
- [x] `frontend/src/` og `frontend/tester/` — vis total, status og separate timer × satser på riktig kandidat, og test ordinær, blandet og overtid (P-03, OP-16).
- [x] `docs/ki-logg/`, `docs/testing.md`, `docs/emne/vurderingsmatrise.md` — dokumenter faktisk arbeid og kontroll.

**Acceptance Criteria:**
- Given gyldige kandidater, when listen vises, then har hver kandidat korrekt beregnet kostnad med to desimaler og forståelig ordinær/overtidsfordeling.
- Given ugyldig beregningsgrunnlag, when vurderingen kjøres, then returneres datafeil uten kandidatvalg eller godkjenning.
- Given en vakt over ukeskifte eller sommertid, when kostnaden beregnes, then fordeles faktisk tid på riktige uker og hver ukes 36-timersgrense anvendes.

## Implementation Notes

Kostnadsvisning ble også lagt på godkjenningsflaten slik at P-09s nye bekreftelse viser oppdatert grunnlag. Varighet vises i timer:minutter med «ca.» når sekunder avrundes. 493 backendtester, frontendbygg, 50 modultester og 29 komponenttester bestod. En mutasjon som fjernet overtidsstatus ga feil i komponenttesten; etter tilbakeføring bestod 13 tester.

## Spec Change Log

- 2026-11-15, PR-gjennomgang (Johannes): integrert med story 4.2 etter merge av PR #27. «Inkluderer overtid» bruker nå `Varselmerke` fra 4.2, slik at høy belastning og overtid vises som to like, synlige varsler (Kims krav ved integreringen). Etiketten «Overtid» i detaljlinjen er flyttet til `tekster.ts`. Intensjonen er uendret.

## Review Triage Log

| Funn | Verdikt og bevis | Tiltak |
|---|---|---|
| Endret kostnad manglet på godkjenningsflaten | medium: P-09 kan gi nytt grunnlag uten synlig kostnad | Rettet og komponenttestet |
| Store lønnstall kunne gi ugyldig JSON | medium: lønnsvalideringen tillot vilkårlige desimaltall | Rettet til positivt SQLite-heltall med tester |
| Lønn med tekst eller desimal ble godtatt | medium: lagringskontrakten er heltall | Rettet og testet |
| Avrundede timer kunne gi misvisende regnestykke | medium: ett minutt ble vist som 0,02 timer | Timer:minutter, «ca.» ved sekunder; testet |
| Datafeilmeldingen forklarer ikke lønnsfeil | low: generisk melding angir ikke årsak | Lukket i PR-gjennomgangen (Johannes): årsaken logges i backend (`Datafeil for vakt …: ansatt …: ugyldig timelønn`), og meldingen i brukerflaten er fast per kode (AD-4) |
| POST etter ugyldiggjort lønn manglet egen test | low: grunnlagsmerket dekker ansattkolonner og P-09 har POST-tester | Rettet i PR-gjennomgangen: `test_endret_lønn_krever_nytt_trykk_og_gir_ny_kostnad`, med negativ kontroll |
| Sommertidstest uten eksisterende timer | medium: viste ikke overtidsfordeling | Begge skifter over grensen testet |
| API-test manglet full blandet fordeling | medium: totale beløp og like svar beviser ikke fordelingen | Ingrid-fasit utvidet |
| Status for overtid var ikke testet | medium: feil etikett kunne vises | Testet per rad |


## Verification

**Commands:** Backend `.venv\Scripts\python -m pytest`; frontend `npm.cmd run build` og `npm.cmd run test` sekvensielt. Testene skal bestå.

**Manuell kontroll:** Ved manglende automatisert dekning kontroller layout ved 680, 960, 1080 og 1600 px, farger, fokus, større skrift og ekte backend (AV-17, OP-16). Dokumenter faktiske resultater.

**Manuell kontroll (docs/testing.md):** Codex, 2026-11-15, Playwright Chromium på Windows, ekte backend med isolerte testdata. #4127 ble visuelt kontrollert ved 680, 960, 1080 og 1600 px uten synlig klipping eller overlapping. Ingrid viste 3 850,00 kr og 4:00 ordinær + 4:00 overtid også på godkjenningsflaten; #4189 viste null gyldige. Farger samsvarer visuelt med statusene. Tastatur/fokus, større skrift og faktisk skjermleser er ikke kontrollert.
