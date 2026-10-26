---
title: Kildeundersøkelse av Turnushjelperens produktbrief
type: domain
topic: Turnushjelperen produktbrief
decision: Presisere briefens forutsetninger uten å utvide v1
source: native web research
status: complete
claims_verified: 3
claims_unverified: 7
preset: standard
validation: normal
created: 2026-10-26
updated: 2026-10-26
---

# Kildeundersøkelse av Turnushjelperens produktbrief

Beslutningsspørsmål: Hvilke løfter, antakelser og begreper bør presiseres for at briefen skal gi et etterprøvbart grunnlag for v1, uten å utvide prototypen?

Godkjent plan 2026-10-26: regler og kandidatbegreper, eksisterende turnusverktøy, rangering og brukerforståelse. Kilder og funn føres i digestfiler før syntese. Prosjektdokumenter er beslutningskontekst, ikke bevis for eksterne påstander.

## Beslutningssammendrag

**Behold den avgrensede prototypen. Presiser løftene og prøv forståelsen før dere hevder praktisk gevinst.** Kildene støtter at fire modellerte regler ikke er en full lovlighetskontroll. Eksisterende verktøy beskriver allerede kandidatforslag og forklaringer. Forskning gir ikke grunnlag for at en forklaring i seg selv sikrer bedre beslutninger. [1] [3] [7] [11] [15] [16]

Vektene 40/35/25 kan beholdes som gruppens demonstrasjonsvalg. De er ikke validert som riktige vekter for turnusansvarlige. Dokumenter skalaene, like verdier og følsomheten for endret kandidatsett; regneeksemplet nedenfor viser hvorfor dette har betydning. [13] [14]

Researchen gir konkrete presiseringer til brief, PRD og kommende tester. Den dokumenterer ikke spart tid, bedre bemanning eller full juridisk etterlevelse. Ingen intervjuer, praktiske konkurrenttester eller brukertester er gjennomført. Anbefalingene nedenfor er forslag; `product-brief.md` og produktbeslutningene er ikke endret.

**Les konfidensen presist:** «Verifisert» betyr at den avgrensede påstanden har uavhengig kildegrunnlag. «Uverifisert» betyr her manglende uavhengig bekreftelse eller ukjent aktuell funksjon, ikke at påstanden er motbevist. Kildens troverdighet, publiseringsdato og overførbarhet vurderes separat.

## Anbefalinger og mottakende dokumenter

| Forslag | Hvor det hører hjemme | Grunnlag og begrensning |
|---|---|---|
| Bytt «regler avgjør hva som er lovlig og mulig» med «kontrollerer de fire implementerte kravene i prototypen». | Brief: Sammendrag, Løsningen | Høy konfidens i avgrensningen av regelverket; formuleringen er et eget forslag. [1] [3] |
| Beskriv tilgjengelighet og preferansenes gyldighetsperiode som eksplisitte forutsetninger for fiktive data. | Brief: Løsningen/Omfang; PRD: datagrunnlag | Produktutledning. Trenger ikke ny fraværsmodul eller et universelt samtykkekrav. [5] [6] |
| Merk 36 timer og faktor 1,5 som scenarioforutsetninger; behold forenklet kostnadsmodell. | PRD §4.3 og kostnadsvisning | Høy konfidens i at tallene ikke er universelle lovregler. [1] [4] [5] |
| Behold ikke-unikhetsforbeholdet; nyanser hva eksisterende verktøy allerede tilbyr. | Brief: Hva gjør dette annerledes | Middels konfidens; dokumenterte tilbud, ukjent aktuell praktisk kvalitet. [7] [11] [12] |
| Dokumenter skalaer, likhetstilfeller, sekundærsortering og følsomhet for vekter/kandidatsett. | PRD §4.4; tester for story 4.1 | Metodegrunnlag og direkte beregning, ikke beslutning om nye vekter. [13] [14] [18] |
| Skill mislykket preferansetolkning fra feil i forklaringstekst; definer merket feiltilstand/videre flyt. | PRD §4.5; arkitekturport; story 5.1 | Produktutledning: rangeringen trenger gyldig input selv om forklaring kan erstattes av reservetekst. |
| Legg til oppgavebasert forståelsespilot, nye preferansetekster og positive regelkontroller. | Brief: Suksesskriterier; testplan og KI-logg | Avgrensede studier og testmetode, ikke et løfte om målt produktnytte. [15] [16] [17] |

