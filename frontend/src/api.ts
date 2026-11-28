// HTTP mot API-et gjennom Vite-proxyen for /api (OP-10). Sesjonen ligger i en
// httpOnly-cookie som nettleseren sender selv. Tokenet ses aldri av koden her.

export type Innlogget = { navn: string; avdeling: string; demomodus: boolean };
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
// sortert etter plass i Rangeringen (story 4.4). Datafeil er et 200-svar uten liste (P-08).
// `minutter_i_uka`: hele minutter i uka Vakten starter i, uten Vakten selv (story 4.1, FR8).
export type Ulempebelastning = {
  dagtimer: number;
  kveldstimer: number;
  helgetimer: number;
  natttimer: number;
  poeng: number;
  score: number;
};
export type Kostnad = {
  total: number; ordinære_timer: number; overtidstimer: number; ordinær_sats: number; overtidssats: number;
};
export type Kandidat = {
  id: number; navn: string; kompetansenivå: number; minutter_i_uka: number;
  // Fra backend (story 4.2, P-04): prosent av 36 t, uavrundet og ikke kuttet, og om uavrundet tid er minst 32,4 t.
  timebelastning_prosent: number; hoy_belastning: boolean;
  ulempebelastning: Ulempebelastning; kostnad: Kostnad;
};

// Rangeringen (story 4.4, FR9). Poengene er uavrundet og avrundes ved visning (K-03).
// `preferansekategori` er satt bare når `tolkestatus` er "tolket" (P-05).
export type Tolkestatus = "tolket" | "venter_paa_tolkning" | "kunne_ikke_tolkes" | "ingen_registrert";
export type Faktor = "kostnad" | "timebelastning" | "ulempe" | "preferanse";
export type RangertKandidat = Kandidat & {
  grunnlagsmerke: string;
  faktorretninger: Partial<Record<Faktor, "opp" | "ned">>;
  stilling: string; ansiennitet: number; plass: number; totalscore: number;
  faktorpoeng: { kostnad: number; timebelastning: number; ulempe: number };
  preferansepoeng: number; tolkestatus: Tolkestatus; preferansekategori: string | null;
  // Råteksten, for forhåndsutfylling når teksten endres (story 5.9). `null` er «Ingen registrert».
  preferansetekst: string | null;
};

type Avveiningsgrunnlag = { vaktnummer: number; kandidat_id: number; grunnlagsmerke: string };
export type Avveiningssvar = Avveiningsgrunnlag & (
  | ({ status: "ok"; modell: string; paastander: string[] } & (
      | { ki_kilde: "live" | "mal" }
      | { ki_kilde: "forhandsgenerert"; generert: string }
    ))
  | { status: "avveining_feilet" }
);

export function hentAvveining(vaktnummer: number, id: number): Promise<Avveiningssvar | { status: "datafeil" }> {
  return kall(`/api/vakter/${vaktnummer}/kandidater/${id}/avveining`, {}, true);
}

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
  | { status: "ok"; kandidater: RangertKandidat[]; utelukkelser: UtelukkelsesOppsummering }
  | { status: "ingen_gyldige_kandidater"; kandidater: RangertKandidat[]; utelukkelser: UtelukkelsesOppsummering }
  | { status: "datafeil"; kode: string; datagrense: string };

// GET /api/vakter/{nr}/kandidater/{ansatt_id} (story 3.1). Bare for en Gyldig
// kandidat. Utelukket eller ukjent Ansatt gir 404 `ikke_funnet` (NFR2).
// `kandidat` er en fullt rangert kandidat (story 4.5), og `topprangert` er nr. 1
// i samme rangering, eller `null` nøyaktig når `kandidat.plass` er 1 (UX-DR18).
export type Godkjenningssvar =
  | { status: "ok"; vakt: Vaktdetaljer; kandidat: RangertKandidat; topprangert: RangertKandidat | null; grunnlagsmerke: string }
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

export function godkjennErstatning(vaktnummer: number, ansattId: number, grunnlagsmerke: string): Promise<
  { status: "godkjent" } | { status: "datafeil"; kode: string; datagrense: string }
> {
  return kall(`/api/vakter/${vaktnummer}/kandidater/${ansattId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grunnlagsmerke }),
  }, true);
}

export function provPreferanse(vaktnummer: number, ansattId: number): Promise<{ status: "tolket" | "feilet" | "endret" }> {
  return kall(`/api/vakter/${vaktnummer}/kandidater/${ansattId}/preferanse`, { method: "POST" }, true);
}

// PUT (story 5.9, P-10B). Lagrer ny tekst og tolker den. `uendret`: samme tekst som lagret;
// `ingen`: tom tekst; `venter`: ingen KI eller låsen ble ikke ledig; `endret`: en nyere endring kom imellom.
export type LagrePreferanseStatus = "tolket" | "feilet" | "endret" | "uendret" | "ingen" | "venter";

export function lagrePreferanse(vaktnummer: number, ansattId: number, tekst: string): Promise<{ status: LagrePreferanseStatus }> {
  return kall(`/api/vakter/${vaktnummer}/kandidater/${ansattId}/preferanse`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tekst }),
  }, true);
}
