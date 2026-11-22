---
title: 'Story 5.5 – Rader vises før forklaringene er ferdige'
type: 'feature'
created: '2026-11-22'
status: 'done'
baseline_commit: '222a9ee8a4519567590a8eb6b16d168087b7ea1f'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Turnusansvarlig skal kunne sammenligne nøkkeltall og velge kandidat mens forklaringene lastes. Første rad åpnes automatisk. Brukeren kan åpne øvrige rader uavhengig og ta med seg forklaringen til godkjenningsflaten. I dag utløser overgangen til godkjenning et ekstra forklaringskall også når brukeren velger førstekandidaten på samme grunnlag.

## Boundaries & Constraints

Bruk separate HTTP GET-kall for rangering og for hver åpnet kandidats avveining (UX-DR12/13, AD-7). Behold topp fem og «Vis alle». Innen én bemanningsflyt skal et vellykket normalforløp med bare førstekandidaten åpen gi ett forklaringskall. Adapterens automatiske forsøk ved feil følger AD-7. Hver visning bruker sitt ferske rangerings- eller godkjenningsgrunnlag (P-09). Gjenbruk skjer i minnet innen samme sesjon og vakt (P-12).

## I/O & Edge-Case Matrix

| Gitt | Når | Så |
|---|---|---|
| Rangeringen er klar, første forklaring venter | Listen åpnes | Hver synlig rad har nøkkeltall og valgknapp. Første panel viser lastetekst. Øvrige rader kan vises og velges straks. |
| Første forespørsel venter | Brukeren åpner rad to og dens svar kommer først | Rad to viser sin forklaring. Første rad viser fortsatt lasting. Ved feil vises reservetekst bare i raden som feilet. |
| En åpnet rad har en ventende eller ferdig forklaring | Raden lukkes og åpnes, eller kandidaten velges på samme grunnlag | Samme forespørsel eller svar brukes. Godkjenningen kan fullføres mens forklaringen venter. |
| Grunnlaget endres, vakten byttes eller sesjonen avsluttes | Et tidligere svar kommer sent | Bare svar som tilhører gjeldende visning kan oppdatere panelet. Et nytt grunnlagsmerke gir en ny forespørsel. |
| Listen har ingen gyldige kandidater | Flaten åpnes | Tomtilstanden vises uten forklaringskall. |

</frozen-after-approval>

## Code Map

- `backend/adaptere/api/main.py` tilbyr begge GET-rutene. Forklaringssvaret bærer vaktnummer, kandidat-ID og grunnlagsmerke. `backend/tester/api/test_avveining.py` dekker at rangeringen kan hentes uten KI.
- `frontend/src/App.tsx` styrer sesjon og navigasjon mellom kandidat- og godkjenningsflaten. `Kandidatrad` i `frontend/src/komponenter/Kandidatflate.tsx` beholder monterte paneler når de skjules. `Godkjenningsflate.tsx` monterer et nytt panel etter eget oppslag av grunnlag.
- `frontend/src/komponenter/Avveiningspanel.tsx` henter avveiningen per montering. `frontend/src/api.ts` leverer forespørsel og sesjonsgenerasjon. `gyldigAvveining` kontrollerer identitet og innhold før visning.

## Tasks & Acceptance

- [x] Gi de to flatene tilgang til samme midlertidige oppslag gjennom App. Del pågående forespørsel og ferdig kontrollert forklaring per sesjon, vakt, kandidat og merke. Avgrens levetiden til arbeidet med vakten. Ved direkte åpning av godkjenning hentes forklaringen ved behov. Bevar panelenes feilvisning, tastaturbetjening og vern mot sene svar.
- [x] Utvid `frontend/tester/komponenter/avveining.test.tsx` med kontrollerte, forsinkede svar. Prøv radene før første forklaring, uavhengig ferdigstilling og full App-navigasjon før og etter ferdig svar. Tell forespørslene. Kontroller at gjenbruk aldri krysser en grense i identitet eller levetid. Gjenbruk eksisterende tilfeller for omrangering, radfeil, StrictMode og godkjenning etter 409.
- [x] Dokumenter transportvalg og begrunnelse opp mot streaming og polling i `docs/ki-logg/2026-11-22-progressiv-lasting.md`. Flytt transportpunktet fra Deferred til gjeldende beslutning i `ARCHITECTURE-SPINE.md`. Knytt faktiske bevis til `docs/testing.md` og `docs/emne/vurderingsmatrise.md`.

## Implementation Notes

App deler forespørselen mellom flatene i minnet. Nettleserkontroll med 680 × 700 px og ekte FastAPI bekreftet at Mette fikk sin forklaring mens Jonas fortsatt ventet, og at det ble ett forklaringskall per åpnet kandidat. [KI-logg](../../docs/ki-logg/2026-11-22-progressiv-lasting.md).

## Spec Change Log

## Review Triage Log

| Funn | Vurdering | Kontroll eller retting |
|---|---|---|
| Blind 1 | medium | Transportfeil og svar med feil identitet kunne bli liggende i oppslaget. Etter rettingen kan en ny montering prøve igjen. En eksplisitt feil med riktig identitet kan gjenbrukes. |
| Blind 2 | low | Nettleserhistorikk utløser ny sesjonskontroll via popstate. Det starter en ny levetid for oppslaget. Appens «Avbryt» bevarer flyten. Dette er presisert i AD-4. |
| Blind 3 | low | StrictMode-testen gikk utenom App. Returtesten kjører nå begge flatene i StrictMode og teller forklaringskall. |
| Blind 4 | medium | Den første testen lot den vellykkede raden fullføre før feilen. En ny test snur rekkefølgen. |
| Blind 5 | low | «Vis færre» avmonterer rad seks. Testen åpner den på nytt mens svaret venter og kontrollerer ett GET. |
| Blind 6 | low | UX-dokumentet og listen over utsatte beslutninger viste gammel transportstatus. Begge viser nå til AD-4. |
| Blind 7 | low | Sprintstatus oppdateres til review ved overleveringen. |
| Grensetilfelle 1 | medium | Bekreftet at midlertidig feil hindret nytt forsøk ved ny montering. Dekket med HTTP 503, reserve og vellykket retur. |
| Grensetilfelle 2 | low | Testhjelperen forsinket alle metoder på samme sti. Den kontrollerer nå GET før den holder igjen et svar. |
| Testdekning 1 | medium | Forsinket HTTP 503 på godkjenningsflaten er nå dekket med reservetekst, aktiv knapp og ett opprinnelig GET. |
| Testdekning 2 | low | App-testen bruker «Avbryt» for å gå tilbake og kontrollerer at listen hentes på nytt mens forklaringen gjenbrukes. |

## Verification

Sluttkontrollen bestod med 52 modultester, 70 komponenttester, frontendbygg og 59 målrettede backendtester. Alle fem scenarier i matrisen er dekket. Kontrollen i Chrome mot ekte FastAPI ble gjentatt etter feilrettingen. [Resultater](../../docs/ki-logg/2026-11-22-progressiv-lasting.md).

Kjør `npm.cmd run build` og `npm.cmd run test` fra frontend, og eksisterende avveiningstester med pytest fra backend. Kontroller lastetekst, synlig fokus og radplassering på et smalt datamaskinvindu med ekte backend og forsinket falsk KI-transport (AV-17, OP-16). Gjennomgangen skal skille frontendens forespørsler fra adapterens eventuelle nye forsøk.
