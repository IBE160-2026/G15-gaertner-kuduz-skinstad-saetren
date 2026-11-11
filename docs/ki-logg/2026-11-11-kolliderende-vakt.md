# KI-logg: Story 2.2 – filtrere bort kandidater med kolliderende vakt

Dato: 2026-11-11. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (AV-02, AV-06, AV-07, P-08). Arbeidet ble gjort av Claude Code (Sonnet 5.5) som implementeringsagent i `bmad-build`, på branchen `story-2.2-kolliderende-vakt`.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read …/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **Domenet** (`backend/domene/`): `typer.py` har `Tidsrom(start, slutt)` og `Kandidat.vakter` (standard tom, `compare=False` som `kompetanse`, så 2.1-kall og tester virker uendret). `regelmotor/kolliderende_vakt.py` har `ÅRSAK = "kolliderende vakt"`, `bryter_kollisjon` (halvåpne intervall, `a.start < b.slutt and b.start < a.slutt`, alle tider omregnet til UTC) og `kollisjonsdatafeil` (egen vakt uten tidssone eller med start ikke før slutt gir datafeil, P-08). Regelen er nummer to i `REGLER` i `vurdering.py`. Sorteringen og svarformen er uendret.
- **Lagring**: `kandidatgrunnlag.py` henter alle rader i `vakt` med `tildelt_ansatt_id IS NOT NULL` i én spørring, grupperer på ansatt-id og legger dem på Kandidaten (AD-5, ingen N+1). Ingen endring i skjema, testdata eller API-rute.
- **Frontend og README**: merknaden er «Filtrert på kompetanse og kolliderende vakt. Flere regler kommer.», og README sier at #4127 gir 9 og #4189 19 gyldige.
- **Tester**: `tester/regelmotor/test_kolliderende_vakt.py` (40) og utvidet `tester/api/test_kandidater.py` (28, mot `FASIT`, AV-07).

## Korrigering og kvalitetssikring

Rettet underveis:

1. Første versjon av testen for timen som går to ganger laget egen vakt som `andre_gang + timedelta(minutes=10)`. Aritmetikk på en `datetime` med `tzinfo` regner på veggklokka og mister `fold`, så sluttiden havnet før starten og vurderingen ga datafeil. Testen legger nå til tiden via UTC. Dette er samme fallgruve som regelen unngår ved å sammenligne i UTC.
2. To tester hadde i første utkast lange, selvmotsigende kommentarer fra at sommertidsscenarioet ble tenkt ut underveis. De ble skrevet om til korte forklaringer, og én test ble splittet, før noe ble levert.

Kontroller:

