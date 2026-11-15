// Godkjenningsflaten (story 3.2): aktiv bekreftelse og feilhåndtering.
import { expect, test, vi } from "vitest";
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { nySesjonsgenerasjon } from "../../src/api";
import userEvent from "@testing-library/user-event";
import Godkjenningsflate from "../../src/komponenter/Godkjenningsflate";
import { datoOgKlokke } from "../../src/format";
import { kandidatsti } from "../../src/navigasjon";
import { TEKSTER } from "../../src/tekster";
import { GODKJENNING_DATAFEIL, GODKJENNING_JONAS, falskFetch, feil, json, ok, type Svar } from "./hjelpere";

const t = TEKSTER.godkjenning;
const URL = "/api/vakter/4127/kandidater/6";

function rendreMed(svar: Svar, post?: Svar) {
  const fetch = falskFetch({ [URL]: svar, ...(post ? { [`POST ${URL}`]: post } : {}) });
  const onTilbake = vi.fn();
  const onGodkjent = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} onGodkjent={onGodkjent} />);
  return { fetch, onTilbake, onGodkjent, bruker: userEvent.setup() };
}

test("«Godkjenn erstatning» sender merket og navigerer bare etter suksess", async () => {
  const { fetch, onTilbake, onGodkjent, bruker } = rendreMed(ok(GODKJENNING_JONAS), ok({ status: "godkjent" }));

  expect(await screen.findByRole("heading", { name: "Jonas Bakke" })).toBeTruthy();
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(String(fetch.mock.calls[0][0])).toBe(URL);
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(onGodkjent).toHaveBeenCalledTimes(1);
  expect(onTilbake).not.toHaveBeenCalled();
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch.mock.calls[1][1]?.method).toBe("POST");
  expect(JSON.parse(String(fetch.mock.calls[1][1]?.body))).toEqual({ grunnlagsmerke: GODKJENNING_JONAS.grunnlagsmerke });
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

test("endret grunnlag hentes på nytt og krever nytt trykk", async () => {
  const oppdatert = { ...GODKJENNING_JONAS, grunnlagsmerke: "b".repeat(64), kandidat: { ...GODKJENNING_JONAS.kandidat, navn: "Jonas Oppdatert" } };
  const fetch = falskFetch({
    [URL]: [ok(GODKJENNING_JONAS), ok(oppdatert)],
    [`POST ${URL}`]: [feil(409, "endret_grunnlag"), ok({ status: "godkjent" })],
  });
  const onGodkjent = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={onGodkjent} />);
  const bruker = userEvent.setup();
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByRole("heading", { name: "Jonas Oppdatert" })).toBeTruthy();
  expect(screen.getByRole("status").textContent).toBe(t.endret);
  expect(onGodkjent).not.toHaveBeenCalled();
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(onGodkjent).toHaveBeenCalledTimes(1);
  expect(JSON.parse(String(fetch.mock.calls[3][1]?.body))).toEqual({ grunnlagsmerke: oppdatert.grunnlagsmerke });
});

test("ugyldig kandidat etter POST gir nøytral melding uten ny bekreftelse", async () => {
  const { onGodkjent, bruker } = rendreMed(ok(GODKJENNING_JONAS), feil(409, "ugyldig_kandidat"));
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByRole("heading", { name: t.ikkeFunnet })).toBeTruthy();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();
  expect(onGodkjent).not.toHaveBeenCalled();
});

test("datafeil etter POST stopper godkjenning og viser datagrensen", async () => {
  const { onGodkjent, bruker } = rendreMed(ok(GODKJENNING_JONAS), ok(GODKJENNING_DATAFEIL));
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));

  const varsel = await screen.findByRole("alert");
  expect(within(varsel).getByText(t.datafeil)).toBeTruthy();
  expect(within(varsel).getByText(t.datagrense(datoOgKlokke(GODKJENNING_DATAFEIL.datagrense)))).toBeTruthy();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();
  expect(onGodkjent).not.toHaveBeenCalled();
});

test("sent POST-svar for forrige kandidat kan ikke navigere fra nytt valg", async () => {
  let svarPaGammeltPost: ((svar: Response) => void) | undefined;
  const mette = {
    ...GODKJENNING_JONAS,
    kandidat: { id: 5, navn: "Mette Solberg", kompetansenivå: 4 },
    grunnlagsmerke: "b".repeat(64),
  };
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input) === URL && init?.method === "POST") {
      return new Promise<Response>((resolve) => { svarPaGammeltPost = resolve; });
    }
    if (String(input) === URL) return Promise.resolve(json(GODKJENNING_JONAS));
    if (String(input) === "/api/vakter/4127/kandidater/5") return Promise.resolve(json(mette));
    throw new Error(`Uventet kall: ${String(input)}`);
  }));
  const onGodkjent = vi.fn();
  const onTilbake = vi.fn();
  const bruker = userEvent.setup();
  const { rerender } = render(
    <Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} onGodkjent={onGodkjent} />,
  );
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(svarPaGammeltPost).toBeDefined();

  rerender(<Godkjenningsflate vaktnummer={4127} ansattId={5} onTilbake={onTilbake} onGodkjent={onGodkjent} />);
  expect(await screen.findByRole("heading", { name: "Mette Solberg" })).toBeTruthy();
  await act(async () => { svarPaGammeltPost!(json({ status: "godkjent" })); });
  expect(onGodkjent).not.toHaveBeenCalled();
  expect(screen.getByRole("heading", { name: "Mette Solberg" })).toBeTruthy();
});

test("usikkert POST-svar krever kontroll i Vaktvalg før nytt forsøk", async () => {
  const onTilOversikt = vi.fn();
  const fetch = falskFetch({ [URL]: ok(GODKJENNING_JONAS), [`POST ${URL}`]: feil(500, "intern_feil") });
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={vi.fn()} onTilOversikt={onTilOversikt} />);
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await userEvent.setup().click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByText(t.usikkert)).toBeTruthy();
  expect((screen.getByRole("button", { name: t.godkjenn }) as HTMLButtonElement).disabled).toBe(true);
  expect(fetch).toHaveBeenCalledTimes(2);
  await userEvent.setup().click(screen.getByRole("button", { name: t.tilVaktvalg }));
  expect(onTilOversikt).toHaveBeenCalledTimes(1);
});

test("sent POST-svar fra gammel sesjon gir ingen suksessnavigasjon", async () => {
  let fullfor: ((svar: Response) => void) | undefined;
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input) === URL && init?.method === "POST") return new Promise<Response>((resolve) => { fullfor = resolve; });
    return Promise.resolve(json(GODKJENNING_JONAS));
  }));
  const onGodkjent = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={onGodkjent} />);
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await userEvent.setup().click(screen.getByRole("button", { name: t.godkjenn }));
  nySesjonsgenerasjon();
  await act(async () => { fullfor!(json({ status: "godkjent" })); });
  expect(onGodkjent).not.toHaveBeenCalled();
});

test("raske gjentatte trykk sender bare ett POST-kall", async () => {
  let fullfor: ((svar: Response) => void) | undefined;
  const fetch = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input) === URL && init?.method === "POST") return new Promise<Response>((resolve) => { fullfor = resolve; });
    return Promise.resolve(json(GODKJENNING_JONAS));
  });
  vi.stubGlobal("fetch", fetch);
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={vi.fn()} />);
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  const knapp = screen.getByRole("button", { name: t.godkjenn });
  fireEvent.click(knapp);
  fireEvent.click(knapp);
  expect(fetch.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  await act(async () => { fullfor!(json({ status: "godkjent" })); });
});
