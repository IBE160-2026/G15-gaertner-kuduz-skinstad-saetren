# Uavhengig verifisering av rangering og forklaringer — r1

Dato/accessed: 2026-10-26. Kontrollert prosjektgrunnlag: bare `rangering-r1-1.md`. Fire kildearbeider, fem webkall. Ingen andre prosjektfiler eller skills lest. Primærtekstene var tilgjengelige som fulltekst; relevante metode-, resultat- og begrensningsavsnitt er inspisert, ikke bare abstraktene. `verified` betyr støtte til den presist avgrensede påstanden under, ikke replikasjon eller dokumentert produktnytte.

## C1 — vekter, skala og sensitivitet

- **status:** verified for metodekjernen, uavhengig bekreftet med en annen veiledning. Den opprinnelige 2024-kildens eksakte ordlyd og metadata er unverified i denne kontrollen.
- **confidence:** høy for metodeutsagnet.
- **source URL:** https://assets.publishing.service.gov.uk/media/5a790545e5274a2acd18b975/1132618.pdf
- **publisher:** Department for Communities and Local Government, britisk offentlig metodeveiledning, *Multi-criteria analysis: a manual*.
- **pub_date:** januar 2009; offentlig landingsside oppgir 2009-01-28. Opprinnelig manual fra 2000, revidert 2009.
- **accessed:** 2026-10-26.
- **lest:** §6.2 om swing weighting, trykt s. 63–64; §6.2.14 om sensitivitetsanalyse, trykt s. 68–69; publikasjonens kolofon.

Manualen knytter kriterievekter til både spennet mellom nederste og øverste preferansescore og verdsettingen av denne forskjellen. Kriteriets generelle viktighet alene bestemmer derfor ikke vekten. Den foreskriver undersøkelse av hvordan andre scorer eller vekter endrer alternativrekkefølgen. Dette støtter C1s metodekjerne. Ingen vesentlig overgeneralisering i den avgrensede C1-påstanden. Metoden etablerer verken prosjektets kriterier, riktige norske bemanningsvekter eller effekten av 40/35/25. Sensitivitetsanalyse undersøker robusthet; den beviser ikke at en modell er god eller nødvendigvis ustabil.

## C5 — forklaringer og beslutningsytelse

- **status:** verified med presisering.
- **confidence:** høy for det avgrensede forsøksresultatet.
- **source URL:** https://arxiv.org/pdf/2006.14779
- **publisher:** ACM, CHI 2021; forfatterversjon hos arXiv. DOI: 10.1145/3411764.3445717.
- **pub_date:** CHI 2021, 8.–13. mai; lest arXiv v3 datert 2021-01-12.
- **accessed:** 2026-10-26.
- **lest:** §4 om forsøksbetingelser/prosedyre, §5.1 og figur 4–5, §6.1 og konklusjon.

Bansal mfl. undersøker to sentimentdatasett og LSAT-spørsmål med crowdsourcing. Lag oppnådde komplementær nøyaktighet, men forklaringsbetingelsene ga ingen statistisk signifikant nøyaktighetsforbedring over referansen som viste anbefaling og modellkonfidens. Formuleringen «økte ikke» i digesten bør være «ga ingen påvist signifikant forbedring over denne referansen». Nullfunn er ikke bevis på eksakt null effekt. Aksept av også feil råd er et støttet hovedfunn, men forklaringstype og datasett påvirket delresultatene; «uavhengig av riktighet» må ikke leses som identisk effekt i alle betingelser. §6.1 avgrenser beslutningsnøyaktighet fra blant annet hastighet og ekspertbruk. Studien støtter ingen automatisk gevinstgaranti; den beviser ikke at forklaringer aldri hjelper.

## C7 — motbelegg og oppgaveavhengighet

- **status:** verified for betinget reduksjon av overreliance.
- **confidence:** høy innen labyrintoppgaven, ukjent overførbarhet.
- **source URL:** https://arxiv.org/html/2212.06823v2
- **publisher:** ACM, Proceedings on Human-Computer Interaction 7(CSCW1), artikkel 129; forfatterversjon hos arXiv. DOI: 10.1145/3579605.
- **pub_date:** april 2023 i publikasjonsmetadata; lest versjon 2023-01-26.
- **accessed:** 2026-10-26.
- **lest:** §4.1–4.2, §5.4–5.5, §7.5, §8.5, §10.1 og §10.4.

Vasconcelos mfl. rapporterer fem studier, totalt N=731, med labyrinter og simulert KI. KI-treffsikkerheten kontrolleres til 80 prosent med oppgitte unntak. Forklaringer kan redusere overreliance når kontroll av rådet blir lettere; vanskelighet og insentiver inngår i forsøksmanipulasjonene. Dette er reelt motbelegg mot «forklaringer hjelper aldri». Presisering: studie 3 var eksplorativ uten forhåndsregistrerte hypoteser; alle fem er ikke like sterke bekreftende tester. §10.4 avgrenser et kontrollert lavrisikomiljø og uttrykker usikkerhet om blant annet generative, ikke-spillbaserte og høyrisikooppgaver. Ingen vesentlig avvik fra C7s avgrensede ordlyd. Redusert overreliance må heller ikke automatisk omtales som generell produktivitetsgevinst.

## C8 — CheckLists grunnleggende testtaksonomi

- **status:** verified.
- **confidence:** høy for taksonomien.
- **source URL:** https://aclanthology.org/2020.acl-main.442.pdf
- **publisher:** Association for Computational Linguistics, ACL 2020, s. 4902–4912.
- **pub_date:** 2020-07, konferanse 5.–10. juli.
- **accessed:** 2026-10-26.
- **lest:** innledning, §2.1–2.2 og figur 1.

Ribeiro mfl. organiserer tester som språklige evner × testtyper: Minimum Functionality (MFT), Invariance (INV) og Directional Expectation (DIR). MFT undersøker enkle avgrensede atferder; INV bruker etikettbevarende endringer; DIR krever en forventet retning eller relasjon i prediksjonen. Presisering til digesten: DIR trenger ikke alltid etikettbytte; et krav kan være at sentimentet ikke blir mer positivt. Aggregerte mål kan skjule bestemte feil. Artikkelen støtter metodeanvendelsen, ikke akkurat 40–60 norske tekster, et statistisk tilstrekkelig utvalg eller kvaliteten til prosjektets nye klassifikator.

## Felles overføringsgrense

På grunnlag av de leste tekstene er metodeutsagnet og de avgrensede forsøksfunnene støttet. Dokumentert gevinst i norsk bemanning er **unverified**, med intet direkte evidensgrunnlag i disse fire arbeidene. C5 og C7 sammen støtter å prøve forklaringer mot konkrete oppgaver og separate utfall, ikke et generelt løfte om bedre valg eller en konklusjon om at forklaringer er unyttige. Prosjektkonteksten bestemmer hvilke spørsmål som bør undersøkes lokalt; den er ikke evidens for svarene.

C2–C4 og C6 er ikke kontrollert i denne avgrensede runden. Ingen konklusjon her bygger på treningserindring eller abstrakt alene.
