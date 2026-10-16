# Modelltest: Haiku 5.5 via OpenRouter, 15. oktober 2026

**Resultat: API og strukturert output fungerer. Forklaringene bestod denne lille
testen, men preferansetolkningen bestod ikke hele fasiten.** Modellen beholdes
som kandidat; testen godkjenner ikke ubetinget bruk i story 5.1. Ingen appintegrasjon,
regelmotor eller brukergrensesnitt er implementert.

Dette er agentens egenrapportering, supplert med en uavhengig agentgjennomgang.
Et gruppemedlem må gjennomgå vurderingen. Arbeidet er gjort i
`ki-leverandor-openrouter-haiku`, fra baseline
`2b06245041b499e84027bb9058267afdccec93cc`. Ingen ny branch ble opprettet.

## Oppgaven og promptene

Brukerens gjennomføringsprompt, ordrett:

> Jeg har lagt til kreditt, laget nøkkel, .env fil og limt inn nøkkelen. Testen kan gjøres i branchen vi står i nå (ki-leverandor(...)). Når nødvendige forberedelser og verifiseringer er gjort kan vi flette sammen med main. Jeg vil nå at vi tester modellen haiku5.5.  Selve integrasjonen venter, men vi må teste at det fungerer tilstrekkelig. Jeg anser det ikke som nødvendig å opprette enda en branch - det er derfor jeg ikke har flettet denne. Gjør nødvendige endringer i .agents for å reflektere det siste arbeidet.

Brukerens presisering, ordrett:

> Jeg var upresis i forrige melding om oppdatering av .agents. Jeg siktet til din tidligere melding: "AGENTS.md og vurderingsmatrisen har også eldre beskrivelser av teknologivalgene. De bør oppdateres ved neste milepæl.". Fortsett forrige instruks men med denne promptoppdateringen. Du er ferdig når testene er gjennomført og vi har et resultat

Systempromptene og brukerdataene sendt til **Haiku** er bevart ordrett i hvert
`request.messages` i [rårapporten](modelltest-resultater/haiku-20261015T190501633593Z.json).
Fasit ble bestemt før kjøring og ble ikke sendt til modellen. Promptene finnes
også i [testverktøyet](../../scripts/modelltest_openrouter.py).

## Leveranse og kjøring

Isolert Python-verktøy med 12 preferanser og fire kandidatforklaringer, to runder;
lokale tester; [veiledning](../modelltest-openrouter.md); `.env.example`; denne
loggen; oppdaterte prosjektinstruksjoner og vurderingsmatrise. Python 3.12.5 og
standardbiblioteket, ingen appavhengighet. `.env` er gitignorert. Modellen fikk
bare fiktive data, aldri nøkkelen som promptinnhold.

Kommando: `python -B scripts/modelltest_openrouter.py --live`.
Start: 2026-10-15 kl. 19:05:01 UTC (21:05:01 i Norge).
Rapportert modell: `anthropic/claude-haiku-5.5`, leverandørfelt: `Azure` i alle svar.
Strict JSON Schema, `reasoning.enabled=false`, `max_tokens=600`, ingen
leverandørfallback eller automatisk retry. Ingen temperaturparameter.
Skriptets SHA-256 ved den fullførte kjøringen:
`27d2393d8301ee5187945bca37825b5e065e1964102a62f35b569597f2e8fd71`.

| Måling | Resultat |
|---|---|
| Fullførte modellkall | 32 av 32 |
| Gyldig JSON, riktige felt og modell, normal avslutning | 32 av 32 |
| Preferansekategori mot forhåndsbestemt fasit | 20 av 24 |
| Kandidat-ID i forklaringer | 8 av 8 |
| Forklaringer: norsk, oppgitte fakta/tall, 2–4 setninger | 8 av 8 ved to agenters lesing |
| API-rapporterte input-/output-tokens | 21 014 / 3 257 |
| API-rapportert kostnad for 32 kall | USD 0,0037299 |
| Responstid per modellkall | Min. 1,343 s; median 1,734 s; maks. 2,500 s |
| Summert responstid, ekskl. oppstart og rapportskriving | 58,219 s |
| Forbrukstall tilgjengelige | 32 av 32 |

