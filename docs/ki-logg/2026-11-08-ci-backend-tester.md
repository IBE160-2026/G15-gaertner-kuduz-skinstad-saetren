# Backend- og frontendtestene i CI

Dato: 2026-11-08. Branch: `ci-backend-tester` (PR #9). Agent: Claude Code (Claude Opus 5.5).
Utført for Johannes W. Gaertner.

Dette er agentens egenrapportering. Et gruppemedlem må lese den gjennom og korrigere.

## Oppgaven

Mithad Kuduz foreslo i gjennomgangen av PR #6 at CI også kjører backend-testene
(`pytest`). Johannes ba først om en vurdering av ulempene, med en skill. Ut fra den ba han
om implementering i egen branch, og om en PR som forklarer hva CI er og hvorfor det er
god praksis, vurdert mot sensorveiledningen.

## Prompten

Johannes W. Gaertner, ordrett, i rekkefølge:

> er det noen ulemper med å la CI også kjøre pytest? Bruk en relevant skill for å undersøke dette

> Kjør metode 1, 2 og 5

> Mottatt. Tidsbruken på 1-2 minutter, vil det bli med hver git-operasjon? Punktet om Python-versjonsoppdateringer vil helt riktig sannsynligvis forrårsake en krasj over tid, MEN: Dette er en del av normalt vedlikehold, og som du sier er fixen enkel. Kan vi ikke også si at å  tvinge "gammel" versjonskjøring også er en risiko over tid? Vi må kunne legge opp til at systemet vedlikeholdes over tid.

> Apply. Gi meg en anbefaling om dette bør på egen branch eller om vi kan implementere det rett i main

> Bra, jeg støtter vurderingen om egen branch. Jeg vil at du starter implementeringen i en egen branch. I PR'en som blir tilhørende denne: Skriv litt om hva en CI er, og hvorfor vi oppretter dette med CI-testing, at det er bra utviklerpraksis. Vurder dette også opp i mot sensorveiledningen og si noen ord om det.

## Vurderingen før koden

Agenten brukte `bmad-advanced-elicitation`. Johannes valgte pre-mortem, red team og
feilmodusanalyse. Vurderingen bygde på disse fakta fra repoet:

- Workflowen for speilingen bruker bare standardbiblioteket.
- Backend har sju eksakt låste pakker.
- 112 tester tar 29–42 s lokalt.
- Testene bruker `tmp_path`, `monkeypatch.setenv` og eksplisitt `Europe/Oslo`, og ingen nettverkskall.
- Lokalt finnes `__pycache__` for både cpython-312 og cpython-315.
- `main` ser ikke ut til å ha branchebeskyttelse (API-et svarte 404).

Funnene:

- **Største fordel:** CI blir den eneste kjøringen av backend utenfor Windows. Fysisk test på macOS/Linux er strøket (OP-05).
- **Reelle risikoer:**
  - Python-versjonen endrer seg mens pakkene er eksakt låst.
  - Noen legger `OPENROUTER_API_KEY` inn i CI når KI-adapteren kommer (story 5.1). Det gir betalte kall ved hver push, og grensen på 20 kall per minutt treffes.
- **Mindre risikoer:**
  - PyPI kan være nede.
  - Grønn CI kan bli forvekslet med gjennomgått kode.
  - Hvis `pytest` lå i samme jobb som speilingen, ville en installasjonsfeil skjule speilingsresultatet.

## Hva som ble rettet, og hvorfor

- **Python-versjonen.** Agenten foreslo å låse CI til Python 3.12. Johannes påpekte at det også er en risiko over tid: en ren lås skjuler versjonsdrift, og den kommer da samlet senere. Systemet skal kunne vedlikeholdes. Agenten endret forslaget til en matrise med `3.12` (laveste versjon vi lover i `requires-python`) og `3.x` (nyeste stabile). Agenten frarådet `continue-on-error` på `3.x`, fordi det gir rød CI som ingen ser på.
- **Tidsbruken.** Agenten skrev «1–2 minutter» uten å si at det bare gjelder ved push, og at kjøringen går ved siden av det man gjør. Det ble presisert etter spørsmålet fra Johannes.
- **README ble ikke endret.** PR #8 (story 1.4, Kim) skriver om Tester-avsnittet i README. En linje om CI der ville gitt konflikt. Den legges inn etter at PR #8 er merget.

## Hva modellen leverte

- `.github/workflows/backend-tester.yml`:
  - En egen workflow, ved hver push og ved manuell start.
  - Matrisen `["3.12", "3.x"]` med `fail-fast: false`, så begge resultatene vises.
  - `actions/setup-python@v5` med `cache: pip` for `backend/requirements*.txt`.
  - `pip install -r requirements-dev.txt`, deretter `python -m pytest` i `backend/`.
  - Bare `contents: read` og ingen secrets.
- `AGENTS.md`:
  - Ny regel under Policy: CI får aldri `OPENROUTER_API_KEY` eller andre hemmeligheter.
  - CI-avsnittet beskriver begge workflowene og hva CI ikke dekker.
- `docs/beslutninger/avklaringspunkter.md`: ny oppføring i §11, merket som foreslått.
- `docs/emne/vurderingsmatrise.md`: nytt avsnitt om CI med lenker til kjøringene.

## Kvalitetssikring

- **Lokalt:** `pytest` ga 112 av 112 på Python 3.12.5 (Windows). Et venv med Python 3.15.2 kunne ikke lages lokalt, fordi `ensurepip` feilet. 3.x er derfor bare kontrollert i CI.
- **CI på GitHub:** Den første kjøringen, [42477253888](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42477253888) på `89cfee4`, var grønn. Runneren var Ubuntu 26.04.

  | Jobb | Python | Resultat | Pytest | Hele jobben |
  |---|---|---|---:|---:|
  | `pytest (3.12)` | 3.12.16 | 112 av 112 | 17,8 s | 37 s |
  | `pytest (3.x)` | 3.15.2 | 112 av 112 | 10,4 s | 25 s |

  Speilingstesten kjørte ved siden av og var også grønn (42477253789).
- **Linux:** UTF-8-testen i `test_testdata.py` og testene som starter underprosesser, besto. Det var det eneste ukjente i feilmodusanalysen. Det første beviset på at backend virker utenfor Windows er dermed på plass.
- **Ikke kontrollert:** Ingen test ble gjort rød med vilje for å se at CI blir rød. Det ville gitt en rød kjøring på branchen. `pytest` avslutter med en annen exit-kode enn 0 når en test feiler, og den koden gjør at jobben feiler.
- **Ressurser:** Ingen nettverkskall utenom installasjon fra PyPI, og ingen modellkall eller tokens. Repoet er offentlig, så GitHub Actions er gratis.

## Utvidelse: frontend i CI, og rød CI blokkerer ikke merge

### Prompten

Johannes W. Gaertner, ordrett, etter at PR #9 var åpnet:

> Supert. Rød CI skal ikke blokkere merge, ellers er alt OK. Anbefaler at CI også kjører frontendtestene, med mindre det tar veldig lang tid.

### Hva modellen leverte

- **Måling før koden.** Frontendmappen fra PR #8 (story 1.4, med `npm run test`) ble pakket ut med `git archive` i en midlertidig mappe, slik at den lokale `node_modules` ikke ble rørt. Lokalt tok `npm ci` 9 s, `npm run build` 2 s og `npm run test` 1 s (3 av 3). Et første forsøk med `git worktree` feilet på Windows med «Filename too long» og ble ryddet bort.
- **`.github/workflows/frontend-tester.yml`:**
  - En egen workflow med samme oppbygging som for backend.
  - Matrisen `["20.19", "lts/*"]`. 20.19 er laveste versjon README lover.
  - `actions/setup-node@v4` med `cache: npm`.
  - `npm ci`, `npm run build` og `npm run test --if-present`.
- **`AGENTS.md` og §11:**
  - Begge beskriver nå tre workflows.
  - Begge sier at rød CI ikke blokkerer merge, og at det er et valg.

### Hva som ble rettet, og hvorfor

- **`latest` ga en alfaversjon.** Matrisen brukte først `node-version: "latest"`. I den første kjøringen, [42478122926](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42478122926), ga det `v27.0.0-alpha.0.0.0`. Jobben var grønn, men hensikten var nyeste *stabile*, ikke en forhåndsversjon. Feilen ble funnet ved å lese `node --version` i loggen, ikke fordi CI ble rød. Rettet til `lts/*` i `9f404bc`.
- **`--if-present` på `npm run test`.** Testskriptet finnes bare på branchen til PR #8. Uten flagget ville frontendjobben vært rød på `main` til PR #8 er merget. Ulempen er at et manglende skript hoppes over i stillhet. Derfor sier kommentaren i workflowen at flagget skal fjernes når PR #8 er merget, og det er ført som åpent punkt.

### Kvalitetssikring

- **CI etter rettingen:** [42478187812](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42478187812) på `9f404bc` var grønn.

  | Jobb | Node | `npm ci` og `npm run build` | Hele jobben |
  |---|---|---|---:|
  | `npm (20.19)` | 20.19.6 | grønn | 10 s |
  | `npm (lts/*)` | 26.13.0 | grønn | 15 s |

  `npm run test` ble hoppet over, som forventet, fordi skriptet ikke finnes ennå.
- **Ikke kontrollert i CI:** At frontendtestene fra PR #8 består på Linux. Det skjer først når PR #8 og denne PR-en begge er merget. Lokalt på Windows besto de (3 av 3, Node 26.7.0).
- **Observasjon, ikke endret:** README lover Node 20.19 eller nyere. Ifølge Nodes utgivelsesplan gikk Node 20 ut av vedlikehold i april 2026. Om laveste versjon skal heves, avgjør gruppa.
