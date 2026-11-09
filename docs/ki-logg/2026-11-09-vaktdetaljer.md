# KI-logg: Story 1.6 – vaktdetaljer

Dato: 2026-11-09. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-1-6-velge-vakten-som-skal-bemannes.md), Epic 1-kontekst og beslutningene AV-03 og AV-13. Arbeidet ble gjort av Codex som implementeringsagent.

## Oppgave og prompt

Brukerens instruksjon til agenten: «Read ... spec-1-6-velge-vakten-som-skal-bemannes.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.» Specen krevde beskyttet detaljoppslag, kandidatflate uten kandidater, ruting, tester og dokumentasjon.

## Leveranse

- Leseoppslag i lagringsadapteren og `GET /api/vakter/{vaktnummer}`. Spørringen begrenser resultatet til innlogget brukers turnus, ubemannet status og halvåpen visningsperiode. API-et sender avdeling, vaktnummer, type, start/slutt og minstenivå, med Oslo-offset. Avviste oppslag gir felles 404-form uten vaktdetaljer.
- Egen kandidatflate på eksisterende URL med detaljtekst, brødsmulesti, lasting, nøytral 404, sesjonsavvisning, feil og nytt forsøk. Ingen kandidater, regler eller KI-kall er lagt inn.
- API-tester for demovaktene, bemannet/ukjent/historisk vakt, annen turnus, sesjon og periodekanter; frontendtester for rutetolkning og Oslo-dato i brødsmulen.

## Korrigering og kvalitetssikring

Første KI-genererte API-test antok `minstenivå 2` for #4127 og #4189. Testen feilet mot faste seeddata, som har `minstenivå 3`; forventningen ble rettet etter kontroll av API-resultatet. Dette endret ingen testdata. Uavhengig kodegjennomgang avdekket at «Minstenivå 3» ikke forklarte skalaen; visningen ble endret til «Minstenivå 3 av 4». Review ba også om kontroll av 401 fra detaljoppslaget og en full flyt mot testdatabasen, som begge ble utført. Alle ni reviewfunn og vurderingene står i spesifikasjonens Review Triage Log. Etter retting ga full `pytest` **150 bestått**, `npm.cmd test` **17 bestått**, og `npm.cmd run build` bestod. [Nettleserkontrollen](2026-11-09-vaktdetaljer-nettleserkontroll.md) dekker direkte URL, tilbakeknapp, 404, 401, serverfeil og nytt forsøk, 360/1600 px og 20 px standardskrift, samt en full flyt mot en midlertidig seedet database. Skjermbildene er tatt etter reviewrettingen mot testdatabasen.
