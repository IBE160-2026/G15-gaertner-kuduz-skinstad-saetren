# PRD Quality Review — Turnushjelperen (2026-11-10)

## Overall verdict

PRD-en gir en sammenhengende og etterprøvbar kjerneflyt fra valgt vakt til menneskelig godkjenning. P-01–P-13 og E-01/E-02 er i hovedsak omsatt til krav og gjenstående kontroller uten å fremstille dokumentvedtak som implementasjon. Én normativ formulering i en hard regel bør rettes før dette brukes som grunnlag for story 2.2; noen konsekvenser og statuslinjer trenger presisering. Samlet vurdering: **Fair** inntil den høye feilen er rettet.

## Decision-readiness — adequate

Produktvalgene og avgrensningene er synlige: §4.3 fastsetter merkostnad og kalenderukefordeling (P-01/P-02), §4.5 skiller feilet tolkning fra manglende tekst (P-05), og §§2.2/5 avgrenser P-10B, P-07s valgfrie sammenligning og P-12B. §8 skiller krav fra utestående implementasjon og kontroll. Den muntlige kilden bak E-01 og gjenstående E-02-sluttkontroll er oppgitt med riktig bevisnivå.

### Findings

- **[low] Misvisende status for P-10B** (§8 punkt 4) — «Skriv og prioriter egen story» er utdatert når story 5.9 nå er skrevet i epics. *Fix:* Si at story 5.9 er planlagt i backlog, og at implementering/prioritering etter fungerende kjerneflyt gjenstår.

## Substance over theater — strong

Eksempler på 32 + 8 timer, søndag–mandag-fordeling, 32:23/32:24, ventende/feilet preferanse og datafeil ved seedgrensen gjør kravene konkrete. Personaen Kari driver én faktisk brukerreise og det finnes ingen unødig rollestruktur. Suksesskriteriene måler de sentrale risikopunktene fremfor generisk vekst eller aktivitet.

### Findings

Ingen.

## Strategic coherence — strong

Fire avgrensede harde regler, deterministisk rangering, KI som tolker/forklarer, og menneskelig valg støtter samme tese. P-08s stopp ved ufullstendig grunnlag og P-06s reservetekst bevarer troverdighet uten å utvide regelsettet. P-10B kommer etter kjerneflyten, P-12B er ikke v1-krav, og motmetrikkene SM-C1/SM-C2 hindrer feil optimalisering.

### Findings

Ingen.

## Done-ness clarity — thin

De fleste FR-ene har testbare konsekvenser, spesielt FR-4/5/7/8/9/10/12. Ett verb i FR-3 åpner likevel for at en hard regel kan hoppes over. P-06s kontroll er retningsbestemt, men PRD-en navngir ikke hele settet av påstandstyper som kan aksepteres; §8 sender dette til kontraktarbeidet. Det er en akseptabel utsatt designavgjørelse bare dersom story 5.3/5.4 faktisk fastsetter og tester settet før ferdigstilling.

### Findings

- **[high] Hard kollisjonsregel formulert som valgfri** (§4.2, FR-3) — «Systemet kan utelukke» motsier at kollisjon er en hard regel og samme FRs 100 %-konsekvens. *Fix:* Endre til «Systemet skal utelukke» og behold grensetesten for tidsmessig overlapp.
- **[medium] Faktakontrollens aksepterte påstander er ikke endelig avgrenset** (§4.5, FR-11) — «strukturerte begrunnelser fra et avgrenset sett» lar fremdeles implementatøren velge hvilke påstander som kan vises, mens kravet lover validering av referanser og retning. *Fix:* Navngi kontraktens tillatte begrunnelsestyper og test ugyldig kandidat, kostnad, preferanse, omvendt sammenligning og feil likhet i tilhørende story før den markeres ferdig. La PRD-en peke til den kontrakten.
- **[medium] Reproduserbarhet er formulert med ufullstendig input** (§4.3, FR-7 og FR-14) — «Samme Kandidat og samme Vakt» kan gi annen kostnad/ulempe når turnus, lønn eller historikk endres; P-09 forutsetter nettopp endret beslutningsgrunnlag. *Fix:* Si «samme fullstendige strukturerte beslutningsgrunnlag» i disse konsekvensene, slik SM-5 gjør.

