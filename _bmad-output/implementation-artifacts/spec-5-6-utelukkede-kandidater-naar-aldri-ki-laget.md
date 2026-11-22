---
title: 'Story 5.6: Utelukkede kandidater når aldri KI-laget'
type: 'feature'
created: '2026-11-21'
status: 'done'
baseline_commit: 'd7bf9f7f2e3994847bed797f4e211b1227bd44f0'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 5.3 avviser utelukkede kandidater ved forklaringsruten. Det finnes ennå ingen samlet kjøretidstest som beviser lekkasjeinvarianten (NFR2, SM-2) gjennom hele API-flyten for alle fire harde regler, og som viser at testen faktisk blir rød når grensen brytes.

**Approach:** Lag en kjøretidstest gjennom `adaptere/api` mot testdataene for vakt #4127, som har utelukkelser etter alle fire regler. Testen bruker ekte `OpenRouterKiAdapter` med en falsk transport som registrerer hver forespørsel. Den skiller forklaringsporten fra tolkingsporten, og en negativ kontroll viser at den feiler hvis en utelukket kandidat slipper gjennom. Testen og hva den beviser, dokumenteres i KI-loggen.

## Boundaries & Constraints

**Always:**
- Bare testkode og dokumentasjon. Ingen endring i produksjonskoden, med mindre testen avdekker en faktisk lekkasje. Da stopper arbeidet, og funnet legges fram før det rettes.
- Ingen nettverk og ingen nøkkel. `tester/conftest.py` fjerner allerede KI-variablene.
- Testen er laget slik at story 5.7 kan legge `DemoKiAdapter` til som ny parameter uten å skrive testen om (AD-6).
- Ekskludert-boksen (`utelukkelser` i listesvaret) skal vise utelukkede navn (story 2.5). Kravet om «ikke i API-svaret» gjelder kandidatradene, godkjenningsgrunnlaget og avveiningssvarene.

