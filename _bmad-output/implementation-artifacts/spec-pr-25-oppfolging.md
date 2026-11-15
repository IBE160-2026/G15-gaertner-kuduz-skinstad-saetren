---
title: 'PR 25: Oppfølging av gjennomgang'
type: 'bugfix'
created: '2026-11-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Skjermleser utelater minutter og enhet i timeverdien. Testen knytter ikke verdier til kandidatrader, og dokumentasjon viser foreldet status.

**Approach:** Behold synlig t:mm, gi forståelig opplesing av timer og minutter, test hver kandidats verdi, og samordne dokumentasjonen med faktisk manuell kontroll. Manuell skjermleserkontroll forblir åpen til den er utført.

</frozen-after-approval>

## Implementation Notes

- Bruker eksisterende `.visuelt-skjult` for opplest tekst og `aria-hidden` for den synlige forkortelsen. Begge tekstene avledes fra samme formatterte verdi.
- Testen kontrollerer kandidatens rad, null, minutter og entall. KI-logg og Ragnhilds issues er samordnet; faktisk skjermleserkontroll gjenstår.
- `npm run test`: 50 modultester og 25 komponenttester bestått; frontendbygg bestått. En uavhengig gjennomgang fant ingen konkrete feil.
