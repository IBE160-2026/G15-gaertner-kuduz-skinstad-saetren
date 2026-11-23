# Gjennomgang mot sensorveiledningen

## 2026-11-23 kl. 14:23 — Ragnhild

### Oppgave
Ragnhild ville vite hvordan gruppa ligger an mot sensorveiledningen for del 1. Analysen skulle dekke hele arbeidet. Økten var først tenkt uten endringer, men analysen viste at mye bør ryddes opp i. Funnene tas derfor ett og ett, og alle endringer logges her.

### Plan
- Les `docs/emne/sensorveiledning-del-1.md` og `docs/emne/vurderingsmatrise.md`.
- Hent faktisk status: sprintstatus, PR-er og gjennomganger (`gh`), commit-fordeling per uke og person, README, sporede filer og hemmeligheter.
- Kjør alle testene på `main`.
- Sett et begrunnet karakteranslag per kriterium og en prioritert liste med tiltak.
- Gå gjennom tiltakene ett og ett sammen med Ragnhild.

### Resultat
**Analyse (ingen endringer):**
- Testene på `main` bestod: 844 backendtester, 52 modultester, 70 komponenttester og frontendbygget.
- Anslag etter sensorveiledningens skjema: Prosess A, Funksjonalitet B, Kvalitetssikring A, Design B, Kodekvalitet B, README B, Ryddighet B. Det gir 4,45, altså B rett under grensen for A (4,5). Dette er et anslag, ikke en garanti.
- Svakheter som ble funnet:
  - Demo-modus (5.7) er ikke merget. Uten den ser sensor KI-delen bare som reservetekst.
  - Oversiktstabellen i vurderingsmatrisen var utdatert.
  - README mangler en kort beskrivelse av appen, skjermbilde og mappeoversikt.
  - P-13 med en person utenfor gruppa er ikke gjennomført.
  - Ingen linter er satt opp.
  - Det ligger en løs fil i roten.
  - Omtrent 630 av drøye 700 commits er fra 2.–22. november.
  - Det finnes bare én sak i GitHub Issues.
- Samarbeid: alle fire har committet kode (Johannes 23, Kim 19, Ragnhild 13 og Mithad 9 commits i `backend/`/`frontend/`). 28 av 39 PR-er har en registrert gjennomgang på GitHub.

**Punkt 1, demo-modus (PR #38):** Ragnhild opplyste at punktet er under arbeid. Ingenting endret.

**Punkt 2, vurderingsmatrisen:**
- Oversiktstabellen i `docs/emne/vurderingsmatrise.md` er skrevet om, både «Bevis» og «Gjenstår», til status på `main` 2026-11-23. Ragnhild godkjente utkastet før det ble lagt inn. Innledningen sier nå at tabellen er oppdatert 23.11.
- To formuleringer er fjernet: «Gruppen gjennomgår agentens logger» (uklart om det er gjort) og merknaden om HTTP-klienten i modelltesten.
- Kjønnspunktet er flyttet fra «Gjenstår» til «Bevis», fordi robusthetstesten av Luna fant 0 brudd.
- Alle lenkede filer er kontrollert. Committet på `main` i `4aad46d`, ikke pushet.

**Punkt 3, README (plan, ingen endringer):**
- Hele README er lest og kontrollert mot koden.
- Feil som ble funnet:
  - «Kandidatlisten kommer i Epic 2» står fortsatt.
  - Kandidatene beskrives som «alfabetisk», men de har vært rangert siden 4.4.
  - Rangering, kostnad, ulempe, KI-avveining (5.3), reservetekst (5.4) og avviksnotat (4.5) er ikke beskrevet.
  - API-beskrivelsen har gamle svarformater og mangler endepunktene for avveining og «Prøv igjen».
  - Vite-sårbarheten vises til OP-16, men vedtaket står i §11 i referatet (14.11).
  - Testtallene er gamle.
- Foreslått struktur, i ti seksjoner: om appen, medlemmer, forutsetninger, kom i gang, slik bruker du appen, konfigurasjon, tester, feilsøking, mappestruktur, planlegging og prosess.
- Hvor innholdet flyttes:
  - API-beskrivelsen og KI-driftsdetaljene til én ny fil, `docs/teknisk-referanse.md`.
  - Testdetaljene til `docs/testing.md`.
  - Gamle testtall fjernes, siden de allerede står i matrisen og i OP-05.
- Bestemt av Ragnhild: oppryddingen venter til PR #38 er merget, fordi den PR-en også endrer README med 35 linjer. Arbeidet skal gjøres i en branch med PR.
- Sensorutkastet `docs/innlevering/til-sensor-innlogging.md` (Johannes, 07.11, ikke godkjent) er gjennomgått. Det tas stilling til når den nye README er skrevet: kortes ned med rettede lenker, eller slås inn i README etter avtale med Johannes. Johannes har det som åpent punkt i sin `issues.md`.

**Punkt 3, README (gjennomført etter at PR #38 ble merget, `8a9bdfc`):**
- Appen ble kjørt uten nøkkel mot en egen testdatabase før skrivingen. Demo-modus tolket alle 19 preferansetekstene, rangeringen for #4127 ble Jonas, Mette, Thomas, Ingrid, og avveiningen ga `ki_kilde: forhandsgenerert`. #4189 ga 0 gyldige og 24 utelukkede.
- `README.md` er skrevet om etter planen, fra ca. 2 900 til 1 450 ord.
- Ny fil `docs/teknisk-referanse.md` samler API-et, KI-integrasjonen (modusvalg, takt og nye forsøk, demo-modus, macOS-sertifikater) og databasen, kontrollert mot `backend/adaptere/api/main.py`.
- `docs/testing.md` har fått to testdetaljer fra README.
- Kontroll:
  - README-stegene er fulgt i en ren klone (Python 3.15.2, Node 26.8.1), med innlogging gjennom Vite-proxyen.
  - `npm audit` melder fortsatt 1 høy sårbarhet, slik README sier.
  - Alle relative lenker og ankre i de tre filene virker.
- Ragnhild valgte å committe rett på `main` i stedet for PR, siden det bare er dokumentasjon, og hun hadde varslet gruppa. Committet i `87db4d9`.
- Skjermbilde er ikke med. Det er ikke et krav («gjerne» i kriterium 6) og tas eventuelt rett før innlevering.

### Åpne punkter
- Sensorutkastet `docs/innlevering/til-sensor-innlogging.md` lenker til to README-overskrifter som har fått nye navn, og lenkene er brutte. Det må avklares med Johannes.
- Testtallene i tabellen i `docs/testing.md` er fra 2026-11-14.
- Punkt 4 og 5 fra analysen (P-13 og linter/rotfil) gjenstår.