**Never:**
- `DemoKiAdapter`. Den delen av AC3 venter på story 5.7 (brukerens valg 2026-11-21) og føres i `deferred-work.md`.
- Betalte kall og nye avhengigheter.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Hele flyten | #4127: 4 gyldige, 20 utelukkede (8/7/4/1). Liste, alle godkjenningsgrunnlag og avveining for hver gyldig | Ingen forklaringsforespørsel inneholder utelukket ID eller navn. Kandidatrader og avveininger har bare gyldige ID-er og navn | N/A |
| Direkte oppslag på utelukket | GET avveining og godkjenningsgrunnlag for hver av de 20 | 404 `ikke_funnet`, likt svaret for ukjent ID. Null forklaringskall | N/A |
| Modellen peker på utelukket | Svaret bruker en utelukket ID som `kandidat_id` eller `referanse_id` | `avveining_feilet`. Ingen utelukket navn i svaret | Hele svaret forkastes (P-06) |
| Tolkingsporten | Bakgrunnstolkningen ved oppstart sender ventende tekster, også fra senere utelukkede | Tillatt. Tolkeforespørselen har bare `tekst`, ingen kandidat-ID eller vaktstatus | N/A |
| Negativ kontroll | Testen lar en utelukket kandidat bli regnet som gyldig | Invariantkontrollen feiler | `pytest.raises(AssertionError)` |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py` -- `avveining` (linje 557–575) slår opp i `grunnlag.rangert` og gir 404 før `ki.forklar`. `les_rangering` kaller `vurder_kandidater` og `ranger` på modulnivå. Den negative kontrollen kan monkeypatche `main.vurder_kandidater` og flytte én `Utelukket` inn i `gyldige` (husk `ulempe_per_kandidat`). Ikke endre filen.
- `backend/adaptere/ki/openrouter.py` -- `forklar` sender `{"kandidat": {kandidat_id, plass, poeng}, "referanse": …, "tillatte": [...]}` i `messages[1].content`. `response_format.json_schema.name` er `"avveining"` eller `"preferanse"` og skiller portene. Tolkingen sender `{"tekst": ...}`.
- `backend/adaptere/ki/avveining.py` -- `valider` godtar bare påstander som er identiske med `tillatte_påstander`. Navn settes inn fra `kandidat`/`referanse`.
- `backend/tester/api/test_avveining.py` -- mønster for `TestClient`, `lag_app(engine=..., ki=OpenRouterKiAdapter("test", transport=...))`, `logg_inn` og `innhold(...)` fra `tester/ki/test_openrouter.py`. Gjenbruk dem.
- `backend/tester/api/test_innlogging.py` -- fixturen `engine` fyller testdata. `adaptere/lagring/testdata.py` har `FASIT[4127]["utfall"]` og `ANSATTE` (id, navn).
- `backend/tester/test_arkitektur.py` -- den statiske kontrakten. Den beholdes uendret og kjøres i samme `pytest`.
- `docs/ki-logg/`, `docs/emne/vurderingsmatrise.md`, `docs/testing.md` -- dokumentasjon.

## Tasks & Acceptance

**Execution:**
- [x] `backend/tester/api/test_lekkasjeinvariant.py` -- Ny testmodul. Den registrerende transporten lagrer hver forespørsel og svarer gyldig på begge porter. En hjelpefunksjon henter alle `kandidat_id` og `referanse_id` rekursivt fra forklaringsforespørslene og kontrollerer dem mot utelukkede ID-er, navn i hele kroppen og ID-er og navn i rader og avveiningssvar. Testene dekker hver rad i matrisen. AppTesten parametriseres over en adapterfabrikk med `OpenRouterKiAdapter` i dag. Kontroller at fasiten for #4127 har minst én utelukkelse per regel, så testdataene ikke kan miste en regel uten at testen blir rød. -- AC1–AC3
- [x] `_bmad-output/implementation-artifacts/deferred-work.md` -- Legg til punktet om `DemoKiAdapter` i lekkasjetesten under story 5.7. -- AC3
- [x] `docs/ki-logg/2026-11-21-lekkasjeinvariant.md` -- Oppgave, prompt, leveranse, rettinger, hva testen beviser og ikke beviser, og den negative kontrollen. -- AC4
- [x] `docs/emne/vurderingsmatrise.md`, `docs/testing.md` -- Ny milepæl for 5.6 med lenker, og testen nevnt der backendtestene er beskrevet. -- Sensorveiledning

**Acceptance Criteria:**
- Gitt `pytest` i `backend/`, når hele samlingen kjøres, så kjører både import-linter-kontrakten og den nye kjøretidstesten. Den negative kontrollen viser at kjøretidstesten feiler når grensen brytes (AD-1, AD-2).
- Gitt forklaringsporten, når API-et beregner listen eller godkjenningsgrunnlaget, så er det null forklaringskall.
- Gitt at storyen er ferdig, når KI-loggen leses, så beskriver den hva testen beviser og at demodelen venter på 5.7.

## Verification

**Commands:**
- `cd backend && .venv/bin/python -m pytest tester/api/test_lekkasjeinvariant.py -v` -- expected: alle bestått
- `cd backend && .venv/bin/python -m pytest` -- expected: alle bestått, også `test_arkitektur.py`

**Manual checks (if no CLI):**
- Ingen. Storyen endrer ikke UI eller produksjonskode, så OP-16-sjekklisten gjelder ikke.

## Implementation Notes

- 21 tester i `backend/tester/api/test_lekkasjeinvariant.py`. Kontrollene er fire separate funksjoner (`INVARIANTKONTROLLER`): kall på `forklar`, HTTP-forespørslene til modellen, API-svarene og direkte oppslag. Den negative kontrollen kjører hver av dem for én utelukket per regel (16 kjøringer) og krever `AssertionError` etter å ha bekreftet at lekkasjen faktisk når rad og `forklar`.
- I tillegg til den registrerende transporten pakkes adapteren i `RegistrerendePort`, slik at kontrollene på porten også gjelder for `DemoKiAdapter` i 5.7, som ikke bruker HTTP.
- Den falske klokken (`FalskKlokke`) brukes for begrenseren, ellers ville den 19. tolkningen ventet 60 s ekte tid.
- Funn: en utelukket uten nivå for vakttypen (Eirik Moen) som lekkes inn i `gyldige`, stoppes av `ranger` med `ValueError` før KI. Den negative kontrollen velger derfor en utelukket med nivå for dag per regel. Ingen lekkasje i produksjonskoden.

## Spec Change Log

## Review Triage Log

Tre underagenter på Opus gjennomgikk diffen uavhengig: Blind Hunter (12 funn), Edge Case Hunter (5 funn) og Verification Gap (ingen hull). Tabellen viser vurderingen av hvert funn og hva som ble gjort.

| Gjennomgang | Vurdering | Funn og oppfølging |
|---|---|---|
| Blind 1 | low, patch | Navnesjekken i HTTP-forespørselen kan ikke feile, fordi `forklar` bare sender ID-er. KI-loggen sier nå at navnedelen holder fordi forespørselen ikke har navn, og at den negative kontrollen beviser ID-delen. |
| Blind 2 | low, patch | Feilmeldingen viste alle ID-er (`{11, 6}`, der 6 er gyldig). Den viser nå bare de utelukkede, og eksempelet i loggen er rettet. |
| Blind 3 + Grensetilfeller 1 | medium, patch | Ingenting viste at den reduserte svarformen besto med gyldig ID, så avvisningen kunne hatt en annen årsak. Det første svaret i testen er nå en positiv kontroll med `status: ok`. Loggen sier at avvisningen kommer fra den generelle regelen i `avveining.valider`. |
| Blind 4 + Grensetilfeller 3 | low, avvist | `ÉN_PER_REGEL` med hardkodet `dag` feiler ved innsamling hvis testdataene endres. Det er en høylytt feil, ikke en stille feil. Vakt #4127 er en dagvakt i testdataene. |
| Blind 5 | low, patch | Bare `kandidater` i listesvaret ble sjekket. Hele listesvaret unntatt `utelukkelser` sjekkes nå for utelukkede ID-er og navn. |
| Blind 6 | false | Testen sjekker at `ki.tolkninger` inneholder tekstene til de utelukkede. For OpenRouter gir hvert `tolk`-kall en forespørsel, så listen kan ikke være tom mens testen er grønn. |
| Blind 7 | low, patch | Søket etter forbudte ord dekket også systemprompten. Det dekker nå bare brukermeldingen, og systemprompten kontrolleres med likhet. Variabler som skygget innebygde navn, er omdøpt. |
| Blind 8 | low, patch | Den negative kontrollen er ikke parametrisert over adapterne. `deferred-work.md` sier nå at 5.7 må gjøre det og hoppe over HTTP-kontrollen for demo. |
| Blind 9 | low, patch | `epic-5-context.md` ble endret av steg 1 i `bmad-build`, fordi planleggingsfilene var nyere. Begrunnelsen står i commit-meldingen. |
| Blind 10 + Grensetilfeller 4 | false | `TestClient` uten `with` starter ingen lifespan og ingen tolketråd. Databasen er per test i `tmp_path`, så ingen tilstand lekker. Nr. 1 har alltid en referanse når det finnes 4 gyldige. |
| Blind 11 | avvist | Retting ville endret denne spesifikasjonen (linjenumre i Code Map). |
| Blind 12 | low, avvist | Import av fixture og konstanter fra andre testmoduler følger mønsteret i `tester/api/test_avveining.py`. |
| Grensetilfeller 2 | false | Når lekkasjen ikke når HTTP, kaster ikke HTTP-kontrollen `AssertionError`, og testen med `pytest.raises` blir rød. Alle 16 kjøringer er grønne, så lekkasjen nådde HTTP. |
| Grensetilfeller 5 | false | Ingen ansatt i testdataene har et navn som inneholder navnet til en utelukket (kontrollert med skript). |

Etter rettingene bestod `test_lekkasjeinvariant.py` 21 av 21, og hele backendsamlingen 738 av 738.

### Oppfølging av PR #36, 22. november 2026

Gjennomgangen av `e59adf4` viste at en ekstra modellmelding, et tillegg i den sendte preferanseteksten og en nestet referanse-ID i detaljsvarene kunne passere kontrollene. Alle tre funn ble rettet i testmodulen. Den utvidede kontrollen kjøres også med endret svarskjema, tekstkodet ID og en ID føyd til en avveiningssetning. [Forsøk før og etter retting](../../docs/ki-logg/2026-11-22-oppfolging-pr-36.md).
