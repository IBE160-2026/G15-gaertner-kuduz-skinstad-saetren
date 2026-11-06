# README-planleggingsgrunnlag og speiling av skills

## 2026-11-06 kl. 12:28 — johagartnerHiMolde

### Oppgave
README på GitHub lenket bare til briefen under «Planleggingsgrunnlag». Brukeren ville ha lagt til PRD-en og de andre planleggingsdokumentene. I tillegg skulle det undersøkes om `.agents/skills` (Codex) og `.claude/skills` (Claude Code) har fått forskjeller, og om ordningen som skal holde dem like, fortsatt virker.

### Plan
- Finne ut hvorfor avsnittet bare har briefen, og legge inn lenker med én linje per dokument.
- Sammenligne de to skill-treene fil for fil uten å ta hensyn til linjeskift, og lete etter hooks, CI eller tester som håndhever speilingen.

### Resultat
- **README (`cc61d96`):** lenker til PRD, UX (DESIGN og EXPERIENCE), arkitektur, epics med sprintstatus og beslutningsreferatet. Avsnittet kom inn i `1822b41` (12.10), da briefen ble samlet på ett sted. PRD, UX, arkitektur og epics fantes da, men ble aldri lagt inn. Alle lenkene i README er sjekket mot filer som finnes.
- **Speilingen:**
  - Begge trærne har 216 sporede filer og de samme stiene.
  - Med CRLF ignorert er 215 filer identiske. Den eneste som avviker, er `sesjonslogg/SKILL.md`, og det er det dokumenterte unntaket i AGENTS.md.
  - Ingen utrackede eller ignorerte filer i noen av mappene.
- **Commits som bare endret det ene treet:** de to første innleggene (`2b3a59b` og `c424956`, 17.09) og sesjonslogg-arbeidet (`592b8c3`, `0056ee4` og `b85d75f`). Alt annet er speilet i samme commit.
- **Ordningen:** speilingen hviler bare på en skriftlig regel i AGENTS.md, under «Konvensjoner som avviker fra standard». Ingen hook, CI eller test håndhever den. Det finnes verken `.github/`, `core.hooksPath` eller aktive hooks i `.git/hooks`. Regelen er fulgt så langt, men brudd blir ikke fanget opp automatisk.
- **Utdatert tall:** fallgruven i AGENTS.md sier «alle 214 identiske filer» (fra `7e70b89`, 23.09). Nå er det 215 identiske av 216. Tallet er ikke endret, fordi det berører AGENTS.md (AV-08).
- **Linjeskift:** `.agents` har CRLF i alle 216 filene. `.claude` har LF i 214 og CRLF i 2. Det gjelder bare arbeidstreet, siden indeksen har LF.

### Åpne punkter
- Avgjør om speilingen skal kontrolleres automatisk, for eksempel med en `unittest` som sammenligner trærne med CRLF ignorert og med `sesjonslogg` som unntak. Avgjør også om tallet 214 i AGENTS.md skal rettes eller fjernes (AV-08).
