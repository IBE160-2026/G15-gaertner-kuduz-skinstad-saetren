// Kandidatflate med Kandidatliste, Rangeringstabell og EkskludertBoks (story 2.1, 2.4,
// 2.5, 3.1, 4.4 og 4.6). De er interne og testes gjennom Kandidatflate.
import { describe, expect, test, vi } from "vitest";
import { act, cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Kandidatflate, { Kandidatliste } from "../../src/komponenter/Kandidatflate";
import { datoOgKlokke } from "../../src/format";
import { ekskludertBoksTekst, ekskludertRadTekst } from "../../src/kandidater";
import { INGEN_KONTAKT, RESERVETEKST, TEKSTER, feiltekst } from "../../src/tekster";
import type { Kandidatsvar, RangertKandidat } from "../../src/api";
import {
  INGEN_GYLDIGE, KANDIDATER_DATAFEIL, OK_MED_TOM_LISTE, TO_GYLDIGE, TO_UTELUKKET, VAKT_4127,
  falskFetch, feil, kallTil, malRegex, ok, rangering, regexTekst, type Svar,
} from "./hjelpere";

const t = TEKSTER.kandidatflate;
const g = TEKSTER.godkjenning;
const ek = TEKSTER.ekskludertBoks;
const VAKT_URL = "/api/vakter/4127";
const KANDIDATER_URL = "/api/vakter/4127/kandidater";

/** Rendrer flaten for vakt #4127 og venter til kandidatdelen har fått svar. */
async function rendreMed(kandidater: Svar | Svar[], onVelg = vi.fn()) {
  const fetch = falskFetch({ [VAKT_URL]: ok(VAKT_4127), [KANDIDATER_URL]: kandidater });
  const bruker = userEvent.setup();
  render(<Kandidatflate vaktnummer={4127} onVelg={onVelg} />);
  const del = await screen.findByRole("region", { name: t.kandidaterOverskrift });
  // Vent til «Henter kandidatene …» er borte.
  await vi.waitFor(() => expect(within(del).queryByText(t.kandidaterLaster)).toBeNull());
  return { fetch, bruker, del, onVelg };
}

// Navnene bygges av tekstmalene i TEKSTER, ikke skrevet på nytt her.
const VELG = malRegex(g.velgEtikett("¤"), "¤");
const UTELUKKET = malRegex(ek.totaltUtelukket(999999), 999999);
// Pilen ligger i et aria-hidden-span, så knappens navn er teksten alene, men
// textContent har pilen med. Derfor bare begynnelsen.
const begynnerMed = (tekst: string) => new RegExp(`^${regexTekst(tekst)}`);

// Timerkolonnen (4.1) er testens tema; ulempen (4.7) er påkrevd av typen, men uten betydning her.
const INGEN_ULEMPE = TO_GYLDIGE.kandidater[1].ulempebelastning;

/** Kandidat slik backend sender den: prosent uavrundet, høy-flagget fra 1944 minutter (story 4.2). */
const kandidat = (id: number, navn: string, minutter: number) => ({
  id, navn, kompetansenivå: 3, minutter_i_uka: minutter,
  timebelastning_prosent: (100 * minutter) / 2160, hoy_belastning: minutter >= 1944,
  ulempebelastning: INGEN_ULEMPE,
  // Kostnaden (4.3) er påkrevd av typen; ordinær som standard, så den ikke gir varselmerke.
  kostnad: TO_GYLDIGE.kandidater[1].kostnad,
  // Rangeringen (4.4) er påkrevd av typen; plassen er id-en, som bare vises.
  ...rangering(id),
});

/** Raden i rangeringstabellen for kandidaten med dette navnet. */
const radFor = (del: HTMLElement, navn: string) =>
  within(del).getByText(navn, { selector: ".ansattnavn" }).closest("tr")!;

const velgknapper = () => screen.queryAllByRole("button", { name: VELG });

test("vaktbytte nullstiller pågående forsøk", async () => {
  const first = TO_GYLDIGE.kandidater[0];
  const failed = { ...first, tolkestatus: "kunne_ikke_tolkes" as const, preferansekategori: null };
  const gammelPost = `${KANDIDATER_URL}/${first.id}/preferanse`;
  const nyListe = "/api/vakter/4189/kandidater";
  const nyPost = `${nyListe}/${first.id}/preferanse`;
  const fetch = falskFetch({
    [KANDIDATER_URL]: ok({ ...TO_GYLDIGE, kandidater: [failed] }),
    [nyListe]: ok({ ...TO_GYLDIGE, kandidater: [failed] }),
    [`POST ${nyPost}`]: ok({ status: "feilet" }),
  });
  let svar!: (response: Response) => void;
  const ventende = new Promise<Response>((resolve) => { svar = resolve; });
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) =>
    String(input) === gammelPost ? ventende : fetch(input, init));
  const bruker = userEvent.setup();
  const visning = render(<Kandidatliste vaktnummer={4127} onVelg={vi.fn()} />);
  await bruker.click(await screen.findByRole("button", { name: t.provPreferanse(first.navn) }));
  expect(screen.getByRole("button", { name: g.velgEtikett(first.navn) })).toHaveProperty("disabled", true);
  visning.rerender(<Kandidatliste vaktnummer={4189} onVelg={vi.fn()} />);
  await vi.waitFor(() => expect(kallTil(fetch, nyListe)).toBe(1));
  const knapp = await screen.findByRole("button", { name: t.provPreferanse(first.navn) });
  expect(knapp).toHaveProperty("disabled", false);
  expect(screen.getByRole("button", { name: g.velgEtikett(first.navn) })).toHaveProperty("disabled", false);
  await bruker.click(knapp);
  expect(await screen.findByText(t.tolkefeil)).toBeTruthy();
  await act(async () => { svar(new Response(JSON.stringify({ status: "tolket" }), { status: 200 })); });
  expect(screen.getByText(t.tolkefeil)).toBeTruthy();
  expect(kallTil(fetch, `POST ${nyPost}`)).toBe(1);
});

