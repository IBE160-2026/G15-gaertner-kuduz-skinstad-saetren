# Modellsammenligning via OpenRouter, 15. oktober 2026 (pågår)

**Status: ikke ferdig.** GPT-6 Luna er testet fullt. Mistral Small 4 og gratis
Gemma 4 31B ble stoppet av midlertidige kvotegrenser hos leverandøren (HTTP 429)
og fortsetter 16. oktober. Se [Overlevering](#overlevering-til-neste-økt) nederst.

Dette er agentens egenrapportering. Et gruppemedlem må gjennomgå vurderingen.
Arbeidet er gjort i `ki-leverandor-openrouter-haiku` fra
`527b64b00aa4aa7f25998c609e29bf1a8f47c736`, etter brukerens beslutning om å
ikke opprette ny branch.

## Oppgaven og promptene

Første prompt (gitt til en annen agent og overlevert hit), ordrett:

> Jeg vil kjøre samme test med alternative modeller for å sammenligne kvaliteten. Kan vi gjøre det samme med Google sin Gemma 4 (gratis) og et godt billig alternativ på samme prisnivå som Haiku5.5, for eksempel en billig fra Open AI, Meta eller andre. Jeg vil unngå kinesisk hvis det er mulig. Du er ferdig når jeg har forslag å vurdere, og vi har en fremgangsmåte for gjennomføring

Beslutningen etter forslaget, ordrett:

> 1. støtter denne vurderingen. rapporter formatfeil og kategorifeil hver for seg. 2. Jeg ser for meg at vi senere ønsker å benytte håndhevet skjema. Vi kan teste Gemma uten håndhevet skjema (det koster uansett ingenting), vi bruker testresultatene fra forrige Haiku test, og tester Luna og Mistral med håndhevet skjema. Branch: Behold arbeidet på branchen vi står i. Dette handler om testing av modeller, som er hensikten med denne branchen. Hvis du trenger flere avklaringer tar vi de først, hvis ikke, gjennomfør tester. Du er ferdig når vi har et resultat av testene som kan brukes i en vurdering av modellenes prestasjon.

## Testoppsett

Promptene, de 16 scenarioene og fasiten er uendret fra
[Haiku-testen](2026-10-15-modelltest-haiku.md). Haiku kjøres ikke på nytt;
resultatet derfra brukes som referanse.

| Modell | Pris inn/ut USD per M tokens | Leverandør låst til | Svarformat |
|---|---|---|---|
| `anthropic/claude-haiku-5.5` (referanse) | 0,10 / 0,50 | ikke låst, gikk til Azure | strict JSON Schema |
| `openai/gpt-6-luna` | 0,10 / 0,50 | `openai` | strict JSON Schema |
| `mistralai/mistral-small-2603` (Small 4) | 0,15 / 0,60 | `mistral` | strict JSON Schema |
| `google/gemma-4-31b-it:free` | 0 / 0 | `google-ai-studio` | vanlig JSON-modus |

Priser og støtte er lest fra OpenRouters katalog og endepunktliste 2026-10-15.
Gratis-Gemma har ikke `structured_outputs`; de betalte Gemma-endepunktene har det.
`gpt-6-luna-pro` er samme modell med ekstra resonnering og ble holdt utenfor fordi
testen slår av resonnering. Kinesiske vertsleverandører unngås ved leverandørlåsen.

Gemma i vanlig JSON-modus er ikke direkte sammenlignbar med de tre andre på format:
uten håndhevet skjema kan modellen svare med ekstra felt eller ugyldig kategori.
Derfor føres `format`, `innhold` og `teknisk` hver for seg, og kategoritreffet
regnes bare av svar med gyldig format.

## Resultater så langt

### GPT-6 Luna: fullført

Rapport: [gpt6-luna-20261015T200334291355Z.json](modelltest-resultater/gpt6-luna-20261015T200334291355Z.json).
Start 20:03:34 UTC. Skript-SHA-256 `ef395396…6c6e` (før 429-endringen, se under).

| Måling | Luna | Haiku (referanse) |
|---|---|---|
| Fullførte kall | 32 av 32 | 32 av 32 |
| Formatfeil / tekniske avvik | 0 / 0 | 0 / 0 |
| Preferansekategori mot fasit | **24 av 24** | 20 av 24 |
| Kandidat-ID i forklaringer | 8 av 8 | 8 av 8 |
| Input-/output-tokens | 9 248 / 1 729 | 21 014 / 3 257 |
| API-rapportert kostnad, 32 kall | USD 0,0017893 | USD 0,0037299 |
| Responstid min / median / maks | 1,157 / 1,430 / 3,406 s | 1,343 / 1,734 / 2,500 s |
| Leverandør i svarene | OpenAI | Azure |
| Resonneringstokens | 0 | ikke målt |

Luna klassifiserte både negasjonen («ønsker ikke flere») og kriseutsagnet («kan ta
en ekstravakt hvis det blir krise») som `ingen_registrert` i begge runder, der Haiku
avvek. Samme pris per token, men Luna brukte under halvparten så mange input-tokens
på samme tekst, så faktisk kostnad ble om lag halvparten.

**Foreløpig manuell lesing (agent, ikke gruppemedlem):** Alle 24 begrunnelser og
8 forklaringer er lest én gang. Ingen kjønnet omtale («vedkommende» brukes). Tallene
i forklaringene (2400/3000/1800/2100 kr, 18/33/9/18 timer, 50/92/25/50 %) er korrekte.
Ingen ny rangering, beregning eller lovgaranti. Forklaringene har 3–4 setninger,
noe lange. Negasjonsbegrunnelsen gjengir delvis regelen («skal ikke tolkes som det»)
i stedet for bare å beskrive ønsket. Injeksjonssvarene beskriver bare preferansen.
Full manuell vurdering etter samme mal som Haiku-loggen gjenstår, gjerne blindet.

### Mistral Small 4 og gratis Gemma: ikke kjørt

Alle forsøk fikk HTTP 429. Feilkroppen, lest én gang med nøkkelen fjernet, sa
`temporarily rate-limited upstream` med `limit_source: upstream_provider_shared_pool`:
en felles kvote hos leverandøren, ikke kontoens grense eller feil i oppsettet.
Mistral svarte på ett diagnosekall kl. 22:11 norsk tid, men var stengt igjen
sekunder senere. Ingen modellsvar fra disse to er vurdert.

Delrapporter beholdes som dokumentasjon. Ingen av dem inneholder modellsvar:

- `*-smoke-*` for begge modeller: 429 på ettkallskontrollen (to forsøk hver).
- `mistral-small-4-20261015T201107102246Z.json`: 429 uten nye forsøk.
- `mistral-small-4-20261015T201137763928Z.json`: 429 etter 10 nye forsøk à 30 s.
- `mistral-small-4-20261015T201659322557Z.json` og
  `gemma4-31b-free-20261015T201142943621Z.json`: stoppet manuelt etter 1 og 9 nye
  forsøk da økten ble avsluttet. Status står som `in-progress` fordi prosessen ble
  avbrutt; filene er ikke redigert i etterkant.

## Endringer i testverktøyet

- `MODELS` erstatter at alle modeller unntatt Haiku avvises. `--model` overstyrer
  `OPENROUTER_MODEL`. Leverandørlås sendes som `provider.only`. Haiku er uten lås,
  slik den gikk i referansekjøringen.
- `check_answer` returnerer `{"format": [...], "innhold": [...]}`; tekniske avvik
  føres i `teknisk`. Kategori utenfor de fire lovlige (f.eks. `færre`) er formatfeil.
  `summary` i rapporten teller gruppene hver for seg.
- `--smoke` (ett kall) og `--pause` (sekunder mellom kall).
- `--retry-429 N` og `--retry-wait S`: nytt forsøk **bare** ved HTTP 429. Standard 0.
  Antall forsøk føres per kall (`rate_limited`) og i `summary.http_429_for_svar`.

## Rettelser og avvik fra plan

1. Første versjon fulgte den dokumenterte regelen «ingen retry». Det gjorde at én
   429 avbrøt hele kjøringen, og den felles kvoten svingte for raskt til at en
   kjøring kom gjennom. 429-forsøk ble lagt til etter at Luna var kjørt. Det endrer
   ikke Luna-resultatet: Luna fikk ingen 429. Det er forsvarlig fordi 429 avvises
   før modellen svarer; et nytt forsøk kan derfor ikke velge et gunstigere modellsvar.
   Andre feil prøves fortsatt aldri på nytt.
2. Skriptets SHA-256 er derfor ulik for Luna (`ef395396…`) og for kommende kjøringer.
   Nåværende versjon: `581861e6e17ec68ab0d974fa78027b4ca4664b12af6a939614ea398e0e95e20a`.
3. Første forsøk på å patche skriptet via skallet feilet på sitering; patchen ble
   kjørt fra fil i stedet. Ingen innholdskonsekvens.

## Kvalitetssikring

`python -B -m unittest discover -s scripts -p "test_modelltest*.py"`: alle tester
16 av 16 bestått etter siste endring. Nye tester dekker modellvalg,
leverandørlås og svarformat per modell, avvisning av ikke-godkjent modell,
`færre` som formatfeil, oppsummering med separate feiltyper, 429-forsøk med og uten
tillatelse, og at andre HTTP-feil ikke behandles som 429.

## Overlevering til neste økt

Gjenstår, i rekkefølge:

1. Kjør fra roten (Mistral og Gemma kan kjøres samtidig i hvert sitt vindu):

   ```powershell
   python -B scripts/modelltest_openrouter.py --live --model mistralai/mistral-small-2603 --smoke
   python -B scripts/modelltest_openrouter.py --live --model google/gemma-4-31b-it:free --smoke
   python -B scripts/modelltest_openrouter.py --live --model mistralai/mistral-small-2603 --pause 2 --retry-429 30 --retry-wait 120
   python -B scripts/modelltest_openrouter.py --live --model google/gemma-4-31b-it:free --pause 4 --retry-429 30 --retry-wait 120
   ```

   Sett `$env:PYTHONIOENCODING="utf-8"` først hvis norske tegn vises feil i terminalen.
   Exit 0/1 er fullført kjøring (1 = innholdsavvik), exit 2 = avbrutt.
2. Er kvoten fortsatt stengt, trengs en beslutning fra brukeren før noe annet prøves:
   - eget Mistral-/Google-nøkkel i OpenRouter (BYOK) gir egen kvote, eller
   - betalt `google/gemma-4-31b-it` låst til `deepinfra` i vanlig JSON-modus
     (~USD 0,003 for 32 kall), som bevarer testbetingelsen men ikke «gratis».
   Ingen av delene er innført i `MODELS`.
3. Fyll inn Mistral og Gemma i tabellen over: formatfeil, kategori av gyldige,
   kandidat-ID, tokens, kostnad, responstid, antall 429.
4. Manuell lesing av alle begrunnelser og forklaringer for alle tre nye modeller
   etter malen i [veiledningen](../modelltest-openrouter.md#vurdering-bestemt-før-kjøring):
   oppdiktede fakta/kjønn, norsk bokmål, instruksjonsangrep, tall, 2–4 setninger.
   Les helst uten modellnavn synlig.
5. Skriv konklusjon og anbefaling. Fjern «(pågår)» fra tittelen.
6. Commit på denne branchen; brødteksten skal nevne 429-avviket fra «ingen retry».
