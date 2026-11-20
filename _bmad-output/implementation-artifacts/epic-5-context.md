# Epic 5 Context: KI-forklaring av avveininger

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Mål

Når en Vakt har gyldige, rangerte kandidater (Epic 4), skal KI gjøre to ting og bare det:
tolke den ansattes frie preferansetekst til en kategori Rangeringen kan bruke, og forklare
i klartekst hvorfor hver kandidat er rangert der den er — hva som trekker opp, hva som
trekker ned, kostnadsvurderingen og relevante preferanser. KI beregner aldri Harde regler,
arbeidstid, kostnad eller selve Rangeringen; den tolker tekst og forklarer tall som
domenekjernen allerede har regnet ut. Grensen mellom det deterministiske laget og KI-laget
er en hard systemgrense: en kandidat utelukket av en Hard regel skal aldri nås eller
nevnes av forklaringsporten. Epicet leverer også en demo-modus uten API-nøkkel, slik at
appen kan kjøres og vurderes uten gruppens KI-tilgang, og oppsettet som lar sensor kjøre
mot ekte KI.

Story 5.1 (preferansetolkning, inkludert brukerutløst «Prøv igjen» etter endelig feil) er
`done` — alle akseptansekriteriene er oppfylt og uavhengig gjennomgått. De øvrige storiene
er ikke blokkert: `RangertKandidat`-porten fra Epic 4 er ferdig, så arbeidet kan starte
(se `sprint-status.yaml` for faktisk status per story — den endrer seg oftere enn denne
filen bør regenereres).

## Stories

- Story 5.1: Tolke tekstbaserte ansattpreferanser med KI (ferdig/`done`)
- Story 5.2: Rangeringen bruker tolkede preferanser
- Story 5.3: Avveining per kandidat
- Story 5.4: Reservetekst når KI-forklaringen feiler
- Story 5.5: Rader vises før forklaringene er ferdige
- Story 5.6: Test av at utelukkede kandidater aldri når KI-laget
- Story 5.7: Demo-modus uten API-nøkkel
- Story 5.8: Sensor kan kjøre live KI
- Story 5.9: Redigere preferansetekst etter fungerende kjerneflyt (P-10B, planlagt v1-tillegg;
  blokkerer ikke kjerneflyten og kan utsettes hvis tiden ikke rekker)

## Krav og avgrensninger

- KI har to atskilte, ensrettede roller: **tolke** rå preferansetekst til en
  `TolketPreferanse`-kategori før filtrering (uten kandidatstatus for en bestemt Vakt), og
  **forklare** en allerede ferdig rangert kandidat ut fra fakta regelmotoren har beregnet.
  Ingen av rollene kaller inn i domenekjernen, og domenekjernen kaller aldri KI. Bare
  `adaptere/ki` fastsetter en ny `TolketPreferanse`; `adaptere/lagring` kan bare
  deserialisere og validere en tidligere lagret, vellykket verdi for samme Ansatt og
  preferansetekst — aldri tolke på nytt selv. Lagringsadapteren eier skjemaet (AD-5).
- Preferansekategorier og poeng (fast skala, koden setter poenget, ikke modellen): 100
  ønsker aktivt flere vakter, 75 positiv ved behov, 50 nøytral, 25 foretrekker å slippe men
  åpen ved behov, 0 tydelig ønske om å unngå ekstravakter. 15 definerte preferansetekster
  med fasit skal tolkes til forventet kategori (eksakt KI-ordlyd er ikke fasit). Manglende
  registrert preferanse gir 50 poeng merket «Ingen registrert», aldri fremstilt som et
  uttrykkelig nøytralt ønske; venter-på-tolkning og feilet tolkning gir midlertidig 50 poeng
  med egne statuser, «Preferanse venter på tolkning» og «Preferanse kunne ikke tolkes».
- Rangeringen gjør aldri et live KI-kall — den leser bare lagrede `TolketPreferanse`-verdier.
  Tolkning og tolkestatus inngår i grunnlagsmerket (P-09): kolonner på `ansatt` dekkes
  automatisk, men en egen tabell for formålet må føres i `GRUNNLAGSTABELLER`. En ny gyldig
  tolkning som lagres mens godkjenningsflaten er åpen, skal beregne rangeringen på nytt og
  kreve ny bekreftelse før godkjenning (P-05/P-09); gammel tolkning av endret tekst brukes
  aldri.
- Forklaringsporten får bare forhåndsberegnede fakta for gyldige kandidater: nr. 1 blir
  sammenlignet med nr. 2, øvrige med nr. 1, og én kandidat uten referanse. KI kan ikke velge
  referansen selv; fri sammenligning av to merkede kandidater er et strekkmål etter v1.
  Tillatte påstandstyper er avgrenset til: oppfyller de fire prototypereglene, en navngitt
  faktor trekker opp/ned, eller en faktor/totalscore er høyere/lavere/lik referansens («lik»
  krever lik uavrundet verdi). Koden, ikke KI, setter inn navn og tall, og validerer hver
  påstand mot uavrundet grunnlag. Ett ugyldig påstandsfelt forkaster hele forklaringen til
  fordel for Reservetekst. Hver gyldig forklaring må ha minst én relevant, faktakontrollert
  påstand om en Myk faktor; «faktoren som bidrar mest» er ikke et krav (SM-4/AV-15).
