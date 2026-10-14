---
title: "Endringsforslag: KI-leverandør og kjøring uten gruppens nøkkel"
type: sprint-change-proposal
status: approved (2026-10-14)
created: 2026-10-14
branch: ki-leverandor-openrouter-haiku
scope: moderat
---

# Endringsforslag: KI-leverandør og kjøring uten gruppens nøkkel

## 1. Hva som utløser endringen

To forhold utløser endringen. Ingen av dem er funnet under implementering, for det finnes ingen applikasjonskode ennå.

1. **Gruppa snur KI-leverandøren.** Arkitektursteget valgte Google Gemini 2026-09-29, fordi Gemini hadde et gratisnivå uten betalingskort. Bare leverandøren ble valgt, ikke modellen. Gruppa velger nå OpenRouter (openrouter.ai) med `anthropic/claude-haiku-5.5` som standardmodell. Begrunnelsen er tredelt:
   - Oppgavene er små: korte norske preferansetekster skal tolkes til JSON, og hver avveining er 2–4 setninger.
   - Prisen er lav. Per 2026-10-14 koster modellen $0.10 per million tokens inn og $0.50 ut. Det gir rundt $0.003 per vakt med 10 kandidater.
   - Modellen støtter strukturert output. Gruppa betaler heller en liten sum enn å være avhengig av gratiskvoter som endrer seg.
2. **Faglærers tilbakemelding på product brief (2026-10-06), punkt 3.** Sensor må kunne kjøre appen uten gruppens nøkkel. Dette har stått som åpent spørsmål 3 i PRD §8. Sensorveiledningen gjør punktet skarpere:
   - Sensor skal få appen til å kjøre bare etter README, uten å spørre gruppa.
   - Nøkler i repoet eller i historikken gir trekk (`docs/emne/sensorveiledning-del-1.md`, kriterium 6 og kriteriet om ryddighet).

**Kjent begrensning:** Haiku 5.5 er ikke målt i noen norsk benchmark. EuroEvals norske leaderboard ble sist oppdatert i april 2026, og forgjengeren Claude Haiku 4.5 fikk rang 1.98 der, som er midt på treet. Norskkvaliteten skal derfor verifiseres i en modelltest før Epic 5 implementeres. Å bytte modell krever bare å endre en miljøvariabel.

**Type endring:** Ny beslutning i gruppa og nytt krav fra en interessent (faglærer og sensorveiledningen).

## 2. Konsekvenser

### Epics og stories

| Epic | Konsekvens |
|---|---|
| Epic 1 | Ingen endring i storiene. `.env.example` i story 1.1 er generisk nok. |
| Epic 2–4 | Ikke berørt. Domenekjernen endres ikke. |
| Epic 5 | Storiene 5.1, 5.3, 5.4 og 5.6 justeres. To nye stories: 5.7 (demo-modus) og 5.8 (sensor kan kjøre live KI). Epicet dekker i tillegg NFR14. |

### Artefakter

| Artefakt | Konsekvens |
|---|---|
| PRD | Nytt NFR i §4.5, SM-9 presiseres, og åpent spørsmål 3 flyttes til løst. MVP-omfanget er uendret. |
| Arkitekturspinen | `adaptere/ki` byttes til OpenRouter med to implementasjoner. Ny AD-6 (KI-modus). AD-4, config-raden, Stack, diagrammer, kildetre og Deferred oppdateres. |
| ARKITEKTUR-FORKLARING.md, ARKITEKTUR-PRESENTASJON.html, `.memlog.md` | Begrunnelsen for leverandøren skrives om, og den snudde beslutningen logges. |
| `reviews/` under arkitekturen | Røres ikke. Mappa er historikk over gjennomgangen 2026-09-29. |
| EXPERIENCE.md | Merking av KI-kilde i appbar og forklaringspanel, en ny tilstand («Demo-modus») og en ny rad i Voice and Tone. DESIGN.md er uendret, fordi bare eksisterende komponenter brukes. |
| `.env.example`, README | Opprettes og fylles ut i story 1.1 og 5.8, ikke i denne endringen. |

### Teknisk

Ingen kode finnes, så ingenting må rulles tilbake. Endringen ligger i adapterlaget og i oppstartslaget til `adaptere/api` (AD-2). Domenekjernen og portene er uendret.

