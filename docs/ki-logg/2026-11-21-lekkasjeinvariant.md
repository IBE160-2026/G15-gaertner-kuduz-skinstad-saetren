# KI-logg: Story 5.6 – utelukkede kandidater når aldri KI-laget

Dato: 2026-11-21. Testkoden er skrevet av Claude (Opus 5.5) som implementeringsunderagent
i `bmad-build` (rute `dispatch`), på branchen `story-5.6-utelukkede-aldri-ki`.

## Oppgave og prompt

Ragnhild startet story 5.6 og godkjente spesifikasjonen
[`spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md`](../../_bmad-output/implementation-artifacts/spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md).
Der valgte hun også å utsette demodelen av AC3 til story 5.7. Implementeringsagenten fikk
denne prompten fra orkestreringen, ordrett:

> Read `_bmad-output/implementation-artifacts/spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md`
> fully and implement it — the spec is the sole source of truth. Load every file listed in
> its frontmatter `context:` before you start.

Spesifikasjonens frosne Intent: lage en kjøretidstest gjennom `adaptere/api` som beviser
lekkasjeinvarianten (NFR2, SM-2, AD-1, AD-2) for alle fire harde regler, og vise med en
negativ kontroll at testen blir rød når grensen brytes. Bare testkode og dokumentasjon.

## Leveranse

Ny testmodul [`backend/tester/api/test_lekkasjeinvariant.py`](../../backend/tester/api/test_lekkasjeinvariant.py)
med 21 tester. Ingen produksjonskode er endret, og ingen lekkasje ble funnet.

- **Oppsett.** Appen bygges med `lag_app` mot testdataene i en midlertidig database. KI-
  adapteren er ekte `OpenRouterKiAdapter` med en falsk transport som lagrer hver
  forespørsel og svarer gyldig på begge porter, og en falsk klokke, så begrenseren
  (18 kall per minutt) ikke venter på ordentlig. Adapteren pakkes i en tynn
  `RegistrerendePort` som også lagrer hvert kall på `forklar` og `tolk`. Portene skilles
  på `response_format.json_schema.name` (`avveining` eller `preferanse`).
- **Hele flyten** for vakt #4127 (4 gyldige, 20 utelukkede: 8 kompetanse, 7 kolliderende,
  4 elleve-timer, 1 trettifem-timer): oppstart med bakgrunnstolkning, kandidatlisten,
  godkjenningsgrunnlaget for hver rad, direkte oppslag på alle 20 utelukkede og på en
  ukjent ID, og til slutt en avveining for hver gyldig kandidat.
- **Fire invariantkontroller**, hver for seg:
  1. `kontroller_forklaringsporten`: ingen utelukket ID eller navn i kallene på `forklar`,
     verken som kandidat eller referanse.
  2. `kontroller_forklaringsforespørslene`: alle `kandidat_id` og `referanse_id`, hentet
     rekursivt fra det som faktisk sendes til modellen, er gyldige. Kontrollen søker også
     etter utelukkede navn i forespørselen, men `forklar` sender ingen navn, bare ID-er.
     Navnedelen holder derfor fordi innholdet ikke har navn, og den kan ikke bli rød i
     dag. Det er ID-delen den negative kontrollen beviser.
  3. `kontroller_api_svar`: kandidatradene, godkjenningsgrunnlaget (også `topprangert`) og
     avveiningssvarene har bare gyldige ID-er og navn. For listen kontrolleres hele svaret
     unntatt `utelukkelser`, så også et nytt toppfelt med en utelukket blir fanget.
  4. `kontroller_direkte_oppslag`: hver utelukket gir samme 404 `ikke_funnet` som en
     ukjent ID, både for avveiningen og godkjenningsgrunnlaget, og ingen nye
     forklaringskall.
- **Null forklaringskall** mens listen og godkjenningsgrunnlaget beregnes, talt både på
  porten og på transporten.
- **Ekskludert-boksen** skal vise de utelukkede (story 2.5). Testen kontrollerer at den har
  alle 20 med navn og årsak, og at tallene per regel følger fasiten.
- **Fasittest:** `FASIT[4127]` har minst én utelukkelse per regel, og minst én utelukket
  har en preferansetekst. Mister testdataene en regel, blir testen rød.
- **Modellen peker på utelukket:** svaret bytter `kandidat_id` eller `referanse_id` med en
  utelukket ID, for alle 20. Hvert svar blir `avveining_feilet` uten utelukkede navn (P-06).
  En positiv kontroll først viser at samme svarform med den gyldige ID-en gir `ok`, så
  avvisningen skyldes den utelukkede ID-en. Avvisningen kommer fra den generelle regelen i
  `avveining.valider` (bare påstander som er identiske med de tillatte, består), ikke fra en
  egen sperre mot utelukkede ID-er. `AvveiningFeiletUt` har ingen navnefelt, bare
  vaktnummer, kandidat-ID og grunnlagsmerke.
