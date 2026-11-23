# Epic 5 Context: KI-forklaring av avveininger

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epicet legger KI oppå den deterministiske kjernen uten at KI noen gang beregner regler, arbeidstid, kostnad eller rangering. Preferansetekstene til de ansatte tolkes én gang og lagres. Rangeringen leser bare lagrede tolkninger. Hver rangert kandidat får en faktakontrollert Avveining, og ved feil vises en tydelig merket reservetekst. En kjøretidstest beviser at utelukkede kandidater aldri når KI-laget. Appen kan kjøres i demo-modus uten nøkkel, og sensor skal kunne kjøre live KI med en nøkkel fra innleveringen. Story 5.1–5.7 er ferdige. Story 5.8 (sensor og live KI) er under arbeid, og 5.9 ligger i backlog.

## Stories

- Story 5.1: Tolke tekstbaserte ansattpreferanser med KI
- Story 5.2: Rangeringen bruker tolkede preferanser
- Story 5.3: Avveining per kandidat
- Story 5.4: Reservetekst når KI-forklaringen feiler
- Story 5.5: Rader vises før forklaringene er ferdige
- Story 5.6: Test av at utelukkede kandidater aldri når KI-laget
- Story 5.7: Demo-modus uten API-nøkkel
- Story 5.8: Sensor kan kjøre live KI
- Story 5.9: Redigere preferansetekst etter fungerende kjerneflyt (P-10B)

## Requirements & Constraints

- KI-grensen: KI tolker bare preferansetekst og forklarer kandidater som allerede er godkjent av regelmotoren. Harde regler, timer, kostnad, ulempe og rangering er deterministiske og uten KI.
- Lekkasjeinvariant: en utelukket kandidat skal aldri finnes i rangeringen, i API-svaret eller i input/output til forklaringsporten. Det gjelder begge KI-adapterne.
- Robusthet: feil, tidsavbrudd, 429, 402, tomt svar, ubrukelig svar eller svar som stryker i faktakontrollen gir reservetekst, aldri krasj og aldri en anbefaling uten grunnlag. Rangering og godkjenning virker fortsatt. Korrekthet går foran hastighet.
- Tolkning uten gyldig lagret verdi gir midlertidig 50 poeng med egen status («venter på tolkning» eller «kunne ikke tolkes»). Det er noe annet enn «Ingen registrert» (P-05).
- Kjørbar uten gruppens nøkkel: uten `OPENROUTER_API_KEY` starter appen i demo-modus. I live-modus fører en feil til reservetekst, ikke en stille overgang til demo-modus.
- Hemmeligheter: nøkler leses bare fra miljøvariabler og ligger aldri i kildekode, i git-historikken eller i en committet `.env`. Nye variabler dokumenteres uten verdi i `.env.example`. CI får aldri nøkkelen, og tester bruker falsk OpenRouter uten nettverk.
- **Sensor og live KI (5.8):** Sensor setter nøkkelen fra innleveringen som `OPENROUTER_API_KEY` i terminalen (PowerShell og bash) og starter backend i samme terminal. Backend leser ikke `.env`, så en nøkkel lagt der brukes ikke. Appen starter da i demo-modus uten feilmelding (AV-20, vedtatt 2026-11-23). README må si dette, forklare at appbaren viser «Demo-modus» når appen ikke kjører live (sensor kontrollerer at taggen mangler), og si at oppbrukt kreditt gir reservetekst, ikke krasj.
- **ÅB-8 er åpen:** Om sensor får den felles utviklingsnøkkelen eller en egen sensornøkkel med kredittgrense, avgjøres nær innlevering ut fra faktisk forbruk. Hele gruppa er beslutningseier. Det blokkerer bare nøkkelleveransen i 5.8, ikke README eller demo-modus. Nøkkelen står bare i innleveringsteksten. Historikken sjekkes for nøkler før innlevering, og sjekken noteres. Før fristen installerer én person fra en ren klone bare etter README og kjører flyten både med sensornøkkelen og i demo-modus. Etter sensur slettes eller byttes nøkkelen, og den ansvarlige navngis.

## Technical Decisions

