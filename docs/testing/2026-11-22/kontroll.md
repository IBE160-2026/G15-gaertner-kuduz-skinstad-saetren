# Kontroll av åpne punkter 22. november 2026

## Miljø og avgrensning

Utført av Codex på oppdrag fra Kim, med Chrome 158.0.8127.36 på Windows 11 via
Playwright MCP. Vanlig Chrome med innstillingssiden `chrome://settings/appearance`,
100 % sidezoom og et faktisk loddrett rullefelt på 15 px. Browser-CDP identifiserte
nettleserprosessen som PID 44384; prosesskontrollen viste `Headless=false` for
nettopp denne prosessen (en annen, separat Chrome-prosess var headless).
Ingen CSS-rettinger i denne
økten. Grunnlaget er `main` ved `3239e881a5a1422f94dc752f2fc868d325bbe365`, inkludert
endelig 4.6-CSS og 5.3-panelet. Testtillegget er lagret i `10706fa`.

Frontend er startet med Vite mot FastAPI på localhost. Databasen er en separat fil
`g15-aapne-punkter-20261122.db` i TEMP, med standard seeddata; den vanlige
`backend/turnushjelperen.db` er ikke endret. `KI_MODUS=demo` slår av live-kall i dagens
app; faktisk demoadapter er ennå ikke levert. Ingen nøkkel er lest eller brukt.

## Godkjenning, kontrast og fokus (3.2, OP-16)

Kandidatkortet for Ingrid ble kontrollert mot ekte backend. For å fremkalle begge
varselmerkene ble bare #4102 i testdatabasen forlenget fra 15:00 til 15:24. Det gir
32:24 i startuka, ordinær del 3:36 og overtid 4:24 for den vurderte vakten, og
kostnad 3 927,00 kr. Etter kontrollene ble standard seeddata gjenopprettet; #4102
slutter igjen 15:00. Totalscore 79,8 i enkelte bilder er fra det endrede
min–maks-grunnlaget, ikke den uendrede #4127-fasiten på 79,4.

Fargeparene ble hentet fra beregnet CSS og faktisk bakgrunn gjennom foreldrene;
kontrast ble regnet med relativ sRGB-luminans. Dette er en målrettet kontroll av
godkjenningsflyten, ikke en full tilgjengelighetsrevisjon.

| Tekst / bakgrunn | Kontrast |
| --- | ---: |
| Hovedtekst / hvitt panel | 15,17:1 |
| Sekundærtekst / hvitt panel | 5,48:1 |
| Sekundærtekst / appbakgrunn | 4,84:1 |
| Varseltekst / hvitt panel | 5,28:1 |
| Varseltekst / avviksnotat | 5,00:1 |
| Reservelinje / avveiningspanel | 5,05:1 |
| «Trekker opp» / avveiningspanel | 4,89:1 |
| «Trekker ned» / avveiningspanel | 7,54:1 |
| Hvit tekst / godkjenningsknapp | 13,21:1 |

Tab ga synlig 2 px fokusramme på Logg ut, Avbryt og Godkjenn erstatning.
[Fokus på godkjenning](godkjenning-fokus.png).

Mens Ingrids godkjenningsflate var åpen, ble Jonas godkjent gjennom et separat
autentisert API-kall med hans aktuelle grunnlagsmerke. Enter på den allerede åpne
flaten viste «Vakten er allerede bemannet». «Til Vaktvalg» fikk fokus automatisk,
`:focus-visible=true` og 2 px ramme i `accent`. Enter gikk tilbake til Vaktvalg.
Hovedtekst og returknapp bruker hovedtekst på hvitt panel (15,17:1).
[Faktisk allerede-bemannet-tilstand og fokus](allerede-bemannet-fokus.png).

**Resultat:** De to restpunktene i Kims 3.2-punkt er oppfylt.

## Vaktvalg: tomtilstand og feil / nytt forsøk

Eksisterende `vaktvalg.test.tsx` dekker 500 → «Prøv igjen» → oppdatert oversikt,
og tom liste over vakter som krever handling etter godkjenning. OP-16 krever ikke
en identisk manuell funksjonskontroll. Testen bekrefter ikke layout; den dekker
heller ikke visuelt begge tomme seksjoner samtidig.

