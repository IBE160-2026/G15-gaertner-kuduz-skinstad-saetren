# P-08: fem faktiske periodekantvakter

## Oppgave og prompt

Kim ba 22.11.2026: «Undersøk eksisterende tester før du supplerer dem. Kontroller at ny vurdering og godkjenning av #4261–#4265 stopper ved mangelfullt datagrunnlag. Bevar #4127/#4189-fasiten og KS-04-avgrensningen.» Arbeidet inngår i oppfølgingen av åpne punkter, gjennom `bmad-build` [BD].

## Leveranse og fremgangsmåte

Codex/GPT-6 undersøkte eksisterende tester og brukte en egen kontekstagent. Testene for 04.10 flyttet #4127, mens #4261/#4265 bare ble prøvd som allerede bemannede vakter. Tillegget i [godkjenningsgrunnlagstestene](../../backend/tester/api/test_godkjenningsgrunnlag.py) gjør de faktiske fem vaktene ubemannede i hver sin isolerte testdatabase. Tidene beholdes, og opprinnelig ansatt bevares som `satt_opp_ansatt_id`.

Det nye beviset dekker gjentatt GET av kandidatlisten, GET av godkjenningsgrunnlag og POST for Jonas og Mette. Alle svar er nøyaktig `datafeil` / `mangler_turnusgrunnlag` med datagrense `2026-10-05T00:00:00+02:00`; ingen rangering eller kandidat følger svaret. Alle tabeller er uendret etter kallene, også godkjenningstabellen. Produksjonskode og seeddata er uendret.

## Hva som ble rettet og hvorfor

Den første genererte testen brukte bare et syntaktisk gyldig, uriktig grunnlagsmerke og stolte på seedvaktenes tidspunkter. En blind gjennomgang foreslo å styrke dette: testen prøver nå også et korrekt merke for gjeldende database og låser de avtalte datoene, vakttypene og tidene eksplisitt. Dette gjør beviset mindre følsomt for senere seedendringer og dokumenterer at datafeil stopper selv når merket stemmer.

En ny uavhengig gjennomgang fant ingen ytterligere feil og kjørte de fem tilfellene med bestått resultat. [Spesifikasjon og triage](../../_bmad-output/implementation-artifacts/spec-p-08-fem-periodekantvakter.md).

## Kvalitetssikring

- 219 backendtester bestod etter rettingen (51,44 s): kandidat- og godkjennings-API, seeddata/KS-04, rangering/KS-02, KI-faktakontroll og avveinings-API.
- 54 komponenttester i Vaktvalg, kandidatflate, godkjenningsflate og avveining bestod i én kjøring (9,71 s). Ingen frontendkode er endret.
- Automatiske KI-tester bruker falsk transport. Ingen betalte kall eller ekte API-nøkler.
- Ekte backend i separat SQLite-database viser datafeil for #4261 med riktig datagrense; [nettleserbevis](../testing/2026-11-22/kontroll.md).

Kontrollen utvider ikke KS-04-godkjenningen utover #4127/#4189. Den gjør ingen påstand om full juridisk etterlevelse eller datadekning for hele demoperioden.
