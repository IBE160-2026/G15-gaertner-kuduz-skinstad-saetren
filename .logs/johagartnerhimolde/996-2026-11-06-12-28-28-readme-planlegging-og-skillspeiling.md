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

**Oppfølging kl. 12:54 – test, CI og forslag til nye regler (branch `ci-skills-speiling`):**
- **Avgjort av brukeren:** Kontrollen skulle være enkel og automatisk. Løsningen er en `unittest` som GitHub Actions kjører ved hver push. Testen bruker ingen modellkall eller tokens. Repoet er offentlig, så kjøringene er gratis.
- **Kode og CI (`f42a253`):**
  - `scripts/test_skills_speiling.py` inneholder tre tester:
    - de sporede filene er de samme i begge mappene
    - innholdet er likt, med CRLF ignorert
    - unntaket `sesjonslogg` er fortsatt en henvisning
  - `.github/workflows/skills-speiling.yml` kjører testene.
  - I AGENTS.md er TODO-en om CI erstattet, og tallet «214» er fjernet.
  - Forslaget til ny ordlyd i andre del av AV-08: endringer i AGENTS.md og loggreglene tillates når de registreres i §11 og, i en branch, godkjennes i PR-en.
- **Forslag til ny regel for branch og PR (`7792fcf`), fra brukeren:**
  - Branch og PR er et aktivt valg den enkelte tar, ut fra størrelse og hvor mange definerende avgjørelser arbeidet inneholder.
  - Avgrensede endringer kan gå rett på `main`.
  - Agenter oppretter ikke branch eller PR på egen hånd.
  - Kvalitetssikringen skal kunne spores uansett vei.
  - Forslaget er registrert i §11.
- **KI-logg:** `docs/ki-logg/2026-11-06-skills-speiling.md`.
- **Verifisert:**
  - Lokalt ga de 3 testene OK, og hele `scripts/` ga 67 OK.
  - Tre brudd som ble laget med vilje, ble fanget opp av hver sin test og fjernet igjen etterpå.
  - CI på GitHub er ikke kjørt ennå.
- **Ikke pushet:** GitHub avviste branchen fordi `gh`-tokenet mangler tilgangen `workflow`. Det løses med `gh auth refresh -h github.com -s workflow`, som brukeren må kjøre selv.
- Branchen er rebaset på `origin/main` før den er pushet, så PR-en får bare disse to commitene.

**Oppfølging kl. 13:00 – CI og PR:**
- Brukeren ga `gh` tilgangen `workflow`.
- Det første CI-kjøret ([42214162167](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/actions/runs/42214162167)) på `5f6c31c` var grønt. De 3 testene ga OK, og kjøret tok 7 s.
- Resultatet er ført i KI-loggen.
- [PR #6](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/6) er åpnet mot `main`. Beskrivelsen markerer AV-08 og regelen for branch og PR som forslag som gruppa må godkjenne.

### Åpne punkter
- Gruppa gjennomgår og godkjenner PR #6. Det er da den nye ordlyden i AV-08 og den nye regelen for branch og PR blir vedtatt.

## 2026-11-08 kl. 12:14 — johagartnerHiMolde

### Oppgave
Gå gjennom tilbakemeldingene på PR #6 og løse konfliktene med `main` som Mithad ba om, slik at PR-en kunne merges. Etterpå registrere forslagene i PR-en som vedtatt og lukke punktet om godkjenning i `issues.md`. Til slutt pushe, slette branchen og vurdere ulempene ved Mithads forslag om å la CI også kjøre `pytest`.

### Plan
- Lese gjennomgangen med `gh pr view 6` og kontrollere med `git merge-tree` hvilke filer som har konflikter.
- Merge `main` inn i `ci-skills-speiling`, løse konfliktene, kjøre testene og pushe. Brukeren merget PR-en selv.
- Føre vedtaket inn i AV-08 og §11 i `avklaringspunkter.md`.
- Vurdere `pytest` i CI med `bmad-advanced-elicitation`: pre-mortem, red team og feilmodusanalyse, bygd på workflowen, `requirements*.txt`, testene og `--durations`.

### Resultat
- Tilbakemeldingen: Mithad Kuduz godkjente PR #6 2026-11-08, og godkjenningen gjaldt begge forslagene. Kravet hans var at konfliktene med `main` ble løst før merge. Forslag til senere: la CI også kjøre `pytest`.
- Konfliktene ble løst i merge-commit `a2a79b1` på branchen:
  - `AGENTS.md`: kjørestegene for backend og frontend er tatt fra `main` (story 1.3), og TODO-en om CI er erstattet med branchens CI-avsnitt. Policy var ikke endret på `main`.
  - `avklaringspunkter.md`: oppføringen om speilingen står først i §11, foran AV-13/AV-14/OP-10 fra samme dag.
  - `issues.md`: punktet om speilingen er tatt fra branchen, der det var løst. Resten kommer fra `main`.
- Kontroll: 67 tester i `scripts/` og 112 i backend ga OK. CI-kjøringen 42474560746 var grønn. Brukeren merget PR-en med `gh pr merge 6 --merge` (`9939cfa`). Agenten fikk ikke merge selv, fordi tillatelsen ble avvist.
- `avklaringspunkter.md` (Sist oppdatert, oversiktstabellen og AV-08): forslaget er endret til «Endring vedtatt 2026-11-08». Oppføringen 2026-11-06 i §11 er markert som vedtatt. Den nye oppføringen «2026-11-08 – Godkjenning av PR #6» har med hvem, grunnlag, hva som er vedtatt og Mithads forslag om `pytest` i CI som ikke vedtatt.
- Lukket i `issues.md`: «Gruppa gjennomgår og godkjenner PR #6».
- Ikke endret: to historiske formuleringer i referatet sier fortsatt at loggreglene og agentinstruksjonene er uendret. Den ene står i tabellen over berørte områder («Ingen endring i loggregler (AV-08/K-05)»), den andre i merknaden om agentinstruksjoner etter forslaget til AGENTS-tekst. Begge er fra møtet 02.11 og er lest som historikk.
- Branchen `ci-skills-speiling` er slettet på origin og lokalt. Før sletting ble det kontrollert at den var helt merget inn i `main`.
- Vurderingen av `pytest` i CI:
  - Fakta: 112 tester tar 29–42 s lokalt. Ingen nettverkskall, ingen secrets og ingen bruk av `backend/turnushjelperen.db`. Det finnes `__pycache__` for både cpython-312 og cpython-315. `main` ser ikke ut til å ha branchebeskyttelse (API-et svarte 404).
  - Største fordel: CI blir den eneste kjøringen av backend på Linux etter OP-05.
  - Reelle risikoer: at Python-versjonen endrer seg, og at noen legger `OPENROUTER_API_KEY` inn i CI når story 5.1 kommer.
  - Brukeren påpekte at en ren 3.12-lås også er en risiko over tid. Forslaget ble derfor endret til en matrise med `3.12` (versjonen vi lover) og `3.x` (nyeste). Tidsbruken gjelder bare ved push og kjører ved siden av det man gjør.
  - Anbefalingen er ført i det åpne punktet i `issues.md`. Ingenting er implementert.

### Åpne punkter
- Vurder å la CI også kjøre backend-testene (`pytest`, 112 tester). Mithad foreslo det i gjennomgangen av PR #6. Anbefalingen står i `issues.md`.
- Slett branchen `ci-skills-speiling` på origin rundt 2026-11-15, en uke etter merge av PR #6, slik dere gjorde med story 1.2. (løst 2026-11-08: slettet etter brukerens ønske)
