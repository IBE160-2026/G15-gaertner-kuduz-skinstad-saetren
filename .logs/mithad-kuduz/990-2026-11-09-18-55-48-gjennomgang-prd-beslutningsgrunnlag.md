# Gjennomgang av beslutningsgrunnlaget for PRD

## 2026-11-09 kl. 18:55 — Mithad Kuduz

### Oppgave

Kim ba Mithad gå gjennom `docs/beslutninger/prd-beslutningsgrunnlag-2026-11-07.md` og fylle inn synspunktene sine før møtet.

### Plan

- Gå gjennom punktene i bolker, med de andres synspunkter og et forslag for hvert punkt.
- Skrive bare i Mithads felt, slik dokumentet ber om, og hente fra GitHub før det skrives.

### Resultat

- **P-01 til P-04** er fylt inn etter forslaget Mithad godtok (`820883e`):
  - P-01: støtter anbefalingen. A stemmer med fasiten for #4127 i story 1.2.
  - P-02 og P-03: støtter anbefalingen.
  - P-04: støtter A, men testdataene fra 1.2 forutsatte at Ingrid med 32 t (89 %) har høy belastning. Med grensen 32,4 t må Ingrid få flere timer, eller så velges B. Tallene er kontrollert mot spesifikasjonen for 1.2.
- **P-05 til P-07** (`481393b`): Mithad støtter anbefalingene, også Johannes' presisering om at reserveteksten må merkes. Valgfri sammenligning venter til etter v1. Verdien 50 som nøytral preferanse er kontrollert mot regneeksempelet for #4127.
- **P-08 til P-11** (`344a2eb`): Mithad støtter anbefalingene.
  - P-08: et synlig unntak for KS-04 i demoen.
  - P-10: B som mulig tillegg i v1, med egen story.
  - P-11: innleie nevnes i teksten, men det kommer ingen knapp.
- **P-12, P-13 og E-01** (`30de77e`): Mithad støtter anbefalingene. P-13 viser til kontrollen av story 1.5 på 360 px.
- **E-02** (`30de77e`): Mithad er uenig med de tre andre i å lukke punktet. Sensorveiledningen (linje 59 og 141) sier at sensor leser den godkjente proposalen og kontrollerer at avvik er begrunnet.
- Alle 15 feltene til Mithad er fylt ut, og ingen andres felt er endret. Commitene er ikke pushet.

### Åpne punkter

- Velger gruppa P-04 A, må testdataene for Ingrid i story 1.2 endres.
- E-02: finn den innleverte proposalen og lag en kort liste over avvik med begrunnelse før innlevering, hvis gruppa er enig.

## 2026-11-10 — Mithad Kuduz

### Oppgave

Etter pull: Kim har ferdigstilt beslutningsgrunnlaget og bekreftet P-01 til P-13 som gruppevedtak 2026-11-09. Mithad ba om å rette spesifikasjonen for story 1.2 etter P-04.

### Plan

- Lese Kims følgevalg for P-04 og E-02.
- Søke etter forventninger om høy belastning for Ingrid i spesifikasjonen, planene og testene.

### Resultat

- **P-04:** Kim avklarte at Ingrid beholder 32 t i testdataene, og at forventningen rettes. Linje 186 i spesifikasjonen for 1.2 sier nå at Ingrid *ikke* skal vises med høy belastning (grense minst 32,4 t), med lenke til vedtaket og en merknad om hva som stod før (`967274e`). Ingen test i backend eller frontend forventet høy belastning. Testdata og fasit er uendret.
- **E-02:** Kim fant den første versjonen av briefen (`ee6d798`) og bekreftet at det var den godkjente proposalen. Han har også ført inn en liste over avvik. Det var det Mithad ba om.
- **Ikke rettet, utenfor oppgaven:** PRD §8 punkt 6 og K-02 i `avklaringspunkter.md` sier fortsatt at 32,4 t ikke er vedtatt. Ifølge beslutningsgrunnlaget skal vedtakene føres inn og samordnes senere.
- **Story 1.6:** Kim godkjente PR #11 selv. Ingen andre i gruppa har sett over koden.

### Åpne punkter

- Ingen nye for Mithad. Samordningen av vedtakene med PRD, K-02 og stories ligger hos gruppa, ifølge beslutningsgrunnlaget.
