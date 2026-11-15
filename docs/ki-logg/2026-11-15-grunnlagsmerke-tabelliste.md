# KI-logg: Gjennomgang av PR #23 – grunnlagsmerke, «Til Vaktvalg» og SQLite-transaksjoner

Dato: 2026-11-15. Utført av Johannes med Claude Code (Claude Opus 5.5) under
gjennomgangen av PR #23 (story 3.2, Kim). Grunnlag: [spesifikasjonen for 3.2](../../_bmad-output/implementation-artifacts/spec-3-2-godkjenning-og-bemanning.md),
AD-5 og P-09 i arkitekturen, og storyene 5.1, 5.3 og 5.5 i `epics.md`.

## Oppgave

Grunnlagsmerket i `backend/adaptere/lagring/kandidatgrunnlag.py` hashet de tre
tabellene `turnus`, `ansatt` og `vakt` fra en hardkodet liste. En ny tabell i
Epic 4/5, for eksempel for `TolketPreferanse`, ville ikke kommet med i merket.
Godkjenning mot en rangering brukeren ikke har sett, kunne da gått gjennom uten
at noen test ble rød (P-09). Det eneste vernet var en kommentar i docstringen.

## Prompt

Under walkthrough av PR #23 (`bmad-walkthrough`), etter at detaljpasset hadde
pekt ut risikoen:

> Ta meg igjennom [kontrakt for senere epics] og foreslå forbedring

Agenten foreslo en eksplisitt tabelliste med en klassifiseringstest, og å skrive
to forutsetninger inn i dokumentasjonen. Deretter:

> Utfør endringen med eksplisitt tabelliste og noter det som kommer til å skje i
> story 5.1. Noter funnene du lister opp i notatene til tilhørende story 5.3 og
> 5.5. Deretter fortsetter vi gjennomgangen

## Modellens leveranse

- `GRUNNLAGSTABELLER` og `UTENFOR_GRUNNLAG` (med begrunnelse per tabell) i
  `kandidatgrunnlag.py`. `grunnlagsmerke` bruker listen. Merket er uendret for
  dagens skjema, så GET/POST-kontrakten fra PR #23 er den samme.
- Docstringen skriver ut to forutsetninger. Konstanter i `domene/` er dekket bare
  fordi JWT-nøkkelen byttes ved omstart. KI-forklaringer holdes bevisst utenfor
  merket.
- `backend/tester/lagring/test_grunnlagsmerke.py`: hver tabell i `Base.metadata`
  må stå i én av de to listene, listene kan ikke overlappe, og hver utelatt tabell
  har begrunnelse.
- Notater i `epics.md` for story 5.1 (klassifiser en ny tabell, test at en
  tolkning som blir ferdig i bakgrunnen gir `endret_grunnlag`), 5.3 (bind
  Avveiningen til et merke i stedet for å ta den inn i merket) og 5.5 (forkast
  Avveininger med utdatert merke, med komponenttest).
- `docs/testing.md` nevner den nye lagringstesten.

## Hva som ble rettet, og hvorfor

- Agenten vurderte en egen versjonskonstant for beregningene i merket og
  frarådet den: den må økes for hånd og har samme svakhet som kommentaren den
  skulle erstatte. Forutsetningen om JWT-nøkkelen er dokumentert i stedet. Ingen
  kode ble skrevet for dette.
- Forslaget i chatten sa at en ny tabell kunne føres «inn i merket eller ut med
  begrunnelse». For en tabell for `TolketPreferanse` var det for løst: tolkningen
  påvirker Rangeringen og må inn i merket. Notatet for 5.1 sier dette eksplisitt,
  og `UTENFOR_GRUNNLAG` er bare for tabeller uten beslutningsdata.
- Ingen kode måtte rettes etter testkjøringen.

## Begrensninger

Testen fanger nye ORM-tabeller, ikke tabeller laget med rå SQL. Den kan heller
ikke avgjøre om klassifiseringen er riktig, bare at den er gjort. Forutsetningen
om JWT-nøkkelen er dokumentert, men ikke håndhevet av noen test.

## Kvalitetssikring

