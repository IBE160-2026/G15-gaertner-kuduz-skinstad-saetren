---
title: 'Story 1.5: Vaktoversikt med «Krever handling»'
type: 'feature'
created: '2026-11-08'
status: 'done'
baseline_commit: '8b93aa9a3e1df0b324fc2b0d9617c0709fc32035'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/mockups/key-vaktvalg.html'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Etter innlogging viser `/turnus/kirurgisk-sengepost` bare en plassholder fra 1.3. Turnusansvarlig ser ikke hvilke vakter som mangler bemanning (FR1, UX-DR3, UX-DR5, UX-DR6).

**Approach:** Et beskyttet API gir vaktoversikten for den innloggede brukerens turnus. Vaktvalg erstatter plassholderen med brødsmulesti, «Krever handling» og bemannede vakter i tabell, etter akseptansekriteriene i story 1.5 (epics.md L345–388), UX-DR5/6 og `key-vaktvalg.html`. `epic-1-context.md` er forkortet og er ikke kilde for detaljene (valg B, Mithad 2026-11-08).

## Boundaries & Constraints

**Always:**
- Bare vakter med start i `[periode_start, periode_slutt)` vises (AV-03). Historikken vises aldri.
- API-et følger AD-4 og vernet fra 1.4. Tid sendes som ISO 8601 med offset og vises i `Europe/Oslo`.
- Rå farger og størrelser står bare i `frontend/src/stil/tokens.css` (AV-13). Innholdet har `max-width: 1180px`, og tabellen ruller i egen beholder ned til 360px (AV-14).
- «Bemannet» er en nøytral tag, aldri `ok`-farge. Mockupens «Se detaljer» tas ikke med. Ingen utropstegn i tekst (UX-DR23).
- Spørringen ligger i `adaptere/lagring`. Domenet røres ikke.

**Never:** kandidatflaten eller vaktdetaljer (story 1.6), skriving til databasen, endring av testdata eller fasit fra 1.2, KI-kall.

