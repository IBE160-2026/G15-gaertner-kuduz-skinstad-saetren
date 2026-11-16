# Epic 5 Context: KI-forklaring av avveininger

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epicet legger KI-laget rundt den deterministiske regelmotoren. Preferansetekstene til de ansatte tolkes én gang til en fast kategori, lagres og brukes som input til Rangeringen. Hver rangert Kandidat får en Avveining i klartekst. Avveiningen er bygd av strukturerte, faktakontrollerte påstander og får tydelig merket reservetekst når modellen feiler. Epicet leverer også en kjøretidstest som beviser at utelukkede kandidater aldri når forklaringslaget, demo-modus uten API-nøkkel og oppsettet som lar sensor kjøre live KI. Målet er at turnusansvarlig forstår og kan stå inne for rangeringen uten at KI noen gang beregner eller overstyrer den.

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

- **KI tolker og forklarer, men beregner aldri.** KI beregner aldri Harde regler, arbeidstid, kostnad, Timebelastning, Ulempebelastning eller Rangering, og kan ikke overstyre dem. Koden tildeler kategoripoengene.
- **Preferansekategorier og poeng:** 100 = ønsker aktivt flere vakter, 75 = positiv ved behov, 50 = nøytral, 25 = foretrekker å slippe, men er åpen, 0 = vil unngå ekstravakter. Alle de 15 definerte fasittekstene skal tolkes til forventet kategori (SM-7). Tekst uten holdning til flere vakter, for eksempel bare ønsker om tidspunkt, er nøytral.
- **Preferansestatusene holdes atskilt (P-05/OP-03):** manglende tekst gir 50 poeng og «Ingen registrert». Tekst som venter på tolkning gir midlertidig 50 poeng og «Preferanse venter på tolkning». Feilet eller ugyldig tolkning gir midlertidig 50 poeng og «Preferanse kunne ikke tolkes». En reell nøytral tolkning er en egen status. Råteksten beholdes, ingen nøytral tolkning diktes opp, og en KI-feil utelukker aldri Kandidaten. Forbigående feil gir avgrensede automatiske forsøk. Etter endelig feil kan brukeren be om nytt forsøk. En ny vellykket tolkning oppdaterer rangeringen før bekreftelse.
- **Åpent før story 5.1:** ventetrinn ved 5xx og nettverksfeil, antall forsøk, tidsbudsjett med startpunkt og sluttstatus ved 429/5xx/nettverksfeil er ikke avklart for preferansetolkning. Avveiningens 2/4/8 s, 90 s og `avveining_feilet` gjelder ikke automatisk for tolkningen. Avklaringen må gjøres før story 5.1 og 5.2 kan bli `done`.
- **Avveiningens innhold (FR-11):** hvorfor Kandidaten kan ta Vakten, hva som trekker opp og ned, kostnadsvurdering og relevante preferanser. KI leverer bare påstandstype og referanse, aldri egne tall eller navn. Tillatte påstander: oppfyller de fire prototypereglene, en navngitt faktor trekker opp eller ned, eller en faktor eller totalscore er høyere, lavere eller lik referansens. «Lik» krever lik uavrundet verdi.
- **Faktakontroll (P-06):** koden validerer kandidat- og faktareferanser og sammenligningsretning mot uavrundede verdier, og setter inn navn og tall. Én ugyldig påstand forkaster hele forklaringen og gir merket reservetekst. En gyldig forklaring har minst én relevant, faktakontrollert påstand om en Myk faktor (SM-4/AV-15). «Faktoren som bidrar mest» er ikke et krav.
- **Referanse (P-07):** nr. 1 sammenlignes med nr. 2, og de andre sammenlignes med nr. 1. Ved én gyldig Kandidat er det ingen referanse. KI kan ikke velge referansen selv. Fri sammenligning av to merkede kandidater er et strekkmål etter v1.
- **Feil er ikke krasj (NFR4):** 429, 402, tidsavbrudd, tomme eller ubrukelige svar og forkastet faktakontroll gir 200 med `status: "avveining_feilet"` for Kandidaten. Rangering og Godkjenning virker videre. Vaktkostnad, Timebelastning, Ulempebelastning og preferansekategori eller -status med poeng vises også ved reservetekst.
- **SM-C2/AV-15:** en live-forklaring vises bare etter bestått faktakontroll. Innen 90 s fra første live-kall for Avveiningen vises en godkjent forklaring eller merket reservetekst. Fristen regnes ikke fra vaktvalget og gjelder ikke demo-modus. Korrekthet går foran hastighet (NFR10).
- **Lekkasjeinvariant (NFR2/SM-2):** ingen utelukket kandidat-ID når forklaringsporten, og ingen utelukket Kandidat nevnes i output, i Rangeringen eller i API-svaret. Et svar som nevner en utelukket Ansatt, forkastes.
- **Determinisme (NFR1):** samme lagrede preferanser og samme input gir samme rekkefølge. Rangeringen gjør aldri et live KI-kall.
- Avveininger lagres ikke historisk ved Godkjenning (P-12).
- Ingen nøkler i repoet, i git-historikken eller i en committet `.env` (NFR7).

