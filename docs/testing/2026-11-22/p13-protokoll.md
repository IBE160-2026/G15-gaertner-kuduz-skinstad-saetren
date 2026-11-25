# P-13 og lokal problemvalidering

## Ramme

Forberedt 22.11.2026. Én person løser tre oppgaver uten hint på én datamaskin.
Bruk samme versjon og datagrunnlag som i [kontrollrapporten](kontroll.md), Chrome
på Windows, 1600 × 1000 px og standard skriftstørrelse. Testleder registrerer
svar ordrett før vurdering. Ingen ekte person- eller pasientdata skal samles inn.

Kim ba uttrykkelig 22.11: «jeg vil ta testen nå, men den skal også senere taes av
en som er utenfor gruppen så det kan sees med nye øyne. Dette punktet skal derfor
ikke loggføres som ferdig selv om jeg tar testen». Intern prøve og senere ekstern
prøve skal holdes atskilt. P-13 forblir åpen etter den interne prøven.

## Oppgaver til deltakeren

1. I kandidatvisningen: Hvorfor står kandidaten på plass 1 øverst? Forklar med egne ord.
2. Finn en annen kandidat du mener kan velges. Oppgi navn og vis eller beskriv hvordan du velger personen.
3. Se visning A og B: Hva sier hver visning, og hva ville du gjort videre i hver situasjon?

Testleder viser først [kandidatvisningen](p13-kandidater.png) eller tilsvarende
aktive app. Først etter svar 1/2 vises [A](p13-visning-a.png) og
[B](p13-visning-b.png). Det gis ingen forklaring av rangering, knapper eller
feiltilstand før svarene er registrert. Noter om deltakeren brukte bilde eller
appen; et beskrevet valg er forståelsesbevis, ikke en observert knapphandling.

## Intern prøve — gjennomført med oppfølging

- Deltaker: Kim, gruppemedlem. På spørsmål om egen erfaring med å finne erstatter til en vakt svarte han: «Det har jeg ikke erfaring med».
- Testflate: forsøkt gjennom app/innlogging, deretter A/B som direkte PNG-bilder generert fra Chrome på Windows ved 1600 × 1000 px. Direkte knappbruk hos deltakeren er ikke observert; valg av Mette ble beskrevet med ord.
- Oppgave 1, ordrett: «Fordi den har lavest ulempepoeng av kandidatene».
- Oppgave 2, ordrett: «Mette Solberg. Klikke på velg knappen og godkjenn erstatter kappen på neste side».
- Oppgave 3: Presentert, men første forsøk viste innlogging i begge lenker fordi deltakerens Chrome hadde en egen sesjon. Ordrett: «A og B er like. Det er innlogging så jeg ville lagt inn brukernavn og passord og trykket logg inn». Dette er et tilgangsproblem i testopplegget og skåres ikke som feil forståelse av kandidattilstandene. Testtilgang er gitt, og nytt svar avventes uten hint om innholdet.
- Etter innlogging svarte Kim: «Begge er like. Jeg ville klikket inn på velg vakt - finn erstatter». Deltakeren hadde fremdeles ikke fått bekreftet tilgang til de to tilstandene; heller ikke dette skåres som feil på oppgaven. Ingen årsak i appen er fastslått. For å fjerne leveringsproblemet ble de lagrede A/B-bildene servert direkte som PNG fra en egen, lokal HTTP-server på port 8765. Begge lenker ble verifisert med HTTP 200 og `image/png` før deltakeren fikk dem. Endelig svar avventes.
- Oppgave 3 etter riktig bildelevering, ordrett: «Den ene har ingen gyldige kandidater, veit ikke hva jeg skulle gjort. den andre har gyldige kandidater, men gyldig turnus finnes ikke så får ikke valgt noen men ville gjort det om det var tilgjengelig».
- Observasjon: Kim skiller null treff fra en datamangel, men tolker B som at gyldige kandidater finnes. Det kan appen ikke vite når vurderingen er stoppet. Overskriften «Gyldige kandidater» over datafeilen er en mulig årsak. I A ble rådet om innleie ikke brukt som neste steg. Testleder forklarte deretter forskjellen. En senere kontroll med Kim må derfor merkes som prøve etter forklaring, ikke som en ny prøve uten hint.
- Misforståelse: B ble oppfattet som at gyldige kandidater allerede var kjent. Testleder vurderte overskriften som misvisende i datafeiltilstanden. I A ble innleierådet ikke funnet som neste steg.

