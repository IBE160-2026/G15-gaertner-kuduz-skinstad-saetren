# Uavhengig regneeksempel for KS-02 og AV-12

Kontrollert mot PRD §4.3–4.4 og story 4.7 før sammenligning med kode.
Dette er et faktor- og differanseeksempel, ikke en ny godkjent fasit for
hele rangeringen. Kandidatene forutsettes gyldige og har lik kostnad,
timebelastning og preferansescore.

Med tak 300 gir 40 ulempepoeng `100 × (1 − 40/300) = 86⅔` i
ulempescore. 180 ulempepoeng gir `100 × (1 − 180/300) = 40`.
Forskjellen er `46⅔ × 0,15 = 7` totalpoeng i favør av kandidaten med
40 ulempepoeng. Ingen avrunding inngår i mellomregningen. Ved poeng på
eller over 300 er scoren 0. Rangering og de øvrige faktorene implementeres
separat i story 4.4; dette eksemplet endrer ikke godkjent #4127-fasit.

De eksisterende seeddataenes AV-12-scenario bruker Jonas Bakke og Mette
Solberg for #4127: begge har timelønn 370, 16 timer i startuken og
preferansepoeng 75, mens historikken gir henholdsvis 40 og 180 poeng.
Kontrollen av at de faktisk er gyldige og at den nye domeneberegningen
gir disse verdiene må utføres i test; selve mellomregningen over er ikke
utledet fra programresultatet.

Målevinduets start kan også kontrolleres direkte i UTC, uavhengig av
lokal veggklokke: 10.04.2026 kl. 12 CEST er 10 UTC, og 672 timer tidligere
er 13.03 kl. 10 UTC, det vil si **11 CET**. 10.11.2026 kl. 12 CET er
11 UTC, og 672 timer tidligere er 13.10 kl. 11 UTC, det vil si **13 CEST**.
Begge vinduene er halvåpne og slutter ved vaktstart.
