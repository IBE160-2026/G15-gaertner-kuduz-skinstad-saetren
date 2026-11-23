---
title: 'Story 5.8: Sensor kan kjøre live KI'
type: 'chore'
created: '2026-11-23'
status: 'done'
baseline_commit: '2d6f3791446fe3d2e71eb485186f2da36dcdf069'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sensor skal kunne kjøre appen med live KI etter README, uten å spørre gruppa. README forklarer i dag hvordan nøkkelen settes i terminalen, men ikke hvordan sensor ser at live KI faktisk er aktiv. En nøkkel lagt i `.env` eller satt i feil terminal gir stille demo-modus (AV-20). README sier heller ikke hva som skjer når kreditten er brukt opp. Gruppa mangler også en sjekkliste og en testet kommando for oppgavene ved innleveringen.

**Approach:** Utvid README-avsnittet «KI: demo-modus eller live» med hvordan sensor kontrollerer modusen, og hva oppbrukt kreditt eller en ugyldig nøkkel gir. Lag en sjekkliste i `docs/innlevering/` med en kryssplattform-kommando for nøkkelsjekk av git-historikken, sjekken fra en ren klone, et utkast til teksten om nøkkelen i innleveringen og oppryddingen etter sensur. Ingen kodeendring.

## Boundaries & Constraints

**Always:**
- Følg AV-20: nøkkelen settes som `OPENROUTER_API_KEY` i samme terminal som backend startes fra. Backend leser ikke `.env`.
- README skal bare love det koden og testene allerede dekker: 402/4xx gir `avveining_feilet` → reservetekst (`tester/api/test_avveining.py`), og tolkningen gir «kunne ikke tolkes» med 50 poeng (P-05).
- Kommandoer vises for både PowerShell og bash (AGENTS.md). Nøkkelsjekken skal være én git-kommando som virker likt i begge.
- Skriv på norsk bokmål og følg stilen i README: korte setninger, ingen gjentakelse av teknisk referanse.

**Never:**
- Ingen ekte nøkkel, nøkkelprefiks utover formatet `sk-or-v1-…` eller kredittbeløp i repoet.
- Ikke endre backend, frontendkode, `.env.example` eller eksisterende tester. Unntak (Ragnhild, 2026-11-23): én ny komponenttest for at appbaren ikke viser «Demo-modus» i live-modus.
- Ikke avgjør ÅB-8 (hvilken nøkkel sensor får). Sjekklisten viser begge utfallene.
- Ikke gjør innleveringsoppgavene selv. De er utsatt (`deferred-work.md`, 2026-11-23).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Live aktiv | Nøkkel satt i samme terminal | Ingen «Demo-modus» i appbaren; forklaringene merkes «KI-generert · openai/gpt-6-luna» | — |
| Nøkkel i `.env` eller annen terminal | Ingen nøkkel i backendens miljø | «Demo-modus» i appbaren; terminalen skriver `Preferansetolkning kjører i demo-modus: OPENROUTER_API_KEY er ikke satt.` | README forteller sensor å stoppe backend, sette nøkkelen i samme terminal og starte på nytt |
| Kreditt brukt opp eller ugyldig nøkkel | 402/401 fra OpenRouter | Ingen krasj; forklaringer viser «Reservetekst · KI-forklaring utilgjengelig», preferanser «Preferanse kunne ikke tolkes» | Rangering og godkjenning virker; sensor kan starte på nytt uten nøkkel for demo |
| Nøkkelsjekk, ren historikk | Ingen `sk-or-v1-` + 32 heksadesimale tegn i noen commit | Kommandoen skriver ingenting | — |
| Nøkkelsjekk, lekket nøkkel | En commit som legger til eller fjerner en slik nøkkel | Kommandoen viser commiten | Sjekklisten sier hva gruppa da gjør: bytt nøkkelen i OpenRouter med en gang |

</frozen-after-approval>

## Code Map

