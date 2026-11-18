# KI-logg: Story 4.5 – avviksnotat og nøkkeltall på godkjenningsflaten

Dato: 2026-11-17. Utført av Claude (Sonnet 5) i én sammenhengende økt, direkte
mot spesifikasjonen, uten `bmad-build`s underagent-oppsett. Grunnlaget er
[spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-5-avviksnotat-og-nokkeltall-pa-godkjenningsflaten.md),
`epic-4-context.md`, `AGENTS.md`, beslutningsreferatet og `docs/testing.md`,
alle lest før koden ble endret, som spesifikasjonens `context`-felt krever.

## Oppgave og prompt

Brukeren (en annen agent, som forvalter oppgaven på brukerens vegne) ba:
«Read spec-4-5-avviksnotat-og-nokkeltall-pa-godkjenningsflaten.md fully and
implement it — the spec is the sole source of truth. Load every file listed
in its frontmatter `context:` before you start.» Ingen ytterligere
presisering ble gitt; spesifikasjonens frosne Intent/Boundaries, Code Map og
I/O-matrise var derfor eneste kilde for avgjørelser.

## Leveranse

- **Backend** (`backend/adaptere/api/main.py`): `GodkjenningsgrunnlagUt.kandidat`
  er nå `RangertKandidatUt` (var `KandidatUt`), og et nytt felt `topprangert`
  er lagt til. `godkjenningsgrunnlag()` kjører `ranger(...)` på samme grunnlag
  som allerede er hentet, finner valgt kandidat og nr. 1 via `plass`, og
  bygger begge med den eksisterende `rangert_ut`. Ingen endring i
  rangeringsformelen, POST-ruten eller `grunnlagsmerke`.
- **Backend-tester** (`backend/tester/api/test_godkjenningsgrunnlag.py`):
  oppdaterte nøkkelsett og fasitsvar for Jonas (topprangert `None`) og en ny
  fasittest for Mette (topprangert er Jonas' fulle `RangertKandidatUt`), samt
  nye tester for at `topprangert` er nøyaktig `None` bare ved plass 1, for én
  gyldig kandidat, og for at en direkte lagret tolkning (uten live KI-kall)
  kan endre topplasseringen. `test_kandidater.py`s
  `test_kandidatfeltene_er_de_samme_som_i_godkjenningsgrunnlaget` ble også
  oppdatert (se Rettelser).
- **Frontend-typer** (`src/api.ts`, `src/godkjenning.ts`): `Godkjenningssvar`
  og `Godkjenningstilstand` bruker nå `RangertKandidat` og `topprangert`.
- **Frontend-komponenter**: `Belastningslinje` og `Ulempeindikator` er skilt
  ut av `Kandidatrad` i `Kandidatflate.tsx` (eksportert, med et `Fragment` som
  holder DOM-en uendret der de var inline før) og gjenbrukt i
  `Godkjenningsflate.tsx`s kandidatkort. En ny `Avviksnotat`-komponent viser
  kostnad, kompetansenivå, timebelastning og ulempe for valgt og topprangert
  kandidat side om side, bare når `tilstand.topprangert` ikke er `null`.
- **Tekster og stil**: `tekster.ts` fikk `godkjenning.avviksnotat` (overskrift,
  innledning og den påkrevde linjen «Turnushjelperen anbefaler, den bestemmer
  aldri selv.»). `app.css` fikk `.avviksnotat` (stiplet kant, som
  Ekskludert-boksen) og en liten overskriftsstil i `accent`-farge, bare med
  tokens fra `tokens.css` (AV-13).
- **Frontend-tester**: `hjelpere.ts`s delte `JONAS`-fixture ble utvidet til
  `RangertKandidat` med #4127s fasit uten lagrede tolkninger (nr. 1, 79,40),
  og en ny `METTE`/`GODKJENNING_METTE`-fixture ble lagt til (nr. 2, 72,40,
  topprangert Jonas). Fire nye komponenttester i
  `godkjenningsflate.test.tsx` dekker kandidatkortets nøkkeltall og
  tekstvarsel ved høy belastning, avviksnotatets innhold for valgt og
  topprangert side om side (uten å blokkere godkjenningsknappen), og at et
  endret grunnlag gir nytt grunnlagsmerke og oppdatert (her: forsvunnet)
  avviksnotat før ny bekreftelse kreves (P-09).

## Rettelser

- `test_kandidater.py::test_kandidatfeltene_er_de_samme_som_i_godkjenningsgrunnlaget`
  antok at godkjenningsgrunnlagets kandidat var en delmengde av listens felt
  (`KandidatUt`). Siden begge nå bygges med samme `rangert_ut`, er testen
  rettet til å sjekke full likhet mot `RANGERT_FELT`, slik kontrakten faktisk
  er etter denne storyen.
- Den eksisterende komponenttesten «viser hver kandidats ulempepoeng og
  fordeling, også null» (story 4.7, `kandidatflate.test.tsx`) hadde Jonas'
  gamle, syntetiske ulempetall (14,6 p) hardkodet. Fordi denne storyen
  oppgraderer den delte `JONAS`-fixturen til #4127s faktiske fasit (40 p, for
  å kunne gjenbrukes i den nye avviksnotat-sammenligningen mot Mette), ble
  testens forventede tekst oppdatert til de nye, fortsatt interne konsistente
  tallene. Dette er ikke en endring i produksjonskoden eller i fasiten for
  #4127 (AV-07) — bare i en frontend-testfixtur som aldri hevdet å representere
  backendens fasit før nå.
