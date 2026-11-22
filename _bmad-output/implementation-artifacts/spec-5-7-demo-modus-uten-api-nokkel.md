---
title: 'Story 5.7: Demo-modus uten API-nøkkel'
type: 'feature'
created: '2026-11-22'
status: 'done'
route: 'dispatch'
baseline_commit: 'f9bf993cd445ed125157ad426474d36de00e2006'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan i dag ikke kjøres eller vurderes uten gruppens `OPENROUTER_API_KEY`: `ki_fra_miljo()` returnerer `None` når nøkkelen mangler, og `KI_MODUS=demo` gir eksplisitt «ikke bygget ennå». Dette bryter AD-6/SM-9 (appen skal kunne bygges og kjøres fra et rent klonet repo uten nøkkelen) og hindrer en sensor uten nøkkel i å se preferansetolkning og Avveining i bruk.

**Approach:** Bygg `DemoKiAdapter` som implementerer samme porter som `OpenRouterKiAdapter` (`Tolker`, `Forklarer`). Den leser forhåndsgenererte `TolketPreferanse`-verdier for PRD §4.5s 15 fasittekster, og slår opp forhåndsgenererte Avveininger på en identitet (Vakt, Kandidat, referanse, kontraktsversjon), re-validert mot gjeldende uavrundede tall med samme `avveining.valider`/`tillatte_påstander` som i dag. Mangler oppslaget eller består det ikke kontrollen, settes svaret sammen direkte fra allerede godkjente påstander (`mal`), aldri KI-generert. Rett `ki_fra_miljo()` slik at manglende nøkkel alltid gir demo-modus (ikke `None`), uansett eksplisitt `KI_MODUS`, med én WARNING-logglinje. Utvid `ki_kilde` til `"live" | "forhandsgenerert" | "mal"`.

## Boundaries & Constraints

**Always:**
- `DemoKiAdapter` har nøyaktig samme form som `Tolker`/`Forklarer`-protokollene i `adaptere/ki/openrouter.py` (se kommentaren ved `Tolker`: «DemoKiAdapter (story 5.7) skal ha samme form»). Kjøretidsinvariant-testen fra story 5.6 (lekkasje) må bestå mot begge adaptere.
- Ukjent/uregistrert preferansetekst i demo gir `kunne_ikke_tolkes` og midlertidig 50 poeng — aldri «Ingen registrert» og aldri en oppdiktet kategori (P-05, AD-6 punkt 1).
- En forhåndsgenerert Avveining faktakontrolleres på nytt ved hvert oppslag mot gjeldende, uavrundede tall (P-06). Består den ikke, eller finnes ikke oppslaget, brukes `mal`, aldri en foreldet sammenligning.
- `mal`-svaret er satt sammen av kode fra allerede beregnede, godkjente påstander (gjenbruk `avveining.tillatte_påstander`) — aldri fritekst, aldri KI-generert. Har kandidaten ingen myk faktor-påstand (alle faktorer like egen total), er svaret `None` som i dag, uavhengig av kilde.
- Forhåndsgenererte svar for Avveining og preferansetolkning er laget med `OpenRouterKiAdapter` og samme prompt som live; modell, dato og kommando logges i `docs/ki-logg/` (AD-6). **Avgjort 2026-11-22 (Mithad):** innholdet genereres med ekte, betalte OpenRouter-kall i denne økten (`--live`), ikke utsatt til en senere, egen kjøring.
- `ki_fra_miljo()`: mangler `OPENROUTER_API_KEY`, returneres `DemoKiAdapter` — uansett om `KI_MODUS` er `openrouter` (standard) eller eksplisitt satt, siden AD-6s regel ikke betinger dette på modusvalget. Eksplisitt `KI_MODUS=demo` gir også `DemoKiAdapter`, med eller uten nøkkel. Ukjent `KI_MODUS`-verdi er fortsatt en feil (ingen KI, som i dag).
- Live-modus (`OpenRouterKiAdapter`) faller aldri stille tilbake til demo ved en feil under kjøring — bare ved oppstart, når nøkkelen mangler.
- Testene i `test_lekkasjeinvariant.py` (5.6) og `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering` (5.4) parametriseres over `DemoKiAdapter` i tillegg til dagens adaptere, slik `deferred-work.md` allerede forutsetter.