## Rettelse og intern oppfølging etter forklaring

Med `bmad-build` og egen kontekst-/gjennomgangsagent ble datafeiloverskriften
endret til «Kandidatvurdering». Meldingen presiserer nå at appen ikke kan avgjøre
hvem som er gyldig. Den vedtatte innleieteksten er flyttet foran utelukkelsesboksen
og vises som brødtekst fremfor metatekst. Ingen ny knapp eller endring av regler.

- Før: [A](p13-visning-a.png) og [B](p13-visning-b.png).
- Etter: [A ved 1600 px](p13-etter-a-1600-16.png) og [B ved 1600 px](p13-etter-b-1600-16.png).
- Smalt vindu og større tekst: [A ved 680 px / 20 px](p13-etter-a-680-20.png),
  [B ved 680 px / 20 px](p13-etter-b-680-20.png). Ekte backend, ingen siderulling
  eller tekstoverlapp, full datagrense og ingen valg ved datafeil.
- To utvidede tester feilet før rettingen. Etterpå bestod bygg, 52 modultester
  og 57 komponenttester. Etter blind gjennomgang bestod bygg og de 27 kandidatflatetestene
  igjen, med sikring av typografi, tekstorden og tilstandsavhengig overskrift.

Kims vurdering av A, ordrett: «A: mer forståelig, men jeg ville kanskje sagt
\"Innleie av personell burde vurderes\"». Den nye plasseringen beholdes.
Forslaget om «burde» er vurdert, men ikke innført: P-11 vedtok «kan vurderes»,
og prototypen kjenner ikke situasjonen godt nok til å anbefale at innleie burde skje.
Dette er testleders begrunnelse; ingen ny samlet gruppeavstemning om ordlyden er utført.
B-oppfølgingen, ordrett: «Kandidater kan ikke vurderes fordi det ikke er noen
gydig turnus. Da stopper det seg for meg». Kim oppfatter nå stopp i selve vurderingen,
og hevder ikke lenger at gyldige kandidater er kjent. Videre fremgang er fortsatt
uklar. Testleder presiserte at datagrunnlaget må kontrolleres utenfor denne visningen,
og la til neste-steg-setningen «Få turnusgrunnlaget kontrollert og oppdatert før ny
vurdering.» Den siste setningen er teknisk og visuelt kontrollert, men er ikke
prøvd uten hint med en deltaker. Ingen ny redigerings-/importfunksjon er innført.
Den interne prøven er ikke godkjent som en ny prøve uten hint.
Det er ikke dokumentert at alle tre oppgavene ble løst uten hint i første prøve.

Endelig B etter siste neste-steg-setning: [1600 px / 16 px](p13-endelig-b-1600-16.png)
og [680 px / 20 px](p13-endelig-b-680-20.png). Mellomversjonen Kim svarte på er
bevart i `p13-etter-b-*.png`; den er ikke overskrevet med den siste teksten.

## Behovssamtale etter oppgavene

Be om konkrete erfaringer, ikke bare om løsningen virker nyttig:

- Har deltakeren selv eller gjennom arbeid observert en vakt som måtte dekkes på kort varsel? Beskriv siste tilfelle uten personopplysninger.
- Hvordan ble erstatter funnet, hvilke opplysninger ble kontrollert og hva tok tid?
- Hvilken avgjørelse ville visningen hjulpet med, og hva måtte fortsatt kontrolleres utenfor appen?
- Hva mangler før verktøyet kunne vært prøvd i den faktiske arbeidsmåten?

Skill opplevd problem fra antatt nytte. Hvis deltakeren mangler turnuserfaring,
gir testen forståelsesbevis, men svakt grunnlag for å hevde validert brukerbehov.

Kim har ikke slik erfaring. Det er derfor ikke dokumentert noe konkret turnustilfelle,
tidsbruk eller behovsbevis gjennom denne prøven. Problemvalidering står åpen og bør
kombineres med den eksterne prøven med en person som har relevant erfaring.

### MJ, 25.11.2026

Samtalen ble tatt etter oppgavene. Dette er Ragnhilds referat, ikke ordrette svar.

