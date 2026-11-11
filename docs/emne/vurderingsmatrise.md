# Vurderingsmatrise – IBE160 del 1

Arbeidsdokument for gruppen, opprettet 2026-10-12. Tiltakene er vår anvendelse av [sensorveiledningen](sensorveiledning-del-1.md), ikke nye emnekrav. Vektene er veiledende innenfor del 1, som teller 70 % av samlet karakter. Matrisen gir ingen karaktergaranti.

Oppdatert 2026-11-10 med dokumentmilepælen for P-01–P-13/E-01/E-02. Lenke til faktiske bevis må legges inn før et tiltak merkes ferdig. Appskjelett, lagring med fiktive testdata og innlogging er implementert og merget. Kjerneflyten med regelmotor, rangering, KI-forklaringer og godkjenning gjenstår. Dette er ikke en full revisjon av repo eller historikk. Godkjent proposal er identifisert som `ee6d798` (E-02); sluttkontroll mot levert app gjenstår.

| Kriterium | Vekt | Forventet leveranse i turnusprosjektet | Bevis / grunnlag nå | Gjenstår / neste tiltak |
|---|---:|---|---|---|
| Prosess og KI-styring | 30 % | Sporbar sammenheng mellom krav, stories, endringer, prompts, kvalitetssikring og begrunnede beslutninger. | [Produktbrief](../../product-brief.md), [epics](../../_bmad-output/planning-artifacts/epics.md), [modelltestens KI-logg](../ki-logg/2026-10-15-modelltest-haiku.md) med ordrette prompts, rettet testkode og fire kategoriavvik. [Beslutningstest Haiku mot Luna](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md): testsett, fasit og beslutningsregel committet før kjøring (`d45f54d`). [Robusthetstest](../ki-logg/2026-10-16-robusthet-luna.md): iterasjon 1 strøk, og kriteriene for iterasjon 2 ble satt før kjøring. Modellvalget er ført inn i PRD, arkitektur (AD-7) og epics. | Gruppen gjennomgår agentens logger. Koble implementerte stories til PR-er og tester; modelltesten fullfører ingen story. |
| Funksjonalitet og omfang | 20 % | Komplett flyt fra valgt vakt til filtrerte og rangerte kandidater, forklaring og menneskelig valg. | [Omfang og suksesskriterier](../../product-brief.md). | Kontroller mot godkjent proposal. Implementer og demonstrer kjerneflyten, feil input og gjentatte handlinger før stretch goals. |
| Kvalitetssikring og testing | 15 % | Meningsfulle tester av harde regler, kostnad og sentrale integrasjoner, samt dokumentert gjennomgang. | [Modelltest](../ki-logg/2026-10-15-modelltest-haiku.md): 32 live svar, 20/24 riktige preferansekategorier, 8/8 faktatro forklaringer og 10/10 lokale tester av måleverktøyet. To agenter leste alle svar. [Beslutningstest](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md): 1 020 live svar, 37/37 lokale tester av verktøyet, 99 manuelt kontrollerte flagg. [Robusthet og PRD-fasit](../ki-logg/2026-10-16-robusthet-luna.md): 218/218 kall levert med takt-politikk, 75/75 riktige på de 15 fasittekstene, 63/63 lokale tester. | Bygg AD-7 (takt og nye forsøk) i KI-adapteren med tester mot en falsk OpenRouter. Test harde regler og lekkasje-invarianten når appen bygges; de er ikke dekket av modellforsøket. |
| Design og brukeropplevelse | 10 % | Forståelig kandidatoversikt, begrunnelser og tilbakemeldinger til turnusansvarlig. | [DESIGN](../../_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md) og [EXPERIENCE](../../_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md) beskriver UX-valgene. | Implementer og verifiser tomtilstander, feilmeldinger, kontrast, tastaturbruk og skjermstørrelser. Rett språkfeil og oppdiktet kjønn i modellens preferansebegrunnelser før visning. |
| Kodekvalitet og arkitektur | 10 % | Tydelig skille mellom regelmotor, rangering, KI-forklaringer og brukergrensesnitt. | [Arkitektur](../../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md): React/TypeScript/Vite, Python/FastAPI, SQLite/SQLAlchemy og OpenRouter. Appskjelett, lagring og innlogging finnes i `backend/` og `frontend/` (story 1.1–1.3, se bevis nedenfor). Regelmotor, rangering og KI-adapter gjenstår. | Implementer og kontroller at koden følger dokumentasjonen. Testverktøyets HTTP-klient er ikke et valg av appens klientbibliotek. |
| README og kjørbarhet | 10 % | Verifiserte kommandoer, versjoner, konfigurasjon, testdata og testinstruksjoner. | [README](../../README.md) lenker til [verifisert modelltestkommando](../modelltest-openrouter.md); [.env.example](../../.env.example) dokumenterer variablene uten verdier. | Installasjon, oppstart og tester for appen er dokumentert i README og kontrollert som beskrevet under story 1.1–1.3. Kontroll fra ren klone gjenstår (OP-05). |
| Ryddighet i repoet | 5 % | Tydelig skille mellom kode, dokumentasjon og ressurser; ingen hemmeligheter eller byggeartefakter. | [Gitignore](../../.gitignore), [original sensorveiledning](sensorveiledning-del-1.pdf), [agentinstruksjoner](../../AGENTS.md). | Kontroller sporede filer og historikk ved milepæler. Bekreft at nye dokumenter følger gruppens utsjekking. |

