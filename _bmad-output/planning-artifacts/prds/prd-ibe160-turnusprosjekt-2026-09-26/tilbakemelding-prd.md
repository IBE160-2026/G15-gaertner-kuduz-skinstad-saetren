# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G15 – G15-gaertner-kuduz-skinstad-saetren |
| **PRD vurdert** | `_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md` (status `final`, sist endret 2026-11-11, commit b0cc8fb) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

Dette er en uvanlig sterk PRD for et studentprosjekt: tydelig tese, FR-er med testbare konsekvenser og regneeksempler, og en ærlig avgrensning. Risikoen ligger ikke i substansen, men i at dokumentet har vokset til rundt 6 500 ord og peker så mye ut til beslutningsreferatet, seeddata og stories at det ikke lenger står på egne bein for den som skal bruke det videre.

## 2. Dette fungerer godt

- **Tesen er konkret og bæres av funksjonene.** §1: «Turnushjelperen anbefaler — den bestemmer aldri selv, og den kan aldri anbefale en kandidat som en hard regel har utelukket.» Grensen mellom deterministisk lag og KI går igjen i §4.2, §4.5, §5 og SM-2.
- **FR-ene kan bli testtilfeller direkte.** FR-4: «Hvile på nøyaktig 11 timer oppfyller denne regelen; 10 timer og 59 minutter gjør det ikke.» FR-7 har håndregnede fasiter (32 t + åttetimersvakt ved 300 kr/t gir 3 000 kr), og FR-10 har 15 preferansetekster med forventet kategori.
- **KI-kontroll og kjørbarhet er tatt på alvor.** §4.5 har demo-modus uten API-nøkkel som tydelig merkes i grensesnittet, reservetekst ved modellfeil, og validering av KI-påstander mot beregnede tall (FR-11). Avveiningene står åpent, for eksempel taket på 300 Ulempepoeng i §4.3 («valgt fremfor 240 og 432»).

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | god | Valg og avveininger er synlige, men §8 blander åpne spørsmål med gjennomføringsoppgaver. |
| Substans | sterk | Alt innhold styrer beslutninger. Ingen pynte-personas eller boilerplate-NFR-er. |
| Strategisk sammenheng | sterk | Klar tese, prioritering følger av den, og motmetrikker (SM-C1, SM-C2) finnes. |
| Testbarhet | sterk | Grensetilfeller, fasiter og invarianter. Noen få formuleringer er fortsatt vage (se 4.4). |
| Scope og avgrensning | god | Ikke-mål er ærlige. Det mangler skille mellom kjerne og «hvis tiden rekker» (se 4.5). |
| Brukbarhet for neste fase | god | Gode ID-er, men PRD-en er ikke selvbærende og glossaret har hull (se 4.1). |
| Formtilpasning | god | Passer et enrolle-verktøy. Én brukerreise er nok, men feilsporet i UJ-1 kunne vært en egen reise. |

## 4. Viktigste forbedringer

