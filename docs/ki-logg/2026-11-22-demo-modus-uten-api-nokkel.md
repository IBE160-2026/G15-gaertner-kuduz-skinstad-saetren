# KI-logg: Story 5.7 – demo-modus uten API-nøkkel

Dato: 2026-11-22. Koden er skrevet av Claude (Sonnet 5) som implementeringsagent i en
Claude Code-sesjon, på branchen `story/5-7-demo-modus-uten-api-nokkel`.

## Oppgave og prompt

Oppgaven ble gitt ordrett:

> Read `_bmad-output/implementation-artifacts/spec-5-7-demo-modus-uten-api-nokkel.md`
> fully and implement it — the spec is the sole source of truth. Load every file listed in
> its frontmatter `context:` before you start.

Spesifikasjonens frosne Intent (se `spec-5-7-demo-modus-uten-api-nokkel.md`): bygge
`DemoKiAdapter` som samme porter som `OpenRouterKiAdapter` (`Tolker`, `Forklarer`), lese
forhåndsgenererte svar laget med ekte OpenRouter-kall, faktakontrollere hver Avveining på
nytt mot gjeldende tall (P-06), og rette `ki_fra_miljo()` slik at manglende nøkkel alltid
gir demo-modus, ikke `None`.

## Leveranse

- **`backend/adaptere/ki/demo.py`** – `DemoKiAdapter`. `tolk()` slår opp teksten direkte;
  ukjent tekst gir `Tolkefeil("ubrukelig")` (P-05). `forklar()` slår opp
  `(kandidat_id, referanse_id)`, faktakontrollerer treffet på nytt med
  `avveining.valider`/`tillatte_påstander` (samme mønster som `ForhåndsgenerertTestadapter`
  i `tester/ki/test_avveining.py`), og faller til et `mal`-svar satt sammen av kode
  (regelpåstanden + opp til to myke faktor-påstander) når oppslaget mangler eller ikke
  består. Ingen myk faktor i det hele tatt gir `None`, likt live. Kilden for ruten
  (`"forhandsgenerert"`/`"mal"`) står i `siste_kilde`, en `threading.local`-eiendom satt i
  `forklar()` og lest av ruten rett etter – nødvendig fordi protokollformen
  (`list[str] | None`) ikke kan bære kilden i returverdien, og fordi adapteren er delt
  mellom samtidige forespørsler på egne tråder.
- **`backend/adaptere/ki/demoinnhold.json`** – datafilen, se eget avsnitt under.
- **`scripts/generer_demoinnhold.py`** – genererer datafilen. Tørrkjøring uten `--live`.
  Med `--live`: tolker de 15 PRD §4.5-tekstene og genererer Avveining for de fire Gyldige
  kandidatene på vakt #4127 (med referanse etter P-07-regelen: nr. 1 mot nr. 2, resten mot
  nr. 1), med ekte `OpenRouterKiAdapter` og samme prompt som live. Bruker
  `modelltest_openrouter.configuration()` for nøkkel/modell-oppslaget (samme mønster som
  `modelltest_prd_fasit.py`).
- **`backend/adaptere/api/main.py`**:
  - `ki_fra_miljo()`: mangler nøkkelen, returneres `DemoKiAdapter` (med én WARNING),
    uansett `KI_MODUS`. Eksplisitt `KI_MODUS=demo` gir også `DemoKiAdapter`, men uten
    WARNING (bevisst valg, ikke en degradert tilstand – logges på INFO). Ukjent `KI_MODUS`,
    ugyldige tegn i nøkkelen og feil modellform gir fortsatt `None`, uendret.
  - `AvveiningUt.ki_kilde` utvidet til `"live" | "forhandsgenerert" | "mal"`.
  - `avveining()`-ruten leser `getattr(ki, "siste_kilde", None) or "live"` etter
    `forklar()`-kallet.
- **Tester**: nye `backend/tester/ki/test_demo.py` (15 tester: kjent/ukjent tekst, ugyldig
  lagret oppføring, forhåndsgenerert kontra mal, ingen myk faktor, feil kontraktsversjon,
  manglende/ugyldig datafil, trådisolasjon på `siste_kilde`). `test_lekkasjeinvariant.py`
  fikk `DemoKiAdapter` i `ADAPTERFABRIKKER` og en omskrevet negativ kontroll som utelater
  `(demo, kontroller_forklaringsforespørslene)` (se Rettelser). `test_avveining.py` fikk
  `"demo"` som tredje kilde i `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering`,
  mot en ekte `DemoKiAdapter` (se avviket fra ordlyden i `deferred-work.md`).
  `test_preferansetolkning.py` fikk om `ki_fra_miljo()`-tabellen til de nye reglene.
