# Reservetekst ved KI-feil

## 2026-11-21 kl. 15:40 — Kimsk81

### Oppgave

Bygg story 5.4 på egen branch med PR. Publiser branchen med nummer og beskrivelse slik at gruppa ser hvem som arbeider med storien.

### Plan

- Hent tittelen fra epicen, publiser branchen og sammenhold story 5.4 med vedtak AV-15, sensorveiledningen og implementeringen fra 5.3.
- Bruk [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-5-4-reservetekst-naar-ki-forklaringen-feiler.md) som grunnlag for gjennomføring og testing.

### Resultat

Branchen `story/5-4-reservetekst-naar-ki-forklaringen-feiler` ble publisert fra `378d8aa`. En underagent kontrollerte epic-konteksten og overgangen fra 5.3. Kode og tester ble lest lokalt. Begge flater viser allerede nøkkeltall og kildelinje ved feil. Spesifikasjonen i `f4efaa9` foreslår reserveteksten og beskriver hvordan feilmatrisen skal prøves fra adapter til godkjenning. Spesifikasjonen er et utkast ved første kontrollpunkt i bmad-build.

Kim godkjente spesifikasjonen med «godkjenn og fortsett». Implementeringen startet fra planutkastet i [PR #37](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/37). En egen implementeringsagent fikk den godkjente spesifikasjonen og epic-konteksten.

Implementering og dokumentasjon ligger i `ebe4ad8`. Gjennomgangen førte til kontroll av hele 90-sekundersfristen, håndtering av reset og brutt forbindelse, et statusfelt for skjermlesere og en test som finner begge åpne paneler på nytt. Ved sluttesten måtte en eldre test avgrense oppslaget til bekreftelsesboksen på godkjenningsflaten.

750 backendtester, frontendbygget, 52 modultester og 58 komponenttester bestod. Chrome ved 680 × 700 px viste reserveteksten før alle fire nøkkeltallene på begge flater. Simulert 402 for Jonas hindret verken forklaring for Mette eller lagret bemanning med Jonas. [KI-logg](../../docs/ki-logg/2026-11-21-reservetekst-ved-ki-feil.md).

### Åpne punkter

Ingen.
