# Epic 3 Context: Godkjenning av erstatter

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Turnusansvarlig velger en hvilken som helst Gyldig kandidat, ikke nødvendigvis den første i listen, og godkjenner i to steg: først velger hun Kandidaten og ser en egen godkjenningsflate, deretter bekrefter hun med «Godkjenn erstatning». Først da kjører API-et de harde reglene på nytt og bemanner Vakten, gjennom én eneste skrivevei i lagringsadapteren. Bekreftelsen vises på Vaktvalg. Epicet sikrer at mennesket alltid tar sluttbeslutningen, og at systemet aldri gjennomfører en endring på egen hånd. Etter epicet virker hele flyten fra innlogging til godkjenning. Epicet er ikke blokkert og bygges før rangeringen. Rangering, kostnad, belastning, avviksnotat og KI-forklaring på kandidatkortet kommer i Epic 4 og 5.

## Stories

- Story 3.1: Velge kandidat og se godkjenningsflaten
- Story 3.2: Gjennomføre godkjenning og bemanne vakten

## Requirements & Constraints

- **Menneskelig sluttbeslutning (FR12, NFR5):** ingen endring i Turnus eller Vakt før turnusansvarlig har trykket «Godkjenn erstatning». Ingen kodevei gjennomfører en Godkjenning automatisk. Det håndheves i API-et, ikke bare i frontend. En test viser at det å åpne godkjenningsflaten ikke endrer databasen.
- **Bare Gyldige kandidater (NFR2):** godkjenningsflaten for en Ansatt som er utelukket av en hard regel, eller som ikke finnes, gir feilformen `{kode, melding}` og en nøytral melding, ikke et bekreftelsesbilde. Testen for en utelukket Ansatt bindes ikke til én bestemt regel, fordi regelsettet vokser (OP-13).
- **Ny regelkontroll ved Godkjenning:** de fire harde reglene kjøres på nytt mot gjeldende Turnus før noe lagres. Er Kandidaten ikke lenger gyldig, lagres ingenting, og brukeren får en nøytral melding. Ved ny kontroll må Vaktens egen rad holdes utenfor Kandidatens vakter, ellers kolliderer Kandidaten med vakten hun godkjennes for (utsatt funn fra story 2.2).
- **Datafeil (P-08):** ukjent eller ugyldig nødvendig grunnlag stopper Godkjenning. Ingenting lagres, og datafeilen vises atskilt fra «ingen gyldige». En feiltilstand viser aldri godkjenningsknappen.
- **Endret grunnlag og sene svar (P-09):** godkjenningen skal gjelde grunnlaget som faktisk ble vist. Har beslutningsgrunnlaget endret seg siden visningen, vises nye beregninger og brukeren må bekrefte på nytt før lagring. Et forsinket svar for en tidligere Vakt eller Kandidat forkastes og erstatter aldri den aktive visningen. Teknisk løsning (dataversjon, transaksjon, forespørselsidentitet) er ikke valgt og avgjøres i storyen.
- **Dublettvern:** en ny Godkjenning for en Vakt som allerede er bemannet, for eksempel ved dobbeltklikk, avvises med en feilkode. Det finnes bare én Godkjenning per Vakt.
- **Varig lagring (P-12):** Godkjenningen lagres varig (hvem, hvilken Vakt, når) og er synlig når Turnusen åpnes på nytt. Vist forklaring og beregningsgrunnlag lagres ikke historisk i v1.
- **Ingen varsling (UX-DR26):** ingen SMS eller annen varsling til valgt Kandidat.
- **Testdata (OP-13):** tester bruker Kandidater som også er gyldige etter story 2.4, for eksempel Jonas Bakke for #4127. Anders Strand faller ut av #4127 med 35-timersregelen.
- **Dokumentasjon:** KI-generert kode logges i `docs/ki-logg/`. Grensesnittet er bare på norsk bokmål.

**Uklart i kildene (avklares i storyen, ikke fyll inn med antakelser):**

1. **Hvem lagres:** PRD sier at det lagres hvem som overtar Vakten og når. Mockupen sier at handlingen registreres med turnusansvarliges navn og tidspunkt. Om godkjennende bruker også skal lagres, avgjøres i 3.2.
2. **P-09 før Epic 4:** kostnad, timer og preferanser finnes ikke ennå. 3.2 må avgjøre hva «beslutningsgrunnlag» er nå, og hvordan endringer oppdages slik at Epic 4 og 5 kan utvide det.
3. **URL-en:** mockupen viser `/vakt/4127/godkjenning`, men akseptkriteriene krever at URL-en identifiserer Kandidaten.

## Technical Decisions

