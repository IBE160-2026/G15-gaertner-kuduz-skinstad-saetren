# Vurderingsmatrise – IBE160 del 1

Arbeidsdokument for gruppen, opprettet 2026-10-12. Tiltakene er vår anvendelse av [sensorveiledningen](sensorveiledning-del-1.md), ikke nye emnekrav. Vektene er veiledende innenfor del 1, som teller 70 % av samlet karakter. Matrisen gir ingen karaktergaranti.

Oppdatert 2026-10-16 etter valg av KI-modell (GPT-6 Luna) og robusthetstest. Lenke til faktiske bevis må legges inn før et tiltak merkes ferdig. Planleggingsdokumenter og testverktøy finnes, men appen er ikke implementert. Dette er ikke en full revisjon av repo eller historikk. Godkjent proposal må kontrolleres før endelig omfang fastsettes.

| Kriterium | Vekt | Forventet leveranse i turnusprosjektet | Bevis / grunnlag nå | Gjenstår / neste tiltak |
|---|---:|---|---|---|
| Prosess og KI-styring | 30 % | Sporbar sammenheng mellom krav, stories, endringer, prompts, kvalitetssikring og begrunnede beslutninger. | [Produktbrief](../../product-brief.md), [epics](../../_bmad-output/planning-artifacts/epics.md), [modelltestens KI-logg](../ki-logg/2026-10-15-modelltest-haiku.md) med ordrette prompts, rettet testkode og fire kategoriavvik. [Beslutningstest Haiku mot Luna](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md): testsett, fasit og beslutningsregel committet før kjøring (`d45f54d`). [Robusthetstest](../ki-logg/2026-10-16-robusthet-luna.md): iterasjon 1 strøk, og kriteriene for iterasjon 2 ble satt før kjøring. Modellvalget er ført inn i PRD, arkitektur (AD-7) og epics. | Gruppen gjennomgår agentens logger. Koble implementerte stories til PR-er og tester; modelltesten fullfører ingen story. |
| Funksjonalitet og omfang | 20 % | Komplett flyt fra valgt vakt til filtrerte og rangerte kandidater, forklaring og menneskelig valg. | [Omfang og suksesskriterier](../../product-brief.md). | Kontroller mot godkjent proposal. Implementer og demonstrer kjerneflyten, feil input og gjentatte handlinger før stretch goals. |
| Kvalitetssikring og testing | 15 % | Meningsfulle tester av harde regler, kostnad og sentrale integrasjoner, samt dokumentert gjennomgang. | [Modelltest](../ki-logg/2026-10-15-modelltest-haiku.md): 32 live svar, 20/24 riktige preferansekategorier, 8/8 faktatro forklaringer og 10/10 lokale tester av måleverktøyet. To agenter leste alle svar. [Beslutningstest](../ki-logg/2026-10-16-beslutningstest-haiku-luna.md): 1 020 live svar, 37/37 lokale tester av verktøyet, 99 manuelt kontrollerte flagg. [Robusthet og PRD-fasit](../ki-logg/2026-10-16-robusthet-luna.md): 218/218 kall levert med takt-politikk, 75/75 riktige på de 15 fasittekstene, 63/63 lokale tester. | Bygg AD-7 (takt og nye forsøk) i KI-adapteren med tester mot en falsk OpenRouter. Test harde regler og lekkasje-invarianten når appen bygges; de er ikke dekket av modellforsøket. |
| Design og brukeropplevelse | 10 % | Forståelig kandidatoversikt, begrunnelser og tilbakemeldinger til turnusansvarlig. | [DESIGN](../../_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md) og [EXPERIENCE](../../_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md) beskriver UX-valgene. | Implementer og verifiser tomtilstander, feilmeldinger, kontrast, tastaturbruk og skjermstørrelser. Rett språkfeil og oppdiktet kjønn i modellens preferansebegrunnelser før visning. |
| Kodekvalitet og arkitektur | 10 % | Tydelig skille mellom regelmotor, rangering, KI-forklaringer og brukergrensesnitt. | [Arkitektur](../../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md): React/TypeScript/Vite, Python/FastAPI, SQLite/SQLAlchemy og OpenRouter. Isolert modelltest finnes, appen mangler. | Implementer og kontroller at koden følger dokumentasjonen. Testverktøyets HTTP-klient er ikke et valg av appens klientbibliotek. |
| README og kjørbarhet | 10 % | Verifiserte kommandoer, versjoner, konfigurasjon, testdata og testinstruksjoner. | [README](../../README.md) lenker til [verifisert modelltestkommando](../modelltest-openrouter.md); [.env.example](../../.env.example) dokumenterer variablene uten verdier. | Appens installasjons-/kjørekommandoer og kontroll i ren klone gjenstår. Modelltest er ikke bevis på kjørbar app. |
| Ryddighet i repoet | 5 % | Tydelig skille mellom kode, dokumentasjon og ressurser; ingen hemmeligheter eller byggeartefakter. | [Gitignore](../../.gitignore), [original sensorveiledning](sensorveiledning-del-1.pdf), [agentinstruksjoner](../../AGENTS.md). | Kontroller sporede filer og historikk ved milepæler. Bekreft at nye dokumenter følger gruppens utsjekking. |