- **Fasiten (AV-07):** API-testene leser `testdata.FASIT` og tilpasser den ikke. De gyldige er alle som ikke har `kompetanse` eller `kolliderende` i fasiten: #4127 gir 9 (16 fra 2.1 minus 7) og #4189 19 (21 minus 2). En egen test viser at ingen med `kolliderende` er med, og at de som bare brytes av 11 t og 35 t fortsatt er med, siden de reglene kommer i 2.3 og 2.4. Regelmotoren importerer ikke testhjelperne.
- **Ingen lekkasje (NFR2):** svaret har bare `id`, `navn` og `kompetansenivå`, og inneholder verken vakter, tider eller årsaken «kolliderende vakt».
- **Mutasjon (akseptansekrav 3), gjort én gang 2026-11-11:** begge sammenligningene i `overlapper` ble endret fra `<` til `<=`, altså lukkede intervall. `pytest tester/regelmotor tester/api/test_kandidater.py` ga **13 røde tester** (blant annet «møtes» på begge sider, natt over midnatt, sommertidsnatten og begge fasittestene for #4127 og #4189). Endringen ble reversert, og de samme testene var grønne igjen (120 bestått). Etter rettelsene fra gjennomgangene ble samme mutasjon kjørt på nytt: **14 røde av 124**, fordi determinismetesten nå også ser vaktene. Reversert, 124 grønne.
- **Mutasjon av UTC-omregningen, gjort én gang etter gjennomgangen:** den uavhengige gjennomgangen viste at `astimezone(UTC)` kunne fjernes fra `overlapper` uten at noen test feilet. Sommertidstestene i første utkast gir samme svar på veggklokke og er derfor ikke bevis for omregningen. To nye tester dekker den: `test_overlapp_på_veggklokka_men_ikke_på_faktisk_tid_utelukker_ikke` (Vakten slutter 02:30 med `fold=0`, 00:30 UTC, og egen vakt starter 02:15 med `fold=1`, 01:15 UTC) og det speilvendte tilfellet. Veggklokka sier overlapp, faktisk tid sier 45 minutter mellom dem, og sluttidene er bygget via UTC. Med `.astimezone(UTC)` fjernet fra begge sammenligningene i `overlapper` (bare der) feilet nøyaktig disse to testene (2 røde, 38 grønne). Endringen ble reversert, og alle 40 var grønne igjen. Testen `test_egen_vakt_med_start_etter_slutt_på_veggklokka_er_gyldig_og_kolliderer` dekker bare at start før slutt regnes på faktisk tid i datasjekken, ikke overlappsjekken.
- **Determinisme og vakter:** `Kandidat.vakter` har `compare=False`, så likhet på resultatet ser ikke vaktene. Testene for determinisme og for at vurderingen ikke endrer grunnlaget sammenligner derfor `(id, vakter)` for gyldige og utelukkede eksplisitt, så en endret eller fjernet vakt gir rød test.
- **Resultater:** full `pytest` i `backend/` ga **273 bestått** etter første gjennomgang (229 før storyen, pluss 44 nye) og **275** etter andre gjennomgang, inkludert import-linter-kontrakten for den nye modulen. `npm.cmd run build` bestod, og `npm.cmd test` ga **26 bestått**.

## Uavhengige gjennomganger

1. **Under `bmad-build` (Sonnet 5.5):** blind-hunter, edge-case-hunter og verification-gap, uten å ha sett implementeringen. 15 funn, tre rettet: UTC-omregningen var ikke vernet av noen test, determinismetestene så ikke `Kandidat.vakter`, og et testnavn var misvisende. Alle funn med dom står i Review Triage Log i spesifikasjonen. Antallet 271 der er før de to `fold`-testene ble lagt til.
2. **`bmad-review` (Opus 5.5) av hele branchen:** adversarial, edge-case-hunter og verification-gap, uten å ha sett den første gjennomgangen. 21 funn. Rettet:
   - Ingen test viste at Kandidatens vakter hentes uavhengig av periode. Reviewer avgrenset spørringen til perioden, og alle 273 tester var grønne. Ny API-test: en tildelt vakt som starter før periodestart og overlapper en Vakt ved periodestart, utelukker.
   - Datafeil for en ugyldig tildelt vakt var bare testet i domenet. Ny API-test: en tildelt vakt med `start = slutt` gir `datafeil`.
   - Begge testene er kontrollert med mutasjon av adapteren (periodefilter og filter på `start < slutt`), og hver mutasjon ga nøyaktig én rød test. Adapteren er tilbakestilt.
   - Testhjelperen `kandidat()` gjorde `kompetanse={}` om til full kompetanse. Rettet med `is None`.
   - Mutasjonstallet og statusen for gjennomgangen i denne loggen og vurderingsmatrisen var utdatert.
   - Ikke rettet her: Vaktens egen rad blir en «egen vakt» når Epic 3 kjører reglene på nytt etter Godkjenning. Det kan ikke skje i dag, fordi databasen krever at en vakt med tildelt Ansatt ikke mangler bemanning, og kandidatgrunnlaget henter bare ubemannede vakter. Ført i `deferred-work.md` for story 3.2. Om datafeilsjekken skal gjelde all historikk eller bare vakter som kan påvirke regelen (P-08, «nødvendig»), er lagt fram for gruppa i PR-en.

## Gjenstår

- Nettleserkontrollen (logg inn, velg #4127 og #4189 og se 9 og 19 kandidater).
- Menneskelig PR-gjennomgang av et gruppemedlem.
