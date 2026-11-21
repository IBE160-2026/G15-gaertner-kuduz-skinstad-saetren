// App: sesjonsvarsleren ved 401 (story 1.4/1.5) og ruten til godkjenningsflaten
// (story 3.1). Stien settes med history.replaceState før render, fordi App
// leser window.location.pathname ved oppstart.
import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../../src/App";
import { INNLOGGING_STI, OVERSIKT_STI, godkjenningssti } from "../../src/navigasjon";
import { TEKSTER } from "../../src/tekster";
import { GODKJENNING_JONAS, MEG, TO_GYLDIGE, VAKT_4127, VAKTOVERSIKT, falskFetchMedReserve as falskFetch, feil, kallTil, ok } from "./hjelpere";

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

test("godkjenning navigerer til oppdatert Vaktvalg med konkret melding som fjernes ved neste valg", async () => {
  settSti(godkjenningssti(4127, 6));
  const oppdatert = {
    ...VAKTOVERSIKT,
    krever_handling: [{ ...VAKTOVERSIKT.krever_handling[0], vaktnummer: 4189 }],
    bemannet: [...VAKTOVERSIKT.bemannet, {
      vaktnummer: 4127, vakttype: "dag" as const,
      start: VAKT_4127.start, slutt: VAKT_4127.slutt,
      ansatt: { navn: "Jonas Bakke", stilling: "Sykepleier", ansiennitet: 5 },
    }],
  };
  const fetch = falskFetch({
    "/api/meg": ok(MEG),
    "/api/vakter/4127/kandidater/6": ok(GODKJENNING_JONAS),
    "POST /api/vakter/4127/kandidater/6": ok({ status: "godkjent" }),
    "/api/vaktoversikt": ok(oppdatert),
    "/api/vakter/4189": ok({ ...VAKT_4127, vaktnummer: 4189 }),
    "/api/vakter/4189/kandidater": ok(TO_GYLDIGE),
  });
  render(<App />);
  const bruker = userEvent.setup();
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: TEKSTER.godkjenning.godkjenn }));
  const bekreftelse = TEKSTER.vaktvalg.godkjent("Jonas Bakke", 4127);
  expect(await screen.findByText(bekreftelse)).toBeTruthy();
  expect(window.location.pathname).toBe(OVERSIKT_STI);
  expect(kallTil(fetch, "/api/vaktoversikt")).toBe(1);
  expect(screen.getByText("Jonas Bakke")).toBeTruthy();
  await bruker.click(screen.getByRole("button", { name: TEKSTER.vaktvalg.velgVakt }));
  expect(screen.queryByText(bekreftelse)).toBeNull();
});
