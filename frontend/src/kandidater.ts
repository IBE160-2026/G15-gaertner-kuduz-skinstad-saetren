// Tilstanden til kandidatlisten (story 2.1), skilt ut fra komponenten så den kan
// testes med `node --test`. Laster, feil og datafeil er ulike tilstander med
// ulik tekst (P-08). Et forsinket svar for en tidligere vakt eller sesjon
// meldes aldri (P-09).

import {
  ApiFeil,
  gjeldendeSesjonsgenerasjon,
  hentKandidater,
  type EkskludertKandidat,
  type Kandidat,
  type Kandidatsvar,
  type UtelukkelsesOppsummering,
} from "./api";
import { INGEN_KONTAKT, RESERVETEKST, TEKSTER, feiltekst } from "./tekster";

export type Kandidattilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "feil"; tekst: string }
  | { type: "datafeil"; datagrense: string }
  | { type: "klar"; kandidater: Kandidat[]; utelukkelser: UtelukkelsesOppsummering };

export function tilstandFraSvar(svar: Kandidatsvar): Kandidattilstand {
  if (svar.status === "ok") return { type: "klar", kandidater: svar.kandidater, utelukkelser: svar.utelukkelser };
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
 * Ekskludert-boksens hovedlinje (story 2.5, UX-DR15): «N utelukket av harde
 * regler · N under kompetanse-minstekrav · …». En regel med 0 utelukkede tas
 * ikke med. Rekkefølgen følger `oppsummering.per_regel` (regelmotorens `REGLER`).
 * Ren funksjon, skilt ut fra komponenten så den kan testes med de ekte fasittallene.
 */
export function ekskludertBoksTekst(oppsummering: UtelukkelsesOppsummering): string {
  const ek = TEKSTER.ekskludertBoks;
  const deler = [
    ek.totaltUtelukket(oppsummering.totalt),
    ...oppsummering.per_regel
      .filter((regel) => regel.antall > 0)
      .map((regel) => {
        const mal = ek.årsaksmaler[regel.årsak];
        // Ukjent årsak (regelmotoren har fått en regel uten tekstmal): vis tallet
        // og regelmotorens egen årsakstekst i stedet for å kaste.
        return mal ? mal(regel.antall) : `${regel.antall} ${regel.årsak}`;
      }),
  ];
  return deler.join(" · ");
}

/**
 * Én rad i Ekskludert-boksens full liste: «Navn — årsak» eller «Navn — årsak,
 * årsak» ved flere årsaker (Design Notes-eksempelet «Kari Nordmann —
 * kolliderende vakt, 35-timersregelen»). Ren funksjon, skilt ut så raden kan
 * testes uten å rendre komponenten.
 */
export function ekskludertRadTekst(kandidat: EkskludertKandidat): string {
  return `${kandidat.navn} — ${kandidat.årsaker.join(", ")}`;
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
