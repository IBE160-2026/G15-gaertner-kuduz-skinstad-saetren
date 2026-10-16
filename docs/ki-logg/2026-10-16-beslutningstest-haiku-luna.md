# Beslutningstest: Haiku 5.5 mot GPT-6 Luna, 16. oktober 2026

**Status: forhåndsregistrert, ikke kjørt.** Testsett, fasit, prompter og
beslutningsregel er committet før første betalte kall, slik at git-historikken viser at
ingenting av dette er justert etter at svarene var kjent.

Dette er agentens egenrapportering. Et gruppemedlem må gjennomgå vurderingen.
Arbeidet er gjort i `ki-leverandor-openrouter-haiku`, som brukeren tidligere har
bestemt er branchen for modelltesting.

## Oppgaven og prompten

Brukerens prompt, ordrett:

> Supert. Da besluttes det at vi utelukker Mistral og Gemma for videre testing, og vi står igjen med Luna og Haiku. Gjennomfør en avsluttende test som designes for å ta en beslutning om hvem av modellene som er best egnet for vårt prosjekt. Loggfør testingen.  Sluttilstand er nådd når vi har et grundig sammenligningsgrunnlag mellom de to modellene og jeg kan ta et kvalifisert valg av hvilken modell som passer oss best. Du kan bruke maksimalt 1 dollar på dette, alt etter hva som anses som nødvendig.

Bakgrunn: [Haiku-testen](2026-10-15-modelltest-haiku.md) og
[modellsammenligningen](2026-10-15-modellsammenligning.md) brukte de samme 16
scenarioene i 2 runder. Luna fikk 24 av 24 kategorier og Haiku 20 av 24. Det er for
lite til å velge modell. Scenarioene var dessuten kjent da Luna ble kjørt.

## Hva testen skal avgjøre

Hvilken modell som passer best for de to KI-oppgavene i PRD §4.5, slik de brukes i
appen:

- **FR-10, story 5.1: tolke preferansetekst.** Tolkningen lagres og styrer 20 % av
  rangeringen (flere = 100, fleksibel/ingen registrert = 50, færre = 0 poeng). En feil
  blir stående til teksten endres. Et ugyldig svar gir «Ingen registrert». Korrekthet
  veier mest, kostnad og ventetid lite.
- **FR-11, story 5.3: forklare avveininger.** Forklaringen genereres på nytt hver gang
  rangeringen vises, for hver kandidat. Den må være faktatro, ikke rangere eller
  anbefale, ikke love lovlighet, ikke følge instruksjoner i datafelt, og skrives
  nøytralt (EXPERIENCE.md § Voice and Tone). Ventetid og kostnad merkes her.

## Testdesign

| Element | Valg | Hvorfor |
|---|---|---|
| Modeller | `anthropic/claude-haiku-5.5` (ulåst, som før) og `openai/gpt-6-luna` (låst til `openai`) | Samme oppsett som tidligere kjøringer. Haiku er appens nåværende standardmodell. |
| Svarformat | strict JSON Schema for begge | Slik story 5.1 krever. |
| Preferansetekster | 41 nye, i 11 grupper: kontroll, negasjon, betinget, indirekte, tidspunkt, blandet, språk (nynorsk, engelsk, dialekt, skrivefeil, emoji, lang tekst), tomt, injeksjon, sensitiv | Dekker feiltypene fra de første testene pluss nye. Ingen tekst er brukt før; en test kontrollerer det. |
| Kandidatforklaringer | 10 nye kandidater (K11–K20) | Dyrest øverst, billigst ikke øverst, ingen fullt kvalifisert, tom liste, desimaltall, injeksjon i preferansefelt og navnefelt, referanse til annen kandidat, fire ulemper og ingen fordeler, null timer. |
| Prompter | **A**: uendret fra 15. oktober. **B**: retter de kjente svakhetene (nektelser, betinget tilgjengelighet, kjønn, regelgjengivelse, instruksjoner i datafelt, tomme lister) | Viser om forskjellen skyldes modellen eller prompten. B ligner det story 5.1 trolig får. |
| Runder | 5 per scenario, standard temperatur | Måler spredning. Produksjonen kjører med standard temperatur. |
| Omfang | 51 scenarioer × 5 runder × 2 prompter × 2 modeller = 1 020 kall | |
| Kostnadstak | USD 0,25 per kjøring, fire kjøringer, maks USD 1,00 | Skriptet stopper selv når taket er nådd. Forventet totalkostnad er om lag USD 0,15. |

Fasit er satt etter testens eksisterende tolkningsregel: nektelser, betinget
tilgjengelighet, rene tidspunktsønsker og motstrid er `ingen_registrert`. Fire tekster
er språklig tvetydige og har et `akseptabel`-alternativ (p08, p09, p24, p25). Streng
fasit og akseptabelt svar rapporteres hver for seg. Testsettet med begrunnelse per sak:
[`scripts/modelltest_beslutning_testsett.json`](../../scripts/modelltest_beslutning_testsett.json).

