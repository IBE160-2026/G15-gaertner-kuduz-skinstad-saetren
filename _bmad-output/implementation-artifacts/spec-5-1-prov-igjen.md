---
title: 'Story 5.1: Prøv preferansetolkning igjen'
type: 'feature'
created: '2026-11-19'
status: 'done'
route: 'dispatch'
baseline_commit: '57ae8ee8a9702972838dce8c11878be9e4a9d3a6'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Etter endelig feil kan turnusansvarlig ikke be om ny preferansetolkning uten å starte backend på nytt. Dette gjenstår i story 5.1 (FR-10, P-05/OP-03).

**Approach:** Vis «Prøv igjen» ved den feilede kandidatens preferanse, og la et beskyttet endepunkt starte et nytt forsøk. Oppdater hele rangeringen når resultatet foreligger.

## Boundaries & Constraints

**Always:** Råtekst beholdes; venting eller feil gir midlertidig 50 poeng og utelukker ikke kandidaten. Tolkning utføres bare av KI-adapteren, aldri av rangeringen. Eksisterende felles adapter og begrenser brukes for både oppstart og brukerforsøk. Ingen transaksjon holdes under KI-kall, og resultat for endret tekst forkastes. P-09: lagret sluttresultat inngår i grunnlagsmerket; endret grunnlag krever ny bekreftelse. AD-7s begrenser og AV-19s vedtatte feilregler gjelder; Kim bekreftet 2026-11-19 at AV-19 legges til grunn til tross for foreldet formulering i AD-7. Statusendringer i brukerflaten må være tilgjengelige med tastatur og skjermleser, og sene svar må ikke oppdatere en annen visning eller sesjon.

**Never:** Ingen live-kall i tester, hemmeligheter, endringer i beregningsregler eller KI-basert filtrering. Ikke lagre mellomliggende forsøk som beslutningsgrunnlag. Ikke marker story 5.1 ferdig før krav og kontroller er oppfylt.

## I/O & Edge-Case Matrix

| Situasjon | Tilstand / handling | Forventning |
|---|---|---|
| Nytt forsøk lykkes | Feilet kandidat; brukeren trykker | Vis pågående tilstand, lagre resultat, hent rangeringen på nytt og vis oppdaterte poeng og rekkefølge før bekreftelse. |
| Nytt forsøk feiler | KI gir endelig feil | Behold råtekst og feilstatus, 50 poeng; vis forståelig tilbakemelding og tillat nytt forsøk. |
| KI utilgjengelig | Ingen aktiv adapter | Gi forståelig beskjed uten å late som forsøket startet eller endre lagrede data. |
| Samtidige forsøk | Dobbeltklikk, flere forespørsler eller oppstartssnapshot | Høyst ett aktivt forsøk per ansatt; eldre arbeid kan ikke overskrive nyere resultat. Revalider tilstand etter tilgang til arbeidet. |
| Tekst endres | Teksten endres under kall | Forkast gammelt svar; hent oppdatert grunnlag. |
| Ugyldig tilgang | Uinnlogget, annen turnus, ukjent eller ugyldig kandidat | Avvis med eksisterende sikkerhets- og feilkonvensjoner; ingen KI-kall. |
| Godkjenning åpen | Ny tolkning lagres før bekreftelse | Eksisterende grunnlagskontroll gir 409 og krever ny bekreftelse. |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py` — `tolk_ventende`, `lag_app`, kandidat- og godkjenningsrutene; gjenbruk autentisering, tilgangskontroll og appens KI-adapter. Oppstart tar et snapshot som må revalideres.
- `backend/adaptere/lagring/preferansetolkning.py` — `les_tolkning`, `ventende_tekster`, `lagre_resultat`; behold betinget lagring og beskytt mot eldre resultat for samme tekst.
- `backend/adaptere/ki/` — eksisterende adapter og begrenser; ikke opprett en ny adapter per forespørsel.
- `frontend/src/komponenter/Kandidatflate.tsx` — `Kandidatliste`, `Rangeringstabell`, `Kandidatrad` og preferansecellen; oppdater hele listen uten å miste nødvendig fokus eller godta utdaterte svar.
- `frontend/src/api.ts`, `kandidater.ts`, `tekster.ts` og relevante stilfiler — eksisterende autentisert kall, sesjonsvern, lastelogikk og sentrale tekster/tokens.
- `backend/tester/api/test_preferansetolkning.py`, `frontend/tester/komponenter/kandidatflate.test.tsx` — falsk KI, hendelsesstyrt samtidighet og komponenttester; gjenbruk eksisterende hjelpefunksjoner.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py`, `backend/adaptere/lagring/preferansetolkning.py` — implementer beskyttet retry og samordning med oppstart og konkurrerende forespørsler; dekk matrisen med deterministiske backendtester.
- [x] `frontend/src/komponenter/Kandidatflate.tsx`, `api.ts`, `tekster.ts` og stil — legg til tilgjengelig retry, tilbakemelding og oppfriskning; dekk nye koblinger og tilstander i komponenttester.
- [x] `docs/testing.md`, `docs/ki-logg/`, `deferred-work.md`, story- og sprintstatus — dokumenter faktisk resultat, KI-bruk og kontroller; lukk status først ved dokumentert oppfyllelse.
- [x] `_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md` — samordne den foreldede AD-7-teksten med vedtaket AV-19.
- [x] Oppdater vurderingsmatrisen med lenker til faktiske bevis og dokumenter relevante manuelle kontroller eller åpne punkter.

