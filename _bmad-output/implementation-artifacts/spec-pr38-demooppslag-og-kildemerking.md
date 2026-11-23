---
title: 'PR 38 – demooppslag og kildemerking'
type: 'bugfix'
created: '2026-11-22'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent">

## Intent

Sensor skal kunne følge forklaringen på #4127 uten API-nøkkel. Vis forhåndsgenererte og malbaserte svar med kildelinjene fra UX-DR27 og merk appbaren etter innlogging. Ved endring av vakt, kandidat eller referanse skal oppslaget gi mal etter AD-6, også når påstandsretningen fortsatt stemmer.

</frozen-after-approval>

## Implementation Notes

Gjenbruk de fire validerte modellsvarene og 15 tolkningene fra PR-en. Kontroller dem mot originalt seedgrunnlag før oppdatering av de lagrede nøklene. Verifiser begge visningene og regresjonen fra PR-gjennomgangen.

API og generator bruker samme avtrykk av vakt, kandidatens grunndata, hele den rangerte kandidaten, eventuell rangert referanse og kontraktsversjon. De eksakte poengene inngår med teller og nevner. Demoadapteren kontrollerer påstandene mot gjeldende tall etter treff. De fire lagrede svarene ble kontrollert mot det opprinnelige seedgrunnlaget før nøklene ble oppdatert. Modell, genereringsdato og råsvar er bevart.

Innlogging og sesjonsgjenoppretting rapporterer aktiv demomodus. Begge flater bruker samme panel. Modellen og genereringsdatoen kommer fra datafilen.

Sluttkontroll 2026-11-23: 882 backendtester, 52 Node-tester og 62 komponenttester bestod. Frontendbygget og generatorens tørrkjøring bestod. [Nettleser og modellbruk](../../docs/ki-logg/2026-11-22-demo-modus-uten-api-nokkel.md#rettelser-etter-gjennomgang-av-pr-38).

## Review Triage Log

- Høy, rettet. Første utkast hashet den rangerte kandidaten, men utelot kandidatens øvrige grunndata. Testen holder rangeringen fast og endrer en annen kompetanse.
- Høy, rettet. Et nytt nøkkelord på den felles forklaringsporten ville fått eldre adaptere til å feile. Den opprinnelige porten er bevart. Demoadapteren har et eget oppslag som får avtrykket.
- Middels, rettet. En direkte typesjekk mistet dato og demomerking ved innpakking. Oppslagsporten er strukturell. En API-test sjekker den innpakkede demoadapteren med levert innhold.
- Middels, rettet. Standardmodell kunne bli vist som kilde når modellnavnet manglet. Manglende eller blank modell og ugyldig dato gir mal.
- Lav, rettet. Frontend godtok datoer som 31. februar. En komponenttest kontrollerer at svaret forkastes.
- Middels, rettet. Et bytte av bare vaktnummer manglet regresjonstest. Testen holder kandidat og referanse faste.
- Middels, rettet. README, testveiledningen, vurderingsmatrisen og oppfølgingspunktet for UI beskrev den tidligere implementeringen. De er oppdatert med dagens flyt og testbevis.
