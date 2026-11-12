# KI-logg: Story 2.4 – filtrere på 35-timersregelen (ukentlig fri)

Dato: 2026-11-11 (spesifikasjon), implementert 2026-11-12. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (AV-04, AV-07, P-08, vedtak A5 i §11, OP-14). Arbeidet ble gjort av Claude Code (Opus 5.5) som implementeringsagent i `bmad-build`, på branchen `story-2.4-trettifem-timer`.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read …/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **Ny regel** (`backend/domene/regelmotor/trettifem_timer.py`): `ÅRSAK = "35-timersregelen"`, `MINSTE_FRI = 35 t`, `OSLO`, `berørte_uker`, `lengste_fri`, `bryter_trettifem_timer` og `vindu`. Ukegrensene settes på veggklokka i Oslo med `datetime.combine(mandag, time(0), tzinfo=OSLO)` og regnes om til UTC. Neste mandag finnes ved å legge 7 dager til datoen, ikke til tidspunktet. Berørte uker er ukene det halvåpne `[start, slutt)` overlapper, så en Vakt som slutter mandag 00:00, berører bare én uke. Fri regnes fra unionen av Kandidatens gyldige vakter og Vakten, klippet til uka, også fra ukestart og til ukeslutt. Under 35 t i én uke gir utelukkelse, nøyaktig 35 t er gyldig. Semantikken er den samme som fasithjelperen `bryter_trettifem_timer` i `tester/lagring/test_testdata.py`, som regelmotoren ikke importerer.
- **Overlapp (beslutning A, Ragnhild 2026-11-11, OP-14):** en egen vakt som overlapper Vakten, telles med i unionen. En Kandidat med kolliderende vakt kan da også få «35-timersregelen».
- **`elleve_timer.py`**: `_gyldig_tidsrom` er gjort offentlig som `gyldig_tidsrom` og importeres i 35-timersregelen, uten duplisering.
- **`vurdering.py`**: regel nummer fire i `REGLER`, med tomme `vaktkrav` og `kandidatkrav`. Vinduet er `[mandag i første berørte uke, mandag etter siste berørte uke)` i UTC. Det samlede vinduet og datafeilsjekken arves uendret fra 2.3. Det erstatter `[ASSUMPTION]` i story 2.4 i epics: ligger en berørt uke utenfor `[historikkstart, datagrense]`, gir det `Datafeil` (P-08).
- **Frontend**: `midlertidigMerknad` er fjernet. Når listen er tom, viser `Kandidatliste` «Ingen gyldige kandidater for denne vakten.» i `meta`-stil, uten ikon og uten `danger` (beslutning B). API-et er uendret.
- **README**: regelstatusen sier fire regler, og #4127 gir 4 gyldige og #4189 0.
- **Tester**: ny `tester/regelmotor/test_35_timersregelen.py` (40), tilpasset `test_11_timersregelen.py` (48), `test_kolliderende_vakt.py` (44) og `tester/api/test_kandidater.py` (43). Frontendtestene i `frontend/tester/kandidater.test.mjs` har to nye tester.

## Korrigering og kvalitetssikring

Rettet underveis:

1. **Feil forventning i egen test:** `test_fri_fra_ukestart_rundt_grensen` hadde et tilfelle med 0 min fri fra ukestart som skulle gi brudd. Med Vakten mandag 00–08 og egne vakter fra onsdag er det 47 t fri etter Vakten, så forventningen var gal, ikke koden. Tilfellet er fjernet.
2. **Determinismetesten** hadde en kommentar og en konstruksjon som ikke stemte med tallene (alle 24 ble utelukket). Skrevet om: id 1–12 har nøyaktig 35 t fri og er gyldige, id 13–24 har en ekstra vakt lørdag og er utelukket. Testen sjekker begge gruppene og omvendt rekkefølge.
3. **Startgrensen for 11-timersvinduet i `test_11_timersregelen.py`:** med regel fire starter det samlede vinduet mandag i uka, så seks tester av startgrensen til 11-timersvinduet testet ikke lenger den grensen (tre ble røde, tre ble grønne av feil grunn). De kjører nå med `regler=REGLER[:3]`, gjennom en ny `regler`-parameter i hjelperne `vurder` og `datafeil`. Startgrensen for uka testes i `test_35_timersregelen.py`.
4. **`test_egen_vakt_før_periodestart_som_overlapper_utelukker`** flyttet #4127 til mandag 21.09 00–08 og antok at første gyldige i fasiten for #4127 (Ingrid Dahl) også er gyldig der. Med 35-timersregelen er hun ikke det. Testen henter nå den første gyldige på det nye tidspunktet fra API-et. Det testen skal vise, at en vakt før periodestart som overlapper, utelukker, er uendret.
5. Regellistetestene i `test_11_timersregelen.py` og `test_kolliderende_vakt.py` forventer nå fire regler. API-testen som sa at de som bare bryter 35-timersregelen, er med, er fjernet, og forventningen om at Anders Strand og Line Moe står først, er erstattet av den eksakte listen fra `FASIT`.

