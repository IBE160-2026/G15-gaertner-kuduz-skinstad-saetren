// Godkjenningsflaten (story 3.1): «Godkjenn erstatning» gjør ingen kall
// (beslutning 2A), «Avbryt» går tilbake, og datafeil og 404 viser ingen knapper
// for godkjenning (P-08, beslutning 3A).
import { expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Godkjenningsflate from "../../src/komponenter/Godkjenningsflate";
import { datoOgKlokke } from "../../src/format";
import { kandidatsti } from "../../src/navigasjon";
import { TEKSTER } from "../../src/tekster";
import { GODKJENNING_DATAFEIL, GODKJENNING_JONAS, falskFetch, feil, ok, type Svar } from "./hjelpere";

const t = TEKSTER.godkjenning;
const URL = "/api/vakter/4127/kandidater/6";

function rendreMed(svar: Svar) {
  const fetch = falskFetch({ [URL]: svar });
  const onTilbake = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} />);
  return { fetch, onTilbake, bruker: userEvent.setup() };
}

test("«Godkjenn erstatning» gjør ingen kall og viser bare at ingenting er lagret; «Avbryt» går tilbake", async () => {
  const { fetch, onTilbake, bruker } = rendreMed(ok(GODKJENNING_JONAS));

  expect(await screen.findByRole("heading", { name: "Jonas Bakke" })).toBeTruthy();
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(String(fetch.mock.calls[0][0])).toBe(URL);
  const status = screen.getByRole("status");
  expect(status.textContent).toBe("");

  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(status.textContent).toBe(t.ikkeLagret);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(onTilbake).not.toHaveBeenCalled();

  await bruker.click(screen.getByRole("button", { name: t.avbryt }));
  expect(onTilbake).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledTimes(1);
});

test("datafeil viser ingen knapper for godkjenning", async () => {
  rendreMed(ok(GODKJENNING_DATAFEIL));

  const varsel = await screen.findByRole("alert");
  expect(within(varsel).getByText(t.datafeil)).toBeTruthy();
  expect(within(varsel).getByText(t.datagrense(datoOgKlokke(GODKJENNING_DATAFEIL.datagrense)))).toBeTruthy();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();
  expect(screen.queryByRole("button", { name: t.avbryt })).toBeNull();
  expect(screen.getByRole("link", { name: t.tilbake }).getAttribute("href")).toBe(kandidatsti(4127));
});

test("404 viser «kan ikke velges» og ingen knapper for godkjenning", async () => {
  const { onTilbake, bruker } = rendreMed(feil(404, "ikke_funnet"));

  expect(await screen.findByRole("heading", { name: t.ikkeFunnet })).toBeTruthy();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();
  expect(screen.queryByRole("button", { name: t.avbryt })).toBeNull();

  await bruker.click(screen.getByRole("link", { name: t.tilbake }));
  expect(onTilbake).toHaveBeenCalledTimes(1);
});