- Ved feil, tomt eller ubrukelig svar skal systemet aldri vise en oppdiktet tolkning eller
  anbefaling, og aldri krasje: Reservetekst/feilstatus vises i stedet, mens Rangering og
  Godkjenning forblir tilgjengelig, og Vaktkostnad, Timebelastning, Ulempebelastning og
  preferansekategori/-status med poeng vises fortsatt ved siden av Reservetekst (NFR4). En
  Avveining som nevner en kandidat utelukket av en Hard regel, forkastes som ubrukelig.
- Testbare invarianter som binder epicet: ingen utelukket kandidat-ID sendes til
  forklaringsporten eller nevnes i output (SM-2); samme input gir samme rangeringsrekkefølge
  hver gang (SM-5/NFR1); innen 90 sekunder fra første live-forklaringskall vises enten en
  faktakontrollert forklaring eller tydelig merket Reservetekst (SM-C2); appen kan bygges og
  kjøres fra et rent klonet repo uten gruppens API-nøkkel (SM-9).
- Avveiningen lagres ikke historisk ved Godkjenning — en ny visning genererer en ny
  forklaring fra gjeldende grunnlag (P-12). Hver Avveining er bundet til grunnlagsmerket den
  ble laget fra; et svar for et eldre merke forkastes og vises aldri som gjeldende.

## Tekniske avgjørelser

- **Rate limiting og nye forsøk (AD-7):** OpenRouter-kontoen med `openai/gpt-6-luna` har en
  fast grense på 20 kall per kalenderminutt. Adapteren binder rutingen til leverandøren
  `openai` uten fallback, og en felles begrenser i `adaptere/ki` slipper gjennom høyst 18
  kall per 60 sekunder og 5 samtidige, delt mellom tolkning og forklaring. Ved 429 ventes til
  `X-RateLimit-Reset` (minst 1 s, 60 s hvis ikke lesbar). For Avveining ventes 2/4/8 sekunder
  ved 5xx/nettverksfeil, innen et tidsbudsjett på 90 sekunder fra første live-kall; 402 og
  andre 4xx prøves ikke på nytt. For preferansetolkning (vedtatt i AV-19) gjelder samme
  2/4/8-sekunders venting, tre nye forsøk, 90 sekunder per tekst fra første forsøk på plass i
  begrenseren, og sluttstatus `kunne_ikke_tolkes` med feiltype — `avveining_feilet` brukes
  aldri som tolkestatus. Begrenseren deles ikke mellom flere serverprosesser (v1 kjøres med
  én worker).
- **Porttyper:** `domene/porter` har frosne, logikkfrie dataklasser (`@dataclass(frozen=True)`,
  ikke Pydantic) — `TolketPreferanse` inn til Rangeringen og `RangertKandidat` ut. Validering
  av KI-svar skjer i `adaptere/ki` ved mottak og i `adaptere/lagring` ved lesing av lagrede
  verdier, ikke i porten selv (AV-18).
- **Strukturell grense (AD-1/AD-2):** `domene/regelmotor` og `domene/porter` har null
  importer av noen `adaptere/*`-pakke, håndhevet av en import-linter-kontrakt og dekket av en
  kjøretidstest som verifiserer at ingen utelukket kandidat når forklaringsporten (statisk
  sjekk alene fanger ikke kjøretidslekkasje).
- **Demo-modus (AD-6):** `KI_MODUS` er `openrouter` eller `demo`; mangler
  `OPENROUTER_API_KEY`, starter appen automatisk i demo uten å krasje. Valget skjer bare i
  oppstartslaget til `adaptere/api`. `DemoKiAdapter` bruker forhåndsgenererte
  `TolketPreferanse`- og Avveiningsverdier fra testdataene, slått opp mot en identitet som
  dekker hele faktagrunnlaget (Vakt, Kandidat, `RangertKandidat`, referanse,
  forklaringskontraktens versjon); mangler oppslaget eller svarer det ikke
  faktakontrollen, brukes maltekst fra gjeldende beregnede fakta (`ki_kilde: "mal"`) eller
  Reservetekst. Forhåndsgenererte svar er laget med `OpenRouterKiAdapter` og samme prompt
  som live, og loggført i `docs/ki-logg/`. Live-feil gir aldri stille fallback til demo.
  Hver gyldige Avveining bærer `ki_kilde: "live" | "forhandsgenerert" | "mal"`.
