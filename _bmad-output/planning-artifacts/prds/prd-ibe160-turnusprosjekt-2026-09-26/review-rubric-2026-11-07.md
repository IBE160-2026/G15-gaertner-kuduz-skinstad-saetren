# PRD Quality Review — Turnushjelperen

## Overall verdict
Den avgrensede oppdateringen kan ferdigstilles: AV-04, AV-05, AV-06 og K-03 er innarbeidet korrekt, og FR-12 viderefører allerede beskrevne krav fra story 3.2 og AD-5 uten å innføre tokenversjoner, atomisitetskrav eller nye feilprotokoller. Ingen nye blokkerende avvik er funnet i diffen. Hele PRD-en har fortsatt kjente uavklarte krav innen kostnad, KI-feil/faktakontroll og nøyaktig belastningsterskel; de er nå synlige i §8 og hindrer at dokumentet alene regnes som ferdig implementasjonsgrunnlag for disse delene.

Gjennomgangen er utført 2026-11-07 mot arbeidstreets PRD og diff fra HEAD, beslutningsreferatets AV-04/05/06, K-02/03/04 og OP-03, samt epics story 3.2 og arkitektur AD-5. Den vurderer dokumentkrav, ikke juridisk fullstendighet eller implementasjon. Ingen av funnene nedenfor er nye feil innført av denne oppdateringen.

## Decision-readiness — adequate

§4.2 oppgir både vedtatt prototypemodell og begrensningen mot full juridisk kontroll. §4.4 beskriver særregelen for like faktorverdier, reell poenglikhet og visningsavrunding med riktig kilde-ID. Den tidligere anbefalingen om to desimaler er ikke videreført; vedtaket om én desimal gjelder. §8 skiller samordnet innhold fra konkrete åpne valg og fastholder at 32,4 timer er et forslag.

Ingen funn i det nye vedtaksinnholdet.

## Substance over theater — strong

Presiseringene gir konkrete kontrakter: 11:00 mot 10:59 hvile, 35:00 mot 34:59 ukefri, 50 faktorpoeng ved like verdier og ny kontroll før lagring. Kandidatgrunnlag og preferansenes demonstrasjonsperiode er nødvendige avgrensninger fra AV-06. De 15 preferanseeksemplene er nyttig fasit for SM-7 og er bevart. Ingen nye generiske kvalitetskrav eller overflødige personas er lagt til.

## Strategic coherence — strong

Arbeidsdelingen mellom deterministiske beregninger, KI-tolkning/forklaring og menneskelig godkjenning består gjennom §1, FR-2–FR-14 og §5. Vektene 40/20/15/25 er uendret. Tilgjengelighetsantakelsen og den avgrensede hvilemodellen støtter den vedtatte prototypen for én erstatning om gangen. SM-C1 og SM-C2 bevarer relevante motmetrikker.

## Done-ness clarity — thin

De oppdaterte FR-4, FR-5, FR-9 og FR-12 gir utvikleren tydeligere forventede utfall. Blant annet er det nå mulig å formulere grensetester og teste varig bemanning og avvist dobbel godkjenning direkte mot PRD. Kjente åpne deler har fremdeles ikke én fullstendig fasit; dette er riktig bevart fremfor å avgjøre spørsmål på gruppens vegne.

### Findings
- **medium** Kostnadsverdien og ukefordelingen er fortsatt åpne (§4.3 FR-7, §4.4, §8 punkt 3; eksisterende) — «kostnadsvurdering» og «denne uken» skiller fortsatt ikke entydig mellom vaktkostnad, timesats og ukekostnad, eller timefordeling ved ukeskifte. *Fix:* Ta nødvendig avklaring og før et konkret regneeksempel inn i FR-7 før kostnadsmodellen implementeres; ingen formel bør innføres som del av denne samordningen.
- **medium** Feiltilstandene i KI-laget mangler full akseptkontrakt (§4.5 FR-10/11, §8 punkt 4–5; eksisterende) — «ubrukelig svar» og registrert tekst uten vellykket tolkning har fortsatt ikke avklart behandling for alle relevante situasjoner. *Fix:* Følg OP-03 før story 5.1/5.2 er ferdige og avklar faktakontroll/KI-input i relevant videre arbeid; behold disse punktene åpne nå.
- **medium** Omtrentlig visningsgrense kan ikke gi én grensetestfasit (§4.3 FR-8, §8 punkt 6; eksisterende) — «~90 %» har fortsatt ingen bestemt sammenligningsgrense, og K-02 fastslår at 32,4 timer ikke er vedtatt. *Fix:* Avklar K-02 før den eksakte fargegrensen ferdigstilles. Visningsavrunding etter K-03 avgjør ikke dette valget.

## Scope honesty — strong

§4.2 sier uttrykkelig at øvrige ansatte antas tilgjengelige og at dette ikke er en faktisk tilgjengelighetsgaranti. FR-10 avgrenser preferanser til demonstrasjonsperioden. §5 utelater full juridisk etterlevelse og komplett lønnsmodell. Oppdateringen innfører ikke en ny fraværsmodell, daterte preferanser, ny KI-fallback eller utvidede harde regler. §8 gjør kjente ikke-vedtatte spørsmål tydelige.

## Downstream usability — adequate

Stabile FR-ID-er er bevart, inkludert begrunnet plassering av FR-14. De nye kildehenvisningene gjør det mulig å spore hvile, rangering, kandidatgrunnlag og godkjenning til vedtak eller allerede skrevne krav. Relativt til PRD-mappen peker lenkene til beslutningsreferatet, epics og arkitektur på eksisterende filer. Epics sin foreldede status for ÅB-5/6 og antakelsen i story 2.1 må fortsatt samordnes, men er ikke skjult eller gjort til nye produktvalg her.

## Shape fit — adequate

Funksjonsgrupper med testbare konsekvenser passer fire utviklere og én operatørrolle. Den ene fiktive brukerreisen er tilstrekkelig og beholdes. Nye presiseringer er plassert ved sine respektive regler, rangering og godkjenning. §8 er lang og blander åpne spørsmål med historikk, men en full strukturendring er ikke nødvendig for den bestilte vedtaksoppdateringen.

## Mechanical notes

- **low** Antakelsesindeksen er ikke et fullstendig speil av inline-markeringene (§2.3 og §9; eksisterende) — den åpne antakelsen om presentasjon av «ingen gyldige kandidater» er merket inline, men ikke i §9. Omvendt inneholder §9 også bekreftede eller historiske valg. *Fix:* Samordne indeksen ved neste dokumentopprydding; dette påvirker ikke de nå innarbeidede vedtakene.
- Ingen nye brutte FR-ID-er eller kildehenvisninger funnet.
- Dokumentstatus `final` betyr ferdigstilt dokumentversjon; §8 og den nye samordningsnotisen gjør det tydelig at ikke alle produktvalg eller implementasjoner dermed er ferdige.

## Funnopptelling

Critical: 0. High: 0. Medium: 3. Low: 1. Alle fire funn er eksisterende forhold, ikke regressjoner fra den avgrensede oppdateringen.
