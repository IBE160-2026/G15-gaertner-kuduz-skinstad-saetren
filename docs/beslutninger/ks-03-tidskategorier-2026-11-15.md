# KS-03: kontroll av tidskategorier for fire vakttyper

Kontroll utført 2026-11-15 før implementasjon av story 4.7. Kildene er
beslutningsreferatet KS-03, AV-02, AV-09 og AV-11, PRD §4.3–4.4 og
`epics.md` story 4.7. Dette er en kontroll av vedtatt modell, ikke en ny
beslutning. Helligdager følger ukedagen. Intervallene er halvåpne.

For hver faktisk forløpt time gjelder høyeste sats: natt 22–06 = 3,
helg lørdag 00–mandag 00 og kl. 06–22 = 2, hverdagskveld 18–22 = 1,
resterende hverdag 06–18 = 0. Ved natt/helg-overlapp gjelder natt.

## Ordinære åttetimersvakter uten sommertidsskifte

Tallene i tabellen er faktisk forløpte timer i kategoriene dag / kveld /
helg / natt, fulgt av ulempepoeng. Datoen er **startdag** for vakten.

| Vakt | Mandag–torsdag | Fredag | Lørdag | Søndag |
| --- | --- | --- | --- | --- |
| Dag 07–15 | 8 / 0 / 0 / 0 = 0 | 8 / 0 / 0 / 0 = 0 | 0 / 0 / 8 / 0 = 16 | 0 / 0 / 8 / 0 = 16 |
| Mellom 10–18 | 8 / 0 / 0 / 0 = 0 | 8 / 0 / 0 / 0 = 0 | 0 / 0 / 8 / 0 = 16 | 0 / 0 / 8 / 0 = 16 |
| Kveld 15–23 | 3 / 4 / 0 / 1 = 7 | 3 / 4 / 0 / 1 = 7 | 0 / 0 / 7 / 1 = 17 | 0 / 0 / 7 / 1 = 17 |
| Natt 23–07 | 1 / 0 / 0 / 7 = 21 | 0 / 0 / 1 / 7 = 23 | 0 / 0 / 1 / 7 = 23 | 1 / 0 / 0 / 7 = 21 |

Fredag 23–lørdag 07 er natt til 06 og helg 06–07. Søndag
23–mandag 07 er natt til 06 og hverdag 06–07. Lørdag 05–07 gir
1 natttime og 1 helgetime, altså 5 poeng. Fredag kveld 15–23 gir
3 dagtimer, 4 kveldstimer og 1 nattetime, altså 7 poeng. Lørdag kveld
15–23 gir 7 helgetimer og 1 nattetime, altså 17 poeng. Dette kontrollerer
særlig grensene 06, 18, 22 og ukeskiftene.

## Faktiske tidspunkter ved sommertid

Europe/Oslo går frem fra 02:00 til 03:00 søndag 2026-03-29. Vakten
lørdag 2026-03-28 23:00 CET–søndag 2026-03-29 07:00 CEST er
22:00 UTC–05:00 UTC: **7 faktisk forløpte timer**. Natt 23–06 er
6 timer og helg 06–07 er 1 time: **20 poeng**.

Europe/Oslo går tilbake fra 03:00 CEST til 02:00 CET søndag 2026-10-25.
Vakten lørdag 2026-10-24 23:00 CEST–søndag 2026-10-25 07:00 CET er
21:00 UTC–06:00 UTC: **9 faktisk forløpte timer**. Natt 23–06 er
8 timer, inkludert begge forekomstene av 02–03, og helg 06–07 er
1 time: **26 poeng**.

Målevinduet beregnes i UTC som `[vaktstart − 672 timer, vaktstart)`.
En historisk vakt klippes til dette intervallet før kategorisering;
vurdert vakt bidrar ikke. Lokal klokketid alene kan ikke brukes til
å trekke 28 døgn eller måle varighet over de to overgangene (AV-09).

## Resultat og avgrensning

Vedtatte kilder gir samme kategorier og poengsatser for alle fire
vakttyper; ingen motstrid ble funnet. Tabellen og sommertidseksemplene
er regnet fra tidsintervallene og UTC-tidspunktene, uavhengig av
programresultat. Kontroll av faktisk kode og testutfall kommer i story
4.7. KS-02 gjelder fortsatt enhver ny rangeringsfasit; denne kontrollen
godkjenner ingen totalscore eller rangering.
