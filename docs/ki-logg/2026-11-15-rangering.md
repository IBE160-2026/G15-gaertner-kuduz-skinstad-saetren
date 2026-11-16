# KI-logg: story 4.4 – rangering av gyldige kandidater

## Oppgave og prompt

Implementeringen ble delegert til en underagent (Claude Opus 5.5 i Claude Code) med denne prompten: «Read `_bmad-output/implementation-artifacts/spec-4-4-rangering-av-gyldige-kandidater.md` fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.» Agenten leste spesifikasjonen, epic-konteksten for epic 4, beslutningsreferatet og `docs/testing.md`, i tillegg til PRD §4.4–4.5, DESIGN.md, epics og den eksisterende koden.

## Hva modellen leverte

- **Porten** `backend/domene/porter/rangering.py`: `Tolkestatus` (`tolket`, `venter_paa_tolkning`, `kunne_ikke_tolkes`, `ingen_registrert`), en minimal `TolketPreferanse` med `kategori` og `RangertKandidat` med plass, kandidatfakta (kostnad og fordeling, timer og prosent, ulempe og fordeling), faktorpoeng, totalscore og tolkestatus. Porten har ikke Kandidatens vakter eller rå minutter.
- **Rangeringen** `backend/domene/regelmotor/rangering.py`: `Rangeringsparametere` med vektene som `Fraction` og taket fra `ulempebelastning.STANDARD_TAK`, `STANDARD_PARAMETERE`, `PREFERANSEPOENG` og `ranger(vurdering, vakt, tolkede, feilede, parametere)`. Kostnad (som `float`) og timer i startuka normaliseres med min–maks over alle gyldige, og Ulempescoren regnes på nytt fra poengene med parameterens tak. Alt regnes eksakt med `Fraction` og sorteres på `(-total, id)`. Verdiene gjøres om til `float` først i porten.
- **Domenetypen** `Kandidat` har fått `preferanse`, `stilling` og `ansiennitet` med standardverdi og `compare=False`, og `kandidatgrunnlag.py` fyller dem fra `AnsattRad`.
- **API-et**: kandidatruten kaller `ranger` og svarer med `RangertKandidatUt`, som er alle feltene i `KandidatUt` pluss `stilling`, `ansiennitet`, `plass`, `totalscore`, `faktorpoeng` (kostnad, timebelastning, ulempe), `preferansepoeng`, `tolkestatus` og `preferansekategori`. `KandidatUt` og godkjenningsruten er ikke endret.
- **Frontend**: `RangertKandidat` i `api.ts`, `synligeKandidater`, `SYNLIGE_KANDIDATER` og `preferansetekst` i `kandidater.ts`, og en `<table>` i rullebeholder i `Kandidatflate.tsx` som erstatter `ul.kandidatliste`. Kolonnene er plass (`rank-badge`, med totalscore i `meta`), kandidat (navn, med stilling · ansiennitet i `meta`), kompetanse-tag, kostnad (`Kostnadsvisning`), timebelastning (timer i uka, linje og `Varselmerke`), ulempe, preferanse-tag med poeng, og Velg i siste kolonne. Annenhver rad har `row-alt`. De fem øverste vises. «Vis alle gyldige kandidater» viser resten og flytter fokus til Velg i den sjette raden. Tekstene står i `tekster.ts`, og `--font-size-rank` (14px) er nytt i `tokens.css`. Det ubrukte `--column-hours-width` er fjernet sammen med CSS-reglene for den gamle listen.
- **Tester**: ny `tester/regelmotor/test_rangering.py` (41 tester), nye og endrede tester i `tester/api/test_kandidater.py`, `test_godkjenningsgrunnlag.py`, `frontend/tester/kandidater.test.mjs` og `tester/komponenter/kandidatflate.test.tsx`.

## Avgjørelser underveis

Disse står ikke i spesifikasjonen og bør ses over i PR-gjennomgangen:

