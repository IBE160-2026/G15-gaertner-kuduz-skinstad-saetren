---
title: 'Story 5.2: Rangeringen bruker tolkede preferanser'
type: 'feature'
created: '2026-11-20'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 5.2 krever at Rangeringen faktisk bruker lagrede preferansetolkninger som vanlig input, er reproduserbar, og beregnes på nytt før bekreftelse etter en ny tolkning. `ranger()` gjør allerede alt dette (bygget i story 4.4, 4.5 og 5.1), men prosjektet mangler én dedikert test som beviser den konkrete akseptansekriteriescenarioen: to kandidater like på alle andre myke faktorer, der bare preferansen skiller dem, rangeres etter preferansen alene (epics.md, story 5.2, AC2). Uten den testen er ikke story 5.2 formelt verifisert, selv om koden allerede oppfyller kravet.

**Approach:** Legg til én isolasjonstest i `backend/tester/regelmotor/test_rangering.py`, etter samme mønster som den eksisterende ulempe-isolasjonstesten (`test_jonas_og_mette_skilles_med_nøyaktig_7_av_ulempen`): to syntetiske kandidater med identisk kostnadspoeng, timebelastningspoeng og ulempescore, men ulik tolket preferansekategori, der den med høyest preferansepoeng rangeres først. Dokumenter i spesifikasjonens Implementation Notes at de tre andre akseptansekriteriene (AC1: `ranger()` mottar `tolkede`/`feilede` som vanlig input; AC3: reproduserbarhet; AC4: ny tolkning krever rangering på nytt før bekreftelse) allerede er dekket av eksisterende, navngitte tester og kode fra story 4.4, 4.5 og 5.1, med konkrete filhenvisninger. Oppdater `sprint-status.yaml`, `docs/testing.md`, `docs/emne/vurderingsmatrise.md` og AGENTS.md til å reflektere at story 5.2 er ferdig.

</frozen-after-approval>

## Implementation Notes

2026-11-20: Undersøkte koden før jeg skrev noe. Alle fire akseptansekriteriene i story 5.2
(epics.md) er dekket:

- **AC1** (lagrede `TolketPreferanse`-verdier sendes inn i `domene/regelmotor` som vanlig
  input, og domenekjernen kaller aldri KI): allerede slik siden story 4.4/4.5.
  `adaptere/api/main.py` kaller `ranger(vurdering, grunnlag.vakt, grunnlag.tolkede,
  grunnlag.feilede)` i både `kandidater()`-ruten (linje 513) og
  `godkjenningsgrunnlag()`-ruten (linje 581). At `domene/regelmotor` og `domene/porter`
  aldri importerer noen `adaptere/*`-pakke, er håndhevet av import-linter-kontrakten,
  testet i `test_domenet_importerer_ikke_adaptere`
  (`backend/tester/test_arkitektur.py:15`).
- **AC2** (to kandidater like på alt annet, bare preferansen skiller dem, rangeres etter
  den): **ny isolasjonstest** lagt til,
  `test_preferanse_alene_avgjør_rangeringen_når_alt_annet_er_likt` i
  `backend/tester/regelmotor/test_rangering.py`, etter samme mønster som den eksisterende
  ulempe-isolasjonstesten (`test_jonas_og_mette_skilles_med_nøyaktig_7_av_ulempen`). Id-ene
  er valgt slik at stigende-id-tiebreaket (AV-05) alene ville gitt feil rekkefølge uten
  preferansevekten, så rekkefølgen alene beviser kravet, ikke bare totalscore-tallet. Vist å
  kunne feile: fjernet midlertidig `preferansevekt`-leddet i `totalscore()`, både
  totalscore- og rekkefølge-påstandene ga rødt, og koden ble tilbakestilt (`git diff`
  tomt etterpå).
- **AC3** (samme lagrede preferanser og input, kjørt flere ganger, gir samme rekkefølge):
  allerede dekket av `test_samme_input_i_ulik_rekkefølge_gir_samme_rangering`
  (`test_rangering.py:400`), som inkluderer en `tolkede`-mapping og kjører rangeringen 41
  ganger (ett utgangspunkt, så 20 stokkede rekkefølger og 20 reverserte av dem) med
  identisk resultat hver gang. Reproduserbarheten følger av at `ranger()` er en ren
  funksjon uten klokke, tilfeldighet eller database (AD-1): ingen kildekode i denne
  storien kan påvirke det.
- **AC4** (ny gyldig tolkning etter venting eller feil beregner rangeringen på nytt før
  bekreftelse; gammel tolkning av endret tekst brukes aldri): dekket fra flere kanter,
  bygget i story 4.5 og 5.1:
  - `test_ny_tolkning_etter_visning_gir_endret_grunnlag`
    (`backend/tester/api/test_preferansetolkning.py:182`) viser at en bakgrunnstolkning
    endrer grunnlagsmerket: det gamle merket gir 409 `endret_grunnlag`, det nye gir 200.
  - `test_lagret_tolkning_endrer_topprangert_uten_live_kall`
    (`backend/tester/api/test_godkjenningsgrunnlag.py:270`) viser at en direkte lagret
    tolkning (uten live KI-kall) endrer `plass`/`topprangert` neste gang grunnlaget hentes.
  - `"retry updates the whole ranking after interpretation"`
    (`frontend/tester/komponenter/kandidatflate.test.tsx:588`) viser at brukerflaten
    viser oppdatert rekkefølge og preferansepoeng etter et vellykket «Prøv igjen», uten
    at valg er mulig før det.
  - `"endret grunnlag oppdaterer avviksnotatet (ny topprangert) og krever nytt trykk
    (P-09)"` (`frontend/tester/komponenter/godkjenningsflate.test.tsx:134`) viser at en ny
    tolkning som lagres mens godkjenningsflaten er åpen, gir `endret_grunnlag` og krever
    ny bekreftelse.
  - At en gammel tolkning av endret tekst aldri brukes, er dekket fra begge sider:
    skrivesiden av `lagre_resultat` (`forventet`-tuppel, compare-and-swap) i
    `backend/adaptere/lagring/preferansetolkning.py`, testet av
    `test_endret_tekst_lagrer_ingenting`
    (`backend/tester/lagring/test_preferansetolkning.py:165`); lesesiden av
    teksthash-sjekken i `les_tolkning`, testet av
    `test_endret_tekst_etter_lagring_gir_venter` (samme fil, linje 172).

