// Vaktvalg (story 1.5): feil og «Prøv igjen». 401-tilstanden testes gjennom App
// i app.test.tsx, fordi det er sesjonsvarsleren i App som viser innloggingen.
import { expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Vaktvalg from "../../src/komponenter/Vaktvalg";
import { TEKSTER, feiltekst } from "../../src/tekster";
import { VAKTOVERSIKT, falskFetch, feil, kallTil, ok } from "./hjelpere";

const t = TEKSTER.vaktvalg;
const URL = "/api/vaktoversikt";

test("feil gir «Prøv igjen», og et trykk henter oversikten på nytt", async () => {
  const fetch = falskFetch({ [URL]: [feil(500, "intern_feil"), ok(VAKTOVERSIKT)] });
  const bruker = userEvent.setup();
  render(<Vaktvalg onVelgVakt={vi.fn()} />);

  const varsel = await screen.findByRole("alert");
  expect(within(varsel).getByText(feiltekst("intern_feil"))).toBeTruthy();
  expect(kallTil(fetch, URL)).toBe(1);

  await bruker.click(within(varsel).getByRole("button", { name: TEKSTER.provIgjen }));

  expect(await screen.findByRole("heading", { name: t.kreverHandling })).toBeTruthy();
  expect(screen.getByRole("heading", { name: t.vaktoverskrift(4127, "Dagvakt", VAKTOVERSIKT.avdeling) })).toBeTruthy();
  expect(screen.queryByRole("alert")).toBeNull();
  expect(kallTil(fetch, URL)).toBe(2);
});