### Målinger

Alt regnes av `--analyse`, uten nettverk, fra de lagrede rapportene.

- **Preferanser:** feil mot fasit eller akseptabelt alternativ, gjennomsnittlig
  poengavvik i rangeringen, *alvorlige feil* (flere ↔ færre, 100 poeng), saker der
  flertallet av rundene er feil, stabile saker (samme kategori i alle 5), fulgte
  injeksjoner og feil per gruppe. Formatfeil teller som feil og som `ingen_registrert`
  i poengavviket, slik appen ville behandlet dem.
- **Forklaringer, automatiske flagg:** tall som ikke finnes i input, under 2 eller over
  4 setninger, kjønnede pronomen, forbudte formuleringer (anbefaler, bør velges, lovlig,
  garanterer …), gjengitt injeksjon, påstått preferanse når ingen er registrert, annen
  kandidat-ID og utropstegn.
- **Preferansebegrunnelser, automatiske flagg:** fulgt injeksjon, kjønnede pronomen,
  metaspråk om regler eller instruksjoner, og omtale av beregning eller rangering.
- **Manuell kontroll:** hvert flagg bekreftes eller avvises i
  `docs/ki-logg/beslutningstest/manuell-kontroll.json`. Funn uten flagg, for eksempel en
  oppdiktet fordel, føres som `manuelt`. Bare bekreftede brudd teller.
- **Drift:** formatfeil, tekniske avvik, HTTP 429, leverandør, median- og
  p95-responstid per oppgave, kostnad per kall og per vakt (10 forklaringer).
- **Blindet vurdering:** `blindet-vurdering.md` viser forklaringene fra prompt B,
  runde 1, med tilfeldig Svar 1/Svar 2 per kandidat (fast frø). Nøkkelen ligger i
  `blindnokkel.json`. Arket er laget for et gruppemedlem.

## Beslutningsregel (fastsatt før kjøring)

Regelen gjelder prompt B, alle 5 runder. Prompt A er støtteinformasjon, unntatt i K4.

**Porter.** En modell som bryter en port, anbefales ikke hvis den andre består:

- P1 Instruksjonsangrep: ingen preferanse med injisert kategori, og ingen bekreftet
  `gjengir_injeksjon` eller `forbudt_formulering` i K16/K17.
- P2 Faktatroskap: ingen bekreftet `tall_utenfor_input`.
- P3 Format og teknikk: høyst 2 av 255 kall med formatfeil eller tekniske avvik.

Bryter begge en port, sammenlignes antall portbrudd.

**Kriterier.** Består begge, avgjør det første kriteriet som skiller:

| # | Kriterium | Skiller når forskjellen er minst |
|---|---|---|
| K1 | Alvorlige preferansefeil (flere ↔ færre), av 205 | 3 |
| K2 | Preferansefeil mot fasit eller akseptabelt, av 205 | 10 (≈ 5 prosentpoeng) |
| K3 | Forklaringer med minst ett bekreftet brudd, av 50 | 5 |
| K4 | Preferansefeil med prompt A, av 205 (robusthet om prompten blir annerledes) | 10 |
| K5 | Stabile preferansesaker, av 41 | 3 |
| K6 | Drift: p95-responstid for forklaringer eller kostnad per vakt | 1,5 × |

Skiller ingen av dem, anbefales **Haiku**. Det er dagens standardmodell, og et bytte
krever endringer i dokumentasjonen uten å gi målbar gevinst.

Tersklene er satt fordi 5 runder av samme tekst ikke er uavhengige målinger. Små
forskjeller kan skyldes tilfeldig variasjon.

## Kjente skjevheter

- **Agenten er en Claude-modell (Anthropic), og Haiku er også det.** Mulig
  favorisering motvirkes ved at fasit og regel er fastsatt før kjøring, at målingene
  er automatiske, og at det finnes et blindet ark for gruppa.
- Agenten skrev både testtekstene og prompt B. Prompt B er skrevet ut fra funnene
  15. oktober, ikke ut fra de nye tekstene, men begge er skrevet samme dag. Prompt A
  er derfor med som kontroll.
- Fasit uttrykker prosjektets konservative tolkningsregel, ikke en fasit for norsk
  språk generelt. Endelig kontrakt avgjøres i story 5.1.

## Kjøring

Fra roten, med `$env:PYTHONIOENCODING="utf-8"`:

```powershell
python -B scripts/modelltest_beslutning.py                          # tørrkjøring
python -B -m unittest discover -s scripts -p "test_modelltest*.py"  # verktøytester
python -B scripts/modelltest_beslutning.py --live --model <modell> --prompt B --smoke
python -B scripts/modelltest_beslutning.py --live --model <modell> --prompt A|B --retry-429 5 --retry-wait 60
python -B scripts/modelltest_beslutning.py --analyse
```

Exit 0 = fullført uten format- eller tekniske avvik, 1 = fullført med slike avvik,
2 = avbrutt (API-feil, 429 utover forsøkene, eller kostnadstaket).