test("nettverksfeil etter forsøk krever oppdatert rangering før valg", async () => {
  const first = TO_GYLDIGE.kandidater[0];
  const failed = { ...first, tolkestatus: "kunne_ikke_tolkes" as const, preferansekategori: null };
  const interpreted = { ...first, tolkestatus: "tolket" as const, preferansekategori: "onsker_flere", preferansepoeng: 100 };
  const sti = `${KANDIDATER_URL}/${first.id}/preferanse`;
  const fetch = falskFetch({ [KANDIDATER_URL]: [
    ok({ ...TO_GYLDIGE, kandidater: [failed] }),
    ok({ ...TO_GYLDIGE, kandidater: [interpreted] }),
  ] });
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) =>
    String(input) === sti ? Promise.reject(new Error("network")) : fetch(input, init));
  const bruker = userEvent.setup();
  render(<Kandidatliste vaktnummer={4127} onVelg={vi.fn()} />);
  await bruker.click(await screen.findByRole("button", { name: t.provPreferanse(first.navn) }));
  expect(await screen.findByText(INGEN_KONTAKT)).toBeTruthy();
  expect(screen.queryByRole("button", { name: g.velgEtikett(first.navn) })).toBeNull();
  await bruker.click(screen.getByRole("button", { name: TEKSTER.provIgjen }));
  expect(await screen.findByText(t.preferansekategorier.onsker_flere)).toBeTruthy();
  expect(screen.getByRole("button", { name: g.velgEtikett(first.navn) })).toHaveProperty("disabled", false);
  expect(kallTil(fetch, KANDIDATER_URL)).toBe(2);
});

describe("Kandidatliste (story 2.1)", () => {
  test("kostnad og satsfordeling vises på riktig kandidat", async () => {
    const grunnlag = TO_GYLDIGE.kandidater[0];
    const svar = { ...TO_GYLDIGE, kandidater: [
      { ...grunnlag, id: 1, navn: "Ordinær", kostnad: { total: 2400, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 300, overtidssats: 450 } },
      { ...grunnlag, id: 2, navn: "Blandet", kostnad: { total: 3000, ordinære_timer: 4, overtidstimer: 4, ordinær_sats: 300, overtidssats: 450 } },
      { ...grunnlag, id: 3, navn: "Overtid", kostnad: { total: 3600, ordinære_timer: 0, overtidstimer: 8, ordinær_sats: 300, overtidssats: 450 } },
    ] } satisfies Kandidatsvar;
    const { del } = await rendreMed(ok(svar));
    const rad = (navn: string) => radFor(del, navn);
    const format = (n: number) => new Intl.NumberFormat("nb-NO", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n).replace(/\s/g, " ");
    expect(within(rad("Ordinær")).getByText(`${t.kostnadOverskrift}: ${format(2400)} kr`)).toBeTruthy();
    expect(within(rad("Ordinær")).getByText(t.kostnadOrdinaer, { selector: ".kostnad-ordinaer" })).toBeTruthy();
    expect(within(rad("Blandet")).getByText(t.kostnadOvertid)).toBeTruthy();
    expect(within(rad("Overtid")).getByText(t.kostnadOvertid)).toBeTruthy();
    expect(within(rad("Blandet")).getByText(`${t.kostnadOrdinaer}: ${t.kostnadDetalj("4:00", format(300))}`)).toBeTruthy();
    expect(within(rad("Blandet")).getByText(`${t.kostnadOvertidDel}: ${t.kostnadDetalj("4:00", format(450))}`)).toBeTruthy();
    expect(within(rad("Overtid")).getByText(`${t.kostnadOvertidDel}: ${t.kostnadDetalj("8:00", format(450))}`)).toBeTruthy();
    expect(within(rad("Overtid")).queryByText(/^Ordinær:/)).toBeNull();
  });

  test("ett minutt vises med minuttpresisjon", async () => {
    const kandidat = { ...TO_GYLDIGE.kandidater[0], kostnad: { total: 5, ordinære_timer: 1 / 60, overtidstimer: 0, ordinær_sats: 300, overtidssats: 450 } };
    const { del } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater: [kandidat] }));
    expect(within(del).getByText(`${t.kostnadOrdinaer}: ${t.kostnadDetalj("0:01", "300,00")}`)).toBeTruthy();
  });

  test("varighet med sekunder merkes som avrundet", async () => {
    const kandidat = { ...TO_GYLDIGE.kandidater[0], kostnad: { total: 7.5, ordinære_timer: 1.5 / 60, overtidstimer: 0, ordinær_sats: 300, overtidssats: 450 } };
    const { del } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater: [kandidat] }));
    expect(within(del).getByText(`${t.kostnadOrdinaer}: ${t.kostnadDetalj("ca. 0:02", "300,00")}`)).toBeTruthy();
  });
  test("hver rad viser timer i uka som t:mm, og 0:00 uten vakter (story 4.1)", async () => {
    const svar = {
      ...TO_GYLDIGE,
      kandidater: [
        kandidat(4, "Ingrid Dahl", 1920),
        kandidat(5, "Mette Solberg", 0),
        kandidat(6, "Jonas Bakke", 32 * 60 + 23),
        kandidat(7, "Ola Nord", 61),
      ],
    } satisfies Kandidatsvar;
    const { del } = await rendreMed(ok(svar));

    for (const [navn, verdi, opplest] of [
      ["Ingrid Dahl", "32:00", "32 timer og 0 minutter i uka"],
      ["Mette Solberg", "0:00", "0 timer og 0 minutter i uka"],
      ["Jonas Bakke", "32:23", "32 timer og 23 minutter i uka"],
      ["Ola Nord", "1:01", "1 time og 1 minutt i uka"],
    ]) {
      const rad = within(del).getByText(navn).closest("tr");
      expect(rad).not.toBeNull();
      const synlig = within(rad!).getByText(t.timerIUka(verdi));
      expect(synlig.getAttribute("aria-hidden")).toBe("true");
      expect(within(rad!).getByText(opplest).classList.contains("visuelt-skjult")).toBe(true);
    }
  });

  test("feil gir «Prøv igjen», og et trykk henter kandidatene på nytt", async () => {
    const { fetch, bruker, del } = await rendreMed([feil(500, "intern_feil"), ok(TO_GYLDIGE)]);

    const varsel = within(del).getByRole("alert");
    expect(within(varsel).getByText(feiltekst("intern_feil"))).toBeTruthy();
    expect(velgknapper()).toHaveLength(0);

    await bruker.click(within(varsel).getByRole("button", { name: TEKSTER.provIgjen }));

    expect(await screen.findByRole("button", { name: g.velgEtikett("Jonas Bakke") })).toBeTruthy();
    expect(within(del).queryByRole("alert")).toBeNull();
    expect(kallTil(fetch, KANDIDATER_URL)).toBe(2);
    // Bare listen hentes på nytt, ikke vakten.
    expect(kallTil(fetch, VAKT_URL)).toBe(1);
  });

  test("datafeil viser tekst og datagrense, uten liste", async () => {
    const { del } = await rendreMed(ok(KANDIDATER_DATAFEIL));
    const { datagrense } = KANDIDATER_DATAFEIL;

    const varsel = within(del).getByRole("alert");
    expect(within(varsel).getByText(t.datafeil)).toBeTruthy();
    expect(within(varsel).getByText(t.datagrense(datoOgKlokke(datagrense)))).toBeTruthy();
    expect(within(del).queryByRole("table")).toBeNull();
    expect(velgknapper()).toHaveLength(0);
    expect(within(del).queryByRole("button")).toBeNull();
  });
});

