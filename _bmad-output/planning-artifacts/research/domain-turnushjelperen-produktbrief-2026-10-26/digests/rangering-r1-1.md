# Rangering, forklaringer og liten evaluering — forskningsdigest r1-1

Dato og accessed for alle kilder: 2026-10-26. Avgrensning: beslutningsstøtte for å foreslå erstatter til én vakt; ingen dokumentasjon av turnusoptimalisering eller effekt i faktisk bemanning. Prosjektfiler er ikke lest eller brukt som evidens. Åtte unike kildearbeider ble inspisert, seks med tilgjengelig fulltekst/metodetekst og to bare via indeksert originalabstrakt. Seks webkall; søket stoppet ved dekning. Ingen sitater er gjengitt.

## Beslutningsnytte

Briefen kan forsvarlig love en etterprøvbar, avgrenset sammenstilling av avveininger, med brukerprøving som gjenstår. Den bør ikke love bedre bemanning, økt kalibrert tillit eller tidsbesparelse som dokumentert effekt. Ingen lest kilde etablerer riktige vekter for dette bruksområdet. 40/35/25 er derfor et mulig testscenario, ikke et forskningsresultat. Dette er en avgrensning av evidensen under, ikke en påstand om at en slik effekt er umulig.

## Påstandsregister

`confidence` gjelder støtte til den avgrensede påstanden, ikke overførbarhet til bemanning. `class` skiller offentlig metode, teoretisk eksempel og empirisk resultat.

### C1 — vekter må tolkes sammen med skala og spenn

- **claim:** Offentlig britisk MCDA-veiledning anbefaler at vekter reflekterer både størrelsen på forbedringen fra dårligste til beste nivå og hvor mye denne forbedringen betyr for beslutningstakerne. Bare å vekte kriterienes navn etter opplevd viktighet er utilstrekkelig. Veiledningen anbefaler følsomhetsanalyse av rangeringen.
- **source URL:** https://www.gov.uk/government/publications/green-book-supplementary-guidance-use-of-multi-criteria-decision-analysis/use-of-multi-criteria-decision-analysis-in-options-appraisal-of-economic-cases
- **publisher:** Department for Energy Security & Net Zero og HM Treasury, GOV.UK.
- **pub_date:** 2024-06-24.
- **accessed:** 2026-10-26.
- **confidence:** Høy for metodeveiledningen; ingen påvist bemanningseffekt.
- **class:** Offentlig metodeveiledning, særlig steg 3–5. Ikke empirisk studie av denne prototypen.

### C2 — normalisering kan endre rekkefølgen

- **claim:** Mohammadi og Rezaei viser numeriske eksempler hvor additiv summering med forskjellige normaliseringer gir forskjellig rangering, og hvor et ekstra alternativ snur rekkefølgen mellom opprinnelige alternativer under sum-normalisering. Dette etablerer en mulighet, ikke at all additiv rangering er ustabil.
- **source URL:** https://onlinelibrary.wiley.com/doi/10.1002/mcda.1806
- **publisher:** Wiley, Journal of Multi-Criteria Decision Analysis.
- **pub_date:** 2023-03-09, først publisert.
- **accessed:** 2026-10-26.
- **confidence:** Høy for de konkrete matematiske eksemplene; begrenset som grunnlag for metodevalg generelt.
- **class:** Original metodeartikkel, §2–3 og eksemplene 3.1–3.2. Ikke målt brukereffekt.
- **begrensning:** Forfatterne fremmer sin egen ratio product-metode og forutsetter forholdstallstolkning. Artikkelen alene begrunner ikke å erstatte en eksplisitt additiv verdimodell med deres metode.

### C3 — konstruerte skalaer er ikke nøytrale

- **claim:** Abbas og Hupmans originalabstrakt rapporterer analytiske betingelser og simuleringer som viser at monotone endringer i konstruerte skalaer kan snu rangeringer. I deres simuleringer øker følsomheten med antall kriterier eller alternativer. Dette gjelder deres modell og simuleringsoppsett, ikke en universell effektstørrelse.
- **source URL:** https://www.sciencedirect.com/science/article/abs/pii/S0377221722010062
- **publisher:** Elsevier, European Journal of Operational Research 309(1), 225–235.
- **pub_date:** 2023-08-16, oppgitt utgavenummer/dato; DOI 10.1016/j.ejor.2022.12.038.
- **accessed:** 2026-10-26.
- **confidence:** Middels; originalabstrakt og metadata tilgjengelig gjennom søkeindeks, åpning ga HTTP 403, fulltekst ikke kontrollert.
- **class:** Original analytisk/simuleringsstudie, bare abstrakt inspisert. Supplerende støtte, ikke nødvendig for C2.

