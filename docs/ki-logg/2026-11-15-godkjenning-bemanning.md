# KI-logg: Story 3.2 – godkjenning og bemanning

Dato: 2026-11-15. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-3-2-godkjenning-og-bemanning.md), [Epic 3-konteksten](../../_bmad-output/implementation-artifacts/epic-3-context.md), `AGENTS.md` og [gruppevedtakene](../beslutninger/avklaringspunkter.md) (FR12, AD-5, P-08, P-09, P-12, OP-16). Storytabellen anbefaler Claude Opus på grunn av varig lagring, regelkontroll og dublettvern. Økten kjørte Codex GPT-6.

## Oppgave og prompt

Brukeren ba om bmad-build for story 3.2, med branch og pushet startcommit, underagenter, tester, KI-logg og sesjonslogg. Etter at brukeren godkjente spesifikasjonen, fikk implementeringsagenten uten forutgående samtalekontekst denne instruksen:

> Read C:\Users\krh\kode\ibe160-turnusprosjekt\G15-gaertner-kuduz-skinstad-saetren\_bmad-output\implementation-artifacts\spec-3-2-godkjenning-og-bemanning.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start.
>
> When done, report what you changed, how you verified it, and anything left incomplete or risky.

En egen agent oppdaterte Epic 3-konteksten, og en annen kartla eksisterende kode før spesifikasjonen ble skrevet.

## Modellens leveranse

- Backend fikk `GodkjenningRad` med unik vakt, en eneste skrivefunksjon for bemanning, `Godkjenning` som domenetype og beskyttet POST-rute ved siden av GET-grunnlaget.
- GET fikk et opakt grunnlagsmerke. POST tar SQLite-skrivelås før ny regelvurdering, sammenligner merket og lagrer godkjenning, vaktens tildeling og `sist_oppdatert` i én transaksjon. Egen kode skiller endret grunnlag, ugyldig kandidat, datafeil og allerede bemannet vakt.
- Frontend sender merket ved eksplisitt trykk, håndterer nye feiltilstander og viser bekreftelse i Vaktvalg etter vellykket lagring.
- Testdata kan lastes på nytt etter en godkjenning, og nye API- og komponenttester dekker varig lagring, endret grunnlag, datafeil, dublett, samtidighet og UI-flyten.

## Retting og kvalitetssikring

Hovedøkten leste diffen mot spesifikasjonen og fant at `aktiv.current` kunne bli `true` igjen når samme godkjenningskomponent fikk en ny vakt/kandidat. Et sent POST-svar fra forrige kandidat kunne da navigere til Vaktvalg. Agenten rettet det med forespørselsidentitet og la til en komponenttest som holder Jonas-svaret tilbake mens flaten byttes til Mette (P-09).

Testmatrisekontrollen fant i tillegg at POST-datafeil og «ingen andre API-ruter bemanner vakten» manglet egne tester. Agenten la til begge. Testene med falsk `fetch` gjør ingen modellkall.

Hovedøkten kjørte hele pakken på nytt etter rettingene: **418 av 418 backendtester**, **48 av 48 modultester**, **17 av 17 komponenttester** og frontendbygg bestod. Arkitekturkontrakten inngår i backendtestene.

En målrettet nettleserkontroll brukte en egen database i midlertidig mappe og ekte backend via Vite. Ved 1000 px bredde var vakt, kandidat og bekreftelsesknapp synlige uten vannrett siderulling; fokus- og kontrastkontroll gjenstår. Kari valgte Jonas for #4127 og trykket «Godkjenn erstatning». API-et svarte 200, Vaktvalg åpnet med statusmelding, og Jonas stod i den bemannede tabellen. Denne kontrollen var før den siste tekstendringen; den konkrete bekreftelsen er dekket av komponenttest. Databasefilen ble slettet etter kontrollen.

## Uavhengig gjennomgang

