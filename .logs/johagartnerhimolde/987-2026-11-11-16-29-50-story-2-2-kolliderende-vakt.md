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

## 2026-11-11 kl. 16:49 — johagartnerHiMolde

### Oppgave
Rette det som burde rettes etter Opus-gjennomgangen, forklare valget i A5, skrive PR-en og merge når et gruppemedlem har godkjent den.

### Plan
- Rette VG1, VG2, EC2, EC3 og A1, A2 og A13, kontrollere de nye testene med mutasjon og kjøre full verifisering.
- Rette ikke EC1, fordi den ikke kan nås i dag. Den er utsatt til story 3.2. A3 avvist, fordi det er samme mønster som i 2.1.
- Legge A5 fram for gruppa i PR-en.
- Vente på godkjenning i bakgrunnen og merge når den kommer.

### Resultat
- Commit `878a1a2` har to nye API-tester: egen vakt før periodestart som overlapper, og ugyldig tildelt vakt gir datafeil. Hver av dem er kontrollert med én mutasjon av adapteren, som ga én rød test.
- Testhjelperen `kandidat()` er rettet med `is None`.
- Mutasjonen til lukkede intervall er kjørt på nytt og gir 14 røde av 124.
- KI-loggen, vurderingsmatrisen og Review Triage Log i spec-en er oppdatert med andre gjennomgang. EC1 er ført i `deferred-work.md`.
- Verifisert: `pytest` gir 275 bestått, `npm.cmd run build` går gjennom, og `npm.cmd test` gir 26.
- PR #14 er opprettet: https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/14. A5 er lagt fram som valg mellom A (all historikk, slik det er nå) og B (vindu per regel), med anbefaling om å beholde A i 2.2 og vedta B før 2.3.
- En bakgrunnsjobb i denne økten sjekker PR-en hvert 5. minutt. Den virker bare så lenge økten er åpen.

### Åpne punkter
- Gruppa tar stilling til A5 (P-08: all historikk eller bare nødvendig grunnlag) før 2.3.
- Merge når PR #14 er godkjent: løs konflikter mot `main`, sett 2.2 til `done` i sprint-status og vurderingsmatrisen, og merge.
- Nettleserkontrollen av #4127 og #4189 gjenstår.

## 2026-11-11 kl. 16:59 — johagartnerHiMolde

### Oppgave
Johannes meldte at nettleserkontrollen er gjort og godkjent. Bakgrunnsjobben for merge skulle fjernes, og PR-en skulle si at den som godkjenner, merger og løser konflikter. Gruppa vedtok B i A5, og løsningen bygges i 2.3. Alt skulle pushes.

### Plan
- Stoppe bakgrunnsjobben og føre vedtaket i referatet, Epic 2-konteksten og `deferred-work.md`.
- Oppdatere KI-loggen, vurderingsmatrisen, spec-en og PR-beskrivelsen, og pushe.

### Resultat
- Bakgrunnsjobben er stoppet. PR #14 har fått et avsnitt om merge og et om vedtaket i A5, og nettleserkontrollen står som godkjent.
- Commit for vedtaket og nettleserkontrollen er laget: avklaringspunktene §11 og P-08-raden, `epic-2-context.md`, `deferred-work.md`, KI-loggen, vurderingsmatrisen og Implementation Notes i spec-en.
- Alt er pushet til `origin/story-2.2-kolliderende-vakt`.

### Åpne punkter
- Story 2.3 bygger vinduet per regel og avgrenser datafeilsjekken (vedtak A5, alternativ B).
