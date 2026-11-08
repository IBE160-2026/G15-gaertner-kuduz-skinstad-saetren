# Turnushjelperen – beslutningsgrunnlag for ferdigstilling av PRD

**Status: Forslag til gruppens behandling. Ingen nye gruppevedtak er registrert.**

Utarbeidet 2026-11-07 etter kontroll av hele arbeidstreets PRD, §§0–9 og FR-1–FR-14. Kontrollen gjelder krav og dokumentsamsvar, ikke implementert funksjonalitet, testresultater eller juridisk etterlevelse. PRD-endringene fra tidligere samme dag er med i kontrollgrunnlaget. Lokal HEAD ved kontrollstart: `a6285ca`.

## 1. Bruk dokumentet i gruppemøtet

For hvert punkt: velg alternativ, skriv begrunnelse og noter hvem som faktisk besluttet det. Et svar fra ett medlem er et individuelt produktvalg inntil vedkommende uttrykkelig oppgir at gruppen har vedtatt det. ID-ene P-01 osv. er bare arbeids-ID-er i dette dokumentet; de erstatter ikke AV-, K-, OP- eller KS-ID-er.

**Synspunkter før møtet:** Hvert punkt har ett felt per medlem. Skriv synspunktet ditt etter navnet ditt i stedet for `__`, også når det bare er «støtter anbefalingen» eller «vil drøfte i møtet». Endre ikke andres felt; svar heller i ditt eget. Synspunktene er individuelle og ikke vedtak. Gruppens beslutning føres i feltet under når punktet er behandlet. Kjør `git pull` før du skriver, siden flere redigerer samme fil.

Anbefalingene er laget for en avgrenset, lokal prototype med fiktive data. De utvider ikke automatisk v1. Gruppen kan også velge en tydelig avgrensning eller utsettelse, med ansvarlig og tidspunkt for ny behandling.

**Foreslått rekkefølge:** P-01–P-04 om beregninger, P-05–P-07 om KI, P-08–P-10 om datagrunnlag og flyt, P-11 om tomtilstand. Ta deretter stilling til avgrensningene P-12/P-13 og dokumentasjonsoppgavene E-01/E-02. P-05 har to delvalg som må besvares hver for seg.

## 2. Dette skal bevares

Følgende er allerede dokumentert, og legges ikke frem som nye valg:

- Fire harde regler og avgrenset prototypemodell: kompetanse, kollisjon, 11 timer før/etter og 35 timer sammenhengende fri i hver berørte kalenderuke (AV-04). Ingen garanti om full juridisk kontroll.
- Kostnad 40 %, timebelastning 20 %, ulempebelastning 15 % og preferanser 25 % (AV-11).
- Min–maks for kostnad/timebelastning; 50 faktorpoeng når alle har lik verdi, også ved én kandidat. Uavrundet beregning/sortering, ansatt-ID stigende ved identisk totalscore, én desimal ved visning av faktorpoeng/totalscore (AV-05, K-03).
- Ulempevindu på 672 faktiske timer, halvåpent intervall, tak 300 og gjeldende 0/1/2/3-modell (AV-09/11). Ingen innstillingsside.
- Opprinnelig ansatt utelukkes. Øvrig tilgjengelighet er en demonstrasjonsantakelse; registrerte preferanser gjelder demonstrasjonsperioden (AV-06).
- Timebelastning gjelder kalenderuken den valgte vakten starter i, uten den vurderte vakten. Dette avgjør ikke fordelingen av timer i vakter som krysser en ukegrense.
- Fem preferansenivåer og de 15 fasittekstene i FR-10. Manglende tekst gir 50 poeng med egen merking. Preferanser utelukker ingen.
- Eksplisitt godkjenning, ny hardregelkontroll før lagring, varig bemanning/godkjenning og avvisning av dobbel godkjenning (FR-12, story 3.2, AD-5).
- Demo uten gruppens nøkkel, synlig kildemerking og ingen stille overgang fra live til demo ved feil (FR-11, AD-6).

36 timer og 150 % sats er eksisterende valg i den forenklede kostnadsmodellen. Forslagene under handler om å gjøre bruken entydig, ikke om å fastsette nye lønns- eller lovregler.

## 3. Produktvalg og presiseringer

### P-01 – Hvilken kostnad skal rangeringen sammenligne?

**Grunnlag:** PRD FR-7/FR-9, §8 punkt 3; story 4.3/4.4. Fortsatt åpent. Forslaget i chatten er ikke bekreftet.

**Problemet:** «Lavest kostnad» kan bety tre ulike ting. Valget kan endre hvem som får best kostnadspoeng.

| Alternativ | Hva sammenlignes? | Konsekvens |
| --- | --- | --- |
| A – anbefalt | Økningen i modellberegnet lønnskostnad når vakten legges til | Måler hva akkurat denne tildelingen koster ekstra, med ordinære timer og overtid |
| B | Ordinær timelønn | Enkelt, men overser overtiden som vakten utløser |
| C | Samlet kostnad for kandidatens uke etter tildelingen | Tar også med allerede planlagt arbeid og overlapper med hensynet til timebelastning |

**Eksempel:** Åtte timers vakt innenfor én uke. A har 32 timer fra før og 300 kr/t: vaktens merkostnad er `4 × 300 + 4 × 450 = 3 000 kr`. B har 0 timer og 340 kr/t: `8 × 340 = 2 720 kr`. Ordinær timesats favoriserer A; merkostnad favoriserer B. Samlet ukekostnad blir 12 600 mot 2 720 kr. Dette er bare kostnadsfaktoren, ikke totalrangeringen.

