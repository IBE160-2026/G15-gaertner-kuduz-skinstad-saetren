# Rubrikkgjennomgang av arkitekturspine — 2026-11-14

## Vurdering

Arkitekturen dekker hovedgrensene mellom deterministisk domene, lagring, API og KI, og de fleste nyere P-vedtakene er allerede tatt inn. To grenseflater trenger presisering før de tilhørende storyene bygges. Én teknologirad er foreldet som dokumentasjon.

## Funn

### 1. Godkjenning mangler bindende transaksjonsgrense

**Sted:** `ARCHITECTURE-SPINE.md` AD-4, AD-5 og Capability → Architecture Map; PRD §4.6, FR-12; `epics.md` Story 3.2.

**Utløser:** To samtidige godkjenningskall kan begge lese samme ledige vakt og bestå ny regelkontroll før noen av dem skriver. AD-5 krever én skrivefunksjon, men sier ikke at regelkontroll, kontroll av uendret beslutningsgrunnlag og skriv skjer mot én konsistent databasetilstand. AD-4 krever ny bekreftelse når grunnlaget endres, men definerer ikke hvordan API og lagring oppdager en endring mellom visning og lagring.

**Konsekvens:** To enheter kan implementere hver sin lovlige del av AD-ene, men likevel lagre en dobbelt godkjent eller utdatert beslutning. Kravet om én godkjenning per vakt og P-09 kan da brytes.

**Forslag:** Bind Story 3.2 til en atomisk godkjenningsoperasjon i lagringsadapteren med entydig vakt per godkjenning, kontroll av gjeldende grunnlag og avvisning ved konflikt. Avklar hvordan API-et sender eller gjenfinner grunnlagets versjon før implementasjon. Dette er en arkitekturbeslutning fordi API og lagring ellers kan velge inkompatible strategier.

### 2. KI-invarianten blander preferansetolkning og forklaring

**Sted:** `ARCHITECTURE-SPINE.md` AD-1 og AD-6; PRD §4.5 (FR-10/FR-11) og SM-2.

**Utløser:** AD-1 sier både at ingen utelukket kandidat-ID skal nå KI-porten, og at `adaptere/ki` tolker ansattpreferanser før rangering, eventuelt i bakgrunnen når testdata lastes. Ansatte som senere utelukkes, kan dermed få preferansetekst tolket. PRD §4.5 sier at KI får filtrerte data, men beskriver samtidig tolkning før rangering. SM-2 gjelder uttrykkelig at en utelukket kandidat aldri *anbefales* av KI.

**Konsekvens:** Story 5.1 og 5.6 kan skrive motstridende tester og dataflyter: den ene sender alle ansattpreferanser til tolkning, den andre avviser enhver KI-portbruk for en senere utelukket ansatt.

**Forslag:** Skill invariantene: tolkning av en ansatts egen preferanse kan skje før filtrering uten kandidatstatus; forklaringsporten mottar bare gyldige, ferdig beregnede kandidater og kan aldri anbefale eller nevne utelukkede. La kjøretidstesten i Story 5.6 kontrollere forklaringsporten og KI-output presist. Hvis gruppa faktisk vil forby tolkning av utelukkede ansatte, må tolkningens tidspunkt endres eksplisitt i PRD og AD-1.

### 3. Stack-raden for SQLAlchemy er foreldet

**Sted:** `ARCHITECTURE-SPINE.md` Stack og Deferred; `backend/requirements.txt`.

**Utløser:** Spinen sier at SQLAlchemy-versjon ikke er fastsatt, mens `backend/requirements.txt` låser `sqlalchemy==2.1.6`.

**Konsekvens:** En leser kan behandle et gjennomført teknologivalg som åpent. Her eier koden den konkrete versjonen, slik skillens seed-regel også legger opp til.

**Forslag:** Ved senere Update, fjern det åpne versjonspunktet eller lenk til pakkelåsen som gjeldende kilde; ikke gjør versjonen til en ny arkitekturinvariant.

## Kontrollert og ikke funnet som avvik

- AV-17s skille mellom mobil/nettbrett i v2 og smale datamaskinvinduer i v1 er tatt inn under Deferred.
- OP-16s komponenttester er tatt inn i Testing-raden og Stack.
- P-05s åpne feilbudsjett for preferansetolkning er korrekt holdt atskilt fra AD-7s 90 sekunder for avveining.
- AD-3s cookie-kontrakt stemmer med implementasjonen i `backend/adaptere/api/sesjon.py` og `frontend/src/api.ts`.

**Avgrensning:** Dette er en arkitekturrubrikk, ikke full kodegjennomgang eller kontroll av alle konkrete versjoner mot internett.
