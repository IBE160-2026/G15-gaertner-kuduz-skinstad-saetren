# Story 5.2: Rangeringen bruker tolkede preferanser

## 2026-11-20 kl. 17:43 — Mithad Kuduz

### Oppgave

Etter at PR #32 (4.6) og PR #33 (5.1 «Prøv igjen») var godkjent og merget, spurte
brukeren om en ny story å ta. Jeg sjekket sprint-status: Epic 4 er ferdig bortsett fra
4.6 (venter på Johannes' egne åpne punkter), og 5.1 er ferdig. Bare 5.2 og 5.3 var reelle
kandidater; brukeren valgte 5.2 (Rangeringen bruker tolkede preferanser) framfor 5.3
(Avveining per kandidat, større KI-forklaringsarbeid). Registrert som OP-18, branch
`story/5-2-rangeringen-bruker-tolkede-preferanser` etter brukerens valg av branch+PR
(fremfor rett på main).

### Plan

- `bmad-build` steg 1: `epic-5-context.md` var utdatert (epics.md og
  ARCHITECTURE-SPINE.md endret siden forrige kompilering) og ble bygget på nytt med en
  underagent.
- Steg 2: undersøkte koden før jeg bestemte tilnærming. `ranger()` tar allerede
  `tolkede`/`feilede` som vanlig input (AC1), en eksisterende determinismetest dekker
  allerede AC3, og fire eksisterende tester fra story 4.5/5.1 dekker allerede AC4. Bare
  AC2 (preferanse alene avgjør mellom ellers like kandidater) manglet en dedikert test.
  Ingen intent-gap, ingen irreversibel endring, liten footprint → oneshot-rute.
- Implementerte selv i denne økten (ikke en separat underagent), med en blind-gjennomgang
  (Opus 5.5) etter anbefalingen i `docs/modellvalg-stories.md`.

### Resultat

- **Ny test:** `test_preferanse_alene_avgjør_rangeringen_når_alt_annet_er_likt` i
  `backend/tester/regelmotor/test_rangering.py`. Ingen produksjonskode endret.
- **Gjennomgang:** 13 funn fra Opus. Rettet: testens id-valg (rekkefølgen beviste ikke
  kravet alene — rettet), en redundant dobbel `ranger()`-kalling, tre feil/ufullstendige
  testsiteringer i spesifikasjonens Implementation Notes (AC1/AC3/AC4), og en betydelig
  regresjon i den regenererte `epic-5-context.md` som hadde mistet flere bindende
  detaljer fra forrige versjon (eierskapsregel, `GRUNNLAGSTABELLER`, kildelinjetekster,
  `ki_kilde`-verdier, m.m.) — alt ført tilbake. Avvist: utvidelse av AC2-testen til flere
  tolkestatuser (allerede dekket av `test_alle_fire_tolkestatuser`), og «usitert»-funnet
  om to DemoKiAdapter/KI-kall-påstander (begge sporet direkte til AD-6 og epics.md). Se
  spesifikasjonens Review Triage Log for alle 13.
- **Dokumentasjon oppdatert:** `docs/testing.md`, `docs/emne/vurderingsmatrise.md`,
  `AGENTS.md` (ferdigliste + kort forklaring), `sprint-status.yaml` (5.2 → `review`),
  storyfiguren regenerert. KI-logg:
  `docs/ki-logg/2026-11-20-rangering-tolkede-preferanser.md`.
- **Kvalitetssikring:** 686 backendtester (inkludert den nye), frontendbygget, 52
  modultester og 48 komponenttester (frontend urørt) bestod. Testen vist å kunne feile
  ved en midlertidig mutasjon av `totalscore()` (fjernet `preferansevekt`-leddet); koden
  ble tilbakestilt (`git diff` tomt etterpå).
- I samme runde rettet jeg også en stale setning i `docs/emne/vurderingsmatrise.md`s
  4.6-avsnitt («godkjenning gjenstår», selv om jeg allerede hadde godkjent og merget PR
  #32 i forrige økt).

### Åpne punkter

- PR for `story/5-2-rangeringen-bruker-tolkede-preferanser` er ikke opprettet ennå —
  gjenstår å pushe og åpne PR for gjennomgang fra et gruppemedlem.

## 2026-11-20 kl. 19:28 — Mithad Kuduz

### Oppgave

Pushet branchen og opprettet PR #34. Johannes gjennomgikk den samme dag (`bmad-review`
med Opus) og pushet tre rettekommiter direkte til branchen. Gikk gjennom alle tre og
verifiserte uavhengig før jeg fortsatte.

### Plan

- Leste alle tre commit-meldingene i sin helhet, ikke bare diff-stat.
- Sammenlignet den nye AC2-testen og de to nye API-testene mot koden selv.
- Kjørte `pytest` og `npm.cmd run build`/`test` på nytt selv, for å bekrefte
  Johannes' tall uavhengig av hans egen kjøring.

### Resultat

- **Funnene er reelle og rettingene er riktige.** Den viktigste: med bare to kandidater
  ga min–maks flat 50/50, så testen min kunne ikke skille en vektet preferanse fra et
  rent tiebreak — en mutasjon som gjorde preferansen til bare et tiebreak, besto hele
  `tester/regelmotor`. Rettet med en tredje kandidat (ikke-flat min–maks) og en egen test
  som viser at preferansen veier tyngre enn en liten kostnadsforskjell. En annen
  mutasjon viste at testen ikke skilte en reell nøytral tolkning fra reserveveien
  (venter/feilet, som også gir 50 poeng) — rettet med eksplisitt sjekk av tolkestatus.
  To nye API-tester lukker reelle hull: at rutelaget (ikke bare domenekjernen) aldri
  kaller KI (fant et konkret scenario som ikke var dekket før), og at «Prøv igjen» etter
  endelig feil beregner rangeringen på nytt i backend, ikke bare i en frontendtest med
  stubbet fetch.
- **`epic-5-context.md`:** Johannes fant at planverket knapt var endret siden filen sist
  ble kompilert (bare én statuslinje), så regenereringen min var unødvendig og hadde i
  tillegg fortsatt mistet rundt 15 bindende detaljer selv etter min egen rettingsrunde.
  Løsningen hans var enklere og tryggere enn min: tilbakestill til versjonen på `main`,
  og legg bare til sju kildebelagte setninger. Jeg sammenlignet den nye fila linje for
  linje mot både forrige versjon og min egen — alt stemmer, ingenting mangler.
  **Lærdom:** når en eksisterende, committet kontekstfil bare trenger småoppdateringer,
  er et avgrenset tillegg tryggere enn en full regenerering, selv med en etterfølgende
  gjennomgang.
- Verifiserte selv: 690 backendtester, frontendbygget, 52 modultester og 48
  komponenttester bestod — samme tall som Johannes oppga.
- Ingen uenighet med noen av rettingene. Ingenting tilbakeført eller omgjort.

### Åpne punkter

- Formell godkjenning og merge av PR #34 gjenstår, fra Johannes eller et annet
  gruppemedlem (ikke meg selv, siden jeg er forfatteren).

## 2026-11-20 kl. 20:26 — Mithad Kuduz

### Oppgave

Johannes meldte (gjennom et nummerert funn, «punkt 4», fra sin egen PR-gjennomgang)
tre feil i min egen del av KI-loggen for story 5.2. Jeg verifiserte alle tre mot
kildene før jeg rettet.

### Plan

- Sjekket `docs/ki-logg/README.md` for kravet om ordrett prompt.
- Sjekket min egen OP-18-oppføring i `avklaringspunkter.md` og AGENTS.md Policy for
  branch/PR, for å bekrefte at «gruppen hadde godkjent» var feil.
- Leste min egen logg linje for linje for å bekrefte miskategoriseringen.

### Resultat

- Alle tre funn var reelle og konkret kildebelagt:
  1. Prompten min var bare gjenfortalt, ikke ordrett — README.md krever ordrett.
  2. Loggen påsto et gruppevedtak om branch+PR som ikke finnes. OP-18 er en
     ansvarsmelding (min egen tekst i avklaringspunktene sier det selv), og
     branch/PR er et valg den enkelte gjør (Policy). Jeg valgte selv.
  3. Et avvist funn (DemoKiAdapter/«ett KI-kall per vakt») sto feilaktig under
     «Disse ble rettet».
- Rettet alle tre i `docs/ki-logg/2026-11-20-rangering-tolkede-preferanser.md`,
  committet `3396279`.
- **Lærdom:** jeg skrev selv denne KI-loggen uten å lese den kritisk mot
  README-kravet og mine egne tidligere notater før commit. Loggens formål er
  nettopp å fange denne typen glipp — jeg burde ha gjort det selv, ikke bare
  stolt på at innholdet var riktig fordi jeg skrev det.

### Åpne punkter

- Formell godkjenning og merge av PR #34 gjenstår.
