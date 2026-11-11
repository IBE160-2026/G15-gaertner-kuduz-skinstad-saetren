# KI-logg: Story 2.3 – filtrere på 11-timersregelen (daglig hvile)

Dato: 2026-11-11. Grunnlag: [spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-2-3-filtrere-pa-11-timersregelen-daglig-hvile.md), [Epic 2-konteksten](../../_bmad-output/implementation-artifacts/epic-2-context.md), `AGENTS.md` og [avklaringspunktene](../beslutninger/avklaringspunkter.md) (AV-04, AV-07, AV-09, P-08, vedtak A5 i §11, OP-12). Arbeidet ble gjort av Claude Code (Opus 5.5) som implementeringsagent i `bmad-build`, på branchen `story-2.3-elleve-timer`.

## Oppgave og prompt

Instruksjonen til implementeringsagenten: «Read …/spec-2-3-filtrere-pa-11-timersregelen-daglig-hvile.md fully and implement it — the spec is the sole source of truth. Load every file listed in its frontmatter `context:` before you start. When done, report what you changed, how you verified it, and anything left incomplete or risky.»

## Leveranse

- **Ny regel** (`backend/domene/regelmotor/elleve_timer.py`): `ÅRSAK = "11-timersregelen"`, `bryter_elleve_timer` og `vindu`. Hvilen regnes i UTC. En egen vakt som overlapper Vakten, hoppes over (beslutning A, Mithad 2026-11-11), og en vakt som bare møter Vakten, gir 0 t hvile og brudd. Nøyaktig 11 t er gyldig. Vinduet er `[start − 11 t, slutt + 11 t)` i UTC.
- **Vinduet og datafeilsjekken** (`vurdering.py`): `Regel` har feltet `vindu`, og regelen er nummer tre i `REGLER`. Vurderingen går i fast rekkefølge: Vakten valideres (også tidssone på `historikkstart`), så regnes det samlede vinduet ut (alltid minst Vakten), så sjekkes det mot `[historikkstart, datagrense]`, og til slutt valideres Kandidatens vakter mot vinduet. En vakt som ikke er et tidsrom eller mangler tidssone, gir alltid datafeil. En vakt med `start >= slutt` gir datafeil bare når det lukkede tidsrommet overlapper det halvåpne vinduet (vedtak A5). Den gamle sjekken «slutter etter datagrensen» er erstattet av vindussjekken.
- **`kolliderende_vakt.py`**: `kollisjonsdatafeil` er fjernet. Valideringen er flyttet til den generelle vindussjekken, og regelen har fått `vindu = [start, slutt)`.
- **Adapter og API**: `Kandidatgrunnlag.historikkstart = turnus.periode_start − 672 t`, regnet i UTC (24.08.2026 kl. 00:00 i seeden, beslutning 2A). Ruten sender den videre. Svarformen og skjemaet er uendret.
- **Frontend og README**: merknaden er «Filtrert på kompetanse, kolliderende vakt og 11-timersregelen. Flere regler kommer.», og README sier at #4127 gir 5 og #4189 1 gyldig.
- **Tester**: ny `tester/regelmotor/test_11_timersregelen.py` (48), tilpasset `test_kompetanse.py` (56), `test_kolliderende_vakt.py` (44) og `tester/api/test_kandidater.py` (37).

## Korrigering og kvalitetssikring

Rettet underveis:

1. Tre tester fra 2.2 i `test_kolliderende_vakt.py` antok at en egen vakt som berører Vakten, gir en gyldig Kandidat. Med 11-timersregelen er det nå brudd. Første retting svekket hjelperen `utelukket` til «årsaken er blant årsakene», og gjennomgangen påpekte at kollisjonstestene da ikke fanger en uventet ekstra årsak. Rettet: hjelperne `vurder` og `utelukket` vurderer nå med `regler=REGLER[:2]` (kompetanse og kolliderende vakt), og den eksakte sjekken `årsaker == (ÅRSAK,)` er tilbake. Det gjelder alle testene som bruker hjelperne, blant dem `test_egen_vakt_som_slutter_nøyaktig_ved_vaktens_start_kolliderer_ikke`, `test_egen_vakt_som_starter_nøyaktig_ved_vaktens_slutt_kolliderer_ikke`, `test_ett_minutt_fra_hver_side_kolliderer_ikke`, `test_samme_kalenderdato_uten_overlapp_kolliderer_ikke`, `test_vakt_som_starter_ved_sommertidsnattens_slutt_kolliderer_ikke`, `test_egen_vakt_før_timen_som_går_to_ganger_regnes_på_faktisk_tid`, `test_tider_i_ulike_tidssoner_sammenlignes_som_samme_tidspunkt` og `test_natt_over_midnatt_og_vakt_som_starter_ved_slutten_kolliderer_ikke`. Samspillet med 11-timersregelen testes i `test_11_timersregelen.py`. Determinismetesten (full `REGLER`) fikk vakter med større avstand, så den fortsatt har både gyldige og utelukkede.
4. API-testen for historikkstarten sammenlignet med `PERIODE_START - timedelta(days=28)`, som selv er veggklokkearitmetikk, og seedens 21.09→24.08 krysser ikke noe sommertidsskifte. Rettet til `PERIODE_START.astimezone(UTC) - timedelta(hours=672)`, og ny test med periodestart 13.04 som krysser vårskiftet.
2. API-testen `test_alfabetisk_med_kompetansenivå_for_vakttypen` sjekket at første navn er «Anders Strand» for begge vaktene. For #4189 er det nå bare Line Moe igjen. Forventningen er kontrollert mot `FASIT` (begge bryter bare 35-timersregelen) og ikke tilpasset koden.
3. Datagrensetestene fra 2.1 (kveld 04.10 16:00 og 16:01) er regnet om etter vinduet: siste gyldige Vakt slutter 04.10 kl. 13:00.

