---
title: "Arkitekturen forklart — Turnushjelperen"
purpose: "Forklarende dokument til gruppen selv og til refleksjonsrapporten (IBE160)"
status: draft
created: 2026-09-29
source: "ARCHITECTURE-SPINE.md (autoritativ), .memlog.md (begrunnelser), prd.md, addendum.md §4"
---

# Arkitekturen forklart — Turnushjelperen

Dette dokumentet er *ikke* spesifikasjonen. Den finnes i `ARCHITECTURE-SPINE.md` i samme mappe, og er det som faktisk styrer implementasjonen. Dette dokumentet er en forklaring på **hvorfor** spinen ser ut som den gjør — skrevet slik at alle fire i gruppa kan lese det, forstå valgene, og bruke resonnementene direkte når dere skriver refleksjonsrapporten.

## 1. Hva arkitekturen skal løse

Turnushjelperen løser ett konkret problem: en vakt mister bemanning, og den turnusansvarlige må finne en erstatter uten å sjekke 20–30 ansatte manuelt mot kompetansekrav, kolliderende vakter og hviletidsregler. Løsningen er ikke bare "vis hvem som er ledig" — det kunne enhver kalender gjøre. Den er heller ikke "la en språkmodell foreslå noen" — det ville vært et gjettverk uten grunnlag. Poenget er kombinasjonen: harde regler filtrerer bort det som er *ulovlig eller umulig*, en enkel og reproduserbar modell rangerer det som er *igjen* etter kostnad, arbeidsbelastning og kompetansenærhet, og KI gjør det hele forståelig — ved å tolke fritekst-preferanser og forklare avveiningene i klartekst. Systemet anbefaler. Det bestemmer aldri selv, og det kan aldri anbefale noen en hard regel har utelukket.

Hele arkitekturen er bygget for å gjøre nettopp den siste setningen sann — ikke som en påstand i dokumentasjonen, men som noe som faktisk kan testes og bevises.

## 2. Hvorfor hexagonal arkitektur — forklart uten forutsetninger

"Hexagonal arkitektur" (også kalt "ports and adapters") høres mer skremmende ut enn det er. Tenk på det som et strømuttak. Uttaket i veggen (porten) har en fast, definert form. Det bryr seg ikke om det er en lampe, en laptop-lader eller en støvsuger som plugges inn (adapterne) — så lenge støpselet passer i uttaket, fungerer det. Du kan bytte ut lampa med en annen lampe, eller bytte hele stikkontakten til en ny modell, uten å rive ned veggen den sitter i.

I Turnushjelperen er "veggen" **domenekjernen** — koden som inneholder selve forretningslogikken: de harde reglene (kompetanse, kolliderende vakt, 11-timersregelen, 35-timersregelen), kostnadsberegningen og rangeringen. Denne koden er ren Python. Den vet ingenting om FastAPI, ingenting om React, ingenting om SQLite, og — viktigst av alt — ingenting om Gemini eller noen annen språkmodell. Den kan kjøres og testes helt alene, uten nettverk, uten database, uten rammeverk.

Rundt kjernen ligger **adapterne** — alt som kobler kjernen til omverdenen: `adaptere/api` (FastAPI, tar imot HTTP-kall), `adaptere/web` (React-appen i nettleseren), `adaptere/lagring` (SQLAlchemy mot SQLite) og `adaptere/ki` (Gemini). Regelen er enkel og ensrettet: adapterne avhenger av kjernen, aldri omvendt. Kjernen vet ikke at FastAPI finnes. FastAPI vet at kjernen finnes og bruker den.

Dette er ikke arkitektur for arkitekturens skyld. Grunnen til at det er verdt kompleksiteten her — for et prosjekt av denne størrelsen, med fire studenter og én sesong — er at det finnes ett konkret sted der grensen *må* holde: mellom regelmotoren og KI. Det er tema for neste seksjon, og det er også grunnen til at gruppa valgte dette mønsteret fremfor en enklere, lagdelt arkitektur (jf. memlog): en eksplisitt typet port gir en sterkere garanti enn en uskrevet avtale om "vi kaller bare KI-koden herfra", for omtrent samme kompleksitetskostnad.

## 3. Den viktigste grensen: regelmotor vs. KI

Dette er den mest sentrale beslutningen i hele arkitekturen, og den seksjonen i dette dokumentet som er verdt å lese grundigst — og som dere med fordel kan bygge videre på i refleksjonsrapportens vurdering av teknisk kvalitet og KI-bruk.

### Hvorfor grensen finnes

