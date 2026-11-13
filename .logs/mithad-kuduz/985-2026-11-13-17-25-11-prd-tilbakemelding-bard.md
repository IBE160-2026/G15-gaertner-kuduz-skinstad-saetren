# PRD rettet etter Bårds tilbakemelding

## 2026-11-13 kl. 17:25 — Mithad Kuduz

### Oppgave

Bård Pettersen la inn formativ tilbakemelding på PRD-en 12.11 (`tilbakemelding-prd.md`). Mithad ba om å gå gjennom den og rette punktene.

### Plan

- Lese tilbakemeldingen, hele PRD-en og AD-7, og sjekke det som er bygd i story 1.3 og 1.4 (innlogging og økt).
- Mithads valg:
  - Alle punktene rettes. Tall som ikke er vedtatt, merkes som forslag.
  - Arbeidet gjøres i branchen `docs-prd-tilbakemelding-bard` med PR.
- Ingen vedtatte krav skal endres. Endringene er bare struktur, ordlyd og sporing.

### Resultat

- **`3f89bcf`:**
  - **4.1:** Kravtekstene står nå alene, og ID-ene er samlet i en ny §10 Sporing. Ordlisten har fått Ansatt, Datafeil, Demo-modus og Reservetekst. Kompetansenivå følger skalaen 1–4.
  - **4.2:** §0 forklarer hva `final` betyr. §8 har nå Åpne spørsmål med eier og frist: mobil og nettbrett, sensornøkkelen og SM-tallene. Historikken er flyttet til `.memlog.md` og referatet.
  - **4.3:** FR-13 har fått testbare krav, hentet fra det som er bygd.
  - **4.4:** FR-10 bruker tallene fra AD-7. SM-3, SM-4 og SM-C2 har forslag, merket «ikke vedtatt».
  - **4.5:** Hvert FR er merket Kjerne, og §6.2 skiller Etter kjerne fra Strekk.
  - **Mekaniske funn:** `[ASSUMPTION]` er merket der antakelsene står i teksten.
- **Kvalitetssikring:**
  - Hver erstatning måtte treffe nøyaktig én gang.
  - Lenkemålene og storynumrene i §10 er kontrollert mot epics og filene.
  - PRD-en er cirka 7 000 ord. Den var cirka 6 500 før, så sporingstabellen og ordlisten veier opp for historikken som ble flyttet ut.
- **Funn utenfor PRD-en:** Bårds fil `technology.md` i arkitekturmappen gjelder et annet prosjekt (pytagoras-website-v2).
- **SM-tallene:** Mithad gikk gjennom forslagene og valgte dem som anbefalt. SM-4 ble endret til «minst den viktigste faktoren med tall, og alle fire nøkkeltall vises ved siden av», fordi det første forslaget kolliderte med P-06. Forslagene er merket som Mithads, ikke vedtatt av gruppa.
- Ikke pushet, og ingen PR ennå.

### Åpne punkter

- PR for PRD-rettingene, og gjennomgang fra et annet gruppemedlem.
- Gruppa må ta stilling til forslagene for SM-3, SM-4 og SM-C2 og til de tre åpne spørsmålene i §8.
- Spør Bård om `technology.md` i arkitekturmappen er lagt der med vilje.
