---
title: 'Retro 5, T2 og T3: forventede svar fra «Prøv igjen», feilvern i avveiningsruten og testhull'
type: 'bugfix'
created: '2026-11-28'
status: 'in-progress'
baseline_commit: '5b546e026129382570004f541ace8759fa359985'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-retro-2026-11-28.md'
  - '{project-root}/docs/testing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når «Prøv igjen» får et forventet svar (409 `tolkning_paagar`, 409 `ikke_feilet` eller 503 `ki_utilgjengelig`), erstattes hele rangeringen med et feilpanel (R2 i retroen). Avveiningsruten gir 500 ved uventede unntak og logger ingenting når `forklar` gir `None` (R5). Tre grenser mellom storiene er ikke testet (R6).

**Approach:** Rangeringen blir stående. Svaret vises som melding i statuslinjen og ved raden, og listen hentes på nytt. Avveiningsruten fanger uventede unntak, logger dem og svarer `avveining_feilet`. `forklar` logger feiltypen uten innhold. Testhullene tettes. Hver ny test vises å kunne feile med en mutasjon (T7).

## Boundaries & Constraints

**Always:**
- Sent svar etter vaktbytte eller ny sesjon vises ikke. Bruk samme `gyldig()`-mønster som i dag.
- Nettverksfeil og andre koder enn de i matrisen gir feilpanelet som før. Testen «nettverksfeil etter forsøk krever oppdatert rangering før valg» skal bestå uendret.
- 401 går fortsatt til sesjonsvarsleren («Sesjonen er utløpt»).
- Logglinjer har bare ID-er og feiltype. Ingen preferansetekst, påstand, prompt eller KI-svar (AD-4, AV-19).
- Tekster ligger i `src/tekster.ts`, og testene finner dem derfra.
- Ingen betalte kall. KI-testene bruker falsk transport.

**Never:**
- Ingen endring av kontrakten (statuskoder, felt) for POST, PUT eller avveining. Ingen ny pakke.
- Ikke T4 (egen tilstand for endret grunnlag) og ikke T5 (refaktorering av tolkningsflyten).
- `ki_kilde: "mal"` skal ikke kreve modell.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tolkes allerede | POST gir 409 `tolkning_paagar` | Tabellen blir stående. Listen hentes på nytt. Statuslinje og rad viser at preferansen tolkes allerede. | Feiler GET-en, vises feilpanelet som i dag |
| Ikke lenger feilet | POST gir 409 `ikke_feilet` | Som over, med en melding om at preferansen er endret og rangeringen oppdatert | Som over |
| KI utilgjengelig | POST gir 503 `ki_utilgjengelig` | Som over, med en melding om at tolkning ikke er tilgjengelig nå | Som over |
| Ikke lenger gyldig | POST gir 404 `ikke_funnet` | Som PUT i 5.9: listen hentes på nytt, og statuslinjen viser `rp.ikkeGyldig`. Ingen radmelding, fordi kandidaten ikke lenger står i tabellen. | Som over |
| Uventet unntak | `forklar`, `forklar_med_oppslag` eller `forklaringsnøkkel` kaster | 200 `avveining_feilet` med identitet, og én `logger.exception`-linje med vakt og kandidat | — |
| `forklar` gir `None` | Tolkefeil, ubrukelig JSON, avvist av faktakontrollen, ingen myk faktor | Én logglinje med kandidat-ID og feiltype (`4xx`, `ubrukelig`, `faktakontroll` …). Ingen myk faktor logges på INFO, resten på WARNING. | — |

**Decisions (Johan, 2026-11-28):**
- Spesifikasjonen holdes samlet, med én PR for T2 og T3, selv om den er på omtrent 2400 tokens.
- 404 tas med (raden «Ikke lenger gyldig»).
- Tekstene. Statuslinjen bruker `feiltekst("tolkning_paagar")` og `feiltekst("ki_utilgjengelig")`. For `ikke_feilet` brukes `t.tolkEndret`, fordi listen nå lastes automatisk. Raden viser «Tolkes allerede.», «Endret nå.» og «Tolkning er ikke tilgjengelig nå.»

</frozen-after-approval>

## Code Map

