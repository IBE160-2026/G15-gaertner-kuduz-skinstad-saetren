---
title: 'Story 3.1: Velge kandidat og se godkjenningsflaten'
type: 'feature'
created: '2026-11-12'
status: 'done'
baseline_commit: 'c7df2a31fafd9cf71083f1bd1e5c9faa4d610deb'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatlisten viser hvem som kan ta vakten, men turnusansvarlig kan ikke velge en av dem. Første steg i den to-stegs godkjenningen mangler (FR12, UX-DR17).

**Approach:** Hver gyldig kandidat i listen får en «Velg»-knapp som fører til en egen godkjenningsflate med egen URL. Flaten henter vakten og kandidaten fra et nytt lesende endepunkt, som bare svarer for Ansatte regelmotoren godkjenner. Flaten viser kandidatkort, bekreftelsesboks og statuslinje. Ingenting skrives før 3.2.

## Boundaries & Constraints

**Always:**
- Nytt endepunkt `GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id}` bak sesjonsvernet (AD-3). Det bygger på `hent_kandidatgrunnlag` og `vurder_kandidater` for hele grunnlaget og slår opp id-en i `gyldige`. Svaret er `{status:"ok", vakt:<VaktdetaljerUt>, kandidat:<KandidatUt>}` eller dagens `DatafeilUt` (200, P-08). Grunnlaget filtreres ikke ned til én Ansatt, fordi datafeilsjekken da endres.
- En Ansatt som er utelukket, er den som var satt opp, eller ikke finnes, gir samme 404 `ikke_funnet` i feilformen `{kode, melding}` (AD-4, NFR2). Svaret sier ikke om personen finnes eller hvilken regel som slår inn. Det gjelder også en bemannet eller ukjent vakt.
- Endepunktet er lesende. En test viser at hele `vakt`-tabellen er uendret etter vellykket svar, 404 og datafeil (FR12).
- Tester bruker Kandidater som er gyldige også etter 2.4: Jonas Bakke (id 6) og Mette Solberg (id 5) for #4127. Anders Strand (id 11) brukes ikke som gyldig. Testen for utelukkede er ikke bundet til en regel: alle id-er fra 1 til 25 som ikke finnes i `/kandidater`-svaret, gir 404, og alle som finnes der, gir 200 (OP-13).
- Brødsmulestien er `Turnus > <avdeling> > Vakt #<nr> > Kandidater > Godkjenning`, og det siste leddet er uthevet (UX-DR3).
- Kandidatkortet har navnet som overskrift og taggen `Nivå n/4`. Bekreftelsesboksen sier hvem som settes inn i hvilken Vakt (nummer, type, dato, tid). Den har «Avbryt» (`button-secondary`) og «Godkjenn erstatning» (`button-primary`), og statuslinjen «Ikke gjennomført — venter på eksplisitt godkjenning» (UX-DR19, UX-DR22).
- «Avbryt» går til `/vakt/<nr>/kandidater` uten kall. Begge knappene nås og aktiveres med tastatur (UX-DR24).
- Svar som kommer for sent for en tidligere URL, forkastes med sesjonsgenerasjonen som i `kandidater.ts` (P-09). Ved datafeil vises datafeilen og datagrensen, uten knapper for godkjenning.
- Endringene i `Kandidatflate.tsx` holdes små, fordi 2.4 endrer samme fil. Nye tekster legges i en ny blokk `TEKSTER.godkjenning`, ikke i `kandidatflate`.
- All tekst er på norsk og nøytral (UX-DR23), og stilen bruker bare designtokens (AV-13).

**Beslutninger (Johannes, 2026-11-12, OP-13):**
- **URL (1A):** Flaten ligger på `/vakt/<nr>/godkjenning/<ansatt_id>`. Begge tallene er positive heltall uten ledende null, som i `vaktnummerFraSti`. Andre former gir «Fant ikke siden» som i dag.
- **«Godkjenn erstatning» før 3.2 (2A):** Knappen er aktiv. Et trykk viser `meta`-linjen «Godkjenningen lagres ikke ennå. Ingenting er endret.», og statuslinjen står. Ingen kall til API-et. 3.2 bytter ut handleren.
- **Tekst ved 404 (3A):** Flaten viser «Kandidaten kan ikke velges for denne vakten.» med lenke tilbake til kandidatlisten. Teksten dekker utelukket og ukjent Ansatt og vakt som ikke lenger mangler bemanning, uten å si hvilken av dem det er.
- **Lengde:** Spesifikasjonen er på omtrent 2 900 tokens og beholdes hel, fordi den har ett mål.