- `README.md` (linje 151–184, «KI: demo-modus eller live») -- utvid live-punktet. Steg 3 (linje 96–105) viser allerede demo-linjen i terminalen. Tabellen i «Konfigurasjon» står uendret.
- `frontend/src/tekster.ts` -- de nøyaktige UI-tekstene README siterer: `demoModus` «Demo-modus» (28), `kunne_ikke_tolkes` (151), `reserve` (163). Les dem; ikke endre.
- `backend/adaptere/api/main.py` `ki_fra_miljo()` (413–448) -- logglinjene som siteres; `demomodus = isinstance(ki, DemoOppslag)` (508) styrer appbar-taggen.
- `backend/adaptere/ki/openrouter.py` (~345) -- 402 og andre 4xx prøves ikke på nytt → `Tolkefeil("4xx")`.
- `docs/innlevering/til-sensor-innlogging.md` -- mønsteret for et sensorrettet utkast (statuslinje øverst, lenker til README-avsnitt).
- `docs/teknisk-referanse.md` («Hvilken modus backend starter i») -- lenk dit, ikke kopier tabellen.
- `docs/emne/vurderingsmatrise.md` (linje 10, 19, 24) -- oppdater status for 5.8 og lenk til sjekklisten fra «Ryddighet i repoet».
- `.gitignore` (47–48) ignorerer `.env` og `.env.*`. `git ls-files` sporer ingen `.env`.

## Tasks & Acceptance

**Execution:**
- [x] `README.md` -- i live-punktet: (1) start backend i samme terminal som nøkkelen; (2) kontroller at appbaren ikke viser «Demo-modus», og at terminalen ikke skriver demo-linjen; (3) en nøkkel i `.env` brukes ikke; (4) ved oppbrukt kreditt eller ugyldig nøkkel: reservetekst og «kunne ikke tolkes», ingen krasj, og hvordan sensor går tilbake til demo -- AV-20, AC i epics 5.8.
- [x] `docs/innlevering/sjekkliste-live-ki.md` (ny) -- statuslinje som i `til-sensor-innlogging.md`; seksjonene «Før innlevering» (ÅB-8-valget, nøkkelsjekken med kommandoen og hvor resultatet noteres, sjekk at `git ls-files` ikke sporer `.env`, test fra ren klone etter README i begge moduser), «I innleveringsteksten» (utkast med plassholder `<nøkkel settes inn ved innlevering>`, lenke til README-avsnittet) og «Etter sensur» (slett eller bytt nøkkelen, navngi ansvarlig). Avkrysningsbokser for gruppa.
- [x] Negativ kontroll av nøkkelsjekken -- kjør kommandoen i et midlertidig git-repo i scratchpad med en falsk nøkkel på riktig format, og vis at den treffer. Noter resultatet i Implementation Notes. Ikke commit testrepoet.
- [x] `docs/emne/vurderingsmatrise.md` -- 5.8 er implementert (README og sjekkliste), og innleveringsoppgavene gjenstår. Lenk sjekklisten fra «Ryddighet i repoet».
- [x] `frontend/tester/komponenter/avveining.test.tsx` -- ny test: med `demomodus: false` og et live-svar vises «KI-generert · <modell>», og appbaren har ikke «Demo-modus» -- dekker matriseraden «Live aktiv» (lagt til etter matrisekontrollen, se Spec Change Log).
- [x] `docs/ki-logg/2026-11-23-story-5-8-sensor-live-ki.md` -- KI-logg etter mønsteret i mappen: oppgave, prompt, hva som ble levert, rettelser og kvalitetssikring.

**Acceptance Criteria:**
- Gitt README alene, når en sensor uten forhåndskunnskap følger live-punktet, så vet sensor hvor nøkkelen settes, hvordan aktiv modus kontrolleres, og hva oppbrukt kreditt gir.
- Gitt sjekklisten, når gruppa forbereder innleveringen, så har hvert utsatt punkt fra `deferred-work.md` (5.8) en avkrysningsboks med ansvarlig-felt og en konkret handling.
- Gitt nøkkelsjekken, når den kjøres på repoet i dag, så gir den ingen treff, og den negative kontrollen viser at den treffer en nøkkel på riktig format.

## Implementation Notes

