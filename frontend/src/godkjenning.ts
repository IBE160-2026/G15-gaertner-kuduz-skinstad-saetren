// Tilstanden til godkjenningsflaten (story 3.1), skilt ut fra komponenten så den
// kan testes med `node --test`. Samme mønster som kandidater.ts: laster, ikke
// funnet, feil og datafeil er ulike tilstander med ulik tekst (P-08), og et
// forsinket svar for en tidligere URL eller sesjon meldes aldri (P-09).

import {
  ApiFeil, gjeldendeSesjonsgenerasjon, hentGodkjenningsgrunnlag,
  type Godkjenningssvar, type Kandidat, type Vaktdetaljer,
} from "./api";
import { INGEN_KONTAKT, RESERVETEKST, feiltekst } from "./tekster";

export type Godkjenningstilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "ikke_funnet" }
  | { type: "feil"; tekst: string }
  | { type: "datafeil"; datagrense: string }
  | { type: "klar"; vakt: Vaktdetaljer; kandidat: Kandidat };

export function tilstandFraSvar(svar: Godkjenningssvar): Godkjenningstilstand {
  if (svar.status === "ok") return { type: "klar", vakt: svar.vakt, kandidat: svar.kandidat };
  if (svar.status === "datafeil") return { type: "datafeil", datagrense: svar.datagrense };
  // En status frontend ikke kjenner, vises som feil, aldri som et bekreftelsesbilde.
  return { type: "feil", tekst: RESERVETEKST };
}

/**
 * 401 håndteres av sesjonsvarselet i App, så flaten viser ingenting da. 404 dekker
 * utelukket og ukjent Ansatt og en vakt som ikke lenger mangler bemanning, uten å
 * skille dem (beslutning 3A).
 */
export function tilstandFraFeil(feil: unknown): Godkjenningstilstand {
  if (feil instanceof ApiFeil && feil.status === 401) return { type: "avvist" };
  if (feil instanceof ApiFeil && feil.status === 404) return { type: "ikke_funnet" };
  return { type: "feil", tekst: feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT };
}

/**
 * Henter vakten og kandidaten og melder tilstanden, først «laster». Returnerer
 * en avbryter for opprydding i `useEffect`. Etter avbrytingen, eller når sesjonen
 * er byttet, meldes ikke svaret.
 */
export function lastGodkjenning(
  vaktnummer: number,
  ansattId: number,
  meld: (tilstand: Godkjenningstilstand) => void,
  hent: (vaktnummer: number, ansattId: number) => Promise<Godkjenningssvar> = hentGodkjenningsgrunnlag,
): () => void {
  let aktiv = true;
  const generasjon = gjeldendeSesjonsgenerasjon();
  const gjeldende = () => aktiv && generasjon === gjeldendeSesjonsgenerasjon();
  meld({ type: "laster" });
  hent(vaktnummer, ansattId).then(
    (svar) => { if (gjeldende()) meld(tilstandFraSvar(svar)); },
    (feil: unknown) => { if (gjeldende()) meld(tilstandFraFeil(feil)); },
  );
  return () => { aktiv = false; };
}
