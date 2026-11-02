# KI-logg: ÅB-3 utvidet med ulempebelastning

Planleggingsarbeid i to økter med Claude Code (`claude-opus-5-5`), 30.10 og 02.11.2026,
på branchen `ab-3-ulempbelastning` (PR #4). Det er ikke skrevet programkode. KI-en
foreslo og skrev dokumentendringene og regnet ut tallgrunnlaget for taket. Alle
beslutninger om modell, vekter og tak er tatt av Ragnhild og godkjent av gruppa
2026-11-02. Loggen er skrevet av agenten og er dermed egenrapportering.

## Oppgaven

Arbeidsbelastningen (ÅB-3) målte bare timer denne uken. Den skulle også ta hensyn
til ubekvem arbeidstid, uten å endre hovedvektingen 40/35/25 (kostnad,
arbeidsbelastning, preferanse). Modellen skulle være regelbasert og reproduserbar,
siden KI aldri skal beregne arbeidstid eller rangering (AGENTS.md, NFR1).

## Prompter

Økten 30.10 gikk i flere runder der brukeren ba om vurdering uten filendringer før
hver beslutning. De styrende promptene, ordrett:

> Takk for gjennomgangen. Jeg ønsker å gå videre med modellen du anbefaler, med noen presiseringer.
>
> **Vi legger følgende til grunn for ÅB-3:**
>
> 1. **Rangeringsmodell** – Kostnad: 40 % – Timebelastning: 20 % – Ulempbelastning: 15 % – Ansattpreferanse: 25 %
> 2. **Ulempbelastning** – Hverdager kl. 06–18: 0 poeng/time – Hverdager kl. 18–22: 1 poeng/time – Helg kl. 06–22: 2 poeng/time – Natt kl. 22–06: 3 poeng/time – Hver time telles kun én gang. – Måleperioden er fire uker bakover fra den ledige vaktens starttidspunkt.
> 3. **Poengberegning** – Vi bruker en fast skala fra 0 til 100. – Foreløpig tak settes til 300 ulempoeng. – Taket skal være konfigurerbart, slik at det enkelt kan justeres senere. – Ulempescore = maks(0, 100 × (1 − ulempoeng / 300)). – Kandidater med lik ulempbelastning får lik score.
> 4. **Visning** – Timebelastning og ulempbelastning vises separat. – Ulempbelastningen skal vises med samlet poengsum og fordeling på kveld, helg og natt. – Vi beholder 90 %-grensen som visuell indikator for høy timebelastning.
> 5. **Testdata** – Vi ønsker fire ukers vakthistorikk. – Dette må koordineres med story 1.2, slik at vi unngår unødvendige endringer i datamodellen senere.
>
> **Neste steg:** Lag et konkret forslag til hvilke endringer som må gjøres i PRD, epics.md og eventuelle andre relevante dokumenter. Skill mellom det som allerede er besluttet i prosjektet, og de nye forslagene knyttet til ulempbelastning. Vurder også om dette bør registreres som en egen story, siden det innebærer ny funksjonalitet. Ikke endre noen filer ennå. Jeg vil først se gjennom forslaget og avklare eventuelle konsekvenser for de andre på gruppen.

> Jeg ønsker nå å ferdigstille dokumentasjonen for ÅB-3 og ulempbelastning, basert på modellen vi har kommet frem til.
> Opprett Story 4.7 og oppdater relevante krav og dokumenter i tråd med endringsforslaget ditt.
> Vi beholder den eksisterende hovedvektingen, men deler arbeidsbelastningens 35 % i 20 % timebelastning og 15 % ulempbelastning.
> Bruk den foreslåtte ulempemodellen med fire ukers måleperiode, fast poengskala og konfigurerbart tak på 300 ulempoeng.
>
> Dokumenter avhengighetene til Story 1.2, 4.4, 4.5 og 4.6 tydelig.
>
> Ikke endre selve testdataene eller implementer programkode nå. Det skal gjøres i de respektive storyene.

Økten 02.11 startet med:

> Vi har nå avklart de åpne punktene i ab-3-ulempbelastning og jeg skal ferdigstille den.

Avklaringene ble gitt som svar på spørsmål fra agenten: vakttidene skal være som i
mockupene (kveld 15–23, natt 23–07), helligdager regnes som vanlige ukedager, det
skal lages KI-logg med skriptet sjekket inn, og hele gruppa godkjente modellen
2026-11-02.

## Hva modellen leverte

- **Vurdering før endring (30.10).** Agenten fant at det første forslaget
  (40/35/25 for time/ulempe/kostnad) ville fjerne Ansattpreferanse, som er vedtatt i
  ÅB-1. Brukeren valgte i stedet å dele arbeidsbelastningens 35 % i 20 og 15.
  Agenten anbefalte fast skala fremfor min–maks, fordi min–maks gjør små forskjeller
  maksimale og lar rangeringen snu når en ny kandidat legges til (jf. research
  2026-10-26).
- **Tallgrunnlag for taket.** Et skript regnet ut Ulempepoeng over fire uker for ni
  turnusprofiler og sammenlignet tak på 240, 300 og 432. Skriptet ble bare kjørt i
  terminalen og ble ikke lagret.
- **Dokumentendringer (commit `b7f793d`).** PRD §3, §4.3, §4.4, FR-8, ny FR-14,
  §8 og §9. `epics.md` med ny story 4.7 og endringer i story 1.2, 1.5, 4.1–4.6, 5.3
  og 5.7, UX-DR28, `sprint-status.yaml`, arkitektur, DESIGN.md, EXPERIENCE.md og
  brief. Videre rettet ukedagene i mockupene, som fulgte 2025-kalenderen.

## Hva som ble rettet, og hvorfor

Funnene kommer fra Mithad Kuduz' gjennomgang av PR #4 (30.10) og fra gruppas
avklaringer. Rettet 02.11:

- **Regneeksempelet gikk ikke opp.** UX-DR28, story 4.7 og DESIGN.md viste «136 p»
  med «kveld 22 t · helg 21 t · natt 29 t», men 22 + 2 × 21 + 3 × 29 = 151.
  Fordelingen hører ikke til noen av profilene i skriptet, og agenten kontrollerte
  ikke at den summerte til poengene. Byttet til profil E, regnet med skriptet:
  182 p = kveld 16 t · helg 32 t · natt 34 t (16 + 64 + 102).
- **Vakttidene var en antagelse som ikke stemte med mockupene.** Agenten skrev inn
  dag 07–15, kveld 15–22:30 og natt 22–07:30 i story 1.2 som `[ASSUMPTION]`, mens
  mockupene og story 1.5 bruker 15–23 og 23–07. Agentens tider ga ulike vaktlengder
  (8, 7,5 og 9,5 t) og overlappende vaktskifter. Gruppa valgte mockup-tidene.
  Story 1.2 og testlisten i story 4.7 er rettet.
- **Tallgrunnlaget kunne ikke etterprøves.** Skriptet var ikke sjekket inn. Det ble
  hentet fram fra økttranskriptet, ryddet og lagt i
  `scripts/ulempe_regneeksempler.py`, med valg for både de gamle og de nye
  vakttidene.
- **Taket regnet om.** Med de nye tidene gir profilene 0, 79, 108, 135, 182, 248
  og 323 poeng (før: 0, 69, 96, 136, 187, 262, 372). Taket på 300 står seg: tak 432
  klemmer de vanlige turnusene B–E sammen i 58–82, og tak 240 gir både natt-tung og
  fast natt score 0. PRD §4.3 sier nå at 432 ikke er et teoretisk maksimum, fordi
  overtid er tillatt, og at faste nattevakter bevisst får score 0.
- **ÅB-3 sto som løst før gruppa hadde godkjent.** Godkjenningen 2026-11-02 står nå
  i ÅB-3, arkitekturen, PRD §8 og `sprint-status.yaml`. Helligdagsantakelsen er
  fjernet fra PRD §4.3, §9 og story 4.7.

Ikke rettet her: Mithads punkter om målbare krav til testdataene i story 1.2
(«nesten like», historikkstart, periodegrense) og punktene under «Bør avklares»
(sommertid i «28 døgn», avrunding, min–maks som deler på null, poeng per faktor i
`RangertKandidat`). De hører til story 1.2 og 4.4–4.7.

## Kvalitetssikring

- `python scripts/ulempe_regneeksempler.py --vakttider 2026-10-30` gjenskaper alle
  sju tallene som PRD-memlogen oppga 30.10. Det viser at omregningen bruker samme
  modell og profiler.
- Skriptet kontrollerer for hver profil at kveldstimer × 1 + helgetimer × 2 +
  nattetimer × 3 er lik Ulempepoengene (PRD §4.3). Feilen i 136-eksempelet ville
  blitt fanget av samme kontroll.
- Søk i planleggingsdokumentene etter `22:30`, `07:30`, `136 p`, `50–190` og
  `250–370` gir bare den bevisste henvisningen i `sprint-status.yaml` til
  spesifikasjonen for story 1.2, som må rettes.
- `sprint-status.yaml` er kontrollert som gyldig YAML, og `git diff --check` er
  uten funn.
- Ingen programkode eller tester for ulempemodellen finnes ennå. Grensetilfellene
  er spesifisert i story 4.7 og må testes der.
- Gjenstår: spesifikasjonen for story 1.2 på `story-1.2-fiktiv-turnus` bruker
  fortsatt 22:00–07:30 og må rettes sammen med fasiten for #4127 og #4189.
