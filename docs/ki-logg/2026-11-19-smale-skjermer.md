# KI-logg: Story 4.6 – rangeringstabellen på smalere skjermer

Dato: 2026-11-19. Utført av Claude (Opus 5.5) som underagent i én økt, direkte mot
[spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-6-rangeringstabell-pa-smale-skjermer.md).
`epic-4-context.md`, `AGENTS.md` og `docs/testing.md` (spesifikasjonens `context`) ble lest
før koden ble endret.

## Oppgave og prompt

Agenten som forvalter oppgaven ba: «Read spec-4-6-rangeringstabell-pa-smale-skjermer.md
fully and implement it — the spec is the sole source of truth. Load every file listed in
its frontmatter `context:` before you start. When done, report what you changed, how you
verified it, and anything left incomplete or risky.» Beslutningene i spesifikasjonen
(Johannes, 2026-11-19) avgjorde at skjermbildene lages med et CDP-skript og lagres her.

## Leveranse

- **`frontend/src/stil/tokens.css`:** nytt token `--rank-column-width: 4.25rem` (68 px ved
  16 px) med kommentar. Bevisst i `rem`, ikke px, fordi kolonnen har tekst som skal vokse
  med skriften (AV-13).
- **`frontend/src/stil/app.css`:** i `.rangeringstabell` står de to første kolonnene fast
  med `position: sticky`, `left: 0` og `left: var(--rank-column-width)`, `z-index: 1` og
  ugjennomsiktig bakgrunn etter radtypen (`--color-bg-panel`, `--color-row-alt`, og
  `--color-column-header-bg` fra `.tabell th`). «Kandidat» har skillelinje til høyre, uten
  skygge. Tabellen bruker `border-collapse: separate; border-spacing: 0`, fordi kantene i
  Chrome ellers blir liggende igjen når cellen er sticky. «Nr.» har fast bredde lik tokenet
  og `white-space: normal`, så totalscoren brytes i stedet for å klippes. `isolation:
  isolate` på beholderen holder `z-index` inne i tabellen. De to første `th` og `td` har
  klassene `fast-nr` og `fast-kandidat` i `Kandidatflate.tsx` (se Rettelser). Vaktoversiktens
  tabell er ikke berørt.
- **Komponenttester:** én ny i `kandidatflate.test.tsx` («Smale nettleservinduer (story
  4.6)») og én i `godkjenningsflate.test.tsx`. Begge setter `window.innerWidth` og sender
  `resize` (1600 → 680 → 1600) og kontrollerer at åpne lister, rader og valgt kandidat står,
  og med `kallTil` at ingenting er hentet på nytt.
- **Nettleserkontroll:** [`nettleserkontroll.mjs`](2026-11-19-smale-skjermer/nettleserkontroll.mjs),
  [resultatet](2026-11-19-smale-skjermer/resultat.txt) og skjermbildene i
  [`2026-11-19-smale-skjermer/`](2026-11-19-smale-skjermer/).
- **Dokumentasjon:** `docs/testing.md`, `docs/emne/vurderingsmatrise.md` og statuslinjen i
  `epic-4-context.md`.

Ikke endret: backend, `src/api.ts`, `kandidater.ts`, `godkjenning.ts` og `tekster.ts`.
`Kandidatflate.tsx` fikk bare de to klassenavnene. Ingen `matchMedia`, `resize`-lytter eller
betinget rendering etter bredde.

## Rettelser

- **Bredden på «Nr.» ble endret etter nettleserkontrollen.** Første versjon hadde
  `5.5rem` (88 px), slik at «79,4 poeng» stod på én linje. Ved 680 px var tabellen rullet
  helt til høyre da 17 px for bred: de første tegnene i ulempekolonnen lå under «Kandidat»,
  og I/O-matrisen krever at ulempe og preferanse står ved siden av de faste kolonnene.
  Målte kolonnebredder ved 680 px: 88 + 157 for de faste, 191 + 92 + 76 for ulempe,
  preferanse og Velg, mot 588 px i beholderen. Med `4.25rem` (68 px) er det 3 px til gode.
  Prisen er at totalscoren nå brytes over to linjer («79,4» / «poeng») ved alle bredder,
  også ved 1600 px. Teksten er den samme (UX-DR7).
