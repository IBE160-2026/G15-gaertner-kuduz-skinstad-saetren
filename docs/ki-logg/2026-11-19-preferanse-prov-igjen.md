# Story 5.1: brukerutløst nytt forsøk

## Oppgave og prompt

Kim ba Codex: «Start arbeidet etter din anbefalte rekkefølge. Opprett en branch og puch til gh først så de andre ser at vi er igang så kan du starte med arbeidet. Bruk bmad og subagenter der dette er tilrådelig». Arbeidet gjelder det utsatte brukerutløste forsøket etter feil i preferansetolkning (FR-10, P-05/OP-03). Kim godkjente spesifikasjonen og bekreftet AV-19 ved motstrid med eldre arkitekturtekst.

## Leveranse og rettinger

En implementeringsagent fikk den godkjente [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-5-1-prov-igjen.md) som oppdrag og laget API, brukerflate og tester. Orkestratoren oppdaget at oppstartstråden først ikke fikk samme lås som retry-endepunktet; agenten rettet koblingen og la til en test med appens faktiske oppstart. Det ble også rettet at vaktbytte kunne la valgene være sperret, og at tapt POST-svar kunne etterlate en foreldet rangering som grunnlag for valg. Nye komponenttester dekker disse tilfellene.

## Kvalitetssikring

Testene bruker falsk KI uten nettverkskall. Etter gjennomgangen bestod 685 backendtester, frontendbygget, 52 modultester og 46 komponenttester. Tre uavhengige gjennomganger fant blant annet fokusflytting, manglende test for rekkefølge og oppstartssnapshot samt tapte detaljer i epic-konteksten; funn og tiltak står i spesifikasjonen. Visuell kontroll med ekte backend gjenstår (OP-16). En lokal prosess deler låser mellom oppstart og brukerforsøk; låsene deles ikke mellom flere serverprosesser.