**Anbefaling:** A. Definer verdien som forskjellen i modellberegnet kostnad før og etter tildeling, summert over berørte uker. Ikke trekk fra lønn for den opprinnelig oppsatte ansatte; sykepenger og samlet avdelingsøkonomi er utenfor modellen.

**Foreslått kontroll:** 32 eksisterende timer + 8 nye ved 300 kr/t gir 3 000 kr. Ved 40 eksisterende timer gir de 8 nye 3 600 kr.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-02 – Beregningsuke og timer over ukeskiftet

**Grunnlag:** FR-7/FR-8, story 4.1/4.3, AV-03/04. Startuken for timebelastning er fastsatt; timefordelingen og kostnadsuken trenger presisering.

**Problemet:** En nattevakt kan ligge i to kalenderuker. Også eksisterende vakter må telles entydig, ellers kan samme vakt gi ulike overtids- og belastningstall.

| Alternativ | Beregning | Konsekvens |
| --- | --- | --- |
| A – anbefalt | Uke = mandag 00:00 til neste mandag 00:00 i Europe/Oslo. Fordel faktisk arbeidstid på ukene etter overlapp | Samme time tilhører én uke; 36-timersgrensen brukes separat i hver berørt uke |
| B | Hele vakten og dens timer tilordnes uken den starter i | Enklere, men mandagstimer kan belaste forrige uke |
| C | Rullerende syvdagersvindu fra valgt vakts start | Ny periodemodell som avviker fra kalenderuken brukt ellers |

**Eksempel:** Den vedtatte nattevakten søndag 23–mandag 07 har 1 time i første uke og 7 i neste, uten sommertidsskifte. Kandidaten har 36/20 timer fra før og 300 kr/t. A gir `1 × 450 + 7 × 300 = 2 550 kr`; B gir `8 × 450 = 3 600 kr` hvis hele vakten føres i startuken.

**Anbefaling:** A for både eksisterende vakter og den vurderte vakten. FR-8 viser fortsatt bare eksisterende timer i den valgte vaktens startuke; en eksisterende vakt fra forrige søndag bidrar med mandagstimene sine. AV-03s starttidsregel for hvilke vakter som vises, er en annen regel. Beregn varigheter i faktisk forløpt tid, også ved sommertid. Vakter som slutter akkurat ved ukegrensen bidrar ikke i neste uke.

**Foreslått kontroll:** Regn begge berørte uker, test 36 timer nøyaktig, ukeskifte og begge sommertidsovergangene. Dersom C velges, må konsekvenser for øvrige dokumenter avklares uttrykkelig.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-03 – Kostnadsvisning ved blandet ordinær sats og overtid

**Grunnlag:** FR-7 tillater en kombinasjon; story 4.3 og UX-DR10 beskriver bare «Ordinær»/«Overtid» med kr/t. K-03 fastsetter desimaler for poeng, ikke valuta eller timevisning.

**Problemet:** Å vise bare 450 kr/t for en vakt med fire ordinære og fire overtidstimer kan oppfattes som om hele vakten koster dette.

| Alternativ | Visning ved eksemplet i P-01 |
| --- | --- |
| A – anbefalt | «Vaktkostnad 3 000,00 kr», «Inkluderer overtid», og detaljer: 4 t × 300 + 4 t × 450 |
| B | Gjennomsnittlig sats: 375 kr/t, tydelig merket som gjennomsnitt, med fordeling i detaljer |
| C | Bare ordinær eller høyeste anvendte sats, som i dagens enkle indikator |

**Anbefaling:** A sammen med P-01A. Bruk «Ordinær» når ingen nye timer er overtid og «Inkluderer overtid» når noen eller alle er det. Vis beløp med to desimaler, men behold uavrundet grunnlag i rangeringen som K-03 krever. Teknisk avrundingsmetode dokumenteres i relevant story; ikke innfør avrunding av kostnaden før poengberegningen. Hvis gruppen velger B, må total vaktkostnad fortsatt være tilgjengelig.

**Foreslått kontroll:** Beløp, timer og satser skal forklare samme kostnad; ulik visningsavrunding skal ikke endre rekkefølgen.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-04 – Eksakt grense for høy timebelastning (K-02)

**Grunnlag:** FR-8, §8 punkt 6, story 4.2. 32,4 timer er fortsatt bare anbefalt.

| Alternativ | Når bytter indikatoren? | Konsekvens |
| --- | --- | --- |
| A – anbefalt | Ved minst 32,4 timer, altså 32 t 24 min og nøyaktig 90 % | Følger dagens begrunnelse direkte |
| B | Ved minst 32 timer | Enklere heltall, men grensen er omtrent 88,9 % |
| C | Ved minst 33 timer | Enklere heltall, men grensen er omtrent 91,7 % |

**Anbefaling:** A. Sammenlign før visningsavrunding. 32:23 er under og 32:24 på grensen. Ved 40 timer er faktisk prosent omtrent 111,1 %, selv om selve linjen stopper ved full bredde. Vis nok presisjon nær grensen til å unngå at samme viste timetall virker å gi tilfeldig fargeskifte. Dette er ingen hard regel og endrer ingen rangeringspoeng.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-05 – Registrert preferanse som ikke kan tolkes (OP-03)

**Grunnlag:** FR-10, §8 punkt 4, stories 5.1/5.2 og AD-6. Avklares før story 5.1/5.2 er ferdige. Manglende tekst og tolkningsfeil er ulike tilstander.

**Delvalg 1 – poeng og videre bruk:**

| Alternativ | Resultat ved feil | Konsekvens |
| --- | --- | --- |
| A – anbefalt | 50 midlertidige preferansepoeng, egen feilmerking; rangering og manuelt valg er tilgjengelig | Flyten fortsetter, men usikkerheten er synlig |
| B | Sett hele rangeringen på vent til alle registrerte preferanser er tolket | Ingen foreløpig rangering, men én feil kan stoppe hele oppgaven |
| C | 0 poeng med feilmerking | Flyten fortsetter, men en teknisk feil behandles som et negativt ønske |