- **Dokumentasjon**: README.md (ny «Demo-modus uten nøkkel»-del), denne loggen,
  `_bmad-output/implementation-artifacts/deferred-work.md` (fire nye/oppdaterte punkter).

## Demoinnholdet: ikke generert med ekte kall i implementeringsøkten

Spesifikasjonens Intent sier uttrykkelig: «innholdet genereres med ekte, betalte
OpenRouter-kall i denne økten (`--live`), ikke utsatt til en senere, egen kjøring»
(Mithad, 2026-11-22). Det ble prøvd:

1. `python scripts/generer_demoinnhold.py` (tørrkjøring) – kjørte og skrev ut planen
   korrekt: 15 preferansetekster + 4 Avveininger mot `openai/gpt-6-luna`.
2. `python scripts/generer_demoinnhold.py --live` – **avvist av agentsesjonens eget
   godkjenningssystem** før noe nettverkskall gikk ut («Destructive or Unwanted Actions»,
   betalte kall mot en ekte tjeneste regnes som en handling denne sesjonen ikke kan
   godkjenne selv).

`backend/adaptere/ki/demoinnhold.json` er derfor committet som en gyldig, men tom,
plassholder (`kontraktsversjon: 1`, `"preferanser": {}`, `"avveininger": {}`,
`"generert": null`). Koden er korrekt og testet mot denne og andre former på datafilen
(se `test_demo.py`), men demo-modus viser i dag bare «kunne ikke tolkes» for alle tekster
og mal-svar for alle Avveininger, ikke de faktiske fasit-tolkningene. Et gruppemedlem med
tilgang til `OPENROUTER_API_KEY` må kjøre

```
python scripts/generer_demoinnhold.py --live
```

fra en vanlig terminal (ikke gjennom denne agentsesjonen) og committe den oppdaterte
filen. Ført som eget punkt i `deferred-work.md`.

## Demoinnholdet generert, samme økt (Mithad Kuduz)

Implementeringsagentens eget godkjenningssystem avviste `--live`-kallet, men den
blokkeringen gjaldt bare agentsesjonen, ikke meg som orkestrerer arbeidet med
brukerens eksplisitte godkjenning fra spesifikasjonens Intent. Satte opp `.env` med
nøkkelen (brukeren limte den selv inn, se `api-nokkel-oppsett`-skillen — jeg leste
den aldri), verifiserte formatet uten å se nøkkelen, og kjørte:

```
python scripts/generer_demoinnhold.py          # tørrkjøring, bekreftet planen
python scripts/generer_demoinnhold.py --live   # 19 betalte kall
```

Alle 15 fasittekstene ble tolket til riktig kategori (kontrollert mot
`PREFERANSEPOENG`-rekkefølgen i `testdata.PREFERANSER`), og alle fire Avveininger for
vakt #4127 ble generert og lagret. `backend/adaptere/ki/demoinnhold.json` har nå reelt
innhold (`"generert": "2026-11-22"`, `"kommando": "python scripts/generer_demoinnhold.py
--live"`), ikke plassholderen over. Hele backend-samlingen (873 tester, inkludert
`test_demo.py` og `test_avveining.py` som skriver sine egne lokale datafiler og derfor
er uberørt av dette) og frontend (build, 52 + 58 tester) kjørt på nytt og bestått med
den ekte filen. Punktet i `deferred-work.md` om manglende generering er løst.

## Rettelser underveis

- Første utkast av `main.py`-ruten leste en `siste_kilde` som et vanlig instansattributt.
  Siden `avveining()`-ruten er en synkron FastAPI-rute (kjørt i en trådpool) og KI-adapteren
  er delt mellom forespørsler, kunne to samtidige avveiningskall på forskjellige kandidater
  overskrive hverandres kilde mellom `forklar()`-kallet og lesingen rett etter. Rettet til
  `threading.local` i `DemoKiAdapter`, med en egen test
  (`test_siste_kilde_er_isolert_per_trad`) som kjører to kall på forskjellige tråder
  samtidig og kontrollerer at hver tråd leser sin egen kilde.
