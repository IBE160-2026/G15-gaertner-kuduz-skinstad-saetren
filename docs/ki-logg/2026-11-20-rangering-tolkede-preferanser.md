# KI-logg: Story 5.2 – rangeringen bruker tolkede preferanser

Dato: 2026-11-20. Utført av Claude (Sonnet 5) i `bmad-build`s oneshot-rute, direkte i
denne økten (ikke en separat implementeringsunderagent, siden endringen var liten og
uten intent-gap).

## Oppgave og prompt

Mithad Kuduz ba om story 5.2 (OP-18) etter at story 4.4, 4.5 og 5.1 var ferdige og
gruppen hadde godkjent branch + PR for endringen. Spesifikasjonens frosne Intent:
undersøke om Rangeringen faktisk bruker lagrede preferansetolkninger som vanlig input
(epics.md, story 5.2, AC1–AC4), og tette gapet med en test der det mangler.

## Leveranse

Undersøkelse før koding viste at AC1 (`ranger()` mottar `tolkede`/`feilede` fra
`adaptere/api`), AC3 (reproduserbarhet) og AC4 (ny tolkning krever rangering på nytt før
bekreftelse; gammel tolkning av endret tekst brukes aldri) allerede var oppfylt av kode
og tester fra story 4.4, 4.5 og 5.1. Bare AC2 (to kandidater like på kostnad,
timebelastning og ulempe, der bare preferansen skiller dem) manglet en dedikert test.
Lagt til: `test_preferanse_alene_avgjør_rangeringen_når_alt_annet_er_likt` i
`backend/tester/regelmotor/test_rangering.py`, etter samme mønster som den eksisterende
ulempe-isolasjonstesten fra story 4.4. Ingen produksjonskode endret.

## Rettelser

En uavhengig blind-gjennomgang (Claude Opus 5.5, per anbefalingen i
`docs/modellvalg-stories.md` for story 5.2) fant 13 funn. Disse ble rettet:

- Testens rekkefølge-påstand beviste ikke kravet alene: kandidat-ID-ene var valgt slik at
  stigende-ID-tiebreaket (AV-05) tilfeldigvis ga samme rekkefølge som preferansen, så en
  fjernet preferansevekt bare ville felt totalscore-påstanden, ikke rekkefølgen. ID-ene
  er byttet om, slik at tiebreaket alene ville gitt feil rekkefølge, og rekkefølgen
  beviser nå kravet selv om totalscore-påstanden fjernes.
- En redundant, duplisert kalling av `ranger()` i testen er fjernet til fordel for å
  gjenbruke resultatet som allerede var beregnet.
- Spesifikasjonens Implementation Notes siterte feil eller ufullstendige bevis for tre
  av akseptansekriteriene: AC4 manglet den faktiske backend-testen for `endret_grunnlag`
  (`test_ny_tolkning_etter_visning_gir_endret_grunnlag`) og navnga ikke de to konkrete
  testene for at en gammel tolkning av endret tekst aldri brukes; AC3s kjøretall var
  feil (41 kjøringer, ikke 21); AC1 hadde ingen testreferanse for at domenekjernen aldri
  kaller KI. Alle tre er rettet med fulle filstier og linjenumre.
- Den gjenbrukte `epic-5-context.md` (regenerert ved oppstart av denne storyen, fordi
  planleggingsdokumenter var endret siden forrige versjon) hadde mistet flere konkrete,
  bindende detaljer fra den forrige, committede versjonen: eierskapsregelen for
  `TolketPreferanse`, `GRUNNLAGSTABELLER`-kravet, de eksakte statustekstene, de fire
  kildelinjetekstene (UX-DR27), `ki_kilde`-verdiene, at KI ikke kan velge referanse selv,
  at «faktoren som bidrar mest» ikke er et krav, regelen om ingen utropstegn (UX-DR23),
  KI-logg-kravene for 5.5–5.7, og deler av avhengighetene mellom stories. Alt dette er
  ført tilbake inn i den nye, omstrukturerte filen. Den nye filen påsto også at story
  5.2–5.9 «står i backlog», noe som motsa `sprint-status.yaml` i samme diff — fjernet.
- Et funn om at `DemoKiAdapter` bruker forhåndsgenererte tolkninger «fra testdataene»,
  og at vanlig bruk gir «ett KI-kall per vakt», ble avvist: begge er sporet direkte til
  arkitekturdokumentet (AD-6) og epics.md (story 5.3s akseptansekriterium), ikke diktet
  opp — bare omskrevet til å beskrive formålet i stedet for å sitere kilden, slik
  kompileringsreglene krever.

Avvist uten retting: at AC2 burde testes mot flere statuser enn «nøytral» (venter på
tolkning, ingen registrert, kunne ikke tolkes) i tillegg til den som allerede er lagt
til. Alle disse gir 50 poeng gjennom en annen kodevei, og den likheten er allerede
dekket av `test_alle_fire_tolkestatuser` (story 4.4); å utvide isolasjonstesten videre
ville bare gjentatt det beviset.

## Kvalitetssikring

`pytest` 686 (inkludert den nye testen), kjørt lokalt på
`story/5-2-rangeringen-bruker-tolkede-preferanser` (gren fra `main` ved `2302a8f`).
Testen vist å kunne feile: `preferansevekt`-leddet i `totalscore()` ble midlertidig
fjernet, både totalscore- og rekkefølge-påstandene ga rødt, og koden ble tilbakestilt
(`git diff` tomt etterpå). Frontend er urørt i denne storyen (build, 52 modultester og
48 komponenttester, uendret fra forrige måling på `main`).
