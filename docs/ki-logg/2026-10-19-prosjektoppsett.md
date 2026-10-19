# Story 1.1: Prosjektoppsett som kjører fra en ren klone

Dato: 2026-10-19. Branch: `story-1.1-prosjektoppsett`. Agent: Claude Code (Claude Opus 5.5).

Dette er agentens egenrapportering. Et gruppemedlem må lese den gjennom og korrigere.

## Oppgaven

Lage backend- og frontend-skjelettet som story 1.1 beskriver
(`_bmad-output/planning-artifacts/epics.md`): FastAPI med helsesjekk og én grønn
pytest-test, React/Vite/TypeScript med en tom side med produktnavnet, mappene fra
ARCHITECTURE-SPINE § Minimal kildetre, og dokumenterte kommandoer i AGENTS.md.

## Prompten

Brukerens prompt, ordrett, etter at agenten hadde foreslått story 1.1 som neste steg:

> la oss begynne med neste steg

## Hva modellen leverte

- `backend/`: pakkene `domene/{regelmotor,porter}`, `adaptere/{api,ki,lagring}` og
  `tester/regelmotor` som tomme Python-pakker. `adaptere/api/main.py` har ett endepunkt,
  `GET /api/helse`, som svarer `{"status": "ok"}`. `tester/test_helse.py` tester det.
  Avhengighetene er låst i `requirements.txt` og `requirements-dev.txt`, og
  `pyproject.toml` setter opp pytest.
- `frontend/`: Vite-prosjekt skrevet for hånd, uten `create-vite`, slik at bare det
  storyen trenger er med. Siden viser «Turnushjelperen».
- AGENTS.md og README: kommandoer for installasjon, kjøring og test.

Ingen domenetyper eller databasetabeller er laget, slik storyen krever.

## Valg agenten tok

- **Versjoner:** FastAPI 0.141.1, React 19.3.0, Vite 8.3.1 og TypeScript 7.0.2 er låst
  eksakt slik Stack-tabellen i arkitekturen sier, selv om nyere versjoner finnes
  (blant annet FastAPI 0.148.0). Oppgradering bør være en egen beslutning.
  Verktøy som arkitekturen ikke versjonsfester (uvicorn, pytest, httpx2,
  `@vitejs/plugin-react`), er låst til siste versjon per 2026-10-19.
- **`requirements.txt` i stedet for en installerbar pakke:** backend har flere
  toppnivåpakker (`domene`, `adaptere`), og det er enklere å la pytest finne dem med
  `pythonpath = ["."]` enn å konfigurere pakking.
- **`.env.example` er ikke endret:** skjelettet leser ingen miljøvariabler.
  `KI_MODUS` og JWT-nøkkelen legges til i storiene som tar dem i bruk (5.7 og 1.3).

## Hva som ble rettet, og hvorfor

- Første utkast brukte `httpx` som HTTP-klient for FastAPIs `TestClient`. Testen var
  grønn, men Starlette ga advarselen «Using `httpx` with `starlette.testclient` is
  deprecated; install `httpx2` instead». Byttet til `httpx2==2.14.0`, og testen kjører
  nå uten advarsler.

## Kvalitetssikring

Kjørt på Windows 11 med Python 3.14.6, Node 26.7.0 og npm 11.19.0:

- `python -m venv .venv` og `pip install -r requirements-dev.txt` i et nytt miljø, og
  deretter `pytest`: 1 passed, ingen advarsler.
- `npm install` (0 sårbarheter) og `npm run build`: typesjekk og bygg uten feil.
- Begge serverne ble startet. `curl localhost:8000/api/helse` ga `{"status":"ok"}`,
  og `localhost:5173` serverte siden med tittelen «Turnushjelperen».

Ikke verifisert: kjøring på macOS/Linux og med Python 3.12, som er laveste versjon
README oppgir. Et gruppemedlem med Mac bør teste fra en ren klone.