- **Skriptet ble rettet to ganger.** (1) `captureBeyondViewport` ga skjermbilder med
  standard skrift selv om siden var målt med 20 px. Skriptet gjør nå vinduet midlertidig
  like høyt som siden. (2) Den første overlappskontrollen målte midtpunktet i hele
  ulempecellen. Med større skrift ligger cellen delvis under de faste kolonnene når
  tabellen er rullet helt til høyre, og da traff midtpunktet den faste cellen. Det er
  forventet oppførsel for faste kolonner. Kontrollen måler nå midtpunktet i den synlige
  delen av hver celle, og ruller i tillegg til en posisjon der ulempekolonnen starter rett
  etter «Kandidat» og kontrollerer at den da er helt synlig.
- **Rettinger etter kodegjennomgangen (2026-11-19).** (1) Selektorene var
  `:nth-child(-n + 2)`. De ville også truffet en fremtidig rad med `colspan` over hele
  bredden (begrunnelsespanelet i Epic 5, UX-DR12) og gjort den sticky og 68 px bred. De to
  første `th` i `Rangeringstabell` og `td` i `Kandidatrad` har nå klassene `fast-nr` og
  `fast-kandidat`, og reglene peker på dem. (2) «Nr.» hadde `overflow-wrap: normal`. Chrome
  ser bort fra `max-width` på tabellceller, så hvis min-content blir bredere enn tokenet (for
  eksempel med minste skriftstørrelse i Chrome), vokser kolonnen og «Kandidat» (`left:
  token`) dekker totalscoren. Nå er det `overflow-wrap: anywhere`. (3) Dokumentasjonen sa
  mer enn kontrollene viste, og er presisert her, i `docs/testing.md`, i
  `vurderingsmatrise.md` og i `epic-4-context.md`.

## Kvalitetssikring

**Bevisste feil (testene kan feile).** Begge ble tilbakestilt, og `git diff` på komponentene
var tom etterpå.

| Mutasjon | Rød test | Melding |
|---|---|---|
| `useEffect` i `Rangeringstabell` med `window.addEventListener("resize", () => setVisAlle(false))` | «Vis alle» og «Vis full liste» er fortsatt åpne etter endret vindusbredde | `Unable to find an accessible element with the role "button" and name "Vis bare de 5 øverste"` |
| `useEffect` i `Godkjenningsflate` med `resize` → `setForsok((n) => n + 1)` | valgt kandidat og avviksnotatet står etter endret vindusbredde | `Unable to find an accessible element with the role "region" and name "Mette Solberg"` |

**Kommandoer** i `frontend/`: `npm run build` bestod. `npm run test` bestod med 52
`node --test` og 43 Vitest-komponenttester (41 fra før og 2 nye). Etter rettingene etter
kodegjennomgangen ble `kandidatflate.test.tsx` og `godkjenningsflate.test.tsx` kjørt på nytt,
og orkestratoren kjørte `npm.cmd run build` og hele `npm.cmd run test` (52 + 43 bestått).

**Hva komponenttestene dekker.** De sender `resize` med endret `window.innerWidth` og vokter
mot en `resize`-lytter som monterer på nytt, nullstiller tilstand eller henter på nytt. De
fanger ikke `matchMedia`, `ResizeObserver` eller forsinket (debounced) rendering, fordi jsdom
ikke utløser dem.

**Nettleserkontroll** (headless Chrome 157 på Windows 11, CDP med Node 26). Kontrollen og
skjermbildene er fra **før** rettingene etter kodegjennomgangen (egne klasser i stedet for
`:nth-child`, og `overflow-wrap: anywhere` i «Nr.»). Med testdataene skal de ikke gi en
synlig forskjell, men det er ikke målt. Den manuelle kontrollen før PR må derfor gjøres mot
den endelige CSS-en.