En innvending som er lett å møte på, er at Turnushjelperen egentlig "bare er en sorteringsalgoritme med en tekstgenerator på toppen" — som om KI-delen er pynt og resten er triviell. Den påstanden bommer på hva som faktisk er vanskelig her. Å sortere en liste er ikke det krevende arbeidet. Det krevende er å avgjøre *hva* som skal sorteres på, å beregne hviletid og kompetansekrav riktig hver eneste gang, og å gjøre avveiningen mellom kandidater forståelig nok til at en turnusansvarlig faktisk tør å handle på den. Arbeidsmiljøloven krever et deterministisk svar på om noen har fått nok hvile — ikke et sannsynlig svar. En språkmodell er per natur en sannsynlighetsmaskin: den kan formulere seg annerledes fra kall til kall selv med identisk input. Å la den avgjøre om en hviletidsregel er brutt, ville derfor ikke vært en teknisk mangel som kunne rettes senere — det ville vært feil verktøy for oppgaven, valgt inn i et system der loven krever forutsigbarhet. Det samme gjelder Helseplattform-eksemplet fra bransjen: når leddet som skal gjøre beslutningen etterprøvbar hoppes over, er det brukerne som betaler prisen, i form av tillit de aldri får igjen.

Derfor er ansvarsdelingen i Turnushjelperen ikke en høflig konvensjon, den er strukturelt håndhevet:

- **Regelmotoren** (`domene/regelmotor`) beregner alt som må være reproduserbart: harde regler, kostnad, arbeidsbelastning, og selve rangeringen. Ren Python, ingen avhengighet til KI.
- **KI-adapteren** (`adaptere/ki`) har to — og bare to — oppgaver, begge ensrettede: den tolker rå fritekst om ansattpreferanser til et strukturert format *før* rangeringen skjer, og den forklarer i klartekst *etter* at rangeringen er ferdig. Den kaller aldri inn i regelmotoren for å hente mer informasjon, og den kan aldri overstyre et resultat regelmotoren har kommet frem til.

### Hvorfor det er strukturelt, ikke bare en avtale

Ingeniørarbeidet her ligger ikke i å skrive "KI skal ikke overstyre reglene" i et dokument — det ligger i skjøten mellom lagene, altså i selve grensesnittet mellom dem. Dette er løst med to eksplisitt typede porter (Pydantic-modeller, eid av `domene/porter`), som er de *eneste* stedene data krysser grensen:

- **`TolketPreferanse`** — det KI-adapteren produserer *inn* til rangeringen. Regelmotoren mottar alltid en allerede tolket og lagret verdi her, aldri et rått, live KI-kall midt i selve beregningen. Fordi tolkningen skjer én gang og lagres, forblir rangeringen reproduserbar selv om selve tolkningssteget (som bruker en språkmodell) i seg selv ikke er det.
- **`RangertKandidat`** — det regelmotoren produserer *ut* av rangeringen, og som KI-adapteren mottar for å generere forklaringen. KI-adapteren ser kun de feltene denne porten definerer — kandidat-referanse, kompetansenivå, kostnad, arbeidsbelastning, rangeringsplass og den tilhørende tolkede preferansen. Kun regelmotoren har lov til å konstruere en `RangertKandidat`, og en kandidat som er filtrert bort av en hard regel, finnes rett og slett ikke i den dataen KI-adapteren noensinne får se. Den kan ikke anbefale noen den ikke vet eksisterer.

Ingen av adapterne kaller den andre veien. `adaptere/api` er den eneste som snakker med begge — den orkestrerer kallene og sender data mellom dem som helt ordinære funksjonsargumenter og returverdier, ikke som skjulte avhengigheter.

### Hvordan gruppa faktisk kan vise at grensen holder

En påstand om at en grense holder er verdiløs uten bevis. Dette er testbart på to nivåer, og begge er en del av testkonvensjonen i spinen (pytest på backend, ett testmodul per hard regel):

1. **Statisk (import-linter-kontrakt):** en mekanisk sjekk av at `domene/regelmotor` og `domene/porter` ingen steder importerer `adaptere/ki`, verken direkte eller indirekte. Dette fanger den opplagte feilen — noen legger til en snarvei "for enkelhets skyld" og importerer KI-koden rett inn i kjernen.
2. **Kjøretidsinvariant (en egen test i `tester/`):** en statisk importsjekk alene fanger ikke en logisk feil der `adaptere/api` ved en glipp sender en *utelukket* kandidat inn i porten til KI-adapteren, uten å bryte noen importregel. Derfor kreves en egen test som, for et testscenario med kjente utelukkelser, verifiserer at ingen av ID-ene som faktisk sendes til `adaptere/ki` finnes blant dem regelmotoren har filtrert bort.

Dette er også svaret på et beslektet, reelt metodisk problem: hvordan tester man noe som ikke er deterministisk? Man tester ikke KI-forklaringens eksakte ordlyd — det ville vært skjørt og meningsløst. Man tester i stedet *invariantene*: at forklaringen aldri nevner en utelukket kandidat, at alle påkrevde elementer er til stede, og at systemet fortsetter å fungere (viser en reservetekst, ikke en anbefaling uten grunnlag) hvis Gemini svarer tomt, feil eller ikke i det hele tatt. Det er nettopp fordi grensen mellom de to lagene ble lagt der den ble, at dette i det hele tatt lar seg teste.

