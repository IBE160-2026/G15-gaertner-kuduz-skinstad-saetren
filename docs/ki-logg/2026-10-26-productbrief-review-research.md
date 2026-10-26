# KI-logg: produktbrief, review og kildeundersøkelse

## Oppgave og prompt

Brukeren skrev først «bmad-review» og presiserte deretter: «Jeg ville kjøre en bmad review for en vurdering av productbrief. utfør dette samt en bmad-deep-recon av det som kommer frem i product brief». Etter review og konkret research-plan godkjente brukeren kjøring med «start deep-recon».

Målet var å vurdere hele `product-brief.md` og undersøke forutsetninger uten å utvide v1. Den første, separate reviewen av en staget smoketest traff ikke det tilsiktede dokumentet; den er loggført separat og er ikke del av denne briefvurderingen.

## Hva modellen leverte

Codex kjørte BMADs review med uavhengige innholds-, grensevilkårs- og strukturreviewere og en etterfølgende språklinse. [Reviewrapporten](../../_bmad-output/planning-artifacts/reviews/product-brief-2026-10-26.md) har ti innholdsfunn og fem redaksjonelle forslag.

Den godkjente researchen brukte tre separate webresearchere: regler/kandidatbegreper, eksisterende verktøy og rangering/brukernytte. Researcherne fikk avgrensede spørsmål og kildekrav, ikke prosjektfilene som bevis. Regel- og metodekilder ble kontrollert av egne verifikatorer. En egen avsluttende kontrollør åpnet alle 18 rapportkildene. [Researchrapporten](../../_bmad-output/planning-artifacts/research/domain-turnushjelperen-produktbrief-2026-10-26/research.md) samler funn og anbefalinger; digestfiler, memlog og maskinberegnet ferskhetskart ligger i samme mappe. En statisk HTML-visning lages fra samme rapport med escaped kildetabell, uten nettavhengigheter.

Ingen appkode, modellerte regler, vekter eller brieftekst ble endret. Dette er vurdering, research og dokumentasjonsartefakter, ikke implementering av nye produktkrav.

## Hva som ble presisert og hvorfor

- Reviewen etterlyser ikke full juridisk dekning eller ansattportal; det er bevisst utenfor v1. Hullet gjelder formuleringer og forutsetninger innenfor valgt omfang.
- Linsens tallkrav ble ikke brukt til å finne på flere innholdsfunn. Det ble rapportert seks reelle adversarial-punkter og fire grensevilkår.
- 36 timer og faktor 1,5 er behandlet som scenarioforutsetninger. Faglig støtte gjelder at de ikke er universelle lovregler, ikke at prototypen må utvide kostnadsmodellen.
- Opprinnelig omtale av forklaringsstudier kunne leses som om originalresultatene var uavhengig replisert. Kildeaudit avdekket dette etikettproblemet; rapporten skiller nå korrekt gjengivelse fra replikasjon og ukjent bemanningseffekt.
- Et nullfunn hos Bansal mfl. er presisert som ingen signifikant forbedring over en konkret referansebetingelse, ikke bevis for eksakt null effekt. CheckList-tester av retning krever ikke alltid etikettbytte.
- Leverandørbeskrivelser er ikke omtalt som egne produkttester eller målte effekter. Eldre og udaterte funksjonspåstander er eksplisitt merket; den målrettede andre runden fant ikke ferskere uavhengig belegg for Plandays forklaringsfunksjon.
- Et eget syntetisk regneeksempel viser kandidatsettavhengighet i PRD-ens min–maks-modell. Det er ingen påstand om brudd på determinisme eller et automatisk vedtak om nye vekter.

## Kvalitetssikring

Kildekontroll, begrensninger og publiserings-/hentedatoer kan spores i digestene. BMADs `citations`-verktøy bekreftet samsvar mellom alle 18 henvisninger og kilder. `tally` beregnet ti registrerte nøkkelpåstander: tre uavhengig bekreftet og sju beholdt som uverifiserte etter registerets krav; dette er ikke en kvalitetsprosent for produktet. `staleness` fant én datert funksjonsbeskrivelse utenfor tremånedersvinduet, med forventet exit 1.

Regneeksemplet ble beregnet direkte med JavaScript: A/B får 52,5/47,5; med C får A/B/C 52,5/83,5/35. Den nye kandidaten rangeres sist, men endrer skalaen og A/B-rekkefølgen. Separate redaksjonelle struktur- og språkpass bevarte kilde-/konfidenspresisjonen. HTML-kontrollen fant først at norsk tekst i den genererte kildetabellen ble skadet ved overføring av verktøyets stdout. Eksplisitt UTF-8 ved regenerering rettet dette. Sluttkontrollen fant null manglende tekstlinjer sammenlignet med Markdown, null manglende ankermål, 18 kildeankre, null eksterne ressursreferanser og ingen erstatningstegn. Kildelenkene ble validert av `escape-sources`, og `git diff --check` bestod. HTML er ikke visuelt kontrollert i nettleser. Ingen betalte modellkall, app-tester eller brukerprøver ble kjørt. Faktisk brukerbehov og nytte må fortsatt undersøkes lokalt.