test("viser hver kandidats ulempepoeng og fordeling, også null (story 4.7)", async () => {
  const { del } = await rendreMed(ok(TO_GYLDIGE));
  expect(within(del).getByText(TEKSTER.kandidatflate.ulempePeriode)).toBeTruthy();
  const jonas = radFor(del, "Jonas Bakke");
  const mette = radFor(del, "Mette Solberg");

  // Kolonneoverskriften er «Ulempe» (4.4); cellen har bare poengene.
  // Jonas' tall er #4127s fasit uten lagrede tolkninger (story 4.5, AV-07).
  expect(within(jonas).getByText("40,0 p")).toBeTruthy();
  expect(within(jonas).getByText("Kveld 4,0 t · helg 15,0 t · natt 2,0 t")).toBeTruthy();
  expect(within(mette).getByText("0,0 p")).toBeTruthy();
  expect(within(mette).getByText("Kveld 0,0 t · helg 0,0 t · natt 0,0 t")).toBeTruthy();
});

test("belastningslinja er accent under 32,4 t og warn på og over, kuttet ved 100 % (story 4.2)", async () => {
  const svar = {
    ...TO_GYLDIGE,
    kandidater: [
      kandidat(4, "Ingrid Dahl", 1920),
      kandidat(5, "Mette Solberg", 0),
      kandidat(6, "Jonas Bakke", 32 * 60 + 23),
      kandidat(7, "Ola Nord", 32 * 60 + 24),
      kandidat(8, "Per Vik", 32 * 60 + 25),
      kandidat(9, "Eva Lund", 40 * 60),
    ],
  } satisfies Kandidatsvar;
  const { bruker, del } = await rendreMed(ok(svar));
  // Seks kandidater: den sjette vises først etter «Vis alle gyldige kandidater» (story 4.4).
  await bruker.click(within(del).getByRole("button", { name: t.visAlle }));

  for (const [navn, høy, bredde] of [
    ["Ingrid Dahl", false, "88.8888"],
    ["Mette Solberg", false, "0%"],
    ["Jonas Bakke", false, "89.9537"],
    ["Ola Nord", true, "90%"],
    ["Per Vik", true, "90.0462"],
    ["Eva Lund", true, "100%"],
  ] as const) {
    const rad = radFor(del, navn);
    const fyll = rad.querySelector(".belastningsfyll") as HTMLElement;
    expect(fyll.classList.contains("hoy")).toBe(høy);
    expect(fyll.style.width.startsWith(bredde)).toBe(true);
    expect(rad.querySelector(".belastningslinje")!.getAttribute("aria-hidden")).toBe("true");
    expect(within(rad).queryByText(t.hoyBelastning) !== null).toBe(høy);
    if (høy) {
      const tekst = within(rad).getByText(t.hoyBelastning);
      expect(tekst.classList.contains("visuelt-skjult")).toBe(false);
      expect(tekst.closest('[aria-hidden="true"]')).toBeNull();
      const merke = tekst.closest(".varselmerke");
      expect(merke).not.toBeNull();
      expect(merke!.querySelector("svg")?.getAttribute("aria-hidden")).toBe("true");
    }
    // 4.1-verdien og ulempeblokken er uendret.
    expect(within(rad).getByText(/ t i uka$/)).toBeTruthy();
    expect(rad.querySelector(".kandidat-ulempe")?.textContent).toMatch(/^\d+,\d p/);
  }
});

