# Validering av arkitekturspinen — 2026-11-14

## Vurdering

**Arkitekturen er i hovedsak samordnet med de oppdaterte planleggingsdokumentene, men to kontrakter bør presiseres før de berørte storyene ferdigstilles.** BMADs `lint_spine.py` fant 0 mekaniske feil. Tre uavhengige gjennomganger fant seks ulike forhold; overlappende funn er samlet nedenfor. Dette er en dokument- og grenseflategjennomgang, ikke en påstand om seks feil i kjørende app.

## Funn som bør håndteres først

### 1. Godkjenning må kontrollere og skrive mot samme grunnlag

**Kilder:** `ARCHITECTURE-SPINE.md` AD-4/AD-5; PRD §4.6 (FR-12); `epics.md` Story 3.2; beslutningsreferat P-09. **Håndtering: diskuter og oppdater før Story 3.2 ferdigstilles.**

AD-5 gir lagringsadapteren én skrivevei, men binder ikke ny regelkontroll, kontroll av uendret grunnlag og skriving til én konsistent databasetilstand. To samtidige kall kan lese samme ledige vakt; en kandidat kan også få en annen vakt etter kontrollen. Resultatet kan bryte en hard regel selv om hver del følger AD-5.

**Forslag:** Fastsett en atomisk godkjenningsoperasjon eller eksplisitt versjonsvern med konfliktavvisning. Angi eier av transaksjonsgrensen, krev høyst én godkjenning per vakt i databasen, og test samtidige kall og endring mellom lesing og skriving. La API-kontrakten skille konflikt fra datafeil og «ingen gyldige».

### 2. Skill KI-tolkning fra KI-forklaring i invarianten

**Kilder:** AD-1/AD-6; PRD §4.5 (FR-10/FR-11, SM-2); Story 5.1/5.6. **Håndtering: presiser før disse storyene bygges.**

AD-1 sier at ingen utelukket kandidat-ID skal nå KI-porten, samtidig som preferanser kan tolkes før filtrering eller i bakgrunnen ved innlasting. En ansatt som senere utelukkes, kan dermed allerede ha fått teksten tolket. SM-2 krever at KI aldri anbefaler en utelukket kandidat. Ordlyden kan gi motstridende implementasjoner og tester.

**Forslag:** La tolkingsporten behandle ansattens tekst uten kandidatstatus. Begrens forklaringsporten til gyldige, ferdig rangerte kandidater, og la Story 5.6 teste akkurat denne grensen og outputen. Dersom gruppa mener også tolkning skal vente til etter filtrering, må både PRD og AD-1 endres uttrykkelig.

### 3. Demo-forklaringens nøkkel dekker ikke referansefakta

**Kilder:** AD-1/AD-6; PRD §4.5 (SM-4); P-06/P-07, K-04; Story 5.3/5.7. **Håndtering: oppdater før demo-forklaringer låses.**

AD-6 bruker `(vakt, kandidat, hash av RangertKandidat)` for en forhåndsgenerert Avveining. AD-1 leverer referansesammenligningen separat. Referansens kostnad, belastning eller plassering kan endres uten at kandidatens egen hash endres. Da kan demoen gjenbruke en foreldet sammenligning.

**Forslag:** La identiteten dekke hele faktagrunnlaget, inkludert referansens ID og sammenligningsfakta, samt kontraktsversjon. Faktakontroller også forhåndsgenererte svar; fall tilbake til mal/reservetekst ved avvik. Test endret referanse med uendret kandidat.

## Dokumentpresiseringer

4. **SQLAlchemy-versjon:** Stack og Deferred sier at versjonen er åpen, mens `backend/requirements.txt` låser `sqlalchemy==2.1.6`. Rett dette som observert kodevalg ved neste Update; migreringsspørsmålet kan stå åpent.
5. **OpenRouter-leverandør:** Stack sier «låst til leverandøren openai». Modell-ID-en `openai/gpt-6-luna` alene binder ikke OpenRouters ruting til én tilbyder. Avklar om binding er et tilsiktet vedtak. Hvis ja, angi og test leverandørvalg i adapterkontrakten; hvis nei, rett påstanden. Se [OpenRouters leverandørvalg](https://openrouter.ai/docs/guides/routing/provider-selection).
6. **Cookie-eierskap:** AD-3 sier at webklienten lagrer en `httpOnly`-cookie. `backend/adaptere/api/sesjon.py` setter cookien; nettleseren lagrer og sender den. Rett ordlyden slik at en senere story ikke forsøker å sette `HttpOnly` fra React.

## Kontrollert uten nytt avvik

- AV-17s avgrensning av mobil/nettbrett til v2 og smale datamaskinvinduer i v1 finnes i Deferred.
- OP-16s komponenttester er tatt inn. P-05s åpne forsøk/budsjett for preferansetolkning er holdt atskilt fra AD-7s 90 sekunder for Avveining.
- Importkontrakten, JWT-oppsettet og manifestversjonene er kontrollert mot repoet. Ingen live KI-kall eller full testkjøring ble utført.

## Metode og avgrensning

BMAD `bmad-architecture` Validate: mekanisk lint (0 funn), rubrikkvandring, adversarial grenseflatekontroll og teknologi-/realitetskontroll. Gjeldende produktbrief, PRD, UX, epics, beslutningsreferat og relevante kodefiler ble brukt som grunnlag. Arkitekturspinen er ikke endret. Fullstendige delrapporter: [rubrikk](review-rubric-2026-11-14.md), [adversarial](review-adversarial-2026-11-14.md) og [teknologi](review-web-verification-2026-11-14.md).
