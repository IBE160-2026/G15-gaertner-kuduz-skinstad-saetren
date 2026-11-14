// App: sesjonsvarsleren ved 401 (story 1.4/1.5) og ruten til godkjenningsflaten
// (story 3.1). Stien settes med history.replaceState før render, fordi App
// leser window.location.pathname ved oppstart.
import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../../src/App";
import { INNLOGGING_STI, OVERSIKT_STI, godkjenningssti } from "../../src/navigasjon";
import { TEKSTER } from "../../src/tekster";
import { GODKJENNING_JONAS, MEG, falskFetch, feil, kallTil, ok } from "./hjelpere";

function settSti(sti: string) {
  window.history.replaceState(null, "", sti);
}

test("401 fra vaktoversikten etter bekreftet sesjon viser innloggingen med «sesjonen er utløpt»", async () => {
  settSti(OVERSIKT_STI);
  const fetch = falskFetch({
    "/api/meg": ok(MEG),
    "/api/vaktoversikt": feil(401, "mangler_sesjon"),
    "/api/innloggingsinfo": ok({ passord_kilde: "tilfeldig" }),
  });
  render(<App />);

  expect(await screen.findByRole("heading", { name: TEKSTER.loggInn.overskrift })).toBeTruthy();
  expect(screen.getByRole("alert").textContent).toBe(TEKSTER.sesjonUtlopt);
  expect(window.location.pathname).toBe(INNLOGGING_STI);
  expect(kallTil(fetch, "/api/vaktoversikt")).toBe(1);
});

test("stien /vakt/4127/godkjenning/6 viser godkjenningsflaten for kandidaten", async () => {
  const sti = godkjenningssti(4127, 6);
  expect(sti).toBe("/vakt/4127/godkjenning/6");
  settSti(sti);
  const fetch = falskFetch({
    "/api/meg": ok(MEG),
    "/api/vakter/4127/kandidater/6": ok(GODKJENNING_JONAS),
  });
  render(<App />);

  expect(await screen.findByRole("heading", { name: "Jonas Bakke" })).toBeTruthy();
  expect(screen.getByRole("button", { name: TEKSTER.godkjenning.godkjenn })).toBeTruthy();
  expect(screen.queryByRole("heading", { name: TEKSTER.sideIkkeFunnet })).toBeNull();
  expect(window.location.pathname).toBe(sti);
  // Verken kandidatflaten eller vaktvalget er rendret.
  expect(kallTil(fetch, "/api/vakter/4127")).toBe(0);
  expect(kallTil(fetch, "/api/vaktoversikt")).toBe(0);
});
