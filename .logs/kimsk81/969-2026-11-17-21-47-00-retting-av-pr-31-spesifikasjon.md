# Retting av PR 31-spesifikasjon

## 2026-11-17 kl. 21:47 — Kimsk81

### Oppgave
Følg opp de godkjente funnene fra gjennomgangen av PR 31 ved å rette spesifikasjonen og kontrollere grunnlaget.

### Plan
- Arbeid i en isolert arbeidskopi av PR-branchen fordi hovedarbeidskopien har andre lokale endringer.
- Kontroller presiseringene mot eksisterende kode, prosjektbeslutninger og uavhengig gjennomgang.

### Resultat
Spesifikasjonen presiserer tilgjengelig timetall, lagrede preferansetolkninger og kontrollert fasit, sammenligning i kandidatgrupper og oppdatert rangering etter `endret_grunnlag`. En uavhengig gjennomgang av endringene avdekket og rettet en gjenværende uklarhet om linjebryting. `git diff --check` bestod; 99 målrettede backendtester bestod i PR-arbeidskopien. Frontendkoden er identisk med hovedarbeidskopien, der bygget og alle 52 modultester og 37 komponenttester bestod. Testene gjelder eksisterende kode, ikke den ennå uimplementerte storyen. Spesifikasjonsendringen er ikke committet eller pushet.

### Åpne punkter
Ingen.

## 2026-11-18 kl. 18:07 — Kimsk81

### Oppgave
Gjennomgå implementasjonen i PR 31 etter oppdatering, og oppdatere PR-beskrivelsen.

### Plan
- Gjennomgå diffen mot storyens spesifikasjon og beslutninger med uavhengige kontrollører.
- Kjør relevante tester og oppdater PR-beskrivelsen med faktisk status.

### Resultat
Gjennomgått PR-hode `8d1f332f1c3f1b5956ecf58115241daa87178ff6`. 42 målrettede backendtester, frontendbygg, 52 frontendmodultester og 41 komponenttester bestod. Fant manglende ulempeetikett, rå bredde uten token, testmangler og motstridende status i plandokumenter; funnene er ført i spesifikasjonens Review Findings. PR-tittel og -beskrivelse ble oppdatert på GitHub.

Etter brukerens beskjed ble alle funnene rettet lokalt: etikett, token, ulike timetall og kostnader, begge ulempefordelingene, konsistent P-09-fixtur og samordnet status til `review`/`in-review`. En uavhengig kontroll anbefalte ulik kostnad i testen, som ble tatt inn. Frontendbygget og 52 modultester samt 41 komponenttester bestod etter rettingen. Nettleserkontroll ved 1080 og 680 px med falske API-svar viste etiketten alle tre steder. Faktisk skjermleser ble ikke testet. KI-logg og vurderingsmatrise er oppdatert. Reviewpunktet i `issues.md` er lukket.

### Åpne punkter
Ingen.
