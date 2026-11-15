# Adversarial grenseflatekontroll etter Update — 2026-11-15

## Dom

**Bestått med én liten dokumentsamordning.** D1–D6 lukker de seks nye dokumentfunnene i Validate-rapporten. Jeg fant ingen ny motstrid mellom AD-1–AD-7 som tvinger to AD-kompatible enheter til å bli uforenlige. Én generell setning i `epics.md` motsier fortsatt den avtalte feilflyten for preferansetolkning. Dette er dokumentasjon, ikke en påvist kodefeil.

## Metode og bevisgrense

Jeg leste gjeldende arbeidskopi av [spinen](../ARCHITECTURE-SPINE.md), [.memlog.md](../.memlog.md), [AGENTS.md](../../../../../AGENTS.md), [PRD](../../../prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md), [epics](../../../epics.md), UX [EXPERIENCE](../../../ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md), [beslutningsreferatet](../../../../../docs/beslutninger/avklaringspunkter.md) og sensorveiledningens krav til sporbar plan–kode-sammenheng. Relevant kode er `backend/adaptere/api/sesjon.py`, `backend/adaptere/lagring/modeller.py`, `backend/domene/regelmotor/elleve_timer.py` og `trettifem_timer.py`. Jeg prøvde å konstruere to utviklere som følger AD-ene, men likevel bygger uforenlige eierskap eller datakontrakter. Jeg kjørte ingen app- eller live-KI-test. Story 3.2 og 5.x er fremtidig implementasjon.

## Funn A1 — Lav: epics lover alltid lagret tolkning også ved venting og feil

`epics.md:67` sier at regelmotoren **alltid** får «en lagret, allerede tolket verdi». Det passer ved vellykket tolkning, men AD-1 i spinen (`:48`) og PRD FR-10 (`prd.md:296–298`) krever ved venting eller feil midlertidige 50 poeng med egen status, uten oppdiktet `TolketPreferanse`. Story 5.1 (`epics.md:988–995`) beskriver den samme feilflyten. En regelmotorutvikler som følger «alltid»-setningen kan kreve en vellykket modell også når KI ennå ikke har svart; KI-utvikleren kan korrekt levere bare feilstatus. Rett setningen til at lagret tolkning brukes **når den finnes**, og at venting/feil gir midlertidige 50 poeng med egen status. `adaptere/api` gjør aldri et live KI-kall under Rangering. Ingen nåværende KI-kode finnes som kan være feil her.

## D1–D6 og viktige grenser kontrollert

- **D1 / OP-10, sesjon:** Rolletabellen (`spine:37`) gir lagring bruker/passordhash, ikke sesjon. AD-3 (`:69–73`) gir API-et utstedelse og cookie-setting, nettleseren lagring/sending. `BrukerRad` finnes i `modeller.py:128`; JWT håndteres i `sesjon.py:44–99`. En lagringsutvikler har ikke lenger grunnlag for egen sesjonstabell.
- **D2 / P-05, tolkning:** AD-1 (`:48–50`) skiller ny semantisk tolkning i KI-adapteren fra deserialisering/validering av tidligere lagret verdi i lagringsadapteren. Bruk krever samme Ansatt og tekst. `epics.md:63,975–987` følger skillet. Valg av lagringsfelt og eventuell formatversjon ligger uttrykkelig i story 5.1; det er et implementasjonskrav, ikke en ny påvist dokumentfeil.
- **D3 / AV-04/P-02, tid:** `spine:109` og `epics.md:82,255` beskriver UTC i lagring og faktisk intervallregning og `Europe/Oslo` for kalendergrenser/visning. `OsloTid` i `modeller.py:21–45`, `elleve_timer.py:48–64` og `trettifem_timer.py:33–72` følger samme deling. Ingen DST-kodefeil er påvist ved denne dokumentkontrollen.
- **D4–D6:** Containerdiagrammet (`spine:134`) sier lokal HTTP via Vite-proxy, `.env.example`-kommentaren (`:181`) samsvarer med AGENTS.md, og frontmatter/memlog registrerer Update med AD-ID-ene beholdt. Hosting er fremdeles utsatt (`spine:202`).
- **Godkjenning / P-08/P-09:** AD-5 (`:83–87`) binder identiteten til vist grunnlag, ny kontroll og skriving til én konsistent databasetilstand med unik Godkjenning per Vakt. Story 3.2 (`epics.md:651–688`) eier konkret transaksjonsmekanisme og samtidighetstester. Det finnes foreløpig bare GET-grunnlag i `backend/adaptere/api/main.py:292–319`; dette er ikke en påvist kodefeil i denne gjennomgangen.
- **KI-forklaring / P-06/P-07:** AD-1 og AD-6 binder bare gyldige, rangerte kandidater og referansefakta til forklaringsporten og faktakontroll av demooppslag. Kildelinjens modell/dato i `EXPERIENCE.md:62` må bæres av responsskjemaet i story 5.3/5.7, slik Validate-rapporten allerede noterer. `adaptere/ki` er ennå ikke bygget; ingen kjøretidskontrakt er verifisert.

De seks funnene fra 14.11 er kontrollert som eksisterende dokumentkontrakter og er ikke gjenåpnet. A1 er en ny, konkret samordning i `epics.md:67`, ikke en omklassifisering av manglende fremtidig kode.