test("høy belastning og overtid vises som hvert sitt varselmerke, alene og samtidig (4.2 + 4.3)", async () => {
  const ordinær = { total: 2400, ordinære_timer: 8, overtidstimer: 0, ordinær_sats: 300, overtidssats: 450 };
  const overtid = { total: 3000, ordinære_timer: 4, overtidstimer: 4, ordinær_sats: 300, overtidssats: 450 };
  // Høy belastning uten overtid finnes i virkeligheten for en nattevakt over ukeskiftet
  // (1 t i startuka); overtid uten høy belastning er Ingrid på #4127 (32 t + 8 t).
  const svar = {
    ...TO_GYLDIGE,
    kandidater: [
      { ...kandidat(1, "Ingen varsler", 0), kostnad: ordinær },
      { ...kandidat(2, "Bare høy belastning", 33 * 60), kostnad: ordinær },
      { ...kandidat(3, "Bare overtid", 32 * 60), kostnad: overtid },
      { ...kandidat(4, "Begge varsler", 33 * 60), kostnad: overtid },
    ],
  } satisfies Kandidatsvar;
  const { del } = await rendreMed(ok(svar));

  for (const [navn, forventet] of [
    ["Ingen varsler", []],
    ["Bare høy belastning", [t.hoyBelastning]],
    ["Bare overtid", [t.kostnadOvertid]],
    // Kostnad står før timebelastning i rangeringstabellen (story 4.4).
    ["Begge varsler", [t.kostnadOvertid, t.hoyBelastning]],
  ] as const) {
    const rad = radFor(del, navn);
    const merker = [...rad.querySelectorAll(".varselmerke")];
    expect(merker.map((m) => m.textContent)).toEqual(forventet);
    // Samme komponent: begge varslene har det samme skjulte ikonet.
    for (const merke of merker) expect(merke.querySelector("svg")?.getAttribute("aria-hidden")).toBe("true");
    // «Ordinær» vises bare når kostnaden ikke har overtid.
    const harOvertid = forventet.some((v) => v === t.kostnadOvertid);
    expect(within(rad).queryByText(t.kostnadOrdinaer, { selector: ".kostnad-ordinaer" }) === null).toBe(harOvertid);
  }
});

describe("Tomtilstanden (story 2.6)", () => {
  test("viser full tekst, ikon, boks og innleietekst uten knapp utenom «Vis full liste»", async () => {
    const { del } = await rendreMed(ok(INGEN_GYLDIGE));

    expect(within(del).getByRole("status").textContent).toContain(t.ingenGyldige);
    expect(t.ingenGyldige).toContain("Dette er ikke en feil eller en lastefeil");
    const ikon = del.querySelector(".alert-icon");
    expect(ikon?.textContent).toBe("!");
    expect(ikon?.getAttribute("aria-hidden")).toBe("true");
    expect(within(del).getByText(ekskludertBoksTekst(INGEN_GYLDIGE.utelukkelser))).toBeTruthy();
    expect(within(del).getByText(/^24 utelukket/)).toBeTruthy();
    expect(within(del).getByText(t.innleie)).toBeTruthy();
    expect(within(del).queryByRole("link")).toBeNull();
    const knapper = within(del).getAllByRole("button");
    expect(knapper).toHaveLength(1);
    expect(knapper[0].textContent).toMatch(begynnerMed(ek.visFullListe));
    expect(velgknapper()).toHaveLength(0);
  });

  test("`ok` med tom liste er kontraktsbrudd og gir feiltilstand med «Prøv igjen»", async () => {
    const { del } = await rendreMed(ok(OK_MED_TOM_LISTE));

    const varsel = within(del).getByRole("alert");
    expect(within(varsel).getByText(RESERVETEKST)).toBeTruthy();
    expect(within(varsel).getByRole("button", { name: TEKSTER.provIgjen })).toBeTruthy();
    expect(within(del).queryByText(t.ingenGyldige)).toBeNull();
    expect(within(del).queryByText(t.innleie)).toBeNull();
  });

  test("laster, feil, datafeil og ingen gyldige er fire ulike tilstander", async () => {
    // Lasting hentes mens svaret ikke er kommet; de tre andre etter svar.
    const laster = falskFetch({ [VAKT_URL]: ok(VAKT_4127), [KANDIDATER_URL]: { status: 200, kropp: null } });
    laster.mockImplementation((input) => String(input).endsWith("/kandidater")
      ? new Promise<Response>(() => {})
      : Promise.resolve(new Response(JSON.stringify(VAKT_4127), { status: 200, headers: { "Content-Type": "application/json" } })));
    render(<Kandidatflate vaktnummer={4127} onVelg={vi.fn()} />);
    const lasterDel = await screen.findByRole("region", { name: t.kandidaterOverskrift });
    const laster_ = beskriv(lasterDel);
    cleanup();

    const tilstander = [laster_];
    for (const svar of [feil(500, "intern_feil"), ok(KANDIDATER_DATAFEIL), ok(INGEN_GYLDIGE)]) {
      const { del } = await rendreMed(svar);
      tilstander.push(beskriv(del));
      cleanup();
    }

    const [lasterT, feilT, datafeilT, ingenT] = tilstander;
    expect(lasterT).toMatchObject({ rolle: "status", ikon: false, knapp: false });
    expect(feilT).toMatchObject({ rolle: "alert", ikon: false, knapp: true });
    expect(datafeilT).toMatchObject({ rolle: "alert", ikon: false, knapp: false });
    expect(ingenT).toMatchObject({ rolle: "status", ikon: true, knapp: true });
    for (const felt of ["tekst", "klasse"] as const) {
      expect(new Set(tilstander.map((s) => s[felt])).size).toBe(4);
    }
    expect(new Set(tilstander.map((s) => `${s.rolle}|${s.ikon}|${s.knapp}`)).size).toBe(4);
    expect(datafeilT.klasse).toContain("datafeil");
    expect(ingenT.klasse).not.toContain("datafeil");
  });
});