**Anbefaling:** A, med teksten «Preferanse kunne ikke tolkes – midlertidig 50 poeng». Behold råtekst og feilstatus; ikke lagre en oppdiktet «nøytral» KI-tolkning. Forklaringen må ikke hevde at personen er fleksibel eller mangler registrering. A er et kompromiss: En faktisk 0-preferanse ville få 12,5 flere totalpoeng ved fallback 50; en faktisk 100-preferanse ville få 12,5 færre. Brukeren må derfor se at rangeringen kan endres. Kandidaten skal ikke utelukkes som ugyldig bare på grunn av KI-feilen.

Samme regel foreslås mens registrert tekst fortsatt venter på første tolkning, med merking «Preferanse venter på tolkning – midlertidig 50 poeng». En gyldig kategori kan også være semantisk feil selv om JSON-formatet er riktig. Fasittekstene skal kontrolleres, og en oppdaget feil skal merkes som ugyldig tolkning og følge valgt feilflyt; det foreslås ingen garanti om automatisk oppdagelse av enhver feiltolkning av vilkårlig tekst. Ved P-10A kan retting skje i forberedelsen av testdata, uten et nytt redigeringsskjema i appen.

**Delvalg 2 – hvordan komme videre:**

| Alternativ | Videre håndtering |
| --- | --- |
| A – anbefalt | Avgrensede automatiske nye forsøk etter AD-7 ved forbigående feil; etter endelig feil kan brukeren be om nytt forsøk. Vellykket tolkning gir oppdatert rangering før videre bekreftelse |
| B | Ingen ny brukerhandling i v1; feilen står til neste innlasting/forberedelse av testdata |
| C | Turnusansvarlig velger preferansekategori manuelt i appen |

**Anbefaling:** A. Dette er en foreslått utvidelse av dagens storytekst, ikke allerede implementert. Ikke prøv permanent ugyldige svar kontinuerlig på nytt. Ikke bruk gammel tolkning for en endret tekst. Ukjent tekst i demo må også merkes som manglende tolkning, ikke «Ingen registrert». Eventuell manuell kategori i C krever regler for redigering, kilde og lagring og bør ses sammen med P-10.

**Foreslått kontroll:** Skill manglende tekst, vellykket nøytral tolkning og tolkningsfeil. Test ny vellykket tolkning, endret tekst og feilet nytt forsøk. Vellykket lagret tolkning gjenbrukes; rangeringen gjør ikke nye KI-kall.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen for begge delvalg.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Delvalg 1: __. Delvalg 2: __. Begrunnelse: __. Dato/deltakere: __.

### P-06 – Faktakontroll av KI-forklaringer

**Grunnlag:** FR-11, SM-2/SM-C2, §8 punkt 5, story 5.4 og K-04. Eksisterende krav forbyr feil grunnlag, men metoden for å kontrollere fri tekst er ikke fastsatt.

| Alternativ | Kontroll | Begrensning |
| --- | --- | --- |
| A – anbefalt | KI returnerer strukturerte begrunnelser fra et avgrenset sett. Koden validerer referanser og retning og setter inn beregnede navn, tall og sammenligninger i tekstmaler | Mindre språklig frihet; begrunnelsestypene må defineres |
| B | Fri KI-tekst med kontroll av navn, tall og enkelte mønstre | Kan overse feil mening selv om tallene finnes i grunnlaget |
| C | Fri tekst kontrolleres av et nytt KI-kall | Ekstra ventetid/kostnad og fortsatt ingen sikker fasit |

**Anbefaling:** A. KI kan foreslå hvilke avveininger som er relevante, men kan ikke levere nye tall, endre rangeringen eller velge kandidater utenfor godkjent input. Hvis ett påstandsfelt ikke kan valideres, forkastes hele forklaringen og den eksisterende reserveveien brukes. Rangeringen og godkjenningen skal fortsatt fungere med beregnede fakta (story 5.4).

**Eksempel:** Beregnet kostnad er 3 000 kr. Modellen får ikke gjøre dette til 2 400 kr. En begrunnelse «lavere kostnad enn kandidat B» godtas bare hvis sammenligningen faktisk er sann i beregnet grunnlag. «Like poeng» må bygge på uavrundet verdi, ikke bare samme viste desimal.

**Foreslått kontroll:** Feil beløp, ukjent kandidat, feil preferanse, omvendt sammenligning og feil rangeringspåstand gir reservetekst. Test både live- og demoveien. Manuell språk-/forståelseskontroll kommer i tillegg; struktur alene beviser ikke god forklaring.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Det må synliggjøres på en enkel måte for turnusansvarlig når KI-forklaringen ikke besto faktakontrollen og reserveteksten vises i stedet
- Kim: Jeg støtter denne anbefalingen og Johannes’ presisering om tydelig merking når reserveteksten vises.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-07 – Hva skal forklaringen kunne sammenligne? (K-04)

**Grunnlag:** UJ-1 og FR-11 lover avveininger mellom kandidater. AD-1 beskriver én RangertKandidat, mens story 4.4 også har ulempefelt som ikke finnes i AD-1s minimumsliste. Dette må samordnes.

| Alternativ | Input og forklaring | Konsekvens |
| --- | --- | --- |
| A – anbefalt | Kandidatens fakta og forhåndsberegnede sammenligninger med én angitt gyldig referansekandidat | Gir konkrete avveininger med lite input og kontrollerbar fasit |
| B | Alle gyldige kandidaters beregnede fakta i hvert forklaringskall | Mer kontekst og større kontrakt; KI må fortsatt ikke regne eller rangere |
| C | Bare kandidatens egne nøkkeltall; ingen påstander om andre kandidater | Enklest, men krever at løftet om sammenlignende forklaringer i UJ-1/FR-11 justeres |

