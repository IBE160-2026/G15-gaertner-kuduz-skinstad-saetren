// Godkjenningsflaten (story 3.2): aktiv bekreftelse og feilhåndtering.
import { expect, test, vi } from "vitest";
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { nySesjonsgenerasjon } from "../../src/api";
import userEvent from "@testing-library/user-event";
import Godkjenningsflate from "../../src/komponenter/Godkjenningsflate";
import { datoOgKlokke } from "../../src/format";
import { kandidatsti } from "../../src/navigasjon";
import { FEILTEKSTER, TEKSTER } from "../../src/tekster";
import { GODKJENNING_DATAFEIL, GODKJENNING_JONAS, GODKJENNING_METTE, falskFetchMedReserve as falskFetch, feil, json, kallTil, ok, type Svar } from "./hjelpere";

const t = TEKSTER.godkjenning;
const URL = "/api/vakter/4127/kandidater/6";

function rendreMed(svar: Svar, post?: Svar) {
  const fetch = falskFetch({ [URL]: svar, ...(post ? { [`POST ${URL}`]: post } : {}) });
  const onTilbake = vi.fn();
  const onGodkjent = vi.fn();
  const onTilOversikt = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} onGodkjent={onGodkjent} onTilOversikt={onTilOversikt} />);
  return { fetch, onTilbake, onGodkjent, onTilOversikt, bruker: userEvent.setup() };
}

test("«Godkjenn erstatning» sender merket og navigerer bare etter suksess", async () => {
  const { fetch, onTilbake, onGodkjent, bruker } = rendreMed(ok(GODKJENNING_JONAS), ok({ status: "godkjent" }));

  expect(await screen.findByRole("heading", { name: "Jonas Bakke" })).toBeTruthy();
  expect(kallTil(fetch, URL)).toBe(1);
  expect(String(fetch.mock.calls[0][0])).toBe(URL);
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(onGodkjent).toHaveBeenCalledTimes(1);
  expect(onTilbake).not.toHaveBeenCalled();
  expect(kallTil(fetch, `POST ${URL}`)).toBe(1);
  expect(fetch.mock.calls.filter(([, init]) => init?.method === "POST")[0][1]?.method).toBe("POST");
  expect(JSON.parse(String(fetch.mock.calls.filter(([, init]) => init?.method === "POST")[0][1]?.body))).toEqual({ grunnlagsmerke: GODKJENNING_JONAS.grunnlagsmerke });
});

// --- Nøkkeltall og avviksnotat (story 4.5, FR12, UX-DR18, UX-DR23) ---------------

test("kandidatkortet viser tilgjengelig timetall og ulempe for topprangert kandidat, uten avviksnotat", async () => {
  rendreMed(ok(GODKJENNING_JONAS));
  const kort = await screen.findByRole("region", { name: "Jonas Bakke" });

  expect(within(kort).getByText("16:00 t i uka")).toBeTruthy();
  expect(within(kort).getByText("16 timer og 0 minutter i uka")).toBeTruthy();
  expect(within(kort).getByText(t.ulempe, { selector: "p" })).toBeTruthy();
  expect(within(kort).getByText("40,0 p")).toBeTruthy();
  expect(within(kort).getByText("Kveld 4,0 t · helg 15,0 t · natt 2,0 t")).toBeTruthy();
  // Jonas er topprangert selv (plass 1): ingen avviksnotat (`topprangert` er null).
  expect(screen.queryByText(t.avviksnotat.overskrift)).toBeNull();
});

test("høy belastning gir tekstvarsel på kandidatkortet", async () => {
  const svar = { ...GODKJENNING_JONAS, kandidat: { ...GODKJENNING_JONAS.kandidat, hoy_belastning: true, timebelastning_prosent: 90 } };
  rendreMed(ok(svar));
  const kort = await screen.findByRole("region", { name: "Jonas Bakke" });

  expect(within(kort).getByText(TEKSTER.kandidatflate.hoyBelastning)).toBeTruthy();
});