Ved 680 × 700 px ble API-svaret fra den virkelige oversikten kopiert og begge
lister satt tomme med nettleserens rutestubb. Begge panelene hadde full, lesbar tekst:
«Ingen vakter krever handling nå» og «Ingen bemannede vakter i perioden». Ingen
feilaktige valgknapper eller siderulling. [Tomtilstanden](vaktvalg-tom.png).

En kontrollert HTTP 500 ga serverfeiltekst og «Prøv igjen», med synlig 2 px
tastaturfokus. Etter at feilinnsprøytingen ble fjernet, hentet Enter ekte backend
på nytt og viste begge vaktene som krever handling. [Feil og fokus](vaktvalg-feil-fokus.png).
Feil og tomtilstand er visuelt ulike. Feil-/tomsvarene var kontrollerte testsvar,
mens innlogging, normalt svar og nytt forsøk brukte ekte backend.

**Resultat:** Det gamle nettleserpunktet for Vaktvalg kan lukkes med kombinasjonen
av komponenttester og disse visuelle bevisene.

## Raden med begge varsler (4.2/4.3) og endelig 4.6-CSS

Kontrollhøyde 700 px. Tabellen ruller i egen beholder; siden ruller ikke vannrett.
Begge merker er tekst og trekantikon i `warn`, og er aldri bare farge.

| Vindusbredde | Innholdsbredde med rullefelt | Tabell ved 16 px: synlig / total bredde | Tabell ved 20 px: synlig / total bredde |
| ---: | ---: | ---: | ---: |
| 680 | 665 | 573 / 980 | 573 / 1167 |
| 960 | 945 | 853 / 980 | 853 / 1167 |
| 1080 | 1065 | 973 / 980 | 973 / 1167 |
| 1600 | 1585 | 1088 / 1088 | 1088 / 1167 |

Ved hver bredde ble Ingrids rad undersøkt i normal og større tekst, og valgt med
Tab og Enter. Fokusrekkefølgen var Logg ut → tabellregion → Velg / begrunnelse per
kandidat → Velg Ingrid. Alle fikk synlig 2 px fokusramme. Godkjenningsflaten beholdt
valgt Ingrid, begge merker, kandidatkort og avviksnotat uten siderulling.

Først ble 20 px satt på rot-elementet for sammenlignbare målinger. Deretter ble
**den faktiske Chrome-innstillingen «Stor» valgt**, siden lastet på nytt og alle fire
bredder kontrollert igjen: beregnet grunnskrift 20 px og sidebredde lik innholdsbredde
i alle tilfeller. «Middels» og 100 % zoom ble gjenopprettet før P-13.

Bildeserier (filnavnet inneholder bredde og skriftstørrelse):

- [Begge varsler, 1600 px normal](begge-varsler-1600-16.png),
  [680 px normal](begge-varsler-680-16.png),
  [680 px normal rullet mot høyre](begge-varsler-hoyre-680-16.png).
- [Faktisk Chrome «Stor», 680](begge-varsler-chrome-stor-680.png),
  [960](begge-varsler-chrome-stor-960.png),
  [1080](begge-varsler-chrome-stor-1080.png),
  [1600](begge-varsler-chrome-stor-1600.png).
- [Godkjenning med større tekst, 680](godkjenning-680-20.png),
  [960](godkjenning-960-20.png), [1080](godkjenning-1080-20.png),
  [1600](godkjenning-1600-20.png).

Ved 680 px og normal tekst er de faste kolonnene 68 + 120 px. Etter maksimal
høyreskrolling slutter kandidatkolonnen ved x=234, mens ulempekolonnen starter ved
x=251,66: **17,66 px klaring** med endelig CSS og uendrede seeddata.
[Endelig 4.6-kontroll med rullefelt](4-6-endelig-680-hoyre.png).

Ved 20 px er de faste kolonnene 85 + 150 px. Ulempekolonnen må rulles fram før
man når maksimal høyreskrolling ved 680 px; det er samme dokumenterte begrensning
som i 4.6-kontrollen 19.11, ikke et nytt tap av innhold. Også ved 1600 px trenger
tabellen litt rulling med større tekst. Ingen uopprettelig tekstklipping eller
overlapp på godkjenningsflaten ble funnet. Deler av vanlige tabellceller skjules
under de faste kolonnene mens man ruller, og kan rulles tilbake i syne.

**Menneskelig designvalg:** Kim fikk vist [totalscoren over to linjer](totalscore-to-linjer.png)
gjennom `bmad-walkthrough` [WT] og svarte 22.11: «totalscore på to linjer er ok».
Det er et konkret valg av linjebrytingen, ikke et resultat fra forståelsestesten.

