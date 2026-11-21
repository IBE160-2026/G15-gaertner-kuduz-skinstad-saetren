# Story 5.6 – lekkasjeinvariant

## 2026-11-21 kl. 16:35 — Ragnhild

### Oppgave
Bygge story 5.6 med `bmad-build`: en test som beviser at utelukkede kandidater aldri når KI-laget (NFR2, SM-2). Demodelen (`DemoKiAdapter`) venter på story 5.7. Ragnhild valgte å kjøre på Opus i stedet for Sonnet, som tabellen anbefaler, fordi gruppa har sett feil med Sonnet 5.5.

### Plan
- Branch `story-5.6-utelukkede-aldri-ki`, story satt til `in-progress` og pushet.
- Epic 5-konteksten kompilert på nytt av en underagent, fordi planleggingsfilene var nyere.
- Spesifikasjon: [spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md](../../_bmad-output/implementation-artifacts/spec-5-6-utelukkede-kandidater-naar-aldri-ki-laget.md). Godkjent samlet, selv om den er over tokentaket.
- Implementering ved en underagent på Opus, og gjennomgang ved tre uavhengige underagenter på Opus.

### Resultat
- Ny testmodul `backend/tester/api/test_lekkasjeinvariant.py` med 21 tester. Den kjører hele API-flyten for #4127, som har 4 gyldige og 20 utelukkede (8/7/4/1 etter de fire reglene). Testen bruker ekte `OpenRouterKiAdapter` med registrerende falsk transport, har fire separate invariantkontroller og skiller tolkingsporten fra forklaringsporten. En negativ kontroll gjør alle fire kontrollene røde ved lekkasje, i alle 16 kjøringer. Ingen produksjonskode er endret, og ingen lekkasje ble funnet.
- Gjennomgangen ga 17 funn. Seks ble rettet, og resten ble avvist med begrunnelse. Vurderingen står i spesifikasjonens Review Triage Log.
- Dokumentasjon: KI-loggen `docs/ki-logg/2026-11-21-lekkasjeinvariant.md`, en milepæl i `docs/emne/vurderingsmatrise.md`, et punkt i `docs/testing.md` og et punkt om demodelen i `deferred-work.md`.
- 738 av 738 backendtester er bestått, også import-linter-kontrakten.
- Sprintstatus for 5.6 er `review`. Arbeidet er committet i `93b9c3b` på story-branchen. Det er ikke pushet, og det finnes ingen PR ennå.

### Åpne punkter
- Story 5.7 må legge `DemoKiAdapter` til `ADAPTERFABRIKKER` i lekkasjetesten, parametrisere den negative kontrollen over adapterne og hoppe over HTTP-kontrollen for demo (se `deferred-work.md`).
- PR og gjennomgang av en i gruppa for story 5.6 gjenstår.