### C4 — vektingsmåten har betydning

- **claim:** Fischers originalabstrakt beskriver to eksperimenter: direkte viktighetsvekter var ikke følsomme for kriterienes spenn slik den normative modellen tilsier. Swing- og trade-off-vekter viste større spennfølsomhet, men mindre enn modellen forutsa. Elicitering fjerner dermed ikke automatisk skjønn eller skjevhet.
- **source URL:** https://www.sciencedirect.com/science/article/pii/S0749597885710485
- **publisher:** Elsevier, Organizational Behavior and Human Decision Processes 62(3), 252–266.
- **pub_date:** 1995-06.
- **accessed:** 2026-10-26.
- **confidence:** Middels; originalabstrakt og metadata via søkeindeks, fulltekst ga HTTP 403 og er ikke kontrollert.
- **class:** Original eksperimentstudie, bare abstrakt inspisert. Ikke bemanningsstudie.

### C5 — forklaringer garanterer ikke bedre beslutninger

- **claim:** Bansal mfl. undersøkte sentimentklassifikasjon og spørsmål/svar på tre datasett med KI på omtrent menneskelig treffsikkerhet. KI-støtte kunne gi komplementær prestasjon, men forklaringer økte ikke denne forbedringen; de økte aksept av KI-råd uavhengig av om rådet var riktig. Studien målte primært beslutningsnøyaktighet, ikke alle mulige forståelses- eller tidsgevinster.
- **source URL:** https://arxiv.org/pdf/2006.14779
- **publisher:** ACM CHI 2021; forfatterversjon hos arXiv, DOI 10.1145/3411764.3445717.
- **pub_date:** 2021-05, CHI 2021; lest arXiv v3 datert 2021-01-12.
- **accessed:** 2026-10-26.
- **confidence:** Høy for studiens avgrensede resultat.
- **class:** Original brukerundersøkelse, abstrakt, oppgaver og begrensninger §6.1 inspisert.
- **begrensning:** Crowdsourcingoppgaver, ikke turnusansvarlige. Resultatet viser ikke at forklaringer aldri hjelper forståelse.

### C6 — aktiv kontroll har en brukskostnad

- **claim:** Buçinca mfl. sammenlignet tre interaksjoner som fremmer aktiv tenkning, to enklere forklaringsgrensesnitt og ingen KI, med 199 deltakere. Aktiv kontroll reduserte overreliance sammenlignet med de enklere forklaringene. De mest virksomme variantene fikk samtidig svakere subjektive vurderinger; nytten var større blant deltakere med høyere motivasjon for krevende tenkning.
- **source URL:** https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca21trust.pdf
- **publisher:** ACM Proceedings on Human-Computer Interaction 5(CSCW1), artikkel 188; forfatterversjon hos Harvard, DOI 10.1145/3449287.
- **pub_date:** 2021-04.
- **accessed:** 2026-10-26.
- **confidence:** Høy for studiens betingelser.
- **class:** Original kontrollert studie. Abstrakt og §3 om matvarebytte og forsøksbetingelser inspisert.
- **begrensning:** Simulert KI og ernæringsoppgave for lekfolk, ikke bemanning. Studien gir ingen begrunnelse for en bestemt mengde obligatorisk friksjon her.

### C7 — motbelegg: noen forklaringer reduserer overreliance

- **claim:** Vasconcelos mfl. rapporterer fem studier med totalt 731 deltakere som løste labyrinter sammen med simulert KI. Manipulasjon av oppgavevanskelighet, forklaringsvanskelighet og belønning påvirket overreliance. Enkelte forklaringer hjalp når de gjorde kontroll av rådet mindre krevende. Forfatterne avgrenser overføring fra sitt kontrollerte lavrisikomiljø.
- **source URL:** https://arxiv.org/html/2212.06823v2
- **publisher:** ACM Proceedings on Human-Computer Interaction 7(CSCW1), artikkel 129; forfatterversjon hos arXiv, DOI 10.1145/3579605.
- **pub_date:** 2023-04, publikasjonsmetadata; lest versjon datert 2023-01-26.
- **accessed:** 2026-10-26.
- **confidence:** Høy for de rapporterte labyrintstudiene.
- **class:** Original eksperimentserie; abstrakt, metode og §10.4 inspisert.
- **begrensning:** Ingen dokumentasjon av effekt på generativ bemanningsforklaring. Motbelegg mot den bastante påstanden «forklaringer hjelper aldri».

