# Story 5.5 – rader vises før forklaringene er ferdige

## Oppgave og prompt

Implementeringsagenten fikk instruksen «Read _bmad-output/implementation-artifacts/spec-5-5-progressiv-lasting.md fully and implement it» og skulle rapportere endringer, verifisering og åpne punkter. Turnusansvarlig skal kunne sammenligne og velge kandidater mens forklaringen venter. Ved overgang til godkjenning hentet appen tidligere en ny forklaring selv om kandidaten og grunnlaget var de samme. [Godkjent spesifikasjon](../../_bmad-output/implementation-artifacts/spec-5-5-progressiv-lasting.md).

## Transportvalg

Vi beholdt separate HTTP GET-kall. Rangeringen leverer nøkkeltallene samlet. Førstekandidaten får et forklaringskall når listen åpnes, og de andre får hvert sitt ved åpning eller direkte valg. Backend faktakontrollerer hele modellsvaret før en eneste påstand kan vises (P-06). Streaming av tekstbiter ville derfor krevd bufring til hele svaret foreligger. Polling ville krevd en jobbidentitet, lagring av jobbstatus og gjentatte statusoppslag for å levere det ene ferdige svaret. De eksisterende GET-rutene lar hver rad vise lastetekst og fullføre uavhengig. [Arkitekturbeslutning under AD-4](../../_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md#ad-4--én-feilresponsform-i-api-et).

App eier et oppslag i minnet for arbeidet med én vakt og én sesjonsgenerasjon. Begge flatene bruker samme løfte for et gitt vaktnummer, kandidat-ID og grunnlagsmerke. Resultatet er enten en kontrollert forklaring eller panelets reservetilstand. Godkjenningsflaten henter alltid sitt eget grunnlag. Et annet merke gir et nytt forklaringskall, og når brukeren forlater vakten, forsvinner oppslaget (P-09/P-12). [Oppslag](../../frontend/src/avveiningsoppslag.tsx) · [App](../../frontend/src/App.tsx).

## Verifisering og rettinger

Den første testversjonen krevde ett rangerings-GET også under React StrictModes doble utviklingsmontering. Kravet om ett kall gjelder forklaringen i vanlig bruk. Flyttesten kjører derfor vanlig App og teller rangering, godkjenningsgrunnlag og forklaring hver for seg. En egen StrictMode-test kontrollerer fortsatt antallet forklaringskall ved dobbel montering. Som negativ kontroll lot vi et treff i oppslaget starte et nytt GET. Begge testene for overgang til godkjenning ble røde, både ved ventende og mottatt svar. Vi gjenopprettet gjenbruk av løftet før full testkjøring. [Komponenttester](../../frontend/tester/komponenter/avveining.test.tsx).

Frontendbygget og alle 52 modultester og 66 komponenttester bestod. De 59 eksisterende avveiningstestene i API-et og KI-adapteren bestod. Frontendtestene teller nettleserens GET-kall. KI-testene måler adapterens egne forsøk ved leverandørfeil under AD-7. [API-tester](../../backend/tester/api/test_avveining.py) · [adaptertester](../../backend/tester/ki/test_avveining.py).

## Nettleserkontroll

### Etter uavhengig gjennomgang

Tre gjennomgangsagenter leste endringen. Første versjon beholdt også en transportfeil eller et svar med feil identitet i minnet. Nå vises reserve på den aktive flaten, og en senere montering kan hente på nytt. Et eksplisitt reservesvar med riktig identitet gjenbrukes. Nye tester følger forsinket HTTP 503, feil kandidat-ID, rad seks under «Vis færre», og retur både med «Avbryt» og nettleserens Tilbake. Testen av delt oppslag kjører nå gjennom App i StrictMode. Under rettingen brukte en test ulikt grunnlagsmerke for listen og godkjenningen og traff derfor to forskjellige oppslag. Vi rettet testdataene og brukte den synlige «Avbryt»-knappen for retur.

Sluttkjøringen bestod med 52 modultester, 70 komponenttester, frontendbygg og 59 avveiningstester i backend. Nettleserkontrollen nedenfor ble gjentatt med rettingen og bekreftet ett GET og ett lokalt adapterforsøk for hver av de to kandidatene.

### Resultat ved 680 px

Chrome 158.0.8127.36 kjørte produksjonsbygget ved 680 × 700 px mot ekte FastAPI og en egen kopi av SQLite-testdataene. En lokal transport i `OpenRouterKiAdapter` holdt igjen Jonas Bakkes svar på vakt #4127 til etter overgangen til godkjenning. Alle fire radene hadde kostnad, timetall og aktiv «Velg». Tab flyttet fokus til Mette Solbergs «Vis begrunnelse», med synlig 2 px heltrukken ramme. Enter åpnet panelet rett under hennes rad. Mettes faktakontrollerte forklaring kom mens Jonas fortsatt viste «Henter KI-forklaring …». Begge panelene lå under riktig kandidat. Dokumentbredden var 665 px med 15 px rullefelt i vinduet. Vannrett rulling var avgrenset til tabellen.

Etter valg av Jonas viste godkjenningsflaten lasteteksten og en aktiv «Godkjenn erstatning». Da transporten slapp svaret, kom forklaringen på denne flaten. API-loggen viste ett forklarings-GET for Jonas og ett for Mette. Den lokale transporten registrerte ett forsøk per kandidat. En komponenttest fullførte også selve godkjenningen før det ventende svaret kom. Kontrollen brukte lokale modellresponser (AV-17, OP-16).