## Dokumentgjennomgang 2026-10-26

Planleggingsmilepæl 2026-11-08: [Story 1.4-spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-4-beskyttede-flater-og-utlopt-sesjon.md) kobler FR13/NFR6 til planlagt API-vern, URL-vern, utlogging og kontrollscenarier. Epic-kontekst og kode/UX ble undersøkt av separate underagenter (OP-04). Dette er planleggingsbevis for kriterium 1; implementering, testresultater og kodegjennomgang foreligger ikke ennå.

Implementeringsmilepæl 2026-11-08: API-vern, utlogging og URL-/sesjonskontroll er implementert etter [Story 1.4-spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-4-beskyttede-flater-og-utlopt-sesjon.md), med [KI-logg](../ki-logg/2026-11-08-beskyttede-flater.md), 127 beståtte backendtester og 3 frontendtester. Bygget bestod. Tre uavhengige reviewlag fant løpssituasjoner som ble rettet. [Playwright-kontrollen](../ki-logg/2026-11-08-beskyttede-flater.md#nettleserkontroll-med-playwright-mcp-2026-11-08) verifiserte alle fem akseptansekriterier, tastatur og 360/1600 px, samt to forsinkede svar. Ingen funksjonsfeil ble funnet. Storyen står fortsatt `in-review` til PR-gjennomgangen er fullført; den er ikke `done`.

Implementeringsmilepæl 2026-11-08: Vaktvalg med «Krever handling» er implementert etter [Story 1.5-spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md), med [KI-logg](../ki-logg/2026-11-08-vaktoversikt.md). `GET /api/vaktoversikt` viser bare vakter som starter i perioden (AV-03, FR14). Backendtestene og frontendtestene bestod, og bygget bestod. Etter den uavhengige kodegjennomgangen er det 12 API-tester for vaktoversikten og 12 frontendtester for formateringen, med sommertid, ISO-uker og en ny kjøring i en annen tidssone enn Oslo. En [nettleserkontroll i headless Chrome](../ki-logg/2026-11-08-vaktoversikt/README.md), med skript og skjermbilder, bekreftet tekstene fra spesifikasjonen, tastatur, 360/1600 px og 20 px skrift (kriterium 2, 3 og 4). En ny gjennomgang bekreftet 139 backendtester, 15 frontendtester og frontendbygg. [PR #10](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/10) ble godkjent av Kimsk81 og merget 2026-11-08 (`b16443e`). Storyen er `done`. Tomtilstand og feiltilstand er fortsatt ikke kontrollert i nettleser og står i `deferred-work.md`.

Implementeringsmilepæl 2026-11-09: [Story 1.6-spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-6-velge-vakten-som-skal-bemannes.md) er implementert med [KI-logg](../ki-logg/2026-11-09-vaktdetaljer.md). Beskyttet `GET /api/vakter/{vaktnummer}` avgrenser til ubemannet vakt i brukerens turnus og halvåpne periode (AV-03). Kandidatflaten viser tidspunkt og minstenivå på egen URL, med plassholder fram til Epic 2. API- og rutetester, 150 backendtester, 17 frontendtester og frontendbygg bestod. En [nettleserkontroll](../ki-logg/2026-11-09-vaktdetaljer-nettleserkontroll.md) med simulerte API-svar viste direkte URL, tilbakeknapp, 404, 401, feil/retry og ingen vannrett siderulling eller klippet tekst ved 360/1600 px og 20 px standardskrift. Mot en midlertidig seedet database virket innlogging som `kari.vestby`, Vaktvalg, valg av #4127 og tilbakeknappen; 401 fra selve detaljoppslaget sendte brukeren til `/logg-inn` uten vaktdetaljer. Dette er kode-, test-, integrasjons- og UX-bevis for kriterium 1–5. PR #11 ble godkjent av forfatteren selv, så den menneskelige gjennomgangen skjedde etter merge 2026-11-10: Mithad kjørte testene og prøvde kanttilfeller i API-et ([kommentar på PR #11](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/11#issuecomment-6775679971)), og Johannes gikk gjennom diffen og testet appen selv i nettleseren ([sesjonslogg](../../.logs/johagartnerhimolde/991-2026-11-10-19-25-22-gjennomgang-pr-11.md)). Begge godkjente. Ett lite funn er vurdert og godtatt uten retting: et vaktnummer over 2⁶³−1 gir 500 i stedet for 404 fra API-et, men frontend kan ikke sende slike tall, og svaret er i felles feilform. Storyen er `done`.

[Review av produktbriefen](../../_bmad-output/planning-artifacts/reviews/product-brief-2026-10-26.md) dokumenterer fire review-linser, kontroll mot PRD/arkitektur, ti innholdsfunn og redaksjonelle forslag. [Kildeundersøkelsen](../../_bmad-output/planning-artifacts/research/domain-turnushjelperen-produktbrief-2026-10-26/research.md) følger opp regler, eksisterende verktøy og rangering/brukerforståelse med 18 refererte kilder, kildekontroll og et etterprøvbart regneeksempel. Dette er prosess- og kvalitetssikringsbevis for kriterium 1 og 3, og peker på manglende forståelsestest under kriterium 4. Forslagene er ikke gjennomført; undersøkelsen gir ikke bevis for implementert funksjonalitet, validert brukernytte eller full juridisk etterlevelse. [KI-loggen](../ki-logg/2026-10-26-productbrief-review-research.md) beskriver prompt, leveranse, presiseringer og kontroll.

## PRD samordnet med vedtak 2026-11-07

**Status ved milepælen 2026-11-07:** [PRD-en](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md) ble da oppdatert med AV-04/05/06 og K-03 fra [beslutningsreferatet](../beslutninger/avklaringspunkter.md), og FR-12 ble samordnet med story 3.2 og AD-5. [Kildeavstemmingen](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/reconcile-vedtak-2026-11-07.md), [godkjenningskravene](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/reconcile-godkjenning-2026-11-07.md), [rubrikkgjennomgangen](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/review-rubric-2026-11-07.md) og [den redaksjonelle gjennomgangen](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/review-editorial-2026-11-07.md) er historiske prosessbevis. Åpne spørsmål som disse rapportene fant, ble senere behandlet i P-01–P-13; se ny milepæl nedenfor. Rapportene dokumenterer ikke implementert regelmotor eller godkjenningsflyt.

## Story 1.1 implementert og merget (PR #3)

[KI-loggen for prosjektoppsettet](../ki-logg/2026-10-19-prosjektoppsett.md) dokumenterer appskjelettet, prompten og rettingen fra `httpx` til `httpx2` etter en advarsel fra Starlette. PR #3 ble merget etter selvgjennomgang 2026-10-19 (`af8d289`).

- **Kriterium 1 og 5:** Backendens pakkeinndeling og frontendens Vite-oppsett er dokumentert i KI-loggen og følger arkitekturen.
- **Kriterium 3 og 6:** På Windows ble installasjon i et nytt Python-miljø, helsesjekktesten (1 bestått), frontendens typesjekk/bygg og oppstart av begge serverne kontrollert 19.10. Dette er historiske resultater for story 1.1. [Sprintstatus](../../_bmad-output/implementation-artifacts/sprint-status.yaml) dokumenterer senere kontroll med Python 3.12.5 i en ny venv 04.11 etter story 1.2: installasjon og testdata virket, 35 backendtester bestod og 64 skripttester bestod.

Kontroll fra ren klone gjenstår (OP-05). Fysisk macOS/Linux-test er strøket 07.11; kravet om kode som virker på tvers av operativsystem består. Gruppens generelle beslutning om eksakte versjonslåser er fortsatt åpen.

## Story 1.2 implementert 2026-11-03 og merget (PR #5)

[Spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-2-fiktiv-turnus-med-ansatte-og-vakter.md) følger gruppevedtakene AV-02, AV-03, AV-07, AV-09, AV-10 og AV-12 i [avklaringspunktene](../beslutninger/avklaringspunkter.md). Lagringen i `backend/adaptere/lagring/` har tre tabeller og fiktive testdata: 25 ansatte og 506 faste vakter, inkludert historikk fra 24.08. Det finnes også en forhåndsberegnet fasit for #4127 og #4189.

Bevis per kriterium:
- **Kriterium 3:** 34 tester i `backend/tester/lagring/test_testdata.py`, 35 med `test_helse`, og alle består. Testene sjekker:
  - at hver kandidat bryter nøyaktig regelen fasiten oppgir
  - at ingen ansatt bryter de fire reglene i egen turnus
  - Ulempepoeng for ulempescenarioet
  - inputene til rangeringsfasiten
  - at databasen avviser ugyldige rader

  Tre uavhengige gjennomgangsagenter fant 32 funn. Alle er vurdert i spesifikasjonens Review Triage Log: 12 er rettet og 14 avvist med begrunnelse.
- **Kriterium 1:** [KI-loggen](../ki-logg/2026-11-03-testdata.md) har prompten, leveransen, rettelsene og kladdeskriptene som dataene ble laget med.
- **Kriterium 6:** testdatakommandoen er dokumentert i README og AGENTS.md.

**Menneskelig gjennomgang og godkjenning 2026-11-04:** Johannes W. Gaertner godkjente PR #5 på vegne av gruppa, inkludert KS-04 (datadekningen for #4127/#4189, med kjent begrensning etter 05.10), KS-02 (rangeringsfasiten for #4127) og OP-04 (agentoppsettet med underagenter). Installasjonen virket, testdatakommandoen ga samme resultat to ganger, og 35 tester bestod. Se [beslutningsreferatet §11](../beslutninger/avklaringspunkter.md#11-oppdateringer-etter-møtet) og [loggen fra gjennomgangen](../../.logs/johagartnerhimolde/998-2026-11-04-09-45-04-status-og-pr-5.md). Den tidligere manglende godkjenningen av agentoppsettet er historisk dokumentert i KI-loggen; den er nå avklart.

Ikke dokumentert ennå:
- test fra en ren klone (OP-05). Fysisk test på macOS/Linux er strøket 2026-11-07, fordi verken sensor eller noen i gruppa har Mac.

## Rutine ved milepæler

1. Sammenhold levert funksjonalitet med godkjent proposal og gjeldende plan.
2. Oppdater radene med lenker til konkrete endringer, testresultater og kvalitetssikring.
3. Noter mangler og neste tiltak; ikke beskriv planlagt arbeid som gjennomført.
4. Kontroller README i rent miljø og dokumenter utfallet.
5. Bruk originalveiledningens nivåbeskrivelser til å finne svakheter; prioriter stabil kjerneflyt og etterprøvbar prosess.

## Story 1.3 implementert og merget 2026-11-07 (PR #7)

[Spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md) besvarer OP-10 og følger AV-13 og AV-14 i [avklaringspunktene](../beslutninger/avklaringspunkter.md). Turnusansvarlig logger inn med brukernavn og passord (FR13). Sesjonen er ett JWT i en `httpOnly`-cookie, og alle feil har formen `{ kode, melding }` (AD-4). Frontend har designtokens, appbar, innloggingsflate og en foreløpig startside.

Bevis per kriterium:
- **Kriterium 3:** 111 tester i `backend/` består, både med og uten `TURNUSHJELPEREN_PASSORD` satt. Av dem er 56 i `tester/api/test_innlogging.py` og 16 i `tester/lagring/test_brukere.py`. Testene dekker hele I/O-matrisen i spesifikasjonen, blant annet:
  - cookieattributtene og levetiden til tokenet
  - at feil brukernavn og feil passord gir samme svar og hashes like mange ganger
  - `alg: none`, HS512, feil nøkkel, utløpt token og slettet bruker
  - at 422-svaret aldri gjentar passordet
  - 404, 405 og 500

  En mutasjonskontroll med fire endringer ga røde tester hver gang. Tre uavhengige gjennomgangsagenter fant 25 funn. Alle er vurdert i spesifikasjonens Review Triage Log (#12–#36): 13 er rettet, 1 er utsatt og 11 er avvist med begrunnelse.
- **Kriterium 1:** [KI-loggen](../ki-logg/2026-11-06-innlogging.md) har prompten, leveransen, valgene agenten tok, rettelsene etter gjennomgangen og de manuelle testene.
- **Kriterium 4:** manuelle tester i Chrome av innloggingsflaten, feil passord, gjeninnlasting, backend nede, fokusramme, 1600px og 360px, og 20px rotskrift. Testene er gjort av agenten. Johannes har logget inn bare med tastaturet (tab og enter) på et ekte tastatur, og kontrollert skriftstørrelsene Middels, Stor og Veldig stor i Chrome-innstillingene og bredden 360px og 1600px i enhetsverktøylinjen. Alt ga forventet resultat (2026-11-07, KI-loggen).
- **Kriterium 6:** README har nummererte steg for installasjon, testdata med personlig eller tilfeldig passord (PowerShell og bash), backend og frontend. Variablene er dokumentert uten verdier i [.env.example](../../.env.example).
- **Kriterium 7:** passordet lagres bare som scrypt-hash, og JWT-nøkkelen finnes bare i minnet. Ingen hemmeligheter ligger i repoet.

**Menneskelig gjennomgang og godkjenning 2026-11-07:** Kimsk81 gjennomførte `bmad-walkthrough` av story 1.3 ved `ab78ddc`, testet appen og meldte «Ingen feil oppdaget». Deretter bekreftet han uttrykkelig «Jeg godkjenner story 1.3». Under gjennomgangen ga egen kjøring av backendtestene 112 beståtte tester på Python 3.12, og `npm run build` bestod. Innlogging og sesjonsoppslag er også kontrollert gjennom Vite-proxyen. [Sesjonsloggen](../../.logs/kimsk81/991-2026-11-07-21-39-54-gjennomgang-story-1-3.md) dokumenterer omfang, testresultater og godkjenning. Dette er bevis for kriterium 1, 3 og 6. Brukerens testtilbakemelding spesifiserer ikke enkeltscenarioene. Etter uttrykkelig beskjed fra Kimsk81 ble dokumentasjonen pushet, [PR-godkjenningen registrert i GitHub](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/7#pullrequestreview-5814997786), og [PR #7](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/7) merget som `d13b8e8`. Sprintstatusen er `done`.

Ikke dokumentert ennå:
- test fra en ren klone (OP-05). Fysisk test på macOS/Linux er strøket 2026-11-07. Bash-kommandoene i README er kontrollert i Git Bash på Windows.

## Full kontroll av PRD og beslutningsgrunnlag 2026-11-07

**Status ved undersøkelsen 2026-11-07:** [Beslutningsgrunnlaget for gruppen](../beslutninger/prd-beslutningsgrunnlag-2026-11-07.md) dokumenterte kontroll av PRD §§0–9 og FR-1–FR-14 mot vedtak, stories, arkitektur og tidligere funn. To separate agentkontroller ble sammenholdt. P-01–P-13 og E-01/E-02 var da spørsmål/anbefalinger, ikke vedtak eller implementasjonsbevis. De senere gruppesvarene 2026-11-09 og dokumentsamordningen 2026-11-10 er ført nedenfor.

## CI med GitHub Actions 2026-11-08 (PR #6 og PR #9 merget)

Sensorveiledningen nevner ikke CI. Avsnittet viser hvordan CI støtter kriteriene som er der.

- **PR #6, merget (`9939cfa`):** `.github/workflows/skills-speiling.yml` kontrollerer ved hver push at skillene for Codex og Claude Code er like. [KI-loggen](../ki-logg/2026-11-06-skills-speiling.md) viser at testen feilet i tre brudd som ble laget med vilje. Mithad Kuduz godkjente PR-en etter egen kjøring av testen.
- **[PR #9](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/9), merget etter godkjenning av Mithad Kuduz:** `.github/workflows/backend-tester.yml` kjører `pytest` i `backend/` med Python 3.12 og nyeste 3.x på Linux. Den første kjøringen, [42477253888](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42477253888), ga 112 av 112 på både 3.12.16 og 3.15.2. `.github/workflows/frontend-tester.yml` kjører `npm ci`, `npm run build` og `npm run test` med Node 20.19 og nyeste LTS. Kjøringen [42478187812](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42478187812) var grønn på 20.19.6 og 26.13.0. Etter at PR #8 var merget, ble `--if-present` fjernet, og kjøringen [42519516996](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42519516996) ga 15 av 15 frontendtester på begge versjonene. Samme dag ble laveste Node-versjon løftet fra 20.19 til 22.12, fordi Node 20 ikke lenger vedlikeholdes (§11 i [avklaringspunktene](../beslutninger/avklaringspunkter.md)). Se [KI-loggen](../ki-logg/2026-11-08-ci-backend-tester.md).

Bevis per kriterium:
- **Kriterium 3:** Testene kjøres automatisk ved hver push, ikke bare når noen husker det. CI erstatter ikke sensors egen kjøring etter README.
- **Kriterium 1:** CI-resultatet vises i hver PR, ved siden av gjennomgangen. Prosessen fram til CI-oppsettet er dokumentert i KI-loggen: forslaget kom i en PR-gjennomgang, ble vurdert med pre-mortem, red team og feilmodusanalyse, og Johannes rettet agentens forslag om en ren 3.12-lås. Agenten fant selv at `latest` ga en alfaversjon av Node, og rettet det til `lts/*`.
- **Kriterium 5:** CI kontrollerer at de eksakt låste avhengighetene installeres fra en ren runner, både med laveste og nyeste Python.
- **Kriterium 7:** CI har bare lesetilgang og ingen secrets. Policy i `AGENTS.md` forbyr modellnøkkelen i CI.
- **Kryssplattform:** CI på Linux er den eneste kjøringen utenfor Windows etter OP-05.

Ikke dekket: testene av modellverktøyene i `scripts/` og manuell test. Rød CI blokkerer ikke merge, og det er gruppas valg. README beskriver CI under Tester.
## Dokumentsamordning av PRD-vedtak 2026-11-10

[Beslutningsreferatet §12](../beslutninger/avklaringspunkter.md#12-prd-vedtak-2026-11-09-og-status-ved-dokumentsamordning) fører P-01–P-13 og E-01/E-02 med skille mellom vedtak og gjenstående kontroll. [PRD-en](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md) har beholdt FR-ID-ene og fått testbare konsekvenser for beregning, datamangler, KI-feil/faktakontroll og ny bekreftelse. [Epics](../../_bmad-output/planning-artifacts/epics.md), [arkitektur](../../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md), [UX-reisen](../../_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md), [Story 1.2-spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-2-fiktiv-turnus-med-ansatte-og-vakter.md) og [produktbriefen](../../product-brief.md) er samordnet der tidligere tekst var misvisende. Sprintstatus fører P-10B som story 5.9 i backlog. Dette er bevis for **prosess og planleggingskvalitet** (kriterium 1), ikke for implementert funksjonalitet eller beståtte apptester (kriterium 2/3).

Kontroller som fortsatt trengs for vurderingsgrunnlaget: grensetester av P-01–P-04; P-08-stopp ved #4261–#4265 og andre datamangler; P-05–P-07 mot falsk OpenRouter og manuell forståelighet; P-09-ny bekreftelse; P-11-tomtilstand; P-13s mobil-/nettbrettavklaring og dokumenterte forståelsestest før story 4.6; kontroll av faktisk levert app mot godkjent proposal `ee6d798` (E-02). KS-02s #4127-fasit og KS-04s avgrensede godkjenning av #4127/#4189 står fast. Ingen av disse kontrollene markeres utført av dokumentvedtakene.