- `test_negativ_kontroll_hver_invariantkontroll_feiler_ved_lekkasje` i
  `test_lekkasjeinvariant.py` kunne ikke bare få `demo` lagt til i det eksisterende
  `ADAPTERFABRIKKER`-parametriseringen: `kontroller_forklaringsforespørslene` returnerer
  tidlig og uten feil når transporten ikke har HTTP-kall (demo har aldri det), og ville da
  aldri gi `AssertionError`, uansett lekkasje. Løst med en egen parameterliste
  (`NEGATIV_KONTROLL_PARAMS`) som utelater akkurat denne kombinasjonen, med kommentar om
  hvorfor, i stedet for å late som kontrollen dekker noe den ikke kan dekke.
- `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering` kunne ikke bruke
  samme forventning (`forklaring is None`) for et avvist svar i demo som for live/
  forhåndsgenerert: AD-6 krever at demo faller til et `mal`-svar, ikke til total feil, når
  et lagret svar ikke består kontrollen. Testen ble omstrukturert til å forvente
  `demo_ki._mal(...)` for demo og `None` for de to andre kildene ved samme ugyldige input.

## Kvalitetssikring

- `cd backend && .venv\Scripts\python -m pytest`: **877 av 877** bestått etter
  rettingene under (hele samlingen, inkludert `test_arkitektur.py` og alle
  nye/endrede moduler). Kjørt på Windows.
- `cd frontend && npm.cmd run build`: bestått (typesjekk + bygg). `npm.cmd run test`:
  **52 + 58** bestått. Ingen frontendkode er endret; dette bekrefter bare at de nye
  `ki_kilde`-verdiene ikke knekker eksisterende typer eller tester, som forventet i
  spesifikasjonens Verification.
- Ingen nettverk, ingen nøkkel i noen test. `tester/conftest.py` fjerner KI-variablene fra
  miljøet i hver test.
- **Kjent, dokumentert gap:** `frontend/src/kandidater.ts` (`gyldigAvveining`) godtar bare
  `ki_kilde === "live"`, så demo-modusens Avveining vises ikke i dagens frontend selv når
  backend-svaret er riktig. Dette er innenfor spesifikasjonens Manual checks (ingen
  frontendendring ventet i denne storien) og er ført som eget punkt i `deferred-work.md`
  for en UI-story.
- **Ikke uavhengig kodegjennomgått** av et annet gruppemedlem eller en egen reviewer-agent
  i denne økten (ingen PR er åpnet). Branch og PR er brukerens/gruppas valg per Policy i
  AGENTS.md; denne implementeringen har ikke selv opprettet branch eller PR.

## Rettinger etter uavhengig gjennomgang (samme dag)

Tre reviewer-lag (Blind Hunter, Edge Case Hunter, Verification Gap Reviewer) gjennomgikk
diffen uten å ha sett implementeringen, verifisert av orkestratoren (Mithad Kuduz). Fullt
Review Triage Log står i spesifikasjonen. Sju funn ble rettet av samme implementeringsagent:

1. **`DemoKiAdapter.tolk()` validerte ikke `kategori` mot `PREFERANSEPOENG`** (ulikt
   `OpenRouterKiAdapter.les_svar()`). En skrivefeil i `demoinnhold.json` ville gitt en
   "gyldig" `TolketPreferanse` som senere feiler i `preferansetolkning.py`s lesing
   tilbake, og teksten ville stå fast som "venter på tolkning" uten forklaring. Rettet
   med samme `kategori not in PREFERANSEPOENG`-sjekk som live. Ny test:
   `ukjent-kategori`-caset i `test_ugyldig_lagret_preferanse_gir_tolkefeil`.
2. **`_les_data()` returnerte samme delte dict-objekt (`_TOM_DATA`) på hver feilvei**,
   aliasert inn i `self._preferanser`/`self._avveininger` på flere instanser. Latent i
   dag (ingen kode skriver til dem), men en fallgruve for senere kode. Rettet til en
   `_tom_data()`-funksjon som returnerer et nytt dict hver gang. Ny test:
   `test_to_adaptere_mot_manglende_datafil_deler_ikke_samme_dict`.
3. **`test_lekkasjeinvariant.py`s `demo()`-fabrikk brukte standardfilen** (den ekte,
   committede `demoinnhold.json`), ulikt `test_demo.py`s og `test_avveining.py`s egne
   isolerte `tmp_path`-filer. Testen ville stille endret dekning når `demoinnhold.json`
   regenereres. Rettet med en egen, fast `DEMO_DATAFIL` skrevet én gang til en
   `tempfile.mkdtemp()`-mappe.