- **Config:** `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (standard `openai/gpt-6-luna`) og
  `KI_MODUS` leses fra miljøvariabler, aldri hardkodet, og dokumenteres uten verdier i
  `.env.example`. Tester bruker falske KI-adaptere/HTTP-klienter og krever aldri nettverk
  eller nøkkel; CI får aldri `OPENROUTER_API_KEY`.
- **Feilform (AD-4):** «Avveining feilet/tom» er ikke en HTTP-feil — API-et svarer 200 med
  `status: "avveining_feilet"` for den kandidaten; resten av raden, Rangeringen og
  Godkjenningen fungerer som normalt. Samme prinsipp som ellers i API-et: ingen rå
  backend-tekst vises i frontend, bare statusstyrt tekst fra frontendens egen tekstliste.
- **Transport for progressiv lasting** (story 5.5) er en åpen beslutning: valget mellom
  streaming, polling og separate kall per kandidat tas i selve storien og må dokumenteres i
  KI-loggen.
- **Klientbibliotek mot OpenRouter** (OpenAI-SDK vs. ren HTTP-klient) er ikke besluttet.
- **KI-logg:** transportvalget for progressiv lasting (5.5), invarianttesten mot
  utelukkede kandidater (5.6) og genereringen av demosvar med modell, dato og kommando
  (5.7) skal alle dokumenteres i `docs/ki-logg/`.

## UX og interaksjonsmønstre

- Rangeringstabellens topprangerte kandidat har Avveiningen utvidet som standard når siden
  lastes; øvrige rader er kollapset bak «Vis begrunnelse ▾», som blir «Skjul begrunnelse ▴»
  når åpnet. Å åpne én rad lukker ingen andre, og lenkene nås og aktiveres med tastatur.
  «▲ Trekker opp» vises i `ok`-farge og «▼ Trekker ned» i `danger`, på bakgrunn `#f2f6f9`.
- Lukkede Avveininger hentes først når raden åpnes, slik at vanlig bruk gir ett KI-kall per
  vakt (holder forbruket under takten i AD-7).
- Kildelinjen i `meta` (UX-DR27) vises i alle moduser, med fire faste tekster: «KI-generert
  · <modell>» for en godkjent live-forklaring, «Forhåndsgenerert KI-forklaring · <modell>,
  <dato>» for et forhåndsgenerert svar, «Satt sammen fra beregnede tall, ikke KI-generert»
  for maltekst, og «Reservetekst · KI-forklaring utilgjengelig» ved `avveining_feilet`. Et
  forkastet svar merkes aldri som godkjent KI. Demo-modus er en normaltilstand uten
  varsel-/feilfarge, og appbaren viser taggen «Demo-modus».
  Godkjenningsflatens kandidatkort viser Avveiningen for valgt kandidat i et eget
  forklaringspanel.
- Kandidatlistens preferanse-tag viser tolket preferanse («Ønsker flere vakter»,
  «Fleksibel», osv.) eller «Ingen registrert».
- Alle rader med nøkkeltall vises umiddelbart når kandidatberegningen er ferdig, uten å
  vente på noen Avveining; hver Avveining får en egen lastetilstand forskjellig fra både
  Reservetekst og tomtilstand, og én feilende Avveining påvirker ikke de andre radene.
- Gjennomgående tone (UX-DR23): systemet beskriver tilstand og begrunner tall, formaner og
  feirer aldri, og teksten har ingen utropstegn. Forhåndsgenerert eller malbasert innhold
  sier rett ut at det ikke er live KI.

## Avhengigheter mellom stories

- Story 5.2–5.6 bygger alle på `RangertKandidat`-porten fra Epic 4 (story 4.4), som er
  ferdig — epicet er derfor ikke blokkert.
- Story 5.2 (Rangeringen bruker tolkede preferanser) avhenger av lagrede
  `TolketPreferanse`-verdier fra story 5.1 (ferdig) og mater videre inn i story 5.3.
- Story 5.3 (Avveining per kandidat) er grunnlaget for 5.4 (reservetekst ved feil), 5.5
  (progressiv lasting) og 5.6 (kjøretidstest mot utelukkede kandidater) — alle tre bygger
  direkte på 5.3.
- Story 5.7 (demo-modus) bygger på både 5.1 og 5.3, og krever at forhåndsgenererte svar
  lages *etter* at Epic 4 (story 4.7, Ulempebelastning) er ferdig, fordi de feltene inngår i
  hashen/identiteten til `RangertKandidat`; svar generert før det ville gitt maltekst i
  stedet for forhåndsgenerert innhold.
- Story 5.8 (sensor kan kjøre live KI) bygger på 5.7; delen om å levere en nøkkel til sensor
  avhenger av en ekstern avklaring (ÅB-8).
- Story 5.9 (redigere preferansetekst) er et planlagt v1-tillegg etter at kjerneflyten
  (vaktvalg → Godkjenning) virker, og blokkerer ikke resten av epicet. Krever innlogging
  (FR-13); manuell overstyring av kategori er utenfor scope.
- Grunnlagsmerket og avvisningen av sene svar fra story 3.2 gjenbrukes i 5.1, 5.2, 5.3, 5.5
  og 5.9.
- Story 5.6 bruker import-linter-kontrakten fra story 2.1 og utelukkelsene fra alle fire
  Harde regler (Epic 2).