## Technical Decisions

- **Hard grense (AD-1/AD-2):** `domene/regelmotor` og `domene/porter` importerer aldri `adaptere/*`. Dette håndheves av import-linter-kontrakten og en kjøretidstest. Bare `adaptere/api` kaller `adaptere/ki`, i to retninger: (1) råtekst blir `TolketPreferanse` før Rangeringen, og (2) `RangertKandidat` med referansefakta blir Avveining etter Rangeringen. Portene er Pydantic-modeller i `domene/porter`. Tolkingsporten kan behandle tekst før filtrering uten kandidatstatus. Forklaringsporten får bare gyldige, ferdig beregnede fakta.
- **Eierskap:** bare `adaptere/ki` fastsetter en ny `TolketPreferanse`. `adaptere/lagring` kan bare deserialisere og validere en tidligere lagret, vellykket verdi for samme Ansatt og preferansetekst. Lagringsfelt og eventuell formatversjon fastsettes og testes i 5.1. Lagringsadapteren eier skjemaet (AD-5).
- **Grunnlagsmerket (P-09):** tolkning og tolkestatus påvirker Rangeringen og skal inngå i grunnlagsmerket. Kolonner på `ansatt` dekkes automatisk. En egen tabell må føres i `GRUNNLAGSTABELLER`. En tolkning som blir ferdig mellom visning og godkjenning, gir `endret_grunnlag` og krever ny bekreftelse. Avveiningen er ikke deterministisk og skal **ikke** inn i merket. I stedet bærer hver Avveining merket for rangeringen den ble laget fra, og frontend forkaster Avveininger med et annet merke enn gjeldende visning.
- **OpenRouter (AD-7):** modellen er `openai/gpt-6-luna`, bundet til leverandøren `openai` uten leverandørfallback. Bindingen testes med en falsk HTTP-klient. Svaret er strukturert JSON etter et JSON-skjema, og resonnering er av. Én felles begrenser for begge KI-funksjonene tillater høyst 18 kall per 60 s og 5 samtidige. Ved 429 venter adapteren til `X-RateLimit-Reset`. For Avveining venter den 2, 4 og 8 s ved 5xx og nettverksfeil, innen 90 s. 402, andre 4xx og ubrukelige svar prøves ikke på nytt. Konstantene ligger i adapteren. Valget mellom OpenAI-SDK og ren HTTP-klient er ikke tatt.
- **KI-modus (AD-6):** `KI_MODUS` er `openrouter` eller `demo`. Mangler nøkkelen, starter appen i demo, logger det og krasjer ikke. Modus velges bare i oppstartslaget til `adaptere/api`. `OpenRouterKiAdapter` og `DemoKiAdapter` har identiske porttyper, og invarianttesten kjøres mot begge. I demo-modus gjelder dette:
  - Ukjent preferansetekst får feilet tolkestatus og 50 poeng.
  - En forhåndsgenerert Avveining brukes bare ved full identitetsmatch: Vakt, Kandidat, `RangertKandidat`, referanse-ID, sammenligningsfakta og kontraktsversjon. Den må også bestå samme faktakontroll som live-svar. Ellers brukes maltekst eller reservetekst.
  - Live-modus faller aldri stille tilbake til demo.