Kontroller:

- **Fasiten (AV-07):** API-testene leser `testdata.FASIT`, og `IMPLEMENTERTE_REGLER` har alle fire utfallene. #4127 gir 4 gyldige (Ingrid Dahl, Jonas Bakke, Mette Solberg, Thomas Nygård) og 20 utelukket. #4189 gir 0 gyldige og 24 utelukket, og svaret er `{"status": "ok", "kandidater": []}` til story 2.6. Fasiten er ikke endret.
- **Mutasjon `<` til `<=` (akseptansekrav 2), gjort én gang 2026-11-12:** sammenligningen mot `MINSTE_FRI` i `bryter_trettifem_timer`. Full `pytest` ga **6 røde av 381**: nøyaktig 35 t til ukeslutt, 2100 min fra ukestart, 2100 min mellom to vakter, høstskiftet med 35 faktiske timer og begge determinismetestene. Reversert, 381 grønne.
- **Mutasjon som fjerner UTC-omregningen (akseptansekrav 3), gjort én gang 2026-11-12:** `.astimezone(UTC)` fjernet fra ukegrensene og fra alle sammenligninger i `lengste_fri`. **4 røde av 381**: 167 og 169 timer i ukene med sommertidsskifte, vårskiftet (35 t på veggklokka er 34 faktiske og utelukker) og høstskiftet (34 t på veggklokka er 35 faktiske og er gyldig). Alle tider i testene bruker samme `ZoneInfo`-objekt, så Python regner på veggklokka når omregningen mangler. Reversert, 381 grønne.
- **Mutasjon som setter ukegrensene i UTC (akseptansekrav 3), gjort én gang 2026-11-12:** `tzinfo=UTC` i stedet for `OSLO` i `datetime.combine`, og ukedatoen regnet i UTC. **38 røde av 381**, blant dem alle ukegrensetestene, begge sommertidstestene, eksempelet for #4127 og #4189 og fasittestene for #4189 gjennom API-et (uka slutter da etter datagrensen og gir datafeil). Reversert, 381 grønne.
- **Mutasjon av unionen, etter gjennomgangen 2026-11-12:** gjennomgangen fant at `fri_fra = max(fri_fra, slutt)` i `lengste_fri` kunne endres til `fri_fra = slutt` uten at noen test ble rød, fordi ingen test hadde en vakt som ligger inne i en annen. Ny test `test_vakt_som_ligger_inne_i_en_annen_forkorter_ikke_den_ytre` (egen vakt lørdag 04–16 omslutter Vakten 05–13, fria er 32 t fra 16:00). Med mutasjonen ga `test_35_timersregelen.py` **1 rød av 40**, nøyaktig den nye testen. Reversert, 40 grønne. Samtidig fikk teksten for tom liste i `Kandidatflate.tsx` `role="status"`, som lastemeldingen, slik at skjermlesere leser opp resultatet.
- **Matrisen i spesifikasjonen:** 35:00 og 34:59 (til ukeslutt, fra ukestart og mellom to vakter), krysser ukeskiftet med brudd bare i uka før og bare i uka etter, slutter mandag 00:00 (uke 40 fylt med kveldsvakter og likevel gyldig), 40 t fri lørdag–mandag med 33 t i uka (utelukket), vårskiftet (167 t) og høstskiftet (169 t), ingen egne vakter, #4127 og #4189, uke etter datagrensen (datafeil i domenet og gjennom API-et med periodeslutt flyttet til 03.10), ugyldig vakt i uka utenfor ±11 t (datafeil) og i uka før (vurderes normalt).
- **Uavhengig kodegjennomgang 2026-11-12:** tre gjennomgangsagenter (blind-hunter, edge-case-hunter og verification-gap, alle Opus 5.5) leste diffen uten å ha sett implementeringen. Elleve funn: to rettet (unionstesten og `role="status"`, se over), to utsatt til `deferred-work.md` (ingen test rendrer `Kandidatliste`, og AGENTS.md er utdatert) og sju avvist. Påstanden om at seeden ikke gir noen Ansatt flere årsaker, ble kontrollert manuelt med `vurder_kandidater` på seeden: #4127 4 gyldige og 20 utelukket, #4189 0 og 24, ingen med mer enn én årsak. Alle funn med dom står i spesifikasjonens Review Triage Log.
- **Resultater 2026-11-12, macOS, etter gjennomgangen:** full `pytest` i `backend/` ga **382 bestått**, inkludert import-linter-kontrakten. `npm run build` bestod, og `npm test` ga **28 bestått**.

- **Nettleserkontroll:** Ragnhild gjorde nettleserkontrollen 2026-11-12: #4127 viste Ingrid Dahl, Jonas Bakke, Mette Solberg og Thomas Nygård uten merknad, og #4189 viste «Ingen gyldige kandidater for denne vakten.»

## Gjenstår

- Menneskelig PR-gjennomgang av et gruppemedlem.
- Testene er kjørt på macOS. Fysisk test på Windows (OP-05) er ikke gjort.
