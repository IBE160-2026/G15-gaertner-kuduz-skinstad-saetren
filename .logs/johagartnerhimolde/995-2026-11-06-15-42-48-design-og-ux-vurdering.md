# Design- og UX-vurdering

## 2026-11-06 kl. 15:42 — johagartnerHiMolde

### Oppgave
Brukeren ville vite om darkmode, zoom med Ctrl + scroll og tilpasning til ulike enheter er planlagt. Deretter ba brukeren om å gå over til `main`, notere `rem` i stedet for `px` som et mulig valg for senere, og vurdere design og brukeropplevelse opp mot sensorveiledningen (kriterium 4) og faglærers tilbakemelding på product brief.

### Plan
- Lest `DESIGN.md`, `EXPERIENCE.md`, UX-DR1–28 i `epics.md`, story 4.6, ÅB-7, OP-02, `docs/emne/sensorveiledning-del-1.md`, `docs/emne/vurderingsmatrise.md`, `tilbakemelding-product-brief.md` og reviewen `reviews/product-brief-2026-10-26.md`.
- Regnet ut kontrastforhold (WCAG-formelen) for fargene i paletten mot bakgrunnene de brukes på.
- Sammenlignet PRD FR-9 med UX-DR7 og FR9 i epics.

### Resultat
- Byttet fra `ci-skills-speiling` til `main`. Ingen filer i prosjektet er endret, bare denne loggen og `issues.md`.
- **Darkmode:** bevisst valgt bort som utgangspunkt («ikke dark-mode-først», DESIGN.md og UX-DR1). En mørk retning ble laget og forkastet.
- **Zoom:** nevnes ikke noe sted. Nettleserzoom virker, fordi `frontend/index.html` ikke blokkerer den. Skriftstørrelsene er satt i px (10,5–15px), så nettleserens innstilling for standard skriftstørrelse slår ikke inn.
- **Skjermstørrelser:** planlagt i story 4.6 (UX-DR25), men breakpoints er åpne (ÅB-7), og OP-02 utsetter mobiltilpasning. Mockupene viser bare fast 1180px.
- **Kontrast:** alle tekstfarger har minst 4,5:1 mot bakgrunnene de brukes på (`text-mute` 4,61–5,48, `ok` 4,69–5,32, `warn` 4,66–5,28). `ok` og `warn` på `tag-bg` gir 4,47 og 4,44, men taggene er nøytrale etter spesifikasjonen. `border` mot hvitt er 1,56:1, som er for svakt for kanter på skjemafelt (WCAG 1.4.11 krever 3:1).
- **Vurdering mot kriterium 4:** sterke spor av designarbeid (to dokumenter, fire mockuper, to forkastede retninger med begrunnelse), et konsistent tokensystem og gjennomtenkte tilbakemeldinger og tomtilstander. Svakhetene er at ingenting er bygget, at responsivitet er utsatt og avhenger av 4.4 og 4.7, at tilgjengelighetsgulvet mangler alternativtekst og skjemaetiketter, at arbeidsbelastningslinjen signaliserer bare med farge (UX-DR9), og at det ikke finnes noen forståelsestest.
- **Motstrid funnet:** PRD FR-9 sier at kandidatlisten viser inntil fem av de høyest rangerte, med tilgang til de øvrige. UX-DR7 og FR9 i `epics.md` sier én rad per gyldig kandidat og nevner ikke grensen.

### Åpne punkter
- `rem` i stedet for `px` for designtokenene (UX-DR1) kan være et fornuftig valg. Vurderes før tokenene implementeres. Fordeler og ulemper står under.
  - For `rem`: respekterer nettleserens innstilling for skriftstørrelse, og hele skalaen kan justeres fra én rotverdi. Media queries i `em`/`rem` følger også brukerens tekststørrelse. Det koster lite så lenge frontenden er tom.
  - Mot `rem`: tokenene og mockupene er i px, og omregningen gir skjeve tall (10,5px = 0,65625rem). Den tette tabellen kan sprekke når brukeren har stor standardtekst, så det må testes. Gruppa trenger en regel for hva som fortsatt er px (f.eks. 1px-kanter). Ctrl-zoom virker likt med begge, så gevinsten gjelder bare skriftinnstillingen.
  - Mellomløsning: skriftstørrelser i `rem`, kanter og eventuelt avstander i px.
- PRD FR-9 (inntil fem kandidater) og UX-DR7/FR9 i `epics.md` (alle gyldige) er motstridende. Må avklares før rangeringstabellen bygges.
- Tilgjengelighet for svaksynte og skjermleser bør vurderes inn i tilgjengelighetsgulvet (UX-DR24): alternativtekst for ikoner som «!», ▲ og ▼, etiketter på skjemafelt, tabelloverskrifter skjermleseren kan lese, og at åpnet/lukket begrunnelse og statusmeldinger blir lest opp. EXPERIENCE.md § Accessibility Floor sier i dag «Ingen bekreftet skjermleser-/ARIA-innsats», og omtaler det som en bevisst avgrensning, så endringen krever et gruppevedtak. At høy belastning varsles bare med farge (UX-DR9), er akseptert av brukeren. Zoom regnes som dekket.
- Fra første story som bygger appskallet (story 1.3 Innlogging eller 1.5 Vaktoversikt): vurder flytende bredde med `max-width` i stedet for fast 1180px. Fordeler og ulemper:
  - For `max-width`: ingen horisontal scroll i smale vinduer, delt skjerm eller med zoom; ser ut som mockupene på brede skjermer; story 4.6 blir et tillegg (kortvisning på mobil) i stedet for en omskriving; mindre risiko for at responsivitet kuttes sent, og sensor skal prøve flere skjermstørrelser.
  - Mot `max-width`: tabellen må tåle å krympe (lange navn, kolonner som brytes) og testes på flere bredder i hver story; mellombreddene avviker fra mockupene.
  - For fast 1180px: lett å sammenligne med mockupene, og færre layoutvarianter tidlig.
  - Mot fast 1180px: horisontal scroll under 1180px, også på en laptop med zoom; story 4.6 må bygge om layouten.

### Oppfølging samme dag
Brukeren ba om notat om `max-width` (lagt inn over), presiserte at tilgjengelighet for svaksynte og skjermleser er viktig, at fargevarsel for høy belastning er greit og at zoom er dekket. Forståelsestesten er strøket: gruppa tester brukernytten internt når det er mulig. Kontrollert at `[ASSUMPTION]`-merkene i UX-kravene er ført inn i akseptansekriteriene til storiene de gjelder (1.3, 1.5, 2.1, 2.4, 5.5, ÅB-7 i 4.6). Unntaket er reserveteksten i story 5.4: UX-DR14 sier at teksten ikke er fastsatt, men storien merker det ikke.

Siste oppfølging: brukeren støtter avgrensningen i EXPERIENCE.md § Accessibility Floor for v1. Lagt til et avsnitt der om at utvidet tilgjengelighet for svaksynte med skjermleserstøtte er et mulig tillegg i v2, og satt `updated` til 2026-11-06. Endringen i EXPERIENCE.md er ikke committet. Punktet om tilgjengelighet i `issues.md` er lukket. Brukeren har tatt til etterretning at reserveteksten i story 5.4 ikke er merket som antakelse; ingen endring.
