---
title: 'Story 2.5: Ekskludert-boks med oppsummering av utelukkelser'
type: 'feature'
created: '2026-11-13'
status: 'done'
baseline_commit: 'c029c5c55d9eb6317f0218601d3638283cbe94fa'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatflaten viser bare de Gyldige kandidatene. Turnusansvarlig kan ikke se om listen bare er kort, eller om regelmotoren faktisk har vurdert og forkastet resten (UX-DR15).

**Approach:** Legg til en Ekskludert-boks under kandidatlisten, som viser totalt antall utelukkede og antall per Hard regel, med en utvidbar full liste. Tallene bygges av regelmotoren som en ny port, `UtelukkelsesOppsummering`, og sendes med i det eksisterende `GET /api/vakter/{nr}/kandidater`-svaret.

## Boundaries & Constraints

**Always:**
- Boksen vises når minst én Kandidat er utelukket, uansett om listen over Gyldige er tom (#4189) eller ikke (#4127). Den har stiplet kant og bakgrunn `--color-breadcrumb-bg` (`#f7f9fb`, samme verdi som UX-DR15 krever).
- Teksten følger mockupens mønster, men med fasitens tall, ikke mockupens: «N utelukket av harde regler · N under kompetanse-minstekrav · N kolliderende vakt · N brudd på 11-timersregelen · N brudd på 35-timersregelen». En regel med 0 utelukkede tas ikke med i oppramsingen. Rekkefølgen følger `REGLER`.
- En Kandidat som bryter flere regler, telles én gang i totalen og én gang under hver regel den bryter (summen per regel kan da bli større enn totalen). Seeden har ingen slike tilfeller; dekkes med enhetsdata i domenet.
- «Vis full liste ▾» er en knapp (`<button aria-expanded>`), ikke en lenke, og kan nås og aktiveres med tab/enter (UX-DR24). Åpen viser hver utelukket Ansatt med navn og alle årsakene, kommaseparert, og kan lukkes igjen.
- `UtelukkelsesOppsummering` (typene og en ren byggefunksjon) ligger i `domene/porter`, konstrueres bare av `domene/regelmotor` (AD-1), og bygges fra `Kandidatvurdering.utelukkede`, aldri fra API-laget.
- Svaret er uendret ellers: `status: "ok"`, `kandidater` er fortsatt bare Gyldige, alfabetisk (NFR2). `DatafeilUt` får ingen oppsummering, fordi ingen Kandidat er vurdert.
- Testdatafasiten tilpasses aldri koden (AV-07): #4127 gir 20 utelukket (8/7/4/1), #4189 gir 24 (3/2/18/1).

**Never:** Endre hvem som er Gyldig, tomtilstanden fra story 2.6, rangering, kostnad eller KI. Endring i skjema eller testdata. At en utelukket Kandidat dukker opp i `kandidater`-listen.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| #4127 | seed | boks med «20 utelukket av harde regler · 8 under kompetanse-minstekrav · 7 kolliderende vakt · 4 brudd på 11-timersregelen · 1 brudd på 35-timersregelen» | — |
| #4189 | seed | boks med «24 utelukket …», vist under den eksisterende tomtekst-linjen fra 2.4 | — |
| Flere årsaker | enhetsdata: én Kandidat bryter kolliderende vakt og 35-timersregelen | telles i totalen én gang, og under begge regelradene | — |
| Ingen utelukkede | enhetsdata: alle Gyldige | ingen boks vises | — |
| Full liste lukket → åpen → lukket | knappetrykk | viser/skjuler listen, `aria-expanded` følger tilstanden, fokus beholdes på knappen | — |
| Satt opp-ansatt | den som opprinnelig var satt opp på Vakten | verken i `kandidater` eller i oppsummeringen (AV-06, vurderes aldri) | — |

</frozen-after-approval>

## Code Map

- `backend/domene/porter/utelukkelse.py` (ny) — frosne dataklasser `RegelAntall(årsak: str, antall: int)`, `EkskludertKandidat(id: int, navn: str, årsaker: tuple[str, ...])` og `UtelukkelsesOppsummering(totalt: int, per_regel: tuple[RegelAntall, ...], utelukkede: tuple[EkskludertKandidat, ...])`. Ren Python, ingen import fra `adaptere` (AD-1/AD-2, fanges av `tester/test_arkitektur.py`).
- `backend/domene/regelmotor/vurdering.py` — ny funksjon `lag_utelukkelsesoppsummering(vurdering: Kandidatvurdering, regler: tuple[Regel, ...] = REGLER) -> UtelukkelsesOppsummering` rett etter `vurder_kandidater`. `per_regel`: for hver `regel` i `regler`, tell `u for u in vurdering.utelukkede if regel.årsak in u.årsaker`, i `REGLER`-rekkefølge. `utelukkede`: `vurdering.utelukkede` er allerede alfabetisk sortert (samme grunnlag-sortering som `gyldige`); map hver til `EkskludertKandidat`.
- `backend/adaptere/api/main.py`:
  - Importer `lag_utelukkelsesoppsummering` og porttypene.
  - Nye Pydantic-modeller: `RegelAntallUt`, `EkskludertKandidatUt`, `UtelukkelsesOppsummeringUt` (samme felt som porten).
  - `KandidaterUt` (l.128) får `utelukkelser: UtelukkelsesOppsummeringUt`. Fjern den utdaterte kommentaren «Utelukkede sendes ikke ennå».
  - I `kandidater()` (l.236): bygg `oppsummering = lag_utelukkelsesoppsummering(vurdering)` og `UtelukkelsesOppsummeringUt.model_validate(oppsummering, from_attributes=True)`, samme mønster som `VaktoversiktUt.model_validate(oversikt, from_attributes=True)` (l.226) for nøstede dataklasser.
- `backend/tester/regelmotor/test_utelukkelsesoppsummering.py` (ny) — enhetstester med syntetiske `Kandidatvurdering`: ingen utelukkede, én regel, flere regler på samme Kandidat (summen per regel > totalen), rekkefølgen følger `REGLER`. Import-forbudet mot `adaptere` er allerede dekket av `tester/test_arkitektur.py` for hele `domene/`; ikke dupliser den kontrollen her.
- `backend/tester/api/test_kandidater.py`:
  - `test_gyldige_stemmer_med_fasiten` (l.43): `set(svar)` blir `{"status", "kandidater", "utelukkelser"}`.
  - `test_bare_gyldige_sendes_nfr2` (l.54) omdefineres. I dag sjekker fire linjer (l.64–67) at årsaksstrengene ikke finnes noe sted i responsteksten; ikke bare snu disse til «in respons_tekst», det ville bare bevise at strengen finnes et sted, ikke at den står riktig. Sjekk i stedet presist: hvert navn i `forventet_utelukket(nummer)` finnes i `svar["kandidater"]`-listen er `False`, og finnes nøyaktig i `svar["utelukkelser"]["utelukkede"]` med riktig(e) årsak(er) fra `FASIT`. Den som var satt opp (`satt_opp`), skal verken stå i `kandidater` eller i `utelukkelser["utelukkede"]`.
  - `test_4189_gir_tom_liste_med_status_ok_til_story_2_6` (l.107): oppdater den eksakte likheten til å inkludere `utelukkelser` med riktig fasit (totalt 24, per_regel 3/2/18/1, 24 navn med årsaker).
  - Legg til: fasitens per-regel-tall for #4127 (8/7/4/1) og #4189 (3/2/18/1) mot `svar["utelukkelser"]["per_regel"]`, bygget fra `FASIT[nummer]["utfall"]`.
- `frontend/src/api.ts`: nye typer `RegelAntall`, `EkskludertKandidat`, `UtelukkelsesOppsummering`; `Kandidatsvar`s `"ok"`-variant får `utelukkelser: UtelukkelsesOppsummering`.
- `frontend/src/kandidater.ts`: `Kandidattilstand`s `"klar"`-variant får `utelukkelser: UtelukkelsesOppsummering`, satt fra `tilstandFraSvar`.
- `frontend/src/komponenter/Kandidatflate.tsx`: ny komponent `EkskludertBoks({ oppsummering })`, vist i `Kandidatliste` etter listen og etter tom-teksten (begge grener), bare når `oppsummering.totalt > 0`. Lokal `useState(false)` for åpen/lukket — full listen starter lukket.
- `frontend/src/tekster.ts`: fire ulike maler, én per årsak, ikke én generisk mal — grammatikken er ulik per regel:
  - `"kompetanse-minstekrav"` → `(n) => \`${n} under kompetanse-minstekrav\``
  - `"kolliderende vakt"` → `(n) => \`${n} kolliderende vakt\`` (ingen «brudd på»)
  - `"11-timersregelen"` → `(n) => \`${n} brudd på 11-timersregelen\``
  - `"35-timersregelen"` → `(n) => \`${n} brudd på 35-timersregelen\``

  Nøkkelen er backendens eksakte årsaksstreng (se `årsak`-verdiene i `domene/regelmotor/{kompetanse,kolliderende_vakt,elleve_timer,trettifem_timer}.py`), ikke en generert streng. Pluss en statisk mal for boksens hovedlinje og knappeteksten åpen/lukket.
- `frontend/src/stil/app.css` og `tokens.css`: `.ekskludert-boks` med `border: 1px dashed var(--color-border); background: var(--color-breadcrumb-bg);` og innrykk for full-liste-elementene. Bare tokens (AV-13).
- `frontend/tester/kandidater.test.mjs`: test at `tilstandFraSvar` tar med `utelukkelser`.
- Ikke endre: `kandidatgrunnlag.py`, `typer.py`, `REGLER`-rekkefølgen, testdata eller `FASIT`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/porter/utelukkelse.py` — porttypene (UX-DR15, AD-1).
- [x] `backend/domene/regelmotor/vurdering.py` — `lag_utelukkelsesoppsummering`.
- [x] `backend/adaptere/api/main.py` — `utelukkelser` i `KandidaterUt`, bygd i `kandidater()`.
- [x] `backend/tester/regelmotor/test_utelukkelsesoppsummering.py` — enhetstester, inkl. flere årsaker på én Kandidat.
- [x] `backend/tester/api/test_kandidater.py` — oppdater de tre berørte testene og legg til fasitkontroll av `per_regel`.
- [x] `frontend/src/api.ts`, `kandidater.ts` — nye typer og `utelukkelser` i tilstanden.
- [x] `frontend/src/komponenter/Kandidatflate.tsx`, `tekster.ts`, `stil/app.css` — `EkskludertBoks` med utvidbar full liste.
- [x] `frontend/tester/kandidater.test.mjs` — dekk den nye tilstanden.
- [x] `README.md`, `docs/ki-logg/<dato>-ekskludert-boks.md`, `docs/emne/vurderingsmatrise.md`, `_bmad-output/implementation-artifacts/epic-2-context.md` — dokumenter flyt, KI-arbeid og bevis.

**Acceptance Criteria:**
- Given #4127, when kandidatflaten lastes, then boksen viser 20 utelukket med riktig fordeling på de fire reglene, og «Vis full liste ▾» viser alle 20 med navn og årsaker.
- Given #4189, when flaten vises, then boksen viser 24 utelukket under den eksisterende tomtekst-linjen.
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then alt består.

## Implementation Notes

- 2026-11-13: En underagent implementerte storyen fra spesifikasjonen alene. Verifisert: 390 backendtester, 29 frontendtester og build grønt.
- 2026-11-13, orkestratorens egen kontroll (Matrix Test Audit): grensetabellens to tekstrader («#4127 → boks med …», «#4189 → boks med …») hadde ingen test av selve den sammensatte teksten, bare av dataene bak den. Hovedlinjen ble derfor flyttet ut som en ren funksjon, `ekskludertBoksTekst`, i `frontend/src/kandidater.ts`, brukt av komponenten i stedet for en innebygd `.join`. Tre nye tester i `kandidater.test.mjs` dekker nå begge vaktene med de ekte fasittallene (20/8/7/4/1 og 24/3/2/18/1) og at en regel med 0 utelukkede ikke tas med. 32 frontendtester består etter rettingen.
- De to gjenstående radene i grensetabellen (ingen boks ved 0 utelukkede; full liste lukket→åpen→lukket med `aria-expanded`) er UI-tilstander uten noen komponenttestrigg i prosjektet, slik praksis har vært i 1.5–2.4. De dekkes av nettleserkontroll før PR, ikke av automatiske tester.

## Spec Change Log

## Review Triage Log

En uavhengig underagent (Sonnet, samme modellnivå som økten) gikk gjennom spesifikasjonen 2026-11-13, før godkjenning. Fasittallene (20/8/7/4/1 for #4127, 24/3/2/18/1 for #4189), porten som bare konstrueres av `regelmotor`, `model_validate(..., from_attributes=True)` med nøstede dataklasser, NFR2-tolkningen og rekkefølgen i full listen ble alle kontrollert og funnet i orden. Ingen funn i den låste delen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| 1 | Frontend-tekstmappingen fra årsak til norsk frase var ikke presisert; en generisk mal ville gitt feil grammatikk | middels | rettet i Code Map: fire eksplisitte maler |
| 2 | Startverdien for «Vis full liste» var ikke eksplisitt angitt | lav | rettet i Code Map: starter lukket |
| 3 | En foreslått test for at porten ikke importerer `adaptere` ville duplisert `tester/test_arkitektur.py` | lav | fjernet fra oppgaven |
| 4 | Omdefineringen av `test_bare_gyldige_sendes_nfr2` var ikke presis nok til å hindre en svakere test (bare snu «not in» til «in» på hele responsteksten) | lav | presisert i Code Map |

Kodegjennomgang 2026-11-13 (etter implementering) med blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), alle Sonnet. Verification-gap fant ingen hull. To funn (BH og ECH) hadde samme rotårsak og er slått sammen.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| BH, ECH | `tekster.ts`s `årsaksmaler`-oppslag har ingen reserveløsning for en årsak uten mal; `as Record<string,...>` skjuler det for TypeScript | middels: reelt krasj (kaller `undefined` som funksjon) hvis en fremtidig regel mangler en mal, men ikke nåbart i dag siden `REGLER` er et lukket sett på fire (PRD §4.2). Harde for en vedlikeholder å oppdage før kjøretid | patch: reserveverdi i `ekskludertBoksTekst` og en test med en ukjent årsak |
| ECH | `ID_VED_NAVN` i `test_kandidater.py` bygges fra `navn` uten å sjekke at navnene er unike; en duplikat ville stille ID-en til feil ansatt | lav: testkode, ingen duplikater i dagens 25 ansatte, triviell retting | patch: ett `assert len(...) ==` rett etter oppslaget bygges |
| ECH | Samme mønster i `utelukkede_svar`-ordboken i `test_bare_gyldige_sendes_nfr2`: en duplikat ville stille navnet usynlig | lav: samme rot som over, testkode | patch: samlet med raden over |
| ECH | `forventet_utelukkelser` sorterer med Pythons `sorted()`, ikke regelmotorens `norsk_sorteringsnøkkel`; stemmer i dag ved en kontrollert tilfeldighet, men ikke garantert ved fremtidige navn | lav: testkode, kontrollert at dagens fasitnavn gir samme rekkefølge | patch: gjenbruk `norsk_sorteringsnøkkel` som sorteringsnøkkel i testen |
| BH | `docs/emne/vurderingsmatrise.md` sier «29 frontendtester», men det faktiske tallet etter Matrix Test Audit-rettingen er 32 | lav: kontrollert med egen kjøring og av to av lagene uavhengig | patch: rett tallet |
| BH | Full-listens radtekst (`{navn} — {årsaker}`) er bygd direkte i JSX og er ikke testet, selv om Design Notes gir et eksakt eksempel med to årsaker | lav: samme type hull som den allerede rettede hovedlinjen, ikke nåbart i dag men lett å teste | patch: skill ut som ren funksjon ved siden av `ekskludertBoksTekst`, test med spesifikasjonens eksempel |
| BH | Glyfene «▾»/«▴» i knappeteksten er ikke pakket i `aria-hidden`, ulikt `Brodsmulesti.tsx:16` og `Vaktvalg.tsx:124` i samme kodebase | lav: reelt avvik fra etablert mønster i prosjektet, triviell retting | patch: pakk glyfen i `<span aria-hidden="true">` |
| BH | Knappen mangler `aria-controls` mot full-listen | lav: avvist. UX-DR24 sier uttrykkelig «Det finnes ikke noe utvidet WCAG- eller ARIA-program», og `aria-controls` brukes ingen andre steder i kodebasen. Den låste delen krever bare `aria-expanded` og tastaturbetjening, begge oppfylt | avvist, utenfor omfang (UX-DR24) |
| BH, VG | To rader i grensetabellen (ingen boks ved 0 utelukkede; full liste lukket→åpen→lukket) har ingen automatisk test | lav: avvist. Spesifikasjonens egen Verification-del setter nettleserkontroll som metode for nettopp disse, som i alle tidligere stories (1.5–2.4), og prosjektet har ingen komponenttestrigg | avvist, dekkes av nettleserkontroll før PR |
| BH | KI-loggen sier at ingen uavhengig kodegjennomgang er kjørt denne økten, men den gjennomgangen skjer akkurat nå | lav: reelt, men skyldes rekkefølgen i selve byggeprosessen | rettes direkte i KI-loggen når denne gjennomgangen er ferdig, ikke sendt til implementeringsagenten |
| BH | Et modulnivå `const ek = TEKSTER.ekskludertBoks;` i `Kandidatflate.tsx` har samme navn som en lokal `const ek` i en annen fil (`kandidater.ts`) | false: samme fil har allerede `const t = TEKSTER.kandidatflate;` på modulnivå som etablert mønster (l.21); de to `ek`-konstantene deler aldri omfang, og navnelikhet på tvers av filer er ikke en reell feilkilde i dette mønsteret | avvist |

## Design Notes

- **Hvorfor byggefunksjonen ligger i `regelmotor`, ikke i `porter`:** AC-en krever at porten «konstrueres bare av `domene/regelmotor`». `porter/utelukkelse.py` holder bare datatypene, uten logikk, slik `domene/typer.py` gjør for `Vakt` og `Kandidat`.
- **Eksempel på full liste:** «Eirik Moen — kompetanse-minstekrav» for én årsak, «Kari Nordmann — kolliderende vakt, 35-timersregelen» for to, kommaseparert i samme rekkefølge som `REGLER`.

## Verification

**Commands:**
- `backend/`: `.venv\Scripts\python -m pytest`. Forventet: alt består, også import-linter.
- `frontend/`: `npm.cmd run build` og `npm.cmd test`. Forventet: begge består.

**Manual checks:**
- Nettleserkontroll: #4127 og #4189 viser riktig boks og tall, «Vis full liste» virker med tastatur, og teksten er lesbar ved 360 px.
