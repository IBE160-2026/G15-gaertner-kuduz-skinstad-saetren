# P-13: datafeil og neste steg

## Oppgave og prompt

I oppfølgingen av åpne punkter ba Kim om en faktisk P-13-prøve, dokumentasjon av
misforståelser og eventuell retting og ny kontroll. Etter å ha sett riktig bilde
oppfattet han datafeil som at gyldige kandidater fantes, men ikke kunne velges.
Ved null gyldige visste han ikke hva han kunne gjøre videre. Ordrette svar og
før-/etter-bilder finnes i [protokollen](../testing/2026-11-22/p13-protokoll.md).

Kim presiserte at intern prøve ikke skal lukke punktet: en person utenfor gruppen
skal også testes senere. Dette er bevart i issues og sprintstatus.

## Leveranse

Codex/GPT-6 brukte `bmad-build` for et lite oneshot-arbeid og en separat agent til
P-08/P-11/P-13-/epic-kontekst. Modellveiledningen anbefaler Sonnet for UI-visning;
økten fortsatte i Codex etter prosjektets Codex-unntak. `impeccable` ble brukt til
tekstpresiseringen. Kontekstverktøyet kunne ikke laste motoren på grunn av manglende
lokal motor/cachetilgang; eksisterende produktbrief, DESIGN og rendret app ble brukt direkte.

`Kandidatflate.tsx` viser «Kandidatvurdering» ved datafeil, og `tekster.ts` presiserer
at appen ikke kan avgjøre hvem som er gyldig. Innleietekstens vedtatte ordlyd beholdes,
men flyttes før utelukkelsesboksen og bruker eksisterende brødtekststil.
Ingen CSS, regler, API, datagrense eller nye knapper er lagt til.

## Rettelser og gjennomgang

To komponenttester ble utvidet før implementeringen og feilet på gammel overskrift
og gammel rekkefølge. Den første hele frontendkjøringen avdekket også at en ren
modultest låste gammel ordlyd; forventningen ble oppdatert til den tilsiktede teksten.

En blind gjennomgang fant tre hull i beviset, som ble rettet: brødtekststil måtte
testes, normal-/tomtilstandens overskrift måtte fortsatt låses, og manuell kontroll
med ekstern prøve måtte stå i spesifikasjonen. [Triage og spesifikasjon](../../_bmad-output/implementation-artifacts/spec-p-13-tydeligere-datafeil.md).

## Kvalitetssikring og resultat

- Frontendbygget bestod, inkludert typesjekk av komponenttester.
- 52 modultester og 57 komponenttester bestod i én sekvensiell kjøring.
- Etter gjennomgangens testpresiseringer bestod bygg og 27 kandidatflatetester igjen.
- Ekte backend i isolert testdatabase: A og B ble sett ved 680/1600 × 700 px,
  16/20 px grunnskrift, uten siderulling eller tekstoverlapp.
- Kim fant A mer forståelig etter rettingen. På B oppfattet han stopp i vurderingen,
  men visste fortsatt ikke neste steg. Den siste teksten angir derfor at turnusgrunnlaget
  må kontrolleres og oppdateres før ny vurdering. Det er ingen ny redigeringsfunksjon.
  Den siste setningen er visuelt/teknisk kontrollert, men ikke forståelsestestet uten hint.
- Kims forslag «burde vurderes» er dokumentert, men «kan vurderes» beholdes fra P-11.

P-13 og problemvalidering er fortsatt åpne. Kim har ingen egen erfaring med å finne
erstatter til vakt; denne interne prøven dokumenterer derfor ikke validert brukerbehov.