- **Én skrivevei (AD-5):** `adaptere/lagring` eier skjemaet og har én eneste skrivefunksjon for Godkjenning. Den krever et fullstendig Godkjenning-objekt og er den eneste kodeveien som kan markere en Vakt som bemannet. Tabellen for Godkjenning opprettes i 3.2. En test viser at ingen andre endepunkter endrer bemanningen. Skjemaet krever at en Vakt enten mangler bemanning eller har en tildelt Ansatt, så skrivingen må endre begge i samme transaksjon. Det finnes ingen migreringer, så nye tabeller legges til av `create_all`.
- **Domenet (AD-1, AD-2):** regelkontrollen ved Godkjenning gjenbruker regelmotoren i `domene/regelmotor`. Domenet importerer aldri `adaptere`, og konverteringen fra SQLAlchemy skjer i lagringsadapteren.
- **API-kontrakten (AD-4):** faktiske feil har formen `{kode, melding}`. Frontend viser tekst fra sin egen tekstliste ut fra `kode`, aldri `melding`. Datafeil er et 200-svar med `status: "datafeil"`, `kode: "mangler_turnusgrunnlag"` og `datagrense`, holdt atskilt fra `ingen_gyldige_kandidater`. Feilkodene for utelukket eller ukjent Kandidat, ikke lenger gyldig, endret grunnlag og allerede bemannet er ikke fastsatt og avgjøres i storyene. Tidspunkt sendes som ISO 8601 med offset.
- **Nytt endepunkt (OP-13):** 3.1 innfører et nytt endepunkt og en ny flate som 3.2 bygger videre på. Derfor går 3.1 i branch med PR.
- **Sesjon (AD-3):** alle endepunktene krever gyldig JWT-sesjon. Utløpt sesjon sender brukeren til Logg inn.
- **Bemannede vakter:** vaktdetaljene og kandidatlisten gjelder bare vakter som mangler bemanning. Etter Godkjenning forsvinner Vakten fra «Krever handling».

## UX & Interaction Patterns

- **Egen flate, ikke dialog (UX-DR17):** godkjenningsflaten har egen URL. Brødsmulestien er `Turnus > <avdeling> > Vakt #<nr> > Kandidater > Godkjenning` (UX-DR3). Flyten er lineær, uten sidemeny.
- **Kandidatkort:** i Epic 3 viser kortet navn (`heading`) og Kompetansenivå. Kostnad, arbeidsbelastning, ulempe og forklaringspanel kommer i Epic 4 og 5. Mockupen viser også Vaktens nummer, type, dato, tid og hvem som meldte fra øverst.
- **Bekreftelsesboks (UX-DR19, UX-DR22):** boksen viser hvem som settes inn i hvilken Vakt, i stedet for hvem, med «Avbryt» (`button-secondary`) og «Godkjenn erstatning» (`button-primary`). Statuslinjen «Ikke gjennomført — venter på eksplisitt godkjenning» står til brukeren bekrefter. «Avbryt» fører tilbake til kandidatflaten uten tilstandsendring.
- **Vellykket godkjenning (UX-DR20):** brukeren sendes til Vaktvalg. Der står en kort bekreftelse øverst, for eksempel «Erstatning bekreftet — Jonas Bakke er satt opp på Vakt #4127», og Vakten står blant de bemannede.
- **Tone (UX-DR23):** teksten er kort og nøytral, uten utropstegn og uten språk som antyder at systemet har valgt noe. Avvik fra listen er en gyldig arbeidsflyt, ikke en advarsel. Avviksnotatet (valgt ≠ topprangert) kommer med rangeringen i Epic 4.
- **Tilgjengelighet (UX-DR24, P-13):** begge knappene kan nås og aktiveres med tab og enter, med semantisk HTML. Komponentene bruker bare designtokens (AV-13), og innholdet har `max-width: 1180px` (AV-14). Desktop er bindende nå.

## Cross-Story Dependencies

- Epicet bygger på story 1.4 (sesjon), 1.5 (Vaktvalg med «Krever handling»), 1.6 (vaktvalg og vaktdetaljer) og kandidatlisten fra Epic 2. Story 3.1 startes før 2.4 er ferdig (OP-06, OP-13) og bruker listen slik regelmotoren gir den, uansett hvor mange regler som finnes.
- 3.1 og 2.4 endrer begge `frontend/src/komponenter/Kandidatflate.tsx` og `frontend/src/tekster.ts`. Endringene i 3.1 holdes små der, og den som merger sist, løser konflikten.
- 3.2 forutsetter flaten og endepunktet fra 3.1, og regelkontrollen bruker det fullstendige regelsettet når 2.4 er merget.
- Nedstrøms: Epic 4 legger kostnad, belastning, ulempe og avviksnotatet på godkjenningsflaten. Epic 5 legger til forklaringspanelet med reservetekst, og godkjenningen skal virke også når Avveiningen feiler. En Godkjenning endrer arbeidsbelastningen, så demo-forklaringer med gammel hash skal ikke vises (AD-6). P-09 må utvides når kostnad og preferanser blir en del av grunnlaget.
