import { StrictMode } from "react";
import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import { nySesjonsgenerasjon, type RangertKandidat } from "../../src/api";
import App from "../../src/App";
import { Kandidatliste } from "../../src/komponenter/Kandidatflate";
import Godkjenningsflate from "../../src/komponenter/Godkjenningsflate";
import { kandidatsti } from "../../src/navigasjon";
import { TEKSTER } from "../../src/tekster";
import { GODKJENNING_JONAS, JONAS, MEG, METTE, TO_GYLDIGE, VAKT_4127, VAKTOVERSIKT, falskFetch, feil, json, kallTil, ok, type FalskFetch } from "./hjelpere";

const t = TEKSTER.kandidatflate.avveining;
const g = TEKSTER.godkjenning;
const liste = "/api/vakter/4127/kandidater";
const grunnlag = `${liste}/${JONAS.id}`;
const forklaring = (r: RangertKandidat) => `${liste}/${r.id}/avveining`;
const modell = "test/modell";

function live(r: RangertKandidat, tekst: string) {
  return { status: "ok", ki_kilde: "live", modell, vaktnummer: 4127, kandidat_id: r.id,
    grunnlagsmerke: r.grunnlagsmerke, paastander: [tekst] };
}

function godkjenning() {
  return <Godkjenningsflate vaktnummer={4127} ansattId={JONAS.id} onGodkjent={vi.fn()} onTilbake={vi.fn()} onTilOversikt={vi.fn()} />;
}

/** Hold igjen akkurat det første svaret fra en rute, slik at neste visning kan fullføres først. */
function forsinkFørste(fetch: FalskFetch, sti: string) {
  let send!: (svar: Response) => void;
  let tatt = false;
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input) === sti && !tatt) {
      tatt = true;
      return new Promise<Response>((resolve) => { send = resolve; });
    }
    return fetch(input, init);
  });
  return async (svar: object) => act(async () => { send(json(svar)); });
}

test("åpner nr. 1 én gang, og hver rad kan vises og skjules uavhengig med tastatur", async () => {
  const mette = { ...METTE, faktorpoeng: { ...METTE.faktorpoeng, kostnad: 84.375 }, totalscore: 72.25 };
  const tredje = { ...mette, id: 27, navn: "Sara Vik", plass: 3, grunnlagsmerke: "e".repeat(64) };
  const fetch = falskFetch({
    [liste]: ok({ ...TO_GYLDIGE, kandidater: [JONAS, mette, tredje] }),
    [forklaring(JONAS)]: ok(live(JONAS, "Godkjent forklaring for Jonas.")),
    [forklaring(METTE)]: ok(live(JONAS, "Feil kandidat.")),
  });
  render(<StrictMode><Kandidatliste vaktnummer={4127} onVelg={vi.fn()} /></StrictMode>);
  await screen.findByText("Godkjent forklaring for Jonas.");
  expect(kallTil(fetch, forklaring(JONAS))).toBe(1);
  expect(kallTil(fetch, forklaring(METTE))).toBe(0);
  const bruker = userEvent.setup();
  const andre = screen.getByRole("button", { name: t.visEtikett(METTE.navn), expanded: false });
  const siste = screen.getByRole("button", { name: t.visEtikett(tredje.navn), expanded: false });
  expect(andre.textContent).toBe(t.vis);
  andre.focus();
  await bruker.keyboard("{Enter}");
  const panel = screen.getByRole("region", { name: t.tittel(METTE.navn) });
  expect(await within(panel).findByText(t.reserve)).toBeTruthy();
  expect(within(panel).getByText(t.kvalifisert)).toBeTruthy();
  expect(within(panel).getByText(t.sammenligning("72,3"))).toBeTruthy();
  expect(within(panel).getByText(/Preferanse venter på tolkning · 50,0 poeng/)).toBeTruthy();
  expect(within(panel).getByText(/180 ulempepoeng · Kveld 0 t · helg 90 t · natt 0 t/)).toBeTruthy();
  for (const [faktor, forventet] of [
    [t.kostnad, `${t.opp} · 84,4 kostnadspoeng`],
    [t.timebelastning, `${t.opp} · 100,0 timebelastningspoeng`],
    [t.ulempe, `${t.ned} · 40,0 i ulempescore`],
    [t.preferanse, `${t.ned} · 50,0 preferansepoeng`],
  ]) {
    const term = within(panel).getByText(faktor, { selector: "dt" });
    expect(term.nextElementSibling?.textContent).toContain(forventet);
  }
  expect(screen.queryByText("Feil kandidat.")).toBeNull();
  expect(screen.getAllByText(t.kilde(modell))).toHaveLength(1);
  expect(screen.getByRole("button", { name: g.velgEtikett(METTE.navn) })).toHaveProperty("disabled", false);
  await bruker.keyboard("{Enter}{Enter}");
  expect(kallTil(fetch, forklaring(METTE))).toBe(1);
  expect(screen.getByRole("button", { name: t.skjulEtikett(METTE.navn), expanded: true })).toBe(andre);
  expect(andre.textContent).toBe(t.skjul);
  expect(screen.getByRole("button", { name: t.skjulEtikett(JONAS.navn), expanded: true })).toBeTruthy();
  expect(siste.getAttribute("aria-expanded")).toBe("false");
  expect(kallTil(fetch, forklaring(tredje))).toBe(0);
});