- README følger strukturen fra ryddingen `87db4d9` (Ragnhild avviste et første utkast med tre nye avsnitt i live-punktet): live-punktet fikk én setning om modussjekk og en lenke, og de to feiltilfellene står som «symptom: tiltak» under «Feilsøking».
- Nøkkelsjekk på repoet 2026-11-23 (`2d6f379` + arbeidstre): `git log --all --oneline -E -G "sk-or-v1-[0-9a-f]{32}"` ga ingen utskrift. `git ls-files | grep -i "\.env$"` ga ingen utskrift.
- Negativ kontroll i et midlertidig repo i scratchpad (ikke committet): commitene «lekker nøkkel» (`.env` med `sk-or-v1-` + 64 heksadesimale tegn) og «fjerner nøkkel» ble vist; «ren» og «falsk testnøkkel» (`sk-or-v1-fake-key-for-tests`) ble ikke vist.
- Funn utenfor omfanget: `docs/innlevering/til-sensor-innlogging.md` lenker til `README.md#2-last-testdata-og-noter-passordet`, men overskriften heter nå «2. Last testdata og velg passord». Ikke rettet her.

## Spec Change Log

- 2026-11-23 (matrisekontrollen i step-03): Raden «Live aktiv» var bare delvis dekket. Kildelinjen «KI-generert · <modell>» har komponenttester, men ingen test viste at appbaren er uten «Demo-modus» i live-modus. Det er signalet README ber sensor se etter. Ragnhild valgte å legge til én komponenttest, og «Never»-punktet om tester ble endret tilsvarende. Testen består (27 av 27 i `avveining.test.tsx`), og den ble rød da `Appbar.tsx` midlertidig ble tvunget til alltid å vise demomerket. Appbar-koden er tilbakestilt. Hele frontend: `npm run build` grønn, 52 modultester og 75 komponenttester bestått.

## Review Triage Log

Tre lag kjørt parallelt 2026-11-23 (Blind Hunter, Edge Case Hunter, Verification Gap Reviewer), alle på Opus. Funnene er kontrollert mot koden av orkestratoren; gjennomgåernes alvorlighetsgrad er ikke brukt.