/** Tekst, panelklasse og kombinasjonen av rolle, ikon og knapp for én kandidatdel. */
function beskriv(del: HTMLElement) {
  const status = del.querySelector('[role="status"]');
  const alert = del.querySelector('[role="alert"]');
  return {
    tekst: (status ?? alert)?.textContent ?? "",
    klasse: del.className,
    rolle: status ? "status" : alert ? "alert" : "ingen",
    ikon: del.querySelector(".alert-icon") !== null,
    knapp: del.querySelector("button") !== null,
  };
}

describe("Ekskludert-boksen (story 2.5)", () => {
  test("vises ikke når ingen er utelukket", async () => {
    const { del } = await rendreMed(ok(TO_GYLDIGE));

    expect(within(del).getAllByRole("button", { name: VELG })).toHaveLength(2);
    expect(within(del).queryByText(UTELUKKET)).toBeNull();
    expect(within(del).queryByRole("button", { name: begynnerMed(ek.visFullListe) })).toBeNull();
  });

  test("«Vis full liste» er lukket, åpen og lukket igjen, med aria-expanded", async () => {
    const svar: Kandidatsvar = { ...TO_GYLDIGE, utelukkelser: TO_UTELUKKET };
    const { bruker, del } = await rendreMed(ok(svar));
    const rader = TO_UTELUKKET.utelukkede.map(ekskludertRadTekst);

    expect(within(del).getByText(ekskludertBoksTekst(TO_UTELUKKET))).toBeTruthy();
    const knapp = within(del).getByRole("button", { name: begynnerMed(ek.visFullListe) });
    expect(knapp.getAttribute("aria-expanded")).toBe("false");
    expect(within(del).queryByText(rader[0])).toBeNull();

    await bruker.click(knapp);
    expect(knapp.getAttribute("aria-expanded")).toBe("true");
    expect(knapp.textContent).toMatch(begynnerMed(ek.skjulFullListe));
    for (const rad of rader) expect(within(del).getByText(rad)).toBeTruthy();

    await bruker.click(knapp);
    expect(knapp.getAttribute("aria-expanded")).toBe("false");
    expect(knapp.textContent).toMatch(begynnerMed(ek.visFullListe));
    expect(within(del).queryByText(rader[0])).toBeNull();
  });
});

test("«Velg» sender vaktnummer og id for riktig kandidat (story 3.1)", async () => {
  const { bruker, fetch, onVelg } = await rendreMed(ok(TO_GYLDIGE));
  const kallFoer = fetch.mock.calls.length;

  await bruker.click(screen.getByRole("button", { name: g.velgEtikett("Jonas Bakke") }));

  expect(onVelg).toHaveBeenCalledTimes(1);
  expect(onVelg).toHaveBeenCalledWith(4127, 6);
  // Valget er bare navigasjon (story 3.1): ingen kall til API-et.
  expect(fetch.mock.calls.length).toBe(kallFoer);
});

