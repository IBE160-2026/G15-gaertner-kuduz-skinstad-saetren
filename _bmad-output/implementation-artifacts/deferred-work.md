- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: `urllib_transport` skjuler årsaken til en nettverksfeil. `except` i `adaptere/ki/openrouter.py` gir `Nettverksfeil(type(feil).__name__)` uten kjede, og `OpenRouterKiAdapter.tolk` kaster den uten å logge. Brukeren og loggen ser bare `nettverk`, aldri for eksempel `CERTIFICATE_VERIFY_FAILED`.
  evidence: Live-kontroll 2026-11-16 på macOS (Python 3.15.2): første forsøk ga 3 av 3 `nettverk` etter 14 s, og årsaken ble funnet først ved å kjøre `urllib` for hånd. Midlertidig løsning er `SSL_CERT_FILE=/etc/ssl/cert.pem` (README). Dokumentasjonsendringen er gjort; å logge feiltypen på nivå WARNING er en kodeendring og er ikke gjort.
  status: Løst 2026-11-21. `nettverksårsak` gir typenavn og OpenSSL-koden (for eksempel `URLError/SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED`), aldri feilteksten, og `_send` logger hver nettverksfeil som WARNING. Tester i `tester/ki/test_openrouter.py`. Se [KI-loggen](../../docs/ki-logg/2026-11-21-sma-rettelser-openrouter.md).
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: Fremdriftsmeldingene fra `tolk_ventende` («N tekster venter», «tolket») er `logger.info`, og backend har ingen loggoppsett. Med `uvicorn adaptere.api.main:app` vises bare advarsler og feil, så ingen ser fremdriften i terminalen.
  evidence: Live-kontroll 2026-11-16: 19 tolkninger ga ingen linjer i terminalen, bare uvicorns egne. Fremdriften ble fulgt i databasen. README er rettet til å si at fremdriften ikke vises. Å vise den krever en kodeendring (loggoppsett eller `--log-level`-avklaring) og er ikke gjort.
  status: Løst 2026-11-23. `vis_applogg_i_terminalen` i `adaptere/api/main.py` gir loggeren `adaptere` én terminalhandler på INFO (`INFO:     …`), kalt før `ki_fra_miljo()`. Rot- og uvicorn-loggerne er urørt, og `caplog` fanger som før. Tester i `tester/api/test_terminallogg.py`, README rettet. Se [KI-loggen](../../docs/ki-logg/2026-11-23-loggoppsett-backend.md).
