---
title: 'Story 5.3: Avveining per kandidat'
type: 'feature'
created: '2026-11-20'
status: 'done'
baseline_commit: 'a211167dbf09c065f9daa270a81e9bd1d69d3e9e'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Turnusansvarlig skal forstå hvorfor en gyldig kandidat kan ta vakten og hvilke faktorer som påvirker plasseringen. Vis avveiningen både i kandidatlisten og på godkjenningsflaten (FR-11).

## Boundaries & Constraints

Regelmotoren beregner harde regler, tall, poeng og rekkefølge. KI velger strukturerte påstander om ferdig beregnede fakta. Koden kontrollerer dem og setter inn navn og tall. For kandidatens egne faktorer er sammenligningspunktet kandidatens eksakte totalscore (valg B). Høyere faktorpoeng trekker opp, lavere trekker ned. Like verdier gir ingen retning.

## I/O & Edge-Case Matrix

| Gitt | Når | Så |
|---|---|---|
| Minst to gyldige | En rad forklares | Nr. 1 sammenlignes med nr. 2, øvrige med nr. 1, også ved lik totalscore (P-07). |
| Én gyldig | KI viser til en annen kandidat | Forkast hele svaret. Egne faktorer kan brukes alene. |
| 60 kostnadspoeng og 80 i totalscore | KI sier at kostnadsfaktoren trekker ned | Godta retningen. «Trekker opp» forkaster svaret. |
| En faktor har null vekt | KI hevder at faktoren trekker opp eller ned | Forkast begge retninger. Bare faktorer med positiv vekt påvirker totalen. |
| Like eksakte faktorpoeng hos to kandidater | KI hevder likhet for denne faktoren | Godta. Forkast hvis bare visningstallene eller float-verdiene er like. |
| Én kandidat med alle faktorpoeng lik totalscoren | Ingen gyldig myk påstand finnes | Vis merket reservetekst. |
| Feil felt, faktor, kandidat, retning eller modellens egne navn/tall | Et svar valideres | Én feil forkaster alle påstandene (P-06), også for forhåndsgenererte svar. |
| Ny visning mens et kall pågår | Svaret kommer | Vis bare svar for aktiv sesjon, vakt, kandidat og gjeldende merke (P-09). |

</frozen-after-approval>

## Code Map

- `backend/domene/regelmotor/rangering.py` har eksakte brøker før `domene/porter/rangering.py` konverterer til float. Bevar eksakte faktasammenligninger i porten. Behold dagens numeriske JSON-felt.
- `backend/adaptere/lagring/kandidatgrunnlag.py` binder godkjenningsmerket til bruker, vakt, kandidat og databasegrunnlag. Hver rad får sitt eget kandidatbundne merke. For samme grunnlag skal kandidatens rad, forklaringssvar og godkjenningsflate ha identiske merker. Les grunnlagsradene én gang per forespørsel.
- `backend/adaptere/api/main.py` har eksplisitt SQLite-lesetransaksjon for godkjenningsgrunnlaget. Bruk samme mønster på listen og forklaringsruten. Beregn opphavsmerket på serveren fra samme øyeblikksbilde som rangeringen. Avslutt transaksjonen før KI-kallet.

## Tasks & Acceptance

- [x] I `backend/adaptere/ki/avveining.py`, valider lukket skjema for oppfylte prototyperegler, egen faktor opp/ned og faktor/total høyere, lavere eller lik angitt referanse. Krev minst én verifisert myk faktor. Test at høyere kostnadspoeng kan bety lavere kronebeløp, og skill ulempescore fra ulempepoeng.
- [x] Koble `backend/adaptere/ki/openrouter.py` til beskyttet forklaringsrute. Velg referanse fra hele gyldiglisten. Test ukjent eller utelukket ID mot samme 404 og null KI-kall. Når listen eller godkjenningsgrunnlaget beregnes, skal forklaringsporten ha null kall.
- [x] Gjenbruk delt begrenser og AD-7s venteregler. Test med falsk klokke at 90 sekunder for avveiningen regnes fra første live-kall. Ved ubrukelig svar returneres HTTP 200 med `status: avveining_feilet` og opphavsmerket. Gyldig live-svar har `ki_kilde: live` og modellnavn.
- [x] Utvid `frontend/src/api.ts`, `kandidater.ts`, `komponenter/Kandidatflate.tsx` og `Godkjenningsflate.tsx` med felles panel. Vis kvalifikasjon, opp/ned der grunnlaget gir det, vaktkostnad, time- og ulempebelastning og faktisk preferansekategori eller status med poeng. Ventestatus med 50 poeng beskrives som ventende. Behold nøkkeltall og valg ved feil. Bruk bare beregnet kvelds-, helge- og nattfordeling.
- [x] Ved åpning er nr. 1 utvidet. Andre rader hentes først ved åpning. «Vis begrunnelse ▾» og «Skjul begrunnelse ▴» virker med tastatur uavhengig per rad. Bruk UX-DR12s panelfarge og opp-/nedmarkeringer. Bare godkjente live-svar viser «KI-generert · <modellnavn>». Bruk reservetekstens egen kildelinje ved feil.
- [x] Test gamle og nye svar på begge flater i `frontend/tester/komponenter/`. La en ny preferansetolkning endre rangeringen og en 409 utløse nytt godkjenningsgrunnlag. Sjekk at feil kandidat og gamle svar avvises, at ny gyldig tekst vises, og at godkjenning fortsatt bruker POST-merket fra gjeldende grunnlag.

## Implementation Notes