**Never:**
- Ingen nettverkskall eller nøkkel i noen test. CI får aldri `OPENROUTER_API_KEY`.
- Ikke endre selve faktakontrollen (`avveining.valider`/`tillatte_påstander`) eller rangeringsformelen.
- Ikke bygg et generelt cache-/fallback-lag for live-modus — demo og live er to separate, fullstendige implementasjoner av samme port, ikke én adapter med en demo-bryter inni.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Ingen nøkkel, KI_MODUS tom | Oppstart uten `OPENROUTER_API_KEY` | `DemoKiAdapter` startes, én WARNING logges, appen krasjer ikke | — |
| Eksplisitt demo med nøkkel | `KI_MODUS=demo`, nøkkel satt | `DemoKiAdapter` startes likevel (nøkkelen brukes ikke) | — |
| Kjent fasittekst | Tolkning av en av de 15 PRD §4.5-tekstene i demo | Forhåndsgenerert `TolketPreferanse` med riktig kategori | — |
| Ukjent tekst i demo | Tolkning av en tekst uten forhåndsgenerert treff | `kunne_ikke_tolkes`, midlertidig 50 poeng | Ingen krasj, ingen oppdiktet kategori |
| Kjent Avveining-identitet, fortsatt gyldig | Oppslag treffer, og forhåndsgenerert svar består faktakontroll mot gjeldende tall | `ki_kilde: "forhandsgenerert"`, samme påstandsform som live | — |
| Treff, men grunnlaget er endret | Oppslag treffer, men lagret svar består ikke kontrollen mot nåværende tall | `mal`-svar fra gjeldende beregnede påstander, `ki_kilde: "mal"` | Ingen foreldet sammenligning vises |
| Intet oppslag | Vakt/kandidat/referanse uten forhåndsgenerert Avveining | `mal`-svar, `ki_kilde: "mal"` | — |
| Ingen myk faktor i det hele tatt | Én gyldig kandidat med alle faktorer lik egen total | `avveining_feilet`, likt dagens live-kontrakt | Ikke en demo-spesifikk feil |
| Ukjent KI_MODUS-verdi | `KI_MODUS=noe_annet` | Ingen KI startes (som i dag), én WARNING | Uendret oppførsel |

</frozen-after-approval>

## Code Map

- `backend/adaptere/ki/openrouter.py` -- `Tolker`/`Forklarer`-protokollene (linje 85–95) definerer formen `DemoKiAdapter` må ha. `Tolkefeil`, `PREFERANSEPOENG`-avhengig skjema er gjenbrukt derfra. Ikke endre selve `OpenRouterKiAdapter`.
- `backend/adaptere/ki/avveining.py` -- `tillatte_påstander(kandidat, referanse)` bygger den kontrollerte påstandslisten; `valider(svar, tillatte)` kontrollerer et rått svar (brukes i dag av `ForhåndsgenerertTestadapter` i `tester/ki/test_avveining.py:78`, som er mønsteret for ekte oppslag+kontroll). `mal` bygges av `tillatte_påstander` direkte uten `valider`.
- `backend/adaptere/api/main.py` -- `ki_fra_miljo()` (linje 361–381): rett rekkefølgen slik at manglende nøkkel returnerer `DemoKiAdapter`, ikke `None`. `ki_kilde: Literal["live"]` (linje 320) utvides til de tre verdiene. `avveining()`-ruten (linje ~559–575) må lese hvilken kilde adapteren brukte for det konkrete kallet.
- `domene/porter/rangering.py` -- `RangertKandidat`, `EksaktePoeng` (uendret, bare lest).
- `backend/adaptere/lagring/testdata.py` -- `PREFERANSER` (linje 64, 15 fasittekster) og `FASIT[4127]` (linje 703) er kildedataene forhåndsgenereringen dekker.
- Ny fil: `backend/adaptere/ki/demo.py` -- `DemoKiAdapter`-klassen.
- Ny fil (data): forhåndsgenererte verdier, generert av et nytt skript (se under), ikke håndskrevet.
- Nytt skript: `scripts/generer_demoinnhold.py` -- tørrkjøring uten `--live` (viser hva som ville blitt generert), `--live` gjør de faktiske OpenRouter-kallene og skriver datafilen. Følg mønsteret i `scripts/modelltest_prd_fasit.py` (argparse, samme takt/retry som appen).
- `backend/tester/api/test_lekkasjeinvariant.py` (story 5.6) -- `ADAPTERFABRIKKER`, `kjør_flyt`, se Implementation Notes i `spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md` for nøyaktig hvordan demo legges til uten å skrive testen om.
- `backend/tester/ki/test_avveining.py` -- `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering` (linje 95) parametriseres over ekte `DemoKiAdapter` via `lag_app`, per `deferred-work.md`-punktet fra PR #37.
- `README.md` -- dokumenter `KI_MODUS=demo` og at manglende nøkkel gir demo (AD-6, SM-9).

