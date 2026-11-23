# Sensorutkastet om innlogging

## 2026-11-23 kl. 22:21 — johagartnerHiMolde

### Oppgave
Hente siste endringer og få en gjennomgang av dem. Deretter rydde i sensorutkastet
`docs/innlevering/til-sensor-innlogging.md` (Johannes, 2026-11-07), som lenker til
README-overskrifter som har fått nye navn. README skal inneholde det essensielle, og bare
det som ikke står der, skal beholdes.

### Plan
- `git pull --ff-only`: 62 nye commiter fra Ragnhild, Kim og Mithad (story 5.5, 5.7 og
  5.8, ny README med `docs/teknisk-referanse.md`, ruff og strengere tsconfig, loggoppsett
  i backend, AV-20, foreløpig intern sensorvurdering).
- Sammenligne utkastet punkt for punkt med README etter `87db4d9`, og søke etter
  henvisninger til utkastet i repoet. Ragnhilds funn står i
  [story-5-8-sensor-live-ki](../ragnhild/972-2026-11-23-18-15-42-story-5-8-sensor-live-ki.md)
  og [gjennomgang-mot-sensorveiledningen](../ragnhild/975-2026-11-23-14-23-14-gjennomgang-mot-sensorveiledningen.md).

### Resultat
- **Lenkene:** Bare lenken til steg 2 (`#2-last-testdata-og-noter-passordet`) var brutt.
  Overskriften heter nå «2. Last testdata og velg passord». Lenken til steg 1 virket.
- **Dekning i README:** Alt i utkastet står nå i README: brukernavnet, at passord ikke står
  i repoet, variant A (merket «anbefalt for sensor») og B med utskriftslinjen, taggen på
  innloggingskortet, utlogging ved omstart (Konfigurasjon og Feilsøking), `npm.cmd` og
  operativsystemene. Det eneste som ikke står i README, er henvisningen til OP-10, og den
  trenger ikke sensor.
- **Endringer (ukommittert, venter på Johannes):**
  - `docs/innlevering/til-sensor-innlogging.md` er slettet med `git rm`.
  - Utkastet til innleveringstekst i `docs/innlevering/sjekkliste-live-ki.md` (Ragnhild,
    story 5.8) har fått et avsnitt «Kjøring og innlogging» foran «Live KI»: start etter
    README «Kom i gang», logg inn som `kari.vestby`, passordet velges i steg 2 variant A.
    Det var det opprinnelige formålet med utkastet (punktet fra 2026-11-07 i `issues.md`).
- **Ikke endret:** Henvisningene i `spec-5-8-sensor-kan-kjore-live-ki.md`, Ragnhilds logger
  og den foreløpige interne sensorvurderingen er historiske og står som de er.
  Ragnhilds punkt om den brutte lenken i `.logs/ragnhild/issues.md` er hennes å krysse av.

### Åpne punkter
- Ragnhild krysser av punktet om den brutte lenken i sin `issues.md`, nå som utkastet er
  slettet.
