---
title: 'Story 1.4: Beskyttede flater og utløpt sesjon'
type: 'feature'
created: '2026-11-08'
status: 'in-review'
baseline_commit: 'd15381a755e56c54ce2d0ab1ce0c5e89b6c3e9f7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/AGENTS.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 1.3 kontrollerer bare sesjonen ved oppstart og i `/api/meg`. Felles tilgangskontroll, URL-vern og utlogging mangler (FR13, NFR6).

**Approach:** Beskytt API og flater som standard. Bortfalt sesjon sender brukeren til innlogging uten fornyelse. Appbaren får «Logg ut».

## Boundaries & Constraints

**Always:** Behold JWT/cookie etter OP-10. Bare `GET /api/helse`, `POST /api/innlogging` og `GET /api/innloggingsinfo` er offentlige. AD-4 styrer feil, AV-13/14 styling, OP-04 gjennomgang.

**Never:** Stille fornyelse, gjentakelse av avvist handling, token i nettleserlagring, databaseendring, story 1.5–1.6 eller tilbakekalling av kopierte JWT-er. Utlogging fjerner nettleserens cookie.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Vern | Manglende, utløpt, ugyldig token eller slettet bruker | Alle `/api`-kall utenom de tre unntakene gir 401 før ruting, også ukjent sti/metode | `mangler_sesjon`; slett cookie |
| Offentlig | De tre metode/sti-parene uten sesjon | Tilgjengelige som før | Feil passord forblir `feil_innlogging` |
| Direkte URL | Beskyttet sti uten sesjon | Erstatt URL med `/logg-inn`; skjul innhold under kontroll | Første anonyme besøk får ingen utløpsmelding |
| Bortfalt sesjon | Beskyttet kall gir 401, også uten JSON | Tøm bruker/skjermtilstand; vis innlogging med sesjonsmelding etter tidligere bekreftet sesjon | Bare gjeldende sesjonsgenerasjon kan tømme tilstanden; ingen fornyelse |
| Utlogging | Innlogget trykker «Logg ut» | POST sletter cookie med samme navn og sti; innloggingsflate | 401 sletter også cookie; ved tvetydig nettverksfeil skjules beskyttet innhold til ny sesjonskontroll, med mulighet til nytt forsøk |
| Navigasjon | Tilbake/frem eller ny beskyttet URL | Kontroller sesjonen før innhold vises; `/logg-inn` med gyldig sesjon går til oversikt | Gamle svar kan ikke gjenopprette utlogget sesjon |
| Ny innlogging | Gyldige opplysninger | Gå til `/turnus/kirurgisk-sengepost`, dagens foreløpige startside | Ingen automatisk retur til godkjenning |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py`: gjenbruk `databaseokt`, `/api/meg` og feilhåndterere; `sesjon.py` eier JWT/cookie, lagring eier brukeroppslag.
- `backend/tester/api/test_innlogging.py`: isolert database og tokenhjelpere.
- `frontend/src/App.tsx`: sesjon/skjermvalg; `api.ts`: felles `kall<T>`; `komponenter/LoggInn.tsx`: gjenbruk skjema og `startfeil`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adaptere/api/main.py` — standardvern før ruting og `POST /api/utlogging`. Deaktiver automatisk API-dokumentasjon. Ukjent sti/metode gir 401 uten sesjon, 404/405 med sesjon.
- [x] `backend/adaptere/api/sesjon.py` — slett cookie med riktige attributter.
- [x] `backend/tester/api/test_innlogging.py` — test API-matrisen og en ny testrute som beviser standardvern uten lokal kontroll.
- [x] `frontend/src/api.ts` — 401 fra beskyttede kall varsles før JSON-parsing, bundet til sesjonsgenerasjonen ved utsending. Offentlige kall varsler ikke.
- [x] `frontend/src/App.tsx`, `frontend/src/navigasjon.ts` — History API, navigasjonskontroll og vern mot gamle svar. Bare `/turnus/kirurgisk-sengepost` viser foreløpig oversikt; andre beskyttede stier får en tydelig ikke-funnet-tilstand.
- [x] `frontend/src/komponenter/Appbar.tsx`, `frontend/src/tekster.ts`, `frontend/src/stil/app.css` — sekundærknapp, feiltilbakemelding og teksten «Sesjonen er utløpt. Logg inn på nytt.».
- [x] `README.md`, `docs/ki-logg/2026-11-08-beskyttede-flater.md`, `docs/emne/vurderingsmatrise.md` — dokumenter atferd, prompt, rettelser og kvalitetssikring. OP-10 gjelder foran foreldet NFR7-sammendrag i epics.