### 4.1 PRD-en er ikke selvbærende
- **Alvorlighet:** medium
- **Hvor:** FR-1 («P-08», «P-09»), §4.2 («#4261–#4265», «KS-04»), §4.3 («`scripts/ulempe_regneeksempler.py`», «ikke en miljøvariabel»), §8.
- **Problem og hvorfor det betyr noe:** Kravene henviser til beslutnings-ID-er, ticketnumre og seeddata som bare finnes i andre filer. Den som skriver stories eller tester må åpne referatet for å forstå selve kravet. Implementasjonsvalg (konfigurasjon i domenekjernen, skriptnavn) hører til arkitektur, ikke krav.
- **Forslag:** La kravet stå alene og flytt sporbarheten til en liten tabell sist. Eksempel for FR-1: «Mangler nødvendig turnusgrunnlag for den valgte Vakten, viser systemet «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» og tilbyr verken Rangering eller Godkjenning.» (P-08 i tabellen). Legg «Ansatt», «Demo-modus», «Reservetekst» og «Datafeil» i ordlisten.

### 4.2 §8 er en oppgaveliste, ikke åpne spørsmål, og status er `final`
- **Alvorlighet:** medium
- **Hvor:** §8 «Gjenstående gjennomføring og kontroll», frontmatter `status: final`.
- **Problem og hvorfor det betyr noe:** De seks punktene er kontroller og stories («Implementer og test…»). De virkelig åpne spørsmålene, som mobil/nettbrett (P-13/OP-02) og hvor mye kreditt sensor får, er gjemt i løpende tekst.
- **Forslag:** Del §8 i «Åpne spørsmål» (hvert med eier og frist, for eksempel «OP-02: Skal Turnushjelperen støtte mobil? Avklares før story 4.6») og la kontrollene ligge i epics/testplan. Skriv så i §0 hva `final` betyr her: kravene er låst, implementasjonen er ikke ferdig.

### 4.3 Innlogging og sikkerhet er tynt i forhold til resten
- **Alvorlighet:** medium
- **Hvor:** FR-13 («Ingen funksjonalitet i §4.1–§4.6 er tilgjengelig uten gyldig innlogging»).
- **Problem og hvorfor det betyr noe:** Ett enkelt krav med én konsekvens. Her bestemmes passordlagring, feil innlogging og hvor lenge en økt varer. Dette er også kravet sensor først møter.
- **Forslag:** Utvid FR-13 med testbare konsekvenser: «Feil brukernavn eller passord gir samme melding uten å røpe hvilket som var feil.» «Passord lagres aldri i klartekst.» «En økt utløper etter [x] minutter, og brukeren sendes til innlogging.» Legg til én felles linje om at API-nøkler aldri ligger i repoet eller i testdata.

### 4.4 Noen mål og krav er fortsatt ikke målbare
- **Alvorlighet:** lav
- **Hvor:** SM-3 («uten å måtte kontrollere alle manuelt»), SM-4 («forklarer hvilke faktorer som påvirker»), SM-C2 («Rask responstid»), FR-10 («avgrensede automatiske nye forsøk»).
- **Problem og hvorfor det betyr noe:** Disse kan ikke bli testtilfeller uten at noen tolker dem.
- **Forslag:** «Systemet gjør høyst 2 automatiske nye forsøk mot språkmodellen, og viser reservetekst senest 15 sekunder etter første kall.» SM-4 kan bli «Hver forklaring nevner minst Kostnad, Timebelastning og Ulempebelastning med tall fra regelmotoren.» (tallene er eksempler, velg egne).

### 4.5 Skill kjerne fra «hvis tiden rekker»
- **Alvorlighet:** lav
- **Hvor:** §5 («Planlagt etter kjerneflyten: P-10B»), FR-11 («strekkmål»), §6.2 («Alt listet i §5»).
- **Problem og hvorfor det betyr noe:** For fire personer er omfanget stort, med minuttpresis Ulempemodell, sommertid og 15 preferansetekster. Prioriteringen finnes i spredte setninger, ikke som en markering ved hvert krav.
- **Forslag:** Merk hvert FR med «Kjerne», «Etter kjerne» eller «Strekk», og gi §6.2 egne punkter med begrunnelse.

## 5. Mekaniske funn

- FR-1–FR-14, SM-1–SM-9 og SM-C1/C2 er sammenhengende. FR-14 står mellom FR-8 og FR-9, og det er forklart. Hvis dere omnummererer, må kryssreferansene i SM-5 og story-filene følge med.
- Ordlisten mangler «Ansatt», som brukes overalt. «Demo-modus», «Reservetekst» og «Datafeil» brukes som faste begreper uten definisjon.
- Antakelser-indeksen (§9) har fem punkter, men bare én står som `[ASSUMPTION]` inline (Kari i §2.3). Merk de andre der de oppstår.
- Referanser til `epics.md`, AD-5, story-numre og `docs/beslutninger/` er ikke kontrollert mot filene.

## 6. Før dere går videre

**Må avklares før UX, arkitektur og epics:** mobil/nettbrett (OP-02), hvem som betaler for sensors API-kreditt, og krav til innlogging og økt (4.3).

**Kan vente:** P-10B (redigering av preferansetekst), historikk for forklaringer (P-12B) og eventuelle flere arbeidstidsregler.

**Oppfølging av brief-tilbakemeldingen: ja.** Regelutvalget er låst (§4.2), vektene er bestemt (§4.4), mock-modus er beskrevet (§4.5), «inntil fem kandidater» og 15 preferansetekster er presisert, og briefen ligger nå ett sted.

## 7. Refleksjonsspørsmål

1. Taket på 300 Ulempepoeng bygger på regneeksempler (§9). Hvordan kontrollerte dere at eksemplene og skriptet stemte, og hva hadde dere gjort hvis en håndregning ga et annet svar enn skriptet?
2. PRD-en har fått mange tillegg gjennom vedtak. Hvilke detaljer godtok dere fra KI-forslag uten å kutte, og hvilke hører egentlig hjemme i testplan eller arkitektur?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