## Tasks & Acceptance

**Execution:**
- [x] `scripts/generer_demoinnhold.py` -- generer forhåndsgenererte `TolketPreferanse`-verdier for alle 15 fasittekster og Avveininger for #4127s gyldige kandidater (med og uten referanse) -- AC2, AC4.
      Skriptet er laget, tørrkjøringen validert, og `--live` kjørt av Mithad Kuduz
      2026-11-22 (agentsesjonens eget godkjenningssystem avviste kallet; orkestratoren
      kjørte det i stedet). `backend/adaptere/ki/demoinnhold.json` har nå reelt innhold:
      alle 15 fasittolkningene og alle fire Avveininger for #4127.
- [x] `backend/adaptere/ki/demo.py` -- `DemoKiAdapter` (Tolker + Forklarer), leser datafilen, faktakontrollerer Avveining-oppslag på nytt, faller tilbake til `mal` -- AC1–AC3
- [x] `backend/adaptere/api/main.py` -- rett `ki_fra_miljo()`, utvid `ki_kilde`, oppdater `avveining()`-ruten til å rapportere riktig kilde -- AC1, AC5
- [x] `backend/tester/api/test_preferansetolkning.py`, `test_lekkasjeinvariant.py`, `backend/tester/ki/test_avveining.py` -- dekk alle rader i matrisen, inkludert negativ kontroll og at demo aldri gir et foreldet svar -- AC1–AC5.
      Ny `backend/tester/ki/test_demo.py` (15 tester) dekker `DemoKiAdapter` isolert.
      873 av 873 backendtester bestod.
- [x] `docs/ki-logg/`, `README.md`, `docs/testing.md`, `docs/emne/vurderingsmatrise.md` -- dokumenter genereringskommandoen (modell, dato), demo-oppsettet og testdekningen.
      Se `docs/ki-logg/2026-11-22-demo-modus-uten-api-nokkel.md`.
- [x] Kjør `python scripts/generer_demoinnhold.py --live` med en ekte nøkkel og committ den oppdaterte `backend/adaptere/ki/demoinnhold.json`.
      Kjørt av Mithad Kuduz 2026-11-22 (implementeringsagentens eget godkjenningssystem
      avviste kallet; orkestratoren kjørte det i stedet med brukerens eksplisitte
      godkjenning). 19 kall, alle 15 kategorier riktige mot fasiten. Se KI-loggens
      «Demoinnholdet generert, samme økt».

**Ikke gjort i denne økten (se Implementation Notes og `deferred-work.md`):**
- [ ] Branch+PR er allerede valgt (Mithad, før implementeringen startet). PR er ikke åpnet ennå, og uavhengig kodegjennomgang gjenstår.
- [ ] Frontend: `gyldigAvveining` i `frontend/src/kandidater.ts` godtar bare `ki_kilde === "live"` og viser derfor ikke demo-modusens kildelinje (UX-DR27). Dokumentert som åpent punkt for en UI-story, ikke rettet her (ingen frontendendring var ventet, se Verification).

