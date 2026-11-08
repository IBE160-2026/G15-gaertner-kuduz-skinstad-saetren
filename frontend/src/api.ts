// HTTP mot API-et gjennom Vite-proxyen for /api (OP-10). Sesjonen ligger i en
// httpOnly-cookie som nettleseren sender selv. Tokenet ses aldri av koden her.

export type Innlogget = { navn: string; avdeling: string };
export type PassordKilde = "tilfeldig" | "personlig" | null;

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
