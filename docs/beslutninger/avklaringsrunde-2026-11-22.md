# Fire gjenstående gruppevalg

Forslag til én samlet avklaringsrunde 22.11.2026. Dette er **ikke vedtak**.
Hele gruppa er beslutningseier for sensoropplegget (AV-16/ÅB-8). Kim kan føre
gruppas svar når fullmakten eller enigheten er bekreftet. Ingen nøkkel, betaling
eller kontoendring utføres som del av denne dokumentasjonen.

| Valg | Anbefaling og konsekvens | Konkret vedtakstekst til godkjenning |
| --- | --- | --- |
| Nattevakters sluttdato | Behold startdato som v1-konvensjon og utsett en samlet endring til v2. Det bevarer konsistens mellom flatene og unngår en ny UI-endring før levering. Nattskift går fortsatt over midnatt; faktisk varighet beregnes som før. | «Gruppa viderefører startdato på vaktflatene i v1. Visning av sluttdato for nattevakter utsettes til én samlet UX-endring på alle relevante flater i v2. AV-02s klokkeslett og faktisk varighet etter KS-03 endres ikke.» |
| Eksakte versjonslåser | Viderefør dagens eksakte låser, og oppdater kontrollert med tester på støttede versjoner. Det gjør oppsettet reproduserbart, men krever aktivt vedlikehold ved versjonsdrift. Ingen nye gamle versjonstall kopieres inn som varig fasit. | «Gruppa viderefører eksakte avhengighetslåser i sporede manifest-/lås-/requirements-filer. Oppdateringer gjøres som vanlig vedlikehold med relevante tester og bygg på støttede minsteversjoner og CI-versjoner.» |
| Story 5.9 | Dokumenter utsettelse til etter v1-innlevering, og prioriter 5.4–5.8, ekstern P-13 og leveringskontroll. Kjerneflyten beholder faste preferanser. Ved senere redigering må A–B–A, ugyldiggjøring og ny rangering testes. | «Gruppa utsetter story 5.9 (P-10B) til etter v1-innleveringen. Faste preferanser i seeddata er v1-omfang. P-10B er ikke forkastet; teksten, tilgangskontroll, ugyldiggjøring, A–B–A og ny rangering leveres samlet senere.» |
| Sensornøkkel, ansvar og kreditt | Bruk en egen sensornøkkel med avgrenset forbruk og én navngitt eier; beløpet fastsettes fra målt bruk ved innleveringsversjonen. En konkret innbetaling kan ikke anbefales fra testene her, som brukte falsk transport. Gruppa må oppgi eier, betaler og beløp før punktet kan lukkes. | «Gruppa velger en egen sensornøkkel for live-kjøring i 5.8. Nøkkeleier: [navn]. Betalingsansvarlig: [navn/fordeling]. Før levering måles kostnad for én full sensorøkt på innleveringsversjonen. Tilgjengelig kreditt: [beløp/valuta], valgt for [antall] slike økter med [margin]. Forbrukstak og prøvekjøring dokumenteres uten nøkkelverdien i repoet. Nøkkelen deles sikkert med sensor.» |

For sensoropplegget må målingen ta med preferansetolkning fra en ren database,
forklaringer, planlagt antall sensorøkter og eventuelle nye forsøk. Manglende
forbrukstall er ukjent kostnad, ikke null. Se [testveiledningen](../modelltest-openrouter.md)
og AV-16/ÅB-8 i [referatet](avklaringspunkter.md#13-målbare-prd-mål-og-beslutningseiere-2026-11-13).

## Svar

Avventer gruppas samlede svar. Ingen av de fire punktene lukkes bare fordi
vedtakstekst er foreslått.