**Anbefaling:** A sammen med P-06A. Foreslått referanse: nr. 2 for den topprangerte, og nr. 1 for øvrige kandidater. Ved én kandidat gis ingen sammenligning. Koden beregner forskjeller og veide faktorbidrag; KI formidler dem. Referansen velges blant alle gyldige, før visning begrenses til fem.

**Foreslått kontraktsinnhold:** Kandidat-/vaktreferanse, datagrunnlagets identitet, kostnadsverdi og ordinær/overtidsfordeling, eksisterende uketimer/prosent, ulempepoeng og fordeling, preferansekategori eller feilstatus, faktorpoeng/veide bidrag, totalscore og plassering. Bare nødvendige felt skal inn i KI-input; eksakt skjema er arkitekturarbeid etter beslutningen. En gyldig kandidat kan ha en utelukkelsesoppsummering i UI-et uten at de utelukkedes identiteter sendes til KI.

**Foreslått kontroll:** Ingen referanse til utelukkede, ingen referansekandidat ved én gyldig, og ingen påstand om hvorfor en kandidat vinner som motsier de veide bidragene. Portene i AD-1, story 4.4, 4.7 og 5.3/5.6 må beskrive samme grunnlag.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Kan det være hensiktsmessig med en funksjonalitet: **hvis** turnusansvarlig ønsker det, utfør en sammenligning av merkede kandidater, for eksempel rangert nummer 2 og rangert nummer 3. Sammenligningen utføres kun på forespørsel, normalt er sammenligningen gjort med rangert kandidat nummer 1.
- Kim: Jeg støtter denne anbefalingen. Johannes’ forslag om valgfri sammenligning kan kanskje vurderes etter v1 eller etter kjerneflyten fungerer i v1?
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg/referanseregel: __. Begrunnelse: __. Dato/deltakere: __.

### P-08 – Ufullstendig eller ugyldig datagrunnlag

**Grunnlag:** FR-2–FR-9/FR-14, AV-04, KS-04 og story 2.1/2.4. Story 2.1 har allerede utelukkelse ved manglende kandidatkompetanse. KS-04 er godkjent for dokumenterte seedscenarioer, med kjent begrensning etter 05.10.

**Problemet:** Ingen registrert vakt kan bety enten dokumentert fri eller manglende historikk. Manglende lønn er heller ikke null kostnad. PRD sier ikke samlet hvordan brukeren skal møte slike feil.

| Alternativ | Atferd |
| --- | --- |
| A – anbefalt | Ufullstendig nødvendig beregningsgrunnlag stopper vurderingen med en egen datafeil; ingen godkjenning på dette grunnlaget |
| B | Vis en delvis liste med utelatte kandidater og tydelig varsel om at grunnlaget er ufullstendig |
| C | Anta at manglende vakter betyr fri og at manglende tall er null |

**Anbefaling:** A for ukjent dekning, manglende vaktkrav, ugyldige tidspunkt eller manglende kostnadsgrunnlag. Bevar story 2.1s særregel for manglende kandidatkompetanse; den skal ikke forveksles med manglende kompetansekrav på selve vakten. Dokumentert komplett periode uten vakter gir derimot 0 timer/ulempepoeng og er ikke en feil. Foretrukket tekst: «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.» Dette er forskjellig fra «Ingen gyldige kandidater».

Den allerede godkjente begrensningen i KS-04 skal ikke oppheves i dette dokumentet. Ved valg av A må gruppen uttrykkelig bestemme om den begrensede periodekanten skal være utilgjengelig for ny vurdering, eller godta et synlig, avgrenset unntak for demonstrasjonen. Dekningsmetadata/validering kan løses i arkitektur/story; det foreslås ingen generator eller ny hard arbeidsregel.

**Foreslått kontroll:** Manglende historikk gir ikke 0 ulempepoeng; manglende lønn gir ikke gratis vakt; feiltilstand gir ikke godkjenningsknapp. Test den vedtatte håndteringen av den kjente periodekanten særskilt.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Vi må nødvendigvis starte vår turnus på en gitt dato. Komplikasjonen er reell og virkelighetsnær. Anbefaler at vi godtar et synlig avgrenset unntak for demonstrasjonen, alternativt kan KS-04 justeres hvis det er et konkret behov.
- Kim: Jeg støtter denne anbefalingen og Johannes’ synspunkt om et synlig, avgrenset unntak for demonstrasjonen, med justering av KS-04 hvis det er et konkret behov.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg og håndtering av kjent KS-04-begrensning: __. Begrunnelse: __. Dato/deltakere: __.

### P-09 – Gamle svar og endrede data før godkjenning

**Grunnlag:** FR-1/FR-11/FR-12. Ny hardregelkontroll og dublettvern er allerede krav. AD-6 beskytter forhåndsgenererte forklaringer med hash, men avgjør ikke hele brukerflyten ved endrede myke faktorer.

**Problemet:** Et KI-svar for vakt A kan ankomme etter at brukeren har valgt vakt B. Kostnad eller preferanse kan også endres mens kandidaten fortsatt er gyldig etter de harde reglene.

| Alternativ | Ved endret beslutningsgrunnlag før endelig lagring |
| --- | --- |
| A – anbefalt | Vis oppdaterte beregninger og krev ny bekreftelse før lagring |
| B | Kjør de harde reglene på nytt og lagre hvis kandidaten er gyldig, selv om tidligere viste myke faktorer er endret |
| C | Lås hele vurderingsgrunnlaget fra visning til godkjenning |