## Regler og kandidatbegreper

**Verifisert, høy konfidens:** Hovedregelen er 11 sammenhengende timer arbeidsfri i 24 timer og 35 i sju dager. Det finnes avtale- og særunntak; de to tallene er ikke en komplett lovlighetskontroll. Lovtekst og uavhengig fagforeningsveiledning støtter denne avgrensningen. [1] [2] [3]

**Verifisert, høy konfidens:** 36 timer er knyttet til bestemte arbeidstidsordninger, ikke en generell norsk normaluke. Lovens minste overtidstillegg er 40 prosent; 150 prosent samlet betaling er en valgt sats dersom prototypen bruker den. Det gir grunnlag for å merke PRD-ens 36 timer og faktor 1,5 som demonstrasjonsforutsetninger. Ingen konkret tariffavtale eller full betalingsrett for deltidsansatte er vurdert her. [1] [4] [5]

**Egen produktutledning, ikke et nytt lovkrav:** Skill følgende begreper i briefen og grensesnittet. Lov- og veiledningskildene skiller arbeidstidsrammer, arbeidsplan og betingelser for ekstraarbeid; de etablerer ikke automatisk at en person kan eller vil arbeide en konkret ny vakt. [1] [5] [6]

| Begrep | Presis betydning i prototypen |
|---|---|
| Modellgyldig kandidat | Oppfyller de fire implementerte kravene med tilgjengelige testdata. |
| Kollisjonsfri | Ingen overlapp i registrerte vakter; ikke synonymt med kontrollert hvile eller faktisk tilgjengelighet. |
| Tilgjengelighet | Praktisk mulighet til å arbeide vakten; kan være en eksplisitt forutsetning i fiktive data. |
| Avklart vakt | Tildelingen er avklart i den valgte arbeidsflyten; generell preferanse og rangering er ikke en slik avklaring. |
| Merarbeid / overtid | Ulike arbeidstidsbegreper; betegnelsen «ekstravakt» bestemmer ikke alene betaling. |

Ikke skriv at alle ekstravakter alltid krever individuelt samtykke. Kildene beskriver adgang til pålegg innenfor vilkår, fritak og særskilte krav ved utvidet overtid. Briefens krav om menneskelig sluttbeslutning kan beholdes som produktkrav uten en slik universell juridisk påstand. [1] [5]

**Uavklart:** De leste kildene bestemmer ikke prototypens presise ankerpunkt for 24-timers- og sjudagersperioder. Ikke utled verken kalenderuke eller enhver rullerende 168-timersperiode uten videre. Før hvilekontrollen implementeres, må valgt modell, nødvendig nabodata og behandling av manglende datadekning spesifiseres. Dette er en åpen modellbeslutning, forskjellig fra definisjonen av kostnadsuken.

## Eksisterende verktøy og særpreg

**Middels konfidens; leverandørdokumentasjon, faktisk funksjon uverifisert:** Planday beskriver filtrerte og rangerte kandidatforslag med en kort begrunnelse per kandidat. En produktoppdatering omtaler funksjonen som beta våren 2026. Hjelpesiden fra juli er eldre enn researchens tremånedersvindu; en målrettet andre runde fant ingen ferskere bekreftelse eller uavhengig brukertest innen budsjettet. Funksjonen er dokumentert som tilbud, men dagens utrulling og kvalitet er ikke kontrollert. [7] [8]