describe("Rangeringstabellen (story 4.4)", () => {
  const k = t.kolonner;
  const tabell = (del: HTMLElement) => within(del).getByRole("table");
  /** Datarader i tabellen, uten overskriftsraden. */
  const datarader = (del: HTMLElement) => within(tabell(del)).getAllByRole("row").slice(1);
  const navnIRad = (rad: HTMLElement) => rad.querySelector(".ansattnavn")?.textContent;

  /** Kandidater i rangert rekkefølge med plass 1, 2, … og synkende totalscore. */
  const rangerte = (antall: number): RangertKandidat[] =>
    Array.from({ length: antall }, (_, i) => ({ ...kandidat(100 + i, `Kandidat ${i + 1}`, 600), plass: i + 1, totalscore: 90 - i * 7.25 }));

  test("kolonnene, plassen, kandidaten med meta og taggene står i raden uten klikk", async () => {
    const svar = {
      ...TO_GYLDIGE,
      kandidater: [
        { ...TO_GYLDIGE.kandidater[0], stilling: "Sykepleier", ansiennitet: 3, totalscore: 85.654761904761905,
          preferansepoeng: 75, tolkestatus: "tolket", preferansekategori: "positiv_ved_behov" },
        { ...TO_GYLDIGE.kandidater[1], stilling: "Spesialsykepleier", ansiennitet: 12, totalscore: 78.65,
          tolkestatus: "kunne_ikke_tolkes" },
        { ...kandidat(7, "Ola Nord", 0), plass: 3, totalscore: 59.05, tolkestatus: "venter_paa_tolkning" },
        { ...kandidat(8, "Per Vik", 0), plass: 4, totalscore: 37, tolkestatus: "ingen_registrert" },
      ],
    } satisfies Kandidatsvar;
    const { del } = await rendreMed(ok(svar));

    expect(within(tabell(del)).getAllByRole("columnheader").map((h) => h.textContent)).toEqual(
      [k.plass, k.kandidat, k.kompetanse, k.kostnad, k.timebelastning, k.ulempe, k.preferanse, k.handling]);
    // Den alfabetiske listen fra 2.1 er erstattet.
    expect(within(del).queryByRole("list")).toBeNull();
    const rader = datarader(del);
    expect(rader.map(navnIRad)).toEqual(["Jonas Bakke", "Mette Solberg", "Ola Nord", "Per Vik"]);
    expect(rader.map((r) => r.querySelector(".rank-badge")?.textContent)).toEqual(["1", "2", "3", "4"]);
    // Annenhver rad har row-alt (UX-DR7).
    expect(rader.map((r) => r.classList.contains("row-alt"))).toEqual([false, true, false, true]);

    const [jonas, mette, ola, per] = rader;
    // Totalscore avrundes til én desimal bare ved visning (K-03).
    expect(within(jonas).getByText(t.totalscore("85,7"))).toBeTruthy();
    expect(within(ola).getByText(t.totalscore("59,1"))).toBeTruthy();
    expect(within(jonas).getByText(t.kandidatMeta("Sykepleier", 3))).toBeTruthy();
    expect(within(mette).getByText(t.kandidatMeta("Spesialsykepleier", 12))).toBeTruthy();
    expect(within(jonas).getByText(t.nivaaTag(3), { selector: ".tag" })).toBeTruthy();
    expect(within(mette).getByText(t.nivaaTag(4), { selector: ".tag" })).toBeTruthy();
    // Preferansetaggen viser kategori eller status (UX-DR11, P-05), med poengene under.
    expect(within(jonas).getByText(t.preferansekategorier.positiv_ved_behov, { selector: ".tag" })).toBeTruthy();
    expect(within(jonas).getByText(t.preferansePoeng("75,0"))).toBeTruthy();
    expect(within(mette).getByText(t.tolkestatuser.kunne_ikke_tolkes, { selector: ".tag" })).toBeTruthy();
    expect(within(ola).getByText(t.tolkestatuser.venter_paa_tolkning, { selector: ".tag" })).toBeTruthy();
    expect(within(per).getByText(t.tolkestatuser.ingen_registrert, { selector: ".tag" })).toBeTruthy();
    expect(within(per).getByText(t.preferansePoeng("50,0"))).toBeTruthy();
    // Kostnad, timebelastning og ulempe står i raden, og Velg i siste kolonne.
    for (const rad of rader) {
      const celler = within(rad).getAllByRole("cell");
      expect(celler).toHaveLength(8);
      expect(within(celler[3]).getByText(/^Kostnad: /)).toBeTruthy();
      expect(within(celler[4]).getByText(/ t i uka$/)).toBeTruthy();
      expect(celler[4].querySelector(".belastningslinje")).not.toBeNull();
      expect(within(celler[5]).getByText(/^\d+,\d p$/)).toBeTruthy();
      expect(within(celler[7]).getByRole("button", { name: VELG })).toBeTruthy();
    }
    // Tabellen ruller i egen beholder, som kan nås med tastatur (AV-14).
    const beholder = within(del).getByRole("region", { name: t.rangeringstabell });
    expect(beholder.classList.contains("tabellbeholder")).toBe(true);
    expect(beholder.getAttribute("tabindex")).toBe("0");
  });

  test("viser de fem øverste, og «Vis alle» viser resten i rangert rekkefølge med fokus", async () => {
    const kandidater = rangerte(7);
    const { bruker, del, onVelg } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater }));

    expect(datarader(del).map(navnIRad)).toEqual(kandidater.slice(0, 5).map((k) => k.navn));
    expect(within(del).getByText(t.viserAv(5, 7))).toBeTruthy();
    const visAlle = within(del).getByRole("button", { name: t.visAlle });

    await bruker.click(visAlle);

    expect(datarader(del).map(navnIRad)).toEqual(kandidater.map((k) => k.navn));
    expect(within(del).queryByRole("button", { name: t.visAlle })).toBeNull();
    expect(within(del).queryByText(t.viserAv(5, 7))).toBeNull();
    expect(within(del).getByText(t.viserAlle(7))).toBeTruthy();
    expect(within(del).getByRole("button", { name: t.visFærre(5) }).getAttribute("aria-expanded")).toBe("true");
    // Fokus flyttes til den første nye raden, så tastaturet fortsetter der.
    expect(document.activeElement).toBe(screen.getByRole("button", { name: g.velgEtikett("Kandidat 6") }));
    expect(datarader(del)[5].classList.contains("row-alt")).toBe(true);

    // Velg virker for hver av dem, også de som var skjult.
    for (const kandidat of kandidater) {
      await bruker.click(screen.getByRole("button", { name: g.velgEtikett(kandidat.navn) }));
      expect(onVelg).toHaveBeenLastCalledWith(4127, kandidat.id);
    }
    expect(onVelg).toHaveBeenCalledTimes(7);
  });

  test("«Vis bare de 5 øverste» lukker listen igjen, med fokus på knappen", async () => {
    const kandidater = rangerte(7);
    const { bruker, del } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater }));
    expect(within(del).getByRole("button", { name: t.visAlle }).getAttribute("aria-expanded")).toBe("false");

    await bruker.click(within(del).getByRole("button", { name: t.visAlle }));
    const visFærre = within(del).getByRole("button", { name: t.visFærre(5) });
    await bruker.click(visFærre);

    expect(datarader(del).map(navnIRad)).toEqual(kandidater.slice(0, 5).map((k) => k.navn));
    expect(within(del).getByText(t.viserAv(5, 7))).toBeTruthy();
    const visAlle = within(del).getByRole("button", { name: t.visAlle });
    expect(visAlle.getAttribute("aria-expanded")).toBe("false");
    // Samme knapp, så fokus forsvinner ikke med radene som skjules.
    expect(document.activeElement).toBe(visAlle);

    // Kan åpnes igjen, og fokus flyttes til den første nye raden som før.
    await bruker.keyboard("{Enter}");
    expect(datarader(del)).toHaveLength(7);
    expect(document.activeElement).toBe(screen.getByRole("button", { name: g.velgEtikett("Kandidat 6") }));
  });

  test("«Vis alle» kan brukes med tastaturet alene", async () => {
    const { bruker, del } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater: rangerte(6) }));
    within(del).getByRole("button", { name: t.visAlle }).focus();
    await bruker.keyboard("{Enter}");
    expect(datarader(del)).toHaveLength(6);
    expect(document.activeElement).toBe(screen.getByRole("button", { name: g.velgEtikett("Kandidat 6") }));
  });

  test("fem eller færre gyldige vises alle, uten «Vis alle»", async () => {
    for (const antall of [1, 5]) {
      const { del } = await rendreMed(ok({ ...TO_GYLDIGE, kandidater: rangerte(antall) }));
      expect(datarader(del)).toHaveLength(antall);
      expect(within(del).queryByRole("button", { name: t.visAlle })).toBeNull();
      expect(within(del).queryByText(/^Viser /)).toBeNull();
      cleanup();
    }
  });

  test("ingen tabell ved datafeil eller null gyldige (P-08, P-11)", async () => {
    for (const svar of [ok(KANDIDATER_DATAFEIL), ok(INGEN_GYLDIGE)]) {
      const { del } = await rendreMed(svar);
      expect(within(del).queryByRole("table")).toBeNull();
      expect(within(del).queryByRole("region", { name: t.rangeringstabell })).toBeNull();
      cleanup();
    }
  });
});

