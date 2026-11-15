# KI-logg: Story 4.1 – timer i perioden per kandidat

Dato: 2026-11-15. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-1-timer-i-perioden-per-kandidat.md), [Epic 4-konteksten](../../_bmad-output/implementation-artifacts/epic-4-context.md), `AGENTS.md` og [gruppevedtakene](../beslutninger/avklaringspunkter.md) (FR8, P-02, AV-13, AV-17, OP-16). Storytabellen anbefaler Sonnet med gjennomgang på Opus. Økten og implementeringsagenten kjørte Claude Sonnet 5.5; Blind Hunter kjørte Opus.

## Oppgave og prompt

Brukeren ba om bmad-build for story 4.1, etter at story 3.2 var merget inn i branchen. Spesifikasjonen fantes allerede (`ready-for-dev`, beslutningene fra Ragnhild 2026-11-15). Implementeringsagenten fikk uten forutgående samtalekontekst denne instruksen:

> Read …/spec-4-1-timer-i-perioden-per-kandidat.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start.
>
> When done, report what you changed, how you verified it, and anything left incomplete or risky.

## Modellens leveranse

- `domene/regelmotor/timer_i_uka.py`: `timer_i_startuka` (union av vaktene klippet mot første uke fra `berørte_uker`, i UTC, halvåpne intervaller) og `minutter_i_uka` (hele minutter, rundet ned).
- Feltet `minutter_i_uka` på `KandidatUt`, satt i kandidatruten og godkjenningsgrunnlaget.
- Frontend: `timerOgMinutter` i `format.ts`, verdien «32:00 t i uka» i hver rad i kandidatlisten, token `--column-hours-width`.
- Tester: ny backendmodul for I/O-matrisen (begge sommertidsskifter, ukeskifte, union), API-tester for Ingrid 1920 og Jonas 960, formattester og komponenttest for 0:00.

## Retting og kvalitetssikring

Hovedøkten leste diffen mot spesifikasjonen; alle oppgaver og matriserader var dekket. Tre uavhengige gjennomgangsagenter (Blind Hunter på Opus, Edge Case Hunter og Verification Gap) ga funn som er vurdert enkeltvis i spesifikasjonens Review Triage Log. Dette ble rettet:

- Formattesten for `timerOgMinutter` var lagt inne i grenen som bare kjører i underprosessen med TZ=America/New_York, med ødelagt innrykk. Den kjørte dermed ikke som egen test i Oslo-sonen. Flyttet ut ved siden av de andre rene formattestene.
- Docstringen for `timerOgMinutter` motsa koden (brøkdeler rundes ned, ikke 0:00). Rettet, og tester for brøk, negativt tall og NaN lagt til.
- Kommaet i `test_godkjenningsgrunnlag.py` havnet inne i en kommentar, og testnavnet sa «bare id, navn og nivå» mens det nå er fire felt. Begge rettet.
- Manglende grensetester: Vakten som bemannes starter søndag natt (teller uka den starter i), Vakten starter mandag 00:00, og avrunding av sekunder til hele minutter. Lagt til.

Ett funn ble først utsatt som uverifisert: ugyldige vakter hoppes stille over, og startuka er ikke sjekket mot datagrensen. Ved nærmere undersøkelse var det ikke en feil: 35-timersregelens vindu er hele startuka, og `vurder_kandidater` gir `Datafeil` før tallet beregnes. Hovedøkten hadde antatt et smalere vindu uten å slå det opp. Funnet er avklart i `deferred-work.md`, og docstringen til `timer_i_startuka` sier nå at kalleren må ha vurdert grunnlaget.

Etter rettingene kjørte hovedøkten hele pakken: **442 av 442 backendtester** og frontendbygg, modultester og komponenttester (24 av 24) bestod. Ingen tester gjorde KI-kall. Manuell kontroll ble deretter utført av Ragnhild på macOS/Safari; resultat og forbehold står i spesifikasjonens Verification. Skjermleseren utelot enheten og minuttene, og ny kontroll etter retting gjenstår.

## Oppfølging etter PR 25-gjennomgang

Kim ba Codex rette tre funn: ufullstendig skjermleseropplesing, foreldet dokumentstatus og komponenttest uten kobling mellom kandidat og timeverdi. Codex la til visuelt skjult, utvidet tekst og en radvis komponenttest, og samordnet kontrollstatusen. Den opprinnelige synlige teksten er skjult for hjelpeteknologi slik at verdien ikke leses dobbelt. Faktisk opplesing med skjermleser må fortsatt kontrolleres; automatisk test bekrefter bare HTML og tekst.

Kvalitetssikring: frontendbygg, 50 modultester og 25 komponenttester bestod. En uavhengig gjennomgang fant ingen konkrete feil. Oppfølgingen rettet tidligere generert kode som lot VoiceOver utelate timeenhet og minutter, samt en test som ikke kontrollerte koblingen mellom kandidat og verdi.
