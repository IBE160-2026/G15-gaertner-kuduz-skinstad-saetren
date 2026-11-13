# KI-logg: Story 2.5 – Ekskludert-boks med oppsummering av utelukkelser

Dato: 2026-11-13. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-5-ekskludert-boks-med-oppsummering-av-utelukkelser.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (OP-15: Mithad Kuduz tar storyen). Arbeidet ble gjort av Claude Code (Sonnet 5) som implementeringsagent, på branchen `story-2.5-ekskludert-boks`.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read …/spec-2-5-ekskludert-boks-med-oppsummering-av-utelukkelser.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

Spesifikasjonen var allerede gjennomgått og godkjent av en uavhengig underagent før denne økten (se spesifikasjonens Review Triage Log): fire funn ble rettet i spesifikasjonsteksten selv (tekstmaler per årsak, startverdi lukket for full liste, duplisert arkitekturtest fjernet, presisering av `test_bare_gyldige_sendes_nfr2`), så denne økten implementerte en spesifikasjon uten åpne funn i den låste delen.

## Leveranse

- **Ny port** (`backend/domene/porter/utelukkelse.py`): frosne dataklasser `RegelAntall`, `EkskludertKandidat` og `UtelukkelsesOppsummering`. Ren Python, ingen import fra `adaptere`.
- **`backend/domene/regelmotor/vurdering.py`**: ny funksjon `lag_utelukkelsesoppsummering(vurdering, regler=REGLER)` rett etter `vurder_kandidater`. `per_regel` telles i `REGLER`-rekkefølge, en Kandidat telles under hver regel den bryter; `totalt` teller hver Kandidat én gang; `utelukkede` beholder rekkefølgen fra `vurdering.utelukkede` (allerede alfabetisk).
- **`backend/adaptere/api/main.py`**: `RegelAntallUt`, `EkskludertKandidatUt`, `UtelukkelsesOppsummeringUt`, og `KandidaterUt` får feltet `utelukkelser`. Bygges med samme `model_validate(..., from_attributes=True)`-mønster som `VaktoversiktUt`. `DatafeilUt` er uendret (ingen Kandidat er vurdert).
- **Frontend**: `api.ts` får typene `RegelAntall`, `EkskludertKandidat`, `UtelukkelsesOppsummering`, og `Kandidatsvar`s `"ok"`-variant får `utelukkelser`. `kandidater.ts`s `"klar"`-variant får samme felt, satt i `tilstandFraSvar`. `Kandidatflate.tsx` får en ny komponent `EkskludertBoks`, vist etter både tom-teksten og listen når `oppsummering.totalt > 0`, med en `<button aria-expanded>` for full liste (lukket som startverdi). `tekster.ts` får fire separate maler (én per årsak, ulik grammatikk) pluss statiske tekster for hovedlinjen og knappen. `app.css` får `.ekskludert-boks` med stiplet kant (`var(--border-width) dashed var(--color-border)`, ikke en rå `1px`, for å holde AV-13) og bakgrunn `--color-breadcrumb-bg`, og `.ekskludert-liste` for innrykket i full listen. Ingen nye tokens trengtes i `tokens.css` — alt som specen ber om fantes allerede.
- **Tester**: ny `backend/tester/regelmotor/test_utelukkelsesoppsummering.py` (7 tester: ingen utelukkede, én regel, flere årsaker på samme Kandidat med sum per regel > totalt, rekkefølgen følger `REGLER`, egen regelliste, rekkefølgen i `utelukkede` endres ikke). `backend/tester/api/test_kandidater.py` er oppdatert: `test_gyldige_stemmer_med_fasiten` sjekker nøkkelsettet `{"status", "kandidater", "utelukkelser"}`; `test_bare_gyldige_sendes_nfr2` er omdefinert til å sjekke presist at hvert utelukket navn ikke er i `kandidater` og står nøyaktig i `utelukkelser["utelukkede"]` med riktig årsak fra `FASIT`, og at den satt opp-ansatte er i ingen av dem; `test_4189_gir_tom_liste_med_status_ok_til_story_2_6` har nå eksakt likhet med hele `utelukkelser`-objektet (24 utelukket, per_regel 3/2/18/1, 24 navn med årsaker); ny `test_per_regel_stemmer_med_fasiten` kontrollerer 8/7/4/1 for #4127 og 3/2/18/1 for #4189, bygget fra `FASIT[nummer]["utfall"]`, ikke hardkodet to steder. `frontend/tester/kandidater.test.mjs` har en ny test for at `tilstandFraSvar` tar med `utelukkelser` uendret, og alle eksisterende likhetssjekker av `"klar"`-tilstanden er utvidet med feltet.

