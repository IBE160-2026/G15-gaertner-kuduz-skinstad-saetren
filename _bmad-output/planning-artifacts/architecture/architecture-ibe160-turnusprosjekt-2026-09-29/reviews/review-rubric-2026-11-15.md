# Rubrikkgjennomgang av arkitekturspinen — 2026-11-15

## Dom

**Bestått med dokumentpresiseringer og tydelige implementasjonsporter.** Spinen dekker hovedgrensene for v1 og de seks sakene fra 14.11 er tatt inn i den oppdaterte teksten. Denne gjennomgangen bygger på dagens arbeidsfil, ikke den gamle valideringsrapporten. Jeg fant ingen påvist kodefeil i de kontrollerte kodestykkene. Ett utsagn om lagring av innloggingssesjon motsier den vedtatte og implementerte JWT-modellen.

## Metode og kilder

Jeg gikk systematisk gjennom Reviewer Gates «Good-spine checklist»: faktiske divergenspunkter, håndhevbare AD-regler, Deferred, teknologibeslutninger mot koden, dekning av PRD/UX, og drifts- og miljødimensjonen. Kilder: [spinen](../ARCHITECTURE-SPINE.md), [memlog](../.memlog.md), [brief](../../../../../product-brief.md), [PRD](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md), [epics](../../../epics.md), [UX-opplevelse](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md), [beslutningsreferatet](../../../../../docs/beslutninger/avklaringspunkter.md), [sensorveiledningen](../../../../../docs/emne/sensorveiledning-del-1.md), samt `backend/adaptere/api/sesjon.py`, `backend/adaptere/lagring/modeller.py`, `backend/pyproject.toml` og `backend/requirements.txt`. Teknologinyheter og nøyaktige leverandørparametre ligger til egen teknologireviewer.

## Funn

### R-1 — Medium · dokumentfeil · presiser ved senere Update