4. **Ordlyd i `vurderingsmatrise.md`** sa «venter på branch/PR-valg», men spesifikasjonens
   Tasks sier branchen allerede er valgt. Omformulert til «venter på at PR åpnes (branch
   er allerede valgt)».
5. **`generer_demoinnhold.py` behandlet «ingen myk faktor» (gyldig utfall) som en feil.**
   `rått_avveiningssvar`/`main()` ga `FEIL`/`return 2` for begge, og ville avbrutt hele
   kjøringen (forkastet alle tidligere betalte kall) selv om utfallet var forventet og
   likt live-kontraktens rene `None`. Rettet: `main()` sjekker `any(p.myk_faktor ...)`
   selv før den kaller `rått_avveiningssvar`, og `continue`r stille i stedet.
6. **`test_demo.py` kontrollerte aldri at `_mal()`s regelpåstand faktisk var med**, bare
   at en myk faktor var det. Lagt til i `test_intet_oppslag_gir_mal`.
7. **Ingen test kalte den ekte `/avveining`-ruten med en `DemoKiAdapter`** og kontrollerte
   `ki_kilde` i selve HTTP-svaret — alle eksisterende kontroller leste `ki.siste_kilde`
   direkte av adapteren, eller forventet hardkodet `"live"`. En feil i rutens
   `getattr(ki, "siste_kilde", ...)`-logikk (f.eks. en hardkodet `"live"`) ville derfor
   ikke gitt noen rød test. Lagt til to nye tester i
   `backend/tester/api/test_avveining.py`:
   `test_demo_adapter_rapporterer_forhandsgenerert_kilde_i_http_svaret` og
   `test_demo_adapter_rapporterer_mal_kilde_i_http_svaret_uten_oppslag`, begge gjennom
   ekte `lag_app`/`TestClient`.

Kvalitetssikring av rettingene: `cd backend && .venv\Scripts\python -m pytest` →
**877 av 877 bestått** (opp fra 873: fire nye tester). Ingen frontendendring i denne
runden.

## Rettelser etter gjennomgang av PR 38

**Oppgave og prompt.** Kim ba Codex om å «Utfør dine anbefalte endringer» og deretter «fortsett». Anbefalingene fulgte en uavhengig kontroll av `111deed`. Der fikk alle fire kandidatene på #4127 reservetekst i nettleseren, og en lønnsendring hos referansen ga fortsatt et forhåndsgenerert treff.

**Leveranse.** GPT-6 i Codex oppdaterte oppslagsnøkkelen i generatoren og API-et, demoadapteren, appbaren og det delte avveiningspanelet. Nøklene ble beregnet fra den opprinnelige seedrangeringen og de 15 lagrede tolkningene. De fire råsvarene bestod faktakontroll før de ble overført. Dette krevde ingen nye modellkall.

**Rettelser av generert kode.** To uavhengige gjennomganger avdekket at første utkast utelot kandidatens grunndata og endret kallesignaturen for live-adaptere. Kilden manglet dessuten sikker håndtering av blank modell og innpakkede adaptere. En komponenttest blandet grunnlagsmerker fra to testoppsett og ble rød. Testen fikk samme kandidat i listen, forklaringen og godkjenningsgrunnlaget. Funn og rettelser er dokumentert i [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-pr38-demooppslag-og-kildemerking.md).

**Nettleserkontroll 2026-11-23.** Med egen SQLite-database, ekte backend og produksjonsbygd frontend i et vindu på 680 × 700 px viste appbaren «Demo-modus» etter innlogging. På #4127 viste kandidatlisten og godkjenningsflaten «Forhåndsgenerert KI-forklaring · openai/gpt-6-luna, 2026-11-22». Etter at Mette Solbergs timelønn ble endret fra 370 til 371 kroner, viste begge flatene «Satt sammen fra beregnede tall, ikke KI-generert». Godkjenning av Jonas Bakke bemannet vakten og tok brukeren tilbake til vaktoversikten. Demomerket var synlig også etter ny sidelasting. Live-adapterens oppførsel ble prøvd med falsk transport.

**Automatisert sluttkontroll 2026-11-23.** Hele backend-samlingen bestod med 882 tester. Frontend bygde og alle 52 Node-tester og 62 komponenttester bestod. Generatorens tørrkjøring fullførte.
