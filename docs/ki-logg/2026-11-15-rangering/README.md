# Nettleserkontroll av story 4.4, 2026-11-15

Claude (Opus 5.5) kjørte kontrollen på Windows 11 med `nettleserkontroll.mjs` (Playwright, `playwright-core`) og headless Google Chrome. Den kontrollerer det komponenttestene i jsdom ikke kan se: beregnet CSS, bredder og rulling, og om fokusmarkeringen synes (OP-16). Johannes ba om kontrollen.

## Oppsett

- **Backend:** egen backend på port 8001 med en midlertidig database utenfor repoet, fylt med `python -m adaptere.lagring.testdata` og et eget testpassord.
- **Frontend:** egen Vite på port 5174 med proxy til 8001.
- **Dine egne utviklingsservere** på 8000 og 5173 ble ikke rørt.
- **Konstruerte rader:** seeden har bare fire gyldige kandidater på #4127. For å prøve «Vis alle» utvider skriptet derfor API-svaret i nettleseren med tre konstruerte rader. De heter «Konstruert kandidat 1–3» og har plass 5–7. Alt annet er ekte data fra backend.

Skriptet krever `playwright-core` (`npm install playwright-core` i en egen mappe) og Chrome på standardstien. Juster `BASE` og innloggingen hvis du kjører mot andre porter eller et annet passord.

## Resultat: alle kontroller bestod etter to rettinger

| Kontroll | Resultat |
|---|---|
| Rekkefølge #4127 | Jonas, Mette, Thomas, Ingrid, med plass 1–4 |
| `rank-badge` | `rgb(22, 50, 74)` = `accent`, 14px, vekt 700 |
| `row-alt` | Rad 2 og 4, bakgrunn `rgb(245, 247, 249)` |
| Rad 1 | «79,4 poeng», «Sykepleier · 3 år ansiennitet», «Preferanse venter på tolkning», «50,0 poeng» |
| 1600 px | Siden ruller ikke. Tabellen får plass uten egen rulling (1088 av 1088 px) |
| 1080 px | Siden ruller ikke. Tabellen ruller i egen beholder (AV-14) |
| 960 og 680 px | Siden ruller ikke. Tabellen ruller i beholderen. Bare til informasjon, smale vinduer hører til story 4.6 |
| Fokus | Synlig ring (`solid 2px accent`) på tabellbeholderen, Velg, «Vis alle» og «Vis bare de 5 øverste» |
| «Vis alle» | Fem rader først. Enter viser alle 7, og fokus går til Velg i rad 6. Ved lukking går listen tilbake til fem, og fokus blir på knappen |
| #4189 | Tomtilstand uten tabell |
| Konsoll | Ingen feil |

## Funn som ble rettet

1. **Siden var 1087 px bred ved 1080, 960 og 680 px.**
   - Årsak: den skjulte kolonneoverskriften «Valg» (`.visuelt-skjult`) har `position: absolute`. Den slapp ut av `.tabellbeholder`, fordi beholderen ikke var en `position`-forelder.
   - Retting: `position: relative` på `.tabellbeholder` i `app.css`. Endringen gjelder også tabellen i Vaktvalg, som bruker samme klasse.
2. **Velg-knappen ble klippet ved 1600 px.**
   - Årsak: tabellen var 1104 px, mot 1088 px innholdsbredde. `.tabell td` har `nowrap`, og taggen «Preferanse venter på tolkning» var 154 px.
   - Retting: preferansecellen (`.preferansecelle`) kan nå brytes over to linjer. Det gjelder bare rangeringstabellen.

Ingen av funnene kan fanges av komponenttestene, fordi jsdom ikke regner ut layout. Derfor er de kontrollert her.

## Skjermbilder

Skriptet tar ni skjermbilder: #4127 ved 1600, 1080, 960 og 680 px, fokus på Velg, «Vis alle» lukket, åpnet og lukket igjen, og #4189. De lagres utenfor repoet, i `nettleserkontroll-4-4/` i systemets temp-mappe, eller i mappen som `SKJERMBILDER` peker på. Johannes ønsket ikke bildene i repoet, så de er gjennomgått lokalt og ikke committet. Kjør skriptet på nytt for å lage dem.

Ikke kontrollert: større skrift (200 %) og en faktisk skjermleser.
