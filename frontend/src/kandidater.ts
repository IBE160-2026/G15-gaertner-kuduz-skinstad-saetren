// Tilstanden til kandidatlisten (story 2.1), skilt ut fra komponenten så den kan
// testes med `node --test`. Laster, feil og datafeil er ulike tilstander med
// ulik tekst (P-08). Et forsinket svar for en tidligere vakt eller sesjon
// meldes aldri (P-09).

import {
  ApiFeil,
  gjeldendeSesjonsgenerasjon,
  hentKandidater,
  type EkskludertKandidat,
  type Kandidatsvar,
  type RangertKandidat,
  type UtelukkelsesOppsummering,
} from "./api";
import { INGEN_KONTAKT, RESERVETEKST, TEKSTER, feiltekst } from "./tekster";

export type Kandidattilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "feil"; tekst: string }
  | { type: "datafeil"; datagrense: string }
  | { type: "ingen_gyldige"; utelukkelser: UtelukkelsesOppsummering }
  | { type: "klar"; kandidater: RangertKandidat[]; utelukkelser: UtelukkelsesOppsummering };

/** Så mange av de høyest rangerte vises før «Vis alle gyldige kandidater» (SM-3, AV-15). */
export const SYNLIGE_KANDIDATER = 5;

/**
 * De fem første i rangert rekkefølge, eller alle når `visAlle` er satt (FR9).
 * Listen fra API-et er allerede sortert etter plass, og min–maks er regnet over
 * alle Gyldige før kuttet, så kuttet endrer ingen poeng.
 */
export function synligeKandidater<T>(kandidater: readonly T[], visAlle: boolean): T[] {
  return visAlle ? [...kandidater] : kandidater.slice(0, SYNLIGE_KANDIDATER);
}

export function tilstandFraSvar(svar: Kandidatsvar): Kandidattilstand {
  if (svar.status === "ok") {
    // `ok` har alltid minst én Kandidat (FR6, AD-4). En tom liste er kontraktsbrudd og
    // vises som feil, aldri som tom liste eller som tomtilstanden.
    if (svar.kandidater.length === 0) return { type: "feil", tekst: RESERVETEKST };
    return { type: "klar", kandidater: svar.kandidater, utelukkelser: svar.utelukkelser };
  }
  if (svar.status === "ingen_gyldige_kandidater") return { type: "ingen_gyldige", utelukkelser: svar.utelukkelser };
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
 * Teksten i preferansetaggen (UX-DR11, P-05): kategorien når preferansen er tolket,
 * ellers statusen. En kategori frontend ikke kjenner, vises som den er.
 */
export function preferansetekst(kandidat: Pick<RangertKandidat, "tolkestatus" | "preferansekategori">): string {
  const t = TEKSTER.kandidatflate;
  if (kandidat.tolkestatus === "tolket") {
    const kategori = kandidat.preferansekategori ?? "";
    return t.preferansekategorier[kategori] ?? kategori;
  }
  return t.tolkestatuser[kandidat.tolkestatus];
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