**Acceptance Criteria:**
- Gitt et rent klonet repo uten `OPENROUTER_API_KEY`, når backend startes, så kjører appen i demo-modus uten å krasje, med én WARNING logget.
- Gitt en av de 15 PRD §4.5-tekstene i demo, når preferansen tolkes, så er kategorien lik fasiten, og en ukjent tekst gir `kunne_ikke_tolkes` med 50 poeng.
- Gitt en Avveining i demo med gyldig forhåndsgenerert treff, når grunnlaget er uendret, så vises `ki_kilde: "forhandsgenerert"` med samme faktakontrollerte påstandsform som live.
- Gitt et manglende treff eller et grunnlag som har endret seg, når Avveiningen bygges i demo, så vises `ki_kilde: "mal"` satt sammen av kode, aldri en foreldet sammenligning.
- Gitt kjøretidsinvariant-testen fra story 5.6, når den kjøres mot `DemoKiAdapter`, så lekker ingen utelukket kandidat, og den negative kontrollen viser fortsatt at testen faktisk kan feile.

## Implementation Notes

- **Mekanismen for `ki_kilde` i ruten (Design Notes-spørsmålet):** `OpenRouterKiAdapter`
  er uendret og har ingen kilde-attributt (alltid `"live"` implisitt). `DemoKiAdapter`
  setter `siste_kilde` i en `threading.local` inne i `forklar()`, rett før den returnerer,
  og eksponerer den som en `@property`. `avveining()`-ruten i `main.py` leser
  `getattr(ki, "siste_kilde", None) or "live"` rett etter `forklar()`-kallet. `threading.local`
  (ikke et vanlig instansattributt) er nødvendig fordi `avveining()` er en synkron FastAPI-
  rute kjørt i en trådpool, og KI-adapteren er delt mellom samtidige forespørsler; et vanlig
  attributt kunne blitt overskrevet av en annen forespørsel mellom kallet og lesingen.
- **Identiteten for Avveining-oppslaget:** `(kandidat_id, referanse_id | None)`, ikke
  `(Vakt, Kandidat, referanse, kontraktsversjon)` ordrett som skissert i Intent. Siden
  `Forklarer.forklar(kandidat, referanse)` ikke får vaktnummeret (samme protokollform som
  live, jf. Boundaries), kan ikke Vakt være en del av nøkkelen uten å endre protokollen.
  I stedet bærer selve faktakontrollen (P-06) denne garantien: skulle samme kandidat-/
  referanse-ID-par forekomme på en annen vakt eller med andre tall, ville de lagrede
  påstandene nesten alltid ikke bestå `valider()` mot de nye, uavrundede verdiene, og
  demo faller automatisk til `mal`. `kontraktsversjon` er et eget felt i datafilen (heltall,
  delt konstant `KONTRAKTSVERSJON` i `demo.py` og `generer_demoinnhold.py`) som beskytter
  mot et endret dataformat, uavhengig av innholdet.
- **Datafilens skjema** (`backend/adaptere/ki/demoinnhold.json`): `{"kontraktsversjon": 1,
  "modell": str, "generert": str | null, "kommando": str, "preferanser": {tekst:
  {"kategori", "begrunnelse", "modell"}}, "avveininger": {"<kandidat_id>:<referanse_id|"">":
  <modellens rå "paastander"-svar, ikke den validerte teksten>}}`. Rå svar lagres (ikke
  den ferdige teksten) nettopp for at `avveining.valider`/`tillatte_påstander` kan kjøre på
  nytt mot gjeldende tall ved hvert oppslag, slik Design Notes krever.
- **`mal` sammensatt av kode:** regelpåstanden (alltid til stede) pluss opp til to
  myke-faktor-påstander fra `tillatte_påstander`, i den rekkefølgen de kommer. Minst én er
  garantert av kontrollen `any(p.myk_faktor for p in tillatte)` i `forklar()`.
- **`scripts/generer_demoinnhold.py`** bygger et temporært SQLite-grunnlag med
  `adaptere.lagring.testdata.fyll_testdata`, kjører ekte `vurder_kandidater`/`ranger` for
  vakt #4127, og bruker `OpenRouterKiAdapter`s "private" `_forespørsel`/`_send` (ikke
  `forklar()`, som bare returnerer validert tekst eller `None`) for å fange opp modellens
  rå svar før validering — det er nettopp det rå svaret datafilen skal lagre.
