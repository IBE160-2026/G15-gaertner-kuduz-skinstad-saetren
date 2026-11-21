---
title: 'Story 5.4 – Reservetekst når KI-forklaringen feiler'
type: 'feature'
created: '2026-11-21'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Når en KI-forklaring mangler eller blir forkastet, skal turnusansvarlig forstå hva som skjedde og kunne bemanne vakten ut fra de beregnede tallene. Story 5.3 viser allerede kildelinjen og tallene på begge flater. Story 5.4 legger til selve reserveteksten og prøver feilene fra modellsvaret til godkjenningen (FR-11, NFR4, P-06).

## Boundaries & Constraints

Panelet henter teksten fra frontendens tekstliste. Foreslått ordlyd er «Vi kunne ikke vise en kontrollert KI-forklaring. Du kan bruke nøkkeltallene nedenfor til å vurdere kandidaten.» Vis teksten før nøkkeltallene og behold kildelinjen «Reservetekst · KI-forklaring utilgjengelig». Bruk samme tekst på kandidatlisten og godkjenningsflaten. Vis bare beregnede fakta og godkjente påstander. Ved live-feil beholder appen valgt KI-modus.

## I/O & Edge-Case Matrix

| Gitt | Når | Så |
|---|---|---|
| 402, annen 4xx, tomt eller ubrukelig svar | Forklaringen hentes | Ett forsøk gir HTTP 200 med `avveining_feilet`, vaktnummer, kandidat-ID og grunnlagsmerke. |
| Vedvarende 5xx, nettverksfeil eller transporttidsavbrudd | Adapteren prøver igjen | Vent 2, 4 og 8 s innen fristen. Endelig feil gir samme reservesvar. |
| 429 med reset innen budsjettet | Neste forsøk gir gyldig svar | Vent til reset og vis faktakontrollert forklaring. Ved reset utenfor budsjettet vises reservetekst innen 90 s fra første live-kall (AV-15). |
| Én gyldig og én ugyldig påstand | Faktakontrollen finner ukjent kandidat, feil faktor/referanse, feil kostnads- eller preferansepåstand, omvendt retning eller uriktig likhet før avrunding | Forkast hele svaret for både live og forhåndsgenererte påstander. |
| Modellen føyer til navnet på en faktisk utelukket ansatt | Svaret valideres | Reserveteksten vises. Navnet og forkastede påstander kommer aldri med i forklaringssvaret. |
| Bare én rad har feil | Brukeren åpner en annen rad, velger kandidaten med feil og bekrefter | Den andre raden kan vise gyldig forklaring. Kostnad, timebelastning, ulempebelastning og preferansekategori eller status med poeng vises fortsatt. Godkjenningen lykkes med gjeldende merke. |

</frozen-after-approval>

## Code Map

- `backend/adaptere/ki/openrouter.py` håndterer tidsbudsjett og forsøk i `_send`. `begrenser.py` deler 18 kall per 60 s og fem samtidige mellom KI-funksjonene. Gjenbruk falsk klokke og transport fra `backend/tester/ki/test_openrouter.py`.
- `backend/adaptere/ki/avveining.py` har `tillatte_påstander` og `valider`. Forklaringsruten i `backend/adaptere/api/main.py` omsetter manglende forklaring til kandidatbundet reservesvar. Bruk den samme valideringen på forhåndsgenererte testdata. Produksjonsoppsett, mal og demofiler leveres i 5.7.
- `frontend/src/komponenter/Avveiningspanel.tsx` brukes på begge flater. Panelet har egne tilstander for lasting, gyldig svar og reserve. `frontend/src/tekster.ts` inneholder kildelinjen.

## Tasks & Acceptance

- [ ] Legg reserveteksten i `frontend/src/tekster.ts` og vis den ved feil i `Avveiningspanel.tsx`. Når svaret er godkjent eller fortsatt lastes, viser panelet bare innhold for den aktuelle tilstanden.
- [ ] Utvid `backend/tester/api/test_avveining.py` og `backend/tester/ki/test_avveining.py` med udekkede tilfeller i matrisen. Bruk ekte rangering og faktakontroll, falsk HTTP for live og en testadapter med forhåndsgenerert svar. Verifiser gyldig kontrollsvar via begge veier, kandidatbundet feilstatus, frist, ventetider og antall forsøk. Rett påviste feil i adapteren og bevar eksisterende bevis for den felles begrenseren.
- [ ] Utvid `frontend/tester/komponenter/avveining.test.tsx` med en eksplisitt API-respons med `avveining_feilet`. Kontroller ny tekst, kildelinje, alle fire nøkkeltall og fullført godkjenning. La en annen rad lykkes samtidig og kontroller at dens kilde og forklaring gjelder rett kandidat.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

Kjør full pytest fra `backend/`, deretter bygg og tester fra `frontend/`. Kontroller tekstplassering og tastaturfokus i nettleser ved 680 px med ekte backend og uten betalte kall (AV-17, OP-16). Dokumenter faktisk testdekning, funn og rettinger i KI-logg, testveiledning og vurderingsmatrise.
