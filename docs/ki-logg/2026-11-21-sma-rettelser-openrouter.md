# KI-logg: små rettelser i OpenRouter-adapteren

Dato: 2026-11-21. Utført av Claude (Opus 5.5) i Claude Code, direkte i økten uten
`bmad-build`. Endringen er avgrenset og lett å etterprøve, og gikk rett på `main` etter
Ragnhild Sætrens valg (AGENTS.md Policy).

## Oppgave og prompt

Ragnhild Sætren, ordrett, etter at agenten hadde listet åpne punkter fra
`.logs/ragnhild/issues.md`:

> Jeg kan ta de små rettelsene på main

Rettelsene var to åpne punkter fra gjennomgangen av PR #30 (2026-11-16):

1. Kommentaren over konstantene i `backend/adaptere/ki/openrouter.py` kalte
   feilreglene «FORSLAG … ikke gruppevedtak», selv om de ble vedtatt som AV-19 samme dag.
2. `urllib_transport` skjulte årsaken til nettverksfeil. Live-kontrollen på macOS
   2026-11-16 ga bare `nettverk`, og sertifikatfeilen (`CERTIFICATE_VERIFY_FAILED`) ble
   funnet først ved å kjøre `urllib` for hånd (`deferred-work.md`).

## Leveranse

- Kommentarene viser til AV-19 for ventetrinnene, budsjettet på 90 s og begge
  429-reglene (60 s uten lesbar reset, minst 1 s). Tidsavbruddet på 45 s per kall står
  ikke i AV-19, og kommentaren sier det.
- Ny funksjon `nettverksårsak`: typenavnet, typenavnet på årsaken i `URLError.reason`
  og OpenSSLs faste kode, for eksempel
  `URLError/SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED`.
- `_send` logger hver nettverksfeil som WARNING: «Nettverksfeil mot OpenRouter: …».
  WARNING vises i terminalen uten eget loggoppsett, i motsetning til INFO-meldingene i
  det andre punktet i `deferred-work.md`.
- 8 nye tester i `backend/tester/ki/test_openrouter.py`.

## Vurderinger og rettelser

- Feilteksten logges ikke, bare typenavn og en kode som må være et ASCII-identifikator.
  Docstringen til `urllib_transport` sier at feilkropper kan gjengi prompt eller nøkkel.
  Feilteksten fra et unntak kan i prinsippet gjøre det samme, så den holdes utenfor.
  Testene legger «Bearer hemmelig» i feilteksten og viser at den ikke kommer med.
- `from None` er beholdt, slik at unntakskjeden heller ikke bærer teksten videre.
- Ingen generert kode måtte rettes etter første kjøring.

## Kvalitetssikring

- `pytest tester/ki`: 90 bestått. Hele backend: 725 av 725 bestått (macOS, Python i
  `backend/.venv`).
- Mutasjonskontroll: med den gamle `Nettverksfeil(type(feil).__name__)` og uten
  logglinjen feilet 4 av de nye testene. Koden ble tilbakestilt etterpå.
- Ingen nettverkskall. `ssl.SSLCertVerificationError` får ikke `reason` satt når den
  lages fra Python, så testen setter den slik OpenSSL gjør. Opplesingen av en ekte
  sertifikatfeil er ikke kjørt på nytt mot OpenRouter.
- Ingen uavhengig gjennomgang. Endringen gikk rett på `main`, og commit-meldingen og
  denne loggen er sporet (AGENTS.md Policy).