describe("Smale nettleservinduer (story 4.6)", () => {
  // jsdom gjør ingen layout, så de faste kolonnene kontrolleres i nettleseren
  // (docs/testing.md). Her vokter testen mot breddestyrt rendering: en endret
  // vindusbredde skal ikke montere tabellen på nytt eller hente noe (AV-17).
  const datarader = (del: HTMLElement) => within(within(del).getByRole("table")).getAllByRole("row").slice(1);
  const sju = Array.from({ length: 7 }, (_, i) => ({ ...kandidat(100 + i, `Kandidat ${i + 1}`, 600), plass: i + 1 }));

  test("«Vis alle» og «Vis full liste» er fortsatt åpne etter endret vindusbredde, uten ny henting", async () => {
    const opprinnelig = window.innerWidth;
    const settBredde = (bredde: number) => act(() => {
      Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: bredde });
      window.dispatchEvent(new Event("resize"));
    });
    try {
      settBredde(1600);
      const svar: Kandidatsvar = { ...TO_GYLDIGE, kandidater: sju, utelukkelser: TO_UTELUKKET };
      const { bruker, del, fetch } = await rendreMed(ok(svar));
      await bruker.click(within(del).getByRole("button", { name: t.visAlle }));
      await bruker.click(within(del).getByRole("button", { name: begynnerMed(ek.visFullListe) }));

      for (const bredde of [680, 1600]) {
        settBredde(bredde);
        expect(within(del).getByRole("button", { name: t.visFærre(5) }).getAttribute("aria-expanded")).toBe("true");
        expect(datarader(del).map((r) => r.querySelector(".ansattnavn")?.textContent)).toEqual(sju.map((k) => k.navn));
        expect(within(del).getByRole("button", { name: begynnerMed(ek.skjulFullListe) }).getAttribute("aria-expanded")).toBe("true");
        for (const rad of TO_UTELUKKET.utelukkede.map(ekskludertRadTekst)) expect(within(del).getByText(rad)).toBeTruthy();
      }
      // Kandidatene og vakten er hentet én gang, før bredden ble endret.
      expect(kallTil(fetch, KANDIDATER_URL)).toBe(1);
      expect(kallTil(fetch, VAKT_URL)).toBe(1);
    } finally {
      Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: opprinnelig });
    }
  });
});