**Acceptance Criteria:**
- Gitt en innlogget turnusansvarlig og en gyldig kandidat med feilet tolkning, når nytt forsøk lykkes, så oppdateres poeng og rangering før kandidaten kan bekreftes.
- Gitt et pågående eller foreldet forsøk, når et annet forsøk eller en tekstendring inntreffer, så lagres ikke et foreldet resultat over det gjeldende.
- Gitt en åpen godkjenningsflate, når tolkningen endres før bekreftelsen, så krever systemet ny bekreftelse etter P-09.
- Gitt backend- og frontendtestene, når de kjøres uten nettverk og KI-nøkkel, så består de inkludert de nye feil- og samtidighetstestene.

## Implementation Notes

2026-11-19: Backend og frontend implementert. 683 backendtester bestod; deretter ble to tilgangstester lagt til og alle 35 tester i preferansesuiten bestod. Frontendbygg, 52 modultester og 46 komponenttester bestod. Manuell kontroll gjenstår (OP-16).

Etter gjennomgangsrettingene bestod alle 685 backendtester, frontendbygg, 52 modultester og 46 komponenttester. Story 5.1 sendes til gjennomgang; manuell kontroll av layout, farger, fokus og ekte backend er et åpent punkt.

## Spec Change Log

## Review Triage Log

Gjennomgang 2026-11-19: blind gjennomgang (B), grensetilfeller (G) og testhull (T).

| Funn | Vurdering og tiltak |
|---|---|
| B1 Lås deles ikke mellom prosesser | medium: reelt ved flere workers; v1 kjøres med én worker. Begrensningen er nå eksplisitt i README og må løses før flerprosessdrift. |
| B2 Lik feiltype kan gi ABA mellom prosesser | medium: samme rotårsak som B1; verdibasert kontroll oppdager ikke identisk mellomliggende verdi. Flerprosessdrift krever vedvarende versjon/lås. |
| B3 Tekst A–B–A under kall | medium: verdibasert kontroll kan ikke se mellomliggende endring; ingen tekstredigering finnes i dagens app. Må dekkes når story 5.9 innfører redigering. |
| B4 KI utilgjengelig erstatter listen med feilflate | low: bekreftet; brukeren får beskjed og kan laste listen på nytt. Dette sikrer også at usikkert POST-utfall ikke brukes som gammelt grunnlag. |
| B5 Fokus flyttes etter langt kall | medium: bekreftet og rettet; status annonseres uten å stjele fokus som brukeren har flyttet. |
| B6 Test viser ikke endret rekkefølge | medium: bekreftet; komponenttesten bruker nå to kandidater og kontrollerer byttet rekkefølge. |
| B7 Oppstartssnapshot uten faktisk brukerforsøk | medium: bekreftet testhull; test med faktisk lifespan og manuelt forsøk er lagt til. |
| B8 Ugyldig referanse til utelukket ansatt manglet i ny epic-kontekst | medium: bekreftet; opprinnelig kontekst er beholdt med kun AV-19 oppdatert. |
| B9 Konkrete ki_kilde-verdier manglet i konteksten | medium: bekreftet; opprinnelig kontekst er beholdt. |
| B10 ÅB-8 og 5.9-avgrensning manglet i konteksten | medium: bekreftet; opprinnelig kontekst er beholdt. |
| G1 Samme feiltype i konkurrerende prosesser kan overskrives | medium: samme rotårsak og begrensning som B1–B2; flerprosessdrift er ikke støttet. |
| T1 Oppdatert rekkefølge ikke testet | medium: samme testhull som B6; rettet og kjørt. |

## Verification

**Commands:**
- `cd backend && .venv\Scripts\python -m pytest` — alle tester består.
- `cd frontend && npm.cmd run build` og `npm.cmd run test` — bygg og tester består, sekvensielt.

**Manual checks:** Kontroller udekkede visuelle forhold i representative smale vinduer, farger, fokus og ekte backend etter OP-16/AV-17; dokumenter faktisk resultat eller åpne punkter.