**Statusvurdering:** De gjenstående 4.6-punktene om endelig CSS / rullefelt og
tolinjers totalscore er oppfylt. Story 4.6 kan settes `done`. P-13 er eksplisitt
utenfor storien etter Johannes' beslutning 19.11 og holdes åpen etter Kims nye
krav om også å teste med en person utenfor gruppen. Ingen gjentakbar layouttest
i CI er lagt til; dette er fortsatt utsatt arbeid.

## P-06/P-08, språk og eksisterende 5.4

[Testtillegg og uavhengig gjennomgang](../../../_bmad-output/implementation-artifacts/spec-p-08-fem-periodekantvakter.md)
dekker alle fem faktiske #4261–#4265 i isolerte databaser: ny vurdering,
godkjenningsgrunnlag og POST, både uriktig og korrekt grunnlagsmerke, eksakt
datagrense og uendret database. 219 relevante backendtester og 54 eksisterende
komponenttester bestod. #4127/#4189-fasit og KS-04-avgrensningen er bevart.
[UI-datafeilen for #4261](p13-visning-b.png) er fra ekte backend med vakten markert
som ubemannet uten flytting av tidene.

Alle de 40 [tillatte norske påstandene for #4127](paastander.md) er lest: navn,
myk faktor, egen total og referanse stemmer med beregnede fakta. Jonas/Mette har
samme kostnads- og timepoeng; ulempe 86,7 mot 40,0 forklarer forskjellen.
Thomas har høyere kostnadspoeng enn Jonas, men lavere total. «Lavere kostnadspoeng»
betyr ikke lavere kroner; teksten bruker nettopp poeng for å unngå den motsigelsen.
Ingen språk- eller faktafeil ble funnet i uttrekket. Dette er agentens språkkontroll,
ikke en brukertest eller en uavhengig beregningsfasit.

Reservelinjen og de fire nøkkeltallene ble lest på begge flater i nettleseren.
De beholdt korrekt kandidat og grunnlag ved KI utilgjengelig. Eksisterende tester
bruker falsk transport for feil referanse, identitet, retning og likhet før avrunding.

Story 5.4 er allerede implementert i branch `story/5-4-reservetekst-naar-ki-forklaringen-feiler`.
[PR #37](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/37)
var **OPEN**, ikke draft, ved kontrollen 22.11, med head
`be59221db2549e2fad3daf2839a0d82f2797cfa3` og alle rapporterte CI-kontroller grønne.
Branchens ekstra reservetekst er god norsk og viser til nøkkeltall fremfor å
oppfinne en forklaring. Tidligere nettleser-/testbevis er i branchens KI-logg fra
21.11. Denne økten har ikke kjørt branchens kode på nytt eller merget PR-en.
**P-08 er fullført; samlepunktet P-06/P-08 holdes åpent bare for behandlingen og
integrasjonskontrollen av endelig 5.4-reservetekst.**

## Intern P-13-prøve og etterfølgende retting

Den faktiske prøven med Kim avdekket at overskriften «Gyldige kandidater» ved
datafeil kunne gi inntrykk av at gyldighet var kjent. Overskriften er nå
«Kandidatvurdering», og teksten forklarer både usikkerheten og nødvendig
kontroll/oppdatering av grunnlaget før ny vurdering. Den vedtatte innleieteksten
ved null gyldige er flyttet foran utelukkelsesboksen og vises som brødtekst.
Regler, datagrense og tilgjengelige handlinger er uendret.

[Prøve med ordrette svar og før-/etter-bilder](p13-protokoll.md) ·
[KI-logg, to røde tester og uavhengig gjennomgang](../../ki-logg/2026-11-22-p-13-datafeil-og-neste-steg.md).
Etter siste retting bestod frontendbygg og 52 modultester + 57 komponenttester.
Visuell etterkontroll med ekte backend ved 680/1600 px og 16/20 px grunnskrift
fant ingen siderulling eller tekstoverlapp. Dette er en ny tekstendring etter
kontrollene ovenfor, ikke en endring av CSS-en som lukket 4.6.

P-13 og behovsvalidering er åpne. Kim har ingen turnuserfaring, og den siste
neste-steg-setningen har ennå ingen prøve uten hint. Ekstern prøve og gruppas
endelige designvurdering gjenstår.
