export const OVERSIKT_STI = "/turnus/kirurgisk-sengepost";
export const INNLOGGING_STI = "/logg-inn";

export function maalEtterBekreftetSesjon(sti: string): string {
  return sti === INNLOGGING_STI || sti === "/" ? OVERSIKT_STI : sti;
}

export function naviger(sti: string, erstatt = false): void {
  if (window.location.pathname === sti) return;
  if (erstatt) window.history.replaceState(null, "", sti);
  else window.history.pushState(null, "", sti);
}
