---
title: 'Story 4.6: Rangeringstabellen på smalere skjermer'
type: 'feature'
created: '2026-11-19'
status: 'done'
baseline_commit: '9226f46f3b1c18b74783971ef0ecb5e18a288f7a'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** I et smalt nettleservindu (skjerm på høykant eller vinduer side om side) ruller rangeringstabellen i sin egen beholder, men rangering og navn ruller ut av syne. Da ser ikke turnusansvarlig hvilken kandidat kostnad, timebelastning, ulempe og preferanse gjelder (UX-DR25, UX-DR28, AV-17). At de fire flatene virker ved 1080, 960 og 680 px, er heller ikke dokumentert med skjermbilder.

**Approach:** Bare CSS: kolonnene «Nr.» og «Kandidat» i rangeringstabellen står fast mot venstre kant (`position: sticky`) når tabellen ruller vannrett. Layouten styres ikke av JavaScript etter bredden, så ingen tilstand monteres på nytt når vinduet endrer bredde. Kontroller deretter alle flatene ved de tre breddene, rett eventuell vannrett siderulling eller klipping, og lagre skjermbilder.

## Boundaries & Constraints

**Always:**
- AV-14 gjelder ved alle bredder: siden ruller aldri vannrett, og bare `.tabellbeholder` ruller.
- De to faste kolonnene har ugjennomsiktig bakgrunn som følger raden (`--color-bg-panel`, `--color-row-alt` på `row-alt`, `--color-column-header-bg` i overskriften), og en skillelinje på høyre side av «Kandidat» som følger med når tabellen ruller. Ingen skygger (DESIGN.md).
- Bare tokens fra `tokens.css` (AV-13). Bredden på «Nr.»-kolonnen er et nytt token i `rem`, slik at den vokser med skriftstørrelsen.
- Kolonnene, rekkefølgen og tekstene fra story 4.4/4.7 er uendret (UX-DR7, UX-DR28). Ved 1600 px vises hele tabellen uten rulling.
- Tilstanden overlever endret vindusbredde: valgt vakt og valgt kandidat (står i URL-en), «Vis alle» og «Vis full liste». «Åpne begrunnelser» finnes ikke før Epic 5. Ingen `matchMedia`, `resize`-lytter eller betinget rendering etter bredde.
- Nye koblinger får komponenttester (OP-16). Layout kan ikke testes i jsdom og kontrolleres i nettleser.

**Never:** Egen visning for mobil eller nettbrett, kortvisning eller skjulte kolonner (AV-17, v2). Endringer i backend, i rangeringen eller i API-formen. Faste kolonner i vaktoversiktens tabell. Epic 5s utvidelseskolonne eller begrunnelsespanel.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Bred skjerm | 1600 px, #4127 | alle 8 kolonner synlige, tabellen ruller ikke | — |
| Smalt vindu, rullet til høyre | 680 px, beholderen rullet helt til høyre | «Nr.» og «Kandidat» står fast ytterst til venstre på hver rad og i overskriften; ulempe- og preferansecellene står ved siden av, uten at noe overlapper | — |
| Vindusendring med åpen tilstand | «Vis alle» og «Vis full liste» åpne, bredden går fra 1600 til 680 px og tilbake | begge er fortsatt åpne, samme rader vises, og ingen ny henting | — |
| Godkjenning i smalt vindu | 680 px, Mette valgt (avviksnotat vises) | kandidatkort, avviksnotat og bekreftelsesboks brytes uten klipping eller siderulling | — |
| Større skrift | Chrome «Stor», 680 px | «Nr.»-kolonnen vokser, totalscoren klippes ikke, og de faste kolonnene overlapper ikke | — |

## Decisions (2026-11-19, Johannes)

