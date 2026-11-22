# Oppfølging av PR #37 (story 5.4)

Dato: 2026-11-22. Utført av Claude (Opus 5.5) i Claude Code etter Johannes W. Gärtners gjennomgang av [PR #37](https://github.com/IBE160-2026/G15-gaertner-kuduz-skinstad-saetren/pull/37). Endringene er gjort direkte på PR-branchen. [Opprinnelig KI-logg for 5.4](2026-11-21-reservetekst-ved-ki-feil.md)

## Oppgave og prompt

Johannes kjørte `bmad-review` på PR-en mot flettebasen `378d8aa`. Tre linser kjørte i hver sin underagent: adversarial, edge-case-hunter og verification-gap. Agenten vurderte de 27 funnene og anbefalte fem rettinger før merge. Johannes, ordrett:

> Gjør nødvendige utbedringer/tilpasninger til punkt 1-5

De fem punktene:

1. **Fletting med `main`.** PR-en hadde konflikt med `main` i `sprint-status.yaml` og `vurderingsmatrise.md`. Den nye `except OSError` i `_transport_med_frist` laget `Nettverksfeil(type(feil).__name__)`. Den gikk dermed forbi `nettverksårsak`, som `main` fikk i 769b3fb.
2. **Vurderingsmatrisen.** Den sa at «en rød test avdekket at et direkte transporttidsavbrudd hoppet over nye forsøk», som leses som en produksjonsfeil. Feilen gjaldt bare injiserte testtransporter. `urllib_transport` oversatte allerede slike feil.
3. **Forhåndsgenererte testdata.** «Forhåndsgenererte testdata bruker den samme faktakontrollen som live-svar» bygde på en testklasse som kaller `valider` direkte. Testen sier ingenting om en ekte forhåndsgenerert kilde.
4. **Grensen på 19 sifre.** Grensen i `_venting_429` var ikke testet. Med grensen satt til 399 bestod alle tester.
5. **`>` endret til `>=`.** Endringen ligger i den felles `_send` og endrer derfor også preferansetolkningen fra 5.1. Den er innenfor AV-19, men verken omtalt eller testet for `tolk`.

## Leveranse

- **Flettingen (`4701c4e`):** sprintstatus fikk nyeste `last_updated`. Vurderingsmatrisen fikk avsnittet for 5.3 fra `main`, deretter 5.4 fra branchen og 5.6 fra `main`. Koden flettet rent.
- **`openrouter.py`:**
  - Den nye `except OSError` lager nå `Nettverksfeil(nettverksårsak(feil))`.
  - Kommentaren sier at håndteringen gjelder injiserte transporter.
  - Kommentaren ved grensen på 19 sifre er presisert.
- **Nye tester:**
  - `test_direkte_sertifikatfeil_logger_årsaken_uten_feiltekst` (API, avveiningsruten): en `ssl.SSLCertVerificationError` kastes rett fra transporten. WARNING-linjen skal vise `SSLCertVerificationError/CERTIFICATE_VERIFY_FAILED`, og feilteksten «Bearer hemmelig» skal ikke komme med.
  - `test_429_med_uleselig_reset_venter_ett_vindu[20-sifre]` og `test_429_med_19_sifre_leses_og_går_over_budsjettet`: 20 sifre gir 60 s venting, mens 19 sifre leses og gir tidsbudsjett uten venting.
  - `test_tolk_venter_ikke_når_ventingen_slutter_ved_fristen[89, 90]`: ved reset 89 s fram venter tolkningen og prøver igjen. Ved 90 s gir den tidsbudsjett straks, uten å vente.
- **Dokumentasjon:**
  - Ordlyden i vurderingsmatrisen og i den opprinnelige KI-loggen er rettet.
  - Spesifikasjonens Implementation Notes er avgrenset, og Review Triage Log har fått fem nye rader.
  - `deferred-work.md` har et nytt punkt for 5.7: testen av begge kilder skal kjøres med den ekte `DemoKiAdapter` gjennom `lag_app`.

## Vurderinger og rettelser

- **Unntak i preferansetolkningen:** Tolkningsveien gjør fortsatt ikke en direkte `OSError` om til nettverksfeil. Det gjelder bare transporter som bryter `Transport`-kontrakten, og det er ikke en del av punkt 1–5.
- **Ingen try i ruten:** Avveiningsruten har fortsatt ingen `try` rundt `forklar`, så et uventet unntak gir HTTP 500. Frontend viser reserveteksten også da, og svakheten fantes allerede i 5.3.
- **Retting av generert kode:** Ingen generert kode måtte rettes etter første kjøring.

## Kvalitetssikring

- **KI-testene:** `pytest tester/ki tester/api/test_avveining.py` gav 131 bestått.
- **Mutasjonskontroll:** hver retting ble tilbakestilt, og testene ble røde. Koden ble satt tilbake etterpå.
  - `type(feil).__name__` i stedet for `nettverksårsak(feil)` gav 1 feil (den nye API-testen).
  - Grense 399 i stedet for 19 gav 1 feil (`[20-sifre]`).
  - `>` i stedet for `>=` gav 2 feil (den nye tolk-testen `[90]` og den eksisterende avveiningstesten `[90]`).
- **Hele backend etter flettingen:** 830 av 830 tester bestod på Windows, Python i `backend/.venv`, med import-linter-kontrakten.
- **Frontend:** verken PR-oppfølgingen eller `main` siden flettebasen endret frontend, og testene ble ikke kjørt på nytt. CI kjører dem ved push.
- **Nettverk:** alle testene bruker falsk transport og falsk klokke, uten nettverk eller nøkkel.
