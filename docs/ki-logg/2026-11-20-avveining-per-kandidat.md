# Story 5.3 – avveining per kandidat

## Oppgave og prompt

Kim ba først om å finne hvor arbeidet hadde stoppet. Repoet inneholdt et gjennomgått utkast, mens produksjonskode og tester gjenstod. Kim godkjente utkastet med «godkjent og fortsett arbeidet med hjelp av subagenter». Den [godkjente spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-5-3-avveining-per-kandidat.md) gir oppgaven, akseptansematrisen og filene agenten skulle arbeide med.

## Føringer fra gruppa

Kim valgte kandidatens egen eksakte totalscore som sammenligningspunkt for om en faktor trekker opp eller ned. Det gjør for eksempel 60 kostnadspoeng til en faktor som trekker ned når totalscoren er 80 og vekten er positiv. Koden skal kontrollere hver påstand før den setter inn navn og tall. En annen kandidat kan bare omtales når den er referansen som rangeringen har bestemt. Kildene er FR-11 og [P-06, P-07 og AV-15](../beslutninger/avklaringspunkter.md).

En underagent kontrollerte epic-konteksten mot produktkrav og arkitektur. En egen implementeringsagent fikk spesifikasjonen og beskjed om å lese kontekstfilen før arbeidet.

## Gjenopptakelse og test 2026-11-21

Kim ba om å sjekke status og fortsette med underagenter. Den avbrutte økten hadde etterlatt implementasjon, tester og målinger fra nettleseren. I første fulle frontendkjøring feilet to eldre tester. «Velg»-testen begynte å telle før forklaringen for nr. 1 var hentet. Den venter nå på at reserveteksten vises før den sjekker at valget gir null nye API-kall. Testen av kandidatkortet fant to forekomster av «Ulempebelastning». Oppslaget er avgrenset til etiketten ved kortets nøkkeltall.

Etter retting bestod frontendbygget, 52 modultester og 57 komponenttester. Alle 711 backendtester bestod med Python 3.14.7 og de låste testavhengighetene. Pytest fikk en egen midlertidig mappe fordi brukeren manglet tilgang til den eksisterende pytest-mappen. Modellkall i testene gikk mot falsk transport.

Tre uavhengige underagenter fikk deretter den samlede diffen. Gjennomgangen fant blant annet at den sjette samtidige forespørselen kunne bli avvist straks, og at en påbegynt transport kunne overskride sluttfristen. En test fyller begrenseren og frigir en plass. En annen holder transporten igjen og kontrollerer at avveiningen returnerer innen fristen, uten å frigjøre modellens plass for tidlig. Ved permanent hengende transport forblir plassen opptatt til transporten avsluttes eller prosessen startes på nytt.

Et modellobjekt med to motstridende retningsfelt kunne passere fordi JSON-leseren beholdt siste verdi. Den nye kontrollen avviser begge, og en test leser skjemaet som faktisk sendes til transporten. Gjennomgangen fant også at 62,25 kunne vises som både 62,2 og 62,3. Forklaring og panel bruker nå samme avrunding til én desimal, mens faktakontrollen fremdeles bruker eksakte brøker. Etter alle rettingene bestod 717 backendtester, frontendbygget, 52 modultester og 57 komponenttester. [Alle funn og rettinger](../../_bmad-output/implementation-artifacts/spec-5-3-avveining-per-kandidat.md#review-triage-log).

## Nettleserkontroll

Vi brukte Chrome 158.0.8127.36 på Windows, Vite og FastAPI mot en egen midlertidig SQLite-database med prosjektets testdata. Første kjøring hadde KI avslått. I andre kjøring gikk OpenRouter-adapteren gjennom sin vanlige svarvalidering med en lokal transport som valgte to faktorpåstander fra forespørselen. Ingen av kjøringene krevde en nøkkel eller gjorde betalte kall.

På vakt #4127 fikk Jonas Bakke merket reservetekst i første kjøring. Den andre viste beregnede kostnadspoeng på 84,8 mot hans egen totalscore på 79,4 og kildelinjen med testmodellens navn. Begge flatene viste vaktkostnad på 2 960 kr, tidsbelastning på 16 timer, 40 ulempepoeng og en preferanse som ventet på tolkning med 50 poeng. Godkjenningsknappen var tilgjengelig i begge tilfeller.

Ved 680 × 700 px tok det loddrette rullefeltet 15 px. Med tabellen rullet helt til høyre lå panelet innenfor rullebeholderen, og hele ulempekolonnen var synlig. Enter åpnet og lukket Mettes panel mens Jonas sitt forble åpent. Chrome viste heltrukket fokusramme på 2 px. Beregnede farger var `#f2f6f9` på panelet, `#1f7a4d` for opp og `#8c2f2f` for ned.

Etter gjennomgangsrettingene 2026-11-21 gjentok en underagent kontrollen med nytt frontendbygg, ekte FastAPI og en isolert kopi av testdataene. Etter 407 px vannrett rulling var hele ulempekolonnen synlig for alle fire kandidater, og siden holdt seg innenfor vinduet. Tab nådde Mettes knapp med 2 px fokusramme, og Enter lot Jonas sitt panel stå åpent. Begge flater viste 50,0 preferansepoeng for ventende tolkning. Kildelinje, nøkkeltall og tilgjengelig godkjenning var som forventet i både reserve- og transporttesten.