test("retry updates the whole ranking after interpretation", async () => {
  const first = TO_GYLDIGE.kandidater[0];
  const second = TO_GYLDIGE.kandidater[1];
  const failed = { ...first, plass: 2, tolkestatus: "kunne_ikke_tolkes" as const, preferansekategori: null };
  const interpreted = { ...first, plass: 1, tolkestatus: "tolket" as const, preferansekategori: "onsker_flere", preferansepoeng: 100 };
  const sti = `${KANDIDATER_URL}/${first.id}/preferanse`;
  const fetch = falskFetch({
    [VAKT_URL]: ok(VAKT_4127),
    [KANDIDATER_URL]: [ok({ ...TO_GYLDIGE, kandidater: [{ ...second, plass: 1 }, failed] }),
      ok({ ...TO_GYLDIGE, kandidater: [interpreted, { ...second, plass: 2 }] })],
  });
  let svar!: (response: Response) => void;
  const ventende = new Promise<Response>((resolve) => { svar = resolve; });
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) =>
    String(input) === sti ? ventende : fetch(input, init));
  const bruker = userEvent.setup();
  render(<><button type="button">Annet sted</button><Kandidatflate vaktnummer={4127} onVelg={vi.fn()} /></>);
  await screen.findByRole("button", { name: t.provPreferanse(first.navn) });
  const navn = () => [...document.querySelectorAll(".rangeringstabell tbody .ansattnavn")].map((rad) => rad.textContent);
  expect(navn()).toEqual([second.navn, first.navn]);
  await bruker.click(await screen.findByRole("button", { name: t.provPreferanse(first.navn) }));
  const annet = screen.getByRole("button", { name: "Annet sted" });
  annet.focus();
  await act(async () => { svar(new Response(JSON.stringify({ status: "tolket" }), { status: 200 })); });
  expect(await screen.findByText(t.tolket)).toBeTruthy();
  expect(screen.getByText(t.preferansekategorier.onsker_flere)).toBeTruthy();
  expect(navn()).toEqual([first.navn, second.navn]);
  expect(document.activeElement).toBe(annet);
  expect(kallTil(fetch, KANDIDATER_URL)).toBe(2);
});


test("retry failure leaves the candidate available for another attempt", async () => {
  const first = TO_GYLDIGE.kandidater[0];
  const failed = { ...first, tolkestatus: "kunne_ikke_tolkes" as const, preferansekategori: null };
  const sti = `${KANDIDATER_URL}/${first.id}/preferanse`;
  falskFetch({
    [VAKT_URL]: ok(VAKT_4127),
    [KANDIDATER_URL]: ok({ ...TO_GYLDIGE, kandidater: [failed] }),
    [`POST ${sti}`]: ok({ status: "feilet" }),
  });
  const bruker = userEvent.setup();
  render(<Kandidatflate vaktnummer={4127} onVelg={vi.fn()} />);
  await bruker.click(await screen.findByRole("button", { name: t.provPreferanse(first.navn) }));
  expect(await screen.findByText(t.tolkefeil)).toBeTruthy();
  expect(screen.getByRole("button", { name: t.provPreferanse(first.navn) })).toBeTruthy();
});


test("retry focus and late response after changing shifts", async () => {
  const first = TO_GYLDIGE.kandidater[0];
  const failed = { ...first, tolkestatus: "kunne_ikke_tolkes" as const, preferansekategori: null };
  const sti = `${KANDIDATER_URL}/${first.id}/preferanse`;
  const nyVakt = "/api/vakter/4189";
  const fetch = falskFetch({
    [VAKT_URL]: ok(VAKT_4127),
    [KANDIDATER_URL]: ok({ ...TO_GYLDIGE, kandidater: [failed] }),
    [nyVakt]: ok({ ...VAKT_4127, vaktnummer: 4189 }),
    [`${nyVakt}/kandidater`]: ok(TO_GYLDIGE),
  });
  let svar!: (response: Response) => void;
  const ventende = new Promise<Response>((resolve) => { svar = resolve; });
  vi.stubGlobal("fetch", (input: RequestInfo | URL, init?: RequestInit) =>
    String(input) === sti ? ventende : fetch(input, init));
  const bruker = userEvent.setup();
  const visning = render(<Kandidatflate vaktnummer={4127} onVelg={vi.fn()} />);
  await bruker.click(await screen.findByRole("button", { name: t.provPreferanse(first.navn) }));
  const status = screen.getByText(t.tolker);
  expect(document.activeElement).toBe(status);
  expect(screen.getByRole("button", { name: g.velgEtikett(first.navn) })).toHaveProperty("disabled", true);
  visning.rerender(<Kandidatflate vaktnummer={4189} onVelg={vi.fn()} />);
  await screen.findByRole("heading", { name: t.overskrift(4189) });
  await act(async () => { svar(new Response(JSON.stringify({ status: "tolket" }), { status: 200 })); });
  expect(screen.queryByText(t.tolket)).toBeNull();
  expect(kallTil(fetch, KANDIDATER_URL)).toBe(1);
});
