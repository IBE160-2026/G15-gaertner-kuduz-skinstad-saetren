# Tidsbruk og estimat for ferdigstilling

## 2026-11-15 kl. 13:19 — johagartnerHiMolde

### Oppgave
Johannes ba om en vurdering av gruppens tidsbruk, og om et estimat for når appen er ferdig bygget og klar for innlevering, ut fra tempoet de siste ukene.

### Plan
- Hentet tall fra git: PR-merger på `main` med dato, commits per dag, per forfatter og etter type (`Logg:` mot kode), og antall linjer kode mot dokumentasjon siden 2026-11-02.
- Lest sprintstatus (gjenstående storyer) og rekkefølgen og avhengighetene for Epic 4 og 5 i `epics.md`.
- Søkt i `docs/emne/`, brief og planleggingsdokumenter etter innleveringsfristen. Datoen står ingen steder i repoet.

### Resultat
- **Tempo:** 13 av 30 storyer er ferdige. 12 av dem ble ferdige 2026-11-04–15, og 10 av dem 2026-11-08–15 (ca. 1,25 per dag). Det har vært commits hver dag siden 2026-11-02, også i helgene.
- **Tidsbruk:** Planleggingen gikk fra september til 1. november, og bare story 1.1 ble bygd i den perioden. Siden 2026-11-02 er det 340 commits uten merger. 204 av dem er `Logg:`-commits, og 23 rører `backend/`, `frontend/` eller `scripts/`. I samme periode er det skrevet 12 350 linjer dokumentasjon og 9 880 linjer kode og tester. PR-ene gjennomgås og merges som regel samme dag eller dagen etter.
- **Gjenstår:** 17 storyer (3.2, 4.1–4.7, 5.1–5.9). 5.9 er strekkmål etter P-10B.
- **Estimat:**
  - Ren fremskrivning: ca. 28. november.
  - Justert for tyngre storyer (skriveveien i 3.2, rangeringen i 4.4 og 4.7, og KI med 20 kall per minutt og trege live-tester i Epic 5) og for den kritiske stien 4.1–4.3 → 4.4 → 5.2–5.5: ferdig bygget ca. 3. desember (spenn 29. november–8. desember).
  - Med fire parallelle løp: ferdig bygget ca. 28.–30. november. Løpene er 3.2, 4.1–4.3, 4.7 (bygger bare på 1.2) og 5.1 (kan gå parallelt med Epic 4).
  - Innleveringsklar ca. 3–5 dager etter at appen er ferdig bygget. Sluttkontroll fra ren klone, forståelsestesten i P-13, innleveringsteksten og vurderingsmatrisen gjenstår.
- Ingen filer i prosjektet er endret.

### Åpne punkter
- Innleveringsfristen står ikke i repoet. Den bør inn i planen, slik at estimatet kan holdes opp mot den.

## 2026-11-15 kl. 13:25 — johagartnerHiMolde

### Oppgave
Johannes oppga at innleveringsfristen er 2026-12-15 og ba om at loggen pushes.

### Plan
- Holde estimatet opp mot fristen og føre den i loggen og `issues.md`.

### Resultat
- Mest sannsynlig er appen ferdig bygget ca. 3. desember, og innleveringsklar ca. 6.–8. desember. Det gir omtrent en uke buffer før 15. desember. Med fire parallelle løp blir bufferen nærmere to uker.
- I det verste spennet blir appen ferdig bygget 8. desember og innleveringsklar ca. 11.–13. desember. Da er bufferen bare 2–4 dager, og 5.9 (strekkmål) bør kuttes.
- Fristen står fortsatt ikke i noen sporet plan- eller instruksfil.

### Åpne punkter
- Før fristen (2026-12-15) inn i en sporet fil som gruppa ser, for eksempel AGENTS.md eller sprintstatus.
