- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md`
  summary: Ingen test binder frontendens `FEILTEKSTER` i `frontend/src/tekster.ts` til feilkodene fra backend (`MELDINGER` i `backend/adaptere/api/main.py`), og ingen test viser at 401 fra `/api/meg` ikke gir melding.
  evidence: Verification Gap 2026-11-07: en skrivefeil i en nøkkel, for eksempel `feil_inlogging`, består `npm run build` og alle pytest-testene og gir reserveteksten ved feil passord. Story 1.3 utelukker frontendtester i Never-lista. Ta det opp når frontend får testverktøy, senest i story 1.4.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: Feil-, prøv-igjen- og 401-tilstandene i Vaktvalg har ingen automatisk test, og feiltilstanden er ikke kontrollert i nettleser.
  evidence: Frontend har ingen testrigg for komponenter (bare Node-tester av rene funksjoner). Det ville vært medium, men er ikke verifisert. Avgjøres av en komponenttest (for eksempel med jsdom) eller en manuell kontroll der `/api/vaktoversikt` feiler mens `/api/meg` svarer.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: Innledningen og «Kjøring og verifisering» i AGENTS.md nevner ikke vaktoversikten fra 1.5 eller `npm run test`.
  evidence: AGENTS.md er agentkontekst. Etter AV-08 endres den med registrering i §11 eller i egen PR, ikke som en del av denne storien.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md`
  summary: Frontend har ingen komponenttestrigg, så gjengivelsen av tilstandene og «Prøv igjen» i `Kandidatliste` testes ikke automatisk.
  evidence: Verification-gap 2026-11-11. `frontend/tester/kandidater.test.mjs` tester bare logikken i `src/kandidater.ts`. Fjernes `forsok` fra avhengighetene i `useEffect`, er alle tester fortsatt grønne. Komponenten dekkes bare av den manuelle nettleserkontrollen.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md`
  summary: AGENTS.md sier fortsatt «ingen domenelogikk ennå» og nevner ikke `tester/regelmotor/` eller arkitekturtesten med import-linter.
  evidence: Blind-hunter 2026-11-11. Story 2.1 legger inn `backend/domene/` med regelmotor. Rettingen gjelder en agentkontekstfil (AV-08) og krever et valg fra et gruppemedlem.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md`
  summary: AGENTS.md sier at regelmotoren har «den første harde regelen (kompetanse-minstekrav) fra story 2.1», men etter story 2.2 er det to regler.
  evidence: Blind-hunter 2026-11-11. `domene/regelmotor/kolliderende_vakt.py` og `REGLER` har to regler. Rettingen gjelder en agentkontekstfil og rutes derfor til utsatt arbeid.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md`
  summary: Når reglene kjøres på nytt ved Godkjenning (story 3.2), må Vaktens egen rad holdes utenfor Kandidatens `vakter`, ellers kolliderer den godkjente med sin egen vakt.
  evidence: Edge-case-hunter (Opus) 2026-11-11. `hent_kandidatgrunnlag` henter alle rader med `tildelt_ansatt_id`, og i dag kan Vakten ikke ha det, fordi `finn_ubemannet_vakt` krever `mangler_bemanning`. Filtrer på `VaktRad.id != vaktrad.id` når kontrollen bygges.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md`
  summary: "[UTFØRT i story 2.3, 2026-11-11] Story 2.3 bygger vinduet per regel og avgrenser datafeilsjekken for Kandidatens vakter til vakter innenfor vinduet (vedtak A5, alternativ B)."
  evidence: Vedtatt av Johannes på vegne av gruppa 2026-11-11 (avklaringspunktene, §11, og P-08). Før story 2.3 ga én ugyldig tildelt vakt hvor som helst datafeil for alle kandidatlister (`kollisjonsdatafeil` validerte alle `Kandidat.vakter`, og `hent_kandidatgrunnlag` henter alle tildelte vakter). Story 2.3 implementerte vinduet, og bare vakter i vinduet valideres nå. Utført: `Regel.vindu` og `kandidatvaktdatafeil` i `domene/regelmotor/vurdering.py`, `kollisjonsdatafeil` fjernet, grensetester i `tester/regelmotor/test_11_timersregelen.py` og API-testen `test_tildelt_vakt_med_start_ikke_før_slutt_langt_unna_ignoreres`.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-filtrere-pa-11-timersregelen-daglig-hvile.md`
  summary: epics.md sier fortsatt «Grensetester i story 2.3 gjenstår» (ÅB-5, l.116) og «Grensetester gjenstår» i AV-04-sitatet i Story 2.3 (l.~502). Story 2.3 har levert grensetestene.
  evidence: Blind-hunter 2026-11-11. Endring i planleggingsdokumentet gjør `epic-2-context.md` ugyldig før 2.4 og hører til gruppas samordning av epics.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md`
  summary: Ingen frontendtest rendrer `Kandidatliste`, så grenen for tom liste (beslutning B) og de andre tilstandene er bare dekket av tester på tekstene og kildeteksten.
  evidence: Verification-gap 2026-11-12. `frontend/tester/kandidater-bunt.ts` bunter bare `src/kandidater` og `src/api`. En snudd betingelse (`!== 0`) ville gått gjennom alle 28 testene. Inntil videre dekker den manuelle nettleserkontrollen dette. Bør løses senest i 2.6, som erstatter grenen med tomtilstanden.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md`
  summary: AGENTS.md sier at domenekjernen har «den første harde regelen (kompetanse-minstekrav) fra story 2.1», men etter 2.4 er alle fire harde regler på plass.
  evidence: Blind-hunter 2026-11-12. AGENTS.md er agentkontekst for hele gruppa og oppdateres utenom storyen.