| Produkt | Dokumentert i undersøkte kilder | Hva dette ikke dokumenterer |
|---|---|---|
| Planday | Kandidatforslag, rangeringsvalg og begrunnelsesnoter; egne hjelpesider beskriver ferdighetskrav og lønnskostnad i planen. [7] [9] [10] | At generativ KI tolker ansattes fritekst, at norske tariffregler dekkes komplett, eller at kostnad brukes i den beskrevne kandidatrangeringen. |
| Quinyx | Relevanssortering med tilgjengelighet og ferdigheter; synlige kandidatopplysninger. [11] | Målt forståelse eller korrekthet, og en full sammenligning av alle regel-/kostnadsfunksjoner. |
| Gat | Offentlig produktside beskriver søknader på ledige vakter og registrering av tilgjengelighet. [12] | Oppdatert ledervisning, kandidatrangering eller forklaringsfunksjon; funksjoner som ikke er avklart her kan fortsatt finnes. |

Briefen sier allerede at teknologien ikke er unik. Behold dette. Nyanser likevel fremstillingen av «en enkel digital turnusløsning»: observerte tilbud går lenger enn bare å vise ledige personer. Et egnet særpreg for emneprosjektet er **avgrenset omfang og dokumentert etterprøvbarhet**, formulert som ambisjon til tester og demonstrasjon foreligger. Det er en anbefalt prosjektposisjonering, ikke et bevist konkurransefortrinn.

Plandays tilgjengelighetstekst har en uløst uklarhet: den omtaler både eksplisitt tilgjengelige ansatte og utilgjengelighet som advarsel. Kontotest eller leverandøravklaring trengs før dette brukes som en presis produktforskjell. Ingen av de undersøkte sidene gir her grunnlag for markedstall, dokumentert tidsbesparelse eller påstand om at brukerne foretrekker prototypen.

## Rangering, preferansetolkning og nytte

**Middels konfidens, offentlig metodegrunnlag:** MCDA-veiledning knytter vekter til kriterienes skala og spenn, og anbefaler sensitivitetsanalyse. En eldre offentlig manual støtter samme metode, men kommer ikke fra en helt uavhengig publisist. Ingen lest kilde fastsetter passende kostnads-, belastnings- og preferansevekter for dette prosjektet. Original metodeforskning viser også at normaliseringsvalg kan endre rekkefølger; den brukes ikke her som bevis for at alle additive modeller er ustabile. [13] [14] [18]

### Et etterprøvbart regneeksempel fra PRD-modellen

Dette er en egen beregning med syntetiske tall, ikke en observert brukereffekt eller et eksempel hentet fra forskningen. PRD §4.4 bruker kandidatrelativ min–maks-skala for kostnad og arbeidsbelastning. For lavest-er-best-faktorene er poengene `100 × (maks − verdi) / (maks − min)`. Totalscoren er `0,40 × kostnadspoeng + 0,35 × belastningspoeng + 0,25 × preferansepoeng`.

| Kandidat | Vaktkostnad, kr | Eksisterende timer | Preferansepoeng | Total med A/B | Total med A/B/C |
|---|---:|---:|---:|---:|---:|
| A | 1 000 | 8 | 50 | 52,5 | 52,5 |
| B | 1 200 | 0 | 50 | 47,5 | 83,5 |
| C | 3 000 | 0 | 0 | Ikke med | 35,0 |

Med A/B får B null kostnadspoeng. Når C legges til, får B 90 kostnadspoeng og går foran A, selv om A og B er uendret og C rangeres sist. Regnestykket er kontrollert direkte med JavaScript. Dette bryter ikke determinismen: kandidatsettet er endret. Det viser at «40 % kostnad» avhenger av spennet blant kandidatene. Enten aksepterer og forklarer dere dette, eller dere begrunner faste skalaankre. Researchen velger ikke automatisk en ny modell. Definer også særtilfellet `maks = min` og stabil sortering ved lik totalscore.

