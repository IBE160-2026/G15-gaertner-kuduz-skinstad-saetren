# PRD-beslutningsgrunnlag: synspunkter fra gruppen

## 2026-11-08 kl. 11:08 — johagartnerHiMolde

### Oppgave
Få en gjennomgang av Kims PRD-review og resultatene av den. Deretter: Johannes har skrevet synspunktene sine under hvert punkt i [beslutningsgrunnlaget](../../docs/beslutninger/prd-beslutningsgrunnlag-2026-11-07.md). Dokumentet skal også gi de andre i gruppa mulighet til å skrive sine synspunkter før punktene behandles.

### Plan
- Leste Kims logg [995-…-prd-review.md](../kimsk81/995-2026-10-31-19-18-05-prd-review.md), `issues.md`, beslutningsgrunnlaget og `review-rubric-2026-11-07.md` fra `origin/main`. Lokal branch `story-1.3-innlogging` var bak, så arbeidet fra 07.11 lå ikke i arbeidstreet. Byttet til `main` og hentet 34 commits som fast-forward.
- Kommentarene til Johannes sto bak feltet «Gruppens beslutning» (P-01–P-13) og som egne linjer under E-01/E-02. Med et lite Python-skript ble de flyttet til en ny liste, «Synspunkter før møtet», under hvert punkt. Listen har felt for Johannes, Kim, Mithad og Ragnhild, som er deltakerne i [referatet](../../docs/beslutninger/avklaringspunkter.md). Ordlyden er ikke endret. Beslutningsfeltene står igjen tomme.
- Avsnitt 1 har fått en kort instruks: hver skriver i sitt eget felt, synspunkter er ikke vedtak, og man kjører `git pull` før man skriver.

### Resultat
- 15 punkter er omformet (P-01–P-13, E-01, E-02), med 107 nye linjer og ingen fjernede. `git diff --check` er ren. Hver av de andre har 15 ledige felt. Committet i `2d411f1` på `main`. Ingen gruppevedtak er registrert, og PRD er ikke endret.
- Johannes støtter alle anbefalingene. Tilleggskommentarer: P-06 (synlig for turnusansvarlig når reserveteksten brukes), P-07 (sammenligning av valgte kandidater på forespørsel), P-08 (godta synlig avgrenset unntak for KS-04-periodekanten), P-10 og P-12 (B som stretch-goal), P-11 (si i teksten når innleie er eneste lovlige løsning), E-01 og E-02 (kan lukkes).
- Ting som ble flagget til drøfting, uten at dokumentet ble endret:
  - P-06 sier «når KI har gjort en beregning». Etter policyen beregner ikke KI, så det menes trolig en forklaring som ikke besto faktakontrollen.
  - P-07 er ny funksjonalitet som krever egen story. Den gir også flere KI-kall, og kontoen har en grense på 20 kall per minutt.
  - P-11 om innleie kan være i strid med anbefalingen om ikke å påstå at ingen i virkeligheten kan ta vakten, og appen har ingen data om eksterne vikarer.
  - E-01 krever ifølge dokumentet kilde og dato. En uttalelse i forelesning bør føres med dato før punktet lukkes.

### Åpne punkter
- Kim, Mithad og Ragnhild skal skrive synspunktene sine i beslutningsgrunnlaget, og gruppa skal deretter behandle P-01–P-13 og E-01/E-02.
- E-01: Før inn hvilken forelesning og dato faglærers uttalelse om KI i produktet kom fra, før punktet lukkes.
