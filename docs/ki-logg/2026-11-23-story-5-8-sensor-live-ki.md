# KI-logg: Story 5.8 – sensor kan kjøre live KI

Dato: 2026-11-23. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-5-8-sensor-kan-kjore-live-ki.md), [epic-konteksten](../../_bmad-output/implementation-artifacts/epic-5-context.md), AV-20 i [avklaringspunktene](../beslutninger/avklaringspunkter.md) og de utsatte punktene for 5.8 i [deferred-work.md](../../_bmad-output/implementation-artifacts/deferred-work.md). Arbeidet ble gjort av Claude Code (Opus 5.5) som implementeringsagent på branchen `story-5.8-sensor-live-ki`. Dokumentasjon pluss én ny komponenttest; ingen appkode er endret.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read _bmad-output/implementation-artifacts/spec-5-8-sensor-kan-kjore-live-ki.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **`README.md`:** live-punktet sier nå at nøkkelen settes i samme terminal som backend startes fra, hvordan sensor ser at live er aktiv (ingen «Demo-modus» i appbaren, forklaringer merket «KI-generert · openai/gpt-6-luna»), og lenker til «Feilsøking». Der står to nye punkter: «Demo-modus» selv om nøkkelen er satt (nøkkel i `.env` eller annen terminal), og oppbrukt kreditt eller ugyldig nøkkel (reservetekst, «kunne ikke tolkes» med 50 poeng, ingen krasj, ingen automatisk overgang til demo, og hvordan sensor starter i demo).
- **`docs/innlevering/sjekkliste-live-ki.md` (ny):** sjekkliste med avkrysningsbokser og ansvarlig-felt: ÅB-8 med begge utfallene, nøkkelsjekken av git-historikken, sjekk av at `.env` ikke er sporet, test fra ren klone i begge moduser, et utkast til teksten i innleveringen med plassholder for nøkkel og ansvarlig, og slettingen eller byttet etter sensur.
- **`docs/emne/vurderingsmatrise.md`:** status for 5.8 og lenker til sjekklisten fra «Funksjonalitet og omfang» og «Ryddighet i repoet».

## Korrigering og kvalitetssikring

Rettet underveis:

1. Første utkast til README la tre nye avsnitt med fet overskrift inn i live-punktet, med kommandoer for å fjerne nøkkelen. Ragnhild avviste endringen før den ble skrevet: README ble ryddet tidligere samme dag (`87db4d9`), med et kort KI-avsnitt og problemer samlet under «Feilsøking» som «symptom: tiltak». Endringen ble delt opp etter den strukturen: én setning og en lenke i live-punktet, og to punkter under «Feilsøking».
2. I sjekklisten sto «navngi den ansvarlige» først under «Etter sensur». Navnet skal stå i innleveringen, så punktet er flyttet til «I innleveringsteksten», og utkastet har en plassholder for navnet.
3. Orkestratorens kontroll mot spec-ens tabell over situasjoner fant at ingen test viste at appbaren er uten «Demo-modus» i live-modus, selv om README nå ber sensor se etter nettopp det. Spec-en forbød testendringer. Ragnhild valgte å legge til én komponenttest i [`avveining.test.tsx`](../../frontend/tester/komponenter/avveining.test.tsx) («live KI viser KI-kilden og ikke demomerket i appbaren»). Testen består, og den ble rød da `Appbar.tsx` midlertidig ble tvunget til alltid å vise demomerket. Hele frontend-bygget og alle 52 modultester og 75 komponenttester består.
4. En uavhengig gjennomgang fant disse feilene, og de er rettet:
   - Manglende «Demo-modus» ble brukt som bevis på live. Det beviser ikke live, fordi `ki_fra_miljo()` gir ingen KI og heller ikke noe demomerke ved ukjent `KI_MODUS`, en nøkkel med ugyldige tegn eller feil modellnavn. Live-sjekken i README, i sjekklisten og i utkastet til innleveringsteksten krever nå også merket «KI-generert · openai/gpt-6-luna». README nevner også demo-linjen i terminalen og har et nytt punkt under «Feilsøking» for nøkler med ugyldige tegn.
   - Punktet om oppbrukt kreditt sa ikke at backend må stoppes først. Ellers er port 8000 opptatt.
   - Nøkkelsjekken fant ikke nøkler i commits som bare ligger i PR-er (`refs/pull/*`), i merge-commits, i binærfiler eller i commit-meldinger. Sjekklisten henter nå PR-refs og bruker `-m --text` og en egen `--grep`. I et midlertidig repo traff den gamle kommandoen ingen av de fire tilfellene, og de nye traff alle. I en fersk klone av prosjektets GitHub-repo med 39 PR-refs ga de nye ingen treff. Kommandoene har bare doble anførselstegn uten `$`, så de virker likt i PowerShell og bash. PowerShell er ikke prøvd, fordi `pwsh` ikke finnes på maskinen.
   - Sjekklisten fikk OS for klonetesten (Windows og PowerShell der det er mulig, OP-05) og antall kall som grunnlag for ÅB-8.
   - `docs/testing.md` sier nå at komponenttesten dekker frontenddelen, og at det er KI-merket som viser live. `test_4xx_prøves_ikke_på_nytt` er sitert for «kunne ikke tolkes». Vurderingsmatrisen er oppdatert der den fortsatt sa «5.7–5.9».

Kontroller (macOS):

- `git log --all --oneline -E -G "sk-or-v1-[0-9a-f]{32}"` på repoet: ingen utskrift.
- Negativ kontroll i et midlertidig repo utenfor prosjektet (ikke committet): fire commits, der én la til en `.env` med en falsk nøkkel på riktig format (`sk-or-v1-` + 64 heksadesimale tegn), én fjernet den, og én la til `sk-or-v1-fake-key-for-tests`. Kommandoen viste commitene som la til og fjernet nøkkelen, og ikke de andre.
- `git ls-files | grep -i "\.env$"`: ingen utskrift.
- Tekstene README siterer, er sammenlignet med `frontend/src/tekster.ts` («Demo-modus», «Preferanse kunne ikke tolkes», «Reservetekst · KI-forklaring utilgjengelig», «KI-generert · <modell>») og logglinjen i `ki_fra_miljo()` i `backend/adaptere/api/main.py`.
- Påstandene om oppbrukt kreditt er sjekket mot koden og testene: 402 og andre 4xx gir `Tolkefeil("4xx")` uten nye forsøk (`backend/adaptere/ki/openrouter.py`), `avveining_feilet` for 402 og 403 i `backend/tester/api/test_avveining.py`, og tekster med lagret feil tolkes på nytt ved neste oppstart (`ventende_tekster`).
- Relative lenker og ankre i README, sjekklisten og vurderingsmatrisen er kontrollert mot filene og overskriftene.
- Ingen appkode er endret. Frontend-bygget og alle frontendtester er kjørt etter at komponenttesten kom til (se punkt 3). Ingen live-kall er gjort.

## Gjenstår

- Innleveringsoppgavene i sjekklisten (ÅB-8, nøkkelsjekk på innleveringscommiten, test fra ren klone med sensornøkkel, nøkkelen i innleveringsteksten og sletting etter sensur).
- Påstanden om at oppbrukt kreditt gir reservetekst, er dekket av tester med falsk OpenRouter, ikke prøvd mot en ekte tom konto.