test("ny preferansetolkning bytter nr. 1 og forkaster ventende tekst fra tidligere rangering", async () => {
  const feilet = { ...METTE, tolkestatus: "kunne_ikke_tolkes" };
  const ny = { ...METTE, plass: 1, grunnlagsmerke: "c".repeat(64), tolkestatus: "tolket" as const,
    preferansekategori: "onsker_flere", preferansepoeng: 100 };
  const fetch = falskFetch({
    [liste]: [ok({ ...TO_GYLDIGE, kandidater: [JONAS, feilet] }),
      ok({ ...TO_GYLDIGE, kandidater: [ny, { ...JONAS, plass: 2, grunnlagsmerke: "d".repeat(64) }] })],
    [`POST ${liste}/${METTE.id}/preferanse`]: ok({ status: "tolket" }),
    [forklaring(ny)]: ok(live(ny, "Forklaringen bruker den nye tolkningen.")),
  });
  const fullfør = forsinkFørste(fetch, forklaring(JONAS));
  render(<Kandidatliste vaktnummer={4127} onVelg={vi.fn()} />);
  await screen.findByText(t.laster);
  await userEvent.setup().click(screen.getByRole("button", { name: TEKSTER.kandidatflate.provPreferanse(METTE.navn) }));
  await screen.findByText("Forklaringen bruker den nye tolkningen.");
  await fullfør(live(JONAS, "Gammelt svar for forrige rangering."));
  expect(screen.queryByText("Gammelt svar for forrige rangering.")).toBeNull();
  const panel = screen.getByRole("region", { name: t.tittel(METTE.navn) });
  expect(within(panel).getByText(/Ønsker flere vakter · 100,0 poeng/)).toBeTruthy();
  expect(screen.getAllByText(t.kilde(modell))).toHaveLength(1);
});

