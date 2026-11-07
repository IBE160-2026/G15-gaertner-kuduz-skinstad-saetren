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

async function kall<T>(sti: string, init: Valg = {}): Promise<T> {
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

  let kropp: unknown;
  try {
    kropp = await respons.json();
  } catch {
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
  return kall<Innlogget>("/api/meg");
}

export async function hentInnloggingsinfo(): Promise<PassordKilde> {
  const svar = await kall<{ passord_kilde: PassordKilde }>("/api/innloggingsinfo");
  return svar.passord_kilde;
}
