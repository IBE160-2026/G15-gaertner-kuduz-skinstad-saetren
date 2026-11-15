# Uavhengig grenseflatekontroll — 2026-11-15

## Vurdering og metode

**AD-5 og AD-6 lukker de viktigste grenseflatehullene fra 14. november, men to mindre kontraktmotsetninger står igjen.** Jeg leste den endrede `ARCHITECTURE-SPINE.md` direkte og sammenholdt den med `product-brief.md`, gjeldende PRD, `epics.md`, UX, beslutningsreferatet og eksisterende sesjons-/godkjenningskode. Tidligere rapport er bare brukt til å identifisere de seks kontrolltemaene. Dette er en dokument- og kodeinspeksjon; fremtidige storyer og tester er ikke antatt gjennomført. Sensorveiledningens krav om samsvar mellom plan og kode samt sporbar kvalitetssikring er relevante (`docs/emne/sensorveiledning-del-1.md:85-108`, `:229-252`).

Jeg forsøkte å bygge to enheter som hver følger AD-ene, men ikke fungerer sammen. Der de kan divergere fordi en kontrakt med vilje er utsatt til en story, klassifiserer jeg det som **åpent implementasjonskrav**, ikke som påvist dokument- eller kodefeil.

## Funn

### G1 — Lagringsrollen lover en innloggingssesjon som den vedtatte løsningen ikke lagrer

**Alvorlighet:** middels. **Kategori:** dokumentfeil, også i `epics.md`; ingen påvist kodefeil.

Spinen sier at `adaptere/lagring` persisterer «innloggingssesjon» (`ARCHITECTURE-SPINE.md:37`). AD-3 binder derimot ett JWT i nettlesercookie med tilfeldig signeringsnøkkel i API-prosessens minne, og alle logges ut ved omstart (`:69-73`). Den faktiske koden har tabellene `turnus`, `vakt`, `ansatt`, `bruker` (`backend/adaptere/lagring/modeller.py:52-135`); tokenet lages og verifiseres i `backend/adaptere/api/sesjon.py:44-65`, og API-et setter/fjerner cookien der (`:73-99`). `epics.md:80` gjentar lagring av «innloggingssesjon/bruker», mens Story 1.3 (`epics.md:292-305`) og OP-10 (`docs/beslutninger/avklaringspunkter.md:563-574`) beskriver den statsløse JWT-løsningen.

**Adversarial par:** En utvikler av lagringsadapteren legger til en sesjonstabell og forventer at API-et skriver sesjoner der, i tråd med rolletabellen. API-utvikleren følger AD-3 og setter bare JWT-cookie. Tabell og repository blir ubrukte, og dokumentet gir to ulike sannheter om varig sesjonstilstand. Ved en senere Update bør rolletabellen si at lagring eier bruker/passordhash, mens API og nettleser eier tokenflyten. Rett også `epics.md:80` ved en særskilt, godkjent Update; endre ikke AD-3 eller eksisterende kode for å oppfylle en foreldet setning.

### G2 — «Kun KI konstruerer» kolliderer med lesing av lagret preferansetolkning

**Alvorlighet:** middels. **Kategori:** dokument-/kontraktfeil; ingen påvist kodefeil fordi story 5.1 ikke er implementert.

AD-1 sier både at vellykket `TolketPreferanse` caches/persisteres per Ansatt/tekst og at **kun** `adaptere/ki` konstruerer en vellykket instans (`ARCHITECTURE-SPINE.md:48-50`). Story 5.1 gjentar konstruktørkravet (`epics.md:975-979`), men krever samtidig at `adaptere/lagring` lagrer tolkningen, og at Rangering alltid leser lagret verdi uten live-kall (`epics.md:982-986`); PRD FR-10 forutsetter lagret tolkning og ny beregning ved endret tekst (`prd.md:294-298`).

**Adversarial par:** KI-adapteren oppretter og lagrer den validerte modellen én gang. Lagringsadapteren får ikke konstruere modellen ved uthenting etter omstart, og kan derfor bare returnere en annen form; Rangering forventer derimot `TolketPreferanse` etter AD-1. En alternativ implementasjon lar KI-adapteren rekonstruere modellen fra DB-data, men gir KI-adapteren en lagringskobling som svekker den eksplisitte portgrensen. Ved Update bør regelen skille **semantisk tolkning** (bare KI-adapteren bestemmer kategorien) fra **deserialisering av en allerede lagret, validert verdi** (lagringsadapteren kan rekonstruere porttypen uten ny tolkning). Story 5.1 må samordnes.