**Never:** Ingen skriving, ingen tabell for Godkjenning, ingen POST-rute og ingen ny kontroll av reglene ved godkjenning (3.2). Ingen avviksnotat, kostnad, belastning eller rangering (Epic 4) og ingen KI (Epic 5). Ingen tekst om hvem som byttes ut, eller om at handlingen registreres med navn (3.2). Ingen endring i regelmotoren, skjemaet, testdataene eller `FASIT`. Utelukkede Ansatte og årsakene deres nevnes ikke i noe svar.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Gyldig kandidat | #4127, Jonas Bakke (6) | 200 `ok` med vakt og kandidat. Flaten viser kort, boks og statuslinje | — |
| Velg fra listen | klikk eller Enter på «Velg» hos Mette | `/vakt/4127/godkjenning/5`, godkjenningsflaten vises | — |
| Godkjenn i 3.1 | klikk eller Enter på «Godkjenn erstatning» | `meta`-linjen fra 2A vises, statuslinjen står, ingen kall | — |
| Utelukket | #4127, alle id-er utenfor `/kandidater` | ingen kandidatdata | 404 `ikke_funnet`, teksten fra 3A og lenke tilbake |
| Ukjent eller satt opp | id 999, Silje Amundsen (1) | ingen kandidatdata | 404 `ikke_funnet` |
| Vakt ikke ubemannet | #4128, #9999 | ingen data | 404 `ikke_funnet` |
| Datafeil | grunnlaget gir `Datafeil` | datafeiltekst og datagrense, ingen knapper for godkjenning | 200 `datafeil` |
| Sesjon | manglende eller utløpt | innloggingsflaten | 401 via det eksisterende vernet |
| Direkte URL eller tilbakeknapp | lim inn eller popstate | samme flate | — |
| Avbryt | klikk eller Enter | tilbake til kandidatflaten, DB uendret | — |
| Sent svar | URL byttes før svaret kommer | det gamle svaret vises ikke | — |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py`: `feil()` L48, sesjonsvern L171, `Okt` L161, `VaktdetaljerUt` L112, `KandidatUt`/`KandidaterUt` L121, `DatafeilUt` L135, vaktdetaljer L228, kandidatruten L235–253 (mønster for datafeil og logging). Legg den nye ruten ved siden av, gjenbruk modellene og bygg `vakt` slik vaktdetaljruten gjør.
- `backend/adaptere/lagring/kandidatgrunnlag.py`: `hent_kandidatgrunnlag` (L35) gir `None` for vakter som ikke er ubemannet. Ikke endre den.
- `backend/domene/regelmotor/vurdering.py`: `vurder_kandidater` (L191) fjerner `satt_opp_ansatt_id` selv. `kompetanse.kompetansenivå(k, vakt)` gir nivået. Ikke endre domenet.
- `backend/tester/api/test_kandidater.py`, fixturer fra `test_innlogging.py` (`klient`, `logg_inn`, `feilsvar`, `engine`). DB-snapshot: `select(VaktRad)` til tupler før og etter. Mønsteret `tell()` ligger i `tester/lagring/test_testdata.py` L285.
- `frontend/src/navigasjon.ts`: `vaktnummerFraSti` (L4) og `naviger` (L15). Legg til en parser for godkjenningsstien. `frontend/src/App.tsx` L90 og L138–144: velg-funksjon og ny gren.
- `frontend/src/komponenter/Kandidatflate.tsx`: `Kandidatliste` L89–147. Legg «Velg» i hver `<li>`, som en `button-secondary button-kompakt`, og send inn `onVelg`. Ellers ingen endring.
- `frontend/src/kandidater.ts`: tilstandsmaskin og vern mot sene svar. Lag `godkjenning.ts` etter samme mønster. `api.ts` L93 `kall`, L156 `hentVaktdetaljer`.
- `frontend/src/komponenter/Brodsmulesti.tsx` og `format.ts` (Oslo-tid, `vaktBrodsmule` L69) gjenbrukes. CSS: `app.css` `.button-primary` L168, `.button-secondary` L60, `.button-kompakt` L309, `.tag` L109.
- `frontend/tester/*.test.mjs`: bare rene funksjoner med `lastTs`. `kandidater.test.mjs` og `kandidater-bunt.ts` er mønsteret for falsk `fetch`.
- `README.md`: flyten L165–186 og API-rutene L183–197.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py`: `GodkjenningsgrunnlagUt` og `GET /api/vakter/{vaktnummer}/kandidater/{ansatt_id}`, med 404 og datafeil som beskrevet over.
- [x] `backend/tester/api/test_godkjenningsgrunnlag.py`: hele matrisen på API-siden, den regeluavhengige 404-testen, DB uendret, 401, `POST` gir 405 og ingen utelukket informasjon i svaret.
- [x] `frontend/src/navigasjon.ts`, `App.tsx`: parser for `/vakt/<nr>/godkjenning/<ansatt_id>`, `velgKandidat`, ruting og popstate.
- [x] `frontend/src/api.ts`, `godkjenning.ts`: type, kall og tilstand (laster, ikke funnet, feil, datafeil, klar) med vern mot sene svar.
- [x] `frontend/src/komponenter/Godkjenningsflate.tsx`: brødsmulesti, vaktlinje, kandidatkort, bekreftelsesboks, statuslinje og «Avbryt».
- [x] `frontend/src/komponenter/Kandidatflate.tsx`: «Velg» per rad.
- [x] `frontend/src/tekster.ts`, `stil/app.css`: blokken `TEKSTER.godkjenning` og stil bare med tokens.
- [x] `frontend/tester/godkjenning.test.mjs` (+ bunt): parser, tilstand fra svar og feil, sent svar forkastes, og tekstene for laster, feil, ikke funnet og datafeil er ulike.
- [x] `README.md`: flate og rute.

**Acceptance Criteria:**
- Given kandidatlisten for #4127, when jeg velger en hvilken som helst kandidat, then godkjenningsflaten for den kandidaten vises under riktig brødsmulesti, og databasen er uendret.
- Given godkjenningsflaten, when jeg bare bruker tastatur, then jeg når og aktiverer «Avbryt» og «Godkjenn erstatning».
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then består alt.

## Implementation Notes

- 2026-11-12: Endepunktet henter i tillegg `hent_vaktdetaljer` for `avdeling`. Datafeil besvares før oppslaget på id, så alle id-er får samme datafeilsvar. Nye hjelpere: `vaktlinje` og `datoOgTidsrom` i `format.ts`, og `kandidatsti`, `godkjenningssti` og `godkjenningFraSti` i `navigasjon.ts`. Brødsmulen for vakten er kort (`Vakt #4127`), som i UX-DR3.
- 2026-11-12: Testdekning av matrisen. Backend: 22 tester i `test_godkjenningsgrunnlag.py` for gyldig, utelukket (regeluavhengig for #4127 og #4189), ukjent eller satt opp, vakt som ikke er ubemannet, datafeil, 401, 405 og DB uendret. Frontend: 13 tester i `godkjenning.test.mjs` for ruteparseren, tilstandene, sene svar og tekstene. Radene «Velg fra listen», «Godkjenn i 3.1» og «Avbryt» kan bare delvis testes automatisk, fordi det ikke finnes en komponentrigg (kjent i `deferred-work.md`). Stien og tekstene er testet. Klikket og at det ikke skjer noe kall, er kontrollert i nettleseren av implementeringsagenten mot en egen testdatabase i scratchpad, og av Johannes 2026-11-12.
- 2026-11-12: Verifisert av hovedøkten: `pytest` 359 passed, `npm.cmd test` 39 av 39 og `npm.cmd run build` grønn.
- 2026-11-12: Etter kodegjennomgangen er 7 funn rettet, 2 utsatt til `deferred-work.md` og 10 avvist (se Review Triage Log). KI-loggen er [2026-11-12-godkjenningsflaten.md](../../docs/ki-logg/2026-11-12-godkjenningsflaten.md). 359 backendtester og 39 frontendtester består, og bygget går gjennom.
- 2026-11-12: Johannes gjorde nettleserkontrollen og godkjente den. Knappene oppførte seg som forventet.

## Spec Change Log

## Review Triage Log

Tre uavhengige gjennomganger 2026-11-12, alle på Opus og uten kjennskap til implementeringen: Blind Hunter (BH, 15 funn), Edge Case Hunter (EC, 4) og Verification Gap (VG, 1). EC4 er samme funn som BH8 og står i samme rad.

| # | Funn | Vurdering | Begrunnelse | Utfall |
|---|---|---|---|---|
| VG1 | Koblingen i komponentene («Velg», ruten, Godkjenn uten kall, ingen knapper ved datafeil, Avbryt) er bare kontrollert manuelt | medium | Ingen rendret test ville feilet ved feil id i `onVelg`, et ekstra `fetch` eller at datafeil faller gjennom. Det mangler en komponentrigg, og det er kjent fra før | defer |
| BH1 | Feiltilstanden har bare «Prøv igjen», ingen lenke tilbake og ingen brødsmulesti | low | Kandidatflaten har samme mønster (`Kandidatflate.tsx:62`, `:119`), og nettleserens tilbakeknapp virker. Rettingen legger til elementer for et sjeldent tilfelle | avvist |
| BH2 | «Avbryt» legger til et nytt historikkinnslag, så tilbakeknappen viser godkjenningen igjen | low | Det stemmer, men det er vanlig for lenker i nettlesere. `history.back()` ville sviktet ved direkte URL. Rettingen krever en ny gren | avvist |
| BH3 | Fokus flyttes ikke ved navigasjon | low | Knappene kan nås med tab fra toppen, så UX-DR24 er oppfylt. Ingen flate i appen flytter fokus ved navigasjon, og skjermleser er v2 (EXPERIENCE.md) | avvist |
| BH4 | Leddet «Kandidater» i brødsmulestien er ikke klikkbart | low | `Brodsmulesti.tsx` har aldri hatt lenker (story 1.6). EXPERIENCE.md bruker brødsmulestien som navigasjon, så funnet er reelt, men det skyldes ikke denne storyen | defer |
| BH5 | Lenken ved 404 kan føre til en ny 404 når vakten er bemannet | low | Det skjer bare ved en håndskrevet URL eller en gammel fane. En ekstra lenke til oversikten gjør flaten mer omfattende. Bør vurderes på nytt i 3.2, når vakter blir bemannet | avvist |
| BH6 | README-listen over testfiler mangler `godkjenning.test.mjs` | low | Bekreftet i `README.md:224` | patch |
| BH7 | Oslo-testen for `vaktlinje` og `datoOgTidsrom` kjøres bare i lokal tidssone | low | `format.test.mjs:139–151` kjører sine tester på nytt med `TZ=America/New_York`, men den nye testen gjør ikke det. Å flytte påstandene er en direkte retting | patch |
| BH8/EC4 | `range(1, 26)` låser antallet Ansatte | low | Nye Ansatte i testdataene ville blitt hoppet over uten at noen merker det. Rettingen er å bruke `NAVN` | patch |
| BH9 | Regelnavnene i lekkasjetesten er skrevet inn for hånd, og en `assert` om Silje hører ikke hjemme i testen | low | `Regel.årsak` finnes i `REGLER` (`vurdering.py:42`), så navnene kan hentes derfra. Da dekkes 2.4 automatisk | patch |
| BH10 | Endepunktet gjentar stegene fra kandidatruten | low | Testen sammenligner med `/kandidater`, så avvik blir fanget. En felles hjelper er mer enn en direkte retting. Den bør lages i 3.2, som kjører reglene på nytt. Tilfellet der `hent_kandidatgrunnlag` og `hent_vaktdetaljer` er uenige, kan ikke oppstå: begge bruker `finn_ubemannet_vakt` | avvist |
| BH11 | KI-logg og vurderingsmatrise mangler | medium | Policy krever KI-logg. Dokumentasjonen føres av hovedøkten ved avslutningen (`docs/ki-logg/2026-11-12-godkjenningsflaten.md`) | patch |
| BH12 | Docstringen for `GodkjenningsgrunnlagUt` nevner ikke den som opprinnelig var satt opp | low | Bekreftet. Rettes direkte | patch |
| BH13 | Linjen etter «Godkjenn erstatning» kunngjøres bare ved første trykk | low | Linjen blir stående synlig, så knappen ser ikke ødelagt ut. Kunngjøring til skjermleser er v2 | avvist |
| BH14 | `velgEtikett` er ikke testet | low | Én påstand i en eksisterende test | patch |
| BH15 | Betingelsen for «side ikke funnet» i `App.tsx` blir lengre for hver rute | low | Ingen skade nå. En rutetabell er en omskriving utenfor storyen | avvist |
| EC1 | Vaktnummer over 2⁶³−1 gir 500 | low | Fantes fra før i søskenrutene. Johannes vurderte det 2026-11-10 og fant at det ikke er et reelt problem (`issues.md`) | avvist |
| EC2 | Et 200-svar med `null` eller uten `vakt` krasjer frontend | false | Pydantic-modellen `GodkjenningsgrunnlagUt` gjør at backend aldri sender det. `kandidater.ts` har samme forutsetning | avvist |
| EC3 | Svaret kan gjelde en annen id enn URL-en | false | Backend slår opp `ansatt_id` fra stien og returnerer den samme Kandidaten (`main.py`, `next(... k.id == ansatt_id)`) | avvist |

## Verification

**Commands:**
- `backend/`: `.venv\Scripts\python -m pytest`. Forventet: alt består, også import-linter.
- `frontend/`: `npm.cmd run build` og `npm.cmd test`. Forventet: begge består.

**Manual checks:**
- Nettleserkontroll: #4127, velg Jonas og Mette, Avbryt, Godkjenn (meta-linjen fra 2A), en direkte URL for en utelukket id, tilbakeknappen og tastatur. Ingen vakt endrer status på Vaktvalg.