## Korrigering og kvalitetssikring

Ingen feil i generert kode ble oppdaget under implementeringen som krevde retting utover normal iterasjon mens testene ble skrevet (for eksempel å bekrefte at Python sin vanlige `sorted()` stemmer med regelmotorens norske sortering for hele `ANSATTE`-listen, kontrollert direkte i et Python-skall før testene i `test_kandidater.py` ble skrevet med eksakte navnelister).

Kontroller:

- **Fasiten (AV-07):** fasittallene i Code Map (8/7/4/1 for #4127, 3/2/18/1 for #4189) ble kontrollert mot `testdata.FASIT["utfall"]` før testene ble skrevet, ikke kopiert fra programresultatet — testene bygger de forventede tallene fra `FASIT` med en egen opptelling (`forventet_per_regel`), uavhengig av regelmotorens egen telling.
- **Full `pytest` i `backend/`:** **390 bestått**, inkludert import-linter-kontrakten (`tester/test_arkitektur.py`), som bekrefter at `domene/porter/utelukkelse.py` ikke importerer `adaptere`.
- **`npm run build`:** typesjekk og bygg bestod uten feil.
- **`npm test`:** **29 bestått**, inkludert den nye testen for `utelukkelser` i `tilstandFraSvar`.
- Flere-årsaker-tilfellet (en Kandidat som bryter både kolliderende vakt og 35-timersregelen) finnes ikke i seeden med vilje (Epic 2-konteksten), og er dekket med syntetisk `Kandidatvurdering`-enhetsdata i `test_utelukkelsesoppsummering.py`, som specen krever.

## Retting etter kodegjennomgang (2026-11-13)

En uavhengig gjennomgang av den ferdige implementeringen fant sju punkter, alle rettet:

- `frontend/src/kandidater.ts`: `ekskludertBoksTekst` kastet hvis en `per_regel`-oppføring hadde en `årsak` uten tekstmal i `tekster.ts` (TypeScript-casten `as Record<string, ...>` skjulte dette for typesjekkeren). Lagt til fallback `` `${antall} ${årsak}` `` og en test med en oppdiktet, umappet årsak.
- `backend/tester/api/test_kandidater.py`: `ID_VED_NAVN` og `utelukkede_svar` var ordbøker bygd fra navn, som ville skjult et duplikatnavn stille og pekt testen på feil ansatt-id. Lagt til `assert len(...) == len(...)` rett etter hver er bygd.
- `backend/tester/api/test_kandidater.py`: `forventet_utelukkelser` sorterte med Pythons vanlige `sorted()`, som tilfeldigvis stemmer med dagens fasitnavn, men ikke er bundet til produksjonslogikken. Byttet til regelmotorens egen `norsk_sorteringsnøkkel` på ekte `Kandidat`-objekter.
- `frontend/src/kandidater.ts` og `Kandidatflate.tsx`: full-listens radtekst («Navn — årsak, årsak») lå inline i JSX og var utestet. Skilt ut som `ekskludertRadTekst`, med tester for én og to årsaker (det siste er Design Notes-eksempelet «Kari Nordmann — kolliderende vakt, 35-timersregelen»).
- `frontend/src/komponenter/Kandidatflate.tsx` og `tekster.ts`: pilglyfene «▾»/«▴» lå i selve knappeteksten, ikke i et eget `aria-hidden`-element slik `Brodsmulesti.tsx` og `Vaktvalg.tsx` gjør for andre dekorative tegn. Glyfen er nå et eget `<span aria-hidden="true">` ved siden av den lesbare teksten «Vis full liste»/«Skjul full liste».
- `docs/emne/vurderingsmatrise.md`: frontendtall oppdatert til 35 bestått (29 opprinnelig + 3 fra `ekskludertBoksTekst` lagt til før denne gjennomgangen + 3 nye fra denne rettingen).

Etter rettingene: full `pytest` i `backend/` — fortsatt 390 bestått (testene over la bare til flere assert, ingen nye testfunksjoner), kjørt målrettet mot `tester/api/test_kandidater.py`, `tester/regelmotor/test_utelukkelsesoppsummering.py` og `tester/test_arkitektur.py` (52 bestått). `npm run build` og `npm test` i `frontend/` — 35 bestått.

## Uavhengig kodegjennomgang (2026-11-13)

Etter rettingene over gikk tre uavhengige agenter (blind-hunter, edge-case-hunter, verification-gap, alle Sonnet) gjennom den ferdige implementeringen uten å ha sett den selv — se spesifikasjonens Review Triage Log for hele tabellen. Verification-gap fant ingen hull. De sju funnene over kommer fra denne gjennomgangen (blind-hunter og edge-case-hunter fant delvis samme sak, slått sammen). To funn ble avvist: manglende `aria-controls` (UX-DR24 sier uttrykkelig at prosjektet ikke har noe utvidet ARIA-program) og manglende automatisk test av to UI-tilstander (tomtilstanden og full listens åpen/lukket, som dekkes av nettleserkontroll i alle stories fra 1.5 til 2.4, ikke av en komponenttestrigg prosjektet ikke har).

## Nettleserkontroll (2026-11-13)

Mot en midlertidig testdatabase i scratchpad (ikke `backend/turnushjelperen.db`), med en headless, ekte Chrome drevet av Playwright. 13 kontroller, alle bestått:

- **#4127:** boksteksten var nøyaktig «20 utelukket av harde regler · 8 under kompetanse-minstekrav · 7 kolliderende vakt · 4 brudd på 11-timersregelen · 1 brudd på 35-timersregelen». Knappen startet lukket (`aria-expanded="false"`), og full listen fantes ikke i DOM-en før åpning.
- Tastaturbetjening: fokusert knapp og `Enter` åpnet full listen (`aria-expanded="true"`, 20 rader, alfabetisk med riktig årsak hver) og lukket den igjen ved nytt `Enter`.
- **#4189:** boksteksten var «24 utelukket av harde regler · 3 under kompetanse-minstekrav · 2 kolliderende vakt · 18 brudd på 11-timersregelen · 1 brudd på 35-timersregelen», vist under tomtekst-linjen fra 2.4, med samme tastaturbetjening og 24 rader i full listen.
- **360 px bredde:** `document.documentElement.scrollWidth` var lik `clientWidth`, altså ingen vannrett siderulling, og innholdet var lesbart på skjermbildet.
- Ingen konsollfeil utover forventede 401 (før innlogging) og en manglende favicon.
- Skriptet og skjermbildene ligger i [`2026-11-13-ekskludert-boks/`](2026-11-13-ekskludert-boks/) (`nettleserkontroll.mjs`, `vakt-4127-apen.png`, `vakt-4189-apen.png`, `vakt-4127-360px.png`), kjørt med en ekte, lokal Chrome via `playwright-core` (ikke installert i prosjektets egne `package.json`).

## Gjenstår

- Menneskelig PR-gjennomgang av et gruppemedlem.
- Testene er kjørt på Windows i denne økten (ikke bekreftet på macOS/Linux for denne storyen spesifikt; CI dekker Linux).
