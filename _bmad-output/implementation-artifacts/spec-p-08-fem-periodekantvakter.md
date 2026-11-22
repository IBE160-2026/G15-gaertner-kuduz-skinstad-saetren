---
title: 'P-08: ny vurdering av fem periodekantvakter'
type: 'chore'
created: '2026-11-22'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent">

## Intent

**Problem:** API-testene bruker flyttet #4127 for periodekanten og 404 for bemannede #4261/#4265. De dokumenterer ikke direkte ny vurdering og godkjenning av alle fem #4261–#4265 etter P-08.

**Approach:** Suppler eksisterende API-tester i isolert database. Marker hver av de fem som ubemannet uten å flytte tidspunktene; kontroller datafeil og datagrense i kandidatliste, godkjenningsgrunnlag og POST, og uendret database. Bevar #4127/#4189-fasiten, KS-04 og produksjonskode. Ingen nettverk eller betalte KI-kall.

</frozen-after-approval>

## Implementation Notes

Avgrenset testtillegg på eksisterende main; ingen ny branch eller PR. Konteksten er undersøkt av en egen agent etter AGENTS.md. Gjenbruk `øyeblikksbilde`, `logg_inn`, `sti` og isolerte fixtures i `backend/tester/api/test_godkjenningsgrunnlag.py`. Direkte GET for bemannede vakter skal fortsatt være 404.

Testen låser opprinnelig vakttype og start/slutt, gjentar kandidatvurderingen og prøver to kandidat-ID-er med både feil og korrekt kandidatbundet merke. Alle tabeller sammenlignes før/etter. Ingen produksjonskode, migrasjon, seeddata eller KS-04-vedtak er endret.

## Review Triage Log

| Funn | Vurdering og oppfølging |
| --- | --- |
| Blind gjennomgang: bare feil grunnlagsmerke prøves | low, nyttig styrking av beviset. Gjeldende merke beregnes også; begge må gi samme datafeil før andre kontroller. |
| Blind gjennomgang: seedtidene kan endres uten at testen oppdager det | low, rettet med eksplisitt dato, vakttype og start/slutt for alle fem. |
| Uavhengig grensekontroll etter retting | Ingen funn; 5 målrettede tester bestod hos gjennomgangsagenten. |

## Verification

219 tester bestod: `tester/api/test_godkjenningsgrunnlag.py`, `tester/api/test_kandidater.py`, `tester/lagring/test_testdata.py`, `tester/regelmotor/test_rangering.py`, `tester/ki/test_avveining.py` og `tester/api/test_avveining.py`. Falsk KI-transport; ingen nettverk. 54 eksisterende komponenttester i fire relevante moduler bestod i én sekvensiell frontendkjøring. UI for datafeil #4261 er kontrollert mot ekte backend i separat database; se [kontrollrapporten](../../docs/testing/2026-11-22/kontroll.md).