### Forklaringer må prøves mot en oppgave

**Kildekontrollert gjengivelse av originalresultater; uavhengig replikasjon og bemanningseffekt uverifisert:** Bansal mfl. fant ingen signifikant forbedring i nøyaktighet i forklaringsbetingelsene sammenlignet med referansebetingelsen med KI-anbefaling og modellkonfidens. Forklaringer økte også aksept av feil råd i de undersøkte betingelsene. Vasconcelos mfl. fant derimot at forklaringer kunne redusere overdreven tiltro når de gjorde kontrollen enklere i labyrintoppgaver. Resultatene støtter verken «forklaringer virker alltid» eller «forklaringer hjelper aldri». Ingen av studiene undersøkte denne norske bemanningsoppgaven. [15] [16]

**Eget forslag til pilot:** La noen personer med relevant oppgavekunnskap velge kandidat og forklare forskjellen mellom to kandidater, først med en kriterietabell og i matchede oppgaver med forklaring i tillegg. Varier rekkefølgen. Bruk forhåndsdefinert fasit for faktaspørsmål, skill «gyldig» fra «høyt rangert», og ta med en bevisst feil i et separat, kontrollert testmateriale. Registrer korrekt forståelse, oppdagede feil og tidsbruk; spør om opplevd tillit separat. En liten pilot kan avdekke misforståelser, men dokumenterer ikke generell tidsbesparelse. Medstudenter uten domeneerfaring må omtales som proxybrukere.

**Middels konfidens, original metodeartikkel:** CheckList beskriver minimumstester, etikettbevarende endringer og tester av forventet retning/relasjon i modellsvaret. Dette er et nyttig grunnlag for en separat prøve av preferansetolkningen. [17] Foreslått anvendelse: skriv nye syntetiske norske tekster med negasjon, betingelser, tidsavgrensning og motstrid; merk fasiten før modellsvaret ses; hold tekstene utenfor promptutviklingen. Test også parafraser og minimalpar. Oppgi feil per kategori og ugyldige svar. Kilden fastsetter ikke et tilstrekkelig utvalg for dette prosjektet, og de 15 kjente fasittekstene alene dokumenterer ikke kvalitet på nye tekster.

## Hva funnene samlet betyr

En kandidat kan være deterministisk rangert og godt forklart, men fremdeles bygge på en feil eller utdatert preferansetolkning. Det er en analytisk følge av arbeidsdelingen: kvaliteten i hvert ledd må undersøkes separat. Regeltester, klassifikasjonstest og forståelsespilot kan ikke erstatte hverandre.

Sammenligningen av verktøy og forklaringsforskning peker også i samme retning: det er mer etterprøvbart å vise **hva brukeren faktisk kan kontrollere** enn å hevde at forklaringer alene skaper tillit eller nytte. Det er en prosjektanbefaling, ikke en målt konkurransefordel. [7] [11] [15] [16]

Motstridende evidens er beholdt: forklaringsstudiene har ulike betingelser og utfall; den mulige nytten avhenger blant annet av kontrollkostnad. Lovveiledningens forenklinger er ikke hele unntakskatalogen. Leverandørdokumentasjon inneholder en uløst tilgjengelighetsuklarhet. Det ble ikke kjørt en ekstra red-team-runde utover den godkjente normale kildekontrollen.

## Åpne spørsmål og hva som avgjør dem

- **Faktisk brukerbehov og forståelse:** krever domeneintervju og lokal oppgaveprøving. Offentlig produktdokumentasjon kan ikke validere gruppens brukerhypotese.
- **Hvilemodellens perioder og datadekning:** må fastsettes før implementering, med domeneavklaring og grensetester. Denne kjøringen har ikke avgjort ankerpunktene.
- **Vektene og relativ normalisering:** gruppen må velge hvilke avveininger prototypen skal demonstrere. Regneeksemplet er et beslutningsgrunnlag, ikke en automatisk feilretting.
- **Eksakte konkurrentforskjeller:** krever ferskere dokumentasjon eller kontotest dersom det blir et faktisk produktposisjoneringsspørsmål. Det er ikke nødvendig for å fullføre skoleprototypen.

