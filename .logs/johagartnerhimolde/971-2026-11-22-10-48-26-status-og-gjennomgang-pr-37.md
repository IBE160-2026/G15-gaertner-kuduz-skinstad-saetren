# Status etter PR 35 og 36, og gjennomgang av PR 37

## 2026-11-22 kl. 10:48 — johagartnerHiMolde

### Oppgave
Hente siste oppdateringer og få en gjennomgang av dem. Deretter rette status som ikke stemte etter PR #35 og #36, kryss av løste punkter, ta designavklaringen for 4.6 og starte gjennomgangen av PR #37 (story 5.4, Kim).

### Plan
- Oppdatere `main` (43 nye commiter), lese endringene og kjøre backendtestene.
- Rette status i sprintstatus, vurderingsmatrise, referat og AGENTS.md, og synkronisere storyfiguren.
- `bmad-review` på PR #37 mot flettebasen `378d8aa`. Diffen er staget uten `.logs/`. Tre linser kjørte i hver sin underagent: adversarial, edge-case-hunter og verification-gap.

### Resultat
- **Backendtester på `main`:** 792 av 792 bestod (`1e1a57b`).
- **Status (`a7b0082`):**
  - Story 5.6 er satt til `done` i `sprint-status.yaml`. PR #36 ble merget av Kim i `1e1a57b`. Storyfiguren er synkronisert, og `--sjekk` bestod.
  - Vurderingsmatrisen sier nå at 5.3 (PR #35, `8cdf08b`) og 5.6 (PR #36) er ferdige.
  - AGENTS.md nevner 5.3 og 5.6 som ferdige.
- **Designavklaring for 4.6:** Johannes godtar at totalscoren brytes over to linjer når det trengs, og det rettes senere ved behov. Avklaringen er ført i referatet §11 og vurderingsmatrisen. 4.6 står fortsatt som `review`, fordi den manuelle kontrollen med rullefelt gjenstår.
- **Avkryssede punkter i `issues.md`:** fire punkter, om PR #32, designavklaringen, plassen til begrunnelsesknappen i 5.3 og PR #34.
- **PR #37:**
  - **CI:** alle sju sjekker var grønne.
  - **Konflikt:** PR-en har flettekonflikt mot `main` i `sprint-status.yaml` og `vurderingsmatrise.md`. Koden fletter rent.
  - **Fletteprøve:** verification-gap-linsen flettet PR-en med `origin/main` i et isolert worktree. Der bestod 825 av 825 backendtester, og på PR-branchen alene 750 av 750.
  - **Mutasjoner:** alle tre kodeendringene i `openrouter.py` ble prøvd med mutasjoner, og testene fanget dem. Unntaket er 19-sifret-grensen i `_venting_429`, der grensen 399 også besto alle tester.
  - **Funn:** 27 til sammen (edge-case 9, adversarial 14, verification-gap 4). Rådata ligger i scratchpad og er ikke lagt i repoet.
  - **Viktigste funn, sett av to eller tre linser:**
    1. Den nye `except OSError` bør bruke `nettverksårsak(feil)` fra `main` når konflikten løses.
    2. Vurderingsmatrisen overdriver funnet om transporttidsavbrudd. Det gjaldt bare injiserte transporter, ikke `urllib_transport`.
    3. Påstanden om at «forhåndsgenererte testdata bruker den samme faktakontrollen» prøver bare en klasse definert i testen.
    4. Grensen på 19 sifre er ikke testet.
    5. `>=` endrer også tolkningen fra 5.1 (AV-19). Det er ikke nevnt i commiten og ikke testet for `tolk`.
    6. Tolk-veien oversetter ikke `OSError`.
  - Ingen funn viser feil i produksjonsveien med `urllib_transport`.
- **Ikke gjort:** Ingen kommentar er postet på PR #37, og ingen endringer er gjort på branchen.

### Åpne punkter
- PR #37: Johannes vurderer funnene og gir Kim tilbakemelding på PR-en. De anbefalte rettingene før merge er konfliktløsningen med `nettverksårsak`, ordlyden i matrisen og KI-loggen, en test av 20-sifret reset og en omtale av at `>=` også gjelder `tolk`.
