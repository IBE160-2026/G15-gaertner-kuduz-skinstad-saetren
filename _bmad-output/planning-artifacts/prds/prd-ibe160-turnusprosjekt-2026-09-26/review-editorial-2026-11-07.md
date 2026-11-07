# Redaksjonell gjennomgang av vedtakssamordningen 2026-11-07

Dokumentet skal hjelpe prosjektgruppens fire utviklere med å implementere og teste samme avgrensede produkt. Strukturmodell: **Strategic/Context (Pyramid)**. Målgruppe: mennesker; eksisterende saklige bokmål, domenebegreper med stor forbokstav og FR-/vedtaksreferanser beholdes.

Omfang: bare de endrede avsnittene i PRD og deres umiddelbare sammenheng. Struktur ble vurdert først; prosa deretter. Ordmetrikk med `backend/.venv/Scripts/python.exe -B .agents/skills/bmad-review/scripts/word_metrics.py …/prd.md`: totalt **5 816 ord**, §4.2 **152**, §4.4 **344**, FR-9 **158**, FR-12 **167** og §8 **645**. Tallene gjelder arbeidstreet ved gjennomgangen; ingen generell omstrukturering er foreslått.

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | §4.2/FR-4/FR-5: kandidatgrunnlag og prototypemodell før testbare konsekvenser | **PRESERVE** den valgte plasseringen og skillet mellom modellbeskrivelse og grensetester. | Vedtakene kommer før detaljene som bygger på dem. Gjentakelsen i akseptkrav har verdi som testgrunnlag. Ordvirkning 0. |
| structure | §4.4 og FR-9: likeverdissærregel, avrunding og tilhørende testbare konsekvenser | **PRESERVE** forklaring før FR-9 og konkrete konsekvenser i FR-9. | Hovedregelen kan leses samlet; testkonsekvensene gjør særtilfellene etterprøvbare. Ordvirkning 0. |
| structure | §8: åpne saker etterfulgt av «Samordnet med vedtak og eksisterende krav» | **PRESERVE** skillet mellom åpne produktvalg og gjennomført dokumentoppdatering. | Åpne spørsmål lukkes ikke bare fordi de er registrert. Oppdateringen påstår heller ikke implementasjon. Ordvirkning 0. |
| prose | FR-9: «Like kostnader gir alle 50 kostnadspoeng, og lik Timebelastning gir alle 50 timebelastningspoeng, også ved én Gyldig kandidat.» | «Når alle Gyldige kandidater har samme kostnad, får alle 50 kostnadspoeng. Når alle har samme Timebelastning, får alle 50 timebelastningspoeng. Dette gjelder også ved én Gyldig kandidat.» | Avgrenser særregelen uttrykkelig til at alle kandidater har samme verdi. Den opprinnelige konsekvenssetningen kan isolert leses som at bare noen like kandidater får 50 poeng. Hovedavsnittet er allerede entydig. |

Struktur: tre bevaringsforslag, ingen flytting eller kutt; foreslått reduksjon **0 ord (0 %)**. Prosa: én avgrenset presisering. Ingen lengdegrense var angitt, og ingen forståelsesstøtte foreslås fjernet.

Vedtakskontroll: endringene gjengir AV-04/05/06 og K-03. Én gyldig kandidat er et spesialtilfelle av at samtlige er like, ikke en ny produktregel. FR-4/FR-5 bruker prosjektets prototypemodell og viderefører grensetilfeller fra de eksisterende stories. FR-12 viderefører story 3.2/AD-5. K-02, OP-03 og K-04 har fortsatt åpen status; ingen fallback, eksakt belastningsterskel, ny KI-kontrakt eller pengeavrundingsregel er innført. Kostnadsgrunnlag og kostnadsfordeling ved ukeskifte er fortsatt uttrykkelig åpne.

Ingen PRD-endring er utført av denne gjennomgangen. Forslaget må vurderes av hovedagenten før eventuell innarbeiding.
