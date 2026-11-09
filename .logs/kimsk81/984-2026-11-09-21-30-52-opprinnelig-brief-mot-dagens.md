# Opprinnelig brief mot dagens

## 2026-11-09 kl. 21:30 — Kimsk81

### Oppgave
Sammenligne den opprinnelige `product-brief.md` med dagens versjon i Git-historikken, som grunnlag for E-02 om endringer fra innlevert proposal.

### Plan
- Finne første commit og alle senere endringer av rotfilen med `git log --follow`.
- Sammenligne første commit `ee6d798` med HEAD og lese commitbegrunnelsene.
- Kontrollere E-02 og sensorveiledningen, samt om repoet dokumenterer hvilken versjon som faktisk ble levert og godkjent.

### Resultat
Første commit av `product-brief.md` er `ee6d798` fra 2026-09-16. Sammenligning med HEAD gir 26 innsettinger og 7 slettinger i én fil. Fem senere commits endret briefen: `a67760d`, `6db2d0f`, `49cb2d4`, `c307f5e` og `b7f793d`.

Vesentlige presiseringer er fire navngitte harde regler og kompetanse som bare minstekrav; deterministisk vekting 40/35/25 med arbeidsbelastning delt i timebelastning 20 og ulempebelastning 15; inntil fem kandidater og tomtilstand; fem preferansenivåer med 15 fasittekster; demo uten API-nøkkel; og eksplisitt avgrensning mot maks arbeidstid/overtidsgrenser som harde regler. Kjerneoppgaven med én vakt, fiktive 20–30 ansatte, regelbasert filtrering, KI til teksttolkning/forklaring og menneskelig sluttvalg er beholdt.

Commitmeldingene knytter endringene til gruppens føringer, faglærers tilbakemelding og senere samordning med PRD. Git-historikken viser ikke hvilken versjon som faktisk ble innlevert og godkjent som proposal. Denne diffen kan derfor ikke alene lukke E-02 eller bevise samsvar med levert proposal. Eksisterende E-02-punkt i `issues.md` dekker oppfølgingen; ingen duplikat ble opprettet.

Kvalitetssikring: `git diff ee6d798:product-brief.md HEAD:product-brief.md` og commitmeldinger lest. Ingen produktfiler, appkode eller tester endret.

### Åpne punkter
- E-02: Finn faktisk innlevert/godkjent proposal og sammenlign med dagens plan/leveranse. Eksisterende punkt i `issues.md` beholdes åpent.