- `frontend/src/komponenter/Kandidatflate.tsx:153-177` -- `provPreferanseHandling`. `catch` sender i dag alt til `tilstandFraFeil`. Gjenbruk `setRadmelding({id, tekst})` og `hentKandidater` → `tilstandFraSvar`, som `lagrePreferanseHandling` (:188-232) gjør ved 404.
- `frontend/src/komponenter/Kandidatflate.tsx:436-439` -- radmeldingen vises når `redigering.melding.id === r.id` og raden ikke redigeres. Den passer også for «Prøv igjen».
- `frontend/src/tekster.ts:13-15, 173-202` -- `feiltekst`-kodene og `kandidatflate`-tekstene (`tolker`, `tolkEndret`, `redigerPreferanse.rad`).
- `frontend/src/kandidater.ts:34-45` -- `gyldigAvveining`. `mal` godtas uten modell (:42).
- `frontend/tester/komponenter/kandidatflate.test.tsx:62-113` -- mønster for «Prøv igjen» med `falskFetch`, `feil(status, kode)` og `kallTil`.
- `frontend/tester/komponenter/avveining.test.tsx:313-334` -- `test.each` over `forhandsgenerert`/`mal` i begge flater. `live()` setter `modell: "test/modell"`.
- `frontend/tester/komponenter/app.test.tsx:16-29` -- mønster for 401 → innlogging med `TEKSTER.sesjonUtlopt`.
- `frontend/src/api.ts:241-252` -- `provPreferanse` og `lagrePreferanse`, begge `beskyttet` (deferred-work 2026-11-28).
- `backend/adaptere/api/main.py:627-654` -- avveiningsruten. KI-delen etter lesetransaksjonen skal få feilvern. `logger` finnes i modulen.
- `backend/adaptere/ki/openrouter.py:255-268` -- `forklar`. De tre `None`-veiene: ingen myk faktor (:257), `Tolkefeil` (:267, `svar.feiltype`), og `les_jsoninnhold`/`avveining.valider` (:268). Skill «ubrukelig» (JSON) fra «faktakontroll» (`valider` avviser).
- `backend/adaptere/ki/demo.py:100-101` -- datafil som mangler, gir `modell = ""`.
- `backend/tester/api/test_avveining.py` -- mønster med `lag_app(engine=engine, ki=...)`, `logg_inn` og `caplog`. `TestClient` uten `with` starter ikke tolketråden.
- `backend/tester/ki/test_openrouter.py` -- `FalskTransport`, `FalskKlokke`, `adapter`, `innhold`, `status`.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/tekster.ts` -- de tre radtekstene fra Decisions -- i `kandidatflate`, nær `provPreferanse`.
- [x] `frontend/src/komponenter/Kandidatflate.tsx` -- i `provPreferanseHandling`: `ApiFeil` med de fire kodene i matrisen gir statusmelding, radmelding og ny GET. Alt annet gir `tilstandFraFeil` som før.
- [x] `frontend/tester/komponenter/kandidatflate.test.tsx` -- `test.each` over de fire kodene: tabellen står, meldingene vises, og `kallTil(GET) === 2`. For 409/503 er raden valgbar. Ved 404 er kandidaten borte fra den nye listen.
- [x] `frontend/tester/komponenter/avveining.test.tsx` -- en rad for `mal` med `modell: ""` i `test.each`.
- [x] `frontend/tester/komponenter/app.test.tsx` -- 401 på POST og på PUT `…/preferanse` gir innloggingen med `sesjonUtlopt` (`test.each`).
- [x] `backend/adaptere/api/main.py` -- `try/except Exception` rundt KI-delen av `avveining`. `logger.exception` med vakt og kandidat, og svaret er `AvveiningFeiletUt(**identitet)`.
- [x] `backend/adaptere/ki/openrouter.py` -- én logglinje per `None`-vei i `forklar`, med kandidat-ID og feiltype.
- [x] `backend/tester/api/test_avveining.py` -- `ki=None` og en ren `Tolker` gir `avveining_feilet`. En `Forklarer` som kaster, og en `forklaringsnøkkel` som kaster (monkeypatch), gir 200 `avveining_feilet` og en ERROR-post. Demo uten datafil gir `mal` med `modell == ""`.
- [x] `backend/tester/ki/test_openrouter.py` -- `caplog` per `None`-vei: riktig nivå og feiltype, og ingen påstandstekst eller modellsvar i meldingen.
- [x] `docs/testing.md`, `deferred-work.md`, `docs/ki-logg/2026-11-28-retro-5-t2-t3.md` -- testtabellen, punktet om 401 er løst, og KI-loggen med mutasjonene (T7).

**Acceptance Criteria:**
- Gitt «Prøv igjen» med en av kodene i matrisen, når svaret kommer, så står rangeringen, statuslinjen har fokus og meldingen, og knappene er aktive igjen.
- Gitt en hvilken som helst ny test, når koden den vokter tilbakestilles, så blir testen rød. Mutasjonen og den røde meldingen står i KI-loggen.

## Implementation Notes

- `PROV_AVVIST` i `Kandidatflate.tsx` krever både status og kode. En annen status med samme kode gir feilpanelet.
- `forklar` logger `ubrukelig` når `les_jsoninnhold` gir `None`, og `faktakontroll` for alt `valider` avviser.
- Eksisterende test endret: `test_direkte_sertifikatfeil_logger_årsaken_uten_feiltekst` forventer nå også oppsummeringslinjen fra `forklar` (`… ga reservetekst (nettverk).`). Endringen er tilsiktet.
- Testen uten forklaringsport krever ingen ERROR-linje. Ellers ville feilvernet skjult at `isinstance(ki, Forklarer)` var fjernet (mutasjon B3).
- Mutasjonene (M1–M6, B1–B9) og de røde meldingene står i `docs/ki-logg/2026-11-28-retro-5-t2-t3.md`.
- Manuell kontroll i demo-modus er ikke kjørt. Se «Ikke gjort» i KI-loggen.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `.venv\Scripts\python -m pytest` (fra `backend/`) -- forventet: alle grønne, også arkitektur og ruff.
- `npm.cmd run build` og `npm.cmd run test` (fra `frontend/`, én kjøring om gangen) -- forventet: grønt.

**Manual checks (if no CLI):**
- Ekte backend i demo-modus: «Prøv igjen» mens oppstartstolkningen pågår, skal gi «tolkes allerede» uten at tabellen forsvinner. Hvis det ikke lar seg gjenskape, føres det som åpent punkt.
