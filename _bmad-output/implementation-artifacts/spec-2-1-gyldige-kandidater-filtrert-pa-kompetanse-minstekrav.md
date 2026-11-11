---
title: 'Story 2.1: Gyldige kandidater filtrert på kompetanse-minstekrav'
type: 'feature'
created: '2026-11-11'
status: 'done'
baseline_commit: '75f260f65d2ba9f43bf7c72e53da8302a0626662'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/AGENTS.md'
  - '{project-root}/docs/beslutninger/avklaringspunkter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kandidatflaten fra story 1.6 viser bare en plassholder. Turnusansvarlig må derfor selv sjekke kompetansen til alle 24 mulige kandidater (FR2).

**Approach:** Legg inn den første harde regelen i en ren domenekjerne (`domene/`). Den vurderer alle Ansatte unntatt den som var satt opp, og samler alle årsaker per Kandidat. Et nytt beskyttet endepunkt gir de Gyldige kandidatene alfabetisk, og flaten viser dem med nivå-tag. Storien legger også grunnmønsteret som 2.2–2.6 bygger videre på: domenetyper, regelliste, import-linter, API-kontrakt og datafeil-stopp.

## Boundaries & Constraints

**Always:**
- Kompetanse: gyldig når `kompetanse[nøkkel] >= minstenivå`. Nøkkelen er vakttypen, men `mellom` bruker `dag` (AV-02). Manglende nøkkel gir utelukkelse med årsaken `kompetanse-minstekrav`. Minstekravet senkes aldri.
- Kandidatgrunnlaget er alle rader i `ansatt` unntatt `satt_opp_ansatt_id`. Tabellen har ingen `turnus_id`, og v1 har én turnus (AV-06).
- Regelmotoren er ren Python. Den får alle data som argumenter og bruker verken klokke, database, nett eller KI. Samme input gir samme output.
- Hver Kandidat vurderes mot alle reglene i regellisten, og alle årsakene samles uten at vurderingen stopper ved første brudd.
- Rekkefølgen er alfabetisk på navn med norsk rekkefølge, slik at æ, ø og å kommer etter z, og med id som likhetsbryter.
- Konverteringen fra SQLAlchemy til domenetyper skjer i `adaptere/lagring` (AD-5).
- Import-linter håndhever at `domene.regelmotor` og `domene.porter` ikke importerer `adaptere` (AD-1, AD-2), og kontrakten kjøres i `pytest`.
- Svaret er et 200-svar med `status: "ok"` og bare Gyldige kandidater (NFR2). Tilgang og 404 følger samme regler som `GET /api/vakter/{nr}`. Feil har formen `{kode, melding}` (AD-4), og frontend viser bare tekst fra sin egen tekstliste.
- Taggen viser «Nivå N/4» etter mockupen, med tokens fra `tag-bg` (UX-DR11, AV-13).
- Testdatafasiten tilpasses aldri koden (AV-07).

**Beslutninger (Johannes, 2026-11-11):**
- **Datafeil (P-08) bygges nå.** Stoppen sjekker det kompetanseregelen trenger: gyldig vakttype, `start < slutt` med offset, minstenivå 1–4, kompetanseverdier som er heltall 1–4, og at vakten slutter senest ved datagrensen `turnus.periode_slutt` (05.10.2026 kl. 00:00 i seeden). Ved datafeil vurderes ingen Kandidater. 2.3 og 2.4 utvider vinduet til nabovakter og hele uker, og avgjør da hvor historikken starter. #4261–#4265 nås ikke gjennom 1.6, så stoppen testes i domenet og med en endret testdatabase.
- **Datafeil er et 200-svar** med `status: "datafeil"`, `kode: "mangler_turnusgrunnlag"`, `datagrense` (ISO 8601 med offset) og uten kandidatliste. Envelopen i AD-4 er uendret. Frontend viser «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» sammen med datagrensen, og datafeilen ser annerledes ut enn lasting og feil. Valget binder 2.6.
- **Midlertidig merknad:** under overskriften står «Filtrert på kompetanse-minstekrav. Flere regler kommer.». Linjen fjernes i 2.4.

