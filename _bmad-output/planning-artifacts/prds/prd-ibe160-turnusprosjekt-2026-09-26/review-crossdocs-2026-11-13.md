# Uavhengig samordningskontroll: brief, PRD, UX og arkitektur

**Dato:** 2026-11-13

**Omfang:** `product-brief.md`, gjeldende `prd.md`, UX-dokumentene `DESIGN.md` og `EXPERIENCE.md`, `ARCHITECTURE-SPINE.md`; epics og beslutningsreferatet som støttekilder. Dette er dokumentkontroll, ikke kontroll av implementasjon eller tester.

## Dom

Hovedlinjene er samordnet: deterministisk filtrering og rangering, KI bare til preferansetolkning og forklaring, menneskelig godkjenning, én gyldig kandidat uten referansesammenligning, reservetekst ved KI-feil, P-12B utenfor v1 og 480 minutter som overstyrbar standardøkt. SM-3, SM-4 og SM-C2 har samme innhold i PRD, beslutningsreferat og sentrale UX-/arkitekturtekster. Mobil/nettbrett og sensors nøkkel har eier og frist, men selve valgene er åpne. Tre formuleringer bør rettes før dokumentene brukes som implementasjonsgrunnlag.

## Funn

| ID / alvorlighet | Kilder | Konsekvens og anbefalt retting |
|---|---|---|
| S1 – Middels: mulig forhåndsvedtak om preferansetolkningens forsøk | PRD §4.5 FR-10, linje 298, og §8, linje 463, sier at antall forsøk og tidsbudsjett avklares før story 5.1. Arkitektur AD-7, linje 102, sier generelt at adapteren venter **2, 4 og 8 sekunder** ved 5xx/nettverksfeil, før teksten avgrenser bare 90-sekundersbudsjettet og sluttstatusen til Avveining. Epic story 5.1, linje 957, setter samme åpne beslutningsfrist som PRD. | Slik AD-7 er skrevet, kan utvikleren lese tre ventetrinn som allerede vedtatt også for preferansetolkning. Presiser at 2/4/8-planen gjelder live Avveining, og at preferansetolkningens ventetrinn/antall, tidsbudsjett, startpunkt og sluttstatus fastsettes samlet før story 5.1. Behold felles begrenser og 429-venting for begge funksjoner. Ikke lån Avveiningens 90 sekunder eller `avveining_feilet` til preferansetolkning uten nytt vedtak. |
| S2 – Lav: UX merker fastsatt innloggingsfeil som antakelse | PRD FR-13, linje 388, krever samme melding for feil brukernavn/passord: «Feil brukernavn eller passord.» Arkitektur AD-3, linje 73, har fast sesjonsløsning. UX `EXPERIENCE.md` State Patterns, linje 76, sier `[ASSUMPTION] Ingen kilde viser denne tilstanden` og `må bekreftes før implementasjon`. | Fjern antakelsesmerket og påstanden om manglende kilde. Bruk PRD-ordlyden med punktum, og beskriv inline-plassering som et UX-valg hvis den fortsatt er ønsket. Kontosperring er fortsatt ikke spesifisert, men skal ikke holde det vedtatte feilsvaret åpent. |
| S3 – Middels: reservetekst kan få misvisende KI-kildelinje | PRD SM-4, linje 444, og FR-11, linje 342–344, krever tydelig merket Reservetekst når forklaring feiler eller forkastes. UX `EXPERIENCE.md` linje 62 sier at **hvert** panel har kildelinje, men tilbyr bare «KI-generert · modellnavn», «Forhåndsgenerert KI-forklaring» eller maltekst; linje 83 omtaler Reservetekst uten egen kildelinje. Arkitektur AD-4, linje 79, skiller `avveining_feilet`, mens AD-6, linje 96, gir `ki_kilde` for en Avveining. | Et panel med forkastet live-svar må ikke merkes «KI-generert» som om det viste en godkjent KI-forklaring. Beskriv særskilt kildelinje/status ved Reservetekst, for eksempel «Reservetekst · KI-forklaring utilgjengelig», og la UI bruke `avveining_feilet` fremfor `ki_kilde` for denne tilstanden. Oppdater eventuelt story 5.4s akseptkriterier samtidig. Eksakt norsk brukertekst kan fastsettes i story 5.4, men skillet må være bindende. |

## Kontroll per tema

| Tema | Resultat |
|---|---|
| SM-3 og kandidatvisning | PRD linje 443, UX `EXPERIENCE.md` linje 61 og epic story 4.4 krever inntil fem gyldige og antall utelukkede når kandidatberegningen er ferdig, uten ekstra handling. Tomtilstand og Datafeil er separate. Ingen motstrid funnet. |
| SM-4 og én kandidat | PRD FR-11 linje 344–345 og SM-4 linje 444, UX `EXPERIENCE.md` linje 62, `DESIGN.md` linje 215 og epic story 5.3 linje 1030–1038 krever relevant faktakontrollert myk faktor og ingen referanse ved én gyldig kandidat. Fire beregnede verdier vises også ved Reservetekst. Briefen omtaler generelt avveininger «mellom» kandidater (`product-brief.md` linje 53), men er et overordnet konsept; det er ingen eksplisitt én-kandidatbegrensning der. |
| SM-C2 og feiltid | PRD linje 453, AD-7 linje 102, beslutningsreferat AV-15 linje 756 og epic story 5.4 linje 1072–1075 plasserer faktakontroll før live-visning og 90 sekunder fra første live-kall for Avveining. Demo gjør ingen live-kall. 429-venting må avsluttes innen samme frist for Avveining; dette er tydelig i epic story 5.4 og bør leses inn i AD-7. S1 gjelder den separate tolkeflyten. |
| FR-10 og preferansestatus | Brief linje 133, PRD FR-10 linje 296–298, AD-1 linje 48 og epic story 5.1 linje 976–983 skiller manglende tekst, nøytral tolkning, venting og feil; midlertidig 50 poeng gir ikke oppdiktet nøytral kategori. Teknisk feilbudsjett er korrekt åpent før story 5.1, med forbehold S1. |
| FR-13 | PRD linje 384–391 og AD-3 linje 69–73 samsvarer om innlogging, 480 minutter som standard og overstyring med `TURNUSHJELPEREN_JWT_MINUTTER`. UX håndterer utløpt sesjon, men S2 gjelder feil innlogging. |
| P-12B og omfang | Brief linje 152, PRD linje 371/436 og AD-5/Deferred linje 158/205 sier at vist forklaring ikke lagres historisk ved godkjenning; senere lagring krever eget vedtak/story. Ingen v1-scopeglidning funnet. |
| Mobil/nettbrett og sensornøkkel | PRD §8 linje 461–462 og AV-16 linje 759–762 har «Hele gruppa» som eier. Mobilvalg skjer etter fungerende kandidatvisning og før story 4.6 er ferdig; sensornøkkel/kreditt/betaling før innlevering. UX og arkitektur beskriver mobilmønstre som forslag, ikke vedtak. Epicens sensoroppsett er fremtidige akseptkriterier, ikke bevis for at nøkkelvalget er tatt. |

**Prioritet:** Rett S1 og S3 før KI-stories implementeres. S2 kan rettes som en ren tekstsamordning nå. Dokumentvedtakene gir ennå ikke implementasjons- eller testbevis.
