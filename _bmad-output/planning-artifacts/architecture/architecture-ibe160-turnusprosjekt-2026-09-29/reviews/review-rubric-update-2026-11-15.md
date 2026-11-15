# Reviewer Gate: rubrikk for oppdatert arkitekturspine — 2026-11-15

## Dom

**Bestått uten nye dokumentfunn i D1–D6.** De godkjente rettingene gir sammenheng mellom rollebeskrivelse, AD-1/AD-3, tidssonekonvensjon, lokal transport, miljøvariabler og endringshistorikk. Dette er en kontroll av dokumentkontrakter og utvalgt kode, ikke bevis for at story 3.2 eller 5.x er implementert.

## Metode og grunnlag

Jeg leste den nåværende `ARCHITECTURE-SPINE.md` og `.memlog.md` etter Update, `AGENTS.md`, gjeldende PRD, `epics.md`, UX `DESIGN.md` og `EXPERIENCE.md`, beslutningsreferatet og relevante kodepunkter. Jeg brukte punktene i `references/reviewer-gate.md`: reelle divergenspunkter, AD-reglenes håndhevbarhet, Deferred, teknologivalg, samsvar med kode og krav, samt drifts- og miljødimensjonen. Teknologienes eksterne aktualitet vurderes i den separate teknologi-linsen; her er påstandene kontrollert mot prosjektets manifest og kode. Ingen app- eller live KI-test er kjørt i denne rubrikkgjennomgangen.

## D1–D6 og samsvar

| Valg | Kontroll | Resultat |
| --- | --- | --- |
| D1 | Rolletabellen sier nå at `adaptere/lagring` persisterer `bruker` med passordhash, mens Godkjenning er planlagt i story 3.2; ingen sesjonstabell påstås. AD-3, `epics.md` innledningsdel og story 1.3/OP-10 beskriver JWT i cookie. `backend/adaptere/lagring/modeller.py` har `bruker`, og `backend/adaptere/api/sesjon.py` håndterer JWT. | Dokumentmotstriden er lukket. |
| D2 | AD-1 skiller ny semantisk tolkning hos `adaptere/ki` fra deserialisering/validering av lagret verdi hos `adaptere/lagring`. Både arkitekturavsnittet i `epics.md` og story 5.1 følger dette. PRD FR-10 krever lagret verdi for aktuell tekst; P-05 krever egen ventende/feilet status. | Kontrakten er sammenhengende. Porttype, lagringsfelt og tester gjenstår i story 5.1. |
| D3 | Konvensjonen og `epics.md` beskriver UTC-lagring/faktisk varighet og Oslo-kalendergrenser/visning. `OsloTid` skriver UTC og leser Oslo; 11- og 35-timersmodulene regner varighet i UTC og sistnevnte setter ukegrenser i Oslo. P-02/AV-04 og PRD krever faktisk forløpt tid over sommertid. | Dokumentasjon og observert kode samsvarer. Ingen ny DST-test kjørt her. |
| D4 | Containerdiagrammet sier lokal HTTP via Vite-proxy med JWT-cookie, i tråd med `frontend/vite.config.ts`, `README.md`, OP-10 og `backend/adaptere/api/sesjon.py`. Hosting står i Deferred. | Lokal transport er presis. |
| D5 | Kildetreets `.env.example`-kommentar sier dokumenterte variabler uten verdier, som `AGENTS.md`, NFR7 og den faktiske eksempelfilen. | Ordlydsfeilen er lukket. |
| D6 | Frontmatter har `updated: 2026-11-15`. Append-only memlog fører de seks tidligere dokumentrettingene, at OP-10 erstattet en eldre sesjonsantakelse, og brukerens valg D1–D6. AD-ID-ene er fortsatt AD-1–AD-7. | Endringsproveniens er ajour før gateavslutning. |

## Good-spine-sjekk

- **Divergens og håndheving:** AD-1/AD-2 gir en testbar importretning; `backend/pyproject.toml` forbyr hele `domene` å importere `adaptere`, og `backend/tester/test_arkitektur.py` kjører kontrakten. AD-3/AD-4 avklarer API–web-kontrakter. AD-5 eier skjema og én konsistent Godkjenning-skrivevei. AD-6/AD-7 avklarer KI-modus, faktakontroll og takt. Det finnes ingen ny uforenlig eier eller mutasjonsvei i D1–D6.
- **Produktdekning:** Capability Map dekker PRD FR-1–FR-14. UX-kravene om status, reservetekst, kildeetikett og lokal desktop-flyt har en plass i AD-ene eller Deferred. Den eksakte API-responsen med modellnavn og dato for kildelinjen må fortsatt fastsettes i story 5.3/5.7, slik Validate-rapporten allerede påpeker.
- **Seed og nåværende kode:** Spinen merker Godkjenning og KI-port som planlagt arbeid. Dagens kode har innlogging, lagring og fire hardregelmoduler; det er ikke påstått at fremtidige akseptkriterier er bestått. SQLAlchemy-versjonen peker til eksisterende `backend/requirements.txt`.
- **Driftsdimensjon:** Lokal kjøring er valgt. Hosting, migreringsverktøy, progressiv forklaringstransport, KI-klientbibliotek og runtime-logging er navngitt under Deferred med naturlige avgjørelsespunkter. Ingen hel dimensjon er taus.

## Åpne implementasjonsporter, ikke funn mot oppdatert dokument

Story 3.2 må implementere AD-5s transaksjon, ny regelkontroll og samtidighetstester. Story 5.1 må bygge `TolketPreferanse`-porten, lagring og lesing med Ansatt-/tekstbinding samt tester; 5.3–5.7 må bygge forklaring, faktakontroll, kildeinformasjon, demooppslag og falsk HTTP-test. Dokumentkontraktene er grunnlag for dette arbeidet, ikke implementasjonsbevis.