**Never:**
- Regler for kolliderende vakt, 11 t eller 35 t, Ekskludert-boks, tomtilstand, Rangering, kostnad eller KI-kall.
- Endringer i skjema eller testdata, ny tabell eller migrering.
- At regelmotoren importerer testhjelperne i `tester/lagring/test_testdata.py`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Lik minstekrav | nivå 3, minstenivå 3 | gyldig | — |
| Ett under | nivå 2, minstenivå 3 | utelukket, `kompetanse-minstekrav` | — |
| Mangler nivå | ingen nøkkel for `natt` | utelukket, samme årsak | — |
| Mellomvakt | `{"dag": 3}`, `mellom`, minstenivå 3 | gyldig; `{"kveld": 4}` alene gir utelukkelse | — |
| Satt opp | Silje på #4127 | ikke med i grunnlaget | — |
| #4127 | seed | 16 gyldige; ingen av de 8 med kompetansebrudd i fasiten | — |
| #4189 | seed | 21 gyldige; Silje utelukket | — |
| Ukjent/bemannet vakt | `GET /api/vakter/9999/kandidater` | ingen liste | 404 `ikke_funnet` |
| Uten sesjon | ingen cookie | ingen liste | 401 `mangler_sesjon` |
| Etter datagrensen | vakt slutter 05.10 00:01; 00:00 er gyldig | `status: "datafeil"`, `datagrense`, ingen liste | — |
| Ugyldig grunnlag | minstenivå 0/5, `start >= slutt`, kompetanseverdi 0, 5 eller `"3"` | datafeil, ikke utelukkelse | — |

</frozen-after-approval>

## Code Map

- `backend/domene/`, `domene/regelmotor/`, `domene/porter/` — finnes, men med bare tomme `__init__.py`. Nye moduler legges her.
- `backend/adaptere/lagring/modeller.py` — `AnsattRad.kompetanse` (JSON med nøklene dag/kveld/natt), `VaktRad.minstenivå` (med å), `satt_opp_ansatt_id`, `vakttype`, `start`/`slutt` (`OsloTid`). `TurnusRad.periode_slutt`. Ikke endre.
- `backend/adaptere/lagring/vaktdetaljer.py` — `hent_vaktdetaljer` har filteret for turnus, bemanning og periode. Gjenbruk filteret, ikke kopier det.
- `backend/adaptere/api/main.py` — `lag_app`, `Okt`, middleware `krev_sesjon` (l.138), `MELDINGER`/`feil()` (l.29–41), Pydantic-modellene ved `VaktdetaljerUt` (l.105), ruten `vaktdetaljer()` (l.195).
- `backend/tester/api/test_innlogging.py` — fixturene `engine` og `klient`, `logg_inn`, `feilsvar`. `test_vaktdetaljer.py` viser mønsteret.
- `backend/tester/lagring/test_testdata.py` — `bryter_kompetanse` (l.110) er en uavhengig fasithjelper. Ikke importer den fra produksjonskode. `testdata.FASIT[nr]["utfall"]` (l.703) gir navn → regel.
- `backend/requirements-dev.txt`, `pyproject.toml` — versjoner låst med `==`. Pytest bruker `testpaths=["tester"]` og `pythonpath=["."]`.
- `frontend/src/komponenter/Kandidatflate.tsx` — tilstandsmaskin, mønster for `aktiv`/`gjeldendeSesjonsgenerasjon()` (P-09) og `.kandidatplassholder`, som skal byttes ut.
- `frontend/src/api.ts` (`kall`, `hentVaktdetaljer` l.148), `tekster.ts` (`TEKSTER.kandidatflate`, `FEILTEKSTER`), `stil/app.css` (`.tag` l.109), `stil/tokens.css`.
- `frontend/tester/*.test.mjs` — `node --test`. Det finnes ingen komponenttestrigg.

## Tasks & Acceptance