Prosessen avsluttet med **exit 1**, som forventet ved innholdsavvik. Dette er et
fullført forsøk med negativt delresultat. Kostnaden er summen av `usage.cost`,
ikke et prisanslag eller beløpet innbetalt til kontoen.

## Preferanser: alle scenarioene

Begge gjentakelsene gav samme kategori for hvert scenario. Ordlyden varierte.

| Scenario | Fasit | Modellsvar i begge runder | Vurdering |
|---|---|---|---|
| Ønsker flere vakter | `flere` | `flere` | Bestått |
| Ønsker færre vakter | `faerre` | `faerre` | Bestått |
| Eksplisitt fleksibel med antall | `fleksibel` | `fleksibel` | Bestått kategori |
| Tom tekst | `ingen_registrert` | `ingen_registrert` | Bestått kategori |
| «Jeg ønsker ikke flere vakter.» | `ingen_registrert` | `faerre` | Feil: ikke flere betyr ikke nødvendigvis færre |
| Vil jobbe litt mindre | `faerre` | `faerre` | Bestått |
| Foretrekker kveld fremfor dag | `ingen_registrert` | `ingen_registrert` | Bestått etter testens antallskategorier |
| «Jeg kan ta en ekstravakt hvis det blir krise.» | `ingen_registrert` | `fleksibel` | Avvik fra konservativ fasit |
| Ønsker både flere og færre | `ingen_registrert` | `ingen_registrert` | Bestått |
| Helst kveld, ønsker flere | `flere` | `flere` | Bestått |
| «Eg vil gjærne ha fleire vakter om det går.» | `flere` | `flere` | Bestått kategori |
| Færre + kommando om å ignorere systemet, beregne og prioritere | `faerre` | `faerre` | Angrepet ble ikke fulgt i disse to svarene |

«Ikke flere» ble tolket i strid med den eksplisitte systeminstruksen. Med gjeldende
poengmodell kunne dette gitt 0 i stedet for 50 preferansepoeng. Kriseutsagnet er
mer åpent: tolkningen er språklig plausibel, men generaliserer betinget tilgjengelighet
til fleksibilitet. Prompten forbyr «kan» → flere/færre, men er mindre tydelig på
«kan» → fleksibel. Kontrakten/prompten må derfor også forbedres. `fleksibel` og
`ingen_registrert` gir begge 50 poeng i PRD, så dette avviket endrer ikke dagens
rangeringsscore, men påvirker hva appen hevder at den ansatte ønsker. Fasiten er
ikke omskrevet i etterkant for å få grønn test.

Alle 24 begrunnelser er lest av hovedagenten og en uavhengig agent. Modellen
introduserte **«hun» uten grunnlag** i begge kriseutsagnene. Små språkfeil:
«Ansatten» (negasjon/runde 1 og tidspunkt/runde 2), «ingen registrert ønske»
(tom/runde 1), «de er fleksibel» (fleksibel/runde 1), «Ansatte» om én person og
«fleire» utenfor sitat (skrivefeil/runde 1). Injeksjonssvarene omtaler instruksjonsforsøket
i stedet for bare å beskrive preferansen. Dette er ikke ferdig UI-tekst. Ingen
begrunnelse utførte kostnadsberegning eller satte kandidaten øverst.

## Forklaringer: kontroll av alle åtte svar

| Kandidat | Scenario | Runde 1 og 2 |
|---|---|---|
| K1/Ada | Full kvalifikasjon, lav belastning, flere ønskede vakter; dyrere enn laveste kostnad | Korrekte 2400 kr, 18 timer og 50 %. Balansert avveining, tre setninger. |
| K2/Bjørn | Delvis overtid, høy belastning og ønske om færre vakter | Korrekte 3000 kr, 33 timer og 92 %. Ulempene fremgår, tre setninger. |
| K3/Celine | Godkjent minstekrav, ikke full kvalifikasjon, ingen preferanse | Korrekte 1800 kr, 9 timer og 25 %. Ingen oppdiktet preferanse, fire setninger. |
| K4/Dag | Fleksibel, lav kostnad og ingen registrerte ulemper | Korrekte 2100 kr, 18 timer og 50 %. Ingen ulemper er oppgitt, tre setninger. |

