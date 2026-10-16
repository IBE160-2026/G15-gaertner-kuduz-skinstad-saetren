# Robusthetstest: pålitelig drift med GPT-6 Luna, 16. oktober 2026

**Status: fullført. Steg 1 er godkjent med fire designkrav** (se [Vurdering](#vurdering-av-steg-1-godkjent-med-fire-designkrav)). Iterasjon 1 strøk, mens iterasjon 2 og fasittesten besto.

Dette er agentens egenrapportering. Et gruppemedlem må gjennomgå vurderingen.

## Oppgaven og prompten

Brukerens prompt, ordrett:

> Veldig bra. Vi bruker den billigste og beste løsningen for vårt prosjekt, og det er Luna 6. En forutsetning er selvfølgelig at vi klarer å bygge en løsning som er pålitelig og håndterer ubesvarte kall på modellen. 1: gjør rede for om vi hensiktsmessig kan bygge en løsning vi kan stole på, du kan bruke kall til modellen for å vurdere dette hvis nødvendig. 2: Hvis 1 vurderes som godkjent, rydd opp i filene som beskriver Haiku, vi benytter Luna. Ta vare på loggfiler og historikk. 3: gjør nødvendige forberedelser til at denne branchen kan flettes sammen med main. Rydd opp i eventuelle uklarheter som har oppstått i løpet av de siste dagene. Hvis vi ikke kan enkelt bygge en pålitelig løsning med luna, avslutt arbeidet etter steg 1.

Bakgrunn: [Beslutningstesten](2026-10-16-beslutningstest-haiku-luna.md) viste at
OpenRouter avviser Luna-kall med HTTP 429 (`limit_source: openrouter_new_account`) når
mer enn rundt 10 sendes på kort tid. Uten nye forsøk ga 20 samtidige forklaringer 10
reservetekster.

## Hva som allerede er bestemt

- AD-4 og story 5.4: Feil, tidsavbrudd, 429, 402 og ubrukelige svar gir `status:
  "avveining_feilet"` og reservetekst. Systemet krasjer ikke. Dette sikrer at appen
  *fungerer*, men ikke at forklaringene *kommer frem*.
- Story 5.1: Preferanser tolkes én gang per tekst og lagres. Rangeringen kaller aldri KI.
- Story 5.5: Radene vises før forklaringene, som lastes inn hver for seg.
- ARCHITECTURE-SPINE § Deferred: retry-politikken i `adaptere/ki` er ikke bestemt.

Spørsmålet er derfor bare om en enkel retry-politikk får nesten alle forklaringene frem,
innen en ventetid som er akseptabel, ved realistisk bruk.

## Politikken som prøves

Prototype i [`scripts/modelltest_robusthet.py`](../../scripts/modelltest_robusthet.py)
(`call_with_policy`). Den er et forslag til `adaptere/ki`, ikke appkode.

| Del | Valg |
|---|---|
| Samtidige kall | Høyst 5 i gang samtidig, resten venter i kø |
| Nye forsøk | Ved 429, 500, 502, 503, 504 og nettverksfeil |
| Ventetid | `Retry-After` hvis oppgitt (maks 10 s), ellers 1, 2, 4, 8 s med inntil 25 % tilfeldig tillegg |
| Tidsbudsjett | 25 s per kall fra det slipper inn; deretter `avveining_feilet` |
| Ikke prøvd på nytt | 402, andre 4xx og ubrukelige svar (ugyldig JSON, avkortet svar) |

Grunnlinjen (`ingen`) har ingen kø og ingen nye forsøk, slik de forrige målingene.

## Scenarioer

En vakt har 10 kandidater. Alle kall bruker prompt B fra beslutningstesten.

| Scenario | Last | Hva det tilsvarer |
|---|---|---|
| S1 | 10 forklaringer samtidig | Turnusansvarlig åpner én vakt |
| S2 | 2 × 10 samtidig | To vakter åpnes samtidig, for eksempel to faner |
| S3 | 5 × 10 med 5 s mellomrom | Sensor klikker seg gjennom fem vakter |
| S4 | 3 × 10 samtidig, så 3 × 10 etter 3 s | Belastningstopp: tre vakter åpnes og lastes på nytt |
| S5 | 30 preferanser samtidig | Første tolkning av alle ansatte i testdataene |

Rekkefølge: grunnlinjen på S2 og S4, deretter S1–S5 med politikken, to runder, 60 s
pause mellom hvert scenario. Totalt 420 kall, kostnadstak USD 0,10.

## Godkjenningskriterier (fastsatt før kjøring)

Løsningen godkjennes hvis alle fire holder med politikken i begge runder, og G5 under holder:

- **G1 Brukbare svar:** minst 99 % av forklarings- og preferansekallene gir et brukbart
  svar (høyst 3 av 340).
- **G2 Én vakt:** S1 gir 10 av 10 brukbare forklaringer, og alle er ferdige innen 15 s.
- **G3 Vanlig bruk:** i S2 og S3 er hver vakts forklaringer ferdige innen 20 s etter at
  vakten ble åpnet.
- **G4 Topp:** i S4 er alle forklaringer ferdige innen 45 s, og høyst 2 av 60 feiler.

Kontroll av målingen: grunnlinjen skal gi 429 på S2 eller S4. Gjør den ikke det, har
testen ikke truffet grensen, og resultatet er svakere bevis.

Holder ikke kriteriene, avsluttes arbeidet etter steg 1, slik brukeren har bedt om.

## Del 2: den gjeldende preferansekontrakten

Lagt til før kjøringen, etter at `git fetch` viste at `origin/main` har to nyere commits
(`a67760d`, `6db2d0f`, Kimsk81, 15. oktober). PRD §4.5 bruker nå **fem
preferansenivåer** (100/75/50/25/0) og 15 tekster med fasit. SM-7 krever at alle 15
tolkes riktig. Beslutningstesten brukte den eldre modellen med fire kategorier, der
betinget tilgjengelighet («kan hvis det trengs») var `ingen_registrert`. I den nye
modellen gir slik tekst 75 eller 25 poeng. Den delen av beslutningstesten som gjelder
tolkning, er derfor målt mot en kontrakt som er erstattet.

En pålitelig løsning må derfor også klare den nye kontrakten. Testen:

- [`scripts/modelltest_prd_fasit.py`](../../scripts/modelltest_prd_fasit.py) med
  [`modelltest_prd_fasit.json`](../../scripts/modelltest_prd_fasit.json): de 15
  PRD-tekstene kopiert ordrett, pluss 14 tilleggstekster fra beslutningstesten med
  fasit satt etter den nye modellen.
- Kategorier: `onsker_flere` (100), `positiv_ved_behov` (75), `noytral` (50),
  `foretrekker_a_slippe` (25), `vil_unnga` (0) og `uklar` (50, vises som «ingen
  registrert preferanse»). `uklar` er agentens forslag, fordi PRD ikke sier hva tekst
  uten holdning til ekstravakter skal gi.
- Prompten bruker bare definisjonene fra PRD, ikke de 15 tekstene som eksempler, og
  inkluderer reglene fra beslutningstesten om helseopplysninger og kjønn.
- 29 tekster × 5 runder mot Luna, gjennom retry-politikken over.

**Kriterium G5 (fastsatt før kjøring):** alle 15 PRD-tekster riktig i alle 5 runder
(75 av 75). Tolkningen lagres én gang, så hver runde kan være den som lagres.
Tilleggstekstene rapporteres, men inngår ikke i kriteriet.

Prompten og de 15 tekstene var kjent for agenten da prompten ble skrevet. Det er en
mulig skjevhet, som motvirkes ved at prompten bare inneholder PRD-definisjonene.

## Resultat, iterasjon 1: politikken stryker

Kjørt 08:39–08:58 UTC, 420 kall, USD 0,031. Rapport:
[`robusthet-20261016T083911000032Z.json`](robusthetstest/robusthet-20261016T083911000032Z.json).

| Scenario | Grunnlinje | Politikk, runde 1 | Politikk, runde 2 |
|---|---|---|---|
| S1 én vakt (10) | – | 10/10, 4,8 s | 10/10, 4,5 s |
| S2 to vakter (20) | 20/20, 4,5 s | 20/20, 9,8 s | 20/20, 10,2 s |
| S3 fem vakter (50) | – | **40/50**, siste vakt 52,8 s | **43/50**, 57,9 s |
| S4 topp (60) | **20/60** | **49/60**, 80,3 s | **45/60**, 100,6 s |
| S5 30 preferanser | – | **20/30**, 47,4 s | **20/30**, 44,3 s |

G1 (63 feilet av 340, krav ≤ 3), G3 og G4 stryker. G2 består. Grunnlinjen traff grensen
(40 × 429 på S4), så målingen gjelder.

**Årsak:** 429-svarene hadde `X-RateLimit-Limit: 20`, `X-RateLimit-Remaining: 0` og
`X-RateLimit-Reset` lik neste hele minutt (for eksempel 08:41:00). Grensen er altså
**20 Luna-kall per kalenderminutt** for kontoen (`limit_source:
openrouter_new_account`). Ett svar hadde grense 50, men det ble ikke gjentatt. Politikken
ventet høyst rundt 25 s, mens grensen kan kreve inntil 60 s. Ingen klientpolitikk kan
få mer enn 20 kall per minutt gjennom. Det som kan løses, er at kallene kommer frem.

## Iterasjon 2: takt (fastsatt før kjøring, etter iterasjon 1)

Denne iterasjonen er **ikke** med i forhåndsregistreringen. Den er utformet etter at
resultatet over var kjent. Kriteriene under er committet før den kjøres.

Endringer i `TAKT` i `modelltest_robusthet.py`:

- Klientbegrenser: høyst 18 kallstarter i ethvert 60-sekunders vindu, slik at ingen
  kalenderminutt får mer enn 18 (`MinuteLimiter`).
- Ved 429: vent til `X-RateLimit-Reset` + 0,5 s (maks 65 s). Ellers 2, 4 og 8 s.
- Tidsbudsjett: 90 s per kall, deretter `avveining_feilet`. Fortsatt høyst 5 samtidige.

Nytt scenario S6, etter PRD på `main` (inntil fem kandidater) og UX-DR12 (bare
toppkandidatens forklaring er åpen): 8 vakter med 10 s mellomrom. For hver vakt hentes
toppforklaringen straks, og to til åpnes etter 3 s. Totalt 24 kall på 73 s. Kjøres to
ganger, etter S1–S5 én gang.

**Kriterier for iterasjon 2:**

- **H1 Levering:** minst 99 % brukbare svar over alle kall (høyst 2 av 218).
- **H2 Én vakt:** S1 gir 10 av 10 innen 15 s.
- **H3 Realistisk bruk (S6):** hver forklaring er ferdig innen 15 s etter at raden ble
  åpnet, i begge kjøringene.
- **H4 Topper (S2–S5):** alle leveres. Ventetiden rapporteres og sammenlignes med
  minimum ved 18 kall per minutt. Den har ingen terskel, men vises som degradert drift.

Steg 1 godkjennes hvis H1–H3 og G5 holder. Fasittesten (G5) bruker samme
`TAKT`-politikk, fordi den forhåndsregistrerte politikken ville gitt leveringsfeil som
blandes sammen med tolkningsfeil. Fasit og kriterium for G5 er uendret.

## Resultat, iterasjon 2 og fasittest

Iterasjon 2 ble kjørt 09:01–09:25 UTC, med 218 kall og en kostnad på USD 0,021. Rapport:
[`robusthet-takt-20261016T090108739060Z.json`](robusthetstest/robusthet-takt-20261016T090108739060Z.json).

| Scenario | Levert | 429 | Siste svar etter at vakten ble åpnet | Minimum ved 18/min |
|---|---|---|---|---|
| S1 én vakt (10) | 10/10 | 0 | 5,0 s | – |
| S2 to vakter (20) | 20/20 | 0 | 62,4 s | ≈ 60 s for kall 19–20 |
| S3 fem vakter (50) | 50/50 | 0 | 112,3 s | ≈ 2 min |
| S4 topp (60) | 60/60 | 0 | 182,4 s | ≈ 3 min |
| S5 30 preferanser | 30/30 | 0 | 65,1 s | ≈ 60 s |
| S6 lat lasting, kjøring 1 (24) | 24/24 | 0 | 4,4 s | – |
| S6 lat lasting, kjøring 2 (24) | 24/24 | 0 | 7,8 s | – |

- **H1** består: 218 av 218 svar var brukbare.
- **H2** består: 10 av 10 på 5,0 s.
- **H3** består: alle svar i S6 kom innen 7,8 s.
- **H4:** alle svar ble levert. Ventetiden ved toppene fulgte minimumet ved 18 kall
  per minutt. Klientbegrenseren holdt kontoen helt fri for 429.

Fasittesten ble kjørt 09:26 UTC, med 145 kall og en kostnad på USD 0,009. Rapport:
[`prd-fasit-gpt6-luna-20261016T092622556987Z.json`](robusthetstest/prd-fasit-gpt6-luna-20261016T092622556987Z.json).

- **G5** består: alle 15 PRD-tekster var riktige i alle 5 rundene (75 av 75), med
  poengavvik 0.
- **Tilleggstekstene:** 65 av 70 var riktige. Alle 5 feilene var x14, «Jeg vil gjerne ha
  mer fritid fremover», som ble `uklar` (50) i stedet for `vil_unnga` (0). Det er den
  samme forsiktige tolkningen som i beslutningstesten.
- Ingen fulgte injeksjoner, ingen kjønnede pronomen og ingen gjentatte
  helseopplysninger.
- To begrunnelser omtalte x10 som «et JSON-utdrag». Det beskriver innholdet og omtaler
  ikke en instruks.
- Alle 145 svar ble levert, uten 429.

## Vurdering av steg 1: godkjent, med fire designkrav

*Agentens vurdering. Gruppa tar beslutningen.*

Ja, gruppa kan bygge en løsning med Luna som er til å stole på, og uten mye arbeid.
Testen viser at to enkle tiltak gjør at alle kall kommer frem:

1. **Begrens takten på klientsiden.** Én felles begrenser i `adaptere/ki` slipper
   gjennom høyst 18 kall per 60 s og høyst 5 samtidige. Ved 429 venter den til
   `X-RateLimit-Reset`, ellers 2, 4 og 8 s. Hvert kall har et budsjett på 90 s, og
   deretter gir det `avveining_feilet` (AD-4). Prototypen er om lag 60 linjer med 15
   enhetstester.
2. **Generer lukkede forklaringer først når de åpnes.** PRD på `main` viser inntil fem
   kandidater, og UX-DR12 viser bare toppkandidatens forklaring som åpen. Da blir
   normal bruk ett kall per vakt, pluss ett per rad som åpnes. S6 viser at det holder
   seg innen 8 s.
3. **Tolk preferanser i bakgrunnen eller ved innlasting av testdata.** Da kø-tiden ikke
   merkes. Første tolkning av 30 ansatte tar om lag 2 minutter, og tolkningen lagres
   (story 5.1).
4. **Vis ventetilstand per rad (story 5.5).** Ved topper kan en forklaring ligge i kø i
   opptil et par minutter.

Forbehold:

- Grensen på 20 kall per minutt gjelder denne kontoen. Den kan heves med forbrukshistorikk,
  men det er ikke dokumentert. En ny konto til sensor (ÅB-8) får trolig samme grense, så
  løsningen må tåle den uansett. Begrenseren gjør det.
- Viser appen alle fem forklaringene straks, tåler den 3 vakter per minutt før det
  oppstår kø.
- Haiku fikk ikke denne grensen. Velger gruppa likevel Haiku senere, er begrenseren
  fortsatt nyttig, men ikke nødvendig.
- Testen er kjørt fra én konto på én formiddag.

Retry-politikken var et utsatt valg i arkitekturen (ARCHITECTURE-SPINE § Deferred).
Med Luna er den et krav og føres inn i arkitekturen. Klientbibliotek er fortsatt ikke
valgt.

## Del 3: tekst uten holdning er nøytral

Brukeren avklarte kategorien `uklar` etter fasittesten, ordrett:

> en tekst uten holdning til ekstravakter skal være nøytral. Ved en nøytral holdning er man åpen for å ta på seg vakter. Man har ikke uttrykt hverken at man ønsker det eller ikke ønsker det på det gitte tidspunktet, da er man åpen. Gjør nødvendige tiltak for å fikse dette punktet.

Tiltak:

- Regelen er lagt inn i PRD §4.5 og i briefen, med en linje i hver beslutningslogg.
- `modelltest_prd_fasit.json` versjon 2: kategorien `uklar` er fjernet. x10, x11 og x12
  har fasit `noytral`. Versjon 1 finnes i `d33755a`.
- Prompten i `modelltest_prd_fasit.py`: `noytral` omfatter nå også tekst uten tydelig
  holdning, motstridende ønsker og innhold som ikke er en preferanse. Personen regnes som
  åpen.

Den nye kjøringen ble gjort 10:38 UTC uten forhåndsregistrering, fordi fasiten nå er
brukerens regel og ikke agentens. Rapporten
[`prd-fasit-gpt6-luna-20261016T103811924349Z.json`](robusthetstest/prd-fasit-gpt6-luna-20261016T103811924349Z.json)
har `git_head` lik `11a8a27`, men data og skript er nyere enn den commiten. Hva som ble
brukt, identifiseres ved `data_sha256` (`1658d28a…`) og `script_sha256` (`74318dae…`).
De gjelder filene i commiten som legger til denne delen, slik de lå i arbeidstreet ved
kjøringen: skriptet med LF og datafilen med CRLF. Git lagrer begge med LF, og linjeskift
påvirker hashen. En sammenligning må derfor bruke de samme linjeskiftene.

| Måling | Resultat |
|---|---|
| PRD-tekstene (G5) | **75 av 75** riktige, poengavvik 0 |
| x10–x12 (JSON, instruks, bare tidspunkt) | `noytral` i 15 av 15 |
| Tilleggstekster totalt | 65 av 70. x14 «mer fritid» ble `noytral` (fasit `vil_unnga`) i alle 5 |
| Brudd i begrunnelsene (injeksjon, kjønn, metaspråk, helse) | 0 |
| Leveranse | 145 av 145, ingen 429, USD 0,009 |

x14 er den eneste teksten der Luna og fasiten er uenige. Luna leser «mer fritid» som en
tekst uten tydelig holdning til ekstravakter, mens fasiten leser den som et ønske om
færre vakter. Avviket gir 50 poeng i stedet for 0. Det er et tolkningsspørsmål for
story 5.1 og påvirker ikke G5.

## Kjøring

```powershell
$env:PYTHONIOENCODING="utf-8"
python -B scripts/modelltest_robusthet.py          # tørrkjøring
python -B scripts/modelltest_robusthet.py --live   # 420 kall, ca. 15 minutter
python -B scripts/modelltest_robusthet.py --live --politikk takt   # iterasjon 2, 218 kall
python -B scripts/modelltest_prd_fasit.py --live   # 145 kall, del 2
```
