---
title: 'Story 5.9: Redigere preferansetekst etter fungerende kjerneflyt (P-10B)'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '7aaddf6d37e0b4f4ac90149df2bceecbb1f1ae24'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-5-1-prov-igjen.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Preferansetekstene står fast i testdataene (P-10/ÅB-4). Turnusansvarlig kan ikke prøve hvordan en ny tekst tolkes og påvirker rangeringen (P-10B). Betinget lagring av tolkninger sammenligner bare tekstverdien. En endring A → B → A mens et KI-kall pågår blir derfor ikke oppdaget (`deferred-work.md`, spec-5-1-prov-igjen).

**Approach:** Turnusansvarlig kan endre en gyldig kandidats preferansetekst. Backend lagrer teksten, øker en versjon, nullstiller tolkningen og tolker den nye teksten med samme regler som «Prøv igjen». Frontend henter rangeringen på nytt. Versjonen inngår i all betinget lagring og i grunnlagsmerket. Dermed forkastes gamle KI-svar, og en åpen godkjenning får `endret_grunnlag` (P-09).

## Boundaries & Constraints

**Always:**
- Hele `/api` krever sesjon (`krev_sesjon`). Endringen avvises med 404 `ikke_funnet` hvis ansatt ikke er en gyldig kandidat for vakten, med samme kontroll som `prov_preferanse`. Da endres ingenting.
- Lagret ny tekst nullstiller `tolket_*` og `tolkefeil`, og `preferanseversjon` øker med 1, i én skrivetransaksjon (`BEGIN IMMEDIATE`). Gammel tolkning og forklaring brukes aldri for den nye teksten.
- Hver betinget lagring av en tolkning sammenligner `preferanseversjon`, både i bakgrunnstråden, «Prøv igjen» og redigeringen. Et svar på en eldre versjon lagres ikke.
- Tolkning etter endring følger AV-19 via eksisterende `ki.tolk` og den delte låsen per ansatt. Venter endringen på låsen, sjekkes versjonen på nytt før KI kalles.
- Teksten trimmes. Den kan være høyst 500 tegn (`StrictStr`). En tom tekst lagres som `None` og vises som «Ingen registrert». Samme tekst som den som er lagret, er en no-op: versjonen øker ikke, og ingenting nullstilles.
- Rangeringen beregnes fortsatt bare fra lagrede tolkninger (NFR1). Ruten for rangeringen kaller ikke KI.
- All brukertekst ligger i `src/tekster.ts`.
- **Plassering (Ragnhild 2026-11-26):** en «Endre»-knapp i preferansecellen i rangeringstabellen på kandidatflaten. Knappen åpner et tekstfelt som er forhåndsutfylt med råteksten, med «Lagre» og «Avbryt». Rangeringen hentes på nytt etter lagring.
- **Demo-modus (Ragnhild 2026-11-26):** endring er tillatt. Når appen er i demo-modus, viser tekstfeltet merknaden «I demo-modus tolkes bare de forhåndsdefinerte tekstene.»

**Never:**
- Ingen manuell overstyring av kategori (ÅB-4).
- Ingen KI-beregning av poeng eller rangering, og ingen oppdiktet kategori ved feil.
- Ingen historikk over tidligere tekster. Ingen ansattoversikt utenfor kandidatflaten.
- Ingen endring av flere tekster samtidig, og ingen delt lås mellom prosesser (v1 har én worker).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny tekst, live/fasit-KI | gyldig kandidat, ny tekst | lagret, versjon +1, tolket; `{"status":"tolket"}`; ny rangering | — |
| KI feiler endelig | ny tekst, KI gir `Tolkefeil` | `{"status":"feilet"}`; «kunne ikke tolkes», 50 poeng, «Prøv igjen» vises | ingen krasj |
| Tom tekst | `"   "` | `preferanse=None`; `{"status":"ingen"}`; «Ingen registrert» | — |
| Uendret tekst | samme som lagret | `{"status":"uendret"}`; ingenting endres | — |
| For lang / feil type | > 500 tegn eller ikke streng | 422; ingenting endres | `FEILTEKSTER` |
| Uten sesjon | ingen gyldig cookie | 401; ingenting endres (FR-13) | sesjon utløpt |
| Ikke gyldig kandidat | utelukket eller ukjent ansatt | 404 `ikke_funnet`; ingenting endres | — |
| KI av (`ki=None`) | ny tekst | lagret; `{"status":"venter"}`; «venter på tolkning» | — |
| A–B–A under KI-kall | kall på A pågår, A→B→A lagres | det gamle svaret på A forkastes (versjonen er endret); siste A tolkes | — |
| Endring mens godkjenning er åpen | merket vist før endringen | POST godkjenning gir 409 `endret_grunnlag` og krever nytt trykk | eksisterende flyt |
| Samtidig ny endring | endring 2 lagres mens endring 1 tolkes | svar 1 forkastes, `{"status":"endret"}` | `tolkEndret` |