**Opplevd problem (egen erfaring).** MJ jobber selv med turnus og med vakter som må
dekkes på kort varsel. Slik gjøres det i dag: Den som hadde vakten, legges inn med
fravær. Deretter går man gjennom vaktlisten manuelt for å se om noen kan fristilles fra
andre oppgaver og dekke vakten. Må det leies inn, går man inn i vaktlisten til den
innleide for å kontrollere at ingen regler brytes og at det ikke blir overtid, før
vakten bemannes.

**Antatt nytte (MJs vurdering av prototypen).**

- Appen gjør at man slipper å kontrollere kolliderende vakter og regelbrudd ved å gå
  inn på hver enkelt kandidat.
- Preferansene er «veldig nyttig», fordi man da vet hvem man har størst mulighet til å
  lykkes med.
- Slik MJ jobber i dag, ville ingenting måtte kontrolleres utenfor appen.
- Verktøyet er en hjelper. Turnusansvarlig tar valget selv.

**Hva som mangler før bruk.** Alle lover og regler og hele tariffavtalen til MJs
arbeidsgiver må være lagt inn, og appen må kunne bemanne direkte i
bemanningssystemet. Med det på plass ville ingenting mangle. Forbedringsforslag:
telefonnummer til kandidatene i appen, så det ikke må slås opp et annet sted.

**Vurdering.** MJ beskriver et konkret, gjentakende arbeidsforløp med manuell kontroll
av vaktlister. Det støtter problemet produktbriefen bygger på: å kontrollere regler og
kollisjoner per kandidat tar tid. Det er én persons erfaring, uten målt tidsbruk, og er
derfor et lokalt signal, ikke et validert behov. Utsagnet om at ingenting må
kontrolleres utenfor appen gjelder MJs arbeidsmåte. Prototypen har bare fire harde
regler og ikke tariffavtalen (se addendum og PRD). Telefonnummer og integrasjon mot
bemanningssystemet er utenfor v1. De er notert her som innspill og er ikke vurdert av
gruppa.

## Ekstern prøve — gjennomført 25.11.2026

Samme tre oppgaver uten hint, med én person utenfor gruppen. Registrer initialer,
rolle/erfaring, dato, OS, skjermflate og versjon. Bevar ordrette svar, eventuelle
misforståelser og vurdert designendring. Ved feil på en oppgave: rett årsaken,
bevar før/etter-bilder og prøv igjen. En ny prøve etter hint må merkes som slik.
P-13 lukkes først når kriteriene er oppfylt og gruppas designvurdering er dokumentert.

- Deltaker: MJ, ressursplanlegger, utenfor gruppa, med erfaring med turnus.
- Testleder: Ragnhild.
- Testflate: appen selv, ikke bilder. Safari på macOS, fullskjerm, standard
  skriftstørrelse. Versjon `1d99798` i demo-modus (`KI_MODUS=demo`, ingen nettverkskall)
  mot en egen testdatabase med standard testdata. #4261 var markert som ubemannet uten
  flytting av tidene, som i [kontrollrapporten](kontroll.md). Avvik fra rammen over:
  Safari på macOS i stedet for Chrome på Windows. Avgrensningen krever bare ett
  operativsystem og én skjermflate. Kandidatvisningen hadde KI-avveiningen fra
  story 5.3–5.7, som ikke fantes i [bildet fra 22.11](p13-kandidater.png).
- Vakter: #4127 (fire gyldige) til oppgave 1 og 2, #4189 (null gyldige) som A og
  #4261 (datafeil) som B.
- Oppgave 1, ordrett: «Kandidaten står øverst fordi den har minst ulempe, kostanden
  ikke vesentlig høyere enn andre, har færre ulempevakter, færre timer per uke og kan
  ta på seg ekstravakter ved behov.»
- Oppgave 2, ordrett: «Hadde valgt Mette fordi hun er nummer to på listen fordi jeg
  stoler på systemet har satt opp listen rett.» Testleder observerte at MJ klikket
  «Velg» og bemannet vakten, og at det ikke var vanskelig.
- Oppgave 3, A ordrett: «Vakt 4189 viser at det er ingen aktuelle kandidater. Den
  utvidede listen viser at Thomas Nygård har kolliderende vakt og da ville jeg først
  ha sjekket om noen kunne ha erstattet han slik at han kunne tatt denne vakten. Om
  ikke, så ville jeg ha leid inn personell.»
