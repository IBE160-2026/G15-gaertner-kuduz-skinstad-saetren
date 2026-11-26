# Teknisk referanse

For dem som utvikler eller feilsøker appen. Hvordan appen installeres, startes og
testes, står i [README](../README.md). Teksten her er flyttet fra README 2026-11-23 og
kontrollert mot koden samme dag. Beslutningene bak står i
[arkitekturen](../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md)
og [beslutningsreferatet](beslutninger/avklaringspunkter.md).

## Utviklingskjøring

- `--reload` starter backend på nytt ved hver kodeendring:
  `.venv\Scripts\python -m uvicorn adaptere.api.main:app --reload`. Da logges alle ut,
  og preferansetolkningen starter på nytt for tekster som ikke er ferdige. Med live KI
  kan det gi flere betalte kall.
- Kjør backend med én worker. Låsene som samordner preferansetolkningen ved oppstart,
  «Prøv igjen» og redigering av teksten, deles ikke mellom flere serverprosesser.
- Nøkkelen som signerer innloggingen (JWT), lages tilfeldig ved hver oppstart og lagres
  ingen steder. Innloggingen ligger i en `httpOnly`-cookie.
  `TURNUSHJELPEREN_JWT_MINUTTER` må være et positivt heltall, ellers starter ikke API-et.
- Vite sender `/api` videre til `http://127.0.0.1:8000`, så backend må kjøre på den
  porten når frontend kjøres med `npm run dev`.

## Database

- SQLite via SQLAlchemy. Filen er `backend/turnushjelperen.db` (gitignorert), eller
  stien i `TURNUSHJELPEREN_DB`. En relativ sti tolkes fra arbeidsmappen.
- Fem tabeller: `turnus`, `ansatt`, `vakt`, `bruker` og `godkjenning`. Preferansetolkningene
  lagres som kolonner på `ansatt`.
- Testdatakommandoen (`python -m adaptere.lagring.testdata`) tømmer og fyller tabellene
  i én transaksjon. Den gir 25 ansatte og 506 vakter: 166 i perioden og 340 i historikken
  fra 24.08.2026. Testdataene slutter 05.10.2026 kl. 00:00.
- Det finnes ikke noe migreringsverktøy. Nye tabeller legges til automatisk, men
  endres en eksisterende tabell, må databasefilen slettes og testdataene lastes på nytt.
  En database fra før story 5.1 mangler kolonnene for preferansetolkning, og en fra før
  story 5.9 mangler `ansatt.preferanseversjon`. Begge gir «no such column».
- Transaksjonene bygger på standardoppførselen til Pythons `sqlite3`. Les docstringen
  til `lag_engine` i `backend/adaptere/lagring/database.py` før du endrer
  `isolation_level` eller `autocommit`.

## API

Alle stier begynner med `/api`. Alle krever gyldig sesjon, unntatt `GET /api/helse`,
`POST /api/innlogging` og `GET /api/innloggingsinfo`. Feil har formen
`{"kode": "…", "melding": "…"}`. Den automatiske API-dokumentasjonen (`/docs`) er slått av.
Tidspunkter sendes som ISO 8601 med offset, i `Europe/Oslo`.

| Metode og sti | Svar |
|---|---|
| `GET /helse` | `{"status": "ok"}` |
| `GET /innloggingsinfo` | Hvilken passordvariant som gjelder, uten passordet |
| `POST /innlogging` | Setter sesjonscookien. Svarer med navn, avdeling og `demomodus`. Feil brukernavn og feil passord gir samme 401. |
| `GET /meg` | Samme som innloggingssvaret |
| `POST /utlogging` | 204. Sletter cookien. |
| `GET /vaktoversikt` | Avdeling, periode, vakter som krever handling og bemannede vakter |
| `GET /vakter/{nr}` | Detaljer for en ubemannet vakt i brukerens turnus og periode |
| `GET /vakter/{nr}/kandidater` | Rangerte gyldige kandidater og `utelukkelser` (se under) |
| `GET /vakter/{nr}/kandidater/{id}` | Grunnlaget for godkjenningsflaten: vakten, kandidaten, `topprangert` og `grunnlagsmerke` |
| `POST /vakter/{nr}/kandidater/{id}` | Godkjenner. Krever `{"grunnlagsmerke": "…"}` og svarer `{"status": "godkjent"}`. |
| `GET /vakter/{nr}/kandidater/{id}/avveining` | KI-forklaringen for én kandidat |
| `POST /vakter/{nr}/kandidater/{id}/preferanse` | «Prøv igjen» for en preferanse som ikke kunne tolkes |
| `PUT /vakter/{nr}/kandidater/{id}/preferanse` | Ny preferansetekst. Krever `{"tekst": "…"}` (se under). |

