# KI-logg: oppfølging etter gjennomgangen av PR #24 (story 4.7)

Dato: 2026-11-21. Utført av Claude (Opus 5.5) i Claude Code, direkte i økten uten
`bmad-build`. Endringene er små og lette å etterprøve, og gikk rett på `main` etter
Ragnhild Sætrens valg (AGENTS.md Policy).

## Oppgave og prompt

Tre anbefalinger fra Ragnhilds gjennomgang av PR #24 (2026-11-15,
`.logs/ragnhild/985-2026-11-15-17-02-30-gjennomgang-pr-24.md`). Etter en forklaring av
hva hver endring går ut på, ba Ragnhild ordrett:

> ja gjør alle 3

## Leveranse

1. **8 nye testrader i `backend/tester/regelmotor/test_ulempebelastning.py`.** Testen
   dekket 8 av de 16 rutene i KS-03-tabellen
   (`docs/beslutninger/ks-03-tidskategorier-2026-11-15.md`), nesten bare fredag og
   lørdag. De nye radene er de fire vakttypene mandag–torsdag (dag mandag 16.11,
   mellom tirsdag, kveld onsdag, natt torsdag til fredag), lørdag natt og søndag dag,
   mellom og kveld. Datoene ligger utenfor sommertidsskiftene. Fasiten er skrevet av fra
   KS-03-tabellen, ikke fra programmet.
2. **Kommentar i `backend/domene/regelmotor/vurdering.py`** der vinduene slås sammen:
   ulempevinduet på 672 t går alltid lengst tilbake, så regelvinduenes startside avgjør
   aldri datadekningen og testes ikke gjennom denne veien.
3. **`observer(kandidat, vakt, **kw)`** i `test_beregner_kun_for_gyldige`, slik at
   spionen sender videre nøkkelordargumenter (for eksempel `tak`) og ikke feiler av
   feil grunn.

## Vurderinger og rettelser

- Kommentarens påstand ble kontrollert før commit. For en vakt som starter hver hele
  time gjennom 400 døgn fra 2026-01-01 (Europe/Oslo, begge sommertidsskiftene med)
  startet ulempevinduet før vinduene til kolliderende vakt, 11-timersregelen og
  35-timersregelen. Reglene går høyst 7 døgn tilbake.
- Ingen produksjonslogikk er endret. Generert kode måtte ikke rettes.

## Kvalitetssikring

- Hele backend: 733 av 733 bestått (725 før, pluss 8 nye), macOS.
- De nye radene bestod med en gang. Det betyr at koden stemmer med KS-03 for alle 16
  ruter. Radene er ikke vist å kunne feile ved mutasjon, men fasiten er uavhengig av
  koden.
- Ingen uavhengig gjennomgang. Endringene gikk rett på `main`, og commit-meldingen og
  denne loggen er sporet.