## 3. Anbefalt vei videre

**Direkte justering** innenfor den eksisterende epic-strukturen.

| Alternativ | Vurdering |
|---|---|
| Direkte justering | **Valgt.** Én ny AD, to nye stories og tekstendringer. Innsats: lav. Risiko: lav. |
| Tilbakerulling | Ikke relevant. Ingen kode finnes. |
| Ny vurdering av MVP | Ikke nødvendig. Omfanget er uendret. Demo-modus er et krav til kjørbarhet, ikke en ny funksjon. |

**Risiko:**
- Norskkvaliteten til Haiku 5.5 er ikke dokumentert. *Tiltak:* modelltest før story 5.1, og modellen settes i en miljøvariabel.
- Demo-modus kan skjule feil i live-modus. *Tiltak:* ingen stille overgang til demo-modus (AD-6, PRD §4.5).
- Ferdig genererte forklaringer kan bli utdaterte. *Tiltak:* oppslaget bruker en hash av `RangertKandidat`, og avvik gir maltekst.

## 4. Detaljerte endringer

### 4.1 Arkitektur, `ARCHITECTURE-SPINE.md`

**Design Paradigm-tabellen, raden `adaptere/ki`:** «Gemini-integrasjon.» blir «Språkmodell-integrasjon via OpenRouter (standardmodell `anthropic/claude-haiku-5.5`, satt i miljøvariabel). To implementasjoner bak samme port: `OpenRouterKiAdapter` (live) og `DemoKiAdapter` (forhåndsgenererte svar + mal), se AD-6.» Resten av raden er uendret.

**Ny AD-6: KI-modus velges ved komposisjon, aldri i domenet**
- **Binder:** `adaptere/ki`, oppstartslaget i `adaptere/api`, testdata og README.
- **Forhindrer:**
  - at appen ikke kan kjøres eller vurderes uten gruppens nøkkel (SM-9)
  - at ferdig generert tekst presenteres som live KI
  - at demoveien omgår AD-1
- **Regel:**
  - `KI_MODUS` er `openrouter` eller `demo`. Mangler `OPENROUTER_API_KEY`, starter appen i `demo` og logger det ved oppstart. Den krasjer aldri. Valget skjer bare i oppstartslaget (AD-2).
  - Begge implementasjonene tar imot og returnerer nøyaktig de samme porttypene. Kjøretidstesten i AD-1 kjøres mot begge.
  - **Demo, tolkning:** leser ferdig generert `TolketPreferanse` fra testdataene. Ukjent tekst gir «Ingen registrert».
  - **Demo, forklaring:** slår opp ferdig generert Avveining med nøkkelen (vakt, kandidat, hash av `RangertKandidat`). Finnes den ikke, eller har dataene endret seg, lages en maltekst bare fra feltene i `RangertKandidat`.
  - Ferdig genererte svar lages med den live adapteren og samme prompt. Modell og dato logges i `docs/ki-logg/`.
  - Hver Avveining i API-svaret har feltet `ki_kilde: "live" | "forhandsgenerert" | "mal"`.
  - I `openrouter`-modus faller appen ikke stille tilbake til demo ved feil. Feil gir `avveining_feilet` (AD-4).

**Følgeendringer:**
- AD-4: «Geminis fartsgrense» blir «leverandørens fartsgrense eller tom kreditt (OpenRouter svarer 429 og 402)».
- Config-raden: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (standard `anthropic/claude-haiku-5.5`) og `KI_MODUS`.
- Stack: Gemini-raden erstattes av «OpenRouter API (OpenAI-kompatibelt) med `anthropic/claude-haiku-5.5`. Verifisert 2026-10-14: $0.10/$0.50 per million tokens, `structured_outputs`. Resonnering av. Klientbibliotek ikke valgt.»
- Mermaid-diagrammene og kildetreet: «Gemini» blir «OpenRouter / demo».
- Capability-kartet, raden for §4.5: AD-6 legges til, og «Gemini-nøkkel» blir «OpenRouter-nøkkel».
- Deferred: Gemini-punktet erstattes av to punkter:
  - (a) retry/backoff-policy og klientbibliotek
  - (b) norskkvaliteten til Haiku 5.5 er ikke målt, og modelltest kreves før Epic 5
- `updated: 2026-10-14`.

