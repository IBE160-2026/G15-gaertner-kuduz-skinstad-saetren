# Adversarial gjennomgang av arkitekturspinen — 2026-11-14

## Dom

To reelle hull i kontrakten: godkjenning kan bygges uten atomisk gyldighetskontroll, og en forhåndsgenerert forklaring kan gjenbrukes etter at referansegrunnlaget er endret. Begge lar to deler følge ordlyden i AD-ene og likevel levere et uforenlig resultat. Dette er funn i spesifikasjonen, ikke påstander om feil i ferdig kode.

## Funn 1 — AD-5/P-09: kontroll og lagring er ikke bundet til samme dataversjon

**To lydige enheter:** API-et leser Turnus, kontrollerer de fire harde reglene og øvrig beslutningsgrunnlag ved godkjenning. Lagringsadapterens ene skrivefunksjon tar deretter et fullstendig Godkjenning-objekt og skriver det. Begge oppfyller AD-5 og PRD FR-12 slik de står. Mellom lesingen og skrivingen kan et annet kall bemanne samme Vakt eller endre en Kandidats vakter. Lagringsadapteren kan da lagre en Godkjenning basert på et utdatert grunnlag. En separat unik indeks på Vakt hindrer dobbel godkjenning av samme Vakt, men hindrer ikke at en Kandidat i mellomtiden blir ugyldig på grunn av en annen Vakt.

**Kilder:** `ARCHITECTURE-SPINE.md` AD-5 og State-raden; PRD §4.6 FR-12; `epics.md` Story 3.2; beslutningsreferat P-09.

**Konsekvens:** Godkjenningen kan bryte en hard regel eller P-09 selv om hver modul følger sine lokale krav. Det er særlig relevant når godkjenningskall gjentas eller kjøres samtidig.

**Foreslått presisering:** Bind kontroll av datagrunnlag og skriveoperasjon til én atomisk transaksjon eller en eksplisitt versjonskontroll med avvisning ved endring. Angi hvilken del som eier transaksjonen, og krev databasebegrensning for høyst én Godkjenning per Vakt. Test konkurrerende kall og endring mellom lesing og skriving i Story 3.2. Dette angir invariant, ikke et bestemt ORM-grep.

**Håndtering:** Diskuter og oppdater AD-5/Story 3.2 før godkjenningsflyten ferdigstilles.

## Funn 2 — AD-6/P-07: demo-hash dekker kandidaten, men ikke sammenligningsgrunnlaget

**To lydige enheter:** Rangeringsdelen beregner `RangertKandidat` og en separat referansesammenligning, slik AD-1 krever. Demo-adapteren henter en forhåndsgenerert Avveining med nøkkelen `(vakt, kandidat, hash av RangertKandidat)`, slik AD-6 krever. Referansekandidaten kan få ny kostnad, timebelastning eller plassering mens den aktuelle kandidatens egne felter forblir identiske. Demo-adapteren finner da samme nøkkel og kan levere den gamle sammenligningen. Ordlyden i AD-6 sier at endrede underliggende data skal fanges opp, men nøkkelen inneholder ikke de separat leverte referansefaktaene.

**Kilder:** `ARCHITECTURE-SPINE.md` AD-1 (referansesammenligning leveres separat), AD-6 (nøkkel og hash); PRD §4.5 og SM-4; beslutningsreferat P-06/P-07 og K-04.

**Konsekvens:** En forklaring kan påstå en gammel relasjon til nr. 1/nr. 2. Kildemerket «forhåndsgenerert» gjør ikke innholdet riktig; faktakontrollen må også gjelde demo-svar.

**Foreslått presisering:** La cache-identiteten omfatte hele faktagrunnlaget som forklaringen bruker, særlig referansekandidatens ID og beregnede sammenligningsfakta, samt en versjon for forklaringskontrakten. Krev samme faktavalidering av forhåndsgenerert svar som av live-svar; ved mismatch bruk mal/reservetekst med riktig kildemerke. Test endret referanse mens egen `RangertKandidat` er lik.

**Håndtering:** Oppdater AD-6 og Story 5.3/5.7 før demo-forklaringer låses.

## Avgrensning

Eksakte feilkoder, fullt respons-skjema og transport for progressiv lasting står uttrykkelig i `Deferred`; disse er ikke rapportert som oversette beslutninger. P-05s budsjett for preferansetolkning er et dokumentert åpent spørsmål før Story 5.1, ikke en motstrid funnet her.
