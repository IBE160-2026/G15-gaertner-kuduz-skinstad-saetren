# KI-logg: Story 5.2 – rangeringen bruker tolkede preferanser

Dato: 2026-11-20. Utført av Claude (Sonnet 5) i `bmad-build`s oneshot-rute, direkte i
denne økten (ikke en separat implementeringsunderagent, siden endringen var liten og
uten intent-gap).

## Oppgave og prompt

Mithad Kuduz' prompt, ordrett:

> ny story vi kan ta?

Deretter valgte han blant alternativer jeg presenterte, ordrett som vist i dialogen:

> «5.2 — Rangeringen bruker tolkede preferanser»

og, på spørsmål om branch eller rett på `main`:

> «Branch + PR (Anbefalt)»

Dette er en melding om ansvar (OP-18), ikke et gruppevedtak — det sier referatet selv
(`avklaringspunkter.md`). Branch og PR er et valg den enkelte gjør (AGENTS.md Policy);
Mithad valgte selv, etter min anbefaling. Spesifikasjonens frosne Intent: undersøke om
Rangeringen faktisk bruker lagrede preferansetolkninger som vanlig input (epics.md,
story 5.2, AC1–AC4), og tette gapet med en test der det mangler.

## Leveranse

Undersøkelse før koding viste at AC1 (`ranger()` mottar `tolkede`/`feilede` fra
`adaptere/api`), AC3 (reproduserbarhet) og AC4 (ny tolkning krever rangering på nytt før
bekreftelse; gammel tolkning av endret tekst brukes aldri) allerede var oppfylt av kode
og tester fra story 4.4, 4.5 og 5.1. Bare AC2 (to kandidater like på kostnad,
timebelastning og ulempe, der bare preferansen skiller dem) manglet en dedikert test.
Lagt til: `test_preferanse_alene_avgjør_rangeringen_når_alt_annet_er_likt` i
`backend/tester/regelmotor/test_rangering.py`, etter samme mønster som den eksisterende
ulempe-isolasjonstesten fra story 4.4. Ingen produksjonskode endret.

## Rettelser

En uavhengig blind-gjennomgang (Claude Opus 5.5, per anbefalingen i
`docs/modellvalg-stories.md` for story 5.2) fant 13 funn. Disse ble rettet:

- Testens rekkefølge-påstand beviste ikke kravet alene: kandidat-ID-ene var valgt slik at
  stigende-ID-tiebreaket (AV-05) tilfeldigvis ga samme rekkefølge som preferansen, så en
  fjernet preferansevekt bare ville felt totalscore-påstanden, ikke rekkefølgen. ID-ene
  er byttet om, slik at tiebreaket alene ville gitt feil rekkefølge, og rekkefølgen
  beviser nå kravet selv om totalscore-påstanden fjernes.
- En redundant, duplisert kalling av `ranger()` i testen er fjernet til fordel for å
  gjenbruke resultatet som allerede var beregnet.
- Spesifikasjonens Implementation Notes siterte feil eller ufullstendige bevis for tre
  av akseptansekriteriene: AC4 manglet den faktiske backend-testen for `endret_grunnlag`
  (`test_ny_tolkning_etter_visning_gir_endret_grunnlag`) og navnga ikke de to konkrete
  testene for at en gammel tolkning av endret tekst aldri brukes; AC3s kjøretall var
  feil (41 kjøringer, ikke 21); AC1 hadde ingen testreferanse for at domenekjernen aldri
  kaller KI. Alle tre er rettet med fulle filstier og linjenumre.
- Den gjenbrukte `epic-5-context.md` (regenerert ved oppstart av denne storyen, fordi
  planleggingsdokumenter var endret siden forrige versjon) hadde mistet flere konkrete,
  bindende detaljer fra den forrige, committede versjonen: eierskapsregelen for
  `TolketPreferanse`, `GRUNNLAGSTABELLER`-kravet, de eksakte statustekstene, de fire
  kildelinjetekstene (UX-DR27), `ki_kilde`-verdiene, at KI ikke kan velge referanse selv,
  at «faktoren som bidrar mest» ikke er et krav, regelen om ingen utropstegn (UX-DR23),
  KI-logg-kravene for 5.5–5.7, og deler av avhengighetene mellom stories. Alt dette er
  ført tilbake inn i den nye, omstrukturerte filen. Den nye filen påsto også at story
  5.2–5.9 «står i backlog», noe som motsa `sprint-status.yaml` i samme diff — fjernet.

Avvist uten retting:

- At AC2 burde testes mot flere statuser enn «nøytral» (venter på tolkning, ingen
  registrert, kunne ikke tolkes) i tillegg til den som allerede er lagt til. Alle disse
  gir 50 poeng gjennom en annen kodevei, og den likheten er allerede dekket av
  `test_alle_fire_tolkestatuser` (story 4.4); å utvide isolasjonstesten videre ville bare
  gjentatt det beviset.
- At `DemoKiAdapter` bruker forhåndsgenererte tolkninger «fra testdataene», og at vanlig
  bruk gir «ett KI-kall per vakt», var usitert i `epic-5-context.md`: begge er sporet
  direkte til arkitekturdokumentet (AD-6) og epics.md (story 5.3s akseptansekriterium),
  ikke diktet opp — bare omskrevet til å beskrive formålet i stedet for å sitere kilden,
  slik kompileringsreglene krever.

## Kvalitetssikring

