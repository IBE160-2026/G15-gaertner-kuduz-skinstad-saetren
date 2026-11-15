# Uavhengig teknologi- og kodekontroll — 2026-11-15

## Konklusjon

**Betinget bestått som arkitekturkontrakt.** De seks funnene fra 2026-11-14 er i hovedsak håndtert i *den nåværende arbeidstre-versjonen* av spinen. Kontrollen fant to nye presisjonsfeil i dokumentasjonen, men ingen påvist kodefeil. Godkjennings-, rangerings- og KI-kontraktene er ennå delvis planlagt arbeid; deres fravær i kode er ikke en regresjon i denne Validate-runden.

## Metode

Jeg leste gjeldende `ARCHITECTURE-SPINE.md` og `.memlog.md`, `AGENTS.md`, `product-brief.md`, PRD, `epics.md`, UX `EXPERIENCE.md` og beslutningsreferatets relevante P-/AV-/OP-punkter. Jeg sammenholdt løftene med `backend/requirements.txt`, `frontend/package.json`/`package-lock.json`, nåværende modeller, innlogging, kandidat-API, frontend-fetch, import-linter-kontrakt og modelltestskript. Sensorveiledningen, særlig kriterium 1, 3 og 5, ble brukt som krav til sporbarhet og sannferdig plan–kode-sammenheng. Teknologipåstander ble verifisert mot SQLAlchemys, OpenRouters og MDNs egne sider 2026-11-15. Ingen live KI-kall, full testkjøring eller endring av koden/spinen ble gjort. Den eldre valideringsrapporten ble brukt bare til å identifisere de seks kontrollpunktene.

## Funn

### T1 — Lagringsadapteren påstås å persistere innloggingssesjonen

**Alvorlighet:** middels. **Type:** dokumentfeil. **Tiltak:** rett i senere Update, behold AD-3.

Rolle-tabellen i spinen sier at `adaptere/lagring` persisterer «innloggingssesjon» (`ARCHITECTURE-SPINE.md:37`). AD-3 sier derimot at `adaptere/api` utsteder et JWT i en `httpOnly`-cookie, med tilfeldig nøkkel i minnet som ugyldiggjøres ved omstart (`:69–73`). Faktisk kode har bare tabellene `turnus`, `ansatt`, `vakt`, `bruker` (`backend/adaptere/lagring/modeller.py:52,66,86,128`), mens `backend/adaptere/api/sesjon.py:48–101` signerer og leser tokenet uten sesjonstabell. `backend/adaptere/api/main.py:208–214,242` slår opp brukeren ved hvert kall og setter cookien. Den presise beskrivelsen er at lagringsadapteren persisterer **brukere**, mens API-et eier JWT-sesjonen. Ingen kodefeil ble påvist; `frontend/src/api.ts:112–127` følger AD-3 med `credentials: "same-origin"`, og [MDNs Fetch-dokumentasjon](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) bekrefter nettleserens ansvar for cookie-lagring og sending.

### T2 — Tidssonekonvensjonen beskriver fysisk lagring og regning upresist

**Alvorlighet:** lav. **Type:** dokumentfeil. **Tiltak:** presiser ved senere Update.

Spinen sier at alle Vakt-tidspunkt «lagres og beregnes i `Europe/Oslo`» (`ARCHITECTURE-SPINE.md:109`). `backend/adaptere/lagring/modeller.py:21–45` lagrer tidspunkt som ISO 8601 **i UTC** og leser dem tilbake i `Europe/Oslo`; regelmotoren konverterer til UTC før tidsintervall- og hvileberegninger (`backend/domene/regelmotor/vurdering.py:107,118–134`, `elleve_timer.py:48–64`, `trettifem_timer.py:49–72`). Løsningen ser ut til å ivareta den ønskede Europe/Oslo-semantikken og faktisk tidsforløp over DST. Rett bare ordlyden: lokaltid for kalenderforståelse og visning, UTC for lagring/varighetsregning. Dette er en observasjon av kode; jeg har ikke kjørt nye DST-tester.

## De seks funnene fra 2026-11-14, kontrollert på nytt