- **Avvik fra ordlyden i `deferred-work.md`-oppfølgingen av PR #37** («parametriser … gjennom
  `lag_app`»): `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering`
  bygger en ekte `DemoKiAdapter` mot en lokal `demoinnhold.json` i `tmp_path` og kaller
  `.forklar(en, to)` direkte, ikke via `TestClient`/`lag_app`. Testens `en`/`to` kommer fra
  syntetiske fixtures (`tester/regelmotor/test_rangering.py`), ikke fra en database
  `lag_app` kan lese et grunnlag fra. Dekningen er likevel reell: en demokilde som ikke
  kaller `valider()` ville gitt rød test her.
- **Ikke gjort:** frontendens kildelinje for de nye `ki_kilde`-verdiene (var ikke ventet i
  denne storien), og at PR åpnes/uavhengig gjennomgang av dette arbeidet (branchen er
  allerede valgt). `--live`-kjøringen av `generer_demoinnhold.py` er gjort, se Tasks over.

## Spec Change Log

- 2026-11-22 (implementering): Intent sier «innholdet genereres med ekte, betalte
  OpenRouter-kall i denne økten (`--live`)». Dette ble prøvd og avvist av agentsesjonens
  eget godkjenningssystem (betalte, eksterne nettverkskall), ikke av en teknisk feil i
  skriptet. Spesifikasjonens krav står uendret; se Implementation Notes og
  `deferred-work.md` for hva som gjenstår og hvorfor.

## Review Triage Log

Tre lag kjørt parallelt mot diffen (Blind Hunter, Edge Case Hunter, Verification Gap
Reviewer). Alle funn verifisert mot koden av orkestratoren (Mithad Kuduz, 2026-11-22),
reviewer-alvorlighet ignorert.

**patch** (sendt til samme implementeringsagent, a410757270b6e7edd):
1. `DemoKiAdapter.tolk()` validerer ikke `kategori` mot `PREFERANSEPOENG`, ulikt
   `OpenRouterKiAdapter.les_svar()` (openrouter.py:199) -- verdict: high. Bekreftet ved
   lesing av begge; en skrivefeil i `demoinnhold.json` ville gitt en "gyldig" tolkning som
   senere feiler ved lesing tilbake i `preferansetolkning.py`.
2. `_les_data()`/`_TOM_DATA` (demo.py:54,61-80) returnerer samme delte dict-objekt på hver
   feilvei, aliasert inn i `self._preferanser`/`self._avveininger` -- verdict: medium
   (latent, ingen kode skriver til dem i dag, men fallgruve for senere kode).
3. `test_lekkasjeinvariant.py`s `demo()`-fabrikk bruker standard (ekte, committet)
   `demoinnhold.json` i stedet for en isolert `tmp_path`-fil, ulikt `test_demo.py`s eget
   mønster -- verdict: medium (kobler testen til innhold som kan endres ved regenerering).
4. `docs/emne/vurderingsmatrise.md` linje 7-9 sier "venter på branch/PR-valg", men spesifikasjonens
   Tasks sier branchen allerede er valgt -- verdict: low, ren ordlyd.
5. `scripts/generer_demoinnhold.py`s `rått_avveiningssvar`/`main()` behandler "ingen myk
   faktor" (gyldig utfall) likt som en mislykket modellkall -- begge gir `FEIL`/`return 2`
   og avbryter kjøringen -- verdict: medium. Bekreftet ved lesing av linje 95-96 og 156-159.
6. `test_demo.py` kontrollerer aldri at `_mal()`s regelpåstand faktisk er med (bare myke
   faktorer kontrolleres) -- verdict: low, testdekning.
7. Ingen test kaller den ekte `/avveining`-ruten med en `DemoKiAdapter` og kontrollerer
   `ki_kilde` i HTTP-svaret -- alle eksisterende kontroller leser `ki.siste_kilde` direkte
   av adapteren eller forventer hardkodet `"live"` -- verdict: high (reist av
   Verification Gap Reviewer, forhåndsverifisert evidens godtatt som arkivert).
   Demonstrasjon: hardkod `kilde = "live"` på main.py:586 -- hele samlingen ville fortsatt
   bestå.