- **Skjermbilder:** agenten lager dem med et CDP-skript i headless Chrome mot en midlertidig testdatabase, etter mønsteret fra story 1.5. Skriptet måler også siderulling og posisjonen til de faste kolonnene. Skjermbildene lagres i `docs/ki-logg/2026-11-19-smale-skjermer/` og lenkes fra vurderingsmatrisen. Et menneske gjør likevel den manuelle sjekklisten før PR.
- **P-13:** forståelsestesten ligger utenfor denne storien. 4.6 går til `review` etter koden og den manuelle kontrollen. P-13 står videre som åpent punkt i sprintstatus.
- **Omfang:** hele specen beholdes, selv om den er over 1 600 tokens.

</frozen-after-approval>

## Code Map

- `frontend/src/stil/app.css` -- `.tabell` (l.328–360) har `border-collapse: collapse` og `nowrap`-celler. Med `collapse` følger ikke kantene sticky-cellene i Chrome, så `.rangeringstabell .tabell` får `border-collapse: separate; border-spacing: 0`. Første og andre `th`/`td` får `position: sticky`, `left: 0` og `left: var(--rank-column-width)`, `z-index` over de andre cellene og bakgrunn etter radtypen. «Nr.»-cellen får `width`/`min-width`/`max-width` lik tokenet og `white-space: normal`, slik at totalscoren kan brytes. `.tabellbeholder` (l.320) har allerede `position: relative` og `overflow-x: auto`. Behold `.preferansecelle`-unntaket (l.439).
- `frontend/src/stil/tokens.css` -- nytt token `--rank-column-width` i `rem`, med kommentar. Det er et bevisst avvik fra «faste bredder i px», fordi kolonnen inneholder tekst som skal skalere (AV-13).
- `frontend/src/komponenter/Kandidatflate.tsx` -- `Rangeringstabell`/`Kandidatrad` (l.181–306). Det trengs trolig ingen JSX-endring; selektorene kan bruke `:nth-child`. Legg bare til klasser hvis selektorene blir skjøre, og ikke flytt tilstand.
- `frontend/src/komponenter/Godkjenningsflate.tsx`, `Vaktvalg.tsx`, `LoggInn.tsx` -- rettes bare hvis nettleserkontrollen finner siderulling eller klipping ved 1080, 960 eller 680 px. 4.5s manuelle kontroll var bestått ved disse breddene 2026-11-18.
- `frontend/tester/komponenter/kandidatflate.test.tsx` -- `describe("Rangeringstabellen (story 4.4)")` (l.356), `rangerte(n)`, `datarader`. Ny `describe` for story 4.6 ved siden av.
- `frontend/tester/komponenter/godkjenningsflate.test.tsx` -- `GODKJENNING_METTE` i `hjelpere.ts` (l.229).
- `docs/ki-logg/2026-11-08-vaktoversikt/cdp.mjs` -- mønster for headless Chrome med CDP (Node 26, innebygd `WebSocket`). Chrome er installert lokalt på `C:/Program Files/Google/Chrome/Application/chrome.exe`.
- Ikke endre: `backend/`, `src/api.ts`, `kandidater.ts`, `godkjenning.ts`, tekstene i `tekster.ts`.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/stil/tokens.css`, `frontend/src/stil/app.css` -- token og sticky-regler for de to første kolonnene i `.rangeringstabell` -- AC3.
- [x] `frontend/tester/komponenter/kandidatflate.test.tsx` -- ny test: åpne «Vis alle» (`rangerte(7)`) og «Vis full liste» (`TO_UTELUKKET`), endre `window.innerWidth` og send `resize` (1600 → 680 → 1600). Begge skal fortsatt være åpne med `aria-expanded="true"`, med 7 rader, og `kallTil` skal vise at kandidatene ikke er hentet på nytt -- AC4.
- [x] `frontend/tester/komponenter/godkjenningsflate.test.tsx` -- ny test: med `GODKJENNING_METTE` og `resize` står kandidatkort og avviksnotat for Mette fortsatt, uten ny GET -- AC4.
- [x] Vis at testene kan feile: en midlertidig `resize`-lytter som nullstiller `visAlle` skal gjøre testen rød. Tilbakestill etterpå og noter dette i KI-loggen.
- [x] Nettleserkontroll med CDP-skript i `docs/ki-logg/2026-11-19-smale-skjermer/` av alle fire flatene ved 1080, 960 og 680 px, og 1600 px: `scrollWidth <= innerWidth` på `document.documentElement`, de faste cellene er på plass etter rulling til høyre, og skjermbilder av kandidatflaten og Godkjenning ved de tre breddene. Rett funnene i CSS.
- [x] `docs/testing.md` -- ny rad i komponenttesttabellen og avsnittet «Story 4.6 – smale nettleservinduer».
- [x] `docs/ki-logg/2026-11-19-smale-skjermer.md` -- KI-loggen. `docs/emne/vurderingsmatrise.md` -- milepæl med lenke til skjermbildene. `epic-4-context.md` -- statuslinje.

**Acceptance Criteria:**
- Given 1600 px, when kandidatflaten for #4127 vises, then alle kolonner vises uten rulling i tabellen.
- Given Logg inn, Vaktvalg, kandidatflaten og Godkjenning ved 1080, 960 og 680 px, when siden vises, then ruller den ikke vannrett, ingen tekst klippes eller overlapper, og alle handlinger kan nås med mus og tastatur.
- Given at rangeringstabellen er bredere enn beholderen, when den rulles vannrett, then er «Nr.» og «Kandidat» synlige på hver rad, også mens ulempekolonnen er i syne.
- Given åpne «Vis alle» og «Vis full liste» eller en valgt kandidat på Godkjenning, when vindusbredden endres, then er tilstanden uendret og ingenting hentes på nytt.
- Given hele testpakken, when `npm.cmd run build` og `npm.cmd run test` kjøres i `frontend/`, then består alt.

## Implementation Notes

- Implementert 2026-11-19 av en underagent (Opus 5.5) i `bmad-build`, direkte fra specen. Bare CSS i `app.css` og et nytt token i `tokens.css`; backend og tekster er ikke endret.
- `--rank-column-width` ble først satt til `5.5rem`. Nettleserkontrollen viste at ulempekolonnen da gled 17 px inn under «Kandidat» ved 680 px med tabellen rullet helt til høyre. Tokenet ble rettet til `4.25rem`. Følgen er at totalscoren («79,4 poeng») brytes over to linjer ved alle bredder; teksten er uendret.
- `.rangeringstabell` har `isolation: isolate`, slik at de faste cellenes `z-index` bare gjelder i tabellen.
- Ved 680 px og #4127 var det bare 3 px til overs. Et lengre navn eller en lengre stilling gjør at ulempekolonnen delvis står under de faste kolonnene når tabellen er rullet helt til høyre. Den kan likevel rulles helt fram. Det samme skjer ved 20 px skrift. *(Erstattet 2026-11-20: målingen var gjort uten loddrett rullefelt på siden. Se «Rettet etter PR-gjennomgangen» under.)*
- Underagenten fikk ikke skrive i specen (tillatelsen ble avslått). Orkestratoren krysset av oppgavene og skrev disse notatene etter å ha lest diffen, kjørt `npm.cmd run build` og `npm.cmd run test` på nytt (52 + 43 bestått) og sett på skjermbildene.

- Rettet etter kodegjennomgangen 2026-11-19 (se Review Triage Log):
  - De to første cellene har egne klasser, `fast-nr` og `fast-kandidat`, i `Kandidatflate.tsx` i stedet for `:nth-child`. Ellers ville en framtidig `colspan`-rad fra Epic 5 bli sticky.
  - «Nr.» har fått `overflow-wrap: anywhere`.
  - Dokumentasjonen er avgrenset til det kontrollene faktisk viste.
  - Etter rettingene ble `npm.cmd run build` og `npm.cmd run test` kjørt på nytt (52 + 43 bestått).
  - Nettleserkontrollen og skjermbildene er fra før rettingene. Den manuelle kontrollen før PR må derfor dekke den endelige CSS-en.

- Rettet etter PR-gjennomgangen 2026-11-20 (Mithads funn i PR #32, se Review Triage Log):
  - AC3 feilet ved 680 px når siden har loddrett rullefelt. Rullefeltet tar 15 px, så beholderen blir 573 px i stedet for 588 px, og ulempekolonnen gled 11 px inn under «Kandidat». Den første nettleserkontrollen kjørte med 900 px vindushøyde og målte uten rullefelt.
  - «Kandidat» har fått fast bredde med et nytt token, `--candidate-column-width: 7.5rem` (120 px ved 16 px), og `white-space: normal` og `overflow-wrap: anywhere` som «Nr.». Uten fast bredde ble kolonnen 157 px, fordi stilling og ansiennitet (132 px) ikke ble brutt. Navnene i testdataene er høyst 93 px og står fortsatt på én linje. Stilling og ansiennitet brytes nå over to linjer ved alle bredder.
  - Marginen ved 680 px og 16 px skrift er nå +26 px med rullefelt og +41 px uten. Ved 20 px skrift er den −85 px (før −125 px). Det er det samme INFO-tilfellet som før, se Review Triage Log.
  - Ved 1080 px får tabellen nå plass uten rulling i beholderen.
  - `nettleserkontroll.mjs` kjører nå med 700 px vindushøyde og kontrollerer at kandidatflaten har loddrett rullefelt ved 680 px. Siderulling måles mot `clientWidth` i stedet for `innerWidth`, ellers synes ikke inntil 15 px vannrett overløp. Bredden på «Kandidat» kontrolleres mot tokenet. Tabellen rulles inn i synsfeltet før målingen, og ved 1080 px kontrolleres tabellen som ved 1600 px når den ikke ruller.
  - Kontrollen ble kjørt mot den rettede CSS-en: 125 kontroller besto, og det ble ikke funnet noen feil. Med den faste bredden midlertidig fjernet feilet den med Mithads melding («rullet helt til høyre: ulempe og preferanse står ved siden av de faste»), i tillegg til tokenkontrollen. Kontrollen fanger altså feilen.
  - **Tidlig varsel for Epic 5:** kontrollen legger midlertidig «Skjul begrunnelse ▴» (UX-DR12) inn i siste kolonne. Ved 680 px med rullefelt mangler det da 89 px. Den endelige kolonnen kan bare kontrolleres når den finnes. Story 5.3 må løse dette med egen layout for lenken og kjøre AC3 på nytt (`deferred-work.md`).

## Spec Change Log

## Review Triage Log

Kodegjennomgang 2026-11-19 med blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), alle Opus 5.5 som økten. Gap-funnet fra VG var forhåndsverifisert av laget selv og er tatt inn med dets egen dom.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG | De faste kolonnene kontrolleres bare av et engangsskript i headless Chrome. `npm run test` og CI fanger ikke at bakgrunn, `separate` eller tokenbredde blir endret tilbake | medium (gap-funn, forhåndsverifisert): jsdom gjør ingen layout, og ingen test leser beregnet stil | defer: en nettlesertestløper er et valg for hele gruppa (OP-16) |
| VG, BH, ECH | Resize-testene fanger bare en `resize`-lytter, ikke `matchMedia`, `ResizeObserver` eller forsinket henting. Dokumentasjonen sier at de vokter mot «breddestyrt rendering» generelt | low: kontrollert, jsdom sender ingen `change`-hendelse fra media-spørringer ved endret `innerWidth` | patch: avgrens ordlyden i `docs/testing.md`, `epic-4-context.md` og KI-loggen |
| BH, ECH | Ved 20 px skrift logges det som `[INFO]` at ulempekolonnen ikke står helt ved siden av preferansen når tabellen er rullet helt til høyre. Vurderingsmatrisen sier at alt besto, også med 20 px skrift. Bare Kandidatflaten ble gått gjennom med tab, ikke de tre andre flatene | low: dokumentasjonen sier mer enn kontrollen viste. Matriseraden for større skrift krever bare at de faste kolonnene ikke overlapper hverandre, og kontrollen bekrefter at ulempekolonnen kan rulles helt fram | patch: nevn begge avgrensningene i vurderingsmatrisen, `docs/testing.md` og KI-loggen |
| BH | `:nth-child(-n + 2)` treffer også en framtidig rad med `colspan` (begrunnelsespanelet i Epic 5, UX-DR12), som da blir sticky og 68 px bred | medium: rammer story 5.3. Specen sier at klasser skal brukes hvis selektorene blir skjøre | patch: egne klasser på de to første `th`/`td` i `Rangeringstabell`/`Kandidatrad` og selektorer på dem |
| ECH | «Nr.» har `overflow-wrap: normal`, og Chrome ignorerer `max-width` på tabellceller. Blir min-content større enn tokenet (minste skriftstørrelse i Chrome), vokser kolonnen, og «Kandidat» (`left: token`) dekker totalscoren | low: sjelden innstilling, men rettingen er én verdi | patch: `overflow-wrap: anywhere` i kolonne 1 |
| BH, ECH | Det er bare 3 px til overs ved 680 px. «Kandidat» har ingen maksbredde, så et langt navn eller zoom skyver ulempekolonnen delvis under de faste kolonnene når tabellen er rullet helt til høyre | low: testdataene er faste og fiktive. AC3 holder så lenge faste kolonner + ulempe (ca. 405 px) < beholderen (ca. 590 px). Zoom på 150 % tilsvarer et vindu på 453 px, utenfor kontrollbreddene. Rettingen er ikke direkte, fordi Chrome ignorerer `max-width` på celler | avvist: ført som åpent punkt i `issues.md` før Epic 5 legger til en kolonne. *Snudd 2026-11-20, se neste rad* |
| PR #32 (Mithad Kuduz, 2026-11-19) | AC3 feiler reproduserbart ved 680 px og 16 px skrift: når siden trenger loddrett rulling, tar rullefeltet ca. 15 px, og ulempekolonnen glir inn under de faste kolonnene, med uendrede #4127-data | high: bekreftet 2026-11-20, beholderen var 573 px og marginen −11 px. Vurderingen over regnet ikke med rullefeltet, og `max-width` er ikke nødvendig, fordi `width` og `min-width` virker på celler (som i «Nr.») | patch: fast bredde på «Kandidat» (`--candidate-column-width`), og nettleserkontrollen tester med rullefelt (Implementation Notes) |
| BH | Totalscoren brytes over to linjer også ved 1600 px | false: UX-DR7/DR8 krever ikke én linje. Nummeret står fortsatt først og i fet skrift, og ingenting klippes (skjermbilde ved 1600 px). Følgen er ført i Implementation Notes og vises til mennesket ved godkjenning | avvist |
| VG, BH | Statusen i specen (`in-review`) er ulik `in-progress` i sprintstatus og dokumentene | false: steg 4 i `bmad-build` setter `in-review` før gjennomgangen. Alt samordnes i steg 5 (samme vurdering som i 4.5) | avvist |
| BH | Sesjonslogg og `issues.md` mangler | false: sesjonsloggen skrives av orkestratoren før sluttoppsummeringen (AGENTS.md) | avvist |
| BH, ECH | `nettleserkontroll.mjs` tar passordet som argument og har ingen vern mot manglende argument, CDP-feil eller manglende side | low: engangsskript mot en midlertidig database med tilfeldig testpassord, etter mønsteret fra story 1.5. Rettingene er nye vern, ikke direkte rettelser | avvist |
| BH | Godkjenningstesten teller kall til bare én URL. Ingen mutasjon viser at «Vis full liste» eller ny henting av vakten fanges | false: `falskFetch` feiler testen ved kall til en URL uten rute (`hjelpere.ts:80`). Testen kontrollerer `aria-expanded` for «Vis full liste» og `kallTil(VAKT_URL)` direkte | avvist |
| BH | `docs/testing.md` mangler de konkrete 4.6-kontrollene | false: `docs/testing.md` sier at «Manual checks» i specen tar med de storyspesifikke punktene, og specen har dem | avvist |

## Design Notes

- **Sticky i stedet for egen smal visning:** AV-17 legger mobil/nettbrett til v2, og epics krever vannrett rulling i beholderen, med kandidatidentiteten alltid synlig. To faste kolonner oppfyller det uten å skjule data eller lage en ny layout. Det gir heller ingen JavaScript etter bredde, så AC4 følger av konstruksjonen. Komponenttestene vokter mot at noen legger til breddestyrt rendering senere.
- **`separate` i stedet for `collapse`:** I Chrome blir kantene i en `collapse`-tabell liggende igjen når cellen er sticky. Med `border-spacing: 0` ser tabellen lik ut.

## Verification

**Commands:**
- `frontend/`: `npm.cmd run build` -- typesjekk og bygg består.
- `frontend/`: `npm.cmd run test` -- `node --test` og Vitest består, med de nye 4.6-testene.

**Manual checks (docs/testing.md):** 1080/960/680/1600 px på alle fire flatene, med rangeringstabellen rullet helt til høyre. Tastatur og fokus: tab gjennom tabellbeholderen og «Velg», og fokusrammen skal ikke skjules av de faste kolonnene. Farger: bakgrunnen i de faste cellene på `row-alt`-rader og i overskriften. Større skrift («Stor») ved 680 px. Ekte backend mot #4127 (Jonas og Mette) og #4189. Endre vindusbredden med «Vis alle» og «Vis full liste» åpne. Resultatet føres med malen i `docs/testing.md`.

**Manuell kontroll (docs/testing.md):** Johannes W. Gaertner med Claude (Chrome-utvidelsen), 2026-11-19, Chrome 157 på Windows 11, story 4.6, mot den endelige CSS-en (etter rettingene fra kodegjennomgangen) og en midlertidig testdatabase med `KI_MODUS=demo`.
Først målte agenten med Chrome-utvidelsen. Vinduet var maksimert på en skjerm som er 1280 px bred, så appen ble lagt i en iframe med nøyaktig bredde, og stor skrift ble emulert med 20 px rotskrift. Deretter kontrollerte Johannes selv i vanlig Chrome, med «Stor» skrift i innstillingene og tastatur.
1. 1080, 960 og 680 px: bestått. Vaktvalg, kandidatflaten og Godkjenning (Mette) ble kontrollert med 16 og 20 px skrift. Siden ruller ikke vannrett, ingen tekst klippes, og ingen handling ligger utenfor vinduet. Med tabellen rullet helt til høyre står «Nr.» ved venstre kant og «Kandidat» rett etter på alle rader. Ulempekolonnen får plass ved siden av de faste kolonnene, med minst 65 px til overs. 1600 px er dekket av nettleserkontrollen med skriptet; skjermen er for smal.
2. Tastatur og fokus: bestått. Agenten kontrollerte rekkefølgen på kandidatflaten og Godkjenning og så fokusrammen på Godkjenning. Johannes kontrollerte alle fire flatene.
3. Farger: bestått (bakgrunnen i de faste cellene følger raden og overskriften).
4. Større skrift: bestått («Stor» i Chrome-innstillingene).
5. Ekte backend: bestått (#4127, Jonas og Mette).
Målrettet kontroll av flyt uten komponenttest: vindusbredde 1080 → 960 → 680 → 1080 med «Vis full liste» åpen. Listen forble åpen med alle 20 utelukkede, og det kom ingen nye API-kall.
Ikke relevant: 1600 px manuelt (skjermen er 1280 px; dekket av skriptet).

*Tillegg 2026-11-20:* Den manuelle kontrollen over ble gjort før «Kandidat» fikk fast bredde. Tallet «minst 65 px til overs» kan ikke forenes med målingene i skriptet (3–4 px uten rullefelt). Agentens måling i en iframe er trolig ikke sammenlignbar, og tallet skal ikke brukes. Etter rettingen er den automatiske nettleserkontrollen kjørt på nytt (Implementation Notes). En kort manuell kontroll i et vanlig Chrome-vindu, 680 px bredt og så lavt at siden får rullefelt, gjenstår for den som godkjenner PR-en.
