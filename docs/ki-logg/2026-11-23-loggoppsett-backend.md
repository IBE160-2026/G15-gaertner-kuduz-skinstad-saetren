# KI-logg: Loggoppsett for backend – appens INFO-meldinger i terminalen

Dato: 2026-11-23. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-loggoppsett-backend.md), punktet om fremdriftsmeldinger i [deferred-work.md](../../_bmad-output/implementation-artifacts/deferred-work.md) (story 5.1) og `AGENTS.md`. Arbeidet ble gjort av Claude Code (Opus 5.5) som implementeringsagent, rett på `main` (valg C, Ragnhild 2026-11-23: feilretting innenfor det utsatte punktet «Runtime-/driftslogging» i arkitekturen, som ikke er endret).

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read _bmad-output/implementation-artifacts/spec-loggoppsett-backend.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.» Spesifikasjonen har tom `context:`.

## Leveranse

- **`backend/adaptere/api/main.py`:** ny funksjon `vis_applogg_i_terminalen(strøm=None)`. Den setter loggeren `adaptere` til INFO og gir den én `StreamHandler` med formatet `%(levelname)s:     %(message)s`, merket med attributtet `_turnushjelperen_terminal`, slik at et nytt kall (også etter `importlib.reload(main)`, som en eksisterende test gjør) ikke legger til en handler til. Den kalles rett før `app = lag_app(ki=ki_fra_miljo())`. Rotloggeren, uvicorns loggere, `ki_fra_miljo()`, `lag_app` og alle eksisterende meldinger er uendret, og `propagate` er fortsatt `True`.
- **Handleren slår opp `sys.stderr` ved hver post** når ingen strøm er gitt (en liten underklasse av `StreamHandler`, som `logging.lastResort`). En vanlig `StreamHandler()` binder seg til den `sys.stderr` som gjelder ved import, og under pytest er det en fangstrøm som byttes ut. Det er ikke beskrevet i spesifikasjonen, men følger av at modulen importeres under pytest.
- **`backend/tester/api/test_terminallogg.py`:** én test i en underprosess som viser at handleren fra modulimporten skriver til ekte stderr, og sju tester med `io.StringIO`: modulimporten har gitt én handler, INFO-linjen havner i strømmen med prefikset, advarsler skrives én gang med prefiks, gjentatt kall gir samme handler og én linje, rot- og uvicorn-loggerne er uendret, DEBUG vises ikke, og `caplog` fanger fortsatt. Fiksturen fjerner testhandleren og setter tilbake den fra modulimporten.
- **`backend/tester/api/test_preferansetolkning.py`:** ny test av at `tolk_ventende` logger én «tekster venter»-linje og én «tolket»-linje per Ansatt med tekst (19), uten preferansetekstene.
- **`README.md`:** avsnittet om fremdrift er skrevet om (fremdriften vises som `INFO:`-linjer, med eksempel), den avbrutte setningen er borte, og påstanden om at knappen for nytt forsøk mangler er erstattet av en henvisning til «Prøv igjen».
- **`deferred-work.md`:** punktet er markert løst, og et nytt punkt sier at `ARCHITECTURE-SPINE.md` (linje 116 og 215) bør oppdateres ved neste arkitekturgjennomgang eller i retrospektiven for epic 5.

## Korrigering og kvalitetssikring

Rettet underveis:

1. Første versjon av testen for advarsler forventet `WARNING:  …` (to mellomrom), som uvicorn selv skriver. Formatet i spesifikasjonen gir `WARNING:     …` (fem mellomrom), fordi `%(levelname)s:     ` ikke justerer etter lengden på nivånavnet. Forventningen ble rettet til spesifikasjonens format, ikke koden. INFO-linjene er like uvicorns; WARNING og ERROR har tre mellomrom mer enn uvicorns egne.
2. Idempotensen ble først sjekket med `isinstance` mot handlerklassen. Det ville gitt to handlere etter `importlib.reload(main)` i `test_modulobjektet_app_får_adapteren_fra_miljøet`, fordi klassen da er ny. Byttet til et merke-attributt før testene ble kjørt.
3. Etter en uavhengig gjennomgang (Blind Hunter, Edge Case Hunter og Verification Gap, alle Opus 5.5, uten å ha sett implementeringen) ble fire ting rettet: (a) en ny test i underprosess viser at handleren uten oppgitt strøm faktisk skriver til ekte stderr, fordi alle de andre testene byttet den ut med en `StringIO`; (b) advarselstesten brukte et annet meldingsformat enn det `adaptere/ki/openrouter.py` faktisk logger (`Nettverksfeil mot OpenRouter: %s`), og bruker nå det ekte; (c) ingen test viste at `tolk_ventende` gir INFO-linjene README lover, så det er lagt til en i `test_preferansetolkning.py`; (d) README påsto at linjene har samme form som uvicorns (gjelder bare INFO), at tolkingen er ferdig når det har kommet én linje per tekst (tekster kan hoppes over uten linje, og endrede tekster gir «forkastet»), og sa ikke at bare tolkningen ved oppstart logger. Avsnittet sier nå dette, og ferdigsignalet er kandidatlisten igjen.

Kontroller (macOS, Python i `backend/.venv`):

- `pytest` i `backend/`: **842 bestått** før rettingene etter gjennomgangen, inkludert de sju nye og de eksisterende `caplog`-testene i `tester/api/test_preferansetolkning.py`, `tester/api/test_kandidater.py`, `tester/api/test_avveining.py` og `tester/ki/test_openrouter.py`.
- Manuell kontroll uten nøkkel: `uvicorn adaptere.api.main:app` mot en midlertidig database ga `WARNING:     Preferansetolkning er av: OPENROUTER_API_KEY er ikke satt. Se README.` én gang, før uvicorns egne linjer. Med `--reload` kom linjen også én gang.
- Etter rettingene: `pytest tester/api/test_terminallogg.py tester/api/test_preferansetolkning.py` ga **46 bestått**. Full kjøring gjøres av koordinatoren.
- Live med nøkkel (19 betalte kall) er ikke kjørt. INFO-veien dekkes av testene.

## Gjenstår

- Live-kontroll med nøkkel er valgfri etter spesifikasjonen og er ikke gjort.
