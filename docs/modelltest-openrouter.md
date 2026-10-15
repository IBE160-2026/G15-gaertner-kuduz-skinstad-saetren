# Modelltest av Haiku 5.5

Dette er et isolert forsøk før story 5.1, ikke appens KI-adapter. Python 3.12.5
brukes, kun standardbiblioteket. Kjør fra prosjektroten:

```powershell
python scripts/modelltest_openrouter.py
python -m unittest discover -s scripts -p "test_modelltest*.py"
python scripts/modelltest_openrouter.py --live
```

[Resultat og manuell vurdering fra 2026-10-15](ki-logg/2026-10-15-modelltest-haiku.md):
API/JSON og forklaringsscenarioene bestod; preferansefasiten fikk fire avvik.

Første kommando er tørrkjøring. Den siste gjør 32 betalte kall (12 preferanser og
fire forklaringer, to runder). `--repeat 1` begrenser det til 16 kall. Ingen retry.
Timeout er 45 sekunder per forespørsel og maksimum 600 output-tokens per kall.

Kopier `.env.example` til `.env` **bare dersom `.env` ikke finnes fra før**.
Sett `OPENROUTER_API_KEY` lokalt. `OPENROUTER_MODEL` kan stå tom eller være
`anthropic/claude-haiku-5.5`. Eksisterende miljøvariabler har forrang over filen.
Andre modeller avvises for å sikre at riktig modell testes. Nøkkelen skal ikke
legges i chatten, Git eller dokumentasjonen. `.env` er allerede gitignorert.

OpenRouter-kontoen må ha kreditt. En forbruksgrense på nøkkelen er ikke innbetaling.
Testen leser modellkatalogen og nøkkelens budsjett før modellkallene. Modellen må
annonsere `structured_outputs`. JSON Schema er strict; resonnering er slått av,
og leverandørfallback er slått av. `temperature` sendes ikke: parameteren er ikke
annonsert for denne modellen. Dette garanterer ikke identiske
svar. Bruk av standardbiblioteket her avgjør ikke appens senere klientbibliotek.

Fasit og prompts finnes i testskriptet og lagres sammen med hver forespørsel i
en ny rapport under `docs/ki-logg/modelltest-resultater/`. Rapporter overskrives ikke
mellom kjøringer. De inneholder svar, modell, leverandør, responstid, faktisk
API-rapportert tokenbruk/kostnad, skriptets SHA-256 og Git-baseline. Bare fiktive data
sendes. HTTP-feilkropp og autorisasjonsheader logges ikke.

## Vurdering bestemt før kjøring

- Alle svar må være gyldig JSON med nøyaktig de forventede strengfeltene, normal
  avslutning og riktig modell. Kategorier skal stemme med fasit i begge runder.
- Både preferansebegrunnelser og forklaringer leses manuelt for oppdiktede fakta,
  instruksjonsetterlevelse og uønskede beregninger. Forklaringene vurderes for
  norsk bokmål, 2–4 forståelige setninger,
  korrekte oppgitte tall, positive/negative faktorer uten nye fakta, ingen ny
  rangering/godkjenning eller påstand om full lovetterlevelse.
- «Kan ta ekstravakt», tidspunktspreferanse og «ønsker ikke flere» er konservativt
  klassifisert som `ingen_registrert`. Dette er testens eksplisitte tolkningsregel;
  endelig portkontrakt og visning av slike ønsker må avklares i story 5.1.
- En feil gir ikke automatisk nytt kall. Nettverks-/API-feil avslutter kjøringen
  med delrapport. JSON-/fasitfeil registreres og resten av scenarioene kjøres.
- Exit 0 betyr bestått maskinkontroll, **ikke** ferdig språklig/faglig godkjenning.
  Exit 1 betyr maskinelt innholdsavvik; exit 2 betyr konfigurasjons-/API-feil.
- `usage_complete` viser om API-et returnerte både tokenbruk og kostnad. Manglende
  forbrukstall skal omtales som manglende måledata, aldri som null forbruk.

Scenariene tester FR-10 og deler av FR-11/SM-7. Alle kandidatverdier er faste
testeksempler; ingen regelmotor er implementert. Testen beviser verken juridisk
korrekthet, lekkasje-invarianten i story 5.6, appens feilhåndtering eller generell
motstand mot prompt injection. Ingen utelukkede kandidater sendes til modellen.

Kilder kontrollert 2026-10-15:
[modell](https://openrouter.ai/anthropic/claude-haiku-5.5),
[JSON Schema](https://openrouter.ai/docs/guides/features/structured-outputs),
[resonnering](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens),
[kredittgrenser](https://openrouter.ai/docs/api_reference/limits).