### C8 — en samlet klassifikasjonsscore skjuler språklige feil

- **claim:** Ribeiro mfl. introduserer CheckList: minimumstester av bestemte ferdigheter, endringer som skal bevare etiketten og endringer med forventet retning. De demonstrerer feil som ikke fremgår godt av samlet held-out accuracy, på tre NLP-oppgaver.
- **source URL:** https://aclanthology.org/2020.acl-main.442.pdf
- **publisher:** Association for Computational Linguistics, ACL 2020, 4902–4912.
- **pub_date:** 2020-07.
- **accessed:** 2026-10-26.
- **confidence:** Høy for testmetoden og de undersøkte modellene, ukjent for en ny preferanseklassifikator.
- **class:** Original metode- og evalueringsartikkel, særlig §2. Ingen målt effekt for norsk turnustekst.

## Hva briefen bør dokumentere — egne anbefalinger, ikke målte funn

Utledning fra C1–C4: Beskriv hvert kriteriums rådata, retning, verdifunksjon og ankerpunkter; hva en forbedring mellom ankerpunktene betyr; hvem som valgte vektene, og hvilke avveininger de godtok. Et vektsett er ufullstendig dokumentert uten skalaene det virker på. Vis kriteriebidragene til totalscoren. Hold absolutte krav utenfor en kompenserende sum, slik at en høy preferansescore ikke kan oppveie et brudd. Dette er et designforslag for den oppgitte oppgaven, ikke utledning av juridiske krav fra kildene.

En enkel etterprøvbar modell kan skrives `S(i) = Σ w(j) × v(j, x(i,j))`. Dokumenter også manglende data, like scorer og avrunding. Dersom verdifunksjonene og vektene er faste og bare avhenger av kandidatens egne data, endrer ikke en ny kandidat scoreforskjellen mellom to eksisterende kandidater. Dette følger algebraisk av formelen; det er ingen brukerundersøkelse. Kandidatbasert min–maks-normalisering kan derimot endre skalaen når kandidatsettet endres.

Eget regneeksempel på min–maks, ikke hentet fra et paper: To kriterier maksimeres med like vekter. A=(80,50), B=(40,60), C=(0,55). Normalisert på dette settet blir A=0,50 og B=0,75. Legges D=(0,0) til, blir A≈0,917 og B=0,75. A/B snur selv om D er svakere på begge kriterier. Eksemplet begrunner en konkret stabilitetstest; det sier ikke hvilken normalisering som passer bruksområdet.

Test rangeringen med alternative vekter, små endringer nær en toppkandidat, ekstra/fjernede kandidater og identiske kandidater. Rapporter når toppvalget skifter, ikke bare om koden kjører. Faste skalaer må begrunnes og håndtere verdier utenfor ankrene. Kandidatrelative skalaer krever at sammenhengen mellom spenn og vekter vurderes på nytt. Ingen av delene dokumenterer et globalt optimalt turnusoppsett.

Utledning fra C5–C7: Forklaringstekst bør gjøre datagrunnlaget og den konkrete avveiningen lett å kontrollere. Vurder forståelse, faktisk valg og opplevd tillit separat. «Jeg stoler på svaret» er ikke bevis på at brukeren gjenkjenner et feilaktig råd. Det finnes her ingen direkte studie av at en språkmodellforklaring forbedrer norske vaktbyttebeslutninger.

## Forslag til liten oppgavebasert test

Dette er et praktisk pilotopplegg, ikke et forskningsstøttet minimumsutvalg eller en styrkeberegnet effektstudie: 4–6 personer med relevant oppgavekunnskap, 4 korte syntetiske situasjoner hver, omtrent 30 minutter per person. Dersom bare medstudenter deltar, før dem som proxybrukere og begrens konklusjonene tilsvarende.

Sammenlign samme kandidatdata med kriterietabell alene og med forklaring i tillegg. Bruk ulike, matchede situasjoner og varier rekkefølgen; unngå at samme fasit læres før den andre varianten. Inkluder en tydelig avveining, nesten like kandidater, uklar preferanse og en bevisst feil i testforklaringen. Den siste skal bare forekomme i et kontrollert testmateriale.

Oppgaver: Velg kandidat og begrunn valget; pek på hvilke opplysninger som avgjorde; skill gyldighet fra rangering; identifiser hva teksten ikke kan fastslå; kontroller en påstand mot tabellen. Registrer korrekte faktasvar mot forhåndsdefinert fasit, feil som oppdages, aksept av feil råd og tidsbruk. Samle sikkerhet på eget svar separat. Forklar feilene etter testen.