- source_spec: `_bmad-output/implementation-artifacts/spec-loggoppsett-backend.md`
  summary: `ARCHITECTURE-SPINE.md` sier at runtime-/driftslogging ikke er besluttet (Consistency Conventions, linje 116, og Deferred, linje 215), mens backend nå viser appens INFO-meldinger i terminalen.
  evidence: Valg C (Ragnhild 2026-11-23): endringen er behandlet som en feilretting innenfor det utsatte punktet, og spinen er ikke rørt. Spinen bør oppdateres ved neste arkitekturgjennomgang eller i retrospektiven for epic 5.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: Testdataene kan ikke vise at preferansepoeng endrer rekkefølgen. Bare #4127 har gyldige kandidater (fire), og marginene er så store at 25 % preferansevekt ikke snur dem. Jonas, Mette, Thomas og Ingrid står i samme rekkefølge før og etter tolkning.
  evidence: Live-kontroll 2026-11-16: scorene endret seg som regnet (+6,25, +6,25, −12,50, +12,50), rekkefølgen ikke. At poengene kan snu en rekkefølge dekkes bare av enhetstestene i `tester/regelmotor/test_rangering.py`.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: Kostnaden for live-kontrollen er ikke målt. Anslaget er ca. 1 øre for 22 kall (3 + 19), regnet fra USD 0,057 per 1000 tolkninger i `docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md`.
  evidence: Live-kontroll 2026-11-16. Faktisk forbruk står i OpenRouter-kontoen til gruppa og er ikke lest.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-innlogging-for-turnusansvarlig.md`
  summary: Ingen test binder frontendens `FEILTEKSTER` i `frontend/src/tekster.ts` til feilkodene fra backend (`MELDINGER` i `backend/adaptere/api/main.py`), og ingen test viser at 401 fra `/api/meg` ikke gir melding.
  evidence: Verification Gap 2026-11-07: en skrivefeil i en nøkkel, for eksempel `feil_inlogging`, består `npm run build` og alle pytest-testene og gir reserveteksten ved feil passord. Story 1.3 utelukker frontendtester i Never-lista. Ta det opp når frontend får testverktøy, senest i story 1.4.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Feil-, prøv-igjen- og 401-tilstandene i Vaktvalg har ingen automatisk test, og feiltilstanden er ikke kontrollert i nettleser."
  evidence: Frontend har ingen testrigg for komponenter (bare Node-tester av rene funksjoner). Det ville vært medium, men er ikke verifisert. Avgjøres av en komponenttest (for eksempel med jsdom) eller en manuell kontroll der `/api/vaktoversikt` feiler mens `/api/meg` svarer. Løst: `frontend/tester/komponenter/vaktvalg.test.tsx` (feil og «Prøv igjen») og `frontend/tester/komponenter/app.test.tsx` (401 fra `/api/vaktoversikt` etter `/api/meg` 200 viser innloggingen med `sesjonUtlopt`). Mutasjonene M1 og M2 i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-vaktoversikt-med-krever-handling.md`
  summary: "[LØST 2026-11-15, rettet i AGENTS.md] Innledningen og «Kjøring og verifisering» i AGENTS.md nevner ikke vaktoversikten fra 1.5 eller `npm run test`."
  evidence: AGENTS.md er agentkontekst. Etter AV-08 endres den med registrering i §11 eller i egen PR, ikke som en del av denne storien. Delvis løst 2026-11-14: `npm run test` står nå i «Kjøring og verifisering» i AGENTS.md, med både `node --test` og komponenttestene (OP-16, branchen `frontend-komponenttester`). Delen om vaktoversikten fra 1.5 i innledningen er fortsatt åpen. Løst 2026-11-15: innledningen nevner nå vaktoversikten og valg av vakt (faktarettelse ført i §11, AV-08).
- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] Frontend har ingen komponenttestrigg, så gjengivelsen av tilstandene og «Prøv igjen» i `Kandidatliste` testes ikke automatisk."
  evidence: Verification-gap 2026-11-11. `frontend/tester/kandidater.test.mjs` tester bare logikken i `src/kandidater.ts`. Fjernes `forsok` fra avhengighetene i `useEffect`, er alle tester fortsatt grønne. Komponenten dekkes bare av den manuelle nettleserkontrollen. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` (feil, «Prøv igjen» og datafeil). Mutasjonene M3 (`forsok` fjernet fra deps) og M3b i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-gyldige-kandidater-filtrert-pa-kompetanse-minstekrav.md`
  summary: "[LØST 2026-11-11, rettet i AGENTS.md] AGENTS.md sier fortsatt «ingen domenelogikk ennå» og nevner ikke `tester/regelmotor/` eller arkitekturtesten med import-linter."
  evidence: Blind-hunter 2026-11-11. Story 2.1 legger inn `backend/domene/` med regelmotor. Rettingen gjelder en agentkontekstfil (AV-08) og krever et valg fra et gruppemedlem. Løst: AGENTS.md ble rettet 2026-11-11 på oppdrag fra Johannes (§11, PR #13) og nevner nå domenekjernen, `tester/regelmotor/` og import-linter-kontrakten. Bekreftet 2026-11-15.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-filtrere-bort-kandidater-med-kolliderende-vakt.md`
  summary: "[LØST 2026-11-15, rettet i AGENTS.md] AGENTS.md sier at regelmotoren har «den første harde regelen (kompetanse-minstekrav) fra story 2.1», men etter story 2.2 er det to regler."
  evidence: Blind-hunter 2026-11-11. `domene/regelmotor/kolliderende_vakt.py` og `REGLER` har to regler. Rettingen gjelder en agentkontekstfil og rutes derfor til utsatt arbeid. Løst: innledningen i AGENTS.md beskriver nå alle fire harde regler (faktarettelse ført i §11 i avklaringspunktene, AV-08).

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
  summary: "[LØST 2026-11-15, rettet i AGENTS.md] AGENTS.md sier at domenekjernen har «den første harde regelen (kompetanse-minstekrav) fra story 2.1», men etter 2.4 er alle fire harde regler på plass."
  evidence: Blind-hunter 2026-11-12. AGENTS.md er agentkontekst for hele gruppa og oppdateres utenom storyen. Løst: innledningen i AGENTS.md beskriver nå alle fire harde regler (faktarettelse ført i §11 i avklaringspunktene, AV-08).

- source_spec: `_bmad-output/implementation-artifacts/spec-2-5-ekskludert-boks-med-oppsummering-av-utelukkelser.md`
  summary: "[LØST 2026-11-14, komponenttester (OP-16)] To rader i grensetabellen for Ekskludert-boksen hadde ingen automatisk test: ingen boks ved 0 utelukkede, og «Vis full liste» lukket → åpen → lukket med `aria-expanded`."
  evidence: Review Triage Log i spesifikasjonen for 2.5 avviste funnet fordi prosjektet ikke hadde komponenttestrigg, og radene ble dekket av nettleserkontroll 2026-11-13. Ført her 2026-11-14 for å samle de utsatte punktene. Løst: `frontend/tester/komponenter/kandidatflate.test.tsx` (Ekskludert-boksen). Mutasjonene M5 (`totalt === 0`-sjekken fjernet) og M5b (`aria-expanded` alltid false) i [KI-loggen](../../docs/ki-logg/2026-11-14-komponenttester.md) ga røde tester.

- source_spec: `_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md`
  summary: "[BEVISST VALGT BORT 2026-11-14, OP-16] Vite 8.3.1 har en høy sårbarhet i `npm audit`, rettet i 8.3.8, og er ikke oppgradert."
  evidence: Blind-hunter 2026-11-14. Sårbarheten fantes før komponenttestene og gjelder utviklingsserveren. Oppgraderingen endrer en eksakt låst avhengighet for hele gruppa og bør tas i egen endring med `npm run build` og `npm run test` på Node 22.12. Vurdert 2026-11-14: `npm audit` samler seks varsler (GHSA-587h-7wmj-h5pm, GHSA-698v-4r3x-3vcv, GHSA-r825-w8mm-5pxw, GHSA-9jrq-w75r-8gcw, GHSA-rq7h-c2jc-7f22 og GHSA-vfpm-58rq-9qcg). Alle gjelder bare utviklingsserveren, ikke `npm run build`. De som krever `--host`, et annet OS enn Windows eller `middlewareMode`, gjelder ikke oss. Det som gjenstår, er `launch-editor` på Windows, mens `npm run dev` kjører lokalt. Johannes valgte bevisst å ikke oppgradere, fordi risikoen er lav og serveren bare kjører lokalt (OP-16, §11). Tas opp igjen hvis serveren eksponeres med `--host`, eller hvis det kommer et nytt varsel.

- source_spec: `_bmad-output/implementation-artifacts/spec-frontend-komponenttester.md`
  summary: "[LØST 2026-11-14, PR #20] AGENTS.md sa «P-13 én gang (OP-16)», men OP-16 avgjorde ikke P-13."
  evidence: Blind-hunter 2026-11-14. P-13 er vedtatt i §12 i avklaringspunktene, ikke i OP-16. Rettet i PR-gjennomgangen: `AGENTS.md` peker nå til beslutningsreferatet §12. Forståelsestesten er fortsatt ikke utført.

- source_spec: `_bmad-output/implementation-artifacts/spec-pr-20-samordning-testplan.md`
  summary: "[LØST 2026-11-14, PR #20] Fristen for P-13s forståelsestest var ikke samordnet mellom beslutningsreferatet og planfilene."
  evidence: P-13-raden i `docs/beslutninger/avklaringspunkter.md` beskriver testen uten frist, og Review Triage Log B13 i `spec-frontend-komponenttester.md` avviste «før story 4.6» som ikke vedtatt. Kim valgte 2026-11-14 å beholde før story 4.6 som planlagt arbeidsmål, ikke som eget gruppevedtak om frist. `epics.md`, PRD og sprintstatus er presisert tilsvarende. Selve forståelsestesten er fortsatt ikke utført.

- source_spec: `_bmad-output/implementation-artifacts/spec-4-1-timer-i-perioden-per-kandidat.md`
  summary: "[AVKLART 2026-11-15, ikke en feil] `timer_i_startuka` hopper over ugyldige vakter og sjekker ikke datagrensen selv, men API-et når den bare etter `vurder_kandidater`."
  evidence: 35-timersregelens vindu er hele mandag–mandag-uka Vakten starter i (`berørte_uker`), samme uke som `timer_i_startuka` bruker. `vurder_kandidater` gir `Datafeil` for ugyldige vakter i vinduet (`kandidatvaktdatafeil`) og for vindu utenfor `[historikkstart, datagrense]` (`vindusdatafeil`), før noen kandidatliste eller `minutter_i_uka` finnes. Det opprinnelige funnet bygget på en feil antakelse om at vinduet var smalere. Gjenstående: funksjonen krever at kalleren har vurdert grunnlaget; dokumentert i docstringen for 4.3 og 4.4.

- source_spec: `spec-4-2-belastningslinje-med-terskel.md`
  summary: Kontrast mellom sporet (`--color-tag-bg`) og fyllet i `accent`/`warn` er ikke målt med verktøy (maybe-false, ville vært medium). Sett manuelt i lys drakt 2026-11-15 uten avvik; appen har ingen mørk drakt.
  evidence: Linja har ingen tallverdi av sin egen, bare farge og tekst ved høy belastning. Avgjøres av en målt kontrast (WCAG 1.4.11, 3:1) i lys drakt.
- source_spec: `spec-4-2-belastningslinje-med-terskel.md`
  summary: Fast bredde 110 px (`flex: 0 0`) kan gi overlapp eller klipp ved smale vinduer (maybe-false, ville vært medium).
  evidence: Kodegjennomgangen kunne ikke avgjøre det uten nettleser. Manuell layoutkontroll ved 1600, 1080, 960, 680 og 360 px mot ekte backend 2026-11-15: ingen overlapp, klipp eller vannrett scroll. Kan lukkes.
## Deferred from: code review of spec-4-2-belastningslinje-med-terskel.md (2026-11-15)

- Epic 4-konteksten er forkortet og har mistet sentrale detaljer om normalisering over alle gyldige (lavest gir 100), preferanseskala, uavhengig fasit, P-09, opprinnelig ansatts lønn og referansesammenligning. Samordne mot styrende dokumenter før senere stories bruker konteksten.
  Løst 2026-11-22: `epic-4-context.md` er samordnet med disse føringene og eksakt `Fraction` etter referatet §11–13. Ingen modellvalg endret. Se `docs/testing/2026-11-22/kontroll.md` og Kims sesjonslogg om praktisk oppfølging.

- source_spec: `_bmad-output/implementation-artifacts/spec-4-4-rangering-av-gyldige-kandidater.md`
  summary: "[LØST 2026-11-16, rettet i AGENTS.md] Statuslinjen i AGENTS.md sier at story 4.4 er «implementert og til gjennomgang». Det blir feil når PR-en er merget, og den gjentar det `sprint-status.yaml` allerede holder rede på."
  evidence: Blind Hunter B11 (2026-11-15). Endringen gjelder en agentkontekstfil og er derfor utsatt. Rett linjen når 4.4 settes til `done`, eller vurder å fjerne storystatus fra AGENTS.md. Løst 2026-11-16: PR #29 er merget, 4.4 er `done`, og innledningen i AGENTS.md sier at 4.1–4.4 og 4.7 er ferdige (faktarettelse ført i §11, AV-08). Storystatus står fortsatt i AGENTS.md; å fjerne den er ikke vurdert.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: "[LØST 2026-11-19, PR #33] Brukerutløst «Prøv igjen» for preferansetolkning etter endelig feil (FR-10, P-05) er implementert og levert."
  evidence: Utsatt av Mithad 2026-11-16 og beholdt av Ragnhild ved PR #30. API-endepunkt, knapp og automatiske tester laget 2026-11-19 (`spec-5-1-prov-igjen.md`). Løst 2026-11-19: godkjent av Mithad etter uavhengig gjennomgang, inkludert en egen live-test av samtidighet mot en kjørende backend (se `.logs/mithad-kuduz/979-2026-11-19-22-00-00-gjennomgang-pr-33.md`), og merget til `main` (PR #33). Story 5.1 er `done` i `sprint-status.yaml`.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-prov-igjen.md`
  summary: Flerprosessdrift krever delt lås eller vedvarende versjon for preferanseforsøk.
  evidence: Gjennomgangen 2026-11-19 fant at låser er per app-prosess og at identiske verdier kan skjule et mellomliggende forsøk. V1 dokumenterer én worker; verifiser atomisk samordning før støtte for flere workers.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-prov-igjen.md`
  summary: Test og håndter tekstendring A–B–A under KI-kall når preferanseredigering innføres i story 5.9.
  evidence: Betinget lagring sammenligner tekstens verdi og kan ikke oppdage en mellomliggende endring tilbake til samme verdi. Den nåværende appen har ikke preferanseredigering.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: "[LØST 2026-11-16, AV-19] Gruppa har ikke vedtatt feilreglene for preferansetolkning (3 nye forsøk etter 2/4/8 s, 90 s budsjett, minst 1 s og 60 s ved 429, sluttstatus `kunne_ikke_tolkes` med feiltype). Konstantene i `backend/adaptere/ki/openrouter.py` er Mithads forslag 2026-11-16."
  evidence: P-05/OP-03 og PRD §8 krever avklaring før story 5.1 og 5.2 kan bli `done`. Funnet i kodegjennomgangen 2026-11-16 (blind). Vedtaket føres i `docs/beslutninger/avklaringspunkter.md`. Løst 2026-11-16: Ragnhild Sætren vedtok verdiene på vegne av gruppa (AV-19, `avklaringspunkter.md` §11). «Prøv igjen» er ikke en del av vedtaket og står som eget funn.
- source_spec: `_bmad-output/implementation-artifacts/spec-5-1-tolke-tekstbaserte-ansattpreferanser-med-ki.md`
  summary: AGENTS.md sier at story 5.1 er «implementert og til gjennomgang», og setningen om `scripts/modelltest_*.py` er slått sammen med en svært lang linje.
  evidence: Kodegjennomgang 2026-11-16 (blind). Status i AGENTS.md blir foreldet ved merge, som tidligere funn om storystatus i agentkontekst. Rettes med registrering etter AV-08.

- source_spec: `_bmad-output/implementation-artifacts/spec-4-6-rangeringstabell-pa-smale-skjermer.md`
  summary: De faste kolonnene i rangeringstabellen (story 4.6) har ingen gjentakbar layouttest; bare et engangsskript i headless Chrome og manuell kontroll fanger at bakgrunn, `border-collapse: separate` eller `--rank-column-width` endres.
  evidence: jsdom gjør ingen layout og CI kjører bare `npm run build`/`npm run test`; en nettlesertestløper (f.eks. Playwright) er et valg for hele gruppa (OP-16). Verification-gap-gjennomgangen 2026-11-19.

- source_spec: `_bmad-output/implementation-artifacts/spec-4-6-rangeringstabell-pa-smale-skjermer.md`
  summary: Story 5.3 (ekspanderlenken «Vis begrunnelse ▾» / «Skjul begrunnelse ▴», UX-DR7, UX-DR12) må holde AC3 i 4.6 ved like. Når lenken legges i siste kolonne ved siden av Velg, mangler det 89 px ved 680 px med loddrett rullefelt, og ulempekolonnen glir inn under de faste kolonnene når tabellen er rullet helt til høyre.
  evidence: Simulert i `docs/ki-logg/2026-11-19-smale-skjermer/nettleserkontroll.mjs` (INFO-linjen) 2026-11-20, etter at «Kandidat» fikk fast bredde. Mulige grep er å la lenken stå under Velg eller å bryte teksten. Kjør nettleserkontrollen på nytt i 5.3.
  status: Kontrollert i story 5.3. Knappen under Velg bretter teksten på ordgrenser. Ved 680 px og 15 px loddrett rullefelt hadde ulempekolonnen 17,7 px klaring til de faste kolonnene ved maksimal høyreskrolling. Se [nettleserkontrollen](../../docs/ki-logg/2026-11-20-avveining-per-kandidat.md#nettleserkontroll).

- source_spec: `_bmad-output/implementation-artifacts/spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md`
  summary: Lekkasjetesten i story 5.6 kjøres bare mot `OpenRouterKiAdapter`. AD-6 og AC3 krever at den også kjøres mot `DemoKiAdapter`, som kommer i story 5.7.
  evidence: Utsatt etter brukerens valg 2026-11-21 (spesifikasjonens Never). Testen er forberedt: story 5.7 legger `pytest.param(demo, id="demo")` til `ADAPTERFABRIKKER` i `backend/tester/api/test_lekkasjeinvariant.py`. Fabrikken får den registrerende transporten og kan la være å bruke den. Kontrollene på porten (`forklar`, `tolk`) og i API-svarene gjelder da uendret, mens kontrollen av HTTP-forespørslene blir tom for en adapter uten HTTP. Kontroller i 5.7 at den forhåndsgenererte avveiningen også består uten treff i HTTP-forespørslene. Den negative kontrollen kaller i dag `kjør_flyt(openrouter, …)` direkte, og `kontroller_forklaringsforespørslene` kan ikke feile for en adapter uten HTTP, så 5.7 må parametrisere den negative kontrollen over `ADAPTERFABRIKKER` og hoppe over HTTP-kontrollen for demo.

- source_spec: `_bmad-output/implementation-artifacts/spec-5-4-reservetekst-naar-ki-forklaringen-feiler.md`
  summary: `test_begge_kilder_kontrollerer_alle_påstandene_mot_uavrundet_rangering` i `backend/tester/ki/test_avveining.py` prøver den forhåndsgenererte veien med `ForhåndsgenerertTestadapter`, som er definert i testen og kaller `valider` direkte. Den er ikke en `Forklarer`, og ruten svarer alltid `ki_kilde: "live"`. Story 5.7 må parametrisere testen over den ekte `DemoKiAdapter` gjennom `lag_app`, slik at en demokilde som hopper over faktakontrollen gir rød test.
  evidence: PR-gjennomgangen av PR #37 2026-11-22 (verification-gap og adversarial). Se [oppfølgingen](../../docs/ki-logg/2026-11-22-oppfolging-pr-37.md).
