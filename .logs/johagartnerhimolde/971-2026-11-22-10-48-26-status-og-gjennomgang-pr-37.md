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
- ~~PR #37: Johannes vurderer funnene og gir Kim tilbakemelding.~~ Løst samme dag, se oppfølgingen nedenfor.

### Oppfølging samme dag: rettinger på PR-branchen
Johannes ba om å rette punkt 1–5 («Gjør nødvendige utbedringer/tilpasninger til punkt 1-5»).

- **Fletting (`4701c4e`):** `main` er flettet inn i `story/5-4-reservetekst-naar-ki-forklaringen-feiler`. Konfliktene i `sprint-status.yaml` og `vurderingsmatrise.md` er løst, og storyfiguren stemmer.
- **Rettinger (`b947014`):**
  - `nettverksårsak(feil)` er brukt i den nye `except OSError`, med en API-test for direkte sertifikatfeil.
  - Ordlyden om transportfunnet er rettet i matrisen.
  - Påstanden om forhåndsgenererte testdata er avgrenset i KI-loggen og spesifikasjonen, og ført i `deferred-work.md` for 5.7.
  - Nye tester for reset med 19 og 20 sifre, og for fristgrensen i `tolk` (89 og 90 s).
  - Fem nye rader i spesifikasjonens Review Triage Log, og en ny KI-logg: `docs/ki-logg/2026-11-22-oppfolging-pr-37.md`.
- **Kvalitetssikring:**
  - Hver av de tre kodeendringene ble tilbakestilt, og testene ble røde for alle tre.
  - 830 av 830 backendtester bestod etter flettingen.
  - Frontend er ikke endret av PR-oppfølgingen eller av `main` siden flettebasen, så frontendtestene ble ikke kjørt på nytt.
- **Ikke pushet.** Branchen inneholder også de to lokale commitene på `main` (`a7b0082`, `efbc60a`). `main` bør derfor pushes før branchen.

### Kommentar, godkjenning og fletting
- **Push:** `main` ble pushet først, deretter PR-branchen. Ingen andre hadde pushet i mellomtiden.
- **Kommentar på PR #37:** gjennomgangen, de fem rettingene, kontrollen og funnene som ikke ble rettet ([kommentaren](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/37#issuecomment-7077582254)). Kim er bedt om å se over `b947014`.
- **Godkjenning og fletting:** alle sju CI-sjekker var grønne på `b947014`, også frontend på Node 22.12 og LTS. Johannes godkjente, og PR-en ble flettet i `4bca0ae`.
- **Status (`33d7f85`):** story 5.4 er satt til `done` i `sprint-status.yaml`, storyfiguren, AGENTS.md og vurderingsmatrisen.
- **Branchen** `story/5-4-reservetekst-naar-ki-forklaringen-feiler` er ikke slettet.

### Åpne punkter etter flettingen
- Kim ser over Johannes' rettinger i `b947014` i ettertid. Det gjelder særlig endringene i KI-loggen og matriseteksten. Innvendinger rettes på `main`.
