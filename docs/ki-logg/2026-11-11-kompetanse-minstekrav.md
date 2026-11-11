# KI-logg: Story 2.1 – gyldige kandidater filtrert på kompetanse-minstekrav

Dato: 2026-11-11. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (AV-02, AV-06, AV-07, AV-13, P-08, P-09). Arbeidet ble gjort av Claude Code (Opus 5.5) som implementeringsagent i `bmad-build`, på branchen `story-2.1-kompetanse`.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read …/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.» Specen inneholder Johannes' beslutninger 2026-11-11 om datafeil (P-08 bygges nå, 200-svar med `status: "datafeil"`) og den midlertidige merknaden.

## Leveranse

- **Domenekjernen** (`backend/domene/`), ren Python uten rammeverk, klokke, database eller KI:
  - `typer.py`: frosne dataklasser `Vakt`, `Kandidat`, `Utelukket`, `Kandidatvurdering` og `Datafeil`. Gyldige og utelukkede er adskilte typer, så en utelukket Kandidat ikke kan sendes videre til rangering ved en feil. Kompetansen kopieres til en skrivebeskyttet tabell.
  - `regelmotor/kompetanse.py`: regelen (`nivå >= minstenivå`, `mellom` bruker `dag`, manglende nøkkel utelukker), `kompetansenivå` for taggen og datakravet (nivåer er heltall 1–4, ikke `True` eller `"3"`).
  - `regelmotor/vurdering.py`: regellisten `REGLER`, datafeilsjekken og `vurder_kandidater`. Den som var satt opp, tas bort (AV-06). Datafeil stopper før noen Kandidat vurderes: ukjent vakttype, tid uten tidssone, `start >= slutt`, minstenivå utenfor 1–4, ugyldig kompetanseverdi, eller vakt som slutter etter datagrensen. Tidene sammenlignes i UTC, fordi Python sammenligner veggklokka når to tidspunkt har samme `tzinfo`, og det blir feil i timen som går to ganger når sommertiden slutter. Hver Kandidat vurderes mot alle reglene, og alle årsakene samles. Rekkefølgen er norsk alfabetisk uten locale (æ, ø, å etter z; é som e), med navn og id som likhetsbrytere.
- **Lagring** (`adaptere/lagring/`): `finn_ubemannet_vakt` er skilt ut av `vaktdetaljer.py`, slik at vaktdetaljene og kandidatgrunnlaget bruker samme filter og gir 404 for de samme vaktene. `kandidatgrunnlag.py` konverterer vakt, alle Ansatte og `turnus.periode_slutt` til domenetyper (AD-5).
- **API**: `GET /api/vakter/{vaktnummer}/kandidater` med `KandidaterUt` (`status: "ok"` og bare gyldige, med `id`, `navn` og `kompetansenivå`) og `DatafeilUt` (`status`, `kode: "mangler_turnusgrunnlag"`, `datagrense`). Feilformen i AD-4 er uendret.
- **Import-linter 2.16** (siste stabile versjon 2026-11-11), låst i `requirements-dev.txt`. Kontrakten i `pyproject.toml` forbyr `domene.regelmotor` og `domene.porter` å importere `adaptere`, også indirekte. `tester/test_arkitektur.py` kjører den i `pytest`.
- **Frontend**: `src/kandidater.ts` har tilstandene (laster, feil, datafeil, klar, avvist) og `lastKandidater`, som ikke melder et svar etter at komponenten er ryddet opp eller sesjonen byttet (P-09). `Kandidatflate.tsx` bytter plassholderen mot en liste med navn og «Nivå N/4»-tag (`tag-bg`), lasting, feil med «Prøv igjen», datafeil med datagrensen og merknaden «Filtrert på kompetanse-minstekrav. Flere regler kommer.». Datafeilen har nøytral kant til venstre, verken `danger` eller `warn`.
- **Tester**: `tester/regelmotor/test_kompetanse.py` (53), `tester/api/test_kandidater.py` (20), `tester/test_arkitektur.py` (1) og `frontend/tester/kandidater.test.mjs` (8).

## Valg agenten tok innenfor specen

- Utelukkelsen av den som var satt opp, skjer i domenet (`Vakt.satt_opp_ansatt_id`), ikke i spørringen, slik Approach beskriver. Lagringen henter alle rader i `ansatt`.
- Datakravene ligger i hver `Regel` (`vaktkrav`, `kandidatkrav`), og felles krav til Vakten i `vaktdatafeil`. 2.2–2.4 legger til regler og krav i samme liste. Datakrav sjekkes bare for kandidatgrunnlaget, så ugyldige data hos den som var satt opp, gir ikke datafeil.
- Alle kompetanseverdier sjekkes, også for andre vakttyper enn Vaktens, slik matrisen sier «kompetanseverdi 0, 5 eller `"3"`». En ukjent nøkkel med gyldig nivå 1–4 gir ikke datafeil, men en ugyldig verdi under hvilken som helst nøkkel gjør det.
- `Datafeil.grunner` sier hva som feilet, for tester og feilsøking. Grunnene sendes ikke til frontend.
- Datafeiltilstanden kan ikke nås i grensesnittet med seeddataene. #4261–#4265 slutter etter datagrensen, men er bemannet og gir 404, som i story 1.6. Tilstanden er dekket av domenetestene, API-testene med endret testdatabase og frontendtestene. For å vise den manuelt: kopier `backend/turnushjelperen.db`, start backend med `TURNUSHJELPEREN_DB` satt til kopien, og flytt #4127 over datagrensen med samme endring som `endre_vakt` i testene:

  ```sql
  UPDATE vakt SET vakttype = 'kveld',
    start = '2026-10-04T14:01:00+00:00', slutt = '2026-10-04T22:01:00+00:00'
  WHERE vaktnummer = 4127;
  ```

  Tidene lagres i UTC (`OsloTid`), så dette er 04.10 16:01–05.10 00:01 i Oslo. Kandidatflaten for #4127 viser da datafeilen med datagrensen 05.10.2026 00:00.