## Dokumentgjennomgang 2026-10-26

[Review av produktbriefen](../../_bmad-output/planning-artifacts/reviews/product-brief-2026-10-26.md) dokumenterer fire review-linser, kontroll mot PRD/arkitektur, ti innholdsfunn og redaksjonelle forslag. [Kildeundersøkelsen](../../_bmad-output/planning-artifacts/research/domain-turnushjelperen-produktbrief-2026-10-26/research.md) følger opp regler, eksisterende verktøy og rangering/brukerforståelse med 18 refererte kilder, kildekontroll og et etterprøvbart regneeksempel. Dette er prosess- og kvalitetssikringsbevis for kriterium 1 og 3, og peker på manglende forståelsestest under kriterium 4. Forslagene er ikke gjennomført; undersøkelsen gir ikke bevis for implementert funksjonalitet, validert brukernytte eller full juridisk etterlevelse. [KI-loggen](../ki-logg/2026-10-26-productbrief-review-research.md) beskriver prompt, leveranse, presiseringer og kontroll.

## Story 1.2 implementert 2026-11-03 (i branch, ikke merget)

[Spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-2-fiktiv-turnus-med-ansatte-og-vakter.md) følger gruppevedtakene AV-02, AV-03, AV-07, AV-09, AV-10 og AV-12 i [avklaringspunktene](../beslutninger/avklaringspunkter.md). Lagringen i `backend/adaptere/lagring/` har tre tabeller og fiktive testdata: 25 ansatte og 506 faste vakter, inkludert historikk fra 24.08. Det finnes også en forhåndsberegnet fasit for #4127 og #4189.

Bevis per kriterium:
- **Kriterium 3:** 34 tester i `backend/tester/lagring/test_testdata.py`, 35 med `test_helse`, og alle består. Testene sjekker:
  - at hver kandidat bryter nøyaktig regelen fasiten oppgir
  - at ingen ansatt bryter de fire reglene i egen turnus
  - Ulempepoeng for ulempescenarioet
  - inputene til rangeringsfasiten
  - at databasen avviser ugyldige rader

  Tre uavhengige gjennomgangsagenter fant 32 funn. Alle er vurdert i spesifikasjonens Review Triage Log: 12 er rettet og 14 avvist med begrunnelse.
- **Kriterium 1:** [KI-loggen](../ki-logg/2026-11-03-testdata.md) har prompten, leveransen, rettelsene og kladdeskriptene som dataene ble laget med.
- **Kriterium 6:** testdatakommandoen er dokumentert i README og AGENTS.md.