- Backend på port 8000 med en midlertidig database i scratchpad-mappen
  (`TURNUSHJELPEREN_DB`), fylt med `python -m adaptere.lagring.testdata` og et eget
  testpassord. `KI_MODUS=demo` og ingen `OPENROUTER_API_KEY`, så ingen betalte kall.
  `backend/turnushjelperen.db` ble ikke rørt.
- Vite på 5173. Chrome med `--headless=new --remote-debugging-port=9333` og en midlertidig
  profil. Kjøring: `node nettleserkontroll.mjs 9333 . <testpassord>`. Passordet står ikke
  i skriptet eller i resultatet.
- 135 kontroller bestod, ingen feilet. Logg inn, Vaktvalg, kandidatflaten (#4127) og
  Godkjenning (Mette, med avviksnotat) ved 1600, 1080, 960 og 680 px, og ved 680 px med
  20 px skrift: siden ruller ikke vannrett, ingen klippet tekst og alle handlinger innenfor
  vinduet. Ved 1600 px vises alle 8 kolonner uten rulling (1088 av 1088 px).
- Ved 1080, 960 og 680 px, og 680 px/20, med tabellen rullet helt til høyre og rullet til
  ulempekolonnen: «Nr.» er like bred som tokenet (68 px, og 85 px med 20 px skrift), står
  ved 0 px i hver rad, «Kandidat» følger uten glipe, de faste cellene ligger øverst, ingen
  synlig celle dekkes, bakgrunnen følger raden og skillelinjen er `solid 1px` i `border`.
  Med 20 px skrift ved 680 px står ulempekolonnen ikke helt ved siden av Preferanse når
  tabellen er rullet helt til høyre: den ligger delvis under de faste kolonnene. Det er
  logget som INFO, ikke som bestått. Den kan rulles fram helt
  (`kandidatflate-680-stor-skrift-ulempe.png`).
- Tastatur, bare på kandidatflaten ved 680 px og 16 px: tab fra beholderen gjennom alle
  fire Velg og tilbake med Shift+Tab. Fokusrammen synes og ligger helt til høyre for de faste
  kolonnene hver gang. Tastatur på Logg inn, Vaktvalg og Godkjenning ble ikke kjørt i
  skriptet og hører til den manuelle sjekklisten.
- Vindusendring: med «Vis alle» (sju rader, tre konstruerte i nettleseren som i story 4.4)
  og «Vis full liste» åpne, 1600 → 1080 → 960 → 680 → 1600 px: samme sti, sju rader,
  begge `aria-expanded="true"`, 20 utelukkede og ingen nye `fetch`-kall. Godkjenning for
  Mette: samme sti, kandidat og avviksnotat, og ingen nye kall. Ingen konsollfeil.

Skjermbildene er gjennomgått visuelt. Alle navn er fiktive testdata fra story 1.2.
«Konstruert kandidat 1–3» finnes bare i bildet med «Vis alle».

## Åpne punkter

- ~~Den manuelle sjekklisten mot den endelige CSS-en~~: bestått 2026-11-19. Johannes brukte
  vanlig Chrome med «Stor» skrift og tastatur på alle fire flatene. Agenten målte i forkant
  med Chrome-utvidelsen i en iframe med nøyaktig bredde. Se «Verification» i
  spesifikasjonen.
- Plassen til ulempekolonnen ved 680 px avhenger av dataene: med 3 px til gode for #4127
  kan et lengre navn eller en lengre stilling i «Kandidat» skyve ulempekolonnen delvis inn
  under de faste kolonnene når tabellen er rullet helt til høyre. Den kan fortsatt rulles
  fram.
- Tre uavhengige underagenter (blind-hunter, edge-case-hunter og verification-gap, Opus 5.5)
  har gått gjennom diffen. Funn, dommer og ruting står i spesifikasjonens Review Triage Log.
  PR-gjennomgang av et gruppemedlem gjenstår.
- Ingen gjentakbar layouttest i CI. Ført i `deferred-work.md`.
- P-13 (forståelsestesten) er utenfor storyen og står fortsatt åpen.