### G3 — Kildelinjens modell og dato må bæres gjennom API-kontrakten

**Alvorlighet:** lav. **Kategori:** åpent implementasjonskrav, ikke dokumentfeil nå.

AD-6 krever `ki_kilde` og loggføring av modell/dato for forhåndsgenererte svar (`ARCHITECTURE-SPINE.md:95-96`). UX krever modellnavn for live-forklaring og modellnavn pluss dato for forhåndsgenerert forklaring (`EXPERIENCE.md:62`, `epics.md:149,1063`). Spinen utsetter fullt responsskjema per endepunkt (`ARCHITECTURE-SPINE.md:79,207`). En backend som bare sender `ki_kilde`, og en frontend som følger UX-teksten, kan derfor mangle metadata ved visning. Story 5.3/5.7 må definere hvor modell og genereringsdato kommer fra og teste at kildelinjen ikke gjetter dem. Dette er en konkret grenseflatekontroll før disse storyene er `done`, ikke en nåværende kodefeil.

### G4 — Miljødiagrammet sier HTTPS der den vedtatte lokale flyten bruker HTTP

**Alvorlighet:** lav. **Kategori:** dokumentpresisjon.

Containerdiagrammet merker Web–API som «HTTPS/JSON, JWT» (`ARCHITECTURE-SPINE.md:131-140`), mens kjøremiljøet er lokalt (`:143`), Vite bruker `/api`-proxy (`epics.md:318`), og lokal cookie er bevisst `secure=False` for HTTP (`backend/adaptere/api/sesjon.py:73-84`). Diagrammet bør ved Update uttrykke HTTP/JSON i lokalt miljø og HTTPS som krav dersom hosting senere velges. Ingen kodefeil følger av dagens lokale HTTP-oppsett.

## Seks tidligere funn, kontrollert på nytt

| Tema | Kontroll av nåværende spine | Klassifisering |
| --- | --- | --- |
| Konsistent Godkjenning | AD-5 krever én skrivevei, samme databasetilstand for kontroll og skriving, ny kontroll av fire regler og unik Godkjenning per Vakt (`:83-87`). Story 3.2 krever samtidighetstester (`epics.md:651-688`), mens koden foreløpig bare har visningsflate og GET-grunnlag (`backend/adaptere/api/main.py:294-316`, `frontend/src/komponenter/Godkjenningsflate.tsx:18`). | Tidligere dokumenthull lukket; implementasjonskrav åpent. |
| KI-tolkning / KI-forklaring | AD-1 skiller tolkning per Ansatt før filtrering fra forklaring bare for gyldige, rangerte Kandidater, og spesifiserer runtime-test (`:43-50`). Samme skille står i PRD FR-10/FR-11 (`prd.md:285-349`). | Tidligere dokumenthull lukket; G2 er separat konstruktørmotsetning. |
| Referansefakta i demo | AD-6 identifiserer hele grunnlaget inkludert referansens ID/fakta og kontraktversjon, faktakontrollerer forhåndssvaret og gir mal/reservetekst ved avvik (`:93-96`). Story 5.7 har test for endret referanse (`epics.md:1175-1179`). | Tidligere dokumenthull lukket; implementasjon åpen. |
| SQLAlchemy-versjon | Stack peker nå til faktisk lås i `backend/requirements.txt` (`:124`), uten å blande det med uavgjort migreringsverktøy (`:206`). | Tidligere dokumenthull lukket. |
| OpenRouter-ruting | AD-7 krever leverandør `openai`, ingen fallback og test av forespørselen mot falsk HTTP-klient (`:98-102`), i samsvar med Story 5.1 (`epics.md:980`). | Tidligere dokumenthull lukket; adapter/test åpen. |
| Cookie-eierskap | AD-3 sier API setter, nettleser lagrer/sender, web leser ikke token og bruker `credentials: "same-origin"` (`:69-73`). Koden samsvarer (`backend/adaptere/api/sesjon.py:73-99`, `frontend/src/api.ts:2,115`). | Tidligere dokumenthull lukket; ingen påvist kodefeil. |

## Grense og oppfølging

Jeg fant ingen påvist kjørende kodefeil i de seks kontrolltemaene. G1, G2 og G4 kan presiseres i en senere Update uten å endre etablerte AD-ID-er. G3 kan løses i de utsatte responsskjemaene for Story 5.3/5.7. Jeg har ikke kjørt en full applikasjons- eller samtidighetstest; slike tester ville ikke kunne verifisere kode som ennå ikke er bygget.