**Status etter retting (samme implementeringsagent, 2026-11-22):** alle sju er rettet.
1. `DemoKiAdapter.tolk()` sjekker nå `kategori not in PREFERANSEPOENG`, likt
   `les_svar()`. Ny parametrisert case `ukjent-kategori` i
   `test_ugyldig_lagret_preferanse_gir_tolkefeil`.
2. `_les_data()` returnerer nå et nytt dict fra `_tom_data()` på hver feilvei, ikke en
   delt modulvariabel. Ny test `test_to_adaptere_mot_manglende_datafil_deler_ikke_samme_dict`.
3. `test_lekkasjeinvariant.py`s `demo()`-fabrikk bruker nå en egen, isolert datafil
   (`DEMO_DATAFIL`, skrevet én gang til en `tempfile.mkdtemp()`-mappe), ikke den
   committede `demoinnhold.json`.
4. `docs/emne/vurderingsmatrise.md` linje 6-9 og 278 omformulert: "venter på at PR åpnes
   (branch er allerede valgt) og på uavhengig gjennomgang".
5. `generer_demoinnhold.py`s `main()` sjekker nå `any(p.myk_faktor ...)` for hver
   kandidat *før* den kaller `rått_avveiningssvar`, og `continue`r (ikke `return 2`) når
   ingen myk faktor finnes -- det er et gyldig utfall, likt live-kontrakten, ikke en feil.
6. `test_intet_oppslag_gir_mal` kontrollerer nå at `svar[0]` er regelpåstanden.
7. To nye rutenivå-tester i `backend/tester/api/test_avveining.py`:
   `test_demo_adapter_rapporterer_forhandsgenerert_kilde_i_http_svaret` og
   `test_demo_adapter_rapporterer_mal_kilde_i_http_svaret_uten_oppslag`. Begge bygger
   `lag_app` med en ekte `DemoKiAdapter` mot en isolert `tmp_path`-datafil og kaller den
   ekte `/avveining`-ruten via `TestClient`, og kontrollerer `ki_kilde` i selve
   HTTP-svaret (ikke `ki.siste_kilde` direkte).

877 av 877 backendtester bestod etter rettingene (opp fra 873: to nye rutenivå-tester i
`test_avveining.py`, to nye i `test_demo.py`).

**defer** (ført i `deferred-work.md`):
- AGENTS.md's "Kjøring og verifisering"-avsnitt er foreldet etter denne storyen (sier
  fortsatt at manglende nøkkel/`demo`/ukjent verdi "tolkes ingenting"). Reell årsak, men
  retting gjelder en agentkontekstfil, så den utsettes per arbeidsflytregelen i stedet for
  å rettes her.
- `generer_demoinnhold.py` har ingen delvis lagring/gjenopptak: ett mislykket kall blant 19
  forkaster alle tidligere betalte kall i samme kjøring. Lav praktisk kostnad i dag (19
  kall får plass i kontoens 20/minutt-grense, så en full ny kjøring er billig), men verdt
  en sjekkpunktmekanisme hvis skriptet vokser.

**Ingen endring nødvendig / avvist (verifisert og forkastet):**
- Negativ kontroll for `demo` på `kontroller_forklaringsforespørslene` dekker reelt sett
  ingenting (ingen HTTP i demo) -- allerede dokumentert med begrunnelse i koden og
  KI-loggens "Rettelser underveis".
- Eksplisitt `KI_MODUS=openrouter` med manglende nøkkel er udekket som egen test, men
  koden tar nøyaktig samme kodevei som den allerede testede "nøkkel ikke satt"-saken
  (begge gir `not nøkkel` → `DemoKiAdapter()`) -- ingen reell dekningstap.
- `rått_avveiningssvar` dupliserer formen på `OpenRouterKiAdapter`s private
  forespørsel/respons -- allerede dokumentert i funksjonens egen docstring som et kjent,
  bevisst valg.
- **Forkastet (falsk):** manglende nøkkel skulle gi `DemoKiAdapter.tolk()` som permanent
  "kunne ikke tolkes" for alle andre sådde preferansetekster enn de 15 kjente. Kontrollert:
  `testdata.PREFERANSER` har nøyaktig 15 oppføringer, identisk med de 15 PRD §4.5-tekstene
  skriptet genererer svar for -- ingen sådd tekst er udekket.
