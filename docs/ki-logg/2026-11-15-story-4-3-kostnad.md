# KI-logg: story 4.3 – forenklet kostnad

## Oppgave og prompt
Brukeren ba: «bmad-build story 4.3. Opprett egen branch og push til Github med en gang slik at mine medelever ser at jeg har startet arbeidet». Brukeren ba deretter om storynavnet i branchen og sletting av den første branchen, og opplyste at Ragnhild utvikler 4.2 samtidig.

## Leveranse og vurdering
Codex med GPT-6 og underagenter undersøkte plan, kode og kandidatsvar og implementerte modellert merkostnad etter P-01–P-03: individuell lønn, faktisk tid fordelt på Oslo-uker, 36 timer ordinært og 150 % utover. Beregningen er deterministisk. API-et leverer total og fordeling til kandidat- og godkjenningsgrunnlaget. Visningen skiller ordinær tid og overtid.

Uavhengige gjennomganger identifiserte at endret kostnad ikke var synlig på godkjenningsflaten, at lønnsvalideringen tillot ugyldige verdier, at avrundede timer kunne gi misvisende detaljer og at flere tester manglet. Koden ble rettet: kostnad vises også ved ny bekreftelse, lønn valideres mot lagringskontrakten og varighet vises som timer:minutter, med «ca.» ved avrunding. Fasit for blandet kostnad, status per rad og sommertid over grensen ble lagt til.

## Kvalitetssikring
493 backendtester bestod. Frontendbygget, 50 modultester og 29 komponenttester bestod. En bevisst feil som alltid viste «Ordinær» gjorde komponenttesten rød med manglende «Inkluderer overtid»; etter tilbakeføring bestod alle 13 testene i filen. Under implementeringen ble timehjelperen rettet etter en feilet test. Én full backendkjøring traff en test under samtidig redigering og feilet; testen bestod etterpå, og en ny full kjøring bestod.

Playwright mot ekte backend og en egen midlertidig testdatabase viste #4127s fasit (Ingrid 3 850 kr, Jonas/Mette 2 960 kr, Thomas 2 800 kr), samme Ingrid-kostnad på godkjenningsflaten og tomtilstanden for #4189. Skjermbilder ved 680, 960, 1080 og 1600 px ble kontrollert for #4127. Se spesifikasjonen for gjenstående manuelle kontroller og gjennomgangsresultater.
