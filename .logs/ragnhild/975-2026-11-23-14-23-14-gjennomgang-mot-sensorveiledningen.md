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

### Åpne punkter
Punkt 3–5 fra analysen (README, P-13 og linter/rotfil/agentmapper) gås gjennom videre i denne økten og føres i loggen etter hvert.
