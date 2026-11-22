# E-02: forberedt sammenligning med godkjent proposal

**Forberedelse 22.11.2026, ikke sluttkontroll.** Godkjent proposal er
`ee6d79833967ad0d6638aca9476ff46cf762a2b2:product-brief.md`, identifisert i E-02 i
[beslutningsreferatet](../beslutninger/avklaringspunkter.md#12-prd-vedtak-2026-11-09-og-status-ved-dokumentsamordning).
Innholdet er lest direkte fra git, ikke fra dagens endrede brief. Den opprinnelige
filens `draft`-metadata endrer ikke gruppas identifikasjon av godkjent proposal.

Før endelig kontroll: før inn full commit-ID for siste leverte versjon før fristen,
kontroller README i rent miljø, kjør testene og de faktiske kjerneflytene på akkurat
den versjonen, og dater vurderingen av hvert punkt nedenfor. Ta med begrunnede
utsettelsesvedtak. Ikke bruk en senere grønn utviklingsversjon som leveringsbevis.

| Løfte i proposal | Bevis som finnes nå | Hva må kontrolleres ved innlevering |
| --- | --- | --- |
| Eksisterende fiktiv turnus med omtrent 20–30 ansatte | 25 ansatte og faste vakter; story 1.2, `backend/tester/lagring/test_testdata.py`, AV-07/KS-04 | Gjenskap testdata fra README i rent miljø. |
| Velge én vakt som må bemannes | Vaktvalg og vaktdetaljer, stories 1.5/1.6, komponent-/API-tester | Følg kjeden fra innlogging til #4127 og #4189. |
| Filtrere alle brudd på implementerte harde regler | Story 2.1–2.6, én testmodul per regel, positiv egen-turnus-kontroll, #4127/#4189-fasit | Kjør regel-/fasittestene; behold avgrensningen til fire prototyperegler. |
| Utelukkede skal aldri anbefales av KI | Story 5.6, `test_lekkasjeinvariant.py`, PR #36 | Kjør også demo-grenen etter 5.7; den er fortsatt utsatt i dagens bevis. |
| Kort rangert liste uten manuell kontroll av alle ansatte | Story 4.4, fem øverste og «Vis alle», AV-15/SM-3 | Verifiser ferdig beregning, ingen gyldige og datafeil som ulike utfall. |
| Hvorfor kandidaten kan ta vakten, hva som trekker opp/ned, kostnad og preferanser | Story 5.3, faktakontrollerte påstander, egen total, valgt referanse (P-06/P-07) | Kontroller endelig 5.4-reservetekst, faktisk live og demo, og forståelsesprøven. |
| Samme strukturerte input gir samme harde regler og kostnad | Domenetester og eksakt rangering med Fraction (K-03/AV-05) | Kjør determinisme-, tidssone-, sommertids- og grensetestene. |
| Billigste er ikke nødvendigvis øverst | Uavhengig #4127-fasit og `test_rangering.py`, KS-02/AV-12 | Bekreft fasiten med og uten lagret tolkning; ikke les forventningene fra programresultatet. |
| KI tolker definerte tekstpreferanser og forklarer | Story 5.1/5.2/5.3, tester med falsk OpenRouter og tidligere modellforsøk | Kjør valgt sensoropplegg og dokumenter faktisk forbruk uten hemmeligheter. |
| Mennesket velger og godkjenner | Story 3.2 med varig lagring og P-09; komponent-/API-tester | Bekreft godkjenning, endret grunnlag og allerede bemannet mot ekte backend. |
| Enkel innlogging for turnusansvarlig | Story 1.3/1.4, beskyttede ruter og sesjonstester | Følg README, kontroller feil passord, utløpt sesjon og ny oppstart. |

## Avgrensninger og planavvik som skal forklares

Proposal utelukker full juridisk garanti, full lønn/tariff, ekte persondata,
integrasjoner, helturnusoptimalisering, automatisk KI-godkjenning, ansattportal og
avansert rollemodell. Gjeldende produkt skal fortsatt beskrives med disse grensene.

Avtalte konkretiseringer: fire prototyperegler (AV-04), tilgjengelighetsantakelser og
preferanser for demoperioden (AV-06), modellert merkostnad og kalenderuker (P-01/P-02),
faste vekter og ulempetak (AV-11), fem preferansekategorier, faktakontrollerte påstander
med merket reserve (P-06) og startuke versus 672-timershistorikk (AV-03/AV-09).
Dette er konkrete modellvalg innenfor det brede løftet, ikke full lønns- eller lovmodell.

Åpne leveringsavklaringer: 5.4 er i PR #37, 5.5/5.7/5.8 står i backlog, 5.9 venter
levering eller dokumentert utsettelse, sensornøkkel/betaling/kreditt venter gruppevalg,
og ekstern P-13 samt lokal problemvalidering gjenstår. Mobil/nettbrett er v2 etter
AV-17; smale skrivebordsvinduer er fortsatt v1. Godkjenning lagres, men vist forklaring
lagres ikke historisk (P-12). Endelig vurdering må skille godkjente avgrensninger fra
funksjoner som mangler uten vedtak.

## Sluttkontroll ved levering

- Innleveringscommit, full ID: **ikke fastsatt**.
- Dato og utfører: **gjenstår**.
- Rent miljø / README-bevis og testresultater: **gjenstår for innleveringsversjonen**.
- Faktisk leverte funksjoner, vedtatte utsettelser og begrunnelse per avvik: **gjenstår**.
- E-02-status: **åpen**.
