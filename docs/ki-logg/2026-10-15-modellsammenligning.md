# Modellsammenligning via OpenRouter, 15.–16. oktober 2026

**Status:** Haiku (referanse), GPT-6 Luna og Gemma 4 31B er sammenlignet på samme
16 scenarioer × 2. Mistral Small 4 er **ikke testet**: leverandørens felles kvote
ga HTTP 429 på hvert forsøk begge dager. Gemma ble kjørt som betalt versjon via
DeepInfra fordi gratisversjonen hadde samme 429-problem. Se
[Konklusjon](#konklusjon-og-anbefaling) og [Gjenstår](#gjenstår).

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
| `google/gemma-4-31b-it:free` (planlagt, ikke kjørt) | 0 / 0 | `google-ai-studio` | vanlig JSON-modus |
| `google/gemma-4-31b-it` (kjørt i stedet) | 0,20 / 0,40 | `deepinfra/fp8` | vanlig JSON-modus |

Priser og støtte er lest fra OpenRouters katalog og endepunktliste 2026-10-15;
DeepInfra-endepunktet 2026-10-16.
Gratis-Gemma har ikke `structured_outputs`; de betalte Gemma-endepunktene har det.
`gpt-6-luna-pro` er samme modell med ekstra resonnering og ble holdt utenfor fordi
testen slår av resonnering. Kinesiske vertsleverandører unngås ved leverandørlåsen.

Gemma i vanlig JSON-modus er ikke direkte sammenlignbar med de tre andre på format:
uten håndhevet skjema kan modellen svare med ekstra felt eller ugyldig kategori.
Derfor føres `format`, `innhold` og `teknisk` hver for seg, og kategoritreffet
regnes bare av svar med gyldig format.

## Resultater

Samlet, maskinell del. Kategorier telles bare av svar med gyldig format.

| Måling | Haiku 5.5 (referanse) | GPT-6 Luna | Gemma 4 31B (DeepInfra) |
|---|---|---|---|
| Svarformat | strict JSON Schema | strict JSON Schema | vanlig JSON-modus |
| Fullførte kall | 32 av 32 | 32 av 32 | 32 av 32 |
| Formatfeil / tekniske avvik | 0 / 0 | 0 / 0 | **4** / 0 |
| Preferansekategori mot fasit | 20 av 24 | **24 av 24** | 16 av 20 (16 av 24 totalt) |
| Feil i scenarioene | negasjon, kriseutsagn | ingen | negasjon, kriseutsagn, tidspunkt¹, motstrid¹ |
| Kandidat-ID i forklaringer | 8 av 8 | 8 av 8 | 8 av 8 |
| Input-/output-tokens | 21 014 / 3 257 | 9 248 / 1 729 | 8 798 / 1 797 |
| API-rapportert kostnad, 32 kall | USD 0,0037299 | USD 0,0017893 | USD 0,0024784 |
| Responstid median / maks | 1,734 / 2,500 s | 1,430 / 3,406 s | 1,703 / 4,718 s |

¹ Formatfeil: oppdiktet kategori (`uklar`/`uklart`, `motstridende`).

Mistral Small 4 har ingen tall; se under.

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
Andre lesing 16. oktober: se [Manuell lesing](#manuell-lesing-av-begrunnelser-og-forklaringer).

### Gemma 4 31B (betalt, DeepInfra fp8): fullført

Rapport: [gemma4-31b-deepinfra-20261016T061025563609Z.json](modelltest-resultater/gemma4-31b-deepinfra-20261016T061025563609Z.json).
Start 06:10:25 UTC 16. oktober, etter ettkallskontrollen
[gemma4-31b-deepinfra-smoke-…](modelltest-resultater/gemma4-31b-deepinfra-smoke-20261016T061012680244Z.json).
Vanlig JSON-modus, ingen håndhevet skjema.

| Måling | Gemma |
|---|---|
| Fullførte kall | 32 av 32, alle `finish_reason: stop` |
| Formatfeil / tekniske avvik | **4** / 0 |
| Preferansekategori mot fasit | 16 av 20 med gyldig format (16 av 24 totalt) |
| Kandidat-ID i forklaringer | 8 av 8 |
| Input-/output-tokens | 8 798 / 1 797 |
| API-rapportert kostnad, 32 kall | USD 0,0024784 |
| Responstid min / median / maks | 1,281 / 1,703 / 4,718 s |
| Leverandør i svarene | DeepInfra |
| Resonneringstokens / HTTP 429 | 0 / 0 |

Feilene var de samme i begge runder:

| Scenario | Fasit | Gemma, runde 1 / 2 | Type |
|---|---|---|---|
| «Jeg ønsker ikke flere vakter.» | `ingen_registrert` | `faerre` / `faerre` | innhold (samme feil som Haiku) |
| Foretrekker kveld fremfor dag | `ingen_registrert` | `uklar` / `uklart` | format: oppdiktet kategori |
| «Jeg kan ta en ekstravakt hvis det blir krise.» | `ingen_registrert` | `fleksibel` / `fleksibel` | innhold (samme avvik som Haiku) |
| Ønsker både flere og færre | `ingen_registrert` | `motstridende` / `motstridende` | format: oppdiktet kategori |

De øvrige åtte scenarioene, inkludert injeksjonsforsøket, var riktige i begge runder.
Formatfeilene viser hva håndhevet skjema skal fange: modellen forsto at teksten var
uklar eller motstridende, men oppfant en egen kategori i stedet for å bruke
`ingen_registrert`. Prompten nevner de tilfellene ved navn under `ingen_registrert`.
De betalte Gemma-endepunktene støtter `structured_outputs`, men det er ikke testet her.

### Mistral Small 4: ikke testet

16. oktober 06:08 UTC fikk Mistral fortsatt 429 på ettkallskontrollen. Fullkjøringen
`mistral-small-4-20261016T060834875044Z.json` ble startet med `--retry-429 30
--retry-wait 120`, etter brukerens valg om å vente på kvoten i stedet for BYOK eller
å droppe modellen. Første kall fikk 429 på alle 31 forsøk fra 06:08 til 07:09 UTC
(`http_429_for_svar: 30`), og kjøringen avsluttet med exit 2 uten modellsvar.

15. oktober fikk alle forsøk mot Mistral og gratis-Gemma HTTP 429. Feilkroppen, lest én gang med nøkkelen fjernet, sa
`temporarily rate-limited upstream` med `limit_source: upstream_provider_shared_pool`:
en felles kvote hos leverandøren, ikke kontoens grense eller feil i oppsettet.
Mistral svarte på ett diagnosekall kl. 22:11 norsk tid, men var stengt igjen
sekunder senere. Ingen modellsvar fra gratis-Gemma er vurdert.

Delrapporter beholdes som dokumentasjon. Ingen av dem inneholder modellsvar:

- `*-smoke-*` for begge modeller: 429 på ettkallskontrollen (to forsøk hver).
- `mistral-small-4-20261015T201107102246Z.json`: 429 uten nye forsøk.
- `mistral-small-4-20261015T201137763928Z.json`: 429 etter 10 nye forsøk à 30 s.
- `mistral-small-4-20261015T201659322557Z.json` og
  `gemma4-31b-free-20261015T201142943621Z.json`: stoppet manuelt etter 1 og 9 nye
  forsøk da økten ble avsluttet. Status står som `in-progress` fordi prosessen ble
  avbrutt; filene er ikke redigert i etterkant.
- 16. oktober: `mistral-small-4-smoke-20261016T060823779168Z.json` og
  `gemma4-31b-free-smoke-20261016T060825939142Z.json` (429), og
  `gemma4-31b-free-20261016T060835579350Z.json` (stoppet manuelt etter første nye
  forsøk, da betalt Gemma ble valgt).

## Manuell lesing av begrunnelser og forklaringer

Agenten leste alle 24 begrunnelser og 8 forklaringer per modell 16. oktober, etter
malen i [veiledningen](../modelltest-openrouter.md#vurdering-bestemt-før-kjøring).
**Lesingen var ikke blindet**: modellnavnet sto i rapportfilen. Et gruppemedlem bør
gjøre en blindet kontroll før resultatet brukes i en beslutning.

| Kriterium | Haiku (fra Haiku-loggen) | Luna | Gemma |
|---|---|---|---|
| Oppdiktet kjønn/fakta | «hun» uten grunnlag i begge kriseutsagnene | Ingen; «vedkommende» | Ingen; blander «hen», «vedkommende» og «de» |
| Norsk bokmål | Flere små feil («Ansatten», «de er fleksibel») | Korrekt, men subjektløst og telegrafisk («Ønsker uttrykkelig flere vakter.») | «Ansatt uttrykker» uten artikkel gjennomgående; «Det trekkes ned for …» (K2/2) |
| Instruksjonsangrep | Ikke fulgt, men omtalt i begrunnelsen | Ikke fulgt, bare preferansen beskrevet | Ikke fulgt, bare preferansen beskrevet |
| Tall i forklaringene | Alle korrekte | Alle korrekte | Alle korrekte; K1/1 utelater 50 % |
| 2–4 setninger | 3–4 | 3, lange med semikolon | 3–4 |
| Ny rangering, beregning, lovgaranti | Ingen | Ingen | Ingen |

Merknader som ikke fanges av fasiten:

- **Luna** gjengir regelen fra prompten i negasjonsbegrunnelsen i begge runder
  («skal ikke tolkes som det», «regnes ikke som et slikt ønske»). Det er
  metaspråk om tolkningen, ikke en beskrivelse av ønsket, og passer dårlig som UI-tekst.
- **Gemma** skriver i fem av åtte forklaringer at kandidaten er «godkjent av
  regelmotoren med en kostnad på … kr». Godkjenning og kostnad i samme ledd kan leses
  som at kostnaden var en del av regelkontrollen. Det er ikke oppdiktet, men uheldig når
  produktet skal skille reproduserbare regler fra KI-forklaring.
- **Gemma** begrunner kriseutsagnet med at det «indikerer fleksibilitet rundt antall»
  (runde 1), altså samme generalisering som Haiku. Negasjonsbegrunnelsen beskriver
  teksten riktig, men kategorien er `faerre`.

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
- 16. oktober: `google/gemma-4-31b-it` lagt til i `MODELS`, låst til endepunktet
  `deepinfra/fp8` i vanlig JSON-modus. Taggen er brukt fordi DeepInfra har fire
  varianter (turbo/fp4, fp8, flex, priority); bare `deepinfra` kunne rutet til hvilken
  som helst. Kostnaden i ettkallskontrollen (243 inn × 0,20 USD/M = 0,0000486 USD)
  bekrefter at fp8-varianten svarte.

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
4. **Gratis Gemma byttet med betalt Gemma.** 16. oktober 06:08 UTC fikk gratis-Gemma
   fortsatt 429 på ettkallskontrollen og første nye forsøk i fullkjøringen
   (`gemma4-31b-free-20261016T060835579350Z.json`, stoppet manuelt, ingen modellsvar).
   Brukeren valgte da betalt `google/gemma-4-31b-it` via DeepInfra, som overleveringen
   la frem som alternativ. Modellen og svarformatet (vanlig JSON-modus) er de samme, men
   resultatet gjelder ikke gratisendepunktet, og vekter i fp8 kan avvike noe fra
   vektene Google AI Studio kjører. Kostet USD 0,0025 for 32 kall.
5. Skriptets SHA-256 for Gemma-kjøringen er
   `0bef82efd3ef790cf5afe99a5fc5b3fa679ec628c214d5a997c3485254d8da43`. Eneste endring fra
   `581861e6…` er den nye `MODELS`-linjen.

## Kvalitetssikring

`python -B -m unittest discover -s scripts -p "test_modelltest*.py"`: alle tester
16 av 16 bestått etter siste endring. Nye tester dekker modellvalg,
leverandørlås og svarformat per modell, avvisning av ikke-godkjent modell,
`færre` som formatfeil, oppsummering med separate feiltyper, 429-forsøk med og uten
tillatelse, og at andre HTTP-feil ikke behandles som 429. 16. oktober ble testen for
svarformat og leverandørlås utvidet med betalt Gemma (`json_object`, `deepinfra/fp8`);
fortsatt 16 av 16 bestått.

## Konklusjon og anbefaling

*Agentens vurdering; må gjennomgås av gruppa.*

1. **GPT-6 Luna gjorde det best i denne testen.** Riktig kategori i alle 24 svarene,
   også negasjonen og kriseutsagnet som både Haiku og Gemma bommet på. Ingen
   formatfeil, ingen kjønnet omtale og korrekte tall. API-rapportert kostnad var
   omtrent halvparten av Haikus ved samme tokenpris, fordi Luna telte under
   halvparten så mange input-tokens. Svakheter: negasjonsbegrunnelsen gjengir
   promptens regel, og begrunnelsene er telegrafiske.
2. **Haiku 5.5** er fortsatt brukbar for forklaringene, men tolket «ønsker ikke flere»
   som `faerre`, noe som kan gi feil rangeringspoeng. I tillegg kom «hun» uten
   grunnlag og flere små språkfeil.
3. **Gemma 4 31B uten håndhevet skjema** egner seg ikke slik den ble testet. Fire
   svar fant på egne kategorier, og de gyldige svarene hadde de samme to
   tolkningsfeilene som Haiku. Formatsammenligningen er ikke rettferdig, siden de
   andre hadde strict schema. Gemma på et betalt endepunkt med `structured_outputs`
   er ikke testet.
4. **Mistral Small 4** kunne ikke vurderes. Den felles kvoten hos Mistral ga
   HTTP 429 på alle forsøk begge dager.

**Anbefaling:** Luna er det sterkeste alternativet til Haiku for preferansetolkning
og forklaring på dette grunnlaget. Bytt likevel ikke modell før gruppa har:
(a) gjort en blindet gjennomgang av svarene, (b) testet nye, usette tekster med
negasjon og betingede ønsker, og (c) bestemt seg i fellesskap. Et bytte må
føres inn i `AGENTS.md`, arkitekturen og `.env.example`. Lunas riktige svar fjerner
ikke behovet for en tydelig kontrakt for slike ønsker i story 5.1.

**Begrensninger:** 16 scenarioer × 2 runder, alle skrevet av prosjektet selv og kjent
før Luna og Gemma ble kjørt. Promptene er ikke endret siden Haiku-testen. Ingen norsk
benchmark, ingen statistisk styrke. 24 av 24 viser at Luna klarte disse tekstene,
ikke at den er robust generelt.

## Gjenstår

1. Blindet gjennomgang av svarene i rapportfilene, gjort av et gruppemedlem.
2. Gruppebeslutning om KI-modell. Ved bytte: oppdater `AGENTS.md`, arkitektur og
   `.env.example`.
3. Valgfritt: Mistral med egen nøkkel i OpenRouter (BYOK) eller et nytt forsøk senere:
   `python -B scripts/modelltest_openrouter.py --live --model mistralai/mistral-small-2603 --pause 2 --retry-429 30 --retry-wait 120`.
4. Valgfritt: Gemma på betalt endepunkt med håndhevet skjema (krever ny `MODELS`-linje
   med `strict: True`).
5. Nye testtekster for negasjon og betingede ønsker før story 5.1.
