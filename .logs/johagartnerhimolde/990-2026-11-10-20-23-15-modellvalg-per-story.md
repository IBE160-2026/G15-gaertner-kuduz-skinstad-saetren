# Modellvalg per story

## 2026-11-10 kl. 20:23 — johagartnerHiMolde

### Oppgave
Johannes ville at anbefalingen om Opus 5.5 eller Sonnet 5.5 per story skulle komme automatisk når en story bygges. Målet er å spare 5-timersgrensen uten å svekke kvalitetssikringen der feil er dyre.

### Plan
- Gikk gjennom `bmad-build` med `bmad-customize`. Fant at `persistent_facts` og `activation_steps_append` passer, og at det ikke fantes noen overstyring for gruppa fra før.
- Skrev tabellen i et eget dokument, slik at det er lett å lese og endre, og lot overstyringen lese dokumentet.
- Johannes valgte å legge endringen rett på `main`. Det ble ikke laget branch eller PR.

### Resultat
- `docs/modellvalg-stories.md`: regel og tabell for de 23 storiene i Epic 2–5 og samordningen, til sammen 24 rader. Det er 10 Opus, 4 Sonnet med gjennomgang av Opus og 10 Sonnet. Fordelingen jeg oppga i chatten, 12/4/13, var feiltelt. Dokumentet sier at anbefalingen ikke er drøftet i gruppa.
- `_bmad/custom/bmad-build.toml` (sporet):
  - Tabellen lastes inn som fast kontekst.
  - Før steg 01 sier `bmad-build` hvilken modell som er anbefalt og hvilken modell økten faktisk kjører på. Er de ulike, venter den på svar. Er de like, fortsetter den uten å spørre.
  - For stories med «Sonnet, gjennomgang med Opus» startes minst én gjennomgangsagent med Opus.
  - I Codex nevnes bare anbefalingen.
- Kontrollert:
  - `resolve_customization.py` gir de nye feltene for både `.claude/` og `.agents/`.
  - `render_skill.py` gir en `workflow.md` med tabellen og oppstartssteget.
- Committet i `4538d06`. AGENTS.md er ikke endret.

### Åpne punkter
- Gruppa godtar eller endrer modellanbefalingen i `docs/modellvalg-stories.md`. Den er Johannes' forslag og ikke drøftet i gruppa.
