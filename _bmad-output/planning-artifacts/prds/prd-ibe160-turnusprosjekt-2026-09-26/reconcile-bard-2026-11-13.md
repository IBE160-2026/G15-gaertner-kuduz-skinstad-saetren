# Uavhengig kontroll av PRD mot Bårds tilbakemelding

**Dato:** 2026-11-13

**Kontrollert:** `tilbakemelding-prd.md` (2026-11-12), gjeldende `prd.md`, relevante vedtak i `docs/beslutninger/avklaringspunkter.md` §13 og AD-7 i arkitekturen.

**Omfang:** Dokumentkontroll. Implementasjon og tester er ikke verifisert her.

## Dom

PRD-en følger i hovedsak den formative tilbakemeldingen og vedtakene AV-15/AV-16. SM-3, SM-4 og SM-C2 er konkretisert uten å vedta Bårds illustrative tall eller en regel om «faktoren som bidrar mest». FR-13, P-12B, §8 og sporingen er samordnet. **FR-10 er fremdeles ikke målbart ved feil**, men den uavklarte kontrakten er synlig og har eier og frist før story 5.1. To mindre tekstlige uklarheter rundt gyldig KI-forklaring og én kandidat bør rettes for at PRD-en skal være entydig.

## Funn som bør følges opp

| ID / alvorlighet | Bevis | Konsekvens og konkret anbefaling |
|---|---|---|
| R1 – Middels, åpent beslutningspunkt | Tilbakemeldingen 4.4, linje 52–56, peker på FR-10s «avgrensede automatiske nye forsøk». PRD linje 298 har fortsatt dette uttrykket, men utsetter antall, tidsbudsjett og sluttstatus til §8 linje 462. Beslutningsreferatet linje 764 og AD-7 linje 102 gjør samme avgrensning. | En test av feilflyten ved 429, 5xx og nettverksfeil kan ennå ikke ha entydig fasit. Dette er **ikke** en uautorisert innføring av 90-sekundersgrensen for preferansetolkning, og det er rimelig å la beslutningen stå åpen nå. Før story 5.1 starter må hele gruppa vedta tall, startpunkt for tidsmåling, hva som skjer når budsjettet er brukt, og når brukerutløst nytt forsøk tillates; skriv deretter identisk kontrakt i FR-10, §8, AD-7 og story 5.1. Ikke marker 4.4 som fullt lukket før dette. |
| R2 – Middels, kravtolkning | PRD FR-11 linje 338–344 tillater begrunnelser om bare harde regler og sier at ugyldige påstandsfelt gir Reservetekst. SM-4 linje 443 krever derimot at **hver gyldige** KI-forklaring har minst én relevant, faktakontrollert påstand om en Myk faktor. AV-15 i referatet linje 755 støtter SM-4. | En teknisk implementasjon av FR-11 alene kan godta en hardregelbasert forklaring som bryter SM-4. Legg én testbar setning til FR-11: En vellykket KI-forklaring må inneholde minst én relevant, verifisert påstand om en beregnet Myk faktor; svar uten en slik påstand behandles som ubrukelig og gir tydelig merket Reservetekst. Da samstemmer kravet og målet uten å kreve en «største faktor». |
| R3 – Lav, ordliste | PRD linje 79 definerer «Avveining» som en forklaring på hvorfor én Kandidat rangeres over en annen. FR-11 linje 344 og SM-4 linje 443 krever forklaring også når bare én Kandidat er gyldig og ingen referanse finnes. | Definer Avveining som forklaring av kandidatens beregnede forhold og, når referanse finnes, sammenligning med den. Det fjerner en unødvendig motsetning i den ellers forbedrede ordlisten. |
| R4 – Lav, redaksjonell rest fra 4.1 | Tilbakemeldingen 4.1, linje 34–38, ber om at seeddata og implementasjonsdetaljer flyttes ut av kravet. PRD linje 114 inneholder fortsatt testdataenes eksakte sluttdato og demovakter; linje 194 omtaler taket som en «navngitt parameter». Sporingen linje 496 og 502 har allerede slike detaljer. | Selve regelen om nødvendig datadekning er forståelig og bør beholdes. Flytt den konkrete sluttdatoen/demovaktene til §10 og erstatt «navngitt parameter» med produktkravet om ett felles, fast tak for samme beslutningsgrunnlag. Dette reduserer koblingen til testoppsett uten å endre funksjon. |
| R5 – Lav, antakelser | PRD §9 linje 484–485 omtaler bekreftet regelutvalg og bekreftet helligdagsbehandling i antakelsesindeksen, mens linje 108/193 sier at dette er vedtatt. Fem `[ASSUMPTION]`-merker finnes i teksten (linje 59, 108, 110, 195 og 448); §9 har fem punkter. | Antakelsesmarkeringen er nå mekanisk komplett. Rydd likevel §9 slik at bare gjenstående antakelser merkes som antakelser. Bevar vedtak og begrunnelser i kravtekst/sporing. Særlig setningen i linje 108 gjelder mulig fremtidig utvidelse, ikke usikkerhet om dagens fire regler. |

