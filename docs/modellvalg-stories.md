# Modellvalg per story

Anbefaling for hvilken Claude-modell en story bygges med i `bmad-build`, for å
spare bruksgrensen uten å svekke kvalitetssikringen der feil er dyre. Foreslått
av Johannes 2026-11-10. Ikke drøftet i gruppa ennå — er dere uenige, endre tabellen.
`bmad-build` leser denne filen og sier fra om anbefalingen ved oppstart
(`_bmad/custom/bmad-build.toml`).

## Regel

- **Opus 5.5:** feil er dyre og vanskelige å oppdage — harde regler, beregninger,
  godkjenning og KI-kontrakter, eller grunnmønstre andre stories bygger på.
- **Sonnet 5.5, gjennomgang med Opus:** middels risiko der spesifikasjonen gir
  grensetilfellene. Implementer med Sonnet; minst én gjennomgangsagent kjører Opus.
- **Sonnet 5.5:** følger et mønster som allerede finnes, og feil synes med en gang —
  UI-flater, tekster og visning av ferdig beregnede data.

## Stories

| Story | Modell | Hvorfor |
|---|---|---|
| Samordning av PRD-vedtakene (correct course) | Opus | Mange dokumenter må holdes konsistente |
| 2.1 Kompetanse og minstekrav | Opus | Første regel, legger mønsteret for regelmotoren |
| 2.2 Kolliderende vakt | Sonnet | Enkel overlapp, intervallmodellen finnes |
| 2.3 11-timersregelen | Opus | Sommertid, halvåpne intervaller, grensetilfeller |
| 2.4 35-timersregelen | Opus | Som 2.3 |
| 2.5 Ekskludert-boks | Sonnet | UI over regelmotorens resultat |
| 2.6 Ingen gyldige kandidater | Sonnet | UI |
| 3.1 Godkjenningsflaten | Sonnet | UI etter eksisterende mønster |
| 3.2 Godkjenning og bemanning | Opus | Ny kontroll, varig lagring, dublettvern (FR-12, P-09) |
| 4.1 Timer i perioden | Sonnet, gjennomgang med Opus | Kalenderuke i Oslo-tid |
| 4.2 Belastningslinje med terskel | Sonnet | Visning, terskelen 32,4 t er vedtatt |
| 4.3 Forenklet kostnad | Opus | Ukefordeling og overtid (P-01–P-03) |
| 4.4 Rangering | Opus | Normalisering og likhetsregler (AV-05, AV-12) |
| 4.5 Avviksnotat og nøkkeltall | Sonnet | Visning |
| 4.6 Rangeringstabell på smale skjermer | Sonnet | Layout |
| 4.7 Ulempebelastning | Opus | 672-timersvindu, KS-03 må være gjort |
| 5.1 Tolke preferanser med KI | Opus | KI-kontrakt, feilstatus (P-05), begrenser (AD-7) |
| 5.2 Rangering med tolkede preferanser | Sonnet, gjennomgang med Opus | Bygger på 4.4 og 5.1 |
| 5.3 Avveining per kandidat | Opus | Faktakontroll av forklaringer (P-06) |
| 5.4 Reservetekst | Sonnet | Avgrenset |
| 5.5 Rader før forklaringene | Sonnet, gjennomgang med Opus | Transport og samtidighet |
| 5.6 Utelukkede når aldri KI-laget | Sonnet, gjennomgang med Opus | Sikkerhetsgaranti |
| 5.7 Demomodus | Sonnet | Konfigurasjon |
| 5.8 Live-KI for sensor | Sonnet | Konfigurasjon og dokumentasjon |

Står en story ikke i tabellen, for eksempel P-10B, bruk regelen over og før den inn her.

## Ellers

- Rutinearbeid i en Opus-økt — sesjonslogg, commits, README, sprintstatus — kan
  gjøres etter `/model sonnet`.
- Ett nytt kontekstvindu per story.