**Anbefaling:** A. Uansett valg skal svar for en annen valgt vakt/kandidat aldri vises i den aktive vurderingen. Hashbeskyttelsen i demo videreføres. Teknisk dataversjon, transaksjon og forespørselsidentitet velges i arkitektur/story; de er ikke allerede vedtatte PRD-krav. Ved ny vellykket preferansetolkning etter P-05 skal brukeren se det oppdaterte grunnlaget.

**Eksempel:** Kandidaten er fortsatt gyldig, men kostnaden har økt fra 2 720 til 3 400 kr. A viser endringen og ber om ny bekreftelse; B kan gjennomføre et valg basert på et beløp brukeren ikke har sett.

**Foreslått kontroll:** Forsinket svar fra vakt A erstatter aldri B. Endret kostnad eller preferanse utløser valgt atferd. Endret hardregelgyldighet gir fortsatt ingen lagring etter eksisterende FR-12.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen
- Kim: Jeg støtter denne anbefalingen
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-10 – Skal preferanser kunne redigeres i appen? (ÅB-4)

**Grunnlag:** PRD §2.2 sier turnusansvarlig eller testdata. Epics ÅB-4 er åpen; midlertidig løsning er forhåndsdefinerte preferanser, uten redigeringsskjema. AV-06 avgjør gyldighetsperioden, ikke redigering.

| Alternativ | Omfang |
| --- | --- |
| A – anbefalt | Bare faste preferanser i testdata i v1 |
| B | Turnusansvarlig kan redigere preferansetekst i appen |
| C | Turnusansvarlig kan også overstyre tolket kategori manuelt |

**Anbefaling:** A. Gjør dagens midlertidige avgrensning eksplisitt; behold KI-tolkning som funksjon. B/C krever ny brukerflyt, lagring, tilgangskontroll og ugyldiggjøring av gammel tolkning/forklaring. Nye forsøk på samme tekst etter P-05 er ikke et redigeringsskjema.

**Foreslått kontroll:** PRD og epics lover samme registreringsmulighet. Hvis B/C velges, opprettes egne akseptkrav og stories før implementasjon.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Alternativ B settes som et stretch-goal til v1. ikke noe vi er avhengig av for å lykkes med applikasjonen, men vi tilstreber en arkitektur som muliggjør en implementasjon på fornuftig vis
- Kim: Jeg støtter denne anbefalingen og Johannes’ forslag om alternativ B som et mulig tillegg i v1.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-11 – Når ingen kandidater er gyldige

**Grunnlag:** FR-6 og §8 punkt 2. Story 2.6/UX-DR16 har allerede et tekstforslag og krever fortsatt utelukkelsesoppsummering; ingen funksjon for å dele opp vakten.

| Alternativ | Ordlyd og presentasjon |
| --- | --- |
| A – anbefalt | «Ingen gyldige kandidater for denne vakten.» Under: «Alle vurderte ansatte er utelukket av én eller flere av de fire reglene i prototypen. Se årsakene nedenfor.» Behold utelukkelsesboksen og vei tilbake til vaktoversikten |
| B | Behold eksisterende tekst fra story 2.6: «Ingen gyldige kandidater for denne vakten. Dette er ikke en feil eller en lastefeil — regelmotoren har kjørt ferdig og funnet null treff.» |
| C | Bare overskrift og vei tilbake; utelukkelsesdetaljer åpnes ved behov |

**Anbefaling:** A. Det forklarer resultatet med produktets begreper og uten å påstå at ingen i virkeligheten kan ta vakten. Bruk eksisterende tomtilstandsutforming, men vis resultatet med tekst slik at farge alene ikke bærer betydningen. Ingen godkjenningshandling, automatisk svekking av regler eller nye «del opp vakten»-knapper. Datafeil fra P-08 og KI-feil fra P-05/P-06 skal ha andre meldinger.

**Foreslått kontroll:** #4189 gir riktig tomtilstand og årsaker; lasting og datafeil gir andre tilstander. I oppsummeringen telles en ansatt én gang totalt og kan telles under flere bruddårsaker, som story 2.5 allerede sier.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Legg til i tekstvisningen at innleie av personell kan vurderes når ingen av de vurderte ansatte er gyldige
- Kim: Jeg støtter denne anbefalingen og Johannes’ tillegg om at innleie av personell kan vurderes.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg/justert tekst: __. Begrunnelse: __. Dato/deltakere: __.

## 4. Avgrensninger som bør gjøres uttrykkelige

Disse punktene er ikke nye obligatoriske funksjoner. En eksplisitt utsettelse kan være tilstrekkelig for en ferdig PRD.

### P-12 – Skal vist forklaring lagres ved godkjenning?

**Grunnlag:** Arkitekturens Deferred og story 5.3. Dagens beskrivelse lagrer godkjenningen, men ikke forklaringen; en mulig senere låsing er åpen.

| Alternativ | Resultat |
| --- | --- |
| A – anbefalt for v1 | Behold dagens omfang: varig godkjenning, men ingen historisk forklaringslogg i produktet |
| B | Lagre vist forklaring og beregningsgrunnlag sammen med godkjenningen |
| C | Lagre bare beregningsgrunnlaget og kilde, og lag eventuell forklaring på nytt |

**Anbefaling:** A som eksplisitt avgrensning. B/C gir mer etterprøvbarhet i selve appen, men krever nye lagrings-/visningskrav. Prosessloggene i repoet dokumenterer utviklingsarbeidet og erstatter ikke en historikkfunksjon i produktet. Hvis A velges, må PRD ikke love at den nøyaktige teksten bak et tidligere valg kan hentes frem senere.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen. Kommentar: Alternativ B settes som et stretch-goal til v1.
- Kim: Jeg støtter denne anbefalingen og Johannes’ forslag om alternativ B som et mulig tillegg i v1.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg: __. Begrunnelse: __. Dato/deltakere: __.