| # | Funn (kilde) | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|
| 1 | «Ingen Demo-modus» betyr ikke live: ukjent `KI_MODUS`, ugyldige tegn i nøkkelen eller feil modellform gir `ki=None`, `demomodus=False` og ingen KI (Blind, Edge ×2) | medium | `ki_fra_miljo()` linje 430–446 returnerer `None` med loggen «Preferansetolkning er av: …»; `demomodus = isinstance(ki, DemoOppslag)` (508) blir `False`. Utkastet til innleveringstekst og sjekklistens live-steg bruker bare fraværet av merket. Innlimt nøkkel med feil tegn er et realistisk tilfelle. | patch |
| 2 | Etiketten «KI-generert · openai/gpt-6-luna» er feil hvis `OPENROUTER_MODEL` er satt (Edge) | low | Ekte, men sensor setter ikke modellen, og README sier at modellen er Luna. | avvist (lite sannsynlig) |
| 3 | `KI_MODUS=demo` igjen i miljøet gir demo selv med nøkkel (Blind, Edge) | low | Ekte, men sensor har ingen grunn til å sette `KI_MODUS`. | avvist (lite sannsynlig) |
| 4 | «Start backend i en ny terminal uten nøkkel» uten å stoppe den gamle først gir opptatt port (Blind, Edge) | low | Ekte: uvicorn på 8000 kjører fortsatt. Direkte retting av ordlyden. | patch |
| 5 | Permanent satt nøkkel (setx/profil) arves av ny terminal (Edge) | low | Ekte, men README setter nøkkelen bare for én terminal. | avvist (lite sannsynlig) |
| 6 | Nøkkelsjekken ser ikke GitHubs `refs/pull/*` eller slettede brancher (Blind, Edge) | medium | Ekte: `git fetch --all` henter ikke `refs/pull/*`, som GitHub beholder for alle 40 PR-ene. En nøkkel i en commit som senere ble fjernet fra en PR-branch, er offentlig, men usynlig for kommandoen. | patch |
| 7 | `-G` hopper over merge-differ og binærfiler (Edge) | low | Ekte, men gjelder bare en nøkkel som kom inn ved konfliktløsning. Rettingen er to flagg. | patch |
| 8 | Nøkkel i commitmelding blir ikke funnet (Edge) | low | Ekte. Rettingen er én kommando til med `--grep`. | patch |
| 9 | Varianter som `.env.local` eller en `.env` i historikken fanges ikke av `git ls-files`-sjekken (Blind, Edge) | false | `.gitignore` 47–48 ignorerer `.env` og `.env.*` i alle mapper, og nøkkelsjekken leter etter innholdet uansett filnavn. En variant kan bare spores med `git add -f`, og innholdet ville da gitt treff i sjekken. | avvist |
| 10 | Den nye testen kan bestå uten at innlogget del av appbaren er tegnet (Edge) | false | Testen venter på `t.kilde(modell)`, som bare vises etter innlogging, og den ble rød da merket ble tvunget på. | avvist |
| 11 | Live-punktet nevner ikke terminalsjekken som spec-oppgaven ber om (Edge) | low | Ekte avvik fra oppgaveteksten; demo-linjen står bare under «Feilsøking». Direkte retting. | patch |
| 12 | Den rene klone-testen krever ikke Windows (Blind) | low | OP-05: sensor har ikke Mac, og fysisk test skjer først og fremst på Windows. Direkte retting av ordlyden. | patch |
| 13 | ÅB-8 mangler grunnlag for å vurdere kreditt (Blind) | low | Ekte: sjekklisten sier ikke hvor mange kall én sensorkjøring gjør (19 ved oppstart pluss én per åpnet forklaring). Pris finnes ikke i repoet og legges ikke inn. | patch |
| 14 | Testtallene er uenige: matrisen sier 70 komponenttester, loggen 75 (Blind) | false | 75 er målt på denne branchen 2026-11-23 (`npm run test`). Tallet 70 i matrisen er eldre og fra før denne storyen. | avvist |
| 15 | Matrisen har fortsatt «Story 5.7–5.9» og «Tester for 5.7–5.9 når de bygges» (Blind) | low | Ekte. Direkte retting av 5.8-omtalen. | patch |
| 16 | `docs/testing.md` sier at testen «dekker det», men den dekker bare frontenddelen (Blind) | low | Ekte etter funn 1: merket alene viser ikke live. Ordlyden justeres sammen med funn 1. | patch |
| 17 | `docs/testing.md` siterer bare 402-testene for Avveining, ikke for tolkningen (Blind) | low | Ekte: `test_4xx_prøves_ikke_på_nytt` i `tester/ki/test_openrouter.py` (402 er med) dekker «kunne ikke tolkes». Direkte tillegg. | patch |
| 18 | De utsatte punktene har `source_spec: none` (Blind) | false | De ble ført i step-01, før spec-en fantes, med formatet arbeidsflyten krever der. Eksisterende oppføringer skal ikke endres. | avvist |
| 19 | Diffen mangler spec-en, og sesjonslogg mangler (Blind) | false | Spec-en holdes bevisst utenfor diffen til to av lagene. Sesjonsloggen skrives når storyen er presentert. | avvist |
| 20 | Utkastet til innleveringsteksten nevner ikke 19 kall ved oppstart eller `--reload` (Blind) | low | Sensor bruker ikke `--reload` (README steg 3), og README-avsnittet utkastet lenker til nevner allerede de 19 kallene. | avvist (lite sannsynlig) |
| — | Verification Gap Reviewer | — | Ingen hull funnet. | — |

## Design Notes

Nøkkelsjekken bruker `git log --all --oneline -E -G "sk-or-v1-[0-9a-f]{32}"`. `-G` finner commits der antallet linjer som matcher, endrer seg, altså både en nøkkel som legges til og en som fjernes senere. `--all` tar med alle brancher og tagger. Kommandoen er ren git og virker likt i PowerShell, Git Bash og zsh. De falske nøklene i `scripts/test_modelltest_*.py` (`sk-or-v1-fake-…`) har ikke 32 heksadesimale tegn og gir derfor ingen treff.

## Verification

**Commands:**
- `git log --all --oneline -E -G "sk-or-v1-[0-9a-f]{32}"` -- expected: ingen utskrift
- `git ls-files | grep -i "\.env$"` (Git Bash) -- expected: ingen utskrift (`.env.example` slutter ikke på `.env`)
- `git diff --stat main` -- expected: bare `README.md`, `docs/`, `_bmad-output/` og `frontend/tester/komponenter/avveining.test.tsx`; ingen filer i `backend/` eller `frontend/src/`
- `cd frontend && npm run build && npm run test` -- expected: bygget grønt, alle modul- og komponenttester består

**Manual checks (if no CLI):**
- Alle relative lenker i README og sjekklisten peker til filer og avsnitt som finnes.
- Tekstene README siterer, er identiske med `frontend/src/tekster.ts` og logglinjene i `main.py`.
