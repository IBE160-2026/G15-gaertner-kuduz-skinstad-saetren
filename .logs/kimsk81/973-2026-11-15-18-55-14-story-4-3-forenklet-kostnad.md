# Story 4.3 – forenklet kostnad

## 2026-11-15 kl. 18:55 — Kimsk81

### Oppgave
Bygg story 4.3 og opprett og push en branch med storynavnet slik at gruppen ser arbeidet. Ragnhild utvikler story 4.2 samtidig; felles frontend-filer må koordineres.

### Plan
- Kartlegg kravene P-01–P-03, eksisterende kode og kandidatflyt; dokumenter planen i [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-3-forenklet-kostnad-per-kandidat.md).
- Implementer, test og få uavhengig gjennomgang gjennom bmad-build.

### Resultat
Branchen `story/4-3-forenklet-kostnad` er opprettet og pushet. Den første branchen `story/4-3` ble slettet fra GitHub på brukerens anmodning. Storyen er implementert og uavhengig gjennomgått. Gjennomgangen fant og rettet manglende kostnad ved ny bekreftelse, lønnsvalidering og misvisende avrunding. 493 backendtester, frontendbygg, 50 modul- og 29 komponenttester bestod. En bevisst feil i overtidsstatus fikk komponenttesten til å feile; etter tilbakeføring bestod testen. Ekte backend og isolerte testdata ga forventet #4127-fasit og #4189-tomtilstand. Layout ble kontrollert ved 680, 960, 1080 og 1600 px.

### Åpne punkter
- Kontroller tastaturfokus, større skrift og faktisk skjermleser på kostnadsflatene, og koordiner felles frontend-filer med story 4.2.
- Vurder mer presis datafeilmelding ved ugyldig lønn og en lønnsspesifikk P-09 POST-test.