### P-13 – Hvilket UX-omfang skal være bindende nå?

**Grunnlag:** ÅB-7, OP-02, UX-DR24/25 og story 4.6. AV-13/14 fastsetter designtokens og maksimal innholdsbredde; mobilstabling og brukerprøving er fortsatt utsatt.

| Alternativ | Omfang |
| --- | --- |
| A – anbefalt nå | Behold desktop og eksisterende tilgjengelighetsgulv. Avklar mobil/nettbrett etter fungerende kandidatvisning, før story 4.6 ferdigstilles |
| B | Bekreft nå desktop-tabell, nettbrett-rader og mobilkort som i UX-forslaget; eksakte breakpoints tas i story 4.6 |
| C | Ta mobil/nettbrett helt ut av v1 |

**Anbefaling:** A i tråd med OP-02; PRD kan være ferdig med en eksplisitt utsatt detalj og tidspunkt for behandling. C krever uttrykkelig endring av planlagt scope. Tastaturbetjening, lesbar tekst og forståelige statuser er allerede beskrevet i UX/stories og skal ikke omgjøres til valgfrie tillegg.

**Forslag ellers:** Gjennomfør en liten oppgavebasert forståelsestest når kandidatflaten virker: be en person forklare hvorfor nr. 1 rangeres høyest, finne en annen gyldig kandidat og skille datafeil fra null gyldige. Dette er foreslått kvalitetssikring, ikke gjennomført brukervalidering eller et nytt emnekrav. Fastsett deltakere og akseptmål før testen hvis den vedtas.

**Synspunkter før møtet:**

- Johannes: Jeg støtter denne anbefalingen.
- Kim: Jeg støtter denne anbefalingen og forslaget om en oppgavebasert forståelsestest når kandidatvisningen fungerer.
- Mithad: __
- Ragnhild: __

**Gruppens beslutning:** Ikke behandlet. Valg, ansvarlig og behandlingstidspunkt: __. Eventuell forståelsestest: __. Begrunnelse: __. Dato/deltakere: __.

## 5. Spørsmål som krever dokumentasjon

### E-01 – Er KI i produktet et emnekrav?

**Status:** Lukket 2026-11-08. Faglærer har uttalt i forelesning at KI i produktet ikke er et formelt emnekrav. Utfallet er «valgfritt» i listen under: KI beholdes som valgt produktscope. Kilden er Johannes' gjengivelse av en muntlig uttalelse; forelesningens dato er ikke notert.

Addendum §5 tolker emnet som KI-assistert utvikling og omtaler KI i produktet som et produktvalg, men ber uttrykkelig om bekreftelse fra faglærer. PRD §8 sier at tilbakemeldingen fra 06.10 roser KI/regelmotor-skillet uten å besvare spørsmålet eksplisitt. Sensorveiledningen vektlegger prosess og vurdering opp mot godkjent proposal. Ingen av disse opplysningene er dokumentert svar på selve spørsmålet.

**Mulige utfall etter dokumentert svar:**

- KI i produktet er et krav: noter kilde, dato og hva som faktisk kreves.
- KI i produktet er valgfritt: noter kilde og behold KI som valgt produktscope, med mindre gruppen beslutter en egen scopeendring.
- Svaret finnes ikke eller er uklart: la punktet stå åpent og be faglærer skriftlig avklare det.

**Anbefaling:** Finn en eksisterende skriftlig avklaring eller spør: «Krever IBE160 at selve applikasjonen bruker generativ KI, eller gjelder kravet at KI brukes og dokumenteres i utviklingsprosessen?» Dokumenter svar og kilde. Ingen melding er sendt gjennom dette arbeidet. KI beholdes i gjeldende produktscope uansett; et svar om emnekravet fjerner ikke eksisterende produktkrav automatisk.

**Synspunkter før møtet:**

- Johannes: KI i produktet er ikke et formelt krav i emnet, men de aller fleste av applikasjonene er planlagt med en implementasjon av KI i en eller annen form. Sannsynligvis fordi det er "inn i tiden". Dette ble uttalt i forelesning av faglærer. Dette punktet kan lukkes
- Kim: Jeg slutter meg til Johannes’ kommentar.
- Mithad: __
- Ragnhild: __

**Ansvarlig:** Johannes. **Svar/kilde/dato:** KI i produktet er ikke et formelt krav i emnet; muntlig uttalelse fra faglærer i forelesning, gjengitt av Johannes 2026-11-08. **Status etter møtet:** Lukket av Johannes 2026-11-08 før møtet.

### E-02 – Samsvar med godkjent proposal

**Status:** Må dokumenteres før endelig erklæring om samsvar med emneleveransen. Sensorveiledning §3 og vurderingsmatrisen krever kontroll mot det gruppen faktisk har lovet. Godkjent proposal er ikke identifisert som et selvstendig, godkjent dokument i det kontrollerte grunnlaget.

**Alternativer for oppfølging:**

- A – anbefalt: Finn levert/godkjent versjon og dokumenter dato/kilde. Sammenlign omfanget med PRD og før eventuelle avvik med begrunnelse.
- B: Hvis versjonen ikke kan gjenfinnes, be faglærer bekrefte hvilket grunnlag som ble godkjent. Behold kontrollpunktet åpent til det finnes dokumentasjon.

Ikke anta at dagens produktbrief er identisk med levert proposal. Dersom sammenligningen avdekker konflikt, må gruppen avklare den før den berørte delen av PRD ferdigstilles. Ingen nye avvik er påstått uten denne sammenligningen.

