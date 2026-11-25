# P-13: ekstern prøve og ny datafeiltekst

## Oppgave og prompt

Ragnhild gjennomførte P-13-forståelsestesten med en person utenfor gruppa (MJ,
ressursplanlegger med erfaring med turnus). Claude Code (Opus 5.5) startet appen i
demo-modus mot en egen testdatabase og satte opp testlederarket. Svarene ble limt inn i
økten. Ordrette svar og vurdering står i
[protokollen](../testing/2026-11-22/p13-protokoll.md).

MJ løste alle tre oppgavene, men skrev om datafeilen (B) at teksten «gir ikke mye
mening for meg. Dersom turnusgrunnlaget mangler, hvordan har da den tomme vakten
oppstått? Hva er det som ikke er rett i turnusen?» Ragnhild ba om at teksten ble endret.

## Leveranse

Modellen foreslo først: «Vakten ligger rett før slutten av turnusperioden. For å
kontrollere hviletid og ukentlig fri trengs vaktene etter [dato] …». Forslaget passet
#4261, men da modellen leste `vurder_kandidater` i `backend/domene/regelmotor/vurdering.py`,
viste det seg at samme datafeil også gis for ugyldige vakttider, feil i kandidatenes
vakter, ugyldig timelønn og manglende historikk. Frontend får bare `kode` og
`datagrense`. Forslaget ble forkastet før det ble implementert.

Ragnhild fikk to alternativer: en generell tekst i frontend, eller en årsakskategori fra
backend (endret API-kontrakt, AD-4, branch og PR). Hun valgte den generelle teksten.

Endret:

- `frontend/src/tekster.ts`: `kandidater.datafeil` sier nå hva appen trenger (vaktene i
  ukene før og dagene etter vakten) og hva som skal kontrolleres, uten å påstå én
  bestemt årsak.
- `frontend/tester/kandidater.test.mjs`: låser den nye ordlyden.
- `frontend/tester/komponenter/kandidatflate.test.tsx`: krever at visningen sier hva
  appen trenger og hva som skal kontrolleres.

Ingen endring i regler, API, CSS, datagrense eller godkjenningsflaten.

## Rettelser

- Det første tekstforslaget var faktisk feil for de fleste datafeilårsakene (se over).
  Det ble rettet før koden ble endret.

## Kvalitetssikring og resultat

- Med den gamle teksten i `tekster.ts` og de nye testene feilet 1 av 21 modultester i
  `kandidater.test.mjs` og 1 av 27 komponenttester i `kandidatflate.test.tsx`. Med den
  nye teksten består begge.
- `npm run build` bestod. `npm run test`: 52 modultester og 74 komponenttester bestod
  (macOS, 25.11.2026).
- Utelukkelsen MJ leste i A (Thomas Nygård, kolliderende vakt i #4189) er kontrollert
  mot API-et.
- Ingen uavhengig agentgjennomgang. Endringen er én tekststreng.
- Ragnhild kontrollerte den nye teksten i Safari på macOS i fullskjerm. Den brytes over
  tre linjer uten overlapp ([skjermbilde](../testing/2026-11-25/p13-ekstern-b-etter.png)).
- Ikke kontrollert: om den nye teksten er forståelig for en deltaker, og layout i smale
  vinduer eller med større skrift.