**Acceptance Criteria:**
- Given ingen gyldig JWT, when et annet `/api`-kall enn de tre unntakene gjøres, then svarer API-et 401 med AD-4-feilformen uten at ruten utføres.
- Given en direkte beskyttet URL uten sesjon, when appen åpnes, then vises innlogging uten beskyttede data og URL-en er `/logg-inn`.
- Given en bekreftet sesjon som utløper, when et beskyttet kall gir 401, then vises innlogging med utløpsmelding og kallet gjentas ikke.
- Given en innlogget bruker, when «Logg ut» bekreftes, then slettes cookien og appbaren viser «Ikke innlogget».
- Given tastatur og 360px/1600px vindu, when utlogging brukes, then er knapp og fokus synlige uten vannrett rulling.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Review av spesifikasjonen 2026-11-08: adversarial og edge-case-hunter undersøkte krav mot kode; struktur og prose undersøkte dokumentformen. Orkestratoren kontrollerte funnene mot story 1.4, API-testene og UX.

| Funn | Vurdering | Endring |
|---|---|---|
| 401 mot 404/405 på ukjent API-sti | reell motstrid | 401 før ruting uten sesjon; 404/405 med sesjon |
| Forsinket 401 etter ny innlogging; forsinket `/api/meg` etter utlogging | reell løpssituasjon | sesjonsgenerasjon og eksplisitt manuell kontroll |
| Første anonyme besøk kan få utløpsmelding | reell UX-feil | meldingen krever tidligere bekreftet sesjon |
| `/logg-inn` med gyldig sesjon og ukjent beskyttet URL | reell navigasjonsuklarhet | gå til oversikt ved gyldig sesjon; ukjent sti får ikke-funnet-tilstand |
| Utlogging med utløpt cookie eller tvetydig nettverksfeil | reell tilstandsuklarhet | 401 sletter cookie; skjul beskyttet innhold til ny kontroll ved nettverksfeil |
| Offentlig 401 kan utløse global utlogging | reell avgrensningsfeil | bare beskyttede kall varsler, før JSON-parsing |
| Tester/bygg var de eneste systemkriteriene | reelt akseptansegap | fem Given/When/Then-kriterier for storyens atferd |
| Gjentatt verifikasjonsliste og kortfattet prosa | mindre | verifikasjonslisten er forkortet; tekniske formuleringer beholdt for presisjon |

Kodegjennomgang 2026-11-08: Blind Hunter, Edge Case Hunter og Verification Gap fikk diffen uten implementeringshistorikk. Instruksjonsfilene for de to siste krevde eskalert lesetilgang. Funnene ble kontrollert mot kildekode og tester før retting.

| Lag | Funn | Vurdering og rute |
|---|---|---|
| BH | Utloggingsfeil låser brukeren til retry | low, bevart retry og skjult innhold ved ukjent cookie-status; avvist ekstra utvei som kan vise innhold uten kontroll |
| BH, ECH | Sent innloggingssvar kan sette cookie etter generasjonsskifte | medium, rettet med ny sesjonskontroll |
| BH, ECH | Fokus forsvinner når knapp fjernes | medium, rettet med fokus på innloggingsfelt/retry |
| BH | Nettverksfeil ved navigasjon kaster bort mål-URL | medium, rettet med bevart URL og retry uten innhold |
| BH | Slettet bruker etter innlogging mangler test av felles vern | medium, test lagt til |
| BH, VG | Ingen kjørbar frontendkontroll av URL/401/løpssituasjoner | medium, tre Node-tester lagt til; faktisk nettleserflate gjenstår |
| BH | Oppgavelisten står åpen etter implementering | low, oppgaver krysset av etter diffkontroll |
| BH | Regenerert epic-kontekst er mindre detaljert | low, vedtatte krav finnes i epics/story og konteksten peker på dem; ingen kodefeil i 1.4 |
| ECH | Tilbake under ventende utlogging kan vise innhold etter cookie-sletting | high, rettet med sperre til utlogging er avklart |
| ECH | Retry ved utloggingsfeil mangler tastaturfokus | medium, rettet med fokus på retry |
| VG | Direkte beskyttet URL hadde ingen frontendtest | medium, URL-helper testet; visning i faktisk nettleser fortsatt åpen |
| VG | Forsinket 401 etter ny innlogging hadde ingen test | medium, styrt frontendtest lagt til |

Lokal PR-gjennomgang etter commit `9473de4`: Backend/API-agenten fant ingen nye avvik. Frontend-agenten fant ett middels avvik: fokusrammen på «Logg ut» hadde samme farge som appbarens bakgrunn. Fargevalget er rettet i `app.css` med `--color-on-accent`; faktisk fokusvisning i nettleser gjenstår å kontrollere.

## Verification

- Fra `backend/`: `.venv\Scripts\python -m pytest` (bash: `.venv/bin/python -m pytest`).
- Fra `frontend/`: `npm.cmd run build` (bash: `npm run build`).
- Nettleser: test matrisen, inkludert forsinket `/api/meg` etter utlogging og forsinket 401 etter ny innlogging. Før faktiske resultater i KI-loggen.