**Synspunkter før møtet:**

- Johannes: Product Brief og PRD er levende dokumenter. Ja, det var en "innlevering" av Product Brief, men status på dokumentet ved innleveringstidspunkt er ikke bindende for produktet som leveres til slutt. Vi forstår at i det virkelige liv er dette kontrakter som er bindende, men dette er et læringscenario. Dette punktet kan lukkes
- Kim: Jeg slutter meg til Johannes’ kommentar.
- Mithad: __
- Ragnhild: __

**Ansvarlig:** __. **Dokument/kilde/dato og resultat:** __.

## 6. Samordning og kontroller etter møtet

Dette er dokumentarbeid eller kvalitetssikring, ikke nye produktvalg. Ikke merk oppgaver som utført bare fordi de står her.

| Punkt | Faktisk avvik eller kontrollbehov | Anbefalt oppfølging |
| --- | --- | --- |
| AV-04 | Epics ÅB-5/6 og stories 2.3/2.4 sier fortsatt åpen/midlertidig | Endre status og henvisning til det allerede vedtatte prototypetolkningsvalget; behold grensekravene |
| AV-06 | Story 2.1 sier utelukkelse av opprinnelig ansatt ikke er uttrykt i PRD | Fjern foreldet antakelsesstatus; PRD har nå kravet |
| AV-12 | FR-9 sier «nesten like», mens vedtaket krever identiske øvrige faktorer for isolert ulempetest | Viderefør vedtaket uttrykkelig i PRD og relevant teststory; ikke endre modellen |
| K-02 / ÅB-3 | «Løst» gjelder hva 90 % er prosent av, ikke eksakt grense | Skill den vedtatte 36-timersnormaluken fra valgt grense etter P-04 |
| ÅB-2 / arkitektur Deferred | Satser/terskel omtales som uavklart i arkitekturen selv om 36/150 er avklart | Rett foreldet status; kostnadsverdi og ukefordeling følges separat i P-01/P-02 |
| Story 4.1 / kostnadsuke | Innledningen sier startuken også brukes for kostnad, mens PRD §8 fortsatt holder dette åpent | Avstem kostnadsdelen etter P-02. Behold allerede fastsatt startuke for FR-8 |
| K-04 | AD-1s minimumsfelt og story 4.4/4.7/5.3 har forskjellig detaljnivå | Samordne kontrakter etter P-06/P-07, uten å hevde at de er implementert |
| OP-03 | Story 5.1 og AD-6 bruker «Ingen registrert» ved tolkningsfeil/ukjent tekst | Samordne feilstatus, poeng, retry og demovei etter P-05 |
| K-06 / PRD-status | PRD har status final, men eksplisitte åpne valg; §8 har også historiske «løst»-overskrifter som kan misforstås | Merk dokumentet som kravgrunnlag med åpne deler frem til behandling; behold historikk og datoer. Samordne §9 med faktiske antakelser |
| AV-11 / tak 300 | PRD sier «foreløpig» om et vedtatt v1-tak | Presiser at 300 er vedtatt verdi; konfigurerbar kodeparameter betyr ikke at produktvalget er åpent |
| Ordlyd og lovlighetsløfter | Brief og visjons-/reiseformuleringer kan leses sterkere enn prototypens fire kontroller | Bruk «oppfyller de fire kontrollerte reglene i prototypen», og behold avgrensningen fra AV-04; ingen ny juridisk modell |
| KS-03 / AV-02 | Kontroll av tidskategorier for fire vakttyper står fortsatt som ikke utført | Gjennomfør og dokumenter før story 4.7 implementeres/tilhørende fasit ferdigstilles. «Åtte timer» må ikke overstyre faktisk tid ved sommertid |
| KS-02/04 | Godkjente kontroller finnes med avgrenset scenario/akseptert begrensning | Behold status og begrensning. Ny kostnads-/tidsfasit etter møtet trenger egen kontroll; dette gjenåpner ikke automatisk gamle godkjenninger |
| FR-3 og story 2.2 | PRD sier bare overlapp; story beskriver halvåpne intervaller og grenseeksempler | Ta inn en kort henvisning/presisering; dette trenger ikke en ny intervallmodell |
| FR-9 | Tilgang til alle gyldige er krav selv om bare fem vises først | Beskriv «Vis alle gyldige kandidater» eller tilsvarende i story/UX. Normaliser over alle gyldige før de fem vises; ingen ny rangering bare av de fem |
| FR-11 / story 5.4/5.5 | Reservevei og progressiv lasting finnes allerede nedstrøms | Gjør sporbarheten tydelig: KI-feil stopper ikke beregnet rangering; transport og eksakt reservetekst kan tas i story, med valgt P-05/P-06 som føring |
| FR-12 / story 3.2 | Ny kontroll, varig lagring og dublettvern er nå i PRD | Bevar kravene. Teknisk transaksjon/låsing og feilkoder tas i story; P-09 gjelder det resterende produktvalget |
| FR-13 / OP-10 | Innloggingsdetaljer er avklart i story 1.3 | Henvis til valgt oppsett; ikke åpne JWT-/passordvalg på nytt gjennom PRD-arbeidet |
| SM-9 / OP-05 | Ren klone er et eksisterende leveransekrav; fysisk macOS/Linux-test er strøket | Behold kravet og gjennomfør ren-klone-kontroll etter gjeldende plan. Ikke gjør dette til forslag om å fjerne kjørbarhet |

**Separat utsatt leveransevalg – ÅB-8:** Sensorens utviklingsnøkkel kontra egen nøkkel og kreditt avgjøres nær innlevering. Alternativene står i epics. Anbefaling: behold utsettelsen og ta valget etter målt forbruk; ikke bland det med E-01. Det er ingen ny blokkering for PRD-ens beregningsmodell.