- Hele backendpakken: **430 av 430** bestod (427 fra PR #23 og 3 nye).
- Negativ kontroll: en midlertidig ORM-tabell `tolket_preferanse` ble registrert
  på `Base` i et skript utenfor repoet. Da feilet
  `test_hver_tabell_er_klassifisert_for_grunnlagsmerket` med meldingen
  «Tabellene ['tolket_preferanse'] må føres i GRUNNLAGSTABELLER eller
  UTENFOR_GRUNNLAG …». Testen fanger altså tilfellet den er laget for.
- De eksisterende merketestene i `tester/api/test_godkjenningsgrunnlag.py`
  (endret grunnlag, ansatt og vakttid, kandidatbinding og snapshot) består
  uendret. De viser at merket oppfører seg som før.

## Tillegg: «Til Vaktvalg» når vakten allerede er bemannet

**Oppgave.** Johannes testet PR #23 manuelt: to faner godkjente samme vakt
(#4127, Jonas og Mette). Fanen som tapte, viste «Vakten er allerede bemannet.»
med «Prøv igjen». Et nytt forsøk ga 404 («Kandidaten kan ikke velges …»), og det
var ingen naturlig vei videre.

**Prompt:**

> På test 3: jeg tror vi skal legge inn en knapp som tar brukeren tilbake til
> hovedsiden. Slik at man ikke blir stående på en side man ikke kommer seg ut av
> på fornuftig vis.

**Modellens leveranse.**
- Ny tilstand `allerede_bemannet` i `frontend/src/godkjenning.ts`. Den kommer
  bare fra POST.
- `Godkjenningsflate.tsx` viser meldingen og en knapp, «Til Vaktvalg», som får
  fokus. «Prøv igjen» er tatt bort i denne tilstanden, fordi vakten er bemannet
  for godt og et nytt forsøk aldri kan lykkes. Agenten tok dette valget selv og
  meldte det til brukeren.
- `onTilOversikt` er gjort påkrevd. Før var den valgfri, og knappen ved usikkert
  utfall ble bare vist hvis prop-en var satt. Nå stopper TypeScript en bruk av
  flaten uten vei til Vaktvalg. `App.tsx` sendte den allerede, så bare
  testrendringene måtte få `onTilOversikt={vi.fn()}`.
- Ny komponenttest: overskrift med meldingen, fokus på «Til Vaktvalg», ingen
  «Prøv igjen» og ingen «Godkjenn erstatning», og at callbacken kalles.

**Kvalitetssikring.** `npm run build` består (typesjekk av kode og tester).
`npm run test` gir 49 av 49 modultester og 24 av 24 komponenttester (23 fra
PR #23 og 1 ny). Negativ kontroll: med Kims opprinnelige linje
(`setTilstand({ type: "feil", … })`) satt inn igjen feiler den nye testen. Koden
ble satt tilbake etterpå. Ikke sjekket manuelt i nettleser etter endringen.

## Tillegg: Dokumentasjon av transaksjoner i `sqlite3`

**Oppgave.** Johannes avsluttet gjennomgangen. Funnene om låsetesten og
feilsvarene skulle ikke rettes, men forutsetningen om transaksjoner skulle
dokumenteres.

**Prompt:**

> Push endringene på branchen. Deretter godkjenn PR'en og merge med main. Push
> alt arbeid. Funnene om låsetesten og feilsvar neglisjeres. Noter ned nødvendig
> dokumentasjon på transaksjoner/sqlite3.

**Modellens leveranse.** En docstring på `lag_engine` i
`backend/adaptere/lagring/database.py` og en fallgruve i `AGENTS.md`. Begge
forklarer at `BEGIN` i GET-grunnlaget og `BEGIN IMMEDIATE` i `lagre_godkjenning`
bygger på standardoppførselen til `sqlite3`, og hva som skjer om oppsettet
endres.

**Hva som ble rettet.** Agenten kjørte påstandene før commit:
- Standardverdiene (`isolation_level=""`, `autocommit=LEGACY_TRANSACTION_CONTROL`)
  er bekreftet i prosjektets venv (Python 3.15.2, SQLAlchemy 2.1.6).
- `autocommit=False` gir «cannot start a transaction within a transaction» ved
  eksplisitt `BEGIN IMMEDIATE`. Påstanden holdt.
- Første utkast sa at SQLAlchemys `"AUTOCOMMIT"` ville hindre at godkjenningen
  ble committet. Det var **feil**. En kjøring med `BEGIN IMMEDIATE`, INSERT og
  `session.commit()` lagret raden. Teksten sier nå at de eksplisitte
  transaksjonene virker, men at skriveveier uten eksplisitt `BEGIN` (som
  testdataene) mister transaksjonen sin. Dette er driverens kjente oppførsel med
  `isolation_level=None`, men det er ikke kjørt som eget forsøk.

**Kvalitetssikring.** Bare dokumentasjon og docstring. Hele backendpakken ble
kjørt på nytt før commit.