`pytest` 686 (inkludert den nye testen), kjørt lokalt på
`story/5-2-rangeringen-bruker-tolkede-preferanser` (gren fra `main` ved `2302a8f`).
Testen vist å kunne feile: `preferansevekt`-leddet i `totalscore()` ble midlertidig
fjernet, både totalscore- og rekkefølge-påstandene ga rødt, og koden ble tilbakestilt
(`git diff` tomt etterpå). Frontend er urørt i denne storyen (build, 52 modultester og
48 komponenttester, uendret fra forrige måling på `main`).

## PR-gjennomgang og rettelser, 2026-11-20

Utført av Claude (Opus 5.5) for Johannes Gärtner, som gjennomgang av PR #34.

### Prompt

Første prompt, ordrett:

> hent siste endringer fra repoet. Start gjennomgang av PR 34. Gi meg et overblikk over
> PR'en, kjør review, gå igjennom arbeidet som er gjort og start kjøringen av underagenter
> som utforsker og utfordrer problemene du finner.

Andre prompt, etter gjennomgangen, ordrett. Tallene viser til funnlisten i gjennomgangen
(1 AC2-testen, 2 KI-kall i godkjenningsruten, 3 `epic-5-context.md`, 4 KI-loggen, 5 småting):

> 1: implementer foreslåtte endringer i testing på branchen. Dokumenter hvorfor. 2. Fiks
> problemet og forklar hvorfor. 3. Er dette noe du kan fikse eller må du ha konteksten fra
> arbeidet til Mithad? Hvis du kan - fiks det. 4. mottatt. Dette er sikkert en glipp med en
> prompt som ikke er relevant for branchen, jeg har informert mithad. 5. Fiks småtingene,
> forklar hvorfor.
>
> Kommenter endringene som er gjort på PR'en. kjør tester for å se at det fungerer, gjør
> klar til å push endringene til branchen

### Gjennomgangen

- `bmad-review` med tre uavhengige linser (adversarial, edge-case og verification-gap) på
  diffen mot `origin/main`.
- Deretter fire utfordringsagenter, som først skulle forsøke å avkrefte funnene. De så på
  epic-konteksten mot planverket, AC2-testen med mutasjoner, AC1/AC4-bevisene med utkast
  til tester og prosessen mot tidligere praksis.
- Agentene endret ingen sporede filer. Mutasjonene ble tilbakestilt med `git checkout`.

### Hva modellen leverte

- **AC2-testen** er erstattet av en parametrisert versjon med en tredje kandidat, og en ny
  test viser at preferansen veier tyngre enn en liten kostnadsforskjell.
  - Testkoden er foreslått av en underagent og tatt inn uendret.
  - Tallene i kommentarene er kontrollert for hånd mot vektene 0,40/0,20/0,15/0,25.
  - Nøytralteksten er kontrollert mot PRD §4.5 nr. 7.
- **To API-tester** er lagt til i `backend/tester/api/test_preferansetolkning.py`:
  - `test_rangeringen_kaller_aldri_ki_i_noen_tolkestatus` (AC1)
  - `test_prov_igjen_etter_feil_beregner_rangeringen_paa_nytt` (AC4 etter feil)
- **`epic-5-context.md`** er tilbakestilt til versjonen på `main`, med sju setninger fra den
  regenererte filen som har kilde i planverket (spine linje 103, epics linje 1041, 1133 og
  1198–1201, arkitekturens utsatte beslutninger, PRD SM-9).
- **Ordlyden** i spesifikasjonen, vurderingsmatrisen, `docs/testing.md` og `AGENTS.md` er
  rettet.

### Hva som ble rettet og hvorfor

- **Den gamle AC2-testen** fanget ikke to mutasjoner i `domene/regelmotor/rangering.py`:
  - Mutasjon 1: en `noytral`-tolkning ble ignorert, slik at kandidaten falt tilbake til
    «venter» med de samme 50 poengene.
  - Mutasjon 2: preferansen ble brukt bare som tiebreak. Den besto hele `tester/regelmotor`.
  - Årsaken var at testen ikke sjekket tolkestatus, og at to like kandidater gir flat
    min–maks (50/50).
- **Godkjenningsruten** hadde ingen test for at den ikke kaller KI mens tekstene venter.
  Et KI-kall for ventende tekster lagt inn i `godkjenningsgrunnlag()` ga 686/686 grønn
  suite. Med den nye testen feilet 1 av 690.
- **`epic-5-context.md`** var regenerert med begrunnelsen at `epics.md` og
  `ARCHITECTURE-SPINE.md` var endret. Siden `1e66378` er bare en statuslinje i `epics.md`
  endret (`59fb5c9`).
  - Omtrent 15 bindende detaljer manglet fortsatt, blant annet at Avveiningen ikke skal inn
    i grunnlagsmerket, JSON-skjema og resonnering av (AD-7) og demo-regelen for ukjent tekst.
  - Overskriftene var på norsk, mens epic 1–4 bruker engelsk.
  - Konteksten krever ingen kunnskap fra Mithads økt, fordi den bygges fra planverket.
    Derfor ble den rettet her.
- **AGENTS.md** førte 5.2 som ferdig før merge. For 4.4 og 5.1 ble det gjort etter merge.

### Kvalitetssikring

Mutasjoner mot de nye AC2-testene, alle tilbakestilt:

| Mutasjon | Resultat |
|---|---|
| Preferansevekten fjernet | rødt |
| Nøytral tolkning ignorert | rødt |
| Min–maks på preferansen | rødt |
| Preferansen bare som tiebreak | rødt i vekttesten |
| Synkende id-tiebreak | grønt, riktig fordi totalene er ulike |

Mutasjonen i godkjenningsruten er beskrevet over. `git status` var ren for produksjonskode
etter hver mutasjon. Testkjøringer etter endringene står i spesifikasjonen og i commiten.