**Tekniske valg som kan bli i stories/arkitektur:** Klientbibliotek, HTTP-feilkoder, transport for progressiv lasting, skjema/migreringsdetaljer og eksakte breakpoints. De skal ikke alle gjøres til gruppemøtekrav bare fordi de er utsatt. Hosting utover lokal kjøring og full lov-/tariffmodell er utenfor gjeldende v1.

## 7. Hva må være på plass for å kalle PRD-en ferdig?

Kontrollen gir et samlet grunnlag for de kjente avklaringene nå. Den gir ingen garanti mot nye funn under implementasjon. Følgende er foreslått ferdigstillingskriterium for dokumentet:

1. P-01–P-11 har eksplisitte svar, inkludert delvalgene og konsekvensen for kjent datadekning. Utsatte valg har ansvarlig, tidspunkt og en tydelig avgrensning som gjør øvrige krav brukbare.
2. P-12/P-13 har valgt v1-avgrensning eller dokumentert utsettelse.
3. E-01 er enten dokumentert besvart eller synlig åpent med ansvarlig; det skal ikke fremstilles som løst ved fravær av svar. E-02 er kontrollert før gruppen hevder samsvar med godkjent proposal.
4. Faktiske gruppevedtak er registrert med kilde/dato i beslutningsreferatet og deretter innarbeidet i PRD, relevante stories og arkitektur. Individuelle bekreftelser er merket som slike.
5. Samordningslisten er gjennomgått. Hvert funksjonskrav har et entydig forventet resultat; uavklarte tekniske detaljer er plassert i riktig story.
6. Vurderingsmatrise og prosesslogger viser hva som er dokumentert. Implementasjon, kjøring av tester og menneskelig godkjenning føres først når de faktisk er gjort.

Gruppen kan godkjenne PRD som produktkravgrunnlag med en synlig ekstern avklaring i E-01. Den bør da ikke omtales som «alle spørsmål lukket». Et avvik mot proposal i E-02 kan kreve ny behandling.

## 8. Kontrollens dekning og kilder

| PRD-del | Resultat av kontrollen |
| --- | --- |
| §§0–1 formål/visjon | Sammenhengende mål; kontroller sterke lovlighetsformuleringer og proposal-sporbarhet |
| §2 målgruppe/reise | Én brukerrolle og én vakt er tydelig; registrering av preferanser og sammenligningsløftet følges i P-07/P-10 |
| §3 ordliste | Begrepene støtter modellen; kostnadsverdi og periodefordeling må bli entydige etter P-01/P-02 |
| §4.1 / FR-1 | Valg av vakt utløser vurdering; gamle svar håndteres i P-09 |
| §4.2 / FR-2–6 | Fire regler er avklart; datagrunnlag og tomtilstand følger P-08/P-11, intervallgrense har eksisterende storyfasit |
| §4.3 / FR-7/8/14 | P-01–P-04 er de vesentlige beregningsvalgene; ulempemodell og KS-kontroller bevares |
| §4.4 / FR-9 | Vekter, likhet og sortering er avklart; AV-12 og tilgang til øvrige kandidater trenger samordning |
| §4.5 / FR-10/11 | P-05–P-07 og P-09/P-10; demo og kildekrav er allerede beskrevet |
| §4.6 / FR-12 | Hovedflyten er avklart; endrede myke faktorer og lagret forklaring følger P-09/P-12 |
| §4.7 / FR-13 | Innlogging er krav; tekniske detaljer er avklart i story 1.3, ikke nye PRD-valg |
| §§5–6 ikke-mål/MVP | Tydelig avgrensning; P-10/P-12/P-13 må ikke gi stille scopeutvidelse |
| §7 suksesskriterier | Behold målene, skill dem fra gjennomførte tester. Forståelsestest er foreslått i P-13; ingen nye vilkårlige ytelseskrav er lagt til |
| §§8–9 åpne spørsmål/antakelser | Seks kjente spørsmål er dekket, men ÅB-4, feil-/endringstilstander og eksplisitte avgrensninger må også behandles. Historiske vedtak er ikke nye antakelser |

**Sentrale kilder:**

- [Gjeldende PRD](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md) og [PRD-memlog](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/.memlog.md).
- [Gruppevedtak og åpne kontroller](avklaringspunkter.md), særlig AV-03–06/09/11/12, K-02–06, OP-02/03/05 og KS-02–04.
- [Epics](../../_bmad-output/planning-artifacts/epics.md), særlig ÅB-2–8 og stories 2.1–2.6, 3.2, 4.1–4.4/4.7 og 5.1–5.8.
- [Arkitektur](../../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md), særlig AD-1/4–7 og Deferred.
- [Produktbrief](../../product-brief.md) og [briefens addendum](../../_bmad-output/planning-artifacts/briefs/brief-ibe160-turnushjelperen-2026-09-08/addendum.md), særlig §5 om emnekrav.
- [Sensorveiledning](../emne/sensorveiledning-del-1.md) og [vurderingsmatrise](../emne/vurderingsmatrise.md). Matrisen er prosjektets tolkning/status, ikke en ny emneregel.
- [Tidligere PRD-kontroll og videre avklaring](../../.logs/kimsk81/995-2026-10-31-19-18-05-prd-review.md) og [åpne oppfølgingspunkter](../../.logs/kimsk81/issues.md).

Kontrollen omfatter dokumentlesing, to separate agentkontroller, kildeavstemming og kontrollregning av eksemplene. Ingen appkode er endret, ingen live-kall eller apptester er kjørt, og ingen faglærer er kontaktet. Nye valg i dette dokumentet er forslag til møtet.
