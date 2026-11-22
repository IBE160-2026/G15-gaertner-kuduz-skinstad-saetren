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

## Intern prøve — pågår

- Deltaker: Kim, gruppemedlem. Tidligere turnuserfaring ikke oppgitt.
- Testflate: nettleser og skjermbilder i chatten; faktisk brukt flate bekreftes ved avslutning.
- Oppgave 1, ordrett: «Fordi den har lavest ulempepoeng av kandidatene».
- Oppgave 2, ordrett: «Mette Solberg. Klikke på velg knappen og godkjenn erstatter kappen på neste side».
- Oppgave 3: Presentert, men første forsøk viste innlogging i begge lenker fordi deltakerens Chrome hadde en egen sesjon. Ordrett: «A og B er like. Det er innlogging så jeg ville lagt inn brukernavn og passord og trykket logg inn». Dette er et tilgangsproblem i testopplegget og skåres ikke som feil forståelse av kandidattilstandene. Testtilgang er gitt, og nytt svar avventes uten hint om innholdet.
- Etter innlogging svarte Kim: «Begge er like. Jeg ville klikket inn på velg vakt - finn erstatter». Deltakeren hadde fremdeles ikke fått bekreftet tilgang til de to tilstandene; heller ikke dette skåres som feil på oppgaven. Ingen årsak i appen er fastslått. For å fjerne leveringsproblemet ble de lagrede A/B-bildene servert direkte som PNG fra en egen, lokal HTTP-server på port 8765. Begge lenker ble verifisert med HTTP 200 og `image/png` før deltakeren fikk dem. Endelig svar avventes.
- Oppgave 3 etter riktig bildelevering, ordrett: «Den ene har ingen gyldige kandidater, veit ikke hva jeg skulle gjort. den andre har gyldige kandidater, men gyldig turnus finnes ikke så får ikke valgt noen men ville gjort det om det var tilgjengelig».
- Observasjon: Kim skiller null treff fra en datamangel, men tolker B som at gyldige kandidater finnes. Det kan appen ikke vite når vurderingen er stoppet. Overskriften «Gyldige kandidater» over datafeilen er en mulig årsak. I A ble rådet om innleie ikke brukt som neste steg. Testleder forklarte deretter forskjellen. En senere kontroll med Kim må derfor merkes som prøve etter forklaring, ikke som en ny prøve uten hint.
- Misforståelser og vurdering: Avventes til alle svar er registrert.
- Gruppas designvurdering, eventuell retting og ny kontroll: Ikke utført ennå.

## Behovssamtale etter oppgavene

Be om konkrete erfaringer, ikke bare om løsningen virker nyttig:

- Har deltakeren selv eller gjennom arbeid observert en vakt som måtte dekkes på kort varsel? Beskriv siste tilfelle uten personopplysninger.
- Hvordan ble erstatter funnet, hvilke opplysninger ble kontrollert og hva tok tid?
- Hvilken avgjørelse ville visningen hjulpet med, og hva måtte fortsatt kontrolleres utenfor appen?
- Hva mangler før verktøyet kunne vært prøvd i den faktiske arbeidsmåten?

Skill opplevd problem fra antatt nytte. Hvis deltakeren mangler turnuserfaring,
gir testen forståelsesbevis, men svakt grunnlag for å hevde validert brukerbehov.

## Ekstern prøve — gjenstår

Samme tre oppgaver uten hint, med én person utenfor gruppen. Registrer initialer,
rolle/erfaring, dato, OS, skjermflate og versjon. Bevar ordrette svar, eventuelle
misforståelser og vurdert designendring. Ved feil på en oppgave: rett årsaken,
bevar før/etter-bilder og prøv igjen. En ny prøve etter hint må merkes som slik.
P-13 lukkes først når kriteriene er oppfylt og gruppas designvurdering er dokumentert.