**«Innloggingssesjon» står som varig lagret entitet uten tilsvarende sesjonstabell.** Spinen sier at `adaptere/lagring` persisterer innloggingssesjon ([spine linje 37](../ARCHITECTURE-SPINE.md#L37)), mens AD-3 beskriver ett JWT i nettlesercookie med tilfeldig signeringsnøkkel per oppstart og utlogging ved omstart ([linje 69–73](../ARCHITECTURE-SPINE.md#L69)). I dagens kode finnes bare tabellene `turnus`, `ansatt`, `vakt` og `bruker` (`backend/adaptere/lagring/modeller.py` linje 52–136), og sesjonen håndteres i `backend/adaptere/api/sesjon.py` linje 44–99. `epics.md` linje 290–305 beskriver også JWT/cookie og brukertabellen. En ny implementatør kan ellers legge til unødvendig sesjonslagring eller anta at utlogging tilbakekaller token i databasen. Juster tabellens beskrivelse til at lagring eier bruker og passordhash, mens API-et eier JWT-sesjonen; behold AD-3. Ingen kodefeil er påvist.

### R-2 — Lav · dokumentfeil · enkel tekstkorreksjon

**Kildetreet kaller `.env.example` «udokumenterte miljøvariabler».** Kommentaren på [spine linje 181](../ARCHITECTURE-SPINE.md#L181) motsier [spine linje 110](../ARCHITECTURE-SPINE.md#L110), `AGENTS.md` Policy og `epics.md` NFR7 linje 45, som alle krever dokumenterte variabelnavn uten verdier. Rett ordet ved en senere Update; ingen prosjektfil ble endret her.

### R-3 — Medium · åpent implementasjonskrav, ikke dokumentfeil

**Godkjenningskontrakten må gjøres konkret og testes i story 3.2.** AD-5 binder én skrivevei, beslutningsgrunnlagets identitet, felles konsistent databasetilstand og unik Godkjenning per Vakt ([spine linje 83–87](../ARCHITECTURE-SPINE.md#L83)); dette håndterer den gamle grenseflatefeilen på arkitekturnivå. Valg av transaksjonsmekanisme, konfliktkode og beslutningsgrunnlagets konkrete representasjon er uttrykkelig utsatt til story 3.2. `epics.md` linje 659–680 krever samtidighetstester og avvisning ved endret grunnlag. Rapporter derfor disse som akseptansekrav som gjenstår, ikke som feil i AD-5 eller som gjennomførte tester. `backend/adaptere/api/main.py` har i dagens utsnitt bare GET-grunnlaget for story 3.1 (linje 294–319), og `frontend/src/komponenter/Godkjenningsflate.tsx` linje 18 sier at ingen skriving skjer før 3.2.

### R-4 — Medium · åpent implementasjonskrav, ikke dokumentfeil

**KI-kontrakten er riktig avgrenset, men ikke implementert.** AD-1 skiller teksttolkning før filtrering fra forklaring etter Rangering ([spine linje 24–30 og 47–50](../ARCHITECTURE-SPINE.md#L24)), og AD-6 inkluderer referansens ID, sammenligningsfakta og kontraktsversjon i demo-oppslag ([linje 89–96](../ARCHITECTURE-SPINE.md#L89)). Dette samsvarer med PRD FR-10/FR-11 (linje 300–345) og `epics.md` story 5.3/5.6/5.7 (linje 1042–1051, 1136–1150, 1171–1179). Konkrete porter, negativtester og faktakontroll hører fortsatt til storyene. Ikke tell dokumentets regler som testbevis for at KI-output faktisk overholder dem.

## Kontrollert uten avvik

- **Divergens og håndheving:** AD-1/AD-2 setter en klar import- og kjøreretning; dagens `backend/pyproject.toml` har forbud mot at hele `domene` importerer `adaptere`. AD-4 definerer API-feilform og at frontend eier brukerteksten. AD-5 eier mutasjon og transaksjonsgrense. AD-3 har riktig cookie-eierskap: API-et setter, nettleseren lagrer/sender, webklienten leser ikke token ([spine linje 69–79](../ARCHITECTURE-SPINE.md#L69)); dette samsvarer med `backend/adaptere/api/sesjon.py` linje 73–99 og `frontend/src/api.ts` linje 1–2.
- **Seks tidligere saker:** konsistent Godkjenning (AD-5), tolkning/forklaring (AD-1), referansefakta i demo (AD-6), SQLAlchemy peker til låst manifestversjon 2.1.6 (Stack, `backend/requirements.txt`), OpenRouter-ruting spesifisert med leverandør uten fallback og falsk klienttest (AD-7), og cookie-eierskap (AD-3). Dokumenttilstedeværelse er kontrollert her; faktisk OpenRouter-parameter og gjeldende eksterne versjoner vurderes av teknologirevieweren.
- **Omfang og Deferred:** PRD-flytene FR-1–FR-14 har en plass i Capability Map, med FR-10/FR-11 eksplisitt delt. Hosting, runtime-logging, klientbibliotek og migrering er åpne på [spine linje 196–210](../ARCHITECTURE-SPINE.md#L196); lokal kjøring er uttrykkelig valgt [linje 143](../ARCHITECTURE-SPINE.md#L143). Preferansetolkningens egne forsøk og sluttstatus står åpent uten å arve Avveiningens 90 sekunder. Dette er riktig nivå for et lokalt prosjekt på initiativnivå.
- **Plan–kode-sporing:** Dagens kode implementerer autentisering, lagring, fire hardregelmoduler og en første kandidat-/godkjenningsflate; den viser ikke ferdig Godkjenning eller KI-port. Sensorveiledningens kriterier 1, 3 og 5 (prosess/ki-styring, kvalitetssikring, samsvar mellom arkitektur og kode) støtter at rapporten skiller plan fra bevis.

## Avgrensning

Dette er en dokument- og kodekontroll av relevante grensesnitt, ikke full testkjøring eller nettlesergjennomgang. Teknologirevieweren kontrollerer versjoner og OpenRouter-ruting uavhengig. Ingen arkitektur-, plan- eller kodefiler ble endret.