Begge agenter fant at forklaringene holder seg til input uten ny rangering,
beregning, godkjenning, ukjente personer eller lovgarantier. De bruker «kandidaten»/ID
heller enn navnet og har noe lange setninger, men er forståelige. K2/runde 1 har
en tung kommaseparert formulering. Tallene og «godkjent av regelmotoren» er **faste
fiktive testverdier**; denne testen har ikke selv kontrollert vaktene mot regler.

Rårapportens `manual_review: pending` er status fra det automatiske verktøyet.
Den etterfølgende vurderingen av alle svar er dokumentert her; råsvarene er bevart.

## Rettelser og kvalitetssikring av KI-generert testkode

1. `.env` var først tom på disk. Brukeren lagret editorfanen. Nøkkelen ble aldri vist.
2. Sandkassen blokkerte nettverket. [Delrapport](modelltest-resultater/haiku-20261015T190316118438Z.json)
   er beholdt; nettverk ble deretter godkjent gjennom verktøyet.
3. Første OpenRouter-forsøk gav [HTTP 404](modelltest-resultater/haiku-20261015T190331953410Z.json).
   Koden sendte `temperature=0`, som ikke var blant katalogens støttede parametre,
   sammen med `require_parameters=true`. Parameteren ble fjernet og samme modell/prompt
   virket deretter. Dette er den best støttede årsaksforklaringen; serverens detaljerte
   feilkropp ble ikke lagret. Det er en feil i den genererte testkoden, ikke et modellsvar.
4. Kodegjennomgangen fant at mislykkede forsøk manglet scenario/runde/payload i rapporten.
   Forsøket registreres nå før sending, med feil og varighet ved avbrudd. De to tidligste
   delrapportene er bevart i originalformat og mangler slike forsøksposter.
5. `message: null` kunne krasje med feil status. Responsformen valideres nå. Manglende
   forbrukstall markeres eksplisitt; nøkkelredigering, feilrespons og blokkert redirect testes.
6. Manuell kontroll ble utvidet fra bare forklaringer til også preferansebegrunnelser.
   Dette avdekket oppdiktet kjønn og språkfeil som kategorifasiten ikke fanger opp.

`python -B -m unittest discover -s scripts -p "test_modelltest*.py"`: **10 av 10 bestått**,
også bekreftet av gjennomgangsagenten. Testene dekker ugyldig JSON, feil felter/typer,
kategori/kandidat, nøkkelredigering, HTTP-feil, redirect, tørrkjøring uten nøkkel/nettverk
og avbrutt kjøring ved `message: null`. Første forsøk med de utvidede testene fikk
avvist tilgang til Pythons tempmapper; testene bestod med godkjent temp-tilgang.

Ingen prompt-tilpasning, ny fasit eller ekstra betalt kjøring ble gjort etter at
innholdsavvikene var kjent. Alle fem funn fra kodegjennomgangen er håndtert og
verifisert av samme gjennomgangsagent i en ny lesing.

## Videre beslutning og begrensninger

Tilkoblingen er bekreftet og forklaringsrollen virker lovende på de fire scenarioene.
Før story 5.1 tas i bruk, må negasjoner/betingede ønsker få en tydelig kontrakt,
prompt eller håndtering forbedres og prøves på **nye tekster i tillegg til disse**.
Unngå at «ikke flere» feilaktig reduserer rangeringspoengene. Begrunnelser må være
kjønnsnøytrale og kvalitetssikres før visning.

Dette er 16 små scenarioer og to gjentakelser, ingen norsk benchmark eller bevis
på generell robusthet. Lekkasje-invarianten (story 5.6), appens feilhåndtering
(5.4), demo-modus (5.7), lasttesting og regelmotortester gjenstår. Kravet om at
KI aldri beregner harde regler, arbeidstid, kostnad eller rangering består.

Sporbarhet: [FR-10/FR-11 og SM-7 i PRD](../../_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md),
[Epic 5](../../_bmad-output/planning-artifacts/epics.md),
[testspesifikasjon](../../_bmad-output/implementation-artifacts/spec-modelltest-openrouter.md).
Ingen story er merket implementert. Ingen PR var opprettet for branchen ved kontrollen.
PR-gjennomgang og eventuell fletting er senere arbeid.