</frozen-after-approval>

## Code Map

- `backend/adaptere/lagring/modeller.py` `AnsattRad` (66–94) -- ny kolonne `preferanseversjon: int` (standard 0). Dette er en skjemaendring, så databasen må slettes (`docs/teknisk-referanse.md` 31–35).
- `backend/adaptere/lagring/preferansetolkning.py` -- `tilstandsmerke` (96) tar med `preferanseversjon`. `lagre_resultat` (101–128) sammenligner alltid versjonen. Ny `lagre_tekst(okter, ansatt_id, tekst)` gjør endringen i én transaksjon og returnerer den nye versjonen eller `uendret`. `les_tolkning` (38) og `ventende_tekster` (82) står uendret.
- `backend/adaptere/api/main.py` -- ny `PUT /api/vakter/{nr}/kandidater/{id}/preferanse` ved siden av `prov_preferanse` (643–679). Tilgangskontrollen, `tolkelaaser`/`laasevakt` (509–510) og resultatkoden gjenbrukes. Låsen tas blokkerende med tidsavbrudd `TIDSBUDSJETT_S + 10`, og ved tidsavbrudd blir svaret `venter`. Body-modellen lages etter mønsteret i `InnloggingInn` (126). `RangertKandidatUt` får `preferansetekst: str | None` (råtekst til forhåndsutfylling). `tolk_ventende` (451–493) bruker det nye tilstandsmerket.
- `backend/adaptere/lagring/kandidatgrunnlag.py` `_grunnlagsavtrykk` (65) -- tar med alle kolonner på `ansatt` automatisk. Ikke endre den. `tester/lagring/test_grunnlagsmerke.py` krever at den nye kolonnen er klassifisert.
- `backend/adaptere/lagring/testdata.py` -- `preferanseversjon=0`. `PREFERANSER` (64) står uendret.
- `frontend/src/api.ts` -- `RangertKandidat` (72–78) får `preferansetekst`. Ny `lagrePreferanse(vakt, id, tekst)` etter `provPreferanse` (239).
- `frontend/src/Kandidatflate.tsx` -- preferansecellen (343–346) og `provPreferanseHandling` (134–158). Mønsteret med `opptatt`-ref, `visningsversjon`, `statusRef`-fokus og `hentKandidater` gjenbrukes.
- `frontend/src/api.ts` `Innlogget.demomodus` (4) -- kommer fra `/api/meg`, og `Appbar.tsx` (20) bruker den allerede. Send verdien ned til `Kandidatflate` for demomerknaden.
- `frontend/src/tekster.ts` -- nye tekster ved `provPreferanse` (177) og `tolkestatuser` (153–155).
- Tester som mønster: `backend/tester/api/test_preferansetolkning.py` (`FasitKi(før=...)` 39, 139, 459–572), `tester/api/test_godkjenningsgrunnlag.py` (`øyeblikksbilde` 61, 463, 647) og `frontend/tester/komponenter/kandidatflate.test.tsx` (603–652).

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/lagring/modeller.py`, `testdata.py` -- `preferanseversjon`.
- [x] `backend/adaptere/lagring/preferansetolkning.py` -- versjon i `tilstandsmerke`/`lagre_resultat`, ny `lagre_tekst`.
- [x] `backend/adaptere/api/main.py` -- PUT-rute, body-validering, `preferansetekst` i utdata.
- [x] `backend/tester/lagring/test_preferansetolkning.py`, `backend/tester/api/test_preferanseredigering.py` (ny) -- hver rad i matrisen, inkludert A–B–A med `FasitKi(før=...)`, samtidig endring, `øyeblikksbilde` ved 401/404/422, og `endret_grunnlag` etter endring. Rangeringen gjør ingen KI-kall.
- [x] `frontend/src/api.ts`, `Kandidatflate.tsx`, `tekster.ts`, `stil/` -- redigering i preferansecellen, med demomerknaden når `demomodus` er sann. Tastaturbruk, `aria-label` med navn, Avbryt gjenoppretter, og fokus går til statuslinjen.
- [x] `frontend/tester/komponenter/kandidatflate.test.tsx` -- lagre gir ny rangering, Avbryt, 422-feil, sen respons etter vaktbytte, `endret`, og at demomerknaden bare vises i demo-modus.
- [x] `docs/testing.md`, `docs/teknisk-referanse.md`, README «Slik bruker du appen» (én linje) og «Feilsøking» (ny database) -- dokumentasjon.
- [x] `docs/modellvalg-stories.md` -- rad 5.9 Opus. `docs/emne/vurderingsmatrise.md` -- status for 5.9.
- [x] `docs/ki-logg/2026-11-26-story-5-9-redigere-preferansetekst.md` -- KI-logg.

**Acceptance Criteria:**
- Gitt en åpen kandidatflate, når turnusansvarlig lagrer ny tekst, så viser tabellen ny status og ny rangering uten at siden lastes på nytt, og den gamle avveiningen hentes ikke for det nye merket.
- Gitt en eldre database uten `preferanseversjon`, når backend starter, så sier README hva som skal gjøres (slett databasefilen og last testdata).

### Review Findings

PR-gjennomgang 2026-11-28 (Johannes, `bmad-code-review`): fire lag på Opus (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor) mot `git diff main...02fbd9c`. 30 funn, kontrollert mot koden og gruppert: 2 decision-needed, 12 patch, 1 defer, 11 avvist. Johannes valgte å godta begge avgjørelsene (A1, B2); 11 rettelser er gjort på branchen, og sprintstatusen settes ved merge.

- [x] [Review][Decision] Cellemeldingen vises ikke når kandidaten faller under plass 5 — `radmelding` vises bare i synlige rader. Faller den endrede kandidaten ut av de fem øverste mens «Vis alle» er av, ser brukeren bare statuslinjen, akkurat i tilfellet cellemeldingen ble laget for (manuell test 2026-11-26). Valg: godta (statuslinjen sier at rangeringen er oppdatert), vis alle automatisk, eller nevn ny plass i statuslinjen. (low; Edge Case Hunter) — **Avgjort: godtatt** (Johannes, A1): statuslinjen sier at rangeringen er oppdatert.
- [x] [Review][Decision] KI-loggen mangler promptene for rettingene — «Oppgave og prompt» har bare implementeringsagentens instruksjon. Instruksjonen som ga de ni rettelsene etter gjennomgangen, og den som ga `radmelding` etter manuell test, mangler (Policy: «oppgaven, prompten …»). Bare Ragnhild vet ordlyden. (low; Blind Hunter) — **Avgjort: godtatt** (Johannes, B2): implementeringsprompten og rettelsene er beskrevet, som i KI-loggen for 5.8.
- [x] [Review][Patch] Lekkasjetesten ser bort fra alle toppnivåfelt utenom `kandidater` og `utelukkelser` [backend/tester/api/test_kandidater.py:177] — `status` og ethvert framtidig felt er utenfor ordkontrollen, og KI-loggens «Kontrollen gjelder fortsatt alle andre felt» stemmer ikke. Fjern bare `preferansetekst` fra en kopi av hele `svar`. (medium; Blind Hunter)
- [x] [Review][Patch] Cellemeldingen kommer tilbake etter Avbryt [frontend/src/komponenter/Kandidatflate.tsx:282] — `onApne` og `onLukk` nullstiller ikke `radmelding`, så «Lagret og tolket nå.» vises igjen etter Endre → Avbryt, og blir stående på Jonas mens Mette redigeres. (low; Edge Case Hunter, Verification Gap)
- [x] [Review][Patch] Testen «meldingen forsvinner ved neste handling» fanger ikke at den ikke nullstilles [frontend/tester/komponenter/kandidatflate.test.tsx:749] — den åpner Jonas' eget felt, som skjuler meldingen via `redigering.id !== r.id`. Begge `setRadmelding(null)` kan slettes uten at testen blir rød. (low; Verification Gap)
- [x] [Review][Patch] AK1 er bare testet når kandidaten mister plass 1 [frontend/tester/komponenter/kandidatflate.test.tsx:697] — Jonas flyttes til plass 2 med uåpnet panel, så «gammel avveining hentes ikke» følger av seg selv. Mangler: kandidaten blir på plass 1 med åpent panel og nytt merke. (low; Acceptance Auditor)
- [x] [Review][Patch] Ingen test av PUT på en vakt med Datafeil [backend/adaptere/api/main.py:707] — `not isinstance(vurdering, Datafeil)` i `gyldig_kandidat` er ikke dekket; uten den blir 404 til 500 (#4261–#4265). (low; Blind Hunter)
- [x] [Review][Patch] Dokumentasjonen sier ikke når en `venter`-tekst tolkes [docs/teknisk-referanse.md:107] — det skjer først ved neste oppstart, fordi «Prøv igjen» bare godtar `feilet`. README sier heller ikke at endrede tekster blir stående til testdataene lastes på nytt (steg 2). (low; Blind Hunter)
- [x] [Review][Patch] Raden for 5.9 i testing.md mangler flyter som er testet [docs/testing.md:158] — «ett felt om gangen», 404 («ikke lenger gyldig») og demomerknaden via `<App />`. (low; Blind Hunter)
- [x] [Review][Patch] modellvalg-stories.md bruker P-10B som eksempel på en story som ikke står i tabellen [docs/modellvalg-stories.md:50] — rad 5.9 (P-10B) står nå i tabellen. (low; Blind Hunter)
- [x] [Review][Patch] KI-loggen oppgir ikke full testkjøring etter rettingene [docs/ki-logg/2026-11-26-story-5-9-redigere-preferansetekst.md:63] — «Full kjøring gjøres av koordinatoren» uten tall; 929 / 90 står bare i specen og sesjonsloggen. (low; Blind Hunter)
- [x] [Review][Patch] Vurderingsmatrisen sier at nettleserkontrollen gjenstår [docs/emne/vurderingsmatrise.md] — live- og demotest i nettleseren ble gjort 2026-11-26, og PR #42 finnes. Oppdateres ved merge. (low; Blind Hunter)
- [ ] [Review][Patch] Sprintstatus må settes til `done` ved merge [_bmad-output/implementation-artifacts/sprint-status.yaml:80] — AGENTS.md (i PR-en) sier 5.1–5.9 er ferdige, mens raden står på `review` uten PR-kommentar som de andre i epic 5. (low; Blind Hunter, Acceptance Auditor)
- [x] [Review][Patch] Sesjonsloggen teller 8 avviste funn; Review Triage Log har 9 [.logs/ragnhild/969-2026-11-26-09-03-19-story-5-9-redigere-preferansetekst.md:20] — 9 + 9 + 1 = 19. (low; Blind Hunter)
- [x] [Review][Defer] Ingen frontendtest av 401 på de beskyttede preferansekallene [frontend/src/api.ts:249] — deferred: samme hull finnes for `provPreferanse` fra 5.1; lukkes best med én `<App />`-test for begge.

**Avvist:**
- `false` — Sesjonsloggens åpne punkter motsier `issues.md` (Blind): `issues.md` er den autoritative listen og er oppdatert; sesjonsloggen er et øyeblikksbilde.
- `false` — No-op-sammenligningen feiler for lagret tekst med blanke i kantene (Edge): alle 15 tekster i testdataene er trimmet, og `lagre_tekst` normaliserer.
- `false` — `ki.tolk` kan kaste etter at teksten er lagret (Edge): adapterne returnerer `Tolkefeil`; ingen vist vei kaster, og mønsteret er det samme som i `prov_preferanse`.
- `false` — Endringen av `lagre_tekst`-signaturen avviker fra Code Map (Acceptance): rettingen ville være å endre specen.
- `low` — PUT tolker på nytt uten å sjekke at tolkningen venter (Acceptance): krever en PUT før oppstartstråden leser listen, og etter omstart må brukeren logge inn på nytt; i praksis uoppnåelig.
- `low` — Grensen på 500 tegn sjekkes før trimming (Acceptance): avvist før som #13; feltet har `maxLength={500}`.
- `low` — 500/nettverksfeil etter lagret tekst gir feilflate (Edge): som #16; «Prøv igjen» på feilflaten viser den lagrede teksten.
- `low` — To faner kan overskrive hverandres tekst (Edge): én turnusansvarlig; retting krever nytt felt i API-et.
- `low` — Tekst av bare usynlige tegn lagres (Edge): lite sannsynlig, og retting krever ny vakt.
- `low` — Ingen test for database fra mellom 5.1 og 5.9 (Blind): AK2 gjelder README, som dekker det (`README.md`, «Feilsøking»).
- `low` — Ny flate for prompt-injeksjon (Blind): teksten kommer fra innlogget turnusansvarlig, og svaret er bundet til kategoriene i `PREFERANSEPOENG` via strengt skjema og validering.

## Implementation Notes

2026-11-26: Backend, frontend og dokumentasjon implementert. 929 backendtester (inkludert arkitektur og ruff), frontendbygg, 52 modultester og 87 komponenttester bestod. Mutasjoner og valg som spesifikasjonen ikke avgjorde, står i [KI-loggen](../../docs/ki-logg/2026-11-26-story-5-9-redigere-preferansetekst.md). API-et er prøvd mot ekte backend i demo-modus med `curl`. Nettleserkontrollen (OP-16) og live mot Luna gjenstår.

2026-11-26, etter gjennomgangen: ni rettelser fra Review Triage Log (patch) er gjort av implementeringsagenten. Orkestratoren kjørte full verifisering: 929 backendtester, frontendbygg, 52 modultester og 90 komponenttester bestod. Den nye 404-testen ble rød da 404-grenen i `lagrePreferanseHandling` midlertidig ble slått av; koden er tilbakestilt.

2026-11-26, manuell test live mot Luna (Ragnhild, macOS): redigering, ny rangering, «uendret», Avbryt, Esc og tom tekst virket, også i smalt vindu. Funn: statuslinjen over tabellen ble ikke lagt merke til fordi kandidaten flyttet seg. Ragnhild valgte å rette i storyen: kort melding også i preferansecellen (`radmelding`, `rp.rad`), ny komponenttest (rød med visningen slått av). Bygg, 52 modultester og 91 komponenttester bestod. Retestet i nettleseren.

## Review Triage Log

Tre lag kjørt parallelt 2026-11-26 (Blind Hunter, Edge Case Hunter, Verification Gap Reviewer), alle på Opus. Funnene er kontrollert mot koden av orkestratoren; gjennomgåernes alvorlighetsgrad er ikke brukt.

| # | Funn (kilde) | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|
| 1 | PUT 404/401/500 erstatter hele listen med feiltilstand og forkaster utkastet; ingen test (Blind, Edge, VG) | medium | `lagrePreferanseHandling` sender alt utenom 422 til `tilstandFraFeil`. 404 er realistisk når kandidaten blir ugyldig mens feltet er åpent (`lagre_tekst` med `gyldig_kandidat`). | patch |
| 2 | «Høyst ett felt åpent» har ingen test (Blind, VG) | low | Ekte testhull: alle tester åpner bare Jonas. Direkte tillegg av én test. | patch |
| 3 | Demomerknaden er ikke testet gjennom `<App />` (VG) | low | Ekte: bare `Kandidatflate` med prop satt for hånd; fjernes `demomodus={bruker.demomodus}` i `App.tsx`, består alle tester. | patch |
| 4 | Esc lukker ikke når fokus står på Lagre/Avbryt (Edge) | low | `onKeyDown` ligger bare på `textarea`. Direkte flytting til `form`. | patch |
| 5 | Endringen gjelder den ansatte i alle vakter, men det står ingen steder (Blind) | low | `preferanse` ligger på `ansatt`. Hjelpeteksten gir inntrykk av lokal endring. Direkte tekstretting. | patch |
| 6 | README steg 2 lover tolkning, men demo gir «kunne ikke tolkes» for ny tekst (Blind) | low | README 131–132; sensor bruker demo. Direkte tekstretting. | patch |
| 7 | Dokumentert ventetid «innen 100 s» er feil (opptil låsevent + ett tidsbudsjett); testen avhenger av «+10» (Blind) | low | `teknisk-referanse.md` 105; `test_låsen_blir_ikke_ledig_i_tide_gir_venter` setter `TIDSBUDSJETT_S=-9.95`. Rettes med egen konstant og riktig tekst. | patch |
| 8 | CSS-regelen endrer avstanden over «Prøv igjen» fra 5.1 (Blind) | low | `.preferansecelle > .button-kompakt` treffer begge knappene. Tilsiktet lik avstand, men skal med i manuell kontroll. | patch |
| 9 | KI-loggen mangler avsnitt om hva som ble rettet (Blind) | low | Policy i AGENTS.md krever det. Direkte tillegg etter denne runden. | patch |
| 10 | «venter» etter tidsavbrudd på låsen er en blindvei til omstart (Blind) | low | Ekte, men krever at et annet forsøk for samme ansatt varer over 100 s, mens tidsbudsjettet er 90 s. Rettingen krever ny gren eller endret «Prøv igjen». | avvist (lite sannsynlig) |
| 11 | Ingen historikk over tidligere tekster (Blind) | false | Intensjonen utelukker det: «Ingen historikk over tidligere tekster» (Never). | avvist |
| 12 | Råtekst sendes for alle kandidater, og lekkasjetesten er svekket (Blind) | low | Turnusansvarlig har tilgang til teksten, og dataene er fiktive. Fritekst kan inneholde «vakter», så unntaket er riktig avgrenset til feltet. | avvist |
| 13 | 500 tegn kontrolleres før trimming, og innlimt tekst kuttes uten beskjed (Blind, Edge) | low | Ekte, men `maxLength={500}` i feltet hindrer at mer enn 500 tegn sendes; bare ytterkanter er berørt. Tegnteller er ny funksjon. | avvist (lite sannsynlig) |
| 14 | AGENTS.md er ikke oppdatert (5.8/5.9-status, ny database) (Blind) | low | Ekte. Gjelder agentkontekst. | defer |
| 15 | Kandidaten kan bli ugyldig mens PUT venter på låsen; KI kalles likevel (Edge) | low | Ekte, men teksten er allerede lagret på `ansatt`, og tolkningen gjelder den ansatte, ikke vakten. Koster ett KI-kall i et sjeldent tilfelle. | avvist (lite sannsynlig) |
| 16 | PUT lyktes, men ny henting feiler: brukeren vet ikke at teksten er lagret (Edge) | low | Samme mønster som «Prøv igjen»; krever nettverksfeil rett etter et vellykket kall. Retting gir ny gren. | avvist (lite sannsynlig) |
| 17 | Åpent felt mister utkastet når «Prøv igjen» på en annen rad endrer merket (Edge) | low | Ekte (raden monteres på nytt), men krever at brukeren forlater et åpent felt for å prøve en annen rad. Retting krever å løfte utkastet. | avvist (lite sannsynlig) |
| 18 | `redigerId` kan peke på en skjult rad og åpne seg igjen (Edge) | low | Bare via «Vis bare de 5 øverste» mens feltet er åpent. | avvist (lite sannsynlig) |
| 19 | Påstanden «samme regler som Prøv igjen» er misvisende (Edge, påstand) | false | Påstanden gjelder AV-19-reglene via `ki.tolk`, som er like. At PUT venter på låsen, er et valg i Code Map. | avvist |

## Design Notes

Versjonen lukker A–B–A, fordi tekstverdien ikke er nok. Hver endring gir et nytt tall, og den betingede `UPDATE … WHERE preferanseversjon = ?` treffer bare den versjonen svaret ble bestilt for. Versjonen ligger på `ansatt`, så P-09 gir `endret_grunnlag` uten ny kode.

## Verification

**Commands:**
- `cd backend && .venv/bin/python -m pytest` -- expected: alle grønne, inkludert arkitektur og ruff
- `cd frontend && npm run build && npm run test` -- expected: grønt bygg, alle tester bestått

**Manual checks (if no CLI):**
- Ekte backend i demo-modus og live: endre en kjent og en ukjent tekst, og se status og rangering. Smale vinduer (680/960 px), tastatur, fokus og farger etter sjekklisten i `docs/testing.md`.