- **Forkastet (falsk):** en fjernet parametrisert test for tom/mellomrom-nøkkel under
  `KI_MODUS=openrouter` skulle være et reelt dekningstap. Samme kodevei som den beholdte
  "nøkkel ikke satt"-testen (`strip()` gir samme tomme streng) -- ingen ny gren udekket.
- Avviket mellom Intent sin skisserte identitet `(Vakt, Kandidat, referanse,
  kontraktsversjon)` og den faktiske `(kandidat_id, referanse_id)` er allerede forklart og
  begrunnet i Implementation Notes -- ingen videre retting.
- Sesjonslogg-id `977` kontra eksisterende `978`/`981` i `.logs/mithad-kuduz/` -- utenfor
  denne gjennomgangens omfang (bokføring i et annet, urelatert system).
- **Forkastet (retting ville vært å endre denne spesifikasjonen):** Tasks-linje 71 sier
  Avveininger genereres "med og uten referanse", men alle fire lagrede oppføringer har en
  referanse (P-07 gir alltid én, også for kandidat nr. 1). Rettingen ville vært å endre
  selve spesifikasjonsteksten, som er utenfor denne loggens omfang per arbeidsflytregelen.

**Manuell verifisering utført under triagen:**
`.venv\Scripts\python -m uvicorn adaptere.api.main:app` uten `OPENROUTER_API_KEY`: startet
uten feil, nøyaktig én WARNING-linje ("Preferansetolkning kjører i demo-modus:
OPENROUTER_API_KEY er ikke satt. Se README."), `GET /api/helse` svarte `{"status":"ok"}`.
Spesifikasjonens Verification-kommando er dermed faktisk kjørt, ikke bare antatt.

## Design Notes

- **Hvorfor re-validering, ikke bare avspilling:** et forhåndsgenerert svar kan bli feil hvis testdataene eller vektene endrer seg etter at det ble generert. `ForhåndsgenerertTestadapter`-mønsteret (allerede i `test_avveining.py`) kjører samme `valider`/`tillatte_påstander` som live, så en foreldet lagret sammenligning blir avvist automatisk i stedet for vist som sann.
- **Hvorfor `mal` bygges av kode, ikke av en forenklet KI-prompt:** AD-6 krever at maltekst aldri gir seg ut for KI-generert innhold. Siden `tillatte_påstander` allerede produserer ferdige, korrekte norske setninger for enhver gyldig påstand, er den enkleste og tryggeste `mal`-kilden å gjenbruke én eller flere av dem direkte, uten noe nytt tekstlag.
- **Hvordan ruten får vite hvilken kilde som ble brukt:** `Forklarer`-protokollen utvides med en liten rapporteringsmekanisme (for eksempel en metode som returnerer kilden for siste kall, eller et attributt adapteren setter under `forklar()`). `OpenRouterKiAdapter` returnerer alltid `"live"`. Eksakt mekanisme avgjøres under implementering og føres i Implementation Notes — det er ikke en produktbeslutning, bare en kodegrensesnitt-detalj.

## Verification

**Commands:**
- `cd backend && .venv\Scripts\python -m pytest` -- expected: hele samlingen består, inkludert `test_arkitektur.py` og den utvidede `test_lekkasjeinvariant.py`
- `cd frontend && npm.cmd run build` og `npm.cmd run test` -- expected: består (ingen frontendendring ventet, men `ki_kilde`s nye verdier må ikke knekke eksisterende typer/tester)
- `TURNUSHJELPEREN_DB=<midlertidig> .venv\Scripts\python -m uvicorn adaptere.api.main:app` uten `OPENROUTER_API_KEY` -- expected: starter uten feil, logger WARNING, `/api/helse` svarer

**Manual checks (if no CLI):**
- Ingen ny UI. Hvis kildelinjen («Forhåndsgenerert KI-forklaring» / «Satt sammen fra beregnede tall») ikke allerede vises riktig i frontend for de nye `ki_kilde`-verdiene, dokumenter det som et åpent punkt for en UI-story.
