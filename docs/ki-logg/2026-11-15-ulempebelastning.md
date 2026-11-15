# KI-logg: Story 4.7 – ulempebelastning

Dato: 2026-11-15. Arbeidet er utført med Codex og underagenter i
`bmad-build` på `story-4.7-ulempebelastning`. Grunnlaget er
[spesifikasjonen](../../_bmad-output/implementation-artifacts/spec-4-7-ulempebelastning-per-kandidat.md),
[beslutningsreferatet](../beslutninger/avklaringspunkter.md), PRD og story 4.7.

## Oppgave og instruksjon

Brukeren ba om å kontrollere KS-03 før implementasjon, beregne faktiske 672
timer med klipping og høyeste kategori uten avrunding, teste begge
sommertidsskiftene og kontrollere ny fasit uavhengig (KS-02/AV-12). Ingen KI
skal beregne belastningen. Arbeidet skulle skje på egen branch uten å overta
story 3.2 eller 4.1. Brukeren ba deretter om å fortsette med underagenter.

Sentralt utdrag av brukerens instruksjon: «Målevinduet er de 672 faktisk
forløpte timene før vaktstart, halvåpent; historiske vakter som krysser
grensen skal klippes. Hver arbeidstime telles én gang etter høyeste gjeldende
kategori. Behold poeng og score uavrundet i beregningen; avrund bare ved
visning.» Backendagenten fikk i tillegg uttrykkelig beskjed om overlapp,
begge sommertidsskifter og kontroll av AV-12 mot seeddata; frontendagenten
fikk beskjed om å følge UX-DR28 og teste den endrede kontrakten.

## Kontroll før kode

[KS-03](../beslutninger/ks-03-tidskategorier-2026-11-15.md) viser alle fire
vedtatte vakttyper og uavhengig regning for ukeskifter og sommertid: 20 poeng
vår og 26 høst. Ingen motstrid mellom kildene ble funnet. En separat
[KS-02/AV-12-regning](../beslutninger/ks-02-av-12-ulempeeksempel-2026-11-15.md)
viser 7 totalpoengs forskjell ved 40 mot 180 ulempepoeng, med ellers like
faktorer. Den godkjenner ikke ny fullstendig rangeringsfasit.

## Leveranse og rettelser

- Domenet klipper i UTC, slår sammen overlappende intervaller og deler tiden
  etter Oslo-kategorier. Score beregnes med parameterisert tak 300. Bare
  gyldige kandidater får beregning, og P-08 krever full datadekning.
- API-et formidler verdiene, og kandidatlisten viser poeng og fordeling med
  én desimal. Timekolonnen fra story 4.1 finnes ikke på denne branchen ennå.
- Den første genererte koden telte overlappende vakter dobbelt. Det ble
  oppdaget ved uavhengig kontroll og rettet med sammenslåing og test. Første
  frontendutkast brukte to desimaler; dette ble rettet til én etter K-03.
  Gjennomgangen fant også manglende eksplisitte tester for standardtak,
  like kandidater, grensekategorier og kun gyldige; disse ble lagt til.
  Tekst om målevindu og avrunding ble lagt til etter gjennomgangen.

## Kvalitetssikring og åpne punkter

Tre uavhengige gjennomgangslag ble kjørt; enkeltsvar og vurderinger står i
spesifikasjonens Review Triage Log. Domenetestene kontrollerer blant annet
minuttgrenser, overlapp, klipping, begge klokkeskifter, tak og determinisme.
API-testen sammenholder Jonas/Mette med 40/180-poengsfasiten og 7 poengs
forskjell. Frontendbygget og 49 Node-tester samt 15 komponenttester bestod.
Full backendtest etter rettingene ga 438 bestått, inkludert arkitekturkontrollen.

Nettleserkontroll er ikke gjennomført: ingen nettleser var tilgjengelig i
denne økten. Menneskelig gjennomgang, og plassering etter timekolonnen når
story 4.1 integreres, gjenstår. Det er ikke opprettet PR.