## Kilder

Alle kilder er hentet i denne kjøringen og lest 2026-10-26. Ukjent dato betyr at publiserings-/oppdateringsdato ikke var oppgitt i lest materiale. Lovens vedtaksdato og sidens crawldato brukes ikke som ferskhetsbevis. Publisister kan være uavhengige uten at de undersøker samme konkrete produktfunksjon; to leverandører som beskriver lignende funksjoner verifiserer derfor ikke hverandres implementasjon.

| Ref | Hva kilden støtter | Publisist og direkte kilde | Publisert/oppdatert | Konfidens i bruk her |
|---|---|---|---|---|
| [1] | Arbeidstid, hvile og vilkår/unntak | [Arbeidstilsynet: arbeidsmiljøloven](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) | Lov 2005-06-17; aktuell nettsidedato ukjent | Høy for kryssjekkede hovedregler, ikke komplett juridisk vurdering |
| [2] | Hovedregler og arbeidstidsordninger | [Arbeidstilsynet: arbeidstid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/) | Ukjent | Høy med uavhengig støtte |
| [3] | Hvile og kompenserende fri | [NSF: fritid og pauser](https://www.nsf.no/arbeidsvilkar/fritid-og-pauser) | Ukjent | Høy for kryssjekkede hovedregler |
| [4] | Ordningsavhengige ukegrenser | [NSF: arbeidstid og vaktordninger](https://www.nsf.no/arbeidsvilkar/dagligukentlig-arbeidstid-og-vaktordninger) | Ukjent | Høy for avgrenset uketidspåstand |
| [5] | Overtid, vilkår og tillegg | [Virke: overtid](https://www.virke.no/arbeidsgiverstotte/arbeidstid-overtid/overtid) | Ukjent | Høy med lovtekst; full merarbeidsbetaling ikke avgjort |
| [6] | Arbeidsplan og endringer | [Arbeidstilsynet: arbeidsplan](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/) | Ukjent | Middels; begrepsgrunnlag |
| [7] | Kandidatforslag og korte begrunnelser | [Planday: How Planday suggests employees for shifts](https://help.planday.com/en/articles/572390-how-planday-suggests-employees-for-shifts) | 2026-07-22 | Middels; aktuell funksjon uverifisert, utenfor tre måneder |
| [8] | Beskrevet kandidatforklaring, beta våren 2026 | [Planday: Product updates winter and spring 2026](https://help.planday.com/en/articles/621960-product-updates-winter-and-spring-2026) | 2026-04-17 | Middels; historisk tilbudsbeskrivelse |
| [9] | Dokumenterte ferdighetskrav | [Planday: Skills](https://help.planday.com/en/articles/30445-how-to-set-up-and-use-skills) | Ukjent; relativ dato | Middels; ingen kontotest |
| [10] | Lønnskostnad i planvisning | [Planday: Payroll costs in the Schedule](https://help.planday.com/en/articles/79054-payroll-costs-in-the-schedule-faqs-and-troubleshooting) | 2026-08-21 | Middels; ingen kostnadsrangering konkludert |
| [11] | Relevanssortering og kandidatopplysninger | [Quinyx: Shifts](https://help.quinyx.com/help-centre/docs/shifts) | Oppdatert 2026-08-06 | Middels; faktisk funksjon uverifisert |
| [12] | Ledige vakter og tilgjengelighet som tilbud | [Visma Enterprise: Gat](https://gatressurs.no/) | Ukjent | Middels; markedsføring, KI-merket FAQ ikke brukt |
| [13] | Vekter, skalaer og sensitivitetsanalyse | [DESNZ/HM Treasury: MCDA guidance](https://www.gov.uk/government/publications/green-book-supplementary-guidance-use-of-multi-criteria-decision-analysis/use-of-multi-criteria-decision-analysis-in-options-appraisal-of-economic-cases) | 2024-06-24 | Middels; metode, ikke bemanningseffekt |
| [14] | Normalisering kan påvirke rekkefølge | [Mohammadi og Rezaei: metodeartikkel, Wiley](https://onlinelibrary.wiley.com/doi/10.1002/mcda.1806) | 2023-03-09 | Middels; fulltekst lest, ikke uavhengig validert metodevalg |
| [15] | Forklaringer og beslutningsnøyaktighet | [Bansal mfl.: Does the Whole Exceed its Parts?](https://arxiv.org/pdf/2006.14779) | CHI 2021; lest v3 2021-01-12 | Høy for avgrenset studie; ukjent overføring |
| [16] | Betinget reduksjon av overdreven tiltro | [Vasconcelos mfl.: Explanations Can Reduce Overreliance](https://arxiv.org/html/2212.06823v2) | CSCW 2023; lest v2 2023-01-26 | Høy for avgrenset studie; ukjent overføring |
| [17] | Funksjonstesting av språkmodeller | [Ribeiro mfl.: Beyond Accuracy, CheckList](https://aclanthology.org/2020.acl-main.442.pdf) | ACL 2020-07 | Middels; original metode, ikke ny klassifikators kvalitet |
| [18] | Swing weighting og sensitivitet | [DCLG: Multi-criteria analysis, a manual](https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf) | 2009-01 | Middels; grunnlagsmetode, ikke uavhengig britisk publisist |

## Ferskhet og sporbarhet

Maskinberegnet fra siste påstand per ref i `.memlog.md`; `claims.json` og `staleness.json` er lagret. Tre hovedpåstander er uavhengig bekreftet; sju er beholdt som uverifiserte etter registerets strengere krav. Dette er ti registrerte nøkkelpåstander, ikke antall kilder eller et mål på produktkvalitet.

| Påstandstype | Kontrollbehov | Neste kontroll |
|---|---|---|
| Planday, datert 2026-07-22 | Tre måneder; vinduet utløp før kjøringen. Ingen ferskere uavhengig bekreftelse ble funnet i runde 2. | 2026-10-22 — allerede forfalt; før en aktuell funksjonspåstand |
| Quinyx, oppdatert 2026-08-06 | Tre måneder for funksjonsbeskrivelse | 2026-11-06 |
| Regler og udaterte sider | Hver juridisk anvendelse; ukjent publiseringsdato kan ikke gi en maskinberegnet frist | Før implementeringsbeslutning eller ny anvendelse |
| Grunnlagsmetode og historiske studier | Ingen automatisk utløpsfrist i dette domenepakken; er ikke påstander om dagens KI-adopsjon | Ny kontroll ved sterkere effekt- eller metodepåstander |

Tidligste beregnede frist er 2026-10-22 og er allerede passert. Verktøyets exit 1 er derfor et forventet ferskhetsfunn, ikke en mislykket kjøring. Grunnlagsmetode uten tidsvindu og fire udaterte registerpåstander er eksplisitt skilt fra datert funksjonsdokumentasjon.

Førsterundene er dokumentert i `digests/regler-r1-1.md`, `digests/verktoy-r1-1.md` og `digests/rangering-r1-1.md`. En målrettet andre verktøyrunde og egne kildekontroller er også lagret der. Regel- og rangeringssporene stoppet ved dekket avgrenset spørsmål; verktøysporet stoppet ved siste runde med friskhets-/funksjonsspørsmål fortsatt åpne. Prosjektfiler er bare brukt til å formulere spørsmål og egne modellberegninger, ikke som eksternt kildebelegg.