Verdt å ta med videre til refleksjonsrapporten: enhver rangeringsmodell gjør et normativt valg, og det er ikke noe arkitekturen alene kan løse bort. Å vekte "har sagt ja før" høyt favoriserer systematisk dem som alltid sier ja. Å vekte kostnad høyt favoriserer systematisk lavtlønte og deltidsansatte. Systemet kan ikke gjøres nøytralt — det kan bare gjøres åpent om hva det faktisk vekter, og det er nøyaktig det Avveining-forklaringen er ment å gjøre: ikke skjule en beslutning bak et tall, men vise regnestykket bak den. Grensen mellom regelmotor og KI er dermed ikke bare en teknisk forsiktighetsregel — den er det som gjør denne åpenheten mulig i utgangspunktet, fordi den tvinger frem et presist svar på spørsmålet "hva vekter faktisk dette systemet, og hvor i koden skjer det?"

## 4. Stack-valgene og hvorfor

Dette er ikke en versjonsliste (den ligger i spinens Stack-tabell) — det er begrunnelsen for hvert valg.

- **FastAPI (Python)** — valgt fremfor Django (unødvendig tungt for et prosjekt uten admin-panel eller brukerportal-behov) og Flask (mangler den innebygde typevalideringen som gjør det enkelt å definere og håndheve porter som `TolketPreferanse` og `RangertKandidat`). Fordi regelmotoren uansett er skrevet i Python, gir FastAPI også ett språk gjennom hele backend.
- **React + Vite** — valgt fremfor Next.js, som løser problemer (SEO, server-side rendering) Turnushjelperen ikke har. Appen er fire lineære skjermer bak innlogging, ikke et offentlig nettsted.
- **SQLite via SQLAlchemy** — trengs kun for å huske godkjente erstatninger og innloggingssesjoner mellom omstarter. Ingen samtidige brukere, ingen skaleringsbehov — en tyngre database ville løst et problem prosjektet ikke har.
- **Google Gemini** — valgt fremfor Claude og OpenAI fordi Gemini (på verifiseringstidspunktet) hadde en reell gratis-tier uten betalingskort, mens alternativene enten krever betaling eller kun gir en engangskreditt. For et studentprosjekt uten budsjett er det utslagsgivende.

Ingen av disse valgene er trepilarer i seg selv — de er pragmatiske, begrunnede tilpasninger til at dette er et prosjekt av denne størrelsen, med denne tidsrammen, bygd av fire personer. Det som *er* prinsipielt i arkitekturen, er skillet i seksjon 3, ikke rammeverkvalgene.

## 5. Hva som bevisst er utsatt, og hvorfor det er greit

Spinen har en egen Deferred-liste med ti punkter — ting som *bevisst* ikke er avgjort ennå. Det er ikke slurv, det er en prioritering: disse valgene påvirker ikke om systemet kan begynne å bygges, og å avgjøre dem for tidlig ville bare vært gjetting uten nok informasjon. Noen eksempler:

- **Vekting mellom myke faktorer** (kostnad, arbeidsbelastning, preferanse, kompetansenærhet) — gruppa er enig om at kompetansenærhet skal telle tungt når ingen er fullt kvalifisert, men den fulle vektingen avgjøres når regelmotoren faktisk skal skrives, med ekte testscenarioer å vurdere den mot.
- **Gemini-modellversjon og hva som skjer ved fartsgrense** — leverandøren er valgt, ikke modellen. Gratis-tiers endrer seg fort nok at det er lite poeng i å låse dette før implementasjon starter.
- **Nøyaktig JWT-utløpstid, migreringsverktøy for databasen, feilkode-verdier** — dette er implementasjonsdetaljer som ikke endrer arkitekturen uansett hvilken vei de avgjøres. De kan bestemmes av den som skriver koden, når koden skrives.
- **Hosting/driftsmiljø** — kun lokal kjøring er bestemt for nå. Dette er et v1-prosjekt for et kurs, ikke noe som skal driftes i produksjon ennå.

Fellesnevneren: alt som er utsatt, er utsatt fordi det *kan* utsettes uten å blokkere noe annet — ikke fordi det er ubehagelig å bestemme.

## 6. Hvordan dette kan endres senere

Denne arkitekturen er ikke støpt i betong, og den er ikke ment å være det. Den samme arbeidsformen som er brukt til å komme frem til spinen — beslutning, begrunnelse, logget i `.memlog.md` — gjelder også for å endre den. Ingen del av spinen er mer autoritativ enn at gruppa kan gå tilbake og justere den, så lenge endringen er bevisst og begrunnet, ikke en stille avvik i koden som aldri kommer tilbake til dokumentet. Praktisk sett: finner dere ut underveis at porten `RangertKandidat` mangler et felt, eller at en Deferred-avgjørelse haster raskere enn ventet, oppdateres spinen og memloggen — ikke bare koden. Det er også slik dere holder dokumentasjonen troverdig som bevis for kvalitetssikring i vurderingen av prosjektet: den skal beskrive systemet som det faktisk er, ikke som det var da det ble skrevet første gang.