Rapporter individuelle svar og n/N med konkrete misforståelser. Et så lite forsøk kan finne problemer og gi lokal indikasjon på forståelighet; det dokumenterer ikke generell effekt på produktivitet eller kalibrert tillit. En subjektiv tilfredshetsskår kan supplere oppgaven, ikke erstatte den. Opplegget er en egen anvendelse av spørsmålene i C5–C7.

## Uavhengig test av preferansetolkning

Eget forslag inspirert av C8: Lag 40–60 nye, anonymiserte eller syntetiske norske tekster etter en eksplisitt etikettdefinisjon, inkludert «uklart/ingen preferanse». To mennesker merker uavhengig før de ser modellens svar; avklar uenighet og behold begrunnelsene. Hold fasitsettet unna promptutvikling. Frys prompt, modellversjon og parametere før test.

Dekk negasjon, betingelser, tidsavgrensning, motstrid, indirekte språk og irrelevant tekst. Legg til par med skrivefeil/parafraser som skal bevare etiketten, samt minimalpar der negasjon eller tidspunkt skal endre den. Ikke la samme malfamilie dominere både utvikling og sluttprøve.

Rapporter forvekslingsmatrise, antall per klasse, presisjon/recall og ugyldige svar; vis feil som kan gjøre et ønske sterkere eller svakere enn teksten tilsier. Gjenta et lite delsett for variasjon. Tallene er en diagnose av dette testsettet, ikke estimert produksjonskvalitet. Testen er uavhengig av rangering og brukerprøving: gode forklaringer beviser ikke riktig klassifikasjon.

## Begrensninger, motbelegg og neste spor

- Ingen lest kilde undersøker den oppgitte skoleprototypen eller måler faktisk norsk bemanningsnytte. Overføring er en hypotese som må prøves lokalt.
- C5 må ikke gjengis som at ingen menneske–KI-gruppe oppnådde komplementær prestasjon: noe slik forbedring forekom; forklaringene ga ikke den ekstra forbedringen. Dette skiller originalresultatet fra en for bastant sekundærfortolkning.
- C7 er nødvendig motbelegg: virkningen av forklaringer avhenger av oppgave og kontrollkostnad. C6 viser at en virkningsfull kontrollmekanisme også kan oppleves mindre brukervennlig.
- C3 og C4 er begrenset til indekserte originalabstrakter etter HTTP 403. Unngå detaljer utover abstraktene uten tilgang til fulltekst. De er supplement; hovedanbefalingen om skala, vekter og sensitivitetskontroll støttes også av tilgjengelig C1 og C2.
- Neste empiriske spor er et lokalt vektingsintervju med relevante brukere og pilotene over. Dette er gjenstående arbeid, ikke funn. Ved krav om sterkere effektpåstander trengs en større forhåndsplanlagt sammenligning med realistiske oppgaver; denne runden har ikke identifisert et forsvarlig utvalgsbehov.
- Originalarbeidene som C2 henviser til om rank reversal kan leses hvis en senere teknisk metodeavgjørelse trenger bredere teori. De er ikke lest her og inngår ikke som selvstendig evidens.

## Leste kilder og stoppgrunn

1. C1: GOV.UK 2024 — tilgjengelig metodetekst, særlig steg 3–5.
2. C2: Mohammadi & Rezaei 2023 — tilgjengelig artikkeltekst, definisjoner og eksempler.
3. C3: Abbas & Hupman 2023 — kun indeksert originalabstrakt/metadata; fulltekst blokkert.
4. C4: Fischer 1995 — kun indeksert originalabstrakt/metadata; fulltekst blokkert.
5. C5: Bansal mfl. 2021 — original-PDF, abstrakt, oppgaver og begrensninger.
6. C6: Buçinca mfl. 2021 — original-PDF, abstrakt og forsøksopplegg.
7. C7: Vasconcelos mfl. 2023 — forfatter-HTML, abstrakt, metode og begrensninger.
8. C8: Ribeiro mfl. 2020 — original-PDF, innledning og testtaksonomi.

Stopp: Alle tre spørsmålene er dekket på det nødvendige nivået, inkludert motbelegg mot et generelt forklaringsløfte. Grensen på åtte inspiserte kildearbeider er nådd. Ingen markeds- eller adopsjonspåstander ble undersøkt. Ingen kode, produktfiler eller andre forskningsartefakter er endret.