test("avviksnotatet viser kostnad, nivå, timebelastning og ulempe for Mette og Jonas side om side, uten å blokkere godkjenning", async () => {
  const url = "/api/vakter/4127/kandidater/5";
  // Mette får høy belastning her, så testen også dekker at varselteksten vises
  // skilt per kandidatgruppe (bare hos Mette, ikke hos Jonas).
  const svar = {
    ...GODKJENNING_METTE,
    kandidat: {
      ...GODKJENNING_METTE.kandidat, minutter_i_uka: 1950, hoy_belastning: true,
      timebelastning_prosent: 100 * 1950 / 2160,
      kostnad: { total: 3200, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 400, overtidssats: 600 },
    },
  };
  falskFetch({ [url]: ok(svar) });
  render(<Godkjenningsflate vaktnummer={4127} ansattId={5} onTilbake={vi.fn()} onGodkjent={vi.fn()} onTilOversikt={vi.fn()} />);
  await screen.findByRole("heading", { name: "Mette Solberg" });

  expect(screen.getByText(t.avviksnotat.overskrift)).toBeTruthy();
  expect(screen.getByText(`${t.avviksnotat.innledning("Jonas Bakke")} ${t.avviksnotat.anbefaling}`)).toBeTruthy();

  const mette = screen.getByText("Mette Solberg", { selector: ".avviksnotat-navn" }).closest(".avviksnotat-kandidat") as HTMLElement;
  const jonas = screen.getByText("Jonas Bakke", { selector: ".avviksnotat-navn" }).closest(".avviksnotat-kandidat") as HTMLElement;

  expect(within(mette).getByText(/Kostnad: 3\s200,00 kr/)).toBeTruthy();
  expect(within(mette).getByText(t.nivaaTag(4))).toBeTruthy();
  expect(within(mette).getByText("32:30 t i uka")).toBeTruthy();
  expect(within(mette).getByText(t.ulempe)).toBeTruthy();
  expect(within(mette).getByText("180,0 p")).toBeTruthy();
  expect(within(mette).getByText("Kveld 0,0 t · helg 90,0 t · natt 0,0 t")).toBeTruthy();
  expect(within(mette).getByText(TEKSTER.kandidatflate.hoyBelastning)).toBeTruthy();

  expect(within(jonas).getByText(/Kostnad: 2\s960,00 kr/)).toBeTruthy();
  expect(within(jonas).getByText(t.nivaaTag(3))).toBeTruthy();
  expect(within(jonas).getByText("16:00 t i uka")).toBeTruthy();
  expect(within(jonas).getByText(t.ulempe)).toBeTruthy();
  expect(within(jonas).getByText("40,0 p")).toBeTruthy();
  expect(within(jonas).getByText("Kveld 4,0 t · helg 15,0 t · natt 2,0 t")).toBeTruthy();
  expect(within(jonas).queryByText(TEKSTER.kandidatflate.hoyBelastning)).toBeNull();

  // Avviksnotatet er bare informativt: godkjenningsknappen er fortsatt aktiv.
  expect((screen.getByRole("button", { name: t.godkjenn }) as HTMLButtonElement).disabled).toBe(false);
});

// --- Smale nettleservinduer (story 4.6, AV-17) -----------------------------------

test("valgt kandidat og avviksnotatet står etter endret vindusbredde, uten ny henting", async () => {
  // Layouten kontrolleres i nettleseren (docs/testing.md). Her: ingen tilstand
  // monteres på nytt og ingenting hentes når bredden endres.
  const url = "/api/vakter/4127/kandidater/5";
  const opprinnelig = window.innerWidth;
  const settBredde = (bredde: number) => act(() => {
    Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: bredde });
    window.dispatchEvent(new Event("resize"));
  });
  try {
    settBredde(1600);
    const fetch = falskFetch({ [url]: ok(GODKJENNING_METTE) });
    render(<Godkjenningsflate vaktnummer={4127} ansattId={5} onTilbake={vi.fn()} onGodkjent={vi.fn()} onTilOversikt={vi.fn()} />);
    await screen.findByRole("heading", { name: "Mette Solberg" });

    for (const bredde of [680, 1600]) {
      settBredde(bredde);
      const kort = screen.getByRole("region", { name: "Mette Solberg" });
      expect(within(kort).getByText("180,0 p")).toBeTruthy();
      expect(screen.getByRole("region", { name: t.avviksnotat.overskrift })).toBeTruthy();
      expect(screen.getByText("Jonas Bakke", { selector: ".avviksnotat-navn" })).toBeTruthy();
      expect((screen.getByRole("button", { name: t.godkjenn }) as HTMLButtonElement).disabled).toBe(false);
    }
    expect(kallTil(fetch, url)).toBe(1);
  } finally {
    Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: opprinnelig });
  }
});