**Execution:**
- [x] `backend/domene/typer.py` — frosne dataklasser for `Vakt` og `Kandidat`, og resultattypene (`Utelukket` med årsaker, `Kandidatvurdering`, ev. `Datafeil`) — domenet skal være uten rammeverk.
- [x] `backend/domene/regelmotor/kompetanse.py`, `vurdering.py` — selve regelen, en regelliste og `vurder_kandidater(...)` som samler alle årsaker, sorterer og gjør datafeilsjekken — grunnmønsteret for 2.2–2.4.
- [x] `backend/adaptere/lagring/kandidatgrunnlag.py` (og en liten refaktor i `vaktdetaljer.py`) — hent vakt, ansatte og datagrense med samme filter og konverter dem til domenetyper.
- [x] `backend/adaptere/api/main.py` — `GET /api/vakter/{vaktnummer}/kandidater` med `KandidaterUt` og datafeilsvaret.
- [x] `backend/requirements-dev.txt`, `pyproject.toml`, `backend/tester/test_arkitektur.py` — lås `import-linter` på siste stabile versjon, legg inn en forbidden-kontrakt og en pytest-test som kjører den.
- [x] `backend/tester/regelmotor/test_kompetanse.py` — matrisen, grensene 1–4, alle årsaker samles, determinisme og datafeilgrensene.
- [x] `backend/tester/api/test_kandidater.py` — fasiten for #4127/#4189 mot `FASIT`, 401, 404, NFR2 og datafeil med endret testdatabase.
- [x] `frontend/src/api.ts`, `tekster.ts`, `komponenter/Kandidatflate.tsx`, `stil/app.css` — hent kandidatene automatisk og vis liste, lasting, feil med «Prøv igjen», datafeil og den midlertidige merknaden, med P-09-vern.
- [x] `frontend/tester/` — test ren formatering eller tilstandslogikk der den finnes.
- [x] `README.md`, `docs/ki-logg/2026-11-11-kompetanse-minstekrav.md`, `docs/emne/vurderingsmatrise.md` — dokumenter endepunkt, KI-arbeid og bevis.

**Acceptance Criteria:**
- Given en valgt vakt, when kandidatflaten lastes, then kandidatlisten hentes uten ekstra handling og vises med navn og «Nivå N/4».
- Given en gammel vakt som svarer etter vaktbytte, when svaret kommer, then det erstatter ikke den aktive visningen (P-09).
- Given en bevisst `import adaptere` i `domene/regelmotor`, when `pytest` kjøres, then arkitekturtesten feiler. Kontrollen gjøres én gang og dokumenteres i KI-loggen.
- Given hele pakken, when `pytest`, `npm.cmd run build` og `npm.cmd test` kjøres, then består alt.

## Implementation Notes

- 2026-11-11: Implementert av en underagent fra spec-en alene. Resultat: 224 backendtester (74 nye), 25 frontendtester (8 nye) og bygg består. Import-linter-kontrakten ble kontrollert med en bevisst direkte og en indirekte import av `adaptere`, og vernet for P-09 med mutasjon. Begge er dokumentert i [KI-loggen](../../docs/ki-logg/2026-11-11-kompetanse-minstekrav.md). Utelukkelsen av den som var satt opp, skjer i domenet. Tider sammenlignes i UTC på grunn av den doble timen når sommertiden slutter.
- 2026-11-11: Nettleserkontrollen i Verification gjenstår. Implementeringsagenten fikk ikke starte utviklingsserverne.
- 2026-11-11: Johannes gjorde nettleserkontrollen i Verification manuelt og godkjente den.

## Spec Change Log

## Review Triage Log

Uavhengig gjennomgang 2026-11-11: blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG), alle med Opus og uten å ha sett implementeringen. Hvert funn er vurdert mot koden.

