---
title: 'Avgrenset norsk modelltest av Haiku 5.5 via OpenRouter'
type: chore
created: '2026-10-15'
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

Teste at `anthropic/claude-haiku-5.5` kan nås med den lokale OpenRouter-nøkkelen,
tolke norske ansattpreferanser til strukturert JSON og forklare ferdig beregnede,
fiktive kandidatdata. Brukeren har autorisert testkall med kreditt i eksisterende
branch `ki-leverandor-openrouter-haiku`. Selve appintegrasjonen venter.

Testen skal ha fasit bestemt før kjøring, gjentakelser, lagrede forespørsler/svar,
modellnavn, tidsbruk, API-rapportert forbruk og en ærlig vurdering av begrensningene.
Nøkkelen leses fra lokal `.env` eller miljøet og skal aldri skrives i rapporter.
Oppdater AGENTS.md og vurderingsmatrisen med gjeldende teknologivalg og faktiske
testbevis. Ferdig når testene er gjennomført og resultatet dokumentert.

</frozen-after-approval>

## Implementation Notes

- Baseline: `2b06245041b499e84027bb9058267afdccec93cc`.
- Python 3.12.5 er installert. Bruk standardbiblioteket til en isolert testkommando;
  dette velger ikke klientbiblioteket for appen.
- PRD §4.4 gir preferansekategoriene flere/færre/fleksibel/ingen registrert.
  Uklar tekst håndteres konservativt i denne testen; dette er ingen endelig portkontrakt.
- To gjentakelser av 12 preferanser og fire forklaringer: maksimalt 32 modellkall,
  600 output-tokens per kall, ingen automatisk retry eller bytte av modell.
- Maskinkontroll av JSON/fasit suppleres med lesing av alle forklaringene. Denne
  testen erstatter ikke regelmotortester, lekkasje-invarianten eller apptesting.
- Fullført 2026-10-15: 32/32 gyldige API-/JSON-svar, 20/24 preferanser i samsvar
  med fasit, 8/8 faktatro forklaringer. To agenter har lest alle 32 svar, også
  preferansebegrunnelsene. Testen er ferdig; modellen er ikke ubetinget godkjent.
- Resultat og ordrette brukerprompts: `docs/ki-logg/2026-10-15-modelltest-haiku.md`.
  10/10 lokale verktøytester bestod. Ingen appstory er implementert.
- `temperature=0` ble fjernet før fullført kjøring fordi modellen ikke annonserer
  støtte. Første forsøk gav HTTP 404. Rårapporter, inkludert feilforsøk, er bevart.
- Brukerens presisering av dokumentasjonsoppgaven gjelder AGENTS.md og vurderingsmatrisen;
  ingen endring av `.agents/skills/` eller `.claude/skills/` var nødvendig.

## Review Triage Log

Gjennomgangsagenten fant fem reelle svakheter; alle er rettet og bekreftet ved ny
lesing. Dette er review av måleverktøyet, ikke menneskelig PR-godkjenning.

| Funn | Vurdering og bevis | Tiltak |
|---|---|---|
| Preferansebegrunnelser manglet manuell kontroll | Medium: riktig kategori skjuler oppdiktede fakta; to kjønnspåstander ble faktisk funnet | Alle 24 begrunnelser lest og vurdert i KI-loggen |
| Feilforsøk manglet scenario/runde/payload | Medium: sporbarhet gikk tapt når call_api feilet før append | Registrerer forsøket før sending; lokal feiltest bekrefter bevart forsøk |
| Uventet JSON-type kunne krasje og etterlate in-progress | Medium: message=null gir AttributeError i opprinnelig kode | Formvalidering og lokal test som bekrefter failed-status/exit 2 |
| Manglende usage kunne se ut som fullstendig måling | Medium: response.get tillot null uten merking | usage_complete-felt og dokumentert betydning; faktisk 32/32 komplette målinger |
| Nøkkelredigering og redirect manglet tester | Medium: sentral sikkerhetsegenskap uten kontroll | Tester med oppdiktede nøkler, HTTP-feil og redirect; 10/10 tester består |
