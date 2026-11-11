# Story 2.2: kolliderende vakt

## 2026-11-11 kl. 16:29 — johagartnerHiMolde

### Oppgave
`/bmad-build story 2.2`, med ønske om å lage branch og pushe den tidlig, slik at resten av gruppa ser at Johannes jobber med storyen. Storyen skal filtrere bort Kandidater som allerede har en vakt som overlapper Vakten som skal bemannes (FR3).

### Plan
- Branch `story-2.2-kolliderende-vakt` fra `main` (0fc10f0) og push med en gang, før noe arbeid.
- Modellvalg etter `docs/modellvalg-stories.md`: Sonnet for 2.2. Økten kjørte først på Opus, og Johannes byttet med `/model sonnet` før steg 01.
- `bmad-build` med underagenter: epic-konteksten ble kompilert på nytt (utdatert), spec skrevet og godkjent, implementering av én agent, uavhengig gjennomgang av tre agenter (blind-hunter, edge-case-hunter, verification-gap) som ikke hadde sett implementeringen.
- Spec: `_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md`.

### Resultat
- Branchen er pushet. Commit `605c52e` på branchen inneholder hele storyen og er ikke pushet.
- Ny regel `domene/regelmotor/kolliderende_vakt.py` (årsak «kolliderende vakt») som nummer to i `REGLER`. Halvåpne intervall, sammenlignet i UTC. `Kandidat.vakter` og `Tidsrom` i `domene/typer.py`. `kandidatgrunnlag.py` henter tildelte vakter i én spørring. Ugyldig vakt hos en Kandidat gir datafeil (P-08).
- Fasiten: #4127 gir 9 gyldige og #4189 19 (var 16 og 21). Fasiten er ikke endret (AV-07), bare forventningen i `test_kandidater.py`.
- Frontend: bare merknadsteksten er endret. README, vurderingsmatrise og KI-logg `docs/ki-logg/2026-11-11-kolliderende-vakt.md` er oppdatert.
- Verifisert: `pytest` 273 bestått, `npm.cmd run build` og `npm.cmd test` (26) består. Alle rader i I/O-matrisen er dekket av tester som kjørte.
- Gjennomgangen ga 15 funn. Tre ble patchet: UTC-omregningen var ikke vernet av noen test (reviewer fjernet `astimezone(UTC)` og 120 tester var grønne, så to nye tester med fold=0/fold=1 i timen som går to ganger ble lagt til, og mutasjonen er dokumentert), determinismetestene så ikke `Kandidat.vakter` (`compare=False`), og et misvisende testnavn. Ett ble utsatt (AGENTS.md er utdatert) til `deferred-work.md`. Resten er avvist med begrunnelse i Review Triage Log.
- Feil fra min side: diff-filen gjennomgangsagentene leste, hadde git-advarsler flettet inn fordi stderr gikk til filen. Det gjaldt bare den kopien, ikke koden.
- `epic-2-context.md` er kompilert på nytt fordi ARCHITECTURE-SPINE.md og addendum.md var nyere. Sprint-status: 2.2 står som `review`.

### Åpne punkter
- Nettleserkontrollen i spec-ens Verification gjenstår: logg inn, velg #4127 og #4189 og kontroller at listene har 9 og 19 kandidater. Implementeringsagenten fikk ikke starte utviklingsserverne.
- Commit `605c52e` er ikke pushet, og det finnes ingen PR. Branch eller PR er Johannes' valg (AGENTS.md Policy).
- AGENTS.md sier at regelmotoren bare har kompetanse-minstekrav (utsatt, ført i `deferred-work.md`).

## 2026-11-11 kl. 16:39 — johagartnerHiMolde

### Oppgave
`/bmad-review` av arbeidet Sonnet 5.5 gjorde på story 2.2, kjørt etter `/model` tilbake til Opus 5.5, som en andre og uavhengig gjennomgang.

### Plan
- Diffen for branchen mot `main` (0fc10f0..HEAD) og commit-meldingene ble lagt som filer.
- Tre Opus-linser kjørte parallelt uten å ha sett den forrige gjennomgangen: adversarial, edge-case-hunter (med commit-meldingene) og verification-gap.

### Resultat
- 21 funn: 16 fra adversarial, 3 fra edge-case og 2 fra verification-gap. Ingenting er rettet. Arbeidstreet er rent etter mutasjonene som linsene gjorde.
- Viktigste funn:
  - **Ingen test sikrer «uavhengig av periode».** VG la inn `VaktRad.start >= periode_start` i adapteren, og alle 273 tester var fortsatt grønne.
  - **Ugyldig tildelt vakt er ikke testet ende til ende.** Det finnes ingen API-test for dette, bare domenetester.
  - **Kollisjon med egen vakt ved Godkjenning.** Når Epic 3 kjører reglene på nytt ved Godkjenning og Vakten har fått `tildelt_ansatt_id`, kolliderer Kandidaten med sin egen vakt.
  - **Dokumentasjonen spriker.**
    - Vurderingsmatrisen og KI-loggen sier at gjennomgangen gjenstår.
    - Spec-en står som `done`, mens sprint-status sier `review`.
    - Mutasjonstallet 13 stemmer ikke lenger (nå 14).
    - Testtallet er 271 i triage og 273 i dokumentasjonen.
  - **`epic-2-context.md` er delvis utdatert.** Den beskriver tilstanden før 2.2, og omkompileringen fjernet noen punkter uten at det er begrunnet.
  - **Merknaden bruker et annet navn på regelen.** Den sier «kompetanse», mens årsaken heter «kompetanse-minstekrav».
  - **Gjentatte funn.** Datafeil på all historikk, spørringen uten avgrensning og datafeilgrunnen med listeposisjon ble avvist i den første gjennomgangen og kom opp igjen.

### Åpne punkter
- Johannes velger hvilke funn fra Opus-gjennomgangen som skal rettes før PR. Funnlisten står i chat-rapporten, og hovedpunktene står over.
