# Vurderingsmatrise – IBE160 del 1

Arbeidsdokument for gruppen, opprettet 2026-10-12. Tiltakene er vår anvendelse av [sensorveiledningen](sensorveiledning-del-1.md), ikke nye emnekrav. Vektene er veiledende innenfor del 1, som teller 70 % av samlet karakter. Matrisen gir ingen karaktergaranti.

Oppdater ved milepæler. Lenke til faktiske bevis må legges inn før et tiltak merkes ferdig. Statusen nedenfor bygger på gjennomgått produktbrief og dokumentasjonsoppsett; dette er ikke en full revisjon av repo eller historikk. Godkjent proposal må kontrolleres før endelig omfang fastsettes.

| Kriterium | Vekt | Forventet leveranse i turnusprosjektet | Bevis / grunnlag nå | Gjenstår / neste tiltak |
|---|---:|---|---|---|
| Prosess og KI-styring | 30 % | Sporbar sammenheng mellom krav, stories, endringer, prompts, kvalitetssikring og begrunnede beslutninger. | [Produktbrief](../../product-brief.md), [KI-loggoppsett](../ki-logg/README.md). Dette er grunnlag, ikke bevis på ferdig utviklingsprosess. | Koble stories til konkrete PR-er, tester og KI-logger. Dokumenter faktiske korrigeringer og avvik underveis. |
| Funksjonalitet og omfang | 20 % | Komplett flyt fra valgt vakt til filtrerte og rangerte kandidater, forklaring og menneskelig valg. | [Omfang og suksesskriterier](../../product-brief.md). | Kontroller mot godkjent proposal. Implementer og demonstrer kjerneflyten, feil input og gjentatte handlinger før stretch goals. |
| Kvalitetssikring og testing | 15 % | Meningsfulle tester av harde regler, kostnad og sentrale integrasjoner, samt dokumentert gjennomgang. | [Krav til kvalitetssikring](../../AGENTS.md). Testresultater er ikke dokumentert her. | Test grensetilfeller, deterministiske beregninger og at KI aldri anbefaler utelukkede kandidater. Lenke til testresultater og faktiske feilrettinger. |
| Design og brukeropplevelse | 10 % | Forståelig kandidatoversikt, begrunnelser og tilbakemeldinger til turnusansvarlig. | [Målgruppe og beslutningsgrunnlag](../../product-brief.md). | Dokumenter UX-valg. Verifiser tomtilstander, feilmeldinger, kontrast, tastaturbruk og relevante skjermstørrelser. |
| Kodekvalitet og arkitektur | 10 % | Tydelig skille mellom regelmotor, rangering, KI-forklaringer og brukergrensesnitt. | [Ansvarsdeling mellom regler og KI](../../product-brief.md). | Beslutt rammeverk og arkitektur, og kontroller at koden følger dokumentasjonen. |
| README og kjørbarhet | 10 % | Verifiserte kommandoer, versjoner, konfigurasjon, testdata og testinstruksjoner. | [README](../../README.md), med inngang til vurderingsgrunnlaget. | Fyll inn faktiske kommandoer når kode finnes. La en person installere, kjøre og teste i rent miljø kun etter README. |
| Ryddighet i repoet | 5 % | Tydelig skille mellom kode, dokumentasjon og ressurser; ingen hemmeligheter eller byggeartefakter. | [Gitignore](../../.gitignore), [original sensorveiledning](sensorveiledning-del-1.pdf), [agentinstruksjoner](../../AGENTS.md). | Kontroller sporede filer og historikk ved milepæler. Bekreft at nye dokumenter følger gruppens utsjekking. |

## Rutine ved milepæler

1. Sammenhold levert funksjonalitet med godkjent proposal og gjeldende plan.
2. Oppdater radene med lenker til konkrete endringer, testresultater og kvalitetssikring.
3. Noter mangler og neste tiltak; ikke beskriv planlagt arbeid som gjennomført.
4. Kontroller README i rent miljø og dokumenter utfallet.
5. Bruk originalveiledningens nivåbeskrivelser til å finne svakheter; prioriter stabil kjerneflyt og etterprøvbar prosess.