Kontroller:

- **Fasiten (AV-07):** API-testene leser `testdata.FASIT`. De gyldige er alle uten `kompetanse`, `kolliderende` eller `elleve-timer`: #4127 gir 5 (9 fra 2.2 minus 4) og #4189 1 (19 minus 18). Utelukkede er 19 og 23. Regelmotoren importerer ikke fasithjelperen `bryter_elleve_timer` i `tester/lagring/test_testdata.py`.
- **Mutasjon `<` til `<=` (akseptansekrav 2), gjort én gang 2026-11-11:** begge sammenligningene mot `MINSTE_HVILE` i `bryter_elleve_timer` ble endret til `<=`. `pytest tester/regelmotor` ga **5 røde av 148** (nøyaktig 11 t før og etter, grensen 660 minutter, natt etter dag med nøyaktig 11 t, og determinismetesten). Reversert, 148 grønne.
- **Mutasjon som fjerner UTC-omregningen (akseptansekrav 3), gjort én gang 2026-11-11:** `.astimezone(UTC)` ble fjernet fra både Vaktens og den egne vaktens tider i `bryter_elleve_timer`. **4 røde av 148**, nøyaktig de fire sommertidstestene (vårskiftet før og etter, høstskiftet før og etter). Alle tider i testene bruker samme `ZoneInfo`-objekt, så Python regner på veggklokka når omregningen mangler. Reversert, 148 grønne.
- **Mutasjon av historikkstarten i adapteren, gjort én gang 2026-11-11:** `.astimezone(UTC)` ble fjernet i `kandidatgrunnlag.py`. `test_historikkstart_regnes_i_faktisk_tid_over_vårskiftet` ble rød (forventet 15.03 kl. 23:00, fikk 16.03 kl. 00:00), og den andre historikkstarttesten var grønn. Reversert, begge grønne.
- **Vinduet i UTC:** `test_vinduet_regnes_i_utc_over_vårskiftet` viser at vinduet for en Vakt 29.03 kl. 07:00 starter 28.03 kl. 19:00 CET (11 faktiske timer før), ikke 20:00 som veggklokka ville gitt.
- **Grensene for vinduet:** vindu nøyaktig ved datagrensen og historikkstarten er gyldig, ett minutt over er datafeil. Et punkt i vinduets start er innenfor, et punkt i vinduets slutt er utenfor, og omvendte vakter som når inn i vinduet, gir datafeil. En ugyldig vakt i uke 35 gir ikke datafeil for Vakten 27.09, verken i domenet eller gjennom API-et.
- **Resultater:** full `pytest` i `backend/` ga **336 bestått** før rettingene etter gjennomgangen, inkludert import-linter-kontrakten. Etter rettingene ga `pytest tester/regelmotor tester/api/test_kandidater.py` 186 bestått (én ny API-test). `npm.cmd run build` bestod, og `npm.cmd test` ga **26 bestått**.

## Gjenstår

- Uavhengig kodegjennomgang (underagenter i `bmad-build`) og menneskelig PR-gjennomgang av et gruppemedlem.
- Nettleserkontroll: ikke utført av implementeringsagenten. Mithad gjorde nettleserkontrollen 2026-11-11 mot en midlertidig testdatabase og godkjente den. #4127 viste 5 kandidater (Anders Strand, Ingrid Dahl, Jonas Bakke, Mette Solberg og Thomas Nygård), #4189 viste Line Moe, og merknaden var ny. API-svaret ga de samme navnene.