Tre agenter uten kjennskap til implementeringsarbeidet gjennomgikk den samlede diffen: Blind Hunter, Edge Case Hunter og Verification Gap. Alle 15 funn er vurdert enkeltvis i spesifikasjonens Review Triage Log. Åtte selvstendige funn førte til rettinger, tre overlappet med disse, og fire ble avvist etter kontroll av kontrakt og kode.

- **Konsistent grunnlag:** GET leste opprinnelig visning før merket uten eksplisitt SQLite-snapshot. Rettet til ett lesesnapshot og testet mot samtidig WAL-skriving. Merket var opprinnelig likt for alle kandidater i samme databasetilstand; det er nå bundet til bruker, vakt og kandidat. Tester dekker kryssbruk og endringer i ansatt- og vakttid.
- **Usikkert svar:** Ved tapt POST-svar kunne vakten være bemannet selv om klienten viste kontaktfeil. Flaten sier nå at utfallet er usikkert, sperrer nytt trykk og leder til Vaktvalg for kontroll. Ny POST for en allerede bemannet vakt gir fortsatt 409 som storyen krever.
- **Synlig resultat:** Bekreftelsen viser nå ansatt og vaktnummer. En App-komponenttest følger POST, navigasjon og nyhentet oversikt; andre tester dekker sesjonsbytte og raske gjentatte trykk.
- **Atomisitet:** En test injiserer feil etter oppdatering av vakt og viser at transaksjonen rulles tilbake uten Godkjenning eller delvis bemanning.

Etter rettingene kjørte hovedøkten hele pakken: **423 av 423 backendtester**, **48 av 48 modultester**, **21 av 21 komponenttester**, og frontendbygget bestod. Fokus- og kontrastkontroll i nettleser er fortsatt et åpent manuelt kontrollpunkt.

## Samordning med main og Johannes' AD-5-notat

Etter `git pull origin main` ble story 2.6 og den oppdaterte AD-5 tatt inn. Johannes' notat i [PR #21-loggen](../../.logs/johagartnerhimolde/982-2026-11-15-12-57-45-gjennomgang-pr-21.md) peker på tre forhold: identitet for vist beslutningsgrunnlag, tidlig SQLite-skrivelås og eierskap til transaksjonen. De to første var allerede implementert med opakt grunnlagsmerke og `BEGIN IMMEDIATE`. Det tredje viste et avvik: API-et eide fortsatt transaksjonen og kalte lagring bare for skriving. Implementeringsagenten flyttet derfor lås, ny innlesing, alle harde regler, merkesammenligning, betinget vaktoppdatering og commit inn i lagringsadapterens ene offentlige godkjenningsoperasjon. API-et mapper nå bare utfallet til HTTP. `Godkjenning` bruker vaktnummer, slik at lagringen slår opp riktig intern vakt-ID innenfor låsen. Testen for transaksjonsgrensen og rollback-testen ble tilpasset den nye eierskapsgrensen.

En ny uavhengig gjennomgang av denne refaktoreringen fant to forhold. Det globale merket kan kreve ny bekreftelse ved endringer i andre databaseobjekter; dette var allerede vurdert i spesifikasjonens BH3 og akseptert for én turnus med 506 vakter. Tidspunktet settes ved mottak av brukerens godkjenningsforsøk, før eventuell låseventing. Det er tidspunktet for brukerens beslutning som lagres; selve transaksjonen bruker gjeldende data etter låsen. Begge forholdene er dokumenterte valg, uten funn av feilaktig bemanning eller delvis lagring.

Etter samordningen bestod **427 av 427 backendtester**, **49 av 49 frontendmodultester**, **23 av 23 komponenttester** og frontendbygget. Ingen tester gjorde betalte KI-kall. Den manuelle nettleserkontrollen beskrevet over ble gjort før denne refaktoreringen; den dekker brukerflyten, mens transaksjonsendringen er verifisert med API-testene. Fokus- og kontrastkontroll gjenstår.
