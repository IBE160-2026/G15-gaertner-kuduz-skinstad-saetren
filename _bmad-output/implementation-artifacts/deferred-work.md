- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md`
  summary: Ingen test binder frontendens `FEILTEKSTER` i `frontend/src/tekster.ts` til feilkodene fra backend (`MELDINGER` i `backend/adaptere/api/main.py`), og ingen test viser at 401 fra `/api/meg` ikke gir melding.
  evidence: Verification Gap 2026-11-07: en skrivefeil i en nøkkel, for eksempel `feil_inlogging`, består `npm run build` og alle pytest-testene og gir reserveteksten ved feil passord. Story 1.3 utelukker frontendtester i Never-lista. Ta det opp når frontend får testverktøy, senest i story 1.4.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Feil-, prøv-igjen- og 401-tilstandene i Vaktvalg har ingen automatisk test, og feiltilstanden er ikke kontrollert i nettleser."
  evidence: Frontend har ingen testrigg for komponenter (bare Node-tester av rene funksjoner). Det ville vært medium, men er ikke verifisert. Avgjøres av en komponenttest (for eksempel med jsdom) eller en manuell kontroll der `/api/vaktoversikt` feiler mens `/api/meg` svarer. Løst: `frontend/tester/komponenter/vaktvalg.test.tsx` (feil og «Prøv igjen») og `frontend/tester/komponenter/app.test.tsx` (401 fra `/api/vaktoversikt` etter `/api/meg` 200 viser innloggingen med `sesjonUtlopt`). Mutasjonene M1 og M2 i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: Innledningen og «Kjøring og verifisering» i AGENTS.md nevner ikke vaktoversikten fra 1.5 eller `npm run test`.
  evidence: AGENTS.md er agentkontekst. Etter AV-08 endres den med registrering i §11 eller i egen PR, ikke som en del av denne storien. Delvis løst 2026-11-14: `npm run test` står nå i «Kjøring og verifisering» i AGENTS.md, med både `node --test` og komponenttestene (OP-16, branchen `frontend-komponenttester`). Delen om vaktoversikten fra 1.5 i innledningen er fortsatt åpen.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Frontend har ingen komponenttestrigg, så gjengivelsen av tilstandene og «Prøv igjen» i `Kandidatliste` testes ikke automatisk."
  evidence: Verification-gap 2026-11-11. `frontend/tester/kandidater.test.mjs` tester bare logikken i `src/kandidater.ts`. Fjernes `forsok` fra avhengighetene i `useEffect`, er alle tester fortsatt grønne. Komponenten dekkes bare av den manuelle nettleserkontrollen. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` (feil, «Prøv igjen» og datafeil). Mutasjonene M3 (`forsok` fjernet fra deps) og M3b i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.
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

- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Koblingen i komponentene på godkjenningsflaten er bare kontrollert manuelt: at «Velg» sender riktig id, at ruten i App viser flaten, at «Godkjenn erstatning» ikke gjør noe kall, at datafeil og 404 ikke viser knapper for godkjenning, og at «Avbryt» går tilbake."
  evidence: Verification Gap 2026-11-12. Ingen test rendrer `App`, `Kandidatflate` eller `Godkjenningsflate`, fordi det ikke finnes noen komponentrigg (se punktet fra 2.1 over). Nettleserkontrollen er reserveløsningen til det finnes en rigg. Story 3.2 bytter ut handleren for «Godkjenn erstatning» og bør få en rendret test for den. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` («Velg»), `app.test.tsx` (ruten) og `godkjenningsflate.test.tsx` (Godkjenn, Avbryt, datafeil og 404). Mutasjonene M6–M9b i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester. Testen for «Godkjenn erstatning» må endres i story 3.2, når knappen skal gjøre et kall.

- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-velge-kandidat-og-se-godkjenningsflaten.md`
  summary: Leddene i brødsmulestien er ikke lenker, så «Kandidater» og «Vakt #<nr>» på godkjenningsflaten kan ikke brukes til å gå tilbake.
  evidence: Blind Hunter 2026-11-12. `Brodsmulesti.tsx` har bare `{tekst, uthevet}` fra story 1.6. EXPERIENCE.md sier at flatene «henger sammen via brødsmulesti fremfor global navigasjon». Fantes før 3.1. Lenken «Tilbake til kandidatlisten» og «Avbryt» dekker behovet på godkjenningsflaten foreløpig.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Ingen frontendtest rendrer `Kandidatliste`, så grenen for tom liste (beslutning B) og de andre tilstandene er bare dekket av tester på tekstene og kildeteksten."
  evidence: Verification-gap 2026-11-12. `frontend/tester/kandidater-bunt.ts` bunter bare `src/kandidater` og `src/api`. En snudd betingelse (`!== 0`) ville gått gjennom alle 28 testene. Inntil videre dekker den manuelle nettleserkontrollen dette. Bør løses senest i 2.6, som erstatter grenen med tomtilstanden. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` (tom liste). Mutasjonen M4 (`=== 0` blir `!== 0`) i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga rød test. Story 2.6 må oppdatere testen når tomtilstanden erstatter teksten.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-filtrere-pa-35-timersregelen-ukentlig-fri.md`
  summary: AGENTS.md sier at domenekjernen har «den første harde regelen (kompetanse-minstekrav) fra story 2.1», men etter 2.4 er alle fire harde regler på plass.
  evidence: Blind-hunter 2026-11-12. AGENTS.md er agentkontekst for hele gruppa og oppdateres utenom storyen.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-5-ekskludert-boks-med-oppsummering-av-utelukkelser.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] To rader i grensetabellen for Ekskludert-boksen hadde ingen automatisk test: ingen boks ved 0 utelukkede, og «Vis full liste» lukket → åpen → lukket med `aria-expanded`."
  evidence: Review Triage Log i spesifikasjonen for 2.5 avviste funnet fordi prosjektet ikke hadde komponenttestrigg, og radene ble dekket av nettleserkontroll 2026-11-13. Ført her 2026-11-14 for å samle de utsatte punktene. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` (Ekskludert-boksen). Mutasjonene M5 (`totalt === 0`-sjekken fjernet) og M5b (`aria-expanded` alltid false) i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.

- source_spec: `_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md`
  summary: Vite 8.3.1 har en høy sårbarhet i `npm audit`, rettet i 8.3.8, og er ikke oppgradert.
  evidence: Blind-hunter 2026-11-14. Sårbarheten fantes før komponenttestene og gjelder utviklingsserveren. Oppgraderingen endrer en eksakt låst avhengighet for hele gruppa og bør tas i egen endring med `npm run build` og `npm run test` på Node 22.12.

- source_spec: `_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md`
  summary: AGENTS.md sier «P-13 én gang (OP-16)», men OP-16 avgjorde ikke P-13. Henvisningen bør peke på P-13 i §12 i avklaringspunktene.
  evidence: Blind-hunter 2026-11-14. Linjen ble lagt inn i AGENTS.md med OP-16, men P-13 er vedtatt i §12 og har ingen frist (avklaringspunktene l.783). AGENTS.md er agentkontekst, så rettingen avgjøres i PR-gjennomgangen.