## Punktvis kontroll av tilbakemeldingen

| Punkt | Resultat og bevis |
|---|---|
| 4.1 Selvbærende krav og ordliste | **I hovedsak løst.** Ansatt, Demo-modus, Reservetekst og Datafeil er definert i PRD linje 63 og 82–84. FR-1 linje 100–104 er lesbar uten beslutnings-ID. Teknisk historikk er samlet i §10 linje 489–511. R4 gjelder rester i §4.2–§4.3. |
| 4.2 Åpne spørsmål og `final` | **Løst med én bevisst åpen kontrakt.** `final` er forklart i linje 15; §8 linje 454–462 skiller åpne valg med eier/frist fra kontroller i §8.1 linje 464–473. AV-16 og OP-02 er samordnet i hovedtabellen i referatet linje 58 og §13 linje 759–764. Den gamle «Ikke bestemt»-linjen ved OP-02 linje 316 er eksplisitt merket historisk i linje 311. Ingen kontroll er feilaktig markert utført. |
| 4.3 Innlogging | **Løst.** FR-13 linje 385–390 dekker felles feilmelding, saltet hash, standardøkt 480 minutter med overstyring, utløp/utlogging og hemmeligheter. Sporingen linje 508 angir story 1.3/1.4. |
| 4.4 Målbarhet | **Delvis løst.** SM-3 linje 442 regnes fra ferdig kandidatberegning og krever ingen ekstra handling; SM-4 linje 443 dekker myk faktor, én kandidat og Reservetekst; SM-C2 linje 452 krever kontroll før visning og 90 sekunder fra første live-kall. AV-15 linje 752–757 er samsvarende. FR-10 gjenstår som R1. |
| 4.5 Prioritering | **Løst.** Hvert FR har «Kjerne» (PRD linje 94–390), og §6.1 linje 423 sier det samme. §6.2 linje 425–435 skiller Etter kjerne, Strekk og Utenfor v1 med begrunnelser. P-12B er uttrykkelig utenfor v1 i linje 435 og FR-12 linje 370. |
| Mekanikk | FR-1–FR-14 er til stede; FR-14 står bevisst mellom FR-8 og FR-9 (linje 229–233). SM-1–SM-9 og SM-C1/C2 er til stede (linje 439–452). Ordlistehullene er lukket. Fem antakelsesmarkeringer svarer til fem indekspunkter, med den redaksjonelle merknaden R5. Relative lenker til referat, beslutningsgrunnlag, epics og arkitektur i §10 er kontrollert og finnes. |

## Særlig kontroll av vedtatte formuleringer og scope

- **SM-3:** «Når kandidatberegningen ... er ferdig» (PRD linje 442) retter tvetydigheten «rett etter vaktvalg». Tomtilstand og Datafeil har egne utfall. Fristen før story 4.4 er dokumentert i sporingen linje 510 og AV-15 linje 754.
- **SM-4:** Linje 443 krever én relevant myk faktor, én-kandidatflyt og Reservetekst; ingen algoritme for «faktoren som bidrar mest» er innført. Visning av de fire beregnede forholdene ved Reservetekst er også vedtatt i AV-15 linje 755, altså et **bevisst nytt produktkrav**, ikke et utilsiktet tillegg. R2 og R3 bør likevel rettes.
- **SM-C2:** Linje 452 og AD-7 linje 102 er samordnet om faktakontroll før visning, 90 sekunder fra første live-kall og Reservetekst ved feil. Demo-modus omfattes ikke. Fristen før story 5.3 er dokumentert i AV-15 linje 756.
- **FR-10/FR-13:** FR-10s feilbudsjett er ikke automatisk likt Avveiningens, og §8 setter beslutningsfrist før story 5.1. FR-13 angir korrekt 480 minutter som overstyrbar **standard**, i samsvar med referatet linje 764.
- **§8 og P-12B:** «Hele gruppa» eier mobil/nettbrett og sensornøkkel, med frist før henholdsvis story 4.6 er ferdig og innlevering (PRD linje 460–461, AV-16 linje 761–762). P-12B er utenfor v1 og krever eget vedtak/story.
- **Sporing:** Tabellen i PRD §10 knytter de endrede kravene til AV-15/AV-16, AD-7, P-12B og stories. Ingen manglende mål-ID-er eller døde relative lenker ble funnet i denne kontrollen. Status for implementasjon er uttrykkelig holdt atskilt fra vedtak.

**Prioritet:** Rett R2–R3 i dokumentet nå. R4–R5 er redaksjonell opprydding. Behold R1 som åpent gruppevalg med sperre før story 5.1; ikke velg prøve-tall uten vedtak.
