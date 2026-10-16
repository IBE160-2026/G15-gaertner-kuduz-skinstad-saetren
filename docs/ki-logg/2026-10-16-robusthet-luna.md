# Robusthetstest: pålitelig drift med GPT-6 Luna, 16. oktober 2026

**Status: forhåndsregistrert, ikke kjørt.**

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

## Kjøring

```powershell
$env:PYTHONIOENCODING="utf-8"
python -B scripts/modelltest_robusthet.py          # tørrkjøring
python -B scripts/modelltest_robusthet.py --live   # 420 kall, ca. 15 minutter
python -B scripts/modelltest_prd_fasit.py --live   # 145 kall, del 2
```