**Kandidatlisten.** Svaret har én av tre statuser, alle med HTTP 200:

- `ok`: `kandidater` er bare gyldige kandidater, sortert etter `plass`. Hver kandidat har
  kompetansenivå, minutter i uka, timebelastning (prosent av 36 t, og `hoy_belastning`
  fra 32,4 t), kostnad, ulempebelastning, `totalscore`, `faktorpoeng`,
  `preferansepoeng`, `tolkestatus`, `preferansetekst` (råteksten), `grunnlagsmerke` og
  `faktorretninger`. Tallene er
  uavrundet, og frontend avrunder ved visning.
- `ingen_gyldige_kandidater`: tom liste. Regelmotoren har kjørt ferdig uten treff.
- `datafeil` med `kode: "mangler_turnusgrunnlag"` og `datagrense`: testdataene dekker ikke
  hvilen eller uka rundt vakten, så ingen kandidat er vurdert (P-08).

`utelukkelser` har `totalt`, `per_regel` og `utelukkede` med navn og årsaker. En
utelukket kandidat er aldri med i `kandidater` (NFR2).

**Godkjenning.** En utelukket, ukjent eller opprinnelig oppsatt ansatt gir samme 404
`ikke_funnet`, uten å si hvorfor (NFR2). POST kontrollerer reglene på nytt og gir 409
`endret_grunnlag`, `ugyldig_kandidat` eller `allerede_bemannet` når den ikke kan lagre.
`grunnlagsmerke` er et avtrykk av alt som påvirker vurderingen. Er det endret etter at
flaten ble hentet, må turnusansvarlig bekrefte på nytt (P-09).

**Avveining.** `{"status": "ok", "ki_kilde", "modell", "generert", "paastander"}`, der
`ki_kilde` er `live`, `forhandsgenerert` eller `mal`. Feiler KI-en eller faktakontrollen,
er svaret `{"status": "avveining_feilet"}`, og frontend viser reserveteksten. En utelukket
kandidat avvises før modellkallet.

**Prøv igjen.** Svarer `{"status": "tolket" | "feilet" | "endret"}`. 409
`tolkning_paagar` betyr at teksten allerede tolkes, 409 `ikke_feilet` at den ikke står
som feilet, og 503 `ki_utilgjengelig` at backend kjører uten KI.

**Ny preferansetekst (story 5.9, P-10B).** Bare for en gyldig kandidat for vakten; ellers
404 `ikke_funnet`, og ingenting endres. `tekst` må være en streng på høyst 500 tegn, ellers
422. Teksten trimmes, og tom tekst lagres som ingen tekst («Ingen registrert»). En endret
tekst nullstiller tolkningen og øker `ansatt.preferanseversjon` med 1 i én
skrivetransaksjon (`BEGIN IMMEDIATE`). Deretter tolkes den med samme lås og regler som
«Prøv igjen». Svaret kan derfor ta to deler: venting på låsen i høyst `LAASEVENT_S`
(100 s), og deretter selve tolkningen i høyst ett tidsbudsjett (90 s, AV-19). Svaret er
`{"status": …}`:

| Status | Betydning |
|---|---|
| `tolket` / `feilet` | Teksten er lagret og tolket, eller kunne ikke tolkes (50 poeng, «Prøv igjen» vises) |
| `uendret` | Samme tekst som den lagrede. Ingenting er endret. |
| `ingen` | Tom tekst. Lagret som «Ingen registrert». |
| `venter` | Lagret, men ikke tolket: backend kjører uten KI, eller låsen ble ikke ledig innen `LAASEVENT_S` (100 s) fordi et pågående forsøk for samme ansatt ikke var ferdig |
| `endret` | En nyere endring kom imellom. Svaret for denne teksten er forkastet. |

Hver betinget lagring av en tolkning, også ved oppstart og «Prøv igjen», sammenligner
`preferanseversjon`. Et KI-svar på en eldre versjon lagres derfor ikke, heller ikke når
teksten er endret fram og tilbake til samme verdi (A–B–A). Versjonen inngår i
`grunnlagsmerke`, så en endring mens godkjenningsflaten er åpen gir 409 `endret_grunnlag`.

## KI-integrasjonen

Koden ligger i `backend/adaptere/ki/`. KI brukes bare til å tolke preferansetekster og
forklare avveininger. Regler, arbeidstid, kostnad og rangering beregnes i
`backend/domene/` uten KI, og Rangeringen leser bare lagrede tolkninger.

