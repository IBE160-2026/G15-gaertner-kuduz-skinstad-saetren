// Felles hjelpere for komponenttestene (Vitest, Testing Library, jsdom).
// Testdataene har typene fra src/api.ts, så feil form fanges av `tsc` i
// `npm run build` (tsconfig.test.json). Oppsett og opprydding for hver test
// står i oppsett.ts.
import { vi, type Mock } from "vitest";
import type {
  Godkjenningssvar, Innlogget, Kandidatsvar, RangertKandidat,
  UtelukkelsesOppsummering, Vaktdetaljer, Vaktoversikt,
} from "../../src/api";

// Statuser der `Response` ikke godtar en kropp.
const UTEN_KROPP = new Set([101, 204, 205, 304]);

export function json(data: unknown, status = 200): Response {
  if (UTEN_KROPP.has(status)) return new Response(null, { status });
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });
}

/** Tekst brukt som bokstavelig del av et regulært uttrykk. */
export function regexTekst(tekst: string): string {
  return tekst.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Regex av en tekstmal fra TEKSTER. Kall malen med en plassholder, for eksempel
 * `malRegex(g.velgEtikett(P), P)`. Plassholderen kan være hva som helst.
 */
export function malRegex(utfylt: string, plassholder: string | number): RegExp {
  return new RegExp(utfylt.split(String(plassholder)).map(regexTekst).join(".+"));
}

/** Ett svar fra den falske `fetch`: HTTP-status og JSON-kropp. */
export type Svar = { status: number; kropp: unknown };

export const ok = (kropp: unknown): Svar => ({ status: 200, kropp });
/** Feilformen fra API-et, `{ kode, melding }` (AD-4). */
export const feil = (status: number, kode: string): Svar => ({ status, kropp: { kode, melding: "Fra testen." } });

export type FalskFetch = Mock<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>;

/**
 * Rutenøkkelen «METODE /sti». En nøkkel uten metode, for eksempel
 * "/api/meg", gjelder GET.
 */
function rutenokkel(nokkel: string): string {
  const treff = /^([A-Z]+) (\/.*)$/.exec(nokkel);
  return treff ? `${treff[1]} ${treff[2]}` : `GET ${nokkel}`;
}

function kallnokkel(input: RequestInfo | URL, init?: RequestInit): string {
  return `${(init?.method ?? "GET").toUpperCase()} ${String(input)}`;
}

// Kall testen ikke har satt opp svar for. Sjekkes i afterEach (oppsett.ts),
// fordi et kast inne i fetch bare blir «Får ikke kontakt» i komponenten.
let uventede: string[] = [];

/** For oppsett.ts: kallene uten svar siden forrige test, og nullstill listen. */
export function hentOgNullstillUventede(): string[] {
  const funnet = uventede;
  uventede = [];
  return funnet;
}

/**
 * Stubber `fetch` med ett sett svar per rute. Nøkkelen er «METODE /sti», eller
 * bare «/sti» for GET. Hver rute har en kø: svarene gis i rekkefølge, og det
 * siste gjentas. Et kall uten rute, også med en annen metode enn ruten har,
 * feiler testen.
 */
export function falskFetch(ruter: Record<string, Svar | Svar[]>): FalskFetch {
  const koer = new Map<string, Svar[]>(
    Object.entries(ruter).map(([nokkel, svar]) => [rutenokkel(nokkel), Array.isArray(svar) ? [...svar] : [svar]]),
  );
  const fetch: FalskFetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const nokkel = kallnokkel(input, init);
    const ko = koer.get(nokkel);
    if (!ko || ko.length === 0) {
      uventede.push(nokkel);
      throw new Error(`Uventet kall: ${nokkel}`);
    }
    const svar = ko.length > 1 ? ko.shift()! : ko[0];
    return json(svar.kropp, svar.status);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

/** Antall kall til en rute, «METODE /sti» eller bare «/sti» for GET. */
export function kallTil(fetch: FalskFetch, rute: string): number {
  const mal = rutenokkel(rute);
  return fetch.mock.calls.filter(([input, init]) => kallnokkel(input, init) === mal).length;
}

/** De eldre flyttestene kjører som uten modell. Tillat forklaring bare for kandidaten
 * som åpnes automatisk i hvert oppsatt GET-svar. Andre kall krever egen rute. */
export function falskFetchMedReserve(ruter: Record<string, Svar | Svar[]>): FalskFetch {
  const reserver: Record<string, Svar> = {};
  for (const [sti, kø] of Object.entries(ruter)) {
    const treff = /^\/api\/vakter\/(\d+)\/kandidater(?:\/(\d+))?$/.exec(sti);
    if (!treff) continue;
    for (const { kropp } of Array.isArray(kø) ? kø : [kø]) {
      const svar = kropp as Godkjenningssvar | Kandidatsvar | null;
      if (svar?.status !== "ok") continue;
      const åpne = "kandidater" in svar ? svar.kandidater.filter((r) => r.plass === 1) : [svar.kandidat];
      for (const r of åpne) {
        reserver[`/api/vakter/${treff[1]}/kandidater/${r.id}/avveining`] = ok({
          status: "avveining_feilet", vaktnummer: Number(treff[1]), kandidat_id: r.id, grunnlagsmerke: r.grunnlagsmerke,
        });
      }
    }
  }
  return falskFetch({ ...reserver, ...ruter });
}

// --- Testdata (samme vakt og ansatte som i fiktive testdata) -------------------

export const MEG: Innlogget = { demomodus: false, navn: "Kari Vestby", avdeling: "Kirurgisk sengepost" };

export const VAKTOVERSIKT: Vaktoversikt = {
  avdeling: "Kirurgisk sengepost",
  periode_start: "2026-09-21T00:00:00+02:00",
  periode_slutt: "2026-10-05T00:00:00+02:00",
  sist_oppdatert: "2026-09-27T06:20:00+02:00",
  antall_ansatte: 24,
  krever_handling: [{
    vaktnummer: 4127, vakttype: "dag",
    start: "2026-09-27T07:00:00+02:00", slutt: "2026-09-27T15:00:00+02:00",
    satt_opp: "Silje Amundsen", meldt_fra: "2026-09-27T06:14:00+02:00", grunn: "sykemeldt",
  }],
  bemannet: [{
    vaktnummer: 4128, vakttype: "kveld",
    start: "2026-09-27T15:00:00+02:00", slutt: "2026-09-27T22:30:00+02:00",
    ansatt: { navn: "Eirik Moen", stilling: "Sykepleier", ansiennitet: 7 },
  }],
};

export const VAKT_4127: Vaktdetaljer = {
  avdeling: "Kirurgisk sengepost", vaktnummer: 4127, vakttype: "dag",
  start: "2026-09-27T07:00:00+02:00", slutt: "2026-09-27T15:00:00+02:00", minstenivå: 3,
};

export const INGEN_UTELUKKET: UtelukkelsesOppsummering = { totalt: 0, per_regel: [], utelukkede: [] };

export const TO_UTELUKKET: UtelukkelsesOppsummering = {
  totalt: 2,
  per_regel: [
    { årsak: "kompetanse-minstekrav", antall: 1 },
    { årsak: "11-timersregelen", antall: 1 },
  ],
  utelukkede: [
    { id: 11, navn: "Lars Holm", årsaker: ["kompetanse-minstekrav"] },
    { id: 12, navn: "Nora Lie", årsaker: ["11-timersregelen"] },
  ],
};

/**
 * Rangeringens felt (story 4.4) for testkandidater der rangeringen ikke er temaet:
 * 50 for kostnad og timer (alle like), 100 i Ulempescore og 50 i preferanse.
 */
export const rangering = (plass: number) => ({
  grunnlagsmerke: String(plass).padStart(64, "0"),
  faktorretninger: { kostnad: "ned", timebelastning: "ned", ulempe: "opp", preferanse: "ned" } as const,
  stilling: "Sykepleier", ansiennitet: 3, plass, totalscore: 57.5,
  faktorpoeng: { kostnad: 50, timebelastning: 50, ulempe: 100 },
  preferansepoeng: 50, tolkestatus: "venter_paa_tolkning" as const, preferansekategori: null,
  preferansetekst: null,
});

/**
 * Jonas slik godkjenningsgrunnlaget sender ham (story 4.5: `RangertKandidat`,
 * ikke bare `Kandidat`). Tallene er #4127s fasit uten lagrede tolkninger
 * (AV-07): nr. 1 med 79,40 (backend `test_rangering.py`,
 * UTEN_TOLKNING_4127/FAKTORER_4127).
 */
export const JONAS: RangertKandidat = {
  grunnlagsmerke: "a".repeat(64),
  faktorretninger: { kostnad: "opp", timebelastning: "opp", ulempe: "opp", preferanse: "ned" },
  id: 6, navn: "Jonas Bakke", kompetansenivå: 3, minutter_i_uka: 960,
  timebelastning_prosent: 100 * 960 / 2160, hoy_belastning: false,
  kostnad: { total: 2960, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 370, overtidssats: 555 },
  ulempebelastning: { dagtimer: 67, kveldstimer: 4, helgetimer: 15, natttimer: 2, poeng: 40, score: 100 * (1 - 40 / 300) },
  stilling: "Sykepleier", ansiennitet: 3, plass: 1, totalscore: 3335 / 42,
  faktorpoeng: { kostnad: 1780 / 21, timebelastning: 100, ulempe: 260 / 3 },
  preferansepoeng: 50, tolkestatus: "venter_paa_tolkning", preferansekategori: null,
  preferansetekst: "Jeg trenger ikke flere vakter, men tar gjerne en ekstra ved behov.",
};

/** To Gyldige kandidater i rangert rekkefølge, som fra API-et. */
export const TO_GYLDIGE = {
  status: "ok",
  kandidater: [
    { ...JONAS, ...rangering(1) },
    {
      id: 5, navn: "Mette Solberg", kompetansenivå: 4, minutter_i_uka: 0,
      timebelastning_prosent: 0, hoy_belastning: false,
      kostnad: { total: 2400, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 300, overtidssats: 450 },
      ulempebelastning: { dagtimer: 0, kveldstimer: 0, helgetimer: 0, natttimer: 0, poeng: 0, score: 100 },
      ...rangering(2),
    },
  ],
  utelukkelser: INGEN_UTELUKKET,
} satisfies Kandidatsvar;

/** #4189: alle 24 utelukket (3 kompetanse, 2 kollisjon, 18 på 11 t, 1 på 35 t). */
export const UTELUKKET_4189: UtelukkelsesOppsummering = {
  totalt: 24,
  per_regel: [
    { årsak: "kompetanse-minstekrav", antall: 3 },
    { årsak: "kolliderende vakt", antall: 2 },
    { årsak: "11-timersregelen", antall: 18 },
    { årsak: "35-timersregelen", antall: 1 },
  ],
  utelukkede: [
    { id: 11, navn: "Lars Holm", årsaker: ["kompetanse-minstekrav"] },
    { id: 12, navn: "Nora Lie", årsaker: ["11-timersregelen"] },
  ],
};

export const INGEN_GYLDIGE = {
  status: "ingen_gyldige_kandidater", kandidater: [], utelukkelser: UTELUKKET_4189,
} satisfies Kandidatsvar;

/** Kontraktsbrudd: `ok` skal aldri ha tom liste (FR6). */
export const OK_MED_TOM_LISTE = {
  status: "ok", kandidater: [], utelukkelser: UTELUKKET_4189,
} satisfies Kandidatsvar;

export const KANDIDATER_DATAFEIL = {
  status: "datafeil", kode: "mangler_turnusgrunnlag", datagrense: "2026-10-05T00:00:00+02:00",
} satisfies Kandidatsvar;

export const GODKJENNING_JONAS = {
  status: "ok", vakt: VAKT_4127, kandidat: JONAS, topprangert: null,
  grunnlagsmerke: "a".repeat(64),
} satisfies Godkjenningssvar;

/**
 * Mette for #4127 (plass 2, 72,40), med Jonas som topprangert (story 4.5,
 * I/O-matrisen). Samme kostnad som Jonas (begge 16 t ordinær tid til 370 kr/t),
 * men høyere nivå og ulempe. Ulempefordelingen under er ikke egen fasit i
 * dokumentasjonen (bare poeng og score er det) — valgt slik at kveld/helg/natt
 * summerer korrekt til 180 poeng, for å teste fordelingsvisningen.
 */
const METTE_ULEMPE = { dagtimer: 0, kveldstimer: 0, helgetimer: 90, natttimer: 0, poeng: 180, score: 40 };
export const METTE: RangertKandidat = {
  grunnlagsmerke: "b".repeat(64),
  faktorretninger: { kostnad: "opp", timebelastning: "opp", ulempe: "ned", preferanse: "ned" },
  id: 5, navn: "Mette Solberg", kompetansenivå: 4, minutter_i_uka: 960,
  timebelastning_prosent: 100 * 960 / 2160, hoy_belastning: false,
  kostnad: { total: 2960, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 370, overtidssats: 555 },
  ulempebelastning: METTE_ULEMPE,
  stilling: "Sykepleier", ansiennitet: 9, plass: 2, totalscore: 3041 / 42,
  faktorpoeng: { kostnad: 1780 / 21, timebelastning: 100, ulempe: 40 },
  preferansepoeng: 50, tolkestatus: "venter_paa_tolkning", preferansekategori: null,
  preferansetekst: "Hvis dere mangler folk, stiller jeg gjerne på en ekstravakt.",
};

export const GODKJENNING_METTE = {
  status: "ok", vakt: VAKT_4127, kandidat: METTE, topprangert: JONAS,
  grunnlagsmerke: "b".repeat(64),
} satisfies Godkjenningssvar;

export const GODKJENNING_DATAFEIL = {
  status: "datafeil", kode: "mangler_turnusgrunnlag", datagrense: "2026-10-05T00:00:00+02:00",
} satisfies Godkjenningssvar;