## Scope honesty — adequate

§5 og §6 avgrenser tariff, reelle persondata, hele turnusplanen og ansattportal. §8 lar P-13s forståelsestest og E-02s sluttkontroll stå som uutført. Kjerneflyten holdes atskilt fra P-10B, P-07-strekkmålet og P-12B. `status: final` kan forstås som finalisert kravtekst, men status betyr ikke at appen er ferdig; innledningen og §8 presiserer dette.

### Findings

- **[low] §8 heter «Åpne spørsmål», men innholdet er kontroller og oppgaver** (§8) — beslutningene er tatt, så overskriften kan få leseren til å tro at P-01–P-13 fortsatt er åpne produktvalg. *Fix:* Kall seksjonen «Gjenstående gjennomføring og kontroll» eller tilsvarende, og behold historiske løst-avsnitt som historikk.

## Downstream usability — adequate

FR-1–FR-14 er unike; FR-14 ligger tematisk i §4.3, og forklaringen på nummereringen er bevart. UJ-1 har navngitt hovedperson, FR-er og SM-er er koblet, og nye beslutnings-ID-er er sporbare til referatet. P-08s datafeil og P-11s null gyldige er tydelig skilt. Mekanisk krysshenvisningskontroll bør likevel kjøres på alle berørte filer, særlig etter at story 5.9 ble lagt til.

### Findings

- **[medium] P-08 ligger utenfor en uttrykkelig FR-konsekvens for kandidatvurderingen** (§4.2 «Nødvendig datadekning», FR-1/FR-6) — stoppregelen er tydelig i beskrivelsen og §8, men FR-1 sier ubetinget at valget starter filtrering og rangering. *Fix:* Legg til «når nødvendig grunnlag er komplett» i FR-1 og en testbar datafeilkonsekvens knyttet til FR-1 eller FR-6; behold P-08-eksemplene.

## Shape fit — adequate

Dette er et internt verktøy for én operatør. En kort UJ og funksjonsgrupperte FR-er passer bedre enn en stor personakatalog. PRD-en er detaljert fordi den er kilden til stories, arkitektur og sensorens prosessbevis, og de fleste tekniske mekanismene ligger i nedstrøms dokumenter.

### Findings

Ingen.

## Mechanical notes

- FR-ID-ene 1–14 forekommer én gang hver som overskrift; FR-14 står mellom FR-8 og FR-9 for å bevare historiske ID-er.
- Én inline `[ASSUMPTION]` gjelder Kari og er indeksert i §9. §9 har også eldre beslutninger/forutsetninger som ikke er merket inline; det er historisk materiale, ikke nye uavklarte antakelser.
- PRD-en omtaler «de fire ukene» ved Ulempebelastning; den presise definisjonen er 672 faktiske timer i §4.3.
- E-01 er kun basert på gjengitt muntlig uttalelse uten notert forelesningsdato. PRD-en sier dette, og hevder ikke en ny skriftlig emneregel.

## Etter retting — 2026-11-10

Oppfølgingskontroll av gjeldende PRD og story 5.3/5.4: De seks funnene over er rettet. FR-3 sier nå **skal** og presiserer halvåpne intervaller med ett minutts overlapp. FR-1 knytter rangering til komplett datagrunnlag og har egen datafeilkonsekvens. FR-7/FR-14 krever identisk fullstendig strukturert input for reproduserbarhet. FR-11 navngir tillatte påstandstyper, mens story 5.3/5.4 krever kontrakt og negative faktatester. §8 heter nå «Gjenstående gjennomføring og kontroll» og viser story 5.9 som planlagt i backlog.

**Endelig vurdering: Excellent** etter rubrikkens graderingsregel: alle sju dimensjoner er sterke eller adekvate, og ingen høye eller kritiske dokumentfunn står igjen. Dette vurderer dokumentets beslutningsklarhet og testbarhet; KI-kontraktens konkrete skjema, implementasjon, apptester og P-13s brukerprøve gjenstår som uttrykkelige prosjektoppgaver.