- Oppgave 3, B ordrett: «Vakt 4261 viser manglende datagrunnlag. Teksten "kan ikke
  beregne kandidater fordi nødvendig turnusgrunnlag mangler. Vi kan derfor ikke
  avgjøre hvem som er gyldig for vakte. Få turnusgrunnlaget kontrollert og oppdatert
  før ny vurdering" gir ikke mye mening for meg. Dersom turnusgrunnlaget mangler,
  hvordan har da den tomme vakten oppstått? Hva er det som ikke er rett i turnusen?»

### Vurdering

Testleder og agent har vurdert svarene mot akseptmålet. Dette er ikke gruppas
designvurdering.

- Oppgave 1 er løst. Begrunnelsen bruker de samme faktorene som rangeringen.
  «Kan ta ekstravakter» er hentet fra preferansen og avveiningen.
- Oppgave 2 er løst. Mette Solberg er gyldig og nr. 2, og valget ble gjort i appen.
- Oppgave 3 er løst. MJ skiller null gyldige (A) fra datafeil (B) og finner innleie
  som neste steg i A. Det var dette Kim ikke fant 22.11. MJ åpnet Ekskludert-boksen
  uten hint og leste utelukkelsen av Thomas riktig: han er utelukket for kolliderende
  vakt i #4189 (kontrollert mot API-et).
- Funn i B: MJ forstod at vurderingen stoppet, men ikke hva som er galt eller hva som
  bør gjøres. Neste-steg-setningen fra 22.11 er dermed prøvd uten hint for første gang,
  og den virket ikke. Årsaken er at teksten ikke sier hva appen trenger.

### Rettelse etter ekstern prøve

Frontend får ikke vite hvorfor vurderingen stopper. P-08 gir samme datafeil for flere
årsaker: turnusen slutter for tidlig, går ikke langt nok tilbake, ugyldige vakttider,
feil i kandidatenes vakter og ugyldig timelønn
([vurdering.py](../../../backend/domene/regelmotor/vurdering.py)). En tekst som bare
nevner slutten av perioden ville vært feil i de andre tilfellene. Ragnhild vurderte to
løsninger og valgte en generell tekst i frontend fremfor en årsakskategori fra
backend, som ville endret API-kontrakten (AD-4).

- Før: «Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler. Vi kan
  derfor ikke avgjøre hvem som er gyldig for vakten. Få turnusgrunnlaget kontrollert
  og oppdatert før ny vurdering.» Bilde: [B ved 1600 px](p13-endelig-b-1600-16.png)
  (Chrome, samme tekst som MJ så).
- Etter: «Kandidatene kan ikke vurderes fordi turnusgrunnlaget rundt vakten mangler
  eller har feil, så appen kan ikke avgjøre hvem som er gyldig. For å kontrollere
  hviletid, ukentlig fri og arbeidstid må appen kjenne vaktene i ukene før og dagene
  etter vakten. Kontroller at turnusen for dagene rundt vakten er lagt inn og riktig,
  og vurder vakten på nytt.»
- Datagrenselinjen («Turnusgrunnlaget går til …») er uendret.
- Bare kandidatflaten er endret. Datafeilteksten på godkjenningsflaten er ikke prøvd
  og står uendret.
- Den nye teksten er ikke prøvd med deltaker.

Skjermbilder tatt av Ragnhild i Safari på macOS (fullskjerm) 25.11, etter prøven og mot
samme testdatabase. Bildene er utsnitt av kandidatdelen, ikke hele vinduet:

- [Kandidatvisningen for #4127](../2026-11-25/p13-ekstern-kandidater.png), med
  avveiningen for Jonas Bakke åpen. Rangeringen er den samme som MJ så.
- [A, #4189](../2026-11-25/p13-ekstern-a.png), med Ekskludert-boksen åpen, slik MJ så den.
- [B etter rettingen, #4261](../2026-11-25/p13-ekstern-b-etter.png). Teksten brytes over
  tre linjer uten overlapp, og datagrensen står under.

Behovssamtalen med MJ står under «Behovssamtale etter oppgavene». Gjenstår før P-13
kan lukkes: gruppas designvurdering. Kims krav om ekstern prøve er oppfylt.
