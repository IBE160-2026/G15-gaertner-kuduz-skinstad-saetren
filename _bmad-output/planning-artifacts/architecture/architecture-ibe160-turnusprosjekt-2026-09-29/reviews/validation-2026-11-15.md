# Validering av oppdatert arkitekturspine — 2026-11-15

## Dom

**Reviewer Gate: betinget bestått.** De seks funnene fra 2026-11-14 er håndtert som dokumentkontrakter i den **nåværende** spinen. Mekanisk lint ga 0 funn. Tre uavhengige gjennomganger og egen kildekontroll fant tre middels og tre lave dokumentfunn. Ingen kjørende kodefeil ble påvist. Godkjenning og KI-flytene er ennå ikke implementert; dokumentert krav er ikke bevis for ferdig funksjon.

Denne Validate-runden endret ikke arkitekturspinen, PRD, epics eller kode. Ved en senere Update beholdes AD-1–AD-7.

## Metode og avgrensning

- Kontrollert arbeidskopien av [ARCHITECTURE-SPINE.md](../ARCHITECTURE-SPINE.md), SHA-256 `ddd9687500e73872111ec3574ddaee2d5bd2a246de168c66aacfda048260d769`, mot `HEAD e44b053`. Spinen har lokale, ukommitterte endringer. Rapporten fra 14.11 var en liste over kontrollpunkter, ikke bevis for denne versjonen.
- Lest [AGENTS.md](../../../../../AGENTS.md), arkitekturens [.memlog.md](../.memlog.md), [produktbrief](../../../../../product-brief.md), [PRD](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md), [epics](../../../epics.md), UX [DESIGN](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md) og [EXPERIENCE](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md), [beslutningsreferatet](../../../../../docs/beslutninger/avklaringspunkter.md) og [sensorveiledningen](../../../../../docs/emne/sensorveiledning-del-1.md), særlig kriterium 1, 3 og 5.
- Kjørt `python .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace _bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29`: `ok: true`, **0 funn**. `uv run` kunne ikke starte i sandboxen; samme lint-skript ble derfor kjørt direkte med Python.
- Tre Reviewer Gate-linser ble kjørt uavhengig: [rubrikk](review-rubric-2026-11-15.md), [adversarial grenseflate](review-adversarial-2026-11-15.md) og [teknologi/kode](review-technology-2026-11-15.md). Rubrikken dekket divergenspunkter, AD-enes håndhevbarhet, Deferred, produktdekning, kodevirkelighet og driftsdimensjonen. Adversarial kontroll prøvde å bygge to AD-kompatible, men uforenlige enheter. Teknologikontrollen sammenholdt låsefiler, kode og offisielle leverandørkilder.
- Relevante kodepunkter ble lest, ikke endret. Ingen full apptest, nettlesertest eller betalt/live KI-kall ble kjørt. Derfor er «ingen påvist kodefeil» begrenset til den inspiserte koden og kontraktene, ikke en generell friskmelding.

## Seks funn fra 2026-11-14 — ny kontroll

