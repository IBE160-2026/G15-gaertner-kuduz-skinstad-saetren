# Synkronisering av storyfigur

## Oppgave og prompt

Brukeren ba om et skript som oppdaterer grønn status i avhengighetsfiguren fra sprintstatus, en CI-kontroll og dokumentasjon, og om å pushe endringene.

## Leveranse og rettinger

Codex laget et Python-skript med kontrollmodus, tester og en GitHub Actions-kontroll. Først fikk alle ferdige stories et «Ferdig»-prefiks også på avhengighetsnotater; det ble endret slik at notatene beholdes og bare faktiske statustekster byttes. Dette hindrer unødvendig lange etiketter og bevarer informasjonen i figuren.

## Kvalitetssikring

Automatiske tester dekker statusendring, gjenkjøring, reversering, ukjent status samt manglende og doble storyer. Figuren kontrolleres mot faktisk sprintstatus. En uavhengig agent gjennomgår endringene; funn og vurderinger står i spesifikasjonen.

Gjennomgangen oppdaget også at feilformede verdier, tomme duplikater og doble statusseksjoner kunne overses. Skriptet avviser nå disse, og tester dekker feilene og kommandolinjens kontroll- og skrivemodus.
