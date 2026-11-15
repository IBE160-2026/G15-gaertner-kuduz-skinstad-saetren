# Epic 3 Context: Godkjenning av erstatter

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Turnusansvarlig skal kunne velge en gyldig erstatter for én ubemannet vakt, kontrollere valget på en egen flate og deretter bekrefte det eksplisitt. Først ved bekreftelsen bemannes vakten, og resultatet vises i vaktoversikten. Dette gir en sammenhengende flyt fra innlogging til varig vaktendring, der mennesket tar sluttbeslutningen. Epicet fungerer før rangering, kostnad, belastning og KI-forklaring legges til i senere epics.

## Stories

- Story 3.1: Velge kandidat og se godkjenningsflaten
- Story 3.2: Gjennomføre godkjenning og bemanne vakten

## Requirements & Constraints

- Bare kandidater som består alle gjeldende harde regler kan velges. Reglene kjøres på nytt mot gjeldende turnus ved bekreftelse, før lagring. En kandidat som da er utelukket, gir en nøytral feilmelding og ingen tilstandsendring.
- Å åpne eller avbryte godkjenningsflaten endrer aldri turnusen. Det finnes ingen automatisk godkjenning: bare turnusansvarliges eksplisitte bekreftelse kan bemanne vakten. Systemet sender ingen melding til den ansatte.
- Ukjent eller ugyldig nødvendig grunnlag stopper både kandidatvurdering og godkjenning. Vis datafeil særskilt fra tilfeller med null gyldige kandidater. Dokumentert fri er null timer; ukjent historikk er ikke fri (P-08).
- Godkjenningen skal gjelde beslutningsgrunnlaget brukeren faktisk så. Ved endret grunnlag vises oppdaterte data og det kreves ny bekreftelse. Forsinkede svar for en tidligere vakt eller kandidat kan ikke erstatte aktiv visning (P-09). Løsningen må kunne utvides når kostnad, timer og preferanser kommer i senere epics.
- Lagre hvem som overtar hvilken vakt og tidspunktet for godkjenningen varig. Etter vellykket bekreftelse er vakten bemannet og står ikke lenger under «Krever handling». En ny godkjenning av samme vakt avvises, også ved dobbeltklikk. Vist KI-forklaring og beregningsgrunnlag lagres ikke historisk i kjerneversjonen (P-12).

## Technical Decisions

- Lagringsadapteren eier SQLAlchemy-skjemaet og har én skrivefunksjon som tar et fullstendig Godkjenning-objekt. Den er eneste kodevei som kan markere en vakt som bemannet. Godkjenning og vaktens tildeling skrives atomisk; databasen tillater høyst én Godkjenning per vakt (AD-5).
- Regelmotoren ligger i den rene domenekjernen. Lagringsadapteren konverterer mellom lagringsmodeller og domenetyper; domenet importerer aldri adaptere (AD-1, AD-2). KI beregner ikke harde regler eller godkjenner vakter.
- API-et krever gyldig sesjon. Feil har formen `{kode, melding}`, og klienten velger norsk tekst etter `kode`. Datafeil fra kandidatvurdering er en egen vellykket respons med status `datafeil` og kjent datagrense der den finnes; den må ikke behandles som tom kandidatliste (AD-3, AD-4).
- Datoer og klokkeslett over API-et bruker ISO 8601 med offset. Turnusens beregninger bruker `Europe/Oslo`, slik at de samme harde reglene gir samme resultat også rundt sommertid.

## UX & Interaction Patterns

- Flyten er lineær: kandidatlisten fører til en egen godkjenningsflate med egen URL og brødsmulesti. Bekreftelsesboksen viser valgt ansatt og vakt, med «Avbryt» og «Godkjenn erstatning». Statusen viser at endringen ikke er gjennomført før bekreftelsen.
- Etter lagring returnerer brukeren til Vaktvalg og ser en kort, nøytral bekreftelse øverst. Feil og endret grunnlag skal være forståelige uten å antyde at systemet tok valget. «Avbryt» går tilbake uten lagring.
- Bruk semantiske knapper som kan aktiveres med tab og enter, designtokens og innhold med maksimal bredde 1180 px (AV-13, AV-14). V1 skal fungere i smale nettleservinduer på datamaskin; mobil og nettbrett er v2 (AV-17).

## Cross-Story Dependencies

- Epicet bygger på sesjon, vaktoversikt, vaktdetaljer og kandidatlisten fra Epic 1 og 2. Godkjenningsflaten og lesing av valgt kandidat etableres før lagring og bekreftelse. Regelkontrollen ved lagring bruker hele det implementerte regelsettet, inkludert daglig og ukentlig hvile.
- Epic 4 utvider beslutningsgrunnlaget med kostnad, timer, preferanser, ulempe og rangering. Epic 5 legger til KI-forklaring. Godkjenningen må fortsatt fungere når forklaringen feiler; foreldede forklaringer skal ikke brukes etter endret grunnlag.