- Svaret med status `ok` og null gyldige gir en tom liste uten egen tekst. Tomtilstanden hører til story 2.6 (Never i specen).

## Korrigering og kvalitetssikring

Rettet underveis, før noe ble levert:

1. Første versjon av datakravet for kompetanse hadde en meningsløs typesjekk (`isinstance(…, dict | type(…))`). Den ble erstattet med `isinstance(…, Mapping)` før første testkjøring.
2. Frontendtesten for feiltilstandene laget `ApiFeil` fra en egen bunt av `api.ts`. `instanceof` feilet, fordi `kandidater.ts` er buntet med sin egen kopi av klassen. Testen går nå gjennom en falsk `fetch`, slik at feilen lages av samme kode som i appen.
3. Testen «laster, feil og datafeil har ulik tekst» antok at alle feiltekstene er ulike. To feilkoder deler tekst med vilje, så testen sjekker nå at laste- og datafeilteksten ikke finnes blant feiltekstene.

Kontroller:

- **Import-linter (akseptansekrav 3), kjørt én gang 2026-11-11:** `import adaptere` lagt til nederst i `domene/regelmotor/kompetanse.py` ga rød test med «domene.regelmotor is not allowed to import adaptere: domene.regelmotor.kompetanse -> adaptere». `import adaptere.ki` i `domene/typer.py` ga også rød test, fordi regelmotoren importerer `typer` (indirekte import). Begge endringene ble fjernet, og testen ble grønn igjen.
- **P-09 (akseptansekrav 2):** med vernet i `lastKandidater` byttet ut med `() => true` feilet de to testene for forsinket svar og forsinket feil. Vernet ble satt tilbake.
- **Fasiten:** API-testene leser `testdata.FASIT` og tilpasser den ikke (AV-07). #4127 gir 16 gyldige, ingen av de 8 med kompetansebrudd og ikke Silje. #4189 gir 21 gyldige, Silje og Eirik er ikke med.
- **Mot kjørende backend:** testdatakommandoen og `.venv\Scripts\python -m uvicorn adaptere.api.main:app --port 8765` mot en midlertidig database i agentens kladdemappe (`TURNUSHJELPEREN_DB`), utenfor repoet. Utviklingsserverne på 8000 og 5173 ble ikke startet. Innlogging som `kari.vestby` og `curl` mot endepunktet ga 16 kandidater for #4127 og 21 for #4189 i alfabetisk rekkefølge med riktig nivå, 404 `ikke_funnet` for #9999 og 401 `mangler_sesjon` uten cookie.
- **Testresultater før gjennomgangen:** full `pytest` i `backend/` ga **224 bestått** (150 før storyen, pluss 74 nye). `npm.cmd test` ga **25 bestått**, og `npm.cmd run build` bestod.

Rettet etter den uavhengige gjennomgangen:

- API-testene dekker nå også annen turnus og de halvåpne periodegrensene for kandidatruten, med 404 uten ansattnavn i svaret.
- Import-linter-kontrakten gjelder hele `domene`, ikke bare `domene.regelmotor` og `domene.porter`, så en ny modul direkte under `domene/` er også dekket.
- `Datafeil.grunner` logges som advarsel i API-et med vaktnummeret, så det går an å se hva som feilet. Svaret er uendret.
- Sorteringen normaliserer navnet til NFC først. Før det havnet «Å» skrevet som A + kombinerende ring blant a-navnene. At «aa» sorteres som to a-er og ikke som å, står nå i docstringen.
- Frontendtestene setter Node sin egen `fetch` tilbake etter hver test i stedet for å slette den, og en ny test viser at et svar fra en sesjon som er byttet ut, ikke meldes. Med sesjonsvernet fjernet feilet den testen.
- Datafeilformen er ført inn i AD-4 i arkitekturen, og README sier at listen i story 2.1 bare er filtrert på kompetansekravet.

Ikke gjort av implementeringsagenten:

- Nettleserkontrollen i specen (logg inn, velg #4127 og #4189 og se listene) er ikke gjort. Agenten fikk ikke lov til å starte utviklingsserverne på standardportene.
- Uavhengig kodegjennomgang med egne agenter (`bmad-build`, OP-04) og menneskelig PR-gjennomgang gjenstår. Funnene føres i spesifikasjonens Review Triage Log.