- Gyldige Avveininger bærer `ki_kilde: "live" | "forhandsgenerert" | "mal"`.
- **Konfigurasjon:** `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` og `KI_MODUS` leses fra miljøet og dokumenteres uten verdi i `.env.example`. Testene bruker en falsk KI-adapter eller HTTP-klient og trenger verken nettverk eller nøkkel.
- **Felles 200-svar med `status`-diskriminator (AD-4):** frontend henter brukerteksten fra sin egen tekstliste ut fra `status` eller `kode`, aldri fra `melding`.
- **KI-logg:** transportvalget for progressiv lasting (5.5), invarianttesten (5.6) og generering av demosvar med modell, dato og kommando (5.7) dokumenteres i `docs/ki-logg/`.

## UX & Interaction Patterns

- Preferansetaggen (UX-DR11) viser den tolkede kategorien, for eksempel «Ønsker flere vakter», «Fleksibel» eller «Ingen registrert», eller vente- eller feilstatusen.
- Forklaringspanelet (UX-DR12) har bakgrunn `#f2f6f9`, «▲ Trekker opp» i `ok` og «▼ Trekker ned» i `danger`. Nr. 1 er utvidet ved lasting. De andre er kollapset bak «Vis begrunnelse ▾» / «Skjul begrunnelse ▴», og radene åpnes uavhengig av hverandre. Lenkene kan brukes med tab og enter. Det samme panelet vises på Godkjenning-flaten.
- Kildelinjen i `meta` (UX-DR27) vises i alle moduser:
  - «KI-generert · <modell>» for en godkjent live-forklaring
  - «Forhåndsgenerert KI-forklaring · <modell>, <dato>» for et forhåndsgenerert svar
  - «Satt sammen fra beregnede tall, ikke KI-generert» for maltekst
  - «Reservetekst · KI-forklaring utilgjengelig» ved `avveining_feilet`

  Et forkastet svar merkes aldri som godkjent KI.
- I demo-modus viser appbaren en nøytral «Demo-modus»-tag. Den bruker ingen `warn`- eller `danger`-farge, fordi demo-modus er en normaltilstand.
- Radene med nøkkeltall vises med en gang. Hver Avveining lastes inn i raden sin med en egen lastetilstand som er ulik både reserveteksten og tomtilstanden (UX-DR13). Lukkede Avveininger hentes først når raden åpnes. Én feil påvirker ikke de andre radene.
- Teksten skal være kort, presis og tallbasert, uten utropstegn og uten å antyde at systemet har valgt noe (UX-DR23).

## Cross-Story Dependencies

- 5.1 kan gå parallelt med Epic 4. 5.2–5.6 bygger på `RangertKandidat` og Rangeringen fra story 4.4. Demosvarene i 5.7 må genereres etter story 4.7, fordi ulempefeltene inngår i hashen.
- 5.2 bygger på 5.1. 5.4, 5.5 og 5.6 bygger på 5.3. 5.7 bygger på 5.1 og 5.3. 5.8 bygger på 5.7. Delen om sensornøkkel avhenger av ÅB-8, som hele gruppa avgjør før innlevering.
- Grunnlagsmerket og avvisningen av sene svar fra story 3.2 brukes i 5.1, 5.2, 5.3, 5.5 og 5.9.
- 5.6 bruker import-linter-kontrakten fra story 2.1 og utelukkelser fra alle fire Harde regler (Epic 2).
- 5.9 krever innlogging (FR-13) og en fungerende kjerneflyt. Den er et v1-tillegg som kan dokumenteres som utsatt. Manuell overstyring av kategori er utenfor scope.
