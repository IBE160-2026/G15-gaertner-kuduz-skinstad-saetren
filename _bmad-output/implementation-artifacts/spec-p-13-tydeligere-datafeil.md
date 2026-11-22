---
title: 'P-13: tydeligere skille mellom datafeil og ingen gyldige'
type: 'bugfix'
created: '2026-11-22'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent">

## Intent

I den interne P-13-prøven oppfattet Kim datafeil som at gyldige kandidater fantes,
men ikke kunne velges. Ved null gyldige fant han ikke et klart neste steg.
Gi datafeil en nøytral overskrift og presiser at gyldighet ikke kan avgjøres.
Flytt den vedtatte teksten «Innleie av personell kan vurderes» foran
utelukkelsesboksen og bruk eksisterende brødtekststil. Ingen nye knapper, regler,
dataverdier, farger eller tilgangsfunksjoner. P-13 forblir åpen for en ekstern person.

</frozen-after-approval>

## Implementation Notes

Liten retting på eksisterende main etter faktisk brukerobservasjon. Egen agent
har samlet epic-2/P-08/P-11/P-13-kontekst. Endre bare `Kandidatflate.tsx`, tekstlisten
og relevante komponenttester; bevar datagrensen og fraværet av tabell/valg ved datafeil.
Kontroller gjeldende regionnavn i testhjelperen når datafeiloverskriften endres.

Renmodultesten `frontend/tester/kandidater.test.mjs` låste den gamle teksten og er
også oppdatert. Ingen API-/domenelogikk eller CSS er endret.

## Review Triage Log

| Funn | Vurdering og tiltak |
| --- | --- |
| Brødtekststil manglet test | low, rettet med kontroll av `brodtekst` og fravær av `meta`, i tillegg til rekkefølgen. |
| Testhjelper tillater begge regionnavn | low, hjelperen tåler lasting/ferdig svar, mens eksplisitte påstander nå låser riktig overskrift ved datafeil, ordinær liste og null gyldige. |
| Manuell kontroll og ekstern P-13 manglet i spesifikasjonen | low, kontroll og avgrensning dokumentert nedenfor. |

## Verification

To utvidede komponenttester feilet på gammel kode: datafeilens overskrift og
plasseringen av innleieteksten. Etter retting bestod frontendbygget, 52 modultester
og 57 komponenttester. En gammel ordrett forventning i modultesten ble oppdatert
til den tilsiktede teksten. Etter gjennomgangens testpresiseringer kjøres bygg og
hele kandidatflate-modulen på nytt.

Begge tilstander er kontrollert visuelt mot ekte backend ved 680/1600 × 700 px med
16/20 px grunnskrift. Ingen siderulling eller tekstoverlapp; datagrense og fravær av
valg ved datafeil er bevart. [Før-/etter-bilder og prøve](../../docs/testing/2026-11-22/p13-protokoll.md).
Kim får ny kontroll etter forklaring. Dette er ikke en prøve uten hint. Ekstern
P-13 og problemvalidering holdes åpne, uansett resultat av den interne oppfølgingen.

Etter oppfølgingen forstod Kim at vurderingen stopper, men beskrev fortsatt manglende
neste steg. Endelig tekst gir derfor også beskjed om kontroll/oppdatering av
turnusgrunnlaget før ny vurdering. Hele frontendbygget og 52 + 57 tester bestod
igjen etter dette siste tillegget; en målrettet uavhengig oppfølging fant ingen nye
problemer. Endelig B er kontrollert ved begge bredder og skriftstørrelser. Den
siste setningen er ikke testet uten hint med en deltaker.
