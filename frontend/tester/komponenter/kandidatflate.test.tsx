// Kandidatflate med Kandidatliste og EkskludertBoks (story 2.1, 2.4, 2.5 og 3.1).
// Kandidatliste og EkskludertBoks er interne og testes gjennom Kandidatflate.
import { describe, expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Kandidatflate from "../../src/komponenter/Kandidatflate";
import { datoOgKlokke } from "../../src/format";
import { ekskludertBoksTekst, ekskludertRadTekst } from "../../src/kandidater";
import { TEKSTER, feiltekst } from "../../src/tekster";
import type { Kandidatsvar } from "../../src/api";
import {
  INGEN_GYLDIGE, KANDIDATER_DATAFEIL, TO_GYLDIGE, TO_UTELUKKET, VAKT_4127,
  falskFetch, feil, kallTil, malRegex, ok, regexTekst, type Svar,
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

const velgknapper = () => screen.queryAllByRole("button", { name: VELG });

describe("Kandidatliste (story 2.1)", () => {
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
    expect(within(del).queryByRole("list")).toBeNull();
    expect(velgknapper()).toHaveLength(0);
    expect(within(del).queryByRole("button")).toBeNull();
  });
});

test("tom liste viser «ingen gyldige» og ingen «Velg»-knapp (story 2.4)", async () => {
  const { del } = await rendreMed(ok(INGEN_GYLDIGE));

  expect(within(del).getByRole("status").textContent).toBe(t.ingenGyldige);
  expect(velgknapper()).toHaveLength(0);
});

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