Ikke dokumentert ennå:
- gjennomgang i gruppa av PR-en
- at gruppa godtar resultatet av KS-04. Datadekningen er kontrollert og låst med en test for #4127 og #4189. Begrensningen er at det ikke finnes vakter etter 05.10.
- test fra en ren klone (OP-05). Fysisk test på macOS/Linux er strøket 2026-11-07, fordi verken sensor eller noen i gruppa har Mac.
- gjennomgangen av agentoppsettet i OP-04. `bmad-build` er kjørt med underagenter uten den, og avviket står i KI-loggen.

## Rutine ved milepæler

1. Sammenhold levert funksjonalitet med godkjent proposal og gjeldende plan.
2. Oppdater radene med lenker til konkrete endringer, testresultater og kvalitetssikring.
3. Noter mangler og neste tiltak; ikke beskriv planlagt arbeid som gjennomført.
4. Kontroller README i rent miljø og dokumenter utfallet.
5. Bruk originalveiledningens nivåbeskrivelser til å finne svakheter; prioriter stabil kjerneflyt og etterprøvbar prosess.

## Story 1.3 implementert 2026-11-07 (i branch, ikke merget)

[Spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md) besvarer OP-10 og følger AV-13 og AV-14 i [avklaringspunktene](../beslutninger/avklaringspunkter.md). Turnusansvarlig logger inn med brukernavn og passord (FR13). Sesjonen er ett JWT i en `httpOnly`-cookie, og alle feil har formen `{ kode, melding }` (AD-4). Frontend har designtokens, appbar, innloggingsflate og en foreløpig startside.

Bevis per kriterium:
- **Kriterium 3:** 111 tester i `backend/` består, både med og uten `TURNUSHJELPEREN_PASSORD` satt. Av dem er 56 i `tester/api/test_innlogging.py` og 16 i `tester/lagring/test_brukere.py`. Testene dekker hele I/O-matrisen i spesifikasjonen, blant annet:
  - cookieattributtene og levetiden til tokenet
  - at feil brukernavn og feil passord gir samme svar og hashes like mange ganger
  - `alg: none`, HS512, feil nøkkel, utløpt token og slettet bruker
  - at 422-svaret aldri gjentar passordet
  - 404, 405 og 500

  En mutasjonskontroll med fire endringer ga røde tester hver gang. Tre uavhengige gjennomgangsagenter fant 25 funn. Alle er vurdert i spesifikasjonens Review Triage Log (#12–#36): 13 er rettet, 1 er utsatt og 11 er avvist med begrunnelse.
- **Kriterium 1:** [KI-loggen](../ki-logg/2026-11-06-innlogging.md) har prompten, leveransen, valgene agenten tok, rettelsene etter gjennomgangen og de manuelle testene.
- **Kriterium 4:** manuelle tester i Chrome av innloggingsflaten, feil passord, gjeninnlasting, backend nede, fokusramme, 1600px og 360px, og 20px rotskrift. Testene er gjort av agenten. Johannes har logget inn bare med tastaturet (tab og enter) på et ekte tastatur, med forventet resultat (2026-11-07, KI-loggen).
- **Kriterium 6:** README har nummererte steg for installasjon, testdata med personlig eller tilfeldig passord (PowerShell og bash), backend og frontend. Variablene er dokumentert uten verdier i [.env.example](../../.env.example).
- **Kriterium 7:** passordet lagres bare som scrypt-hash, og JWT-nøkkelen finnes bare i minnet. Ingen hemmeligheter ligger i repoet.

Ikke dokumentert ennå:
- gjennomgang i gruppa av PR-en
- 20px standard skriftstørrelse med innstillingen i nettleseren og 360px vindusbredde. Agenten simulerte begge.
- test fra en ren klone (OP-05). Fysisk test på macOS/Linux er strøket 2026-11-07. Bash-kommandoene i README er kontrollert i Git Bash på Windows.
