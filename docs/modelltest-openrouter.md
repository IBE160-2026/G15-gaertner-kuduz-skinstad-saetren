# Modelltest via OpenRouter

Gruppa valgte `openai/gpt-6-luna` 16. oktober. Denne veiledningen beskriver testverktøyet
fra 15. oktober. De senere testene har egne skript og logger, se
[Senere tester](#senere-tester). Haiku står fortsatt som standard i dette verktøyet, slik at
de loggførte kjøringene kan gjentas.

Dette er et isolert forsøk før story 5.1, ikke appens KI-adapter. Python 3.12.5
brukes, kun standardbiblioteket. Kjør fra prosjektroten:

```powershell
python scripts/modelltest_openrouter.py
python -m unittest discover -s scripts -p "test_modelltest*.py"
python scripts/modelltest_openrouter.py --live
python scripts/modelltest_openrouter.py --live --model openai/gpt-6-luna --smoke
python scripts/modelltest_openrouter.py --live --model google/gemma-4-31b-it:free --pause 4
```

Godkjente modeller og oppsett ligger i `MODELS` i skriptet:

| Modell | Leverandør låst til | Svarformat |
|---|---|---|
| `anthropic/claude-haiku-5.5` | ikke låst (første kjøring gikk til Azure) | strict JSON Schema |
| `google/gemma-4-31b-it:free` | `google-ai-studio` | vanlig JSON-modus; gratisendepunktet har ikke `structured_outputs` |
| `openai/gpt-6-luna` | `openai` | strict JSON Schema |
| `mistralai/mistral-small-2603` (Mistral Small 4) | `mistral` | strict JSON Schema |

`--smoke` sender bare første scenario én gang og kontrollerer at leverandøren godtar
oppsettet. `--pause` legger inn sekunder mellom kall for gratisendepunkter.
[Sammenligning av modellene fra 2026-10-15](ki-logg/2026-10-15-modellsammenligning.md).

[Resultat og manuell vurdering fra 2026-10-15](ki-logg/2026-10-15-modelltest-haiku.md):
API/JSON og forklaringsscenarioene bestod; preferansefasiten fikk fire avvik.

Første kommando er tørrkjøring. Den siste gjør 32 betalte kall (12 preferanser og
fire forklaringer, to runder). `--repeat 1` begrenser det til 16 kall. Ingen retry,
unntatt valgfri `--retry-429` (se under).
Timeout er 45 sekunder per forespørsel og maksimum 600 output-tokens per kall.

Kopier `.env.example` til `.env` **bare dersom `.env` ikke finnes fra før**.
Sett `OPENROUTER_API_KEY` lokalt. `OPENROUTER_MODEL` kan stå tom (Haiku) eller være
en av modellene over; `--model` har forrang. Eksisterende miljøvariabler har forrang
over filen. Modeller utenfor listen avvises for å sikre at riktig modell testes. Nøkkelen skal ikke
legges i chatten, Git eller dokumentasjonen. `.env` er allerede gitignorert.

OpenRouter-kontoen må ha kreditt. En forbruksgrense på nøkkelen er ikke innbetaling.
Testen leser modellkatalogen og nøkkelens budsjett før modellkallene. Modellen må
annonsere `structured_outputs` (strict JSON Schema) eller `response_format` (vanlig
JSON-modus). Resonnering er slått av, og leverandørfallback er slått av.
`temperature` sendes ikke til noen modell, slik at oppsettet er likt: parameteren er
ikke annonsert for Haiku og Luna. Dette garanterer ikke identiske
svar. Bruk av standardbiblioteket her avgjør ikke appens senere klientbibliotek.

Fasit og prompts finnes i testskriptet og lagres sammen med hver forespørsel i
en ny rapport under `docs/ki-logg/modelltest-resultater/`. Rapporter overskrives ikke
mellom kjøringer. De inneholder svar, modell, leverandør, responstid, faktisk
API-rapportert tokenbruk/kostnad, skriptets SHA-256 og Git-baseline. Bare fiktive data
sendes. HTTP-feilkropp og autorisasjonsheader logges ikke.

## Vurdering bestemt før kjøring

- Alle svar må være gyldig JSON med nøyaktig de forventede strengfeltene, normal
  avslutning og riktig modell. Kategorier skal stemme med fasit i begge runder.
- Avvik føres i tre grupper i `failures`: `format` (ikke JSON, feil felter, tomme
  felter eller kategori utenfor de fire lovlige), `innhold` (gyldig format, men feil
  kategori eller kandidat-ID) og `teknisk` (unormal avslutning eller annen modell-ID).
  Innhold vurderes bare når formatet er gyldig. `summary` i rapporten teller dem
  hver for seg.
- Både preferansebegrunnelser og forklaringer leses manuelt for oppdiktede fakta,
  instruksjonsetterlevelse og uønskede beregninger. Forklaringene vurderes for
  norsk bokmål, 2–4 forståelige setninger,
  korrekte oppgitte tall, positive/negative faktorer uten nye fakta, ingen ny
  rangering/godkjenning eller påstand om full lovetterlevelse.
- «Kan ta ekstravakt», tidspunktspreferanse og «ønsker ikke flere» er konservativt
  klassifisert som `ingen_registrert`. Dette er testens eksplisitte tolkningsregel;
  endelig portkontrakt og visning av slike ønsker må avklares i story 5.1.
  *Oppdatert 2026-10-16:* PRD §4.5 bruker nå fem preferansenivåer (100/75/50/25/0),
  der betinget tilgjengelighet gir 75 eller 25. Fasittesten mot den nye modellen er
  `scripts/modelltest_prd_fasit.py`.
- En feil gir ikke automatisk nytt kall. Nettverks-/API-feil avslutter kjøringen
  med delrapport. Eneste unntak er HTTP 429 med `--retry-429 N`: forespørselen er
  da avvist før modellen svarte, så et nytt forsøk kan ikke velge et gunstigere svar.
  Antall 429 føres per kall og i `summary.http_429_for_svar`. JSON-/fasitfeil registreres og resten av scenarioene kjøres.
- Exit 0 betyr bestått maskinkontroll, **ikke** ferdig språklig/faglig godkjenning.
  Exit 1 betyr maskinelt innholdsavvik; exit 2 betyr konfigurasjons-/API-feil.
- `usage_complete` viser om API-et returnerte både tokenbruk og kostnad. Manglende
  forbrukstall skal omtales som manglende måledata, aldri som null forbruk.

Scenariene tester FR-10 og deler av FR-11/SM-7. Alle kandidatverdier er faste
testeksempler; ingen regelmotor er implementert. Testen beviser verken juridisk
korrekthet, lekkasje-invarianten i story 5.6, appens feilhåndtering eller generell
motstand mot prompt injection. Ingen utelukkede kandidater sendes til modellen.

## Senere tester

| Skript | Hva | Logg |
|---|---|---|
| `scripts/modelltest_beslutning.py` | Forhåndsregistrert beslutningstest Haiku mot Luna, prompt A/B, 1 020 kall | [2026-10-16-beslutningstest-haiku-luna.md](ki-logg/2026-10-16-beslutningstest-haiku-luna.md) |
| `scripts/modelltest_robusthet.py` | Takt og nye forsøk under last, prototype for AD-7 | [2026-10-16-robusthet-luna.md](ki-logg/2026-10-16-robusthet-luna.md) |
| `scripts/modelltest_prd_fasit.py` | De 15 fasittekstene i PRD §4.5 med fem nivåer | samme logg, del 2 |

Alle er tørrkjøring uten `--live`. Testene kjøres med samme `unittest`-kommando som over.
Kjør ikke flere live-tester mot Luna samtidig: kontoen har 20 kall per minutt.

Kilder kontrollert 2026-10-15:
[modell](https://openrouter.ai/anthropic/claude-haiku-5.5),
[JSON Schema](https://openrouter.ai/docs/guides/features/structured-outputs),
[resonnering](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens),
[kredittgrenser](https://openrouter.ai/docs/api_reference/limits).