test("endret grunnlag oppdaterer avviksnotatet (ny topprangert) og krever nytt trykk (P-09)", async () => {
  const url = "/api/vakter/4127/kandidater/5";
  const oppdatert = { ...GODKJENNING_METTE, kandidat: { ...GODKJENNING_METTE.kandidat, plass: 1 }, grunnlagsmerke: "c".repeat(64), topprangert: null };
  const fetch = falskFetch({
    [url]: [ok(GODKJENNING_METTE), ok(oppdatert)],
    [`POST ${url}`]: [feil(409, "endret_grunnlag"), ok({ status: "godkjent" })],
  });
  const onGodkjent = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={5} onTilbake={vi.fn()} onGodkjent={onGodkjent} onTilOversikt={vi.fn()} />);
  const bruker = userEvent.setup();
  await screen.findByRole("heading", { name: "Mette Solberg" });
  expect(screen.getByText(t.avviksnotat.overskrift)).toBeTruthy();

  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByText(t.endret)).toBeTruthy();
  // Nytt grunnlag: Mette er nå selv topprangert (plass 1), så notatet forsvinner.
  await vi.waitFor(() => expect(screen.queryByText(t.avviksnotat.overskrift)).toBeNull());
  expect(onGodkjent).not.toHaveBeenCalled();

  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(onGodkjent).toHaveBeenCalledTimes(1);
  expect(JSON.parse(String(fetch.mock.calls.filter(([, init]) => init?.method === "POST")[1][1]?.body))).toEqual({ grunnlagsmerke: oppdatert.grunnlagsmerke });
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
  const oppdatert = { ...GODKJENNING_JONAS, grunnlagsmerke: "b".repeat(64), kandidat: { ...GODKJENNING_JONAS.kandidat, navn: "Jonas Oppdatert", kostnad: { total: 3000, ordinære_timer: 4, overtidstimer: 4, ordinær_sats: 300, overtidssats: 450 } } };
  const fetch = falskFetch({
    [URL]: [ok(GODKJENNING_JONAS), ok(oppdatert)],
    [`POST ${URL}`]: [feil(409, "endret_grunnlag"), ok({ status: "godkjent" })],
  });
  const onGodkjent = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={onGodkjent} onTilOversikt={vi.fn()} />);
  const bruker = userEvent.setup();
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByRole("heading", { name: "Jonas Oppdatert" })).toBeTruthy();
  const kort = screen.getByRole("region", { name: "Jonas Oppdatert" });
  expect(within(kort).getByText(/Kostnad: 3\s000,00 kr/)).toBeTruthy();
  expect(within(kort).getByText(TEKSTER.kandidatflate.kostnadOvertid)).toBeTruthy();
  expect(within(kort).getByText("Ordinær: 4:00 t:min ved 300,00 kr/t")).toBeTruthy();
  expect(within(kort).getByText("Overtid: 4:00 t:min ved 450,00 kr/t")).toBeTruthy();
  const bekreftelse = screen.getByRole("region", { name: t.bekreftOverskrift });
  expect(within(bekreftelse).getByRole("status").textContent).toBe(t.endret);
  expect(onGodkjent).not.toHaveBeenCalled();
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(onGodkjent).toHaveBeenCalledTimes(1);
  expect(JSON.parse(String(fetch.mock.calls.filter(([, init]) => init?.method === "POST")[1][1]?.body))).toEqual({ grunnlagsmerke: oppdatert.grunnlagsmerke });
});

test("ugyldig kandidat etter POST gir nøytral melding uten ny bekreftelse", async () => {
  const { onGodkjent, bruker } = rendreMed(ok(GODKJENNING_JONAS), feil(409, "ugyldig_kandidat"));
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(await screen.findByRole("heading", { name: t.ikkeFunnet })).toBeTruthy();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();
  expect(onGodkjent).not.toHaveBeenCalled();
});

test("allerede bemannet etter POST gir bare vei til Vaktvalg, uten nytt forsøk", async () => {
  const { onGodkjent, onTilOversikt, fetch, bruker } = rendreMed(ok(GODKJENNING_JONAS), feil(409, "allerede_bemannet"));
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));

  const varsel = await screen.findByRole("alert");
  expect(within(varsel).getByRole("heading", { name: FEILTEKSTER.allerede_bemannet })).toBeTruthy();
  const tilVaktvalg = within(varsel).getByRole("button", { name: t.tilVaktvalg });
  expect(document.activeElement).toBe(tilVaktvalg);
  expect(screen.queryByRole("button", { name: TEKSTER.provIgjen })).toBeNull();
  expect(screen.queryByRole("button", { name: t.godkjenn })).toBeNull();

  await bruker.click(tilVaktvalg);
  expect(onTilOversikt).toHaveBeenCalledTimes(1);
  expect(onGodkjent).not.toHaveBeenCalled();
  expect(kallTil(fetch, `POST ${URL}`)).toBe(1);
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
    kandidat: { ...GODKJENNING_JONAS.kandidat, id: 5, navn: "Mette Solberg", kompetansenivå: 4, minutter_i_uka: 0 },
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
    <Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} onGodkjent={onGodkjent} onTilOversikt={vi.fn()} />,
  );
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  await bruker.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(svarPaGammeltPost).toBeDefined();

  rerender(<Godkjenningsflate vaktnummer={4127} ansattId={5} onTilbake={onTilbake} onGodkjent={onGodkjent} onTilOversikt={vi.fn()} />);
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
  expect(kallTil(fetch, `POST ${URL}`)).toBe(1);
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
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={onGodkjent} onTilOversikt={vi.fn()} />);
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
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={vi.fn()} onGodkjent={vi.fn()} onTilOversikt={vi.fn()} />);
  await screen.findByRole("heading", { name: "Jonas Bakke" });
  const knapp = screen.getByRole("button", { name: t.godkjenn });
  fireEvent.click(knapp);
  fireEvent.click(knapp);
  expect(fetch.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  await act(async () => { fullfor!(json({ status: "godkjent" })); });
});
