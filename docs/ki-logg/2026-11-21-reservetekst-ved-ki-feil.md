# Story 5.4 – reservetekst ved KI-feil

## Oppgave og prompt

Kim ba om «bmad-build story 5.4 på egen branch med PR», ba om å ta beskrivelsen med i branchnavnet og godkjente spesifikasjonen med «godkjenn og fortsett». Gruppen kan følge arbeidet i [PR #37](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/37). En underagent hentet epic-konteksten. En egen implementeringsagent fikk den [godkjente spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-5-4-reservetekst-naar-ki-forklaringen-feiler.md) og beskjed om å implementere og verifisere den.

## Leveranse og retting

Panelet viser nå en forklaring på hva brukeren kan gjøre ved KI-feil, før de fire beregnede nøkkeltallene. Kildelinjen under tallene identifiserer reserveteksten. Begge flatene bruker den samme norske teksten. Testene følger tidsavbrudd, transportfeil og forkastede påstander gjennom adapteren. En testadapter med forhåndsgenererte påstander kaller den samme valideringsfunksjonen som live-adapteren. Adapteren er definert i testen, så den viser ikke at en ekte forhåndsgenerert kilde bruker kontrollen. Det må vises med demo-adapteren i story 5.7. Produksjonsoppsettet for demo hører til story 5.7.

Før rettingen stoppet en direkte `TimeoutError` fra en injisert transport etter første kall. En ny API-test forventet tre nye forsøk med venting på 2, 4 og 8 sekunder. Standardtransporten oversatte allerede et slikt tidsavbrudd til nettverksfeil. Rettelsen lar transporttråden behandle et direkte tidsavbrudd på samme måte. Sluttfristen for en transport som fortsatt kjører, gjelder fra første live-kall (AV-15).

## Uavhengig gjennomgang og sluttkontroll

Gjennomgangen fant at en skjermleser kunne gå glipp av veiledningen når en forespørsel feilet. Reserveteksten har nå et dynamisk statusfelt som finnes fra første gjengivelse. Komponenttesten kontrollerer at feltet beholdes og at den andre kandidatens panel fortsatt er tilgjengelig etter feilen. Den fulle testkjøringen avdekket at en eksisterende test søkte etter ett statusfelt på hele godkjenningsflaten. Testen søker nå i bekreftelsesboksen, der meldingen om endret grunnlag hører hjemme.

En API-test lar tidsavbruddene bruke 45 og 43 sekunder med to sekunders venting imellom. Adapteren stopper ved 90 sekunder. Andre tester dekker brutt forbindelse, reset nøyaktig ved sluttfristen og uleselig lange resetverdier. Alle 750 backendtester, frontendbygget, 52 modultester og 58 komponenttester bestod etter retting. [Gjennomgangsfunn og oppfølging](../../_bmad-output/implementation-artifacts/spec-5-4-reservetekst-naar-ki-forklaringen-feiler.md#review-triage-log).

## Nettleserkontroll

Chrome 158.0.8127.36 kjørte produksjonsbygget ved 680 × 700 px mot ekte FastAPI og en egen kopi av SQLite-testdataene. På vakt #4127 stod reserveteksten over nøkkeltallene både i kandidatlisten og på godkjenningsflaten. Jonas Bakke hadde 2 960 kr i vaktkostnad, 16 timer i uka, 40 ulempepoeng og ventende preferansetolkning med 50 poeng. Ved maksimal vannrett rulling var ulempekolonnen synlig i alle fire rader. Tab viste en 2 px fokusramme, og Enter åpnet neste panel.

I en egen kjøring ga den lokale transporten HTTP 402 for Jonas og gyldige påstander for Mette Solberg. Begge paneler var åpne samtidig med hver sin kildelinje. Etter valg av Jonas og bekreftelse med Enter svarte vaktoversikten «Jonas Bakke er godkjent for vakt #4127. Vakten er bemannet.» Alle modellresponser var lokale.