**Følgefiler:**
- ARKITEKTUR-FORKLARING.md: §4 får ny begrunnelse for leverandøren, og Deferred-punktet i §5 oppdateres.
- ARKITEKTUR-PRESENTASJON.html: Gemini erstattes med OpenRouter/Haiku 5.5.
- `.memlog.md`: en `(decision)`-linje om at Gemini-beslutningen er snudd, og hvorfor.

### 4.2 PRD, `prd.md`

- **§4.5, nytt NFR:** «Kjørbar uten gruppens API-nøkkel:
  - Systemet kan kjøres i en demo-modus uten nøkkel til språkmodellen. Tolkede preferanser og Avveininger kommer da fra modellsvar generert på forhånd og lagret i testdataene, eller fra en mal bygd bare av de beregnede tallene.
  - Grensesnittet viser alltid om en Avveining er live, forhåndsgenerert eller malbasert.
  - En feil i live-modus gir reservetekst (FR-11), ikke stille overgang til demo-modus.»
- **SM-9:** «…, og uten gruppens API-nøkkel (demo-modus, §4.5)» legges til.
- **§8:** Åpent spørsmål 3 flyttes til «Løst (2026-10-14)»:
  - KI-leverandøren er OpenRouter med `anthropic/claude-haiku-5.5` som standardmodell, satt i en miljøvariabel. Dette erstatter Gemini, og AD-6 gjelder.
  - Sensor får en OpenRouter-nøkkel med kreditt, levert i innleveringen og aldri i repoet. Om det blir den felles utviklingsnøkkelen eller en egen sensornøkkel, og hvor mye kreditt den får, avgjøres nær innlevering ut fra faktisk forbruk (epics ÅB-8).
  - Uten nøkkel starter appen i demo-modus.
- `updated: 2026-10-14`.

### 4.3 Epics, endringer i eksisterende tekst (`epics.md`)

- **NFR7:** «API-nøkler (Gemini)» blir «API-nøkler (OpenRouter)».
- **Ny NFR14 (Kjørbar uten gruppens nøkkel):** Appen kan kjøres i demo-modus uten API-nøkkel. Grensesnittet viser alltid om en Avveining er live, forhåndsgenerert eller malbasert. En feil i live-modus gir reservetekst, ikke stille overgang til demo-modus (PRD §4.5, SM-9, AD-6).
- **Tilleggskrav, Arkitekturstruktur:** «`adaptere/ki` (Gemini)» blir «`adaptere/ki` (OpenRouter, eller demo-modus etter AD-6)».
- **Tilleggskrav, KI-integrasjon,** erstattes av:
  - OpenRouter med `anthropic/claude-haiku-5.5` som standardmodell i `OPENROUTER_MODEL`. Strukturert output, resonnering av. Fartsgrense (429) og tom kreditt (402) gir `avveining_feilet`, ikke krasj.
  - AD-6: `KI_MODUS=openrouter|demo`. Uten `OPENROUTER_API_KEY` starter appen i demo-modus. Valget skjer bare i oppstartslaget til `adaptere/api`.
  - Norskkvaliteten til Haiku 5.5 er ikke målt. En modelltest kjøres før story 5.1 implementeres, og resultatet logges i `docs/ki-logg/`.
- **Utsatte beslutninger:** «Gemini-modell og retry/backoff-policy» blir «Retry/backoff-policy og klientbibliotek mot OpenRouter».
- **Ny ÅB-8**, se 4.4.
- **Story 5.1:**
  - «sender teksten til Gemini» blir «sender teksten til språkmodellen via OpenRouter, med JSON-skjema for strukturert output».
  - «at Gemini svarer» blir «at språkmodellen svarer».
  - «API-nøkkelen og modellnavnet for Gemini» blir «`OPENROUTER_API_KEY`, `OPENROUTER_MODEL` og `KI_MODUS`».
- **Story 5.3:** Kriteriet om forklaringspanelet får «And panelet viser kildelinjen «KI-generert · <modellnavn>» (UX-DR27)».
- **Story 5.4:** «at Gemini svarer med feil, tidsavbrudd, fartsgrense, tomt svar» blir «at språkmodellen svarer med feil, tidsavbrudd, fartsgrense (429), tom kreditt (402), tomt svar».
- **Story 5.6, nytt kriterium:** Given begge KI-adapterne (`OpenRouterKiAdapter` med falsk HTTP-klient, og `DemoKiAdapter`) / When kjøretidstesten kjøres / Then invarianten holder for begge (AD-6).
- **Ny UX-DR27,** se 4.5.

