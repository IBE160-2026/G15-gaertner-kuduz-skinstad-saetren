# Samordning av PRD med gruppevedtak 2026-11-07

Grunnlag: `docs/beslutninger/avklaringspunkter.md`, AV-04/05/06, K-02/03/04 og OP-03. Avgrenset til oppfølging av de 12 tidligere PRD-funnene; ingen nye produktvalg er foreslått eller vedtatt her.

| Grunnlag | Innarbeiding i PRD | Avgrensning |
| --- | --- | --- |
| AV-04, vedtatt | FR-4: minst 11 timers hvile før og etter aktuell vakt. FR-5: minst 35 timers sammenhengende fri innenfor hver berørte kalenderuke. Beskriv dette som avgrenset prototypetolkning og oppgi behov for relevante nabovakter og komplette berørte uker, også utenfor visningsperioden. | Ingen påstand om full juridisk lovkontroll. Vedtaket erstatter åpen/midlertidig status for selve modellvalget, men dokumenterer ikke implementasjon eller test. |
| AV-05, vedtatt | §4.4/FR-9: min–maks for kostnad og timebelastning, med 50 faktorpoeng til alle når alle har identisk faktorverdi. Ved reelt lik totalscore sorteres etter stigende ansatt-ID. Én gyldig kandidat omfattes også av «alle er like». | Særregelen gjelder ikke ulempescore, som allerede har fast skala. AV-05 endrer ikke vektene 40/20/15/25. |
| K-03, vedtatt | §4.4/FR-9: faktorpoeng og totalscore beregnes og sorteres uavrundet; visning med én desimal. Lik visningsscore utløser ikke ID-sortering hvis uavrundede verdier er forskjellige. | Eksakt håndtering midt mellom to tideler er ikke avtalt. Ikke innfør egen avrundingsalgoritme eller anvend vedtaket som nytt krav om pengeavrunding. |
| AV-06, vedtatt | Kandidatgrunnlaget utelater den opprinnelig oppsatte ansatte. Øvrige antas tilgjengelige med mindre vakter eller harde regler utelukker dem. FR-10: registrerte preferanser gjelder hele demonstrasjonsperioden. | Ingen separat fraværsmodell eller daterte preferanser i v1. Antatt tilgjengelighet er ikke bekreftet faktisk tilgjengelighet. |

Fortsatt åpne saker må fremgå uten at forslag gis vedtaksstatus:

- K-02: eksakt grense for høy timebelastning er åpen. 32,4 timer er en anbefaling; generell avrunding i K-03 avgjør ikke grensen.
- OP-03: feil i preferansetolkning skal være avklart før story 5.1/5.2 er `done`; ingen bestemt fallback, feilmerking eller poengverdi er vedtatt.
- K-04: samordning av KI-/rangeringskontrakten er åpen. Punktet vedtar ingen konkret valideringsalgoritme eller ny kontrakt.
- De leste vedtakene avklarer ikke hvilken kostnadsverdi FR-7/FR-9 skal bruke eller fordeling av kostnadstimer ved ukeskifte. FR-8s eksisterende startuke er heller ikke i seg selv et vedtak om kostnadsberegningen.

Kontrollresultat: Fire opprinnelige beslutningstemaer (like faktorverdier, poenglikhet, hvilemodell og opprinnelig ansatt) kan innarbeides uten nye valg. Eksisterende godkjenningskrav må kontrolleres særskilt mot story 3.2/AD-5 før de løftes inn i FR-12. Ingen PRD- eller memlogendring er utført av denne kontrollen.
