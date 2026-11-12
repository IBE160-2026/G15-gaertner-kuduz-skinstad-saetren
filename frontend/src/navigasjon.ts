export const OVERSIKT_STI = "/turnus/kirurgisk-sengepost";
export const INNLOGGING_STI = "/logg-inn";

// Regex-ene slipper bare gjennom positive heltall uten ledende null. Her stoppes
// tall som er for store til å representeres nøyaktig.
function positivtHeltall(tekst: string): number | null {
  const nummer = Number(tekst);
  return Number.isSafeInteger(nummer) ? nummer : null;
}

export function vaktnummerFraSti(sti: string): number | null {
  const treff = /^\/vakt\/([1-9]\d*)\/kandidater$/.exec(sti);
  return treff ? positivtHeltall(treff[1]) : null;
}

export function kandidatsti(vaktnummer: number): string {
  return `/vakt/${vaktnummer}/kandidater`;
}

// Godkjenningsflaten (story 3.1, beslutning 1A): `/vakt/<nr>/godkjenning/<ansatt_id>`.
export type Godkjenningsmaal = { vaktnummer: number; ansattId: number };

export function godkjenningFraSti(sti: string): Godkjenningsmaal | null {
  const treff = /^\/vakt\/([1-9]\d*)\/godkjenning\/([1-9]\d*)$/.exec(sti);
  if (!treff) return null;
  const vaktnummer = positivtHeltall(treff[1]);
  const ansattId = positivtHeltall(treff[2]);
  return vaktnummer !== null && ansattId !== null ? { vaktnummer, ansattId } : null;
}

export function godkjenningssti(vaktnummer: number, ansattId: number): string {
  return `/vakt/${vaktnummer}/godkjenning/${ansattId}`;
}

export function maalEtterBekreftetSesjon(sti: string): string {
  return sti === INNLOGGING_STI || sti === "/" ? OVERSIKT_STI : sti;
}

export function naviger(sti: string, erstatt = false): void {
  if (window.location.pathname === sti) return;
  if (erstatt) window.history.replaceState(null, "", sti);
  else window.history.pushState(null, "", sti);
}
