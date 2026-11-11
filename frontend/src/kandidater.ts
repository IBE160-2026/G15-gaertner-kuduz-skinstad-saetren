// Tilstanden til kandidatlisten (story 2.1), skilt ut fra komponenten så den kan
// testes med `node --test`. Laster, feil og datafeil er ulike tilstander med
// ulik tekst (P-08). Et forsinket svar for en tidligere vakt eller sesjon
// meldes aldri (P-09).

import { ApiFeil, gjeldendeSesjonsgenerasjon, hentKandidater, type Kandidat, type Kandidatsvar } from "./api";
import { INGEN_KONTAKT, RESERVETEKST, feiltekst } from "./tekster";

export type Kandidattilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "feil"; tekst: string }
  | { type: "datafeil"; datagrense: string }
  | { type: "klar"; kandidater: Kandidat[] };

export function tilstandFraSvar(svar: Kandidatsvar): Kandidattilstand {
  if (svar.status === "ok") return { type: "klar", kandidater: svar.kandidater };
  if (svar.status === "datafeil") return { type: "datafeil", datagrense: svar.datagrense };
  // En status frontend ikke kjenner, vises som feil, aldri som en tom liste.
  return { type: "feil", tekst: RESERVETEKST };
}

/** 401 håndteres av sesjonsvarselet i App, så listen viser ingenting da. */
export function tilstandFraFeil(feil: unknown): Kandidattilstand {
  if (feil instanceof ApiFeil && feil.status === 401) return { type: "avvist" };
  return { type: "feil", tekst: feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT };
}

/**
 * Henter kandidatene for vakten og melder tilstanden, først «laster».
 * Returnerer en avbryter for opprydding i `useEffect`. Etter avbrytingen, eller
 * når sesjonen er byttet, meldes ikke svaret.
 */
export function lastKandidater(
  vaktnummer: number,
  meld: (tilstand: Kandidattilstand) => void,
  hent: (vaktnummer: number) => Promise<Kandidatsvar> = hentKandidater,
): () => void {
  let aktiv = true;
  const generasjon = gjeldendeSesjonsgenerasjon();
  const gjeldende = () => aktiv && generasjon === gjeldendeSesjonsgenerasjon();
  meld({ type: "laster" });
  hent(vaktnummer).then(
    (svar) => { if (gjeldende()) meld(tilstandFraSvar(svar)); },
    (feil: unknown) => { if (gjeldende()) meld(tilstandFraFeil(feil)); },
  );
  return () => { aktiv = false; };
}