| Lag | Funn | Dom og bevis | Rute |
|---|---|---|---|
| VG | Kandidatruten er ikke testet for annen turnus og periodegrensene | medium: `test_kandidater.py` tester bare seednumre. Et eget oppslag uten `BrukerRad`-join i 2.2–2.4 ville gitt navn til en annen turnus uten at noen test ble rød. | patch |
| VG | Gjengivelse og «Prøv igjen» i `Kandidatliste` er ikke automatisk testet | medium: Det finnes ingen komponenttestrigg (gjelder fra før). Logikken i `kandidater.ts` er testet. Komponenten dekkes av nettleserkontrollen, som gjenstår. | defer |
| BH | Spec-en mangler i diffen | false: Den var tatt ut med vilje, fordi spec-en går bare til edge-case-laget. Den er med i commiten. | avvist |
| BH | AD-4 nevner ikke statusen `datafeil` | medium: AD-4 har bare `ok`, `ingen_gyldige_kandidater` og `avveining_feilet`, og P-08-presiseringen sier at kodene fastsettes i berørte stories. 2.6 må ellers finne formen i en story-fil. | patch |
| BH | README sier «fram til 2.4 bare kompetanse» | low: Teksten er feil allerede etter 2.2. Rettes direkte i teksten. | patch |
| BH | AGENTS.md sier «ingen domenelogikk ennå» | low: Stemmer ikke lenger. Rettingen gjelder en agentkontekstfil. | defer |
| BH | Import-linter dekker ikke hele `domene` | low: En ny modul i `domene/` som regelmotoren ikke importerer, kunne importert `adaptere`. Rettes ved å bruke `source_modules = ["domene"]`. | patch |
| BH | Én datafeilkode skjuler ulike årsaker | low: Det er sant, men koden og teksten er Johannes' beslutning i Intent. | avvist |
| BH | `Datafeil.grunner` logges ikke på serveren | low: Uten logg kan ingen se hvilken Ansatt eller hvilket felt som feilet. Rettes med én loggelinje. | patch |
| BH | Datafeil kan ikke nås i UI med seeden, og det er udokumentert | low: #4261–#4265 gir 404. KI-loggen sier ikke hvordan tilstanden vises manuelt. | patch |
| BH | `ok` med tom liste gir en tom `<ul>` | low: Tomtilstanden er utenfor omfanget (Never), og seeden gir 16 og 21. | avvist |
| BH | Byttet sesjonsgenerasjon i P-09 er ikke testet | low: Bare oppryddingen er testet. `nySesjonsgenerasjon()` er eksportert, så testen er enkel. | patch |
| BH | Frontendtestene gjenoppretter ikke `fetch` | low: En feilende test etterlater en `fetch` som aldri svarer, og `delete` fjerner Nodes egen. Rettes direkte. | patch |
| BH | Determinismetesten ser ikke `kompetanse` (`compare=False`) | low: `kompetanse` er en kopi av input og beregnes ikke. `compare=False` holder dataklassen hashbar. Rettingen gir liten nytte. | avvist |
| BH | API-et regner nivået på nytt, og None gir 500 | false: `bryter_kompetanse` utelukker når nivået er None, så Gyldige kandidater har alltid et heltall. API-et kaller domenefunksjonen og kjenner ikke mellom-regelen. | avvist |
| BH | Kandidatgrunnlaget er ikke avgrenset per turnus | low: `ansatt` har ingen `turnus_id`, og Intent bestemmer at alle rader brukes (AV-06). | avvist |
| BH | «aa» sorteres som a, og valget er ikke dokumentert | low: Ingen seednavn er berørt, men tolkningen binder rekkefølgen til Epic 4. Dokumenteres i docstringen. | patch |
| BH | KI-loggen sier at ukjente nøkler ikke gir datafeil | low: `{"helg": 0}` gir datafeil. Det er teksten som er upresis. | patch |
| BH | KI-loggen sier ikke hvilken port og kommando som ble brukt | low: Kontrollen kan da ikke gjentas. Rettes i teksten. | patch |
| ECH | Navn som ikke er tekst, gir 500 | false: `ansatt.navn` er `Mapped[str]` og NOT NULL, og ingen kodevei skriver noe annet. | avvist |
| ECH | Navn i NFD sorteres feil | low: Seeden er i NFC, men rettingen er én `normalize("NFC", …)`. | patch |
| ECH | ð, þ, ł sorteres før a | low: Lite sannsynlig, og rettingen legger til en gren. | avvist |
| ECH | Tom liste uten tekst | low: Samme funn som BH og utenfor omfanget. | avvist |
| ECH | `ok` uten liste krasjer flaten | false: Backend sender alltid `kandidater` når status er `ok` (`KandidaterUt`). | avvist |
| ECH | Vaktnummer over 2⁶³−1 gir 500 | low: Samme funn som i 1.6, som Johannes lukket 2026-11-10 som ikke reelt. | avvist |

## Verification

**Commands:**
- Fra `backend/`: `.venv\Scripts\python -m pytest` — alle tester består, også import-linter.
- Fra `frontend/`: `npm.cmd run build` og `npm.cmd test` — alt består.

**Manual checks:**
- Logg inn, velg #4127 og #4189 og kontroller at listene stemmer med matrisen, uten Silje eller Eirik.
