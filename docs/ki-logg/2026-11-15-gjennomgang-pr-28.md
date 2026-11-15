# KI-logg: Gjennomgang av PR #28 – P-09-test for endret lønn

Dato: 2026-11-15. Utført av Johannes med Claude Code (Claude Opus 5.5) under
gjennomgangen av PR #28 (story 4.3, forenklet kostnad, Kim). Grunnlag:
[spesifikasjonen for 4.3](../../_bmad-output/implementation-artifacts/spec-4-3-forenklet-kostnad-per-kandidat.md),
P-09 i referatet og [KI-loggen for 4.3](2026-11-15-story-4-3-kostnad.md).

## Oppgave

Spesifikasjonen for 4.3 hadde en egen POST-test for ugyldiggjort lønn som åpent
punkt (lav prioritet). Grunnlagsmerket dekker alle ansattkolonnene, men ingen test
viste at en lønnsendring etter visning gir `endret_grunnlag` og en ny kostnad i
det nye grunnlaget.

## Prompt

Under walkthrough av PR #28 (`bmad-walkthrough`), etter at agenten hadde listet de
åpne punktene på branchen:

> Forslagene dine om åpent etter merge: p-09 post-test kan vi implementere med en gang.

## Modellens leveranse

Én ny test i `backend/tester/api/test_godkjenningsgrunnlag.py`:
`test_endret_lønn_krever_nytt_trykk_og_gir_ny_kostnad`. Testen bruker Ingrid Dahl
(id 4) på #4127. Hun har både ordinær tid og overtid, så både satsen og 150 %-satsen
blir kontrollert. Testen viser kostnaden (3 850 kr), endrer timelønnen fra 385 til
400 og poster det gamle merket. Den forventer 409 `endret_grunnlag` og at ingen
tabell er endret. Det nye grunnlaget skal vise 4 000 kr (4 t × 400 + 4 t × 600) med
satsene 400 og 600, og det nye merket skal gi 200.

Ingenting måtte rettes. Testen følger mønsteret i
`test_ansatt_og_vakttid_endrer_merket_uten_lagring`.

## Kvalitetssikring

- Testen bestod. Hele backendsuiten: 494 av 494 (493 før).
- Negativ kontroll: med `timelønn` midlertidig tatt ut av kolonnene i
  `grunnlagsmerke` (`kandidatgrunnlag.py`) feilet testen med `assert 200 == 409`.
  En godkjenning med utdatert kostnad ville da gått gjennom. Endringen er tilbakeført.
- Agenten kontrollerte også under gjennomgangen at SQLite godtar ugyldig lønn
  (`'300abc'`, `1.5`, `1e20`) til tross for `CHECK timelønn > 0` og `NOT NULL`, og at
  backend da logger `Datafeil for vakt 4127: ansatt 4: ugyldig timelønn`. Det ble kjørt
  mot en egen testdatabase utenfor repoet, uten kodeendring.

## Tillegg: integrering med story 4.2 etter PR #27

### Prompt

> Kim har merget PR27 nå. Godkjenn denne PR'en. Gjør nødvendige forberedelser til
> merge. samordne overtidsvarselet med det felles varselmerket fra PR27.

Kims krav, videreformidlet av Johannes: «Når endringene integreres, må den kobles
til samme komponent, og kombinasjonene høy belastning alene, overtid alene og begge
samtidig testes.»

### Modellens leveranse

- `origin/main` (med PR #27) er tatt inn i `story/4-3-forenklet-kostnad`. Det ga
  konflikt i 11 filer, og alle er løst slik at begge funksjonene er med: `KandidatUt`
  og begge rutene har både belastningsfeltene og `kostnad`, og det samme gjelder
  `Kandidat` i `api.ts`, feltsjekkene i API-testene og testdataene i `hjelpere.ts`.
  I `.logs/kimsk81/issues.md` er begge sidene beholdt. Sprintstatus: 4.2 står som på
  `main` (`review`), og 4.3 er satt til `done`.
- `frontend/src/komponenter/Kostnadsvisning.tsx`: «Inkluderer overtid» vises med
  `Varselmerke` fra 4.2 i stedet for egen farget tekst. `.kostnad-overtid` er fjernet
  fra `app.css`. «Ordinær» beholder `ok`-fargen (DESIGN.md).
- `frontend/src/tekster.ts`: ny `kostnadOvertidDel` («Overtid»). Den var hardkodet i
  komponenten og i komponenttesten.
- `frontend/tester/komponenter/kandidatflate.test.tsx`: ny test for ingen varsler,
  bare høy belastning, bare overtid og begge samtidig. Testen sjekker antall og
  tekster for `.varselmerke` i hver rad, at ikonet er skjult for skjermleser, og at
  «Ordinær» bare vises uten overtid.

### Rettet underveis

Typesjekken i `npm run build` feilet først. Hjelperen `kandidat()` fra PR #27 mangler
`kostnad`, som 4.3 gjør påkrevd, og to tester feilet. Hjelperen fikk en ordinær kostnad
som standard, slik at den ikke gir varselmerke.

### Kvalitetssikring

- Backend: 516 av 516. Frontend: bygget gikk gjennom, 50 av 50 modultester og 31 av 31
  komponenttester.
- Negativ kontroll: med «Inkluderer overtid» midlertidig vist som vanlig tekst uten
  `Varselmerke` feilet den nye testen. Endringen er tilbakeført.
- Ikke gjort: den integrerte raden med begge varslene er ikke kontrollert i nettleser,
  verken layout, større skrift eller tastatur (OP-16). Johannes valgte bort fysisk test
  i denne gjennomgangen.
