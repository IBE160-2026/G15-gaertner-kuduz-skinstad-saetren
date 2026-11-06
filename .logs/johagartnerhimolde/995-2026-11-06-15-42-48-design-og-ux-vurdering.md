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
- Tilgjengelighetsgulvet (UX-DR24) bør vurderes utvidet med alternativtekst for ikoner, skjemaetiketter, 200 % zoom uten horisontal scroll og et tekstlig signal i tillegg til fargeskiftet i arbeidsbelastningslinjen (UX-DR9).
- En enkel forståelsestest av kandidatvisningen mangler (påpekt i reviewen 2026-10-26, utsatt i OP-02).