| Tidligere funn | Status i nåværende spine og kode | Klassifisering |
| --- | --- | --- |
| Konsistent Godkjenning | AD-5 (`:83–87`) gir lagringsadapteren én skrivevei og transaksjonsgrense for sammenligning med vist grunnlag, ny hardregelkontroll og skriving, samt databasevern mot mer enn én Godkjenning per Vakt. Story 3.2 gjentar dette med samtidighetstest (`epics.md:651–683`), i tråd med PRD FR-12/P-09 (`prd.md:357–379`, beslutningsreferat `:796`). Dagens skjema har ennå ingen Godkjenning-tabell, og dagens UI sier selv at skriving kommer i story 3.2 (`frontend/src/komponenter/Godkjenningsflate.tsx:18`). | Dokumentretting oppnådd; åpent implementasjonskrav, ikke kodefeil. |
| Tolkning vs. forklaring | Design Paradigm/AD-1 (`:24–29,43–50`) skiller tolkning per Ansatt før filtrering fra forklaring av ferdig gyldig kandidat. Story 5.6 (`epics.md:1128–1154`) tester forklaringsporten og outputen, ikke all preferansetolkning. Samsvarer med PRD `:348` og P-05/P-06/P-07 (`avklaringspunkter.md:792–794`). KI-porten finnes ennå ikke i appkode. | Dokumentretting oppnådd; åpent implementasjonskrav. |
| Referansefakta i demo | AD-6 (`:90–98`) inkluderer Vakt, kandidat, egen `RangertKandidat`, referansens ID, beregnede sammenligningsfakta og kontraktsversjon i oppslagsidentiteten, og krever ny faktakontroll. Story 5.7 (`epics.md:1156–1190`) krever negativ test med endret referanse. | Dokumentretting oppnådd; åpent implementasjonskrav. |
| SQLAlchemy-versjon | Stack/Deferred (`ARCHITECTURE-SPINE.md:124,206`) peker nå til faktisk `backend/requirements.txt:3`, som låser `sqlalchemy==2.1.6`. [SQLAlchemys offisielle 2.1-endringslogg](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html) bekrefter 2.1.6 som en utgitt versjon; [nåværende 2.1-dokumentasjon](https://docs.sqlalchemy.org/en/21/contents.html) viser 2.1.8 per 2026-11-15. Valget 2.1.6 er en reell eksisterende pin, ikke påstand om nyeste utgave. Migrering er fortsatt eksplisitt åpent. | Tidligere dokumentfeil rettet; mulig liten selvstendighetsforbedring ved å gjengi `2.1.6` i tabellen. |
| OpenRouter-ruting | AD-7 (`:100–102`) krever for Luna leverandør `openai` **uten** fallback og falsk HTTP-test. `scripts/modelltest_openrouter.py:25,167–181` bruker `provider.only=["openai"]` og `allow_fallbacks=false`, men er et isolert modellforsøk, ikke appadapter. [OpenRouters modellside](https://openrouter.ai/openai/gpt-6-luna) viser flere mulige leverandører og pris/strukturert output; [OpenRouters rutingdokumentasjon](https://openrouter.ai/docs/guides/routing/provider-selection) bekrefter leverandørfilter og avslått fallback. | Dokumentretting oppnådd; åpent implementasjonskrav i story 5.1. Modellslug alene er ikke bevis for låst ruting. |
| Cookie-eierskap | AD-3 (`:69–73`) sier nå API-et setter `httpOnly`-cookie, nettleseren lagrer/sender, webklienten bruker `credentials: "same-origin"` og leser ikke tokenet. Det samsvarer med `backend/adaptere/api/sesjon.py:73–101`, `main.py:242`, `frontend/src/api.ts:1–2,112–127` og [MDNs Fetch-dokumentasjon](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch). | Tidligere dokumentfeil rettet og gjennomført i kode. |

## Kontrollert uten avvik

- Appens nåværende versjonslåser for FastAPI, React, Vite, TypeScript, Vitest, Testing Library og jsdom samsvarer med Stack (`backend/requirements.txt:1`, `frontend/package.json:8–26`, `ARCHITECTURE-SPINE.md:113–125`). Dette er en samsvarskontroll mot repoet, ingen påstand om at alle er siste utgave.
- Modell, pris og `response_format`/JSON-skjema-støtte for Luna er fortsatt oppgitt på [OpenRouters egen modellside](https://openrouter.ai/openai/gpt-6-luna). Routing-invarianten krever egen leverandørparameter, som AD-7 nå sier.
- Import-linter-kontrakten omfatter hele `domene` og forbyr alle `adaptere`-importer (`backend/pyproject.toml:9–18`, `backend/tester/test_arkitektur.py:1–19`), slik AD-1/AD-2 krever for statisk kontroll. Kjøretidstesten for KI-forklaring er fremtidig story 5.6.
- Manglende KI-adapter, rangering, Godkjenning-tabell og fullstendig `RangertKandidat` i nåværende app er planlagt arbeid i Epic 3–5, ikke påviste kodefeil. Ingen resultater fra denne undersøkelsen alene beviser at de fremtidige akseptkriteriene er oppfylt.