- **Tolkingsporten:** bakgrunnstolkningen sender også tekster fra ansatte som senere blir
  utelukket. Det er tillatt (AD-2), men forespørselen har bare `tekst`, ingen kandidat-ID,
  vaktnummer eller status.
- **Klar for 5.7:** flyttesten og tolketesten er parametrisert over `ADAPTERFABRIKKER`.
  Story 5.7 legger til `DemoKiAdapter` som ny parameter. Kontrollene på porten og i
  API-svarene gjelder da uendret (AD-6). Punktet er ført i `deferred-work.md`.

## Den negative kontrollen

`lekk()` monkeypatcher `main.vurder_kandidater` slik at én utelukket Kandidat flyttes inn
i `gyldige`, med egen Ulempebelastning. Testen kjøres for én utelukket per regel og hver av
de fire kontrollene, til sammen 16 kjøringer. Først kontrolleres det at lekkasjen er
virkelig: den utelukkede står som rad og ble sendt til `forklar`. Deretter må kontrollen
gi `AssertionError`. Alle 16 gjorde det, og hver kontroll feilet av sin egen grunn. For
eksempel meldte kontroll 2 «utelukket ID i forklaringsforespørselen: {11}» for
Anders Strand (35-timersregelen). For kontroll 2 er det ID-delen som feiler, siden
forespørselen ikke har navn.

## Rettelser underveis

- Den første versjonen lekket Eirik Moen (kompetanse) i den negative kontrollen. Han har
  ikke noe nivå for dagvakt, og da stoppet Rangeringen selv med `ValueError` («gyldig uten
  kompetansenivå») før noe nådde KI. Det er en ekstra sperre i regelmotoren, ikke en
  lekkasje. Kontrollen velger nå den første utelukkede per regel som har et nivå for
  vakttypen (Tone Brekke for kompetanse), slik at lekkasjen faktisk når fram.
- Den første versjonen hadde én kontroll for både porten og forespørslene. Den negative
  kontrollen feilet da alltid på porten, så det var ikke vist at kontrollen av
  HTTP-forespørslene virket alene. Den ble delt i to.

## Hva testen beviser og ikke beviser

Beviser: med testdataene for #4127 og ekte regelmotor, rangering, API-ruter og
OpenRouter-adapter når ingen utelukket ID eller navn forklaringsporten, ingen utelukket ID
HTTP-forespørselen (som ikke har navn i det hele tatt), og ingen utelukket står i kandidatradene, godkjenningsgrunnlaget eller
avveiningssvarene. Et modellsvar som peker på en utelukket, forkastes. Kontrollene blir
røde ved lekkasje etter hver av de fire reglene. Sammen med import-linter-kontrakten i
[`test_arkitektur.py`](../../backend/tester/test_arkitektur.py), som kjører i samme `pytest`,
dekker det både den statiske og den kjørende delen av AD-1 og AD-2.

Beviser ikke: andre vakter enn #4127, ekte modellsvar (ingen live-kall), flere
serverprosesser, eller frontend. `DemoKiAdapter` er ikke testet, fordi den kommer i
story 5.7. Den delen av AC3 er utsatt og ført i
[`deferred-work.md`](../../_bmad-output/implementation-artifacts/deferred-work.md).

## Kvalitetssikring

- `cd backend && .venv/bin/python -m pytest tester/api/test_lekkasjeinvariant.py -v`:
  21 av 21 bestått.
- `cd backend && .venv/bin/python -m pytest`: 738 av 738 bestått, også `test_arkitektur.py`.
  Kjørt på macOS med Python i `backend/.venv`.
- Den negative kontrollen er en del av testsamlingen, så den kjøres i CI ved hver push.
- Ingen nettverk, ingen nøkkel og ingen nye avhengigheter. `tester/conftest.py` fjerner
  KI-variablene.
- Uavhengig kodegjennomgang: tre underagenter på Opus (Blind Hunter, Edge Case Hunter og
  Verification Gap) gjennomgikk diffen uten å ha sett implementeringen. De ga 17 funn.
  Seks ble rettet: smalere feilmelding, ærlig beskrivelse av navnesjekken, positiv kontroll
  i testen der modellen peker på en utelukket, hele listesvaret sjekket, ordsøket i
  tolkeforespørselen avgrenset til brukermeldingen, og en merknad om den negative
  kontrollen for story 5.7. De andre ble avvist med begrunnelse. Verification Gap fant ingen
  hull. Vurderingen av hvert funn står i spesifikasjonens Review Triage Log. Etter rettingene
  bestod 21 av 21 i modulen og 738 av 738 i hele backendsamlingen.