**Beslutninger:**
- Fotnoten bruker `sist_oppdatert` fra dataene: «Turnus oppdatert 27.09.2026 06:20 · 25 ansatte totalt i avdelingen». Mockupens 26.09 er bare et eksempel.
- Når ingen vakter mangler bemanning, vises seksjonen «Krever handling» med den nøytrale teksten «Ingen vakter krever handling nå» (UX-DR6).
- Vakttypene vises som Dagvakt, Mellomvakt, Kveldsvakt og Nattevakt.
- (Mithad, 2026-11-08) Alle bemannede vakter i perioden vises i én tabell, sortert etter start og deretter vaktnummer (164 i testdataene). Første rad i hvert nye døgn har en tykkere linje over seg (fargetoken, AV-13) og datoen i fet skrift. Datoen står på hver rad, og `row-alt` på annenhver rad beholdes. Valgt etter visuell sammenligning av variantene A, A2, B og C.
- (Mithad, 2026-11-08) «Velg vakt — finn erstatter →» navigerer til `/vakt/<nr>/kandidater`. Fram til story 1.6 viser den adressen «Fant ikke siden» fra 1.4.
- (Mithad, 2026-11-08) Tidspunktet for melding vises som «kl. 06:14» når det er samme dato som vaktens start, ellers som «26.09 kl. 21:40».
- (Mithad, 2026-11-08) Første rad i tabellen får fet dato, men ikke den tykke linjen. Linjen markerer skifte fra forrige døgn.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Uten sesjon | `GET /api/vaktoversikt` uten gyldig JWT | 401 fra vernet i 1.4, ingen data | `mangler_sesjon` |
| Testdataene | Innlogget som kari.vestby | 2 vakter under «Krever handling» (#4127, #4189), sortert etter start. Tabellen har de 164 bemannede vaktene i perioden. Ingen vaktnummer i serien #3000–#3999. | N/A |
| Varselboks | #4127 | «Vakt #4127 — Dagvakt, Kirurgisk sengepost» og «Søndag 27.09.2026 · 07:00–15:00 (8 t) · **Mangler bemanning** — Silje Amundsen meldt fra sykemeldt kl. 06:14», knappen «Velg vakt — finn erstatter →» | N/A |
| Natt over døgnskifte | #4189 | «Mandag 28.09.2026 · 23:00–07:00 (8 t) · **Mangler bemanning** — Eirik Moen meldt fra sykemeldt 26.09 kl. 21:40». Datoen er startdatoen. | N/A |
| Periodegrense | Natt 20.09 23:00–21.09 07:00 og natt 04.10 23:00–05.10 07:00 | Den første vises ikke, den siste vises | N/A |
| Brødsmulesti og fotnote | Turnus 21.09–05.10 | «Turnus > Kirurgisk sengepost > Uke 39–40, 2026» og fotnoten over | N/A |
| Ingen mangler bemanning | Testdatabase der begge vaktene er bemannet | Teksten «Ingen vakter krever handling nå», ingen tom «!»-boks | N/A |
| API eller nett feiler | 500 eller ingen kontakt | Nøytral feilmelding fra tekstlisten med «Prøv igjen». Ingen data vises. | `intern_feil`, eller ingen kontakt med API-et (frontendteksten `INGEN_KONTAKT`) |
| Tastatur | Bare tab og enter | Hver «Velg vakt»-knapp kan nås og aktiveres, og går til `/vakt/<nr>/kandidater` | N/A |
| Døgnskifte i tabellen | Første bemannede vakt i et nytt døgn | Tykkere linje over raden og datoen i fet skrift. Øvrige rader i døgnet er uendret. | N/A |

</frozen-after-approval>


## Code Map

- `backend/adaptere/api/main.py` -- `lag_app`, `Okt`, `feil`, `MELDINGER`, Pydantic-modellene og `request.state.bruker` (`Innlogget` med `id`) fra vernet i 1.4. `/api/meg` (L125) viser lesemønsteret.
- `backend/adaptere/lagring/modeller.py` -- `TurnusRad` (periode og `sist_oppdatert`), `VaktRad` med `tildelt_ansatt`/`satt_opp_ansatt`, `AnsattRad`, `BrukerRad.turnus_id` knytter brukeren til turnusen. `OsloTid` lagrer UTC.
- `backend/adaptere/lagring/brukere.py` -- mønster for oppslag (`hent_innlogget`). Ingen spørring for vakter finnes ennå.
- `backend/tester/api/test_innlogging.py` (L46–68) -- fixturene `engine` og `klient` og `logg_inn`. Gjenbrukes, ikke kopieres.
- `backend/adaptere/lagring/testdata.py` -- 166 vakter i perioden, #4127 og #4189 mangler bemanning, `SIST_OPPDATERT` 27.09.2026 06:20. Røres ikke.
- `frontend/src/App.tsx` (L130) -- viser `Startside` på `OVERSIKT_STI`. `api.ts` `kall<T>(sti, {}, true)` for beskyttet GET. `navigasjon.ts` `naviger`. `tekster.ts` er tekstlisten.
- `frontend/src/stil/tokens.css` og `app.css` -- `.innhold`, `.panel`, `.meta`, `.tag`, `.button-primary` (`width: 100%`, laget for innloggingskortet). Mangler: section-label, alert-box, tabell, row-alt, brødsmulesti, og tokens for `#f0f3f6`, `#f3e3e3` og `#f7f9fb`.
- `frontend/tester/sesjon.test.mjs` -- mønster for Node-tester med `rolldown`. `frontend/package.json` kjører i dag bare denne filen (`"test": "node --test tester/sesjon.test.mjs"`).
- `brukere.py` `hent_innlogget` (L84–89) joiner `TurnusRad`, og `BrukerRad.turnus_id` er påkrevd. En bruker uten turnus får derfor 401 fra vernet før ruten kjøres.
- `AnsattRad` har ingen kobling til turnus eller avdeling.
- `App.tsx`: `sti` er state (L17). `naviger()` endrer bare historikken. Bytte av side krever `naviger(...)` og `setSti(...)` i `App`. Mønster for generasjonssjekk (L48) og fokus på «Prøv igjen» (L24).

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/lagring/vaktoversikt.py` -- `hent_vaktoversikt(okt, bruker_id)` returnerer turnusen til brukeren:
  - avdeling, periode og `sist_oppdatert`
  - antall ansatte
  - vakter som mangler bemanning, med navnet på den som var satt opp, `meldt_fra` og grunnen
  - bemannede vakter med navn, stilling og ansiennitet

  Bare vakter med start i perioden tas med, sortert etter start og deretter vaktnummer.
- [x] `backend/adaptere/api/main.py` -- `GET /api/vaktoversikt` med Pydantic-modell. Ingen egen 404-gren, fordi en bruker uten turnus allerede får 401 fra vernet. `antall_ansatte` er antall rader i `ansatt`, siden ansatte ikke er knyttet til avdeling. Det er en kjent begrensning med én avdeling i v1.
- [x] `backend/tester/api/test_vaktoversikt.py` -- testene for matrisen på API-siden: vern, innhold, sortering, periodegrensen (#3338/#3339 vises ikke, #4265 vises), at historikken ikke vises, og at ingen mangler bemanning. For den siste settes #4127 og #4189 til `tildelt_ansatt_id` lik en ansatt, `mangler_bemanning` til falsk og `satt_opp`, `meldt_fra` og grunnen til tomme i testens egen database. CHECK-regelen krever det.
- [x] `frontend/src/api.ts` -- `hentVaktoversikt()` som beskyttet kall, med typer.
- [x] `frontend/src/format.ts` -- rene funksjoner, alt i `Europe/Oslo`:
  - ukedag og dato
  - tidsrom og varighet (reell tid)
  - periodetekst og vakttypenavn
  - linja i varselboksen
  - tidspunktet for melding etter beslutningen over
  - `erNyttDogn(forrige, denne)` etter startdato i Oslo

  Strengene bygges fra `Intl.DateTimeFormat(...).formatToParts` med `timeZone: "Europe/Oslo"`, med stor forbokstav i ukedagen og tosifret dag, måned og tid, så de ikke avhenger av ICU-versjonen.
- [x] `frontend/src/komponenter/Brodsmulesti.tsx`, `Vaktvalg.tsx`, `App.tsx` -- Vaktvalg erstatter `Startside` på `OVERSIKT_STI`. `Startside.tsx` og `TEKSTER.startside` slettes.
  - **Navigasjon:** `App` gir Vaktvalg en `onVelgVakt(nr)` som kaller `naviger(`/vakt/${nr}/kandidater`)` og `setSti(...)`. Knappen er en `<button>`.
  - **Tilstander:**
    - Under lasting vises en kort tekst fra tekstlisten.
    - 401 håndteres av `settSesjonsvarsler` fra 1.4, så Vaktvalg viser ingen egen feil.
    - Svar fra en gammel sesjonsgenerasjon overses.
    - Feil og ingen kontakt viser nøytral tekst med «Prøv igjen», og fokus settes på knappen.
  - **Brødsmulestien:**
    - Den er en full-bredde-stripe under appbaren, med innholdet begrenset til 1180 px (AV-14).
    - Den er en `<nav aria-label>`, og avdelingen står i fet skrift.
    - Den kan brukes igjen i 1.6.
  - **Overskrifter:** en visuelt skjult `<h1>` «Vaktvalg», seksjonsnavnene som `<h2>` og overskriftene i varselboksene som `<h3>`.
- [x] `frontend/src/tekster.ts`, `stil/tokens.css`, `stil/app.css` -- tekster og stiler etter UX-DR5 og DESIGN.md. Ny variant av primærknappen uten full bredde. Nye tokens i `tokens.css`:
  - farger: kolonneoverskrift `#f0f3f6`, ikonbakgrunn `#f3e3e3`, brødsmulestripe `#f7f9fb` og linja ved døgnskifte
  - faste mål: ikon 30 px, venstrekant 4 px, og polstring 14/18 i boksen og 10/18 i knappen

  Ingen rå mål i `app.css` (AV-13).
- [x] `frontend/tester/format.test.mjs` -- fester den nøyaktige teksten for:
  - ukedag og dato (#4127 «Søndag 27.09.2026»)
  - tidsrom over døgnskifte (#4189 «23:00–07:00 (8 t)»)
  - varighet over sommertidsskifte (25.10.2026)
  - periodetekst: «Uke 39–40, 2026», «Uke 39, 2026» og ved årsskifte «Uke 52, 2026 – uke 1, 2027», med ISO-ukeåret
  - vakttyper
  - tidspunktet for melding, med samme og annen dag
  - `erNyttDogn`
- [x] `frontend/package.json` -- `"test": "node --test tester/"`, så alle testfilene kjøres.
- [x] `README.md`, `docs/ki-logg/<dato>-vaktoversikt.md`, `docs/emne/vurderingsmatrise.md`, `sprint-status.yaml` -- dokumentasjon og status.

**Acceptance Criteria:**
- Given hele testpakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then består alt.
- Given innlogget i nettleseren på 360 px og 1600 px, when Vaktvalg vises, then ser flaten ut som `key-vaktvalg.html` med avvikene i kriteriene, uten vannrett siderulling.

## Implementation Notes

- 2026-11-08: `frontend/package.json` bruker `"test": "node --test"` og ikke `node --test tester/`. I Node 26 tolkes mappeargumentet som et filmønster, og da kjøres ingen tester. Uten argument finner `node --test` alle `*.test.mjs` rekursivt, utenom `node_modules`. Orkestratoren har godtatt avviket, fordi det oppfyller hensikten med oppgaven: alle testfilene kjøres.
- 2026-11-08: Implementeringsagenten kontrollerte tastatur, 360 og 1600 px og 20 px skrift i hodeløs Chrome. Feiltilstanden med «Prøv igjen» i Vaktvalg er ikke kontrollert i nettleseren. Den kan bare nås når `/api/meg` svarer, men `/api/vaktoversikt` feiler.

## Spec Change Log

## Review Triage Log

Gjennomgang av spesifikasjonen 2026-11-08, én uavhengig underagent mot koden, testdataene, epics, mockupen og DESIGN.md. Bekreftet: tallene (2 og 164), periodegrensen (#3338/#3339 og #4265), ukedagene, ISO-ukene, `sist_oppdatert`, `request.state.bruker.id`, og at API-svaret ikke lekker noe og ikke bygger noe av 1.6.

| # | Funn | Vurdering | Endring |
|---|---|---|---|
| 1 | `npm test` kjører bare `sesjon.test.mjs` | high | `package.json` er lagt til i oppgavene med `node --test tester/` |
| 2 | 404 `ikke_funnet` kan ikke nås | medium | grenen er fjernet, og 401 fra vernet er forklart |
| 3 | Det er uklart hvordan «Velg vakt» navigerer | medium | `onVelgVakt` i `App` med `naviger` og `setSti`, og `Startside` slettes |
| 4 | Lasting og feil er uklart | medium | 401 via vernet fra 1.4, generasjonssjekk, lastetekst og fokus på «Prøv igjen» |
| 5 | Datoformatet er skjørt | medium | `formatToParts` med stor forbokstav, og nøyaktig tekst festet i testen |
| 6 | Matriserader uten test | medium | rene funksjoner for linja i varselboksen og `erNyttDogn`, manuelle kontroller listet, og databasen der ingen mangler bemanning, beskrevet |
| 7 | «kl. 21:40» er misvisende for #4189 | medium | Mithad valgte dato når det er en annen dag (låst blokk) |
| 8 | Antall ansatte er ikke knyttet til avdeling | low | skrevet inn som kjent begrensning |
| 9 | Ukeformat ved kanttilfeller | low | regel og tester for én uke og årsskifte |
| 10 | Brødsmulestien og overskriftene | low | full bredde, `nav`, skjult `h1`, `h2` og `h3` |
| 11 | Tokens for faste mål og test med 20 px skrift | low | lagt til |
| 12 | Låst blokk: `INGEN_KONTAKT` og linja på første rad | low | ordlyden presisert, og Mithad valgte bare fet dato |

Kodegjennomgang runde 1, 2026-11-08: tre lag (blind-hunter BH, edge-case-hunter ECH, verification-gap VG) fikk diffen uten implementeringshistorikk. Duplikater er slått sammen per rad, og laget står i kolonnen «Lag».

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG | Formattestene tvinger ikke fram en annen tidssone enn Oslo | medium | Fjernes `timeZone` i `delformat`, består testene likevel på maskiner i Norge | patch |
| 2 | VG, BH | Radklassene i tabellen er ikke testet (`i > 0 && nyttDogn`, `row-alt`) | medium | Fjernes `i > 0`, får første rad linje, mot Mithads låste beslutning, uten at noen test feiler | patch |
| 3 | BH | Tabellbeholderen kan ikke rulles med tastatur ved 360 px | medium | `.tabellbeholder` har `overflow-x: auto`, men ikke `tabIndex`. Kolonnene Ansatt og Status kan da ikke nås med tastatur | patch |
| 4 | BH | Beviset fra nettleserkontrollen ligger ikke i repoet | medium | KI-loggen og vurderingsmatrisen viser til en kontroll som ikke kan gjenskapes | patch |
| 5 | VG, BH | 401-grenen i ruten når `hent_vaktoversikt` gir `None` er ikke testet | low | Kan bare nås ved sletting midt i en forespørsel. Rettelsen er en test med monkeypatch | patch |
| 6 | BH, VG | Periodegrensen er ikke testet nøyaktig ved 00:00 | low | Ingen vakt i dataene starter 00:00. Rettelsen er en test med syntetiske rader | patch |
| 7 | BH | Testen for offset sjekker bare `bemannet` | low | `krever_handling`, `meldt_fra`, perioden og `sist_oppdatert` er ikke sjekket | patch |
| 8 | BH | Varighet med desimaler og `varsellinje` med bare noen felt tomme er ikke testet | low | Egne grener i koden uten test | patch |
| 9 | BH | Ulik tegnsetting i tomtekstene | low | «Ingen bemannede vakter i perioden.» har punktum, men teksten i den låste delen har ikke | patch |
| 10 | BH | README beskriver testkommandoen feil, og nye linjer bryter linjebredden | low | `node --test` uten argument søker i hele `frontend/`, utenom `node_modules` | patch |
| 11 | VG, BH | Feil-, prøv-igjen- og 401-tilstandene i Vaktvalg er bare kontrollert manuelt, og feiltilstanden ikke en gang det | medium (ikke verifisert) | Krever en testrigg for komponenter, som repoet ikke har | defer |
| 12 | BH | Innledningen og «Kjøring og verifisering» i AGENTS.md er ikke oppdatert | low | Fila er agentkontekst, så endringen hører hjemme utenfor denne storien | defer |
| 13 | BH | Like tilgjengelige navn på «Velg vakt»-knappene, og pilen leses opp | low | EXPERIENCE: utvidet skjermleserstøtte er utenfor v1. Knappene er tilgjengelige med tab og enter | avvist |
| 14 | BH | Brødsmulestien mangler `ol` og `aria-current` | low | Samme avgrensning av v1 som #13 | avvist |
| 15 | BH | Valg som ikke står i spesifikasjonen (ukedag, farge, 12,5 px, tomtekst) | low | Rettelsen ville vært å endre spesifikasjonen. Valgene står i KI-loggen | avvist |
| 16 | BH | Statusen er ulik i spesifikasjonen, `sprint-status.yaml` og vurderingsmatrisen | false | Steg 5 setter `review`. Arbeidsflyten er ikke ferdig | avvist |
| 17 | BH | Fotnoten sier «i avdelingen», men teller alle ansatte | low | Ordlyden står i den låste delen (beslutning), og begrensningen er dokumentert | avvist |
| 18 | ECH | Ugyldig ISO-tid gir `RangeError` og blank side | low | API-et er vårt eget og typet, og `OsloTid` avviser naive tider. Rettelsen er en ny vakt i koden | avvist |
| 19 | ECH | `varsellinje` dropper grunn og tid når `satt_opp` er tom | low | Kan ikke skje i dataene, fordi alle tre settes sammen. Rettelsen er en ny gren | avvist |
| 20 | ECH | Året vises ikke når `meldt_fra` er i et annet år enn vakten | low | Lite sannsynlig i v1. Rettelsen er en ny gren | avvist |
| 21 | ECH | Negativ eller null varighet | low | `tidsrom()` i lagringen gir alltid 8 t | avvist |
| 22 | ECH | Periodeteksten blir baklengs når slutt er før start | low | Perioden er fast i dataene | avvist |
| 23 | ECH (påstand) | Oppgaven sier `node --test tester/` | low | Avviket er godtatt og står i Implementation Notes | avvist |
| 24 | ECH (påstand) | Ukedagen hentes ikke fra `formatToParts` | low | Mer robust enn spesifikasjonen ba om. Rettelsen ville vært å endre spesifikasjonen | avvist |

## Design Notes

API-svaret holder seg til data. All tekst og formatering lages i frontend fra tekstlisten:

```json
{"avdeling": "Kirurgisk sengepost", "periode_start": "2026-09-21T00:00:00+02:00", "periode_slutt": "2026-10-05T00:00:00+02:00",
 "sist_oppdatert": "2026-09-27T06:20:00+02:00", "antall_ansatte": 25,
 "krever_handling": [{"vaktnummer": 4127, "vakttype": "dag", "start": "...", "slutt": "...",
   "satt_opp": "Silje Amundsen", "meldt_fra": "2026-09-27T06:14:00+02:00", "grunn": "sykemeldt"}],
 "bemannet": [{"vaktnummer": 4100, "vakttype": "dag", "start": "...", "slutt": "...",
   "ansatt": {"navn": "...", "stilling": "Sykepleier", "ansiennitet": 4}}]}
```

Ukenumrene er ISO-uker regnet i `Europe/Oslo` fra `periode_start` og siste dag før `periode_slutt`. Er det samme uke, blir det «Uke N, ÅÅÅÅ». Går perioden over to ISO-år, blir det «Uke N, ÅÅÅÅ – uke M, ÅÅÅÅ». Varigheten er reell tid. Med faste vakter på 8 timer gir det «(8 t)».

## Verification

**Commands:**
- Fra `backend/`: `.venv\Scripts\python -m pytest` -- expected: alle tester består.
- Fra `frontend/`: `npm.cmd run build` og `npm.cmd test` -- expected: typesjekk, bygg og tester består.

**Manual checks:**
- Logg inn i nettleseren. Vaktvalg viser #4127 og #4189 øverst og tabellen under, og fotnoten og brødsmulestien er riktige. Det er ingen vannrett siderulling på 360 px, mens tabellen ruller i egen beholder.
- Tomtilstand: med en database der ingen mangler bemanning, vises «Ingen vakter krever handling nå» og ingen «!»-boks.
- Tastatur: tab når hver «Velg vakt», og enter går til `/vakt/<nr>/kandidater`.
- Linja ved døgnskifte: ingen linje over første rad, og en linje mellom hvert døgn.
- Standard skriftstørrelse 20 px i nettleseren: tekst i varselbokser og tabell klippes ikke (AV-13).