Ingen produksjonskode endret utover testfilen. Kjørt lokalt denne økten på
`story/5-2-rangeringen-bruker-tolkede-preferanser` (gren fra `main` ved `2302a8f`):
`pytest` 686 (inkludert den nye testen), frontendbygget, 52 modultester og 48
komponenttester (uendret — ingen frontendfil rørt i denne storyen).

## Review Triage Log

Blind-gjennomgang 2026-11-20 (Claude Opus 5.5, kontekstfri, 13 funn):

| Funn | Vurdering og tiltak |
|---|---|
| Rekkefølge-påstanden i den nye testen beviste ikke AC2 alene: id-ene stemte tilfeldigvis overens med stigende-id-tiebreaket (AV-05), så bare totalscore-påstanden ville felt ved fjernet preferansevekt | medium: bekreftet ved å bytte om id-ene og kjøre mutasjonen på nytt — nå feiler rekkefølge-påstanden også. Rettet. |
| Testen kalte `ranger(...)` to ganger med samme argumenter i stedet for å gjenbruke resultatet | low, enkel retting: fjernet den redundante kallingen. Rettet. |
| AC2 er bare testet mot en «nøytral» motpart, ikke mot ingen tekst, venter på tolkning eller kunne ikke tolkes (alle gir 50 poeng via en annen kodevei) | low: avvist. Likheten mellom disse fire veiene er allerede bevist av `test_alle_fire_tolkestatuser` (story 4.4); å utvide isolasjonstesten videre ville bare gjentatt det. |
| AC4s sitering manglet den faktiske backend-testen for `endret_grunnlag` (`test_ny_tolkning_etter_visning_gir_endret_grunnlag`) | medium: bekreftet, testen fantes men var ikke nevnt. Rettet med full filsti og linjenummer. |
| «Gammel tolkning av endret tekst brukes aldri» viste til feil/ufullstendig mekanisme og en tvetydig filsti (to filer heter `test_preferansetolkning.py`) | medium: bekreftet. Rettet med begge testene (skrive- og lesesiden) navngitt med fulle stier. |
| AC3s beskrivelse av testkjøringer var feil («21 ganger», reelt 41: ett utgangspunkt + 20 stokkede + 20 reverserte) | medium: bekreftet ved å lese løkken. Rettet tallet og lagt til hvorfor reproduserbarheten følger av koden (ren funksjon, AD-1). |
| AC1 hadde ingen testreferanse for at domenekjernen aldri kaller KI | medium: bekreftet manglende sitering. Rettet med `test_domenet_importerer_ikke_adaptere`. |
| Spesifikasjonens frosne Intent (oppdatere `docs/testing.md`, vurderingsmatrisen og AGENTS.md) var ikke levert ennå på gjennomgangstidspunktet | medium: reelt, men var allerede planlagt som siste steg. Fullført etter gjennomgangen. |
| Manglet KI-logg og sesjonslogg for den KI-genererte testen, slik AGENTS.md Policy krever | medium: reelt, var ikke gjort ennå. Fullført etter gjennomgangen (`docs/ki-logg/2026-11-20-rangering-tolkede-preferanser.md`). |
| Den regenererte `epic-5-context.md` påsto «5.2–5.9 står i backlog», som motsa `sprint-status.yaml` i samme diff | medium: bekreftet selvmotsigelse. Rettet: den spesifikke statuspåstanden er fjernet til fordel for en henvisning til `sprint-status.yaml`. |
| Den regenererte `epic-5-context.md` mistet flere konkrete, bindende detaljer fra forrige committede versjon (eierskapsregel, `GRUNNLAGSTABELLER`, eksakte statustekster, fire kildelinjetekster, `ki_kilde`-verdier, «ikke et krav»-presiseringer, ingen utropstegn, KI-logg-krav for 5.5–5.7, deler av avhengighetene) | high: bekreftet ved å sammenligne `git diff` mot forrige versjon linje for linje. Disse detaljene trengs av senere stories (5.3–5.9) som ennå ikke er bygget. Rettet: alt ført tilbake inn i den nye, omstrukturerte filen. |
| Nye påstander i `epic-5-context.md` («DemoKiAdapter bruker forhåndsgenererte tolkninger fra testdataene», «vanlig bruk gir ett KI-kall per vakt») var ikke sitert | false: begge sporet direkte til kilde — AD-6 i arkitekturdokumentet (linje 96) og epics.md story 5.3s akseptansekriterium (linje 1133). Compile-regelen krever omskriving, ikke sitering, så dette er riktig praksis, ikke hallusinasjon. |
| Testtallene i spesifikasjonen (686/52/48) hadde ingen commit-referanse å spore til | low: reelt poeng om sporbarhet. Rettet: lagt til branchens avgreningspunkt (`2302a8f`). |