| Tidligere funn | Nåværende kontrakt og kildekontroll | Status |
| --- | --- | --- |
| Konsistent Godkjenning | [AD-5 linje 87](../ARCHITECTURE-SPINE.md#L87) binder kontroll av vist grunnlag, ny regelkontroll og skriving til én konsistent databasetilstand eid av lagringsadapteren; unik Godkjenning per Vakt kreves også. [Story 3.2 linje 651–690](../../../epics.md#L651) krever samtidighets- og endringstester; [PRD FR-12 linje 357–371](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md#L357) og P-08/P-09 er samordnet. | **Dokumentfunn lukket.** Implementasjon/transaksjonsmekanisme og tester er åpne i story 3.2. |
| KI-tolkning mot KI-forklaring | [AD-1 linje 46–50](../ARCHITECTURE-SPINE.md#L46) lar tolkingsporten behandle Ansattpreferanse uten kandidatstatus før filtrering, mens forklaringsporten og output bare får gyldige kandidater. Dette samsvarer med [PRD FR-10/11 linje 285–349](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md#L285), SM-2 og [Story 5.1/5.6](../../../epics.md#L965). | **Dokumentfunn lukket.** Portene og kjøretidstesten er ennå ikke bygget. |
| Referansefakta i demo-forklaring | [AD-6 linje 95](../ARCHITECTURE-SPINE.md#L95) identifiserer hele grunnlaget, også referansens ID, sammenligningsfakta og kontraktsversjon; forhåndsgenerert svar faktakontrolleres. [Story 5.7 linje 1177](../../../epics.md#L1177) krever test ved endret referanse. P-06/P-07 og PRD FR-11 støtter dette. | **Dokumentfunn lukket.** Demooppslag og testen er åpne i story 5.7. |
| SQLAlchemy-versjon | [Stack linje 124](../ARCHITECTURE-SPINE.md#L124) og Deferred peker til faktisk [requirements.txt linje 3](../../../../../backend/requirements.txt#L3): `sqlalchemy==2.1.6`. Dette er en utgitt versjon ifølge [SQLAlchemys endringslogg](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html); [2.1-dokumentasjonen](https://docs.sqlalchemy.org/en/21/contents.html) viste 2.1.8 ved kontrollen. Spinen hevder ikke at pinnen er nyeste versjon. | **Tidligere feilaktig «ikke versjonsfestet» er rettet.** Migreringsverktøy er fortsatt bevisst åpent. |
| OpenRouter-ruting | [AD-7 linje 102](../ARCHITECTURE-SPINE.md#L102) binder Luna til leverandøren `openai` uten fallback og krever falsk HTTP-test. [Modelltestskriptet linje 170–172](../../../../../scripts/modelltest_openrouter.py#L170) sender `provider.only=["openai"]` og `allow_fallbacks=false`. [OpenRouters rutingdokumentasjon](https://openrouter.ai/docs/guides/routing/provider-selection) bekrefter at modell-ID alene ikke binder tilbyder. | **Dokumentfunn lukket.** Appadapter og forespørselstest er åpne i story 5.1; modelltestskriptet er ikke appadapteren. |
| Cookie-eierskap | [AD-3 linje 73](../ARCHITECTURE-SPINE.md#L73) gir API-et utstedelse/setting, nettleseren lagring/sending og webklienten `credentials: "same-origin"`. Dette stemmer med [sesjon.py linje 73–101](../../../../../backend/adaptere/api/sesjon.py#L73), [api.ts linje 112–127](../../../../../frontend/src/api.ts#L112) og [MDNs Fetch-dokumentasjon](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch). | **Rettet i dokument og observert i kode.** |

## Nye funn — dokumentfeil og presiseringer

### D1 — Middels: Spinen tilordner lagring en innloggingssesjon den ikke persisterer

[Rolletabellen linje 37](../ARCHITECTURE-SPINE.md#L37) sier at `adaptere/lagring` persisterer «innloggingssesjon». [AD-3 linje 73](../ARCHITECTURE-SPINE.md#L73) beskriver derimot et JWT i cookie med signeringsnøkkel bare i API-minnet. [Modellene](../../../../../backend/adaptere/lagring/modeller.py#L52) har `turnus`, `ansatt`, `vakt` og `bruker`, ingen sesjonstabell; [sesjon.py](../../../../../backend/adaptere/api/sesjon.py#L48) signerer og leser JWT. To utviklere kan dermed bygge hver sin eier av sesjonstilstand. **Senere Update:** rett rollebeskrivelsen til persistente brukere og API-eid JWT. Dette er en dokumentmotstrid, ikke en påvist kodefeil.

### D2 — Middels: Eierskapet til en lagret `TolketPreferanse` er for absolutt

[AD-1 linje 50](../ARCHITECTURE-SPINE.md#L50) sier at bare `adaptere/ki` konstruerer en vellykket `TolketPreferanse`, mens [AD-1 linje 48](../ARCHITECTURE-SPINE.md#L48) og [Story 5.1 linje 979–991](../../../epics.md#L979) krever at en vellykket tolkning persisteres og leses av Rangeringen uten nytt KI-kall. Ved lesing må lagringsadapteren rekonstruere eller validere den typede verdien. Streng lesning sender databaseverdien gjennom KI-adapteren; en annen lesning lar lagring konstruere modellen. **Senere Update:** skill mellom *semantisk produksjon* av ny tolkning (KI) og deserialisering av allerede validert, lagret verdi (lagring), med råtekst-/versjonsbinding. Dette er et kontraktshull før story 5.1, ikke en kodefeil i dagens app.

### D3 — Middels: Tidssoneordlyden samsvarer ikke med lagring og regelberegning

[Konvensjonsraden linje 109](../ARCHITECTURE-SPINE.md#L109) sier at alle Vakt-tidspunkt «lagres og beregnes i `Europe/Oslo`». [OsloTid linje 21–45](../../../../../backend/adaptere/lagring/modeller.py#L21) lagrer ISO 8601 i UTC og leser tilbake i Oslo-tid. [11-timersregelen](../../../../../backend/domene/regelmotor/elleve_timer.py#L48) og [35-timersregelen](../../../../../backend/domene/regelmotor/trettifem_timer.py#L34) bruker Oslo-kalendergrenser der det trengs, men regner faktisk tid i UTC. **Senere Update:** bind Oslo-semantikk for kalender/vise-tid og UTC for lagring og varighets-/intervallsammenligning. Ingen DST-kodefeil er påvist i denne dokumentkontrollen.

### D4 — Lav: Lokal transport tegnes som HTTPS

[Containerdiagrammet linje 134](../ARCHITECTURE-SPINE.md#L134) merker Web→API «HTTPS/JSON, JWT», mens spinen selv sier [kun lokal kjøring linje 141](../ARCHITECTURE-SPINE.md#L141) og [README](../../../../../README.md) bruker Vite-proxy og lokal HTTP. Beskriv lokal HTTP som faktisk v1-miljø; HTTPS kan knyttes til en eventuell framtidig hostingbeslutning. Dette er dokumentpresisjon, ikke et krav om å endre koden nå.

### D5 — Lav: Kildetreet kaller miljøvariablene «udokumenterte»

[Kildetreet linje 181](../ARCHITECTURE-SPINE.md#L181) har kommentaren «navngitte, udokumenterte miljøvariabler» om `.env.example`, motsatt [konvensjonen linje 110](../ARCHITECTURE-SPINE.md#L110) og [AGENTS.md](../../../../../AGENTS.md). Rett til «dokumenterte variabler uten verdier» ved Update.

### D6 — Lav: Endringsproveniens er foreldet

Frontmatter i [spinen linje 9](../ARCHITECTURE-SPINE.md#L9) sier `updated: 2026-10-14`, mens de seks dokumentrettingene ble gjort 2026-11-15 og [arkitekturens memlog](../.memlog.md) slutter med 2026-10-16-beslutningen. [Sensorveiledningen kriterium 1](../../../../../docs/emne/sensorveiledning-del-1.md) legger vekt på sporbar prosess. Registrer endringshendelsen og dato ved en senere Update; denne Validate-runden bevarer spinen og memloggen uendret.

## Åpne implementasjonskrav, ikke påviste kodefeil

| Krav | Eier og bevisgrense |
| --- | --- |
| Atomisk Godkjenning, identitet for vist grunnlag, ny regelkontroll og unik Vakt | [Story 3.2](../../../epics.md#L651) og AD-5. Dagens [godkjenningsflate](../../../../../frontend/src/komponenter/Godkjenningsflate.tsx#L18) sier selv at den ennå ikke skriver; ingen Godkjenning-tabell eller POST-flyt er implementert. |
| KI-tolkning, lagring av status/verdi og eget feilbudsjett | [Story 5.1/5.2](../../../epics.md#L965), P-05 og [Deferred linje 204](../ARCHITECTURE-SPINE.md#L204). Ventetrinn, antall forsøk og sluttstatus skal avklares før story 5.1. |
| Faktakontrollert forklaring, referanse, demoidentitet, ruting og falsk HTTP-test | [Story 5.3–5.7](../../../epics.md#L1032), AD-1/6/7 og P-06/P-07. `adaptere/ki` finnes ennå ikke; isolerte modelltester er ikke implementasjon av disse portene. |
| Kildelinje for live/forhåndsgenerert/mal/Reservetekst | [EXPERIENCE linje 62](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md#L62) krever modellnavn og dato der det passer. Sørg for at API-kontrakten faktisk bærer disse metadataene i story 5.3/5.7; AD-6 nevner foreløpig bare `ki_kilde`. Lavt grenseflateoppfølgingspunkt. |

Ingen av disse fremtidige akseptkriteriene er behandlet som en feil i kode som ennå ikke finnes. Det er heller ikke grunnlag for å markere storyene ferdige ut fra planleggingsdokumentene.

## Kontrollert uten avvik

- AD-1/AD-2s importretning samsvarer med [import-linter-kontrakten](../../../../../backend/pyproject.toml#L9); de fire eksisterende harde reglene har egne testmoduler under `backend/tester/regelmotor/`. Kjøretidsgrensen mot KI må testes når adapteren finnes.
- [Stack](../ARCHITECTURE-SPINE.md#L113) er kontrollert mot [frontend/package.json](../../../../../frontend/package.json) og [backend/requirements.txt](../../../../../backend/requirements.txt); de oppgitte React-, Vite-, TypeScript-, Vitest-, Testing Library-, jsdom-, FastAPI- og SQLAlchemy-versjonene stemmer med manifestene eller peker uttrykkelig til dem. Den observerte SQLAlchemy-pinnen er et eksisterende valg, ikke et krav om nyeste versjon.
- P-08s datafeil er skilt fra tom kandidatlistestatus i [AD-4 linje 81](../ARCHITECTURE-SPINE.md#L81) og [API-et](../../../../../backend/adaptere/api/main.py#L274). P-12s historiske forklaring er uttrykkelig utenfor v1. AV-17s desktop/smale vinduer og OP-16s komponenttester er ført i Deferred/Testing.
- Driftsdimensjonen er ikke taus: lokal kjøring er valgt; hosting, migrering, progressiv forklaringstransport og runtime-logging står i Deferred. De åpne valgene må tas ved den angitte storyen eller ved eventuell hosting, ikke fremstilles som allerede implementert.

**Anbefalt videre behandling:** Ta D1–D3 og de små presiseringene i en egen BMAD Update med stabile AD-ID-er. Behold story 3.2 og 5.x som implementasjonsarbeid med sine tester. Ingen endring i styrende dokumenter er gjort i denne Validate-runden.