### Hvilken modus backend starter i

Avgjøres én gang ved oppstart (`ki_fra_miljo` i `backend/adaptere/api/main.py`):

| Miljø | Resultat |
|---|---|
| Ingen `OPENROUTER_API_KEY` | Demo-modus, med én WARNING-linje |
| `KI_MODUS=demo` | Demo-modus, med eller uten nøkkel |
| Nøkkel satt, `KI_MODUS` tom eller `openrouter` | Live mot OpenRouter |
| Ukjent `KI_MODUS` (verdien skiller mellom store og små bokstaver, så `OpenRouter` er ukjent), nøkkel med andre tegn enn synlige ASCII-tegn, eller modellnavn med feil form | Ingen KI. Preferansene venter, og forklaringene viser reservetekst. |

`OPENROUTER_MODEL` tom gir `openai/gpt-6-luna`. Kallet bindes til leverandøren før «/».

### Preferansetolkning

- Ved oppstart tolkes ventende tekster i en bakgrunnstråd. Hver tekst får én av fem
  kategorier, og koden gir poengene: `onsker_flere` 100, `positiv_ved_behov` 75,
  `noytral` 50, `foretrekker_a_slippe` 25 og `vil_unnga` 0.
- Til en tekst er tolket, eller hvis den ikke kunne tolkes, får kandidaten midlertidig
  50 poeng (P-05). En tolkning som lagres mens godkjenningsflaten er åpen, endrer
  `grunnlagsmerke` og krever ny bekreftelse.
- Fremdriften vises i terminalen, med ansattnummer og aldri teksten eller nøkkelen:

  ```
  INFO:     Preferansetolkning: 19 tekster venter.
  INFO:     Preferansetolkning for ansatt 3: tolket.
  ```

  En tekst som er endret underveis, gir `… forkastet: teksten er endret.`. En tekst som
  ikke kunne tolkes, gir en `WARNING:`-linje med feiltypen, for eksempel `(nettverk)`.
  «Prøv igjen» og redigering skriver ingen linjer.

### Takt og nye forsøk (AD-7, AV-19)

- Høyst 18 kall i minuttet. Gruppas konto har en grense på 20 Luna-kall per minutt.
- Ved 5xx-feil og nettverksfeil prøver backend tre ganger til, etter 2, 4 og 8 s.
- Ved 429 venter backend til tidspunktet i `X-RateLimit-Reset`. Mangler overskriften
  eller kan den ikke leses, venter backend 60 s, og aldri under 1 s.
- All venting for én tekst er begrenset til 90 s.
- 402, andre 4xx-feil og svar som ikke følger formatet prøves ikke på nytt. 3xx og andre
  uventede statuser lagres som feiltypen `4xx`.
- Tallene står som konstanter i `backend/adaptere/ki/openrouter.py`.

### Demo-modus

`DemoKiAdapter` (`backend/adaptere/ki/demo.py`) bruker samme porter som live, uten
nettverk. Innholdet i `backend/adaptere/ki/demoinnhold.json` er laget med
`OpenRouterKiAdapter` og samme prompt som live: tolkninger av de 15 fasittekstene i PRD
§4.5, som dekker alle de 19 preferansetekstene i testdataene, og avveiningene for de
fire gyldige kandidatene på #4127.

- Hver forhåndsgenerert avveining faktakontrolleres på nytt mot gjeldende tall ved hvert
  oppslag (P-06). Stemmer den ikke, brukes et svar satt sammen av kode (`ki_kilde: "mal"`),
  aldri en foreldet sammenligning.
- En preferansetekst uten forhåndsgenerert treff gir «kunne ikke tolkes» med 50 poeng,
  aldri en oppdiktet kategori. Det gjelder også en tekst turnusansvarlig har endret, og
  redigeringsfeltet sier det i demo-modus (story 5.9).
- Innholdet lages på nytt fra roten med `python scripts/generer_demoinnhold.py --live`
  (19 betalte kall, se skriptets docstring). Uten `--live` er det en tørrkjøring.

### Rotsertifikater på macOS

Python på macOS kan mangle rotsertifikater. Da feiler alle live-kall etter ca. 14 s med
feiltypen `nettverk`, selv om nettet virker. Årsaken er `CERTIFICATE_VERIFY_FAILED`.
Start backend med `SSL_CERT_FILE=/etc/ssl/cert.pem` foran kommandoen. Dette er prøvd på
macOS 2026-11-16 med Python 3.15.2, men ikke sjekket på Windows.
