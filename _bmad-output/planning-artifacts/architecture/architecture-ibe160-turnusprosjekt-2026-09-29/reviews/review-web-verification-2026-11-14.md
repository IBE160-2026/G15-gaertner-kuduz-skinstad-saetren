# Teknologi- og realitetskontroll — 2026-11-14

## Dom

De sentrale teknologiene finnes og de fastlåste pakkene samsvarer i hovedsak med repoet. Arkitekturen har likevel én tydelig utdatert stackopplysning og to formuleringer som kan styre senere implementasjon feil. Kontrollen er statisk; ingen live KI-kall eller full testkjøring er gjort.

## Funn

### 1. SQLAlchemy er allerede versjonsfestet, mens arkitekturen sier at versjonen er åpen

- **Sted:** `ARCHITECTURE-SPINE.md` § Stack og § Deferred («SQLite-skjema/migreringsverktøy»).
- **Bevis:** `backend/requirements.txt` låser `sqlalchemy==2.1.6`. [SQLAlchemys utgivelser](https://github.com/sqlalchemy/sqlalchemy/releases) bekrefter at 2.1.6 eksisterer; nyere 2.1.8 er ute per 2026-11-14. Det er ingen grunn til å kreve oppgradering bare av den grunn.
- **Konsekvens:** En story som følger arkitekturen kan velge en annen versjon eller tro at avhengigheten ennå ikke er bestemt, mens CI og appen bruker 2.1.6.
- **Forslag:** Oppdater stackraden til `SQLAlchemy 2.1.6` som observert kodevalg, og fjern «eksakt SQLAlchemy-versjon» fra Deferred. La migreringsspørsmålet stå åpent.

### 2. «Låst til leverandøren openai» er ikke håndhevet av det som er beskrevet

- **Sted:** `ARCHITECTURE-SPINE.md` § Stack, OpenRouter-raden.
- **Bevis:** [Modellens leverandørside](https://openrouter.ai/openai/gpt-6-luna/providers) viser også Azure og Amazon Bedrock. [OpenRouters leverandørvalg](https://openrouter.ai/docs/guides/routing/provider-selection) beskriver egen `provider`-styring for å binde forespørselen til én leverandør. Modell-ID-en alene er ikke en slik binding. `backend/adaptere/ki/` inneholder ennå ingen implementasjon som setter provider-valg.
- **Konsekvens:** Senere KI-adapter kan bruke modell-ID-en og likevel rute gjennom flere leverandører, i strid med dokumentets påstand. Det kan gi forskjellig oppførsel fra den forhåndstestede leverandøren.
- **Forslag:** Hvis OpenAI-leverandør er et faktisk vedtak, spesifiser `provider`-kravet i AD-7 eller konvensjonen og test det i adapteren. Hvis ikke, rett stackbeskrivelsen til «modell-ID valgt; leverandørruting ikke bundet» og avklar om dette påvirker tidligere modelltest.

### 3. AD-3 legger cookie-lagring til feil komponent

- **Sted:** `ARCHITECTURE-SPINE.md` AD-3 Rule.
- **Bevis:** `backend/adaptere/api/sesjon.py` setter `httpOnly`-cookie med `Response.set_cookie`; `frontend/src/api.ts` sender `credentials: "same-origin"` og kan ikke lese tokenet. Dette er også [FastAPIs dokumenterte cookie-mønster](https://fastapi.tiangolo.com/advanced/response-cookies/).
- **Konsekvens:** Ordlyden «`adaptere/web` lagrer det i en `httpOnly`-cookie» kan få en senere story til å forsøke å sette tokenet fra React, som ikke kan sette `HttpOnly`-flagget.
- **Forslag:** Skriv at API-et setter cookien, nettleseren lagrer og sender den, og webklienten bruker `credentials: "same-origin"`.

## Verifisert uten funn

- FastAPI 0.141.1, React 19.3.0, Vite 8.3.1, TypeScript 7.0.2, Vitest 5.1.0, Testing Library-versjonene og jsdom 28.1.0 er låst i prosjektets manifestfiler som arkitekturen oppgir. Dette er en kontroll av faktisk oppsett, ikke en anbefaling om nyeste pakke.
- [jsdom 29.0.0 sitt manifest](https://raw.githubusercontent.com/jsdom/jsdom/v29.0.0/package.json) krever minst Node 22.13.0 i 22-serien; begrunnelsen for 28.x ved prosjektets Node 22.12-gulv er riktig.
- [OpenRouters modellside](https://openrouter.ai/openai/gpt-6-luna/) bekrefter modell-ID, oppgitt pris og støtte for strukturert JSON-utdata per kontrolltidspunktet. Pris er tidsavhengig og bør ikke forstås som et varig arkitekturkrav.
- Authkoden realiserer JWT med tilfeldig signeringsnøkkel per oppstart, 480 minutter som standard og `httpOnly`-cookie. Importkontrakten ligger i `backend/pyproject.toml` og arkitekturtesten i `backend/tester/test_arkitektur.py`.
