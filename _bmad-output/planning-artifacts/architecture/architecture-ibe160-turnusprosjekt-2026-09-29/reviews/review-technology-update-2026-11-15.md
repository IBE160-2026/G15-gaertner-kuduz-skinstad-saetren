# Teknologi- og kodekontroll av Update-spinen — 2026-11-15

## Dom

**Bestått som dokumentkontrakt.** D1–D6 er nå forenlige med kontrollert kode, vedtak, PRD, epics og UX. Ingen ny dokumentmotstrid eller påvist kodefeil ble funnet i de undersøkte grensene. Story 3.2 og 5.x har fortsatt implementasjon og tester åpne; den rettede spinen gjør dem ikke ferdige.

## Metode og avgrensning

Jeg leste gjeldende [spine](../ARCHITECTURE-SPINE.md) etter Update, [memlog](../.memlog.md), `AGENTS.md`, [beslutningsreferatet](../../../../../docs/beslutninger/avklaringspunkter.md), [PRD](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md), [epics](../../../epics.md) og UX [EXPERIENCE](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md) og [DESIGN](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md). Teknologiløfter ble sammenholdt med `backend/requirements.txt`, `frontend/package.json` og `frontend/package-lock.json`; aktuelle kodegrenser ble lest i sesjon, lagring, regelmotor, frontend-API og Vite-oppsett. Jeg kontrollerte de ustabile eksterne opplysningene mot leverandørenes egne sider. Dette er inspeksjon, ikke en ny full apptest, nettlesertest eller et live KI-kall.

## D1–D6 mot kode og styringsgrunnlag

