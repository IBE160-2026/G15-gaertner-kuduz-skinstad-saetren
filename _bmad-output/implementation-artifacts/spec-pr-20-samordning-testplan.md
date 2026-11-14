---
title: 'Samordne PR #20 med AV-17 og presisere testdekning'
type: 'chore'
created: '2026-11-14'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** PR #20 har mergekonflikter mot `main`. Testplanen bruker 360 px som fast kontrollbredde etter at AV-17 flyttet mobil og nettbrett til v2, og dokumentasjonen beskriver de 12 komponenttestene som bredere dekning enn de gir. `AGENTS.md` peker P-13 til feil vedtak.

**Approach:** Ta inn gjeldende `origin/main`, bevar begge siders beslutninger og oppfølgingspunkter, samordne manuell sjekkliste med AV-17, beskriv faktisk komponenttestdekning og rett P-13-henvisningen. Verifiser dokumentkoblinger, merge-resultat og frontendens bygg og tester.

</frozen-after-approval>

## Implementation Notes

- Tok inn `origin/main` i PR-branchen. To tekstkonflikter ble løst: Johannes' `issues.md` beholder både OP-16-oppfølgingene og AV-17-punktene; beslutningsreferatet beholder både AV-17 og OP-16. Automatisk sammenslåtte planfiler ble beholdt.
- `docs/testing.md` bruker 1080, 960 og 680 px som representative bredder fra story 4.6, med 1600 px som bred kontroll. 360 px er ekstra regresjonskontroll, ikke et mobilkrav. Ingen vannrett siderulling og tabellrulling i egen beholder følger AV-14.
- `docs/testing.md`, `AGENTS.md`, `_bmad/custom/bmad-build.toml` og beslutningsreferatet presiserer at de 12 testene dekker navngitte flyter. Nye eller endrede flyter får test; udekkede flyter får målrettet manuell kontroll som åpent punkt. `AGENTS.md` viser P-13 til referatets §12.
- P-13-henvisningen er merket løst i `deferred-work.md` og i konfliktløste `issues.md`; forståelsestesten er fortsatt åpen.
- `npm.cmd ci` krevde `NODE_OPTIONS=--use-system-ca` på denne maskinen på grunn av registry-sertifikatet. Den låste installasjonen endret ikke `package-lock.json`. `npm.cmd run build` bestod på Node 24.19.0; `npm.cmd run test` gav 48 av 48 `node:test` og 12 av 12 Vitest. CI på PR-ens forrige commit var grønn på Node 22.12 og LTS; etter lokal samordning er CI ikke kjørt ennå.
- To uavhengige agenter gjennomgikk den sammenslåtte arbeidskopien. De bekreftet at de to konfliktfilene beholder begge siders innhold og fant foreldede formuleringer i OP-16, vurderingsmatrisen, P-13-statusen og den gamle spesifikasjonen. Disse er rettet eller presisert. Kim avklarte deretter at «før story 4.6» beholdes som planlagt arbeidsmål, ikke som eget fristvedtak; PRD, epics, sprintstatus og `deferred-work.md` er samordnet med dette.

## Review Triage Log

| Funn | Dom | Bevis og håndtering |
|---|---|---|
| B1/V1 | medium | Konfliktfilene hadde fortsatt uavklarte indeksstadier. Innholdet var løst; filene er lagt til i indeksen. |
| B2/V2 | medium | OP-16s opprinnelige tekst lovet bredere dekning enn de 12 testene gir og motsa presiseringen. Rettet i vedtaksreferatet. |
| B3 | low | P-13-raden og AV-16-avsnittet brukte framtidsform om mobilvalg som AV-17 allerede har avgjort. Oppdatert som status, med historisk ansvar bevart. |
| B4 | medium | Epics, PRD og sprintstatus anga frist før story 4.6 for P-13-testen; referatet gjør det ikke. Kim valgte å beholde tidspunktet som planlagt arbeidsmål uten eget gruppevedtak om frist. Filene og `deferred-work.md` er samordnet. |
| B5 | low | Eget `issues.md` ba fortsatt om mobilavklaring. Punktet sier nå at AV-17 er vedtatt og beholder forståelsestesten som åpen. |
| B6/V3 | low | Vurderingsmatrisen kalte 360 px fast testbredde. Endret til smale datamaskinvinduer etter AV-17. |
| B7/V5 | low | Den fullførte spesifikasjonens låste blokk hadde bred testpåstand og 360 px. En datert presisering er lagt i Implementation Notes uten å omskrive det historiske grunnlaget. |
| B8 | low | Den felles sjekklisten viste ikke story 4.6s særkrav om kandidatidentitet ved rulling og tilstand ved vindusendring. Lagt til henvisning til disse akseptkriteriene i `docs/testing.md`. |
| V4 | low | Johannes' `issues.md` knyttet fortsatt PR-godkjenningen til P-13-henvisningen. Punktene er skilt; henvisningen er merket løst. |