Kandidatlisten, avveiningen og godkjenningsgrunnlaget bruker samme rangeringsfunksjon og kandidatbundne merke. Forklaringsruten frigir SQLite-transaksjonen før den venter på modellsvaret. Regelmotoren sender de eksakte poengene og faktorene med positiv vekt til faktakontrollen. Panelet på begge flater viser beregnede nøkkeltall også når svaret forkastes.

[Faktakontrolltestene](../../backend/tester/ki/test_avveining.py) dekker 60 mot 80, nullvekt, ulike brøker med samme visningstall, én kandidat og forkasting av hele svaret. [API-testene](../../backend/tester/api/test_avveining.py) kontrollerer blant annet referansen ved poenglikhet og at databasen kan oppdateres mens modellen svarer. [Komponenttestene](../../frontend/tester/komponenter/avveining.test.tsx) følger gamle og nye svar gjennom sesjonsbytte, ny preferansetolkning og ny bekreftelse etter HTTP 409. [KI-loggen](../../docs/ki-logg/2026-11-20-avveining-per-kandidat.md) dokumenterer nettleserkontrollen.

## Spec Change Log

## Review Triage Log

Tre underagenter gjennomgikk endringene uavhengig. Tabellen viser vurderingen av hvert funn og hvordan det ble fulgt opp.

| Gjennomgang | Vurdering | Funn og retting |
|---|---|---|
| Blind 1 | medium | En opptatt semafor med negativ ventetid avviste første kall straks. En avveining i kø venter nå på ledig plass. En trådtest frigir plassen og ser at kallet starter. |
| Blind 2 | high | Et tregt HTTP-svar kunne holde panelet i ventetilstand etter 90 sekunder. En egen sluttfrist frigir forespørselen mens transporten beholder plassen sin. Testen holder transporten igjen til etter at avveiningen har returnert. |
| Blind 3 | medium | Python og nettleseren viste ulike tideler for samme poeng. Begge bruker nå samme visningsregel. Testene dekker midtpunkter og hele poeng. |
| Blind 4 | low | Forklaringen av egne faktorer viste bare avrundede tall som begrunnelse for retningen. Både panelet og modellens validerte faktortekst opplyser at sammenligningen skjer før avrunding. |
| Blind 5 | medium | Den faste kvalifikasjonsteksten kunne leses som en generell hvilegaranti. Den beskriver nå prototypens kontroller rundt denne vakten og i berørte kalenderuker (AV-04). |
| Blind 6 | medium | En sammenligning av en faktor med null vekt kunne alene oppfylle kravet til en relevant myk faktor. Den kan nå bare være tilleggsinformasjon når en aktiv myk faktor også er med. |
| Blind 7 | medium | JSON-leseren beholdt siste verdi for gjentatte felter. Forklaringsadapteren forkaster nå tvetydig JSON. Tre regresjonstilfeller dekker gjentatt kandidat, retning og påstandsliste. |
| Blind 8 | low | Oppslag på en ukjent vakt hentet alle grunnlagsradene. Kandidatgrunnlaget sjekker nå synligheten med samme SQL-filter som vaktdetaljene før det leser hele tabeller. En API-test teller lesingene. |
| Blind 9 | medium | Flere sammenfoldede knapper fikk samme tilgjengelige navn. Knappene identifiserer nå kandidaten i skjermleserens knappeliste. Komponenttesten dekker to lukkede rader. |
| Blind 10 | low | Vurderingsmatrisen manglet milepælen for 5.3. Matrisen er oppdatert med lenker til bevis. |
| Grensetilfeller 1 | medium | Bekreftet at negativ ventetid feilet ved opptatt semafor. Rettet og testet under Blind 1. |
| Grensetilfeller 2 | medium | Bekreftet forskjellig avrunding ved et midtpunkt. Rettet og testet under Blind 3. |
| Grensetilfeller 3 | medium | Motstridende felt kunne passere validering. Rettet og testet under Blind 7. |
| Grensetilfeller 4 | medium | Begrunnelsesknappen manglet kandidatnavn i det tilgjengelige navnet. Rettet og testet under Blind 9. |
| Testdekning 1 | medium | Den falske transporten kunne gi grønt selv med preferansetolkningens skjema. En ny test leser det faktisk utsendte skjemaet og sjekker variantene, de obligatoriske feltene og tillatte verdier. |
| Testdekning 2 | medium | Eksakthetstesten injiserte brøkene etter rangering. Regelmotorens regneeksempel kontrollerer nå at begge eksakte totaler i porten er 60/7 + 15. |
| Testdekning 3 | medium | En ombytting av opp og ned kunne passere paneltesten. Testen sjekker nå retning og poeng i feltet for hver faktor. |

## Verification

Sluttkontroll 2026-11-21 på story-branchen: 717 backendtester, frontendbygg, 52 modultester og 57 komponenttester bestod. En underagent gjentok kontrollen i Chrome med begge kilder etter gjennomgangsrettingene. Alle fire kandidatrader hadde synlig ulempekolonne ved 680 × 700 px med 15 px loddrett rullefelt og maksimal høyreskrolling. Begge flater viste nøkkeltall og riktig kilde. Sprintstatus er `review` i påvente av gruppas gjennomgang.

Kjør pytest, frontendbygg og frontendtester uten betalte kall. Kontroller fokus, farger og ekte backend ved 680 px med loddrett rullefelt og helt høyrescrollet tabell (4.6, AV-17/OP-16). Avveiningen lagres ikke ved godkjenning (P-12). Dokumenter tester, uavhengig kodegjennomgang og rettinger i KI-logg, testveiledning og vurderingsmatrise. Story 5.4–5.7 beholder full feilmatrise, progressiv transport, lekkasjetest på tvers av moduser og demooppsett.