### 4.4 Epics, nye stories og ÅB-8 (`epics.md`)

**Epic-listen og introduksjonen til Epic 5:** «Epicet leverer også demo-modus uten nøkkel og oppsettet som lar sensor kjøre live KI (NFR14, AD-6).» FR-dekningen får «+ NFR14».

**ÅB-8:**

| ID | Beslutning | Kilde | Blokkerer | Status |
|---|---|---|---|---|
| ÅB-8 | Hvilken nøkkel sensor bruker for live KI: (1) den felles utviklingsnøkkelen, hvis det som er igjen av kreditt holder, eller (2) en egen sensornøkkel med kredittgrense. Avgjøres nær innlevering, når modellen er valgt etter modelltesten og gruppa kjenner det faktiske forbruket. Velges (1), må utviklingsnøkkelen byttes ut etter sensur, og utviklingsbruken på den stoppes etter innlevering. Forbruket per nøkkel kan leses i OpenRouters aktivitetsoversikt. | Faglærers tilbakemelding pkt. 3, PRD §8 | Bare den delen av story 5.8 som gjelder levering av nøkkel | Åpen, blokkerer ikke |

**Story 5.7: Demo-modus uten API-nøkkel** (bygger på 5.1 og 5.3)

As a sensor eller ny utvikler, I want at appen kan kjøres og vise hele flyten uten API-nøkkel, so that jeg kan vurdere Turnushjelperen uten gruppens tjenester (NFR14, SM-9).

- **Given** at `OPENROUTER_API_KEY` mangler eller `KI_MODUS=demo` / **When** backend starter / **Then** oppstartslaget kobler inn `DemoKiAdapter` og logger at appen kjører i demo-modus, uten krasj (AD-6) / **And** valget skjer bare i oppstartslaget til `adaptere/api` (AD-2)
- **Given** demo-modus / **When** preferanser tolkes / **Then** ferdig genererte `TolketPreferanse`-verdier fra testdataene brukes, og ukjent tekst gir «Ingen registrert»
- **Given** demo-modus og en `RangertKandidat` / **When** Avveiningen hentes / **Then** en ferdig generert Avveining brukes hvis (vakt, kandidat, hash av `RangertKandidat`) finnes i testdataene, med `ki_kilde: "forhandsgenerert"` / **And** ellers lages en maltekst bare fra feltene i `RangertKandidat`, med `ki_kilde: "mal"`
- **Given** de ferdig genererte svarene / **When** de lages / **Then** de genereres med `OpenRouterKiAdapter` og samme prompt som live-modus, via en dokumentert kommando / **And** modell, dato og kommando logges i `docs/ki-logg/` / **And** vakt #4127 dekkes, så demoflyten viser forhåndsgenererte Avveininger fra start til slutt
- **Given** live-modus og en feil fra OpenRouter / **When** Avveiningen hentes / **Then** svaret er `avveining_feilet` (story 5.4), ikke en overgang til demo-modus
- **Given** demo-modus / **When** en flate etter innlogging vises / **Then** appbaren viser «Demo-modus», og hvert forklaringspanel viser kildelinjen sin (UX-DR27)
- **Given** testene / **When** de kjøres / **Then** de dekker valg av modus, oppslag, at en endret hash gir maltekst, og at begge adapterne holder invarianten i story 5.6

**Story 5.8: Sensor kan kjøre live KI** (bygger på 5.7; delen om levering av nøkkel er avhengig av ÅB-8)

As a sensor, I want en nøkkel med kreditt og en README som forklarer hvordan jeg bruker den, so that jeg kan se live KI-forklaringer uten egen konto og uten å spørre gruppa.

