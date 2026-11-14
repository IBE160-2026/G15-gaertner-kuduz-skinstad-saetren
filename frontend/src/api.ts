// HTTP mot API-et gjennom Vite-proxyen for /api (OP-10). Sesjonen ligger i en
// httpOnly-cookie som nettleseren sender selv. Tokenet ses aldri av koden her.

export type Innlogget = { navn: string; avdeling: string };
export type PassordKilde = "tilfeldig" | "personlig" | null;

// GET /api/vaktoversikt (story 1.5). Tidspunktene er ISO 8601 med offset.
export type Vakttype = "dag" | "mellom" | "kveld" | "natt";

export type VaktSomManglerBemanning = {
  vaktnummer: number;
  vakttype: Vakttype;
  start: string;
  slutt: string;
  satt_opp: string | null;
  meldt_fra: string | null;
  grunn: string | null;
};

export type BemannetVakt = {
  vaktnummer: number;
  vakttype: Vakttype;
  start: string;
  slutt: string;
  ansatt: { navn: string; stilling: string; ansiennitet: number };
};

export type Vaktoversikt = {
  avdeling: string;
  periode_start: string;
  periode_slutt: string;
  sist_oppdatert: string;
  antall_ansatte: number;
  krever_handling: VaktSomManglerBemanning[];
  bemannet: BemannetVakt[];
};

export type Vaktdetaljer = {
  avdeling: string;
  vaktnummer: number;
  vakttype: Vakttype;
  start: string;
  slutt: string;
  minstenivå: number;
};

// GET /api/vakter/{nr}/kandidater (story 2.1). Bare Gyldige kandidater,
// alfabetisk. Datafeil er et 200-svar uten liste (P-08).
export type Kandidat = { id: number; navn: string; kompetansenivå: number };

// Ekskludert-boksen (story 2.5, UX-DR15). `per_regel` følger regelmotorens
// rekkefølge, og summen der kan være større enn `totalt`.
export type RegelAntall = { årsak: string; antall: number };
export type EkskludertKandidat = { id: number; navn: string; årsaker: string[] };
export type UtelukkelsesOppsummering = {
  totalt: number;
  per_regel: RegelAntall[];
  utelukkede: EkskludertKandidat[];
};

export type Kandidatsvar =
  | { status: "ok"; kandidater: Kandidat[]; utelukkelser: UtelukkelsesOppsummering }
  | { status: "datafeil"; kode: string; datagrense: string };

// GET /api/vakter/{nr}/kandidater/{ansatt_id} (story 3.1). Bare for en Gyldig
// kandidat. Utelukket eller ukjent Ansatt gir 404 `ikke_funnet` (NFR2).
export type Godkjenningssvar =
  | { status: "ok"; vakt: Vaktdetaljer; kandidat: Kandidat }
  | { status: "datafeil"; kode: string; datagrense: string };

/** API-et svarte med feilformen `{ kode, melding }`. */
export class ApiFeil extends Error {
  readonly status: number;
  readonly kode: string;

  constructor(status: number, kode: string) {
    super(`API-feil ${status}: ${kode}`);
    this.name = "ApiFeil";
    this.status = status;
    this.kode = kode;
  }
}

/** Nettverksfeil, eller et svar som ikke er JSON (for eksempel 502 fra proxyen). */
export class IngenKontaktFeil extends Error {
  constructor() {
    super("Ingen kontakt med API-et");
    this.name = "IngenKontaktFeil";
  }
}

type Valg = { method?: string; body?: string; headers?: Record<string, string> };

let sesjonsgenerasjon = 0;
let vedAvvistSesjon: (() => void) | null = null;

export function nySesjonsgenerasjon(): number {
  return ++sesjonsgenerasjon;
}

export function gjeldendeSesjonsgenerasjon(): number {
  return sesjonsgenerasjon;
}

export function settSesjonsvarsler(varsler: (() => void) | null): void {
  vedAvvistSesjon = varsler;
}

async function kall<T>(sti: string, init: Valg = {}, beskyttet = false): Promise<T> {
  const generasjon = sesjonsgenerasjon;
  let respons: Response;
  try {
    respons = await fetch(sti, {
      ...init,
      credentials: "same-origin",
      headers: { Accept: "application/json", ...init.headers },
    });
  } catch {
    throw new IngenKontaktFeil();
  }

  // En proxy kan gi 401 uten JSON. Varsle før parsing, men bare om svaret
  // tilhører sesjonen som fremdeles er aktiv.
  if (beskyttet && respons.status === 401 && generasjon === sesjonsgenerasjon) {
    vedAvvistSesjon?.();
  }
  if (respons.status === 204) return undefined as T;

  let kropp: unknown;
  try {
    kropp = await respons.json();
  } catch {
    if (beskyttet && respons.status === 401) throw new ApiFeil(401, "mangler_sesjon");
    throw new IngenKontaktFeil();
  }

  if (!respons.ok) {
    const kode =
      typeof kropp === "object" && kropp !== null && "kode" in kropp && typeof kropp.kode === "string"
        ? kropp.kode
        : "";
    throw new ApiFeil(respons.status, kode);
  }
  return kropp as T;
}

export function loggInn(brukernavn: string, passord: string): Promise<Innlogget> {
  return kall<Innlogget>("/api/innlogging", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brukernavn, passord }),
  });
}

export function hentMeg(): Promise<Innlogget> {
  return kall<Innlogget>("/api/meg", {}, true);
}

export function loggUt(): Promise<unknown> {
  return kall<unknown>("/api/utlogging", { method: "POST" }, true);
}

export async function hentInnloggingsinfo(): Promise<PassordKilde> {
  const svar = await kall<{ passord_kilde: PassordKilde }>("/api/innloggingsinfo");
  return svar.passord_kilde;
}

export function hentVaktoversikt(): Promise<Vaktoversikt> {
  return kall<Vaktoversikt>("/api/vaktoversikt", {}, true);
}

export function hentVaktdetaljer(vaktnummer: number): Promise<Vaktdetaljer> {
  return kall<Vaktdetaljer>(`/api/vakter/${vaktnummer}`, {}, true);
}

export function hentKandidater(vaktnummer: number): Promise<Kandidatsvar> {
  return kall<Kandidatsvar>(`/api/vakter/${vaktnummer}/kandidater`, {}, true);
}

export function hentGodkjenningsgrunnlag(vaktnummer: number, ansattId: number): Promise<Godkjenningssvar> {
  return kall<Godkjenningssvar>(`/api/vakter/${vaktnummer}/kandidater/${ansattId}`, {}, true);
}
