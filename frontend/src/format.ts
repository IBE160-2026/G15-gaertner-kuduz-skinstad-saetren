// Rene formateringsfunksjoner for Vaktvalg og kandidatflaten. Alt vises i
// Europe/Oslo, uansett tidssonen til nettleseren. Bare tallene hentes fra
// `Intl.DateTimeFormat(...).formatToParts`. Ukedagnavn, skilletegn og
// nuller foran settes sammen her, så teksten ikke avhenger av ICU-versjonen.

import type { Vakttype, VaktSomManglerBemanning } from "./api";
import { TEKSTER } from "./tekster";

export const TIDSSONE = "Europe/Oslo";

type OsloDeler = { aar: number; maaned: number; dag: number; time: number; minutt: number };

const delformat = new Intl.DateTimeFormat("nb-NO", {
  timeZone: TIDSSONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

function deler(iso: string | Date): OsloDeler {
  const tid = typeof iso === "string" ? new Date(iso) : iso;
  const verdier: Record<string, number> = {};
  for (const del of delformat.formatToParts(tid)) {
    if (del.type !== "literal") verdier[del.type] = Number(del.value);
  }
  return {
    aar: verdier.year,
    maaned: verdier.month,
    dag: verdier.day,
    // Noen ICU-versjoner gir «24» ved midnatt selv med h23.
    time: verdier.hour % 24,
    minutt: verdier.minute,
  };
}

function to(tall: number): string {
  return String(tall).padStart(2, "0");
}

/** «27.09.2026» */
function dato(d: OsloDeler): string {
  return `${to(d.dag)}.${to(d.maaned)}.${d.aar}`;
}

/** «06:14» */
function klokke(d: OsloDeler): string {
  return `${to(d.time)}:${to(d.minutt)}`;
}

function sammeDato(a: OsloDeler, b: OsloDeler): boolean {
  return a.aar === b.aar && a.maaned === b.maaned && a.dag === b.dag;
}

/** 0 = mandag … 6 = søndag, for en kalenderdato. */
function ukedagsindeks(d: OsloDeler): number {
  return (new Date(Date.UTC(d.aar, d.maaned - 1, d.dag)).getUTCDay() + 6) % 7;
}

/** «Søndag 27.09.2026» */
export function ukedagOgDato(iso: string): string {
  const d = deler(iso);
  return `${TEKSTER.format.ukedager[ukedagsindeks(d)]} ${dato(d)}`;
}

/** «Vakt #4127 — Dagvakt 27.09.2026» for brødsmulestien. */
export function vaktBrodsmule(nummer: number, vakttype: Vakttype, start: string): string {
  return TEKSTER.kandidatflate.brodsmule(nummer, vakttypenavn(vakttype), dato(deler(start)));
}

/** «23:00–07:00 (8 t)». Varigheten er reell tid, også over sommertidsskiftet. */
export function tidsrom(start: string, slutt: string): string {
  const timer = (new Date(slutt).getTime() - new Date(start).getTime()) / 3_600_000;
  const varighet = Number.isInteger(timer) ? String(timer) : String(Math.round(timer * 10) / 10).replace(".", ",");
  return `${klokke(deler(start))}–${klokke(deler(slutt))} (${varighet} ${TEKSTER.format.timer})`;
}

/** «27.09.2026 06:20» */
export function datoOgKlokke(iso: string): string {
  const d = deler(iso);
  return `${dato(d)} ${klokke(d)}`;
}

export function vakttypenavn(vakttype: Vakttype): string {
  return TEKSTER.format.vakttyper[vakttype];
}

/** ISO 8601-uke og ISO-år for en kalenderdato. */
export function isoUke(d: { aar: number; maaned: number; dag: number }): { uke: number; aar: number } {
  const dagen = new Date(Date.UTC(d.aar, d.maaned - 1, d.dag));
  const ukedag = (dagen.getUTCDay() + 6) % 7; // mandag = 0
  // Torsdagen i samme uke avgjør ISO-året.
  const torsdag = new Date(dagen.getTime() + (3 - ukedag) * 86_400_000);
  const aar = torsdag.getUTCFullYear();
  const forsteJanuar = Date.UTC(aar, 0, 1);
  const uke = Math.floor((torsdag.getTime() - forsteJanuar) / 86_400_000 / 7) + 1;
  return { uke, aar };
}

/**
 * «Uke 39–40, 2026», «Uke 39, 2026» eller «Uke 52, 2026 – uke 1, 2027».
 * Perioden er halvåpen, så siste dag er dagen før `slutt` i Oslo.
 */
export function periodetekst(start: string, slutt: string): string {
  const forste = isoUke(deler(start));
  const siste = isoUke(deler(new Date(new Date(slutt).getTime() - 1)));
  const t = TEKSTER.format;
  if (forste.aar !== siste.aar) {
    return `${t.uke} ${forste.uke}, ${forste.aar} – ${t.uke.toLowerCase()} ${siste.uke}, ${siste.aar}`;
  }
  if (forste.uke === siste.uke) return `${t.uke} ${forste.uke}, ${forste.aar}`;
  return `${t.uke} ${forste.uke}–${siste.uke}, ${forste.aar}`;
}

/** «kl. 06:14» samme dato som vaktens start, ellers «26.09 kl. 21:40». */
export function meldtFraTidspunkt(meldtFra: string, vaktstart: string): string {
  const m = deler(meldtFra);
  const kl = `${TEKSTER.format.kl} ${klokke(m)}`;
  return sammeDato(m, deler(vaktstart)) ? kl : `${to(m.dag)}.${to(m.maaned)} ${kl}`;
}

/**
 * Linja i varselboksen, delt i tre så statusen kan vises i fet `danger`:
 * «Søndag 27.09.2026 · 07:00–15:00 (8 t) · » + «Mangler bemanning» +
 * « — Silje Amundsen meldt fra sykemeldt kl. 06:14».
 */
export function varsellinje(vakt: VaktSomManglerBemanning): { foer: string; status: string; etter: string } {
  const foer = `${ukedagOgDato(vakt.start)} · ${tidsrom(vakt.start, vakt.slutt)} · `;
  let etter = "";
  if (vakt.satt_opp) {
    const deler = [vakt.satt_opp, TEKSTER.format.meldtFra];
    if (vakt.grunn) deler.push(vakt.grunn);
    if (vakt.meldt_fra) deler.push(meldtFraTidspunkt(vakt.meldt_fra, vakt.start));
    etter = ` — ${deler.join(" ")}`;
  }
  return { foer, status: TEKSTER.format.manglerBemanning, etter };
}

/** Om `denne` starter på en annen dato i Oslo enn `forrige`. Uten forrige: sann. */
export function erNyttDogn(forrige: string | null | undefined, denne: string): boolean {
  if (!forrige) return true;
  return !sammeDato(deler(forrige), deler(denne));
}

/**
 * Klassene for rad `i` i tabellen over bemannede vakter: `row-alt` på annenhver
 * rad, `dogn-start` (linje over) når et nytt døgn begynner etter første rad, og
 * `datoUthevet` på første rad i hvert døgn, også rad 0.
 */
export function radklasser(
  vakter: readonly { start: string }[],
  i: number,
): { rad: string | undefined; datoUthevet: boolean } {
  const nyttDogn = erNyttDogn(vakter[i - 1]?.start, vakter[i].start);
  const klasser = [i % 2 === 1 ? "row-alt" : "", i > 0 && nyttDogn ? "dogn-start" : ""].filter(Boolean);
  return { rad: klasser.length ? klasser.join(" ") : undefined, datoUthevet: nyttDogn };
}