| Funn | Kontroll etter retting | Vurdering |
| --- | --- | --- |
| D1 – sesjonslagring | [Rolletabellen](../ARCHITECTURE-SPINE.md#L37) beskriver nå bruker/passordhash og planlagt Godkjenning, uten lagret innloggingssesjon. `backend/adaptere/lagring/modeller.py:52–146` har `turnus`, `ansatt`, `vakt` og `bruker`, men ingen sesjonstabell. `backend/adaptere/api/sesjon.py:44–94` signerer/leser JWT og setter/fjerner cookie. `backend/adaptere/api/main.py:185,208–214,242` holder nøkkelen i minnet og slår opp bruker. Dette følger OP-10/AD-3 og PRD FR-13. [Epics](../../../epics.md#L80) er samordnet. | Dokumentmotstrid lukket; ingen kodefeil påvist. |
| D2 – lagret `TolketPreferanse` | [AD-1](../ARCHITECTURE-SPINE.md#L50) skiller ny semantisk tolkning i `adaptere/ki` fra deserialisering/validering ved lesing i `adaptere/lagring`. Bruk bindes til samme Ansatt og tekst. [Epics](../../../epics.md#L61) og [story 5.1](../../../epics.md#L975) bruker samme skille. PRD FR-10/P-05 krever lagret tolkning for aktuell tekst. `backend/adaptere/ki` inneholder ennå bare `__init__.py`; porttypen og lagringsfeltene finnes ennå ikke. | Dokumentkontrakten er sammenhengende. Skjema, eventuell formatversjon og tester er åpne i story 5.1, ikke en påvist kodefeil. |
| D3 – tidssone | [Konvensjonen](../ARCHITECTURE-SPINE.md#L109) sier UTC ved lagring og tidslinjeberegning, Oslo ved kalendergrenser/visning. `OsloTid` i `backend/adaptere/lagring/modeller.py:21–45` lagrer UTC-tekst og leser i `Europe/Oslo`. `backend/domene/regelmotor/elleve_timer.py:48–64`, `trettifem_timer.py:33–72` og `vurdering.py:95–134` regner faktiske intervaller i UTC. Dette følger AV-04/P-02 og PRDs krav om Oslo-uker og faktisk forløpt tid. [Epics](../../../epics.md#L82) og story 1.2 er samordnet. | Dokumentpresisjon rettet; ingen DST-kodefeil påvist ved inspeksjonen. |
| D4 – transport | [Diagrammet](../ARCHITECTURE-SPINE.md#L134) sier lokal HTTP/JSON via Vite-proxy med JWT-cookie. `frontend/vite.config.ts:9–10` sender `/api` til `http://127.0.0.1:8000`; `frontend/src/api.ts:113–115` bruker `credentials: "same-origin"`; `backend/adaptere/api/sesjon.py:73–83` bruker `secure=False` for lokal HTTP. README beskriver de samme adressene. OP-10 velger proxy, og hosting står fortsatt utsatt. | Diagrammet samsvarer med v1-miljøet. |
| D5 – `.env.example` | [Kildetreet](../ARCHITECTURE-SPINE.md#L181) sier dokumenterte variabler uten verdier, i tråd med AGENTS.md, epics NFR7 og den faktiske `.env.example`. | Ordlydsfeil rettet. |
| D6 – proveniens | Frontmatter har `updated: 2026-11-15`, og [memloggen](../.memlog.md) har append-only oppføringer for de seks tidligere dokumentrettingene, OP-10 og D1–D6. AD-1–AD-7 er beholdt. | Endringsgrunnlaget er sporbarhet for dokumentet; gate-resultat føres etter fullført gate. |

## Teknologi- og versjonskontroll

- `backend/requirements.txt` låser FastAPI 0.141.1 og SQLAlchemy 2.1.6, som svarer til Stack. [SQLAlchemys offisielle 2.1-endringslogg](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html) bekrefter at 2.1.6 er en utgitt versjon. Spinen påstår ikke at den er nyest, og migreringsverktøy er fortsatt utsatt.
- `frontend/package.json` låser React 19.3.0, Vite 8.3.1, TypeScript 7.0.2, Vitest 5.1.0, Testing Library-pakkene og jsdom 28.1.0 slik Stack angir. `frontend/package-lock.json:1433–1463` viser at jsdom 28.1.0 støtter Node `^22.12.0`. [jsdoms egen `package.json` for v29.0.0](https://github.com/jsdom/jsdom/blob/v29.0.0/package.json) hever kravet til `^22.13.0`; Stack-påstanden om 28.1.0 som siste passende major for lovet Node 22.12 er dermed forenlig med kildene.
- [OpenRouters modellside](https://openrouter.ai/openai/gpt-6-luna) viser `openai/gpt-6-luna`, $0.10/$0.50 per million tokens for standardtilbyder, strukturert output og flere tilbydere. [Offisiell rutingdokumentasjon](https://openrouter.ai/docs/guides/routing/provider-selection) beskriver leverandørfilter og `allow_fallbacks: false`. AD-7s leverandørbinding trengs; modell-ID alene ville ikke gi den. `scripts/modelltest_openrouter.py:170–181` viser parameterne i isolert modellforsøk, men appadapteren er ennå ikke bygd.

## Gjenstående implementasjonsporter

- AD-5s konsistente godkjenningsoperasjon og unik Godkjenning per Vakt skal implementeres og testes i story 3.2. Dagens `backend/adaptere/api/main.py:292–319` leverer et lesegrunnlag, og `frontend/src/komponenter/Godkjenningsflate.tsx:18` sier uttrykkelig at skriving venter. Dette er ikke en feil i eksisterende skrivekode.
- AD-1/AD-6/AD-7s to KI-porter, faktakontroll, demooppslag og falsk HTTP-test skal bygges i story 5.x. P-05s egne feilbudsjett er fortsatt åpent før story 5.1. UX-kildelinjen med modell/dato må bæres i de fremtidige responsskjemaene for story 5.3/5.7; dette er et allerede identifisert oppfølgingspunkt, ikke en ny dokumentmotstrid.

De seks funnene fra 14.11 er kontrollert som dokumentkontrakter i forrige Validate. Denne gjennomgangen fant ikke nye bevis som krever at de åpnes igjen.
