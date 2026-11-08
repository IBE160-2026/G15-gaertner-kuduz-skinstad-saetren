# Nettleserkontroll av Vaktvalg (story 1.5), 2026-11-08

Filene dokumenterer en nettleserkontroll som ble kjørt én gang. Kontrollen er beskrevet i [KI-loggen](../2026-11-08-vaktoversikt.md#kvalitetssikring). Verken appen eller testene kjører filene, og de vedlikeholdes ikke.

## Skriptene

- `cdp.mjs` styrer headless Chrome via Chrome DevTools Protocol, med Node 26 og den innebygde `WebSocket`. Det logger inn og leser ut tekster, rader, klasser, farger og rulling ved 1600 og 360 px, med standard skriftstørrelse 16 og 20 px. Til slutt kontrollerer det tab og enter på «Velg vakt».
- `topp.mjs` er laget av `cdp.mjs` med `sed`. Det tar skjermbilder bare av synsfeltet (1600/16 og 360/20).

Skriptene inneholder ingen passord, nøkler eller stier. Passordet ble gitt som argument ved kjøringen. Kjøringen gikk slik:

1. `python -m adaptere.lagring.testdata` mot en egen database i en midlertidig mappe (`TURNUSHJELPEREN_DB`), med et eget testpassord i `TURNUSHJELPEREN_PASSORD`.
2. Start uvicorn på port 8000 og `npm run dev` på port 5173.
3. Start Chrome: `chrome --headless=new --remote-debugging-port=9333 --user-data-dir=<midlertidig mappe>`.
4. `node cdp.mjs 9333 <mappe for skjermbilder> <testpassord>`.

## Skjermbildene

| Fil | Bredde / skrift | Utsnitt |
|---|---|---|
| `topp-1600-16.png` | 1600 px / 16 px | synsfeltet |
| `topp-360-20.png` | 360 px / 20 px | synsfeltet |
| `vaktvalg-1600-16.png` | 1600 px / 16 px | hele siden, med linjene ved døgnskifte |
| `vaktvalg-360-16.png` | 360 px / 16 px | hele siden |

Alle navnene i skjermbildene er fiktive testdata fra story 1.2.