test("én forklaring feiler, den andre lykkes og kandidaten med reservetekst kan godkjennes", async () => {
  window.history.replaceState(null, "", kandidatsti(4127));
  const reserve = { status: "avveining_feilet", vaktnummer: 4127, kandidat_id: JONAS.id, grunnlagsmerke: JONAS.grunnlagsmerke };
  const tekst = "Ulempescoren er lavere enn hos Jonas Bakke før avrunding (40,0 mot 86,7).";
  const fetch = falskFetch({
    "/api/meg": ok(MEG), "/api/vakter/4127": ok(VAKT_4127),
    [liste]: ok({ ...TO_GYLDIGE, kandidater: [JONAS, METTE] }),
    [forklaring(JONAS)]: ok(reserve), [forklaring(METTE)]: ok(live(METTE, tekst)),
    [grunnlag]: ok(GODKJENNING_JONAS), [`POST ${grunnlag}`]: ok({ status: "godkjent" }),
    "/api/vaktoversikt": ok(VAKTOVERSIKT),
  });
  const fullfør = forsinkFørste(fetch, forklaring(JONAS));
  render(<App />);
  await screen.findByText(t.laster);
  const jonas = within(screen.getByRole("region", { name: t.tittel(JONAS.navn) }));
  const statusfelt = jonas.getByRole("status");
  expect(statusfelt.getAttribute("aria-live")).toBe("polite");
  expect(statusfelt.textContent).toBe("");
  expect(screen.queryByText(t.reservetekst)).toBeNull();
  expect(screen.queryByText(t.reserve)).toBeNull();

  const bruker = userEvent.setup();
  await bruker.click(screen.getByRole("button", { name: t.visEtikett(METTE.navn) }));
  expect(await screen.findByText(tekst)).toBeTruthy();
  await fullfør(reserve);
  expect(within(screen.getByRole("region", { name: t.tittel(JONAS.navn) })).getByRole("status")).toBe(statusfelt);
  expect(within(statusfelt).getByText(t.reservetekst)).toBeTruthy();

  async function kontrollerReserve() {
    const panel = within(await screen.findByRole("region", { name: t.tittel(JONAS.navn) }));
    const reservetekst = await panel.findByText(t.reservetekst);
    expect(panel.getByRole("status").contains(reservetekst)).toBe(true);
    expect(panel.getByText(t.reserve).closest("[aria-live], [role=status]")).toBeNull();
    expect(panel.queryByText(t.laster)).toBeNull();
    expect(panel.queryByText(t.kilde(modell))).toBeNull();
    expect(panel.queryByText(tekst)).toBeNull();
    for (const [faktor, verdi] of [
      [t.kostnad, /2\s?960,00/],
      [t.timebelastning, /16:00 t:min i uka \(44,4 %\)/],
      [t.ulempe, /40 ulempepoeng · Kveld 4 t · helg 15 t · natt 2 t/],
      [t.preferanse, /Preferanse venter på tolkning · 50,0 poeng/],
    ] as const) {
      const etikett = panel.getByText(faktor, { selector: "dt" });
      expect(reservetekst.compareDocumentPosition(etikett) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
      expect(etikett.nextElementSibling?.textContent).toMatch(verdi);
    }
  }
  await kontrollerReserve();
  const mette = within(screen.getByRole("region", { name: t.tittel(METTE.navn) }));
  expect(mette.getByText(t.kilde(modell))).toBeTruthy();
  expect(mette.getByText(tekst)).toBeTruthy();
  expect(mette.queryByText(t.reservetekst)).toBeNull();
  expect(mette.queryByText(t.reserve)).toBeNull();
  await bruker.click(screen.getByRole("button", { name: g.velgEtikett(JONAS.navn) }));
  await kontrollerReserve();
  await bruker.click(screen.getByRole("button", { name: g.godkjenn }));
  expect(await screen.findByText(TEKSTER.vaktvalg.godkjent(JONAS.navn, 4127))).toBeTruthy();
  const poster = fetch.mock.calls.filter(([sti, init]) => String(sti) === grunnlag && init?.method === "POST");
  expect(poster.map(([, init]) => JSON.parse(String(init?.body)))).toEqual([{ grunnlagsmerke: JONAS.grunnlagsmerke }]);
});

test("409 henter nytt grunnlag og ny avveining, og neste POST bruker nettopp dette merket", async () => {
  const merke = "f".repeat(64);
  const ny = { ...JONAS, grunnlagsmerke: merke };
  const fetch = falskFetch({
    [grunnlag]: [ok(GODKJENNING_JONAS), ok({ ...GODKJENNING_JONAS, kandidat: ny, grunnlagsmerke: merke })],
    [`POST ${grunnlag}`]: [feil(409, "endret_grunnlag"), ok({ status: "godkjent" })],
    [forklaring(ny)]: ok(live(ny, "Ny avveining for Jonas.")),
  });
  const fullfør = forsinkFørste(fetch, forklaring(JONAS));
  render(godkjenning());
  await screen.findByText(t.laster);
  const bruker = userEvent.setup();
  await bruker.click(screen.getByRole("button", { name: g.godkjenn }));
  await screen.findByText("Ny avveining for Jonas.");
  await fullfør(live(JONAS, "Den gamle avveiningen."));
  expect(screen.queryByText("Den gamle avveiningen.")).toBeNull();
  expect(screen.getByText(t.kilde(modell))).toBeTruthy();
  await bruker.click(screen.getByRole("button", { name: g.godkjenn }));
  const merker = fetch.mock.calls.filter(([, init]) => init?.method === "POST")
    .map(([, init]) => JSON.parse(String(init?.body)).grunnlagsmerke);
  expect(merker).toEqual([JONAS.grunnlagsmerke, merke]);
});

test.each([
  { kandidat_id: METTE.id }, { vaktnummer: 4189 }, { grunnlagsmerke: METTE.grunnlagsmerke },
  { ki_kilde: "forhandsgenerert" }, { paastander: [] },
])("godkjenning forkaster svar med feil identitet, kilde eller innhold (%o)", async (avvik) => {
  falskFetch({
    [grunnlag]: ok(GODKJENNING_JONAS),
    [forklaring(JONAS)]: ok({ ...live(JONAS, "Skal forkastes."), ...avvik }),
  });
  render(godkjenning());
  await screen.findByText(t.reserve);
  expect(screen.queryByText("Skal forkastes.")).toBeNull();
  expect(screen.queryByText(t.kilde(modell))).toBeNull();
  expect(screen.getByRole("button", { name: g.godkjenn })).toHaveProperty("disabled", false);
});

test("forsinket svar etter sesjonsbytte vises aldri", async () => {
  const fetch = falskFetch({ [grunnlag]: ok(GODKJENNING_JONAS) });
  const fullfør = forsinkFørste(fetch, forklaring(JONAS));
  render(godkjenning());
  await screen.findByText(t.laster);
  nySesjonsgenerasjon();
  await fullfør(live(JONAS, "Svar fra gammel sesjon."));
  expect(screen.queryByText("Svar fra gammel sesjon.")).toBeNull();
});