- **Frosne dataklasser, ikke Pydantic, i porten.** Arkitekturen sier Pydantic. Spesifikasjonen ba om å følge presedensen fra `utelukkelse.py` (story 2.5), og avviket føres her. Pydantic-modellene ligger i `adaptere/api`. Avviket er ført som AV-18 i beslutningsreferatet ved gjennomgangen av PR #29 (2026-11-16), og bekreftes av gruppa ved godkjenning av PR-en.
- **Kategorinøklene** `onsker_flere`, `positiv_ved_behov`, `noytral`, `foretrekker_a_slippe` og `vil_unnga` er hentet fra modelltestene (`scripts/modelltest_prd_fasit.json`). Story 5.1 fastsetter den endelige kontrakten.
- **Rekkefølgen for tolkestatus:** uten tekst (None, tom eller bare mellomrom) blir det alltid «ingen registrert», også om en gammel tolkning finnes. Ellers gir en lagret tolkning `tolket`, og den går foran `feilede`. En kategori som ikke finnes i `PREFERANSEPOENG`, gir `kunne_ikke_tolkes` (P-05: en ugyldig kategori følger feilflyten).
- **Vektene må være `Fraction` eller heltall, være ikke-negative og summere til 1.** `Fraction(0.4)` er ikke 2/5, og da blir summene ikke eksakte. Taket valideres som i `beregn_ulempebelastning`.
- **Timer i min–maks** regnes fra `timedelta` i hele mikrosekunder, ikke fra prosenten som `float`. Det er eksakt og gir samme rekkefølge.
- **Totalscore vises** i `meta` under plassnummeret med én desimal («79,4 poeng»), og preferansepoengene under taggen («50,0 poeng», etter gjennomgangen, se under). Spesifikasjonen sier at visningen avrunder til én desimal, men nevner ikke hvor. Avrundingen bruker den eksisterende `Intl.NumberFormat` fra ulempecellen (K-03: følg eksisterende kontrakt).
- **Ulempecellen** viser «182 p» uten forstavelsen «Ulempebelastning:», fordi kolonneoverskriften er «Ulempe». `Kostnadsvisning` er brukt uendret, med «Kostnad:» foran, fordi godkjenningsflaten bruker den samme komponenten.
- **«Vis alle»** flytter fokus til den første nye raden. Valget nullstilles ved ny lasting, fordi tabellen monteres på nytt. Den første leveransen var enveis. Etter gjennomgangen ba Johannes om at listen også skal kunne lukkes igjen (se under).

## Hva som ble rettet underveis

- Første testkjøring etter API-endringen feilet i to API-tester som forventet den gamle feltlisten og alfabetisk rekkefølge, og i `test_gyldig_kandidat_gir_vakt_og_kandidat`, som krevde at godkjenningsgrunnlaget var likt listeraden. Testene er oppdatert: listeraden har nå flere felt, og godkjenningsgrunnlaget sammenlignes med de felles feltene.
- To domenetester hadde feil håndregnet forventning da de ble skrevet: standardvektene i vekttesten (nr. 2 er øverst med 67,5, ikke nr. 1) og en kommentar om min–maks over bare fem kandidater (75, ikke 80). Begge ble rettet før første kjøring. Fasiten for #4127 ble ikke endret.
- To komponenttester feilet etter tabellbyttet: belastningstesten har seks kandidater, og den sjette vises først etter «Vis alle». Rekkefølgen på varselmerkene er nå overtid før høy belastning, fordi kostnadskolonnen står foran timebelastningen. Testene er tilpasset dette, og selve kontrollene er de samme.

### Rettet etter uavhengig gjennomgang

Gjennomgangen er ført i Review Triage Log i [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-4-rangering-av-gyldige-kandidater.md). Disse funnene ble rettet:

- **Likhetsvedtaket sto bare i spesifikasjonen.** Det har nå en egen oppføring i referatet §11. Den gamle merknaden «ikke vedtatt» står urørt som historikk. `epic-4-context.md` sier at vedtaket er tatt, med henvisning til §11.
- **Portfeltene var bare kontrollert for Ingrid.** Ny domenetest sammenligner kostnad, fordeling, kostnadstype, timebelastning og ulempetimer for alle fire på #4127 med `beregn_kostnad`, `timebelastning(timer_i_startuka(...))` og `ulempe_per_kandidat`. Den kontrollerer også at Jonas er `ordinær` uten overtid.
- **Ingen test viste at API-svaret og porten stemmer overens.** `rangert_ut` regner `KandidatUt`-feltene for seg. Ny API-test kontrollerer at svaret for #4127 har de samme verdiene som `ranger(...)` fra samme database, og at `faktorpoeng.ulempe` er lik `ulempebelastning.score` med standardtaket.
- **`ulempeOverskrift` i `tekster.ts`** var ikke lenger i bruk og er slettet.
- **«p» betydde motsatte ting i to kolonner ved siden av hverandre:** mer er verre for ulempe og bedre for preferanse. Preferansen viser nå «50,0 poeng».
- **Docstringen til `RangertKandidat` hadde forholdet mellom `float` og `Fraction` feil vei.** Nå står det at sorteringen bruker eksakte brøker, at like `float` kan være ulike brøker (men ikke omvendt), og at rekkefølgen skal leses fra `plass`.

### Endret etter ønske fra Johannes

Johannes ba 2026-11-15 om at «Vis alle gyldige kandidater» også skal kunne lukkes. Endringen er gjort direkte av koordinatoren (Claude Opus 5.5), ikke av underagenten:

- Det er fortsatt én knapp. Når listen er åpen, står det «Vis bare de 5 øverste» på den, og «Viser alle N gyldige kandidater.» over. Knappen har `aria-expanded`, som knappen i Ekskludert-boksen.
- Lukkes listen, blir fokus stående på knappen, fordi det er det samme elementet. Radene som forsvinner, tar ikke fokus med seg. Åpnes listen igjen, flyttes fokus til den første nye raden som før.
- Ny komponenttest: `«Vis bare de 5 øverste» lukker listen igjen, med fokus på knappen`. Den sjekker rader, tekst, `aria-expanded` og fokus i begge retninger. Den feilet da knappen ble gjort enveis igjen (`setVisAlle(true)`), og bestod etter tilbakeføring.

## Kvalitetssikring

- **Fasiten er regnet for hånd (KS-02).** Brøkene står i testene: med tolkede preferanser 75/75/0/100 er totalene 7195/84 ≈ 85,65, 6607/84 ≈ 78,65, 59 og 37, og med 50 for alle 3335/42 ≈ 79,40, 3041/42 ≈ 72,40, 71,5 og 24,5. Programmets verdier sammenlignes med `float(Fraction(...))` og med `testdata.FASIT` (avvik under 1e-12). Jonas mot Mette gir nøyaktig 7,0 (AV-12), og Thomas er billigst, men havner som nr. 3 (FR9, SM-6).
- **Likhet (§11, vedtatt av Johannes 2026-11-15)** er testet på to måter. Eksempelet `[0, 0, 0, 300/7]` mot `[0, 100/7, 200/7, 100/7]` gir begge 75/7 som `Fraction`. I et rangert scenario har to kandidater med ulike faktorer (0 og 300/7 mot 100/7 og 100/7) eksakt lik total, og de sorteres etter ID. Testen kontrollerer også at vanlige flyttall ville satt dem i motsatt rekkefølge.
- **Mutasjoner som gjorde testene røde:**
  - Sortering på flyttallssum i stedet for `Fraction`: `test_lik_total_med_ulike_faktorer_sorteres_etter_id` feilet.
  - Fokusflyttingen etter «Vis alle» fjernet: begge Vis alle-testene feilet på `document.activeElement`.
  - `synligeKandidater` ga alltid alle: «viser de fem øverste …» feilet.
  - `row-alt` på feil rader: kolonnetesten og Vis alle-testen feilet.

  Etter tilbakeføring bestod alle.
- **Testkjøringer før gjennomgangen:** 560 backendtester (inkludert arkitekturtesten), `npm run build`, 52 Node-tester og 36 komponenttester bestod. Frontendtestene ble kjørt én om gangen. Etter rettingene bestod de berørte testfilene: `test_rangering.py` og `test_kandidater.py` (103 tester), `kandidatflate.test.tsx` (20) og `kandidater.test.mjs` (21). Den fulle kjøringen etter rettingene ga 562 backendtester, `npm run build`, 52 Node-tester og 36 komponenttester, alle bestått. Etter at listen kan lukkes, består bygget og 52 Node-tester og 37 komponenttester.
- **Ekte backend:** uvicorn ble startet mot en egen database i scratch-mappen, og testdata ble lagt inn. For #4127 ga `GET /api/vakter/4127/kandidater` rekkefølgen Jonas 79,4, Mette 72,4, Thomas 71,5 og Ingrid 24,5, alle med `venter_paa_tolkning`. #4189 ga fortsatt `ingen_gyldige_kandidater`, og godkjenningsgrunnlaget for Jonas var uten Rangeringens felt.
- **Nettleserkontroll, 2026-11-15:** kjørt av koordinatoren med Playwright og headless Chrome mot ekte backend og en midlertidig testdatabase. Skript og resultat står i [`2026-11-15-rangering/`](2026-11-15-rangering/). Skjermbildene ble gjennomgått, men er ikke committet. Alle kontroller bestod etter to rettinger:
  - Siden var 1087 px bred ved 1080, 960 og 680 px. Årsaken var at den skjulte kolonneoverskriften «Valg» (`.visuelt-skjult`, `position: absolute`) slapp ut av `.tabellbeholder`. Rettet med `position: relative` på beholderen.
  - Velg-kolonnen ble klippet ved 1600 px. Tabellen var 1104 px mot 1088 px innholdsbredde, fordi `.tabell td` har `nowrap`. Rettet ved at preferansecellen kan brytes.

  Komponenttestene kan ikke se noen av disse feilene, fordi jsdom ikke regner ut layout. Det er derfor gruppa har manuell kontroll for layout (OP-16). Større skrift og en faktisk skjermleser er ikke kontrollert. Tre agenter som ikke hadde sett implementeringen, gikk gjennom koden (OP-04), se over. Menneskelig PR-gjennomgang gjenstår.