- `kompetansenivå`-importen i `main.py` ble fjernet: `godkjenningsgrunnlag()`
  bruker den ikke lenger etter omskrivingen til `rangert_ut`, som allerede
  henter kompetansenivå fra `RangertKandidat`.

## Kvalitetssikring

- Backend: `.venv\Scripts\python -m pytest` — 675 bestått (inkludert
  import-linter-kontrakten i `test_arkitektur.py`).
- Frontend: `npm.cmd run build` (typesjekk av kode og tester, samt bygg) og
  `npm.cmd run test` — 52 `node --test` og 41 Vitest-komponenttester bestått
  (37 eksisterende + 4 nye for denne storyen).
- Ingen test gjør nettverkskall eller bruker en ekte KI-nøkkel.

## Uavhengig kodegjennomgang og nettleserkontroll (2026-11-17–18)

Etter leveransen over gikk tre uavhengige agenter (blind-hunter, edge-case-hunter,
verification-gap, alle Sonnet) gjennom koden uten å ha sett implementeringen. 10 funn,
alle ført i spesifikasjonens Review Triage Log: 5 rettet (avviksnotatets overskrift
manglet et semantisk `<h2>`, to dokumenter manglet testtall og beslutnings-ID-er, en
testfikstur hadde uensartet innrykk, og «høy belastning»-varselet ble ikke testet inne i
selve avviksnotatet), 4 avvist med begrunnelse. `pytest` 675, 52 `node --test` og 41
Vitest-komponenttester (uendret i antall etter rettingene) og build bestod etter dette.

Mithad Kuduz gjorde nettleserkontrollen 2026-11-18 mot en midlertidig testdatabase uten
lagrede tolkninger, ikke `backend/turnushjelperen.db`. Alle fem punktene i sjekklisten
(1080/960/680/1600 px, tastatur og fokus, farger, større skrift, ekte backend mot #4127
med Jonas og Mette) besto. Et grunnlag med lagret tolkning inngikk ikke i kontrollen.

## Åpne punkter

- Et grunnlag med lagret tolkning er ikke kontrollert manuelt i nettleser, bare i
  API-testen `test_lagret_tolkning_endrer_topprangert_uten_live_kall`.
- Koden er gjennomgått av uavhengige agenter, men ikke av et annet gruppemedlem ennå.
  Storyen står som `review` i `sprint-status.yaml` til det er gjort.
