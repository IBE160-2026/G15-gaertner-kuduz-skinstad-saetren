# Dokumentvalidering – PRD-samordning 2026-11-10

- **PRD:** [Turnushjelperen](prd.md)
- **Rubrikk:** [.agents/skills/bmad-prd/assets/prd-validation-checklist.md](../../../../.agents/skills/bmad-prd/assets/prd-validation-checklist.md)
- **Kilde:** [P-01–P-13 og E-01/E-02](../../../../docs/beslutninger/prd-beslutningsgrunnlag-2026-11-07.md)
- **Gjennomgang:** [rubrikkreview med oppfølgingskontroll](review-rubric-2026-11-10.md)
- **Endelig dokumentvurdering:** Excellent etter bmad-prd-rubrikkens graderingsregel; alle sju dimensjoner er strong eller adequate etter retting, uten åpne high/critical-funn. Dette er en vurdering av kravdokumentet, ikke av appen.

## Resultat

Rubrikkgjennomgangen fant først ett høyt, tre middels og to lave dokumentfunn. Alle seks er rettet: FR-3 er obligatorisk, P-08 er en testbar FR-1-konsekvens, FR-7/14 bruker fullstendig beslutningsgrunnlag for reproduserbarhet, FR-11 og story 5.3/5.4 avgrenser og tester påstandstyper, §8 skiller gjenstående gjennomføring fra produktvalg, og P-10B viser til eksisterende story 5.9.

Kontroll av gjeldende filer fant én unik overskrift for hver FR-1–FR-14 (FR-14 står tematisk etter FR-8, uten omnummerering), P-01–P-13 og E-01/E-02 i beslutningsreferatet, ingen manglende relative Markdown-filer i endrede dokumenter, og ren `git diff --check`. `backend/.venv/Scripts/python.exe -m pytest tester/lagring/test_testdata.py -q` ga **39 beståtte tester** for eksisterende seeddata/fasit. Ingen nye appkrav er dermed verifisert i kode.

## Konkrete gjenstående kontroller

- **P-01–P-04:** Domenekode og grense-/visningstester for merkostnad, ukeskifte, sommertid og 32:23/32:24. Ingrid har fortsatt 32 timer i seeddata; høy-belastning-visning er ikke implementert/testet gjennom dette dokumentarbeidet.
- **P-05–P-07:** KI-kontrakt, statusene for venting/feil, nye forsøk, faktakontroll og referanseregel må implementeres og testes mot falsk OpenRouter; manuell språk-/forståelseskontroll gjenstår.
- **P-08/P-09/P-11:** Stopp ved #4261–#4265 og annet ufullstendig grunnlag, forkasting av gamle svar, ny bekreftelse og forskjellen mellom datafeil og null gyldige må testes. KS-04 godkjenner fortsatt bare datadekningen for #4127/#4189.
- **P-10B/P-13:** Story 5.9 er backlog etter kjerneflyten. Gruppen må avklare mobil/nettbrett og dokumentere oppgavebasert forståelsestest før story 4.6 ferdigstilles.
- **E-01/E-02/KS-03:** E-01 bygger på gjengitt muntlig faglæreruttalelse uten kjent forelesningsdato. E-02s avviksliste må sammenholdes med levert app ved innlevering. KS-03s kontroll av tidskategorier for fire vakttyper er ikke dokumentert utført.

Den tidlige `direction-a-fagsystem.html` er merket historisk fordi dens kandidatverdier ikke følger #4127-fasiten. Historiske reviews, modelltestresultater og selve fasiten er bevart. P-07s valgfrie to-kandidatvisning er strekkmål etter v1; P-12B er ikke v1-krav.