- Heksagonal arkitektur: `adaptere/ki` har to ensrettede roller (tolk og forklar), og begge orkestreres av `adaptere/api`. Domenekjernen kaller aldri KI. En import-linter-kontrakt pluss en kjøretidstest håndhever grensen (AD-1, AD-2).
- Porttypene `TolketPreferanse` og `RangertKandidat` er frosne dataklasser i `domene/porter` (AV-18). Validering skjer i `adaptere/ki` ved svar og i `adaptere/lagring` ved lesing.
- KI-modus (AD-6): `KI_MODUS=openrouter|demo` velges bare i oppstartslaget. `OpenRouterKiAdapter` og `DemoKiAdapter` bruker de samme porttypene. Hver gyldig Avveining har `ki_kilde: "live" | "forhandsgenerert" | "mal"`. Feil gir `status: "avveining_feilet"` som et 200-svar (AD-4).
- Takt (AD-7): modellen er `openai/gpt-6-luna`, bundet til leverandøren `openai` uten fallback. Én felles begrenser tillater høyst 18 kall per 60 s og 5 samtidige. Ved 429 ventes det til `X-RateLimit-Reset`. Avveining prøver på nytt etter 2/4/8 s ved 5xx og nettverksfeil og har 90 s budsjett fra første live-kall. 402, andre 4xx og ubrukelige svar prøves ikke på nytt.
- Tolkningens feilregler (AV-19): tre nye forsøk etter 2/4/8 s og 90 s per tekst. Sluttstatusen er `kunne_ikke_tolkes` med feiltype. «Prøv igjen» er levert (PR #33).
- Faktakontroll (P-06/P-07): KI returnerer strukturerte påstander fra et avgrenset sett. Koden kontrollerer fakta og retning mot uavrundede verdier og setter inn navn og tall. Referansen er nr. 2 for nr. 1 og nr. 1 for de øvrige. Ved bare én kandidat brukes ingen referanse. Demo-svar kontrolleres på samme måte.
- Grunnlagsmerke (P-09): hver Avveining er bundet til merket for rangeringen den ble laget fra. Svar med et annet merke forkastes. Lagrede tolkninger ligger som kolonner på `ansatt` og inngår i grunnlagsmerket. En ny tolkning gir `endret_grunnlag`.
- Avveiningen lagres ikke historisk ved godkjenning (P-12).
- Progressiv lasting: hver åpnet rad henter sin egen Avveining med `GET /api/vakter/{vakt}/kandidater/{id}/avveining`. Lukkede rader hentes ikke.

## UX & Interaction Patterns

- Forklaringspanelet: den topprangerte kandidatens panel er åpent, og de andre er lukket bak «Vis begrunnelse ▾» / «Skjul begrunnelse ▴». Radene åpnes uavhengig av hverandre. «▲ Trekker opp» vises i `ok` og «▼ Trekker ned» i `danger`. Lenkene kan brukes med tastaturet.
- Kildelinjen i `meta` står på hvert panel i alle moduser: «KI-generert · <modell>», «Forhåndsgenerert KI-forklaring · <modell>, <dato>», «Satt sammen fra beregnede tall, ikke KI-generert» eller «Reservetekst · KI-forklaring utilgjengelig».
- I demo-modus viser appbaren en nøytral tag, «Demo-modus», uten `warn`- eller `danger`-farge, fordi dette er en normaltilstand. Dette er signalet sensor bruker for å se om live KI er aktiv.
- Lastetilstanden for en Avveining skal være ulik både reserveteksten og tomtilstanden. Nøkkeltallene vises også når panelet har reservetekst.
- All brukertekst ligger i `src/tekster.ts` og slås opp på `kode`/`status`. Teksten er kort og nøktern.

## Cross-Story Dependencies

- 5.3–5.6 bygger på `RangertKandidat` fra Epic 4 (story 4.4 og 4.7). 5.4 og 5.5 bygger på 5.3.
- 5.7 bygger på 5.1 og 5.3. De forhåndsgenererte svarene må lages med samme prompt etter 4.7, ellers gir hashen maltekst.
- 5.8 bygger på 5.7 (ferdig). README-delen følger AV-20. Nøkkelleveransen venter på ÅB-8.
- 5.9 kommer etter fungerende kjerneflyt. Ny tekst gir ny tolkning, ugyldiggjør gammel tolkning og forklaring og krever ny bekreftelse (P-09).
