# Regler og produktbegreper – digest r1-1

Dato/accessed: 2026-10-26. Avgrensning: begreper og forutsetninger for en skoleprototype som vurderer én erstattingsvakt; ingen konkrete bemanningsråd. Ingen prosjektfiler er lest. Konklusjonene bygger bare på webkildene hentet i denne runden.

## Funn til beslutningen

Presiser «godkjent av prototypens modellerte regler» og hvilket datagrunnlag som brukes. Skill dette fra fravær av registrert kollisjon, praktisk tilgjengelighet og bekreftelse på å ta vakten. Beskriv 36 timer og en eventuell kostnadsfaktor 1,5 som eksplisitte scenarioforutsetninger, dersom de velges; de er ikke universelle lovregler. Dette er produktvurderinger utledet fra R1–R9 nedenfor, ikke nye lovkrav eller forslag om å bygge flere funksjoner.

## Kilderegister

Alle kilder ble åpnet 2026-10-26. «Ukjent» betyr at publiserings-/oppdateringsdato ikke fremgikk i det leste materialet; søkemotorens crawldato regnes ikke som publiseringsdato.

| ID | Source URL og publisher | pub_date | Type og uavhengighet |
|---|---|---|---|
| S1 | [Arbeidstid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/) – Arbeidstilsynet | Ukjent | Primær fagmyndighetsveiledning |
| S2 | [Arbeidsmiljøloven, særlig §§ 10-1–10-12](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) – Arbeidstilsynet, lovtekst fra Arbeids- og inkluderingsdepartementet | Publisert 2005-06-17; siden oppgir siste endringslov LOV-2026-06-19-33. Dette er metadata for hele loven, ikke dato for alle undersøkte bestemmelser. | Primær rettskilde gjengitt av fagmyndigheten; samme nettsted som S1, ikke uavhengig publisist |
| S3 | [Arbeidstid](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/arbeidstid/) – Altinn/Digitaliseringsdirektoratet | Sist oppdatert 2025-06-25 | Separat offentlig publisist; henviser til Arbeidstilsynet, derfor ikke fullt uavhengig faglig kilde |
| S4 | [Overtid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/) – Arbeidstilsynet | Ukjent | Primær fagmyndighetsveiledning |
| S5 | [Overtid](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/overtid) – Altinn/Digitaliseringsdirektoratet | Sist oppdatert 2025-06-26 | Separat offentlig publisist; henviser til Arbeidstilsynet |
| S6 | [Arbeidsplan, vaktliste, turnus, skift- og turnusplan](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/) – Arbeidstilsynet | Ukjent | Primær fagmyndighetsveiledning |
| S7 | [Deltid: Merarbeid og overtidsbetaling, kapittel 3](https://www.regjeringen.no/no/dokumenter/deltid-merarbeid-og-overtidsbetaling/id3172543/?ch=3) – Arbeids- og inkluderingsdepartementet | Ukjent i åpnet kapittel | Offentlig utredningsmateriale; kapittelet avgrenser selv omtalen til reglene slik de ble praktisert før Lufthansa-/Dialyse-avgjørelsene. Ikke brukt som bevis for dagens endelige lønnsrettslige situasjon. |

Lovdata-siden [kapittel 10](https://lovdata.no/dokument/NL/lov/2005-06-17-62/KAPITTEL_11) ga HTTP 405 ved åpning. Søkeutdrag samsvarte med hovedregelen om hvile, men erstatter ikke lest lovtekst. S2 ble lest som fallback.

## Claims

Felles accessed for hvert claim: **2026-10-26**. Confidence er **medium** for regulatoriske claims: kryssjekk er gjennomført hos flere offentlige publisister, men Altinn henviser til Arbeidstilsynet; dette skal ikke telles som to fullt uavhengige juridiske analyser.

| ID | claim | source URL | publisher | pub_date | accessed | confidence | class |
|---|---|---|---|---|---|---|---|
| R1 | Hovedregelen er minst 11 sammenhengende timer arbeidsfri i 24 timer og 35 sammenhengende timer i sju dager. Dagshvilen plasseres mellom hovedarbeidsperioder. | [S1](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/), [S2 §10-8](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/), [S3](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/arbeidstid/) | Arbeidstilsynet; Altinn/Digdir | S1 ukjent; S2 2005-06-17/endringsmetadata 2026-06-19; S3 2025-06-25 | 2026-10-26 | medium, kryssjekket | Gjeldende lovtekst og offentlig veiledning |
| R2 | Sammenhengende hvile er én ubrutt periode, ikke summen av flere korte friperioder. Bare kontroll av at vakter ikke overlapper beviser derfor ikke hvilekravet. | [S1](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/), [S3](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/arbeidstid/) | Arbeidstilsynet; Altinn/Digdir | Ukjent; 2025-06-25 | 2026-10-26 | medium | Nær teksttolkning; produktkonsekvens utledet her |
| R3 | §10-8(3) åpner for skriftlige tariffbundne avtaler med tillitsvalgte, med kompenserende hvile/passende vern og normalt gulv 8/28 timer. Bestemmelsen har snevre driftsforstyrrelsesunntak, også avtaleadgang uten tariffbinding. §10-12 gir ytterligere særskilte fraviksadganger. | [S2 §§10-8,10-12](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/), [S7 §3.3.1](https://www.regjeringen.no/no/dokumenter/deltid-merarbeid-og-overtidsbetaling/id3172543/?ch=3) | Arbeidstilsynet/AID; AID | 2005-06-17/endringsmetadata 2026-06-19; ukjent | 2026-10-26 | medium; detaljene ikke uavhengig analysert | Lovbestemte unntak; ikke komplett unntakskatalog |
| R4 | 36 timer gjelder bestemte ordninger, blant annet helkontinuerlig skift og sammenlignbar turnus. Hovedgrensen for alminnelig arbeidstid er 40 timer; andre ordninger har 38 timer. Avtaler og gjennomsnittsberegning påvirker anvendelsen. 36 timer er dermed ikke universelt maksimalt samlet ukeverk. | [S2 §§10-4–10-6](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/), [S1](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/), [S3](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/arbeidstid/) | Arbeidstilsynet; Altinn/Digdir | S2 2005-06-17/endringsmetadata 2026-06-19; S1 ukjent; S3 2025-06-25 | 2026-10-26 | medium, kryssjekket | Lovregel med anvendelsesvilkår |
| R5 | Lovens minste overtidstillegg er 40 prosent, altså minst 140 prosent samlet timelønn. 150 prosent samlet betaling betyr 50 prosent tillegg og er ikke lovens universalsats. Avtaler kan gi høyere betaling. | [S4](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/), [S5](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/overtid), [S2 §10-6(11)](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) | Arbeidstilsynet; Altinn/Digdir | Ukjent; 2025-06-26; lov publisert 2005-06-17 | 2026-10-26 | medium, kryssjekket | Lovminimum; prosentforklaring er aritmetisk utledning |
| R6 | Merarbeid er arbeid utover avtalt tid innenfor grensene for alminnelig arbeidstid; overtid er arbeid utover lovgrensen. Betalingsrettigheter kan følge avtaler også ved merarbeid. «Ekstravakt» alene bestemmer derfor ikke kostnadsart eller tillegg. | [S4](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/), [S5](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/overtid) | Arbeidstilsynet; Altinn/Digdir | Ukjent; 2025-06-26 | 2026-10-26 | medium, kryssjekket | Arbeidstidsbegrep; siste setning produktutledning |
| R7 | Arbeid utover avtalt tid krever særlig og tidsavgrenset behov. Overtid kan pålegges innenfor vilkårene; det finnes fritaksrettigheter. Ingen generell påstand om at alle ekstravakter alltid krever individuelt samtykke kan utledes. | [S4](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/), [S5](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/overtid), [S2 §10-6](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) | Arbeidstilsynet; Altinn/Digdir | Ukjent; 2025-06-26; lov publisert 2005-06-17 | 2026-10-26 | medium, kryssjekket | Lovvilkår; avgrensning av mulig overgeneralisering |
| R8 | Individuell villighet kreves for overtid utover §10-6(4)-rammen, jf. §10-6(7). §10-12(4) har eget samtykkekrav. Dette er særskilte regler, ikke universell definisjon av enhver ekstravakt. | [S2 §§10-6(7),10-12(4)](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) | Arbeidstilsynet/AID | 2005-06-17/endringsmetadata 2026-06-19 | 2026-10-26 | medium; primærkilde alene for disse detaljene | Lovtekst, ikke selvstendig kryssjekket detalj |
| R9 | Arbeidsplanen beskriver når arbeid skal utføres. Arbeidstilsynet beskriver normalt 14 dagers varsel ved endringer, samt avtale- og påleggsunntak. En ledig plass i planen dokumenterer ikke at en ny vakt allerede er avtalt. | [S6](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/), [S3](https://info.altinn.no/starte-og-drive/arbeidsforhold/ansettelse/arbeidstid/) | Arbeidstilsynet; Altinn/Digdir | Ukjent; 2025-06-25 | 2026-10-26 | medium; hovedbegrep kryssjekket, detaljunntak fra S6 | Offentlig veiledning; siste setning utledning |
| R10 | Produktet bør bruke fire separate begreper: regelgyldig innenfor modellen; kollisjonsfri i registrert plan; faktisk tilgjengelig; avklart/bekreftet for vakten. De to siste kan være ukjente selv når de to første er sanne. Dette er en analysemodell, ikke en lovpålagt firetrinnsprosess. | [S1](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/), [S6](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/), [S4](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/) | Egen syntese basert på Arbeidstilsynet | 2026-10-26 (syntese); kildedatoer ukjent | 2026-10-26 | medium; anbefalt terminologi, ikke empirisk validert | Produktvurdering |

## Korte eksakte utdrag

- S2 §10-8(1): «Den arbeidsfrie perioden skal plasseres mellom to hovedarbeidsperioder.» (10 ord; eneste direkte sitat fra S2.)
- S5: «Dette betyr at timelønnen for overtidsarbeid skal være minst 140 prosent av den vanlige timelønnen.» (17 ord; eneste direkte sitat fra S5.)
- S6: «Arbeidsgiver og arbeidstaker kan bli enige om vakter som er mindre enn 14 dager frem i tid» (19 ord; eneste direkte sitat fra S6.)

## Liten faglig ordliste

| Begrep | Betydning i en prototype | Forankring |
|---|---|---|
| Arbeidsfri/hvile | Sammenhengende periode uten arbeid; ikke en bekreftelse på at personen kan eller vil ta ny vakt. | R1–R2; siste presisering R10 |
| Alminnelig arbeidstid | Lovens ramme for ordinær arbeidstid, avhengig av ordning. | R4 |
| Avtalt arbeidstid | Tid fastsatt i arbeidsavtalen; kan være kortere enn lovgrensen. | R6/S4 |
| Merarbeid / overtid | To ulike arbeidstidsbegreper; må skilles fra hvilken betaling avtalen gir. | R6 |
| Gjennomsnittsberegning | Avtalt/tillatt annen fordeling av alminnelig arbeidstid over en periode. | R4/S3 |
| Kollisjonsfri | Ingen overlapp i registrerte vaktintervaller; teknisk produktbegrep. | R2/R10 |
| Tilgjengelig | Praktisk mulighet til å arbeide den konkrete vakten; bør kunne være uavklart. | R10, egen definisjon |
| Avklart/bekreftet | Konkret avklaring av vakten; ikke synonymt med algoritmisk rangering. | R9–R10, egen definisjon |
| Kostnadsestimat | Scenarioresultat med oppgitt lønn, timer og satser; 1,5 er en valgt faktor dersom den brukes. | R5–R6, egen produktvurdering |

## Motbelegg og grenser

- S1 kaller 28 timer en absolutt ukentlig grense i sin forenklede omtale. S2 §10-12 har særskilte fraviksadganger. Ikke løft en veiledningsformulering ut av avtalesammenhengen til en universell regel for alle ordninger.
- S6 omtaler normalt manglende arbeidsplikt på kort varsel, men lister samtidig unntak. Den støtter skillet mellom forslag og avklart vakt, ikke et generelt samtykkekrav for alt merarbeid.
- S7 varsler i kapittelinnledningen at omtalen gjelder praksis før to EU-dommer. Den bekrefter begrepshistorikken, men er utilstrekkelig som eneste kilde til dagens lønnsrettigheter for deltidsansatte. Ikke påstå generelt at merarbeid aldri gir overtidsbetaling.
- Ingen lovlighetsgaranti kan utledes bare av R1 og R4: andre vilkår og forsvarlighetsvurdering omtales i S1/S4. Å avgrense prototypens kontroll er en produktbeskrivelse, ikke et nytt regulatorisk krav.

## Uavklart og videre leads

1. Nøyaktig valg av beregningsperioder/ankerpunkt for 24 timer og sju dager er ikke avgjort her. De leste kildene gir ikke grunnlag for å påstå at hvile alltid kontrolleres som «enhver rullerende 168-timersperiode», eller bare kalenderuke. Dette må skilles fra S4s uttrykkelige faste sjudagersperiode for overtidskvoter.
2. Ingen konkret tariffavtale, arbeidsavtale, sektorordning eller unntaksavtale er undersøkt. En bestemt 36-timersgrense og 50-prosenttillegg kan derfor verken valideres eller avkreftes for et konkret arbeidssted.
3. Oppfølging ved krav om reell kostnadsberegning: les gjeldende tariffgrunnlag og oppdaterte primærkilder om EU/EØS- og norsk rettspraksis for deltidsansattes overtidsbetaling. Dette er ikke nødvendig for å merke et skoleeksempel som forenklet.
4. Oppfølging ved implementering av hvile: presiser tidsgrunnlag, datadekning før/etter vakten og hvilke avtaleunntak modellen utelater. Kildene i denne runden bestemmer ikke en bestemt algoritme.

## Søkestopp

Sju unike kilder ble åpnet og lest i relevante avsnitt; ett ekstra åpneforsøk hos Lovdata feilet. Sju webverktøykall (søk, åpning og gjenlesing samlet). Søkeutdrag ble brukt til å finne kilder, ikke som eneste grunnlag for konklusjoner. Stoppgrunn: alle fire spørsmål er dekket på begrepsnivå; åpne implementerings- og avtalespørsmål er eksplisitt avgrenset. Flere brede søk vil ikke avgjøre dem uten valgt ordning og avtalegrunnlag.