- **Given** utviklingsfasen / **When** gruppa bruker live KI / **Then** gruppa bruker én felles utviklingsnøkkel med kredittgrense, og ingen nøkler i repoet
- **Given** at ÅB-8 er avgjort før innlevering / **When** innleveringen forberedes / **Then** sensor får enten utviklingsnøkkelen eller en egen sensornøkkel, med den kreditten gruppa har vurdert som nok / **And** nøkkelen står i innleveringsteksten, aldri i repoet, i git-historikken eller i en committet `.env` / **And** historikken er sjekket for nøkler før innlevering, og sjekken er notert
- **Given** README / **When** sensor følger den / **Then** README forklarer: kopier `.env.example` til `.env`, lim inn nøkkelen fra innleveringen, og start appen / **And** README forklarer at appen uten nøkkel starter i demo-modus, og hvordan man ser hvilken modus som er aktiv / **And** README sier hva sensor ser hvis kreditten er brukt opp: reservetekst, ikke krasj
- **Given** innleveringsfristen / **When** gruppa gjør sluttkontroll / **Then** én person installerer fra en ren klone kun etter README, kjører flyten både med nøkkelen sensor skal få og i demo-modus, og noterer resultatet
- **Given** at sensuren er ferdig / **When** gruppa rydder opp / **Then** nøkkelen sensor fikk, slettes eller byttes ut i OpenRouter, og den ansvarlige personen er navngitt i innleveringen

### 4.5 UX, `EXPERIENCE.md` og `epics.md`

- **Component Patterns, raden Appbar:** I demo-modus viser appbaren en nøytral tag, «Demo-modus», til venstre for innlogget bruker. Taggen er statisk så lenge appen kjører.
- **Component Patterns, raden Forklaringsrad/-panel:** Hvert panel har en kildelinje nederst i `meta`:
  - «KI-generert · <modellnavn>»
  - «Forhåndsgenerert KI-forklaring · <modellnavn>, <dato>»
  - «Satt sammen fra beregnede tall, ikke KI-generert»

  Kildelinjen vises i alle moduser.
- **State Patterns, ny rad «Demo-modus (ingen API-nøkkel)»:** Appbaren viser «Demo-modus». Avveininger vises med kildelinjen «forhåndsgenerert» eller «mal». Det er en normaltilstand, ikke en feil, og vises derfor ikke i `warn` eller `danger` (AD-6, NFR14).
- **Voice and Tone, ny rad:**
  - Gjør: «Satt sammen fra beregnede tall, ikke KI-generert».
  - Unngå: å presentere ferdig generert tekst eller maltekst som om den var live KI-svar.
- `updated: 2026-10-14`.
- **epics.md, UX-DR27 (Merking av KI-kilde):** Hvert forklaringspanel har en kildelinje i `meta` (live, forhåndsgenerert eller mal). I demo-modus viser appbaren en nøytral tag, «Demo-modus». Ingen `warn`- eller `danger`-farge (NFR14, AD-6).

## 5. Overlevering

**Omfang:** Moderat. Planen får nye stories og en ny åpen beslutning, men MVP-omfanget og domenekjernen er uendret.

| Hvem | Ansvar |
|---|---|
| Johan, med Claude Code | Gjennomføre endringene i 4.1–4.5 på branchen `ki-leverandor-openrouter-haiku` og åpne en PR. |
| Gruppa (PR-gjennomgang) | Godkjenne beslutningen om leverandør og modell og de nye storiene 5.7 og 5.8. PR-gjennomgangen er kvalitetssikringen (AGENTS.md). |
| Gruppa, før story 5.1 | Kjøre modelltesten på norsk for Haiku 5.5, med alternativer ved behov. Logge resultatet i `docs/ki-logg/`. Opprette den felles utviklingsnøkkelen med kredittgrense. |
| Gruppa, nær innlevering | Avgjøre ÅB-8 og gjennomføre story 5.8. |

**Suksesskriterier:**
- Ingen dokumenter i `_bmad-output/planning-artifacts/` utenom `reviews/` og `.memlog.md`-historikken nevner Gemini som gjeldende valg.
- PRD §8 har ingen åpent spørsmål om kjøring uten nøkkel.
- AD-6, NFR14, UX-DR27, ÅB-8 og storiene 5.7–5.8 finnes og henviser til hverandre.
- Sprint-planleggingen (`bmad-sprint-planning`) kan kjøres etterpå uten konflikter mellom PRD, arkitektur og epics.

**Neste steg etter fletting:** `bmad-sprint-planning`. Ingen `sprint-status.yaml` finnes ennå, så sjekkpunkt 6.4 er ikke relevant. De nye storiene tas med når sprint-statusen genereres.
