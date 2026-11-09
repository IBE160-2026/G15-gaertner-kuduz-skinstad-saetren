# Nettleserkontroll av kandidatflaten – story 1.6

Kjørt 2026-11-09 i Playwright mot Vite på `127.0.0.1:5174`, med simulerte svar for `/api/meg`, `/api/vaktoversikt` og `/api/vakter/{vaktnummer}`. Kontrollen bruker fiktive data for #4127, med `minstenivå` 3. Den kontrollerer frontendflyten og layouten; API-oppslaget er kontrollert separat med `pytest`.

| Tilfelle | Observert resultat |
|---|---|
| Direkte `/vakt/4127/kandidater` | Brødsmule `Turnus > Kirurgisk sengepost > Vakt #4127 — Dagvakt 27.09.2026`; start 07:00, slutt 15:00, kompetansekrav fra dataene og plassholder uten kandidatnavn. Etter reviewrettingen viste flaten «Minstenivå 3 av 4». |
| «Velg vakt» og nettleserens tilbakeknapp | Kandidatflaten åpnet; tilbakeknappen viste Vaktvalg igjen. |
| 404 for valgt vakt | Nøytral tekst «Fant ikke det du ba om.»; ingen vaktdetaljer eller backendmelding. |
| 500 for valgt vakt | Lokal feiltekst og «Prøv igjen»; backendens testmelding `MÅ IKKE VISES` ble ikke vist. Da svaret ble endret til 200, hentet «Prøv igjen» vakten på nytt. |
| 401 for `/api/meg` ved direkte URL | Sendt til `/logg-inn`; vaktdetaljer ble ikke vist. |
| 360 og 1600 px, standard skrift 16 px | Ingen vannrett siderulling eller klippet tekst. |
| 360 px, standard skrift 20 px | Rotfonten ble 20 px; ingen vannrett siderulling eller klippet tekst. |

Skjermbilder: [360 px / 20 px](2026-11-09-vaktdetaljer-360-20.png) og [1600 px / 16 px](2026-11-09-vaktdetaljer-1600-16.png). De ble tatt på nytt etter reviewrettingen, mot den midlertidige testdatabasen.

## Integrasjonsflyt med midlertidig database

I tillegg ble Vite og backend kjørt mot en midlertidig database fylt med prosjektets faste testdata. Innlogging som `kari.vestby` åpnet Vaktvalg, «Velg vakt» for #4127 åpnet riktig kandidatflate, og nettleserens tilbakeknapp viste Vaktvalg igjen. Testpassordet er ikke lagret i dokumentasjonen.

Da selve detaljoppslaget `/api/vakter/4127` svarte 401, ble brukeren sendt til `/logg-inn` uten at vaktdetaljer ble vist. Dette kontrollerer sesjonsutfallet etter at appen allerede har åpnet detaljruten, i tillegg til 401 fra `/api/meg` ved direkte URL i tabellen over.
