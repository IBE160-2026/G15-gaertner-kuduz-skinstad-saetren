// Godkjenningsflaten (story 3.1). Testene går mot den rene logikken i
// src/godkjenning.ts og src/navigasjon.ts med en falsk fetch, som
// kandidater.test.mjs. Komponenten testes i komponenter/godkjenningsflate.test.tsx.
import assert from "node:assert/strict";
import test, { afterEach } from "node:test";
import { fileURLToPath } from "node:url";
import { build } from "rolldown";

async function lastTs(sti) {
  const resultat = await build({ input: fileURLToPath(new URL(sti, import.meta.url)) });
  const js = resultat.output[0].code;
  return import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
}

const g = await lastTs("./godkjenning-bunt.ts");
const { TEKSTER, INGEN_KONTAKT, RESERVETEKST, FEILTEKSTER } = await lastTs("../src/tekster.ts");
const t = TEKSTER.godkjenning;

function json(kropp, status = 200) {
  return new Response(JSON.stringify(kropp), { status, headers: { "Content-Type": "application/json" } });
}

/** fetch som svarer først når testen sier fra, per URL. */
function styrtFetch() {
  const ventende = new Map();
  globalThis.fetch = (url) => new Promise((resolve) => ventende.set(String(url), resolve));
  return (url, respons) => {
    assert.ok(ventende.has(url), `ingen forespørsel til ${url}`);
    ventende.get(url)(respons);
  };
}

const NODE_FETCH = globalThis.fetch;
afterEach(() => { globalThis.fetch = NODE_FETCH; });

const nesteTick = () => new Promise((resolve) => setTimeout(resolve, 0));

const VAKT_4127 = {
  avdeling: "Kirurgisk sengepost", vaktnummer: 4127, vakttype: "dag",
  start: "2026-09-27T07:00:00+02:00", slutt: "2026-09-27T15:00:00+02:00", minstenivå: 3,
};
const JONAS = { status: "ok", vakt: VAKT_4127, kandidat: { id: 6, navn: "Jonas Bakke", kompetansenivå: 3 } };
const METTE = { status: "ok", vakt: VAKT_4127, kandidat: { id: 5, navn: "Mette Solberg", kompetansenivå: 4 } };
const DATAFEIL = { status: "datafeil", kode: "mangler_turnusgrunnlag", datagrense: "2026-10-05T00:00:00+02:00" };
const IKKE_FUNNET = { kode: "ikke_funnet", melding: "Fant ikke ressursen." };

// --- URL (beslutning 1A) --------------------------------------------------------

test("godkjenningsstien tolkes bare for positive heltall uten ledende null", () => {
  assert.deepEqual(g.godkjenningFraSti("/vakt/4127/godkjenning/6"), { vaktnummer: 4127, ansattId: 6 });
  assert.deepEqual(g.godkjenningFraSti("/vakt/4189/godkjenning/21"), { vaktnummer: 4189, ansattId: 21 });
  for (const sti of [
    "/vakt/4127/godkjenning", "/vakt/4127/godkjenning/", "/vakt/4127/godkjenning/6/",
    "/vakt/4127/godkjenning/0", "/vakt/0/godkjenning/6", "/vakt/4127/godkjenning/06",
    "/vakt/04127/godkjenning/6", "/vakt/4127/godkjenning/-1", "/vakt/4127/godkjenning/abc",
    "/vakt/4127/godkjenning/6.0", "/vakt/4127/godkjenning/9007199254740993",
    "/vakt/9007199254740993/godkjenning/6", "/vakt/4127/kandidater/6", "/vakt/4127/kandidater",
  ]) {
    assert.equal(g.godkjenningFraSti(sti), null, sti);
  }
});

test("stiene bygges og tolkes likt begge veier", () => {
  assert.equal(g.godkjenningssti(4127, 5), "/vakt/4127/godkjenning/5");
  assert.deepEqual(g.godkjenningFraSti(g.godkjenningssti(4127, 5)), { vaktnummer: 4127, ansattId: 5 });
  assert.equal(g.kandidatsti(4127), "/vakt/4127/kandidater");
  assert.equal(g.vaktnummerFraSti(g.kandidatsti(4127)), 4127);
  // Godkjenningsstien er ikke en kandidatsti, så bare én flate vises.
  assert.equal(g.vaktnummerFraSti("/vakt/4127/godkjenning/5"), null);
});

// --- Tilstand fra svar og feil ----------------------------------------------------

test("svar blir klar eller datafeil, og ukjent status blir feil, aldri bekreftelsesbilde", () => {
  assert.deepEqual(g.tilstandFraSvar(JONAS), { type: "klar", vakt: VAKT_4127, kandidat: JONAS.kandidat });
  assert.deepEqual(g.tilstandFraSvar(DATAFEIL), { type: "datafeil", datagrense: DATAFEIL.datagrense });
  assert.deepEqual(g.tilstandFraSvar({ status: "noe_nytt" }), { type: "feil", tekst: RESERVETEKST });
});

test("kallet går til endepunktet for vakten og den ansatte", async () => {
  const svar = styrtFetch();
  const meldt = [];
  g.lastGodkjenning(4127, 5, (tilstand) => meldt.push(tilstand));
  assert.deepEqual(meldt, [{ type: "laster" }]);
  svar("/api/vakter/4127/kandidater/5", json(METTE));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "klar", vakt: VAKT_4127, kandidat: METTE.kandidat });
});

test("404 blir ikke funnet, 401 viser ingenting, andre feil gir tekst fra tekstlista", async () => {
  const tilfeller = [
    [json(IKKE_FUNNET, 404), { type: "ikke_funnet" }],
    [json({ kode: "mangler_sesjon", melding: "Ingen gyldig sesjon." }, 401), { type: "avvist" }],
    [json({ kode: "intern_feil", melding: "Uventet feil på serveren." }, 500), { type: "feil", tekst: FEILTEKSTER.intern_feil }],
    [json({ kode: "ugyldig_foresporsel", melding: "x" }, 422), { type: "feil", tekst: FEILTEKSTER.ugyldig_foresporsel }],
    [new Response("<html>", { status: 502 }), { type: "feil", tekst: INGEN_KONTAKT }],
  ];
  for (const [respons, forventet] of tilfeller) {
    const svar = styrtFetch();
    const meldt = [];
    g.lastGodkjenning(4127, 6, (tilstand) => meldt.push(tilstand));
    svar("/api/vakter/4127/kandidater/6", respons);
    await nesteTick();
    assert.deepEqual(meldt.at(-1), forventet);
  }
  globalThis.fetch = () => Promise.reject(new TypeError("nett"));
  const meldt = [];
  g.lastGodkjenning(4127, 6, (tilstand) => meldt.push(tilstand));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "feil", tekst: INGEN_KONTAKT });
});

test("datafeil fra API-et blir datafeil, ikke bekreftelsesbilde", async () => {
  const svar = styrtFetch();
  const meldt = [];
  g.lastGodkjenning(4127, 6, (tilstand) => meldt.push(tilstand));
  svar("/api/vakter/4127/kandidater/6", json(DATAFEIL));
  await nesteTick();
  assert.deepEqual(meldt, [{ type: "laster" }, { type: "datafeil", datagrense: DATAFEIL.datagrense }]);
});

// --- Sene svar (P-09) -------------------------------------------------------------

test("forsinket svar for forrige kandidat erstatter ikke den aktive", async () => {
  const svar = styrtFetch();
  const meldt = [];
  const meld = (tilstand) => meldt.push(tilstand);

  const avbrytJonas = g.lastGodkjenning(4127, 6, meld);
  avbrytJonas(); // URL-en byttes: komponenten ryddes opp.
  g.lastGodkjenning(4127, 5, meld);

  svar("/api/vakter/4127/kandidater/5", json(METTE));
  await nesteTick();
  svar("/api/vakter/4127/kandidater/6", json(JONAS));
  await nesteTick();

  assert.deepEqual(meldt, [
    { type: "laster" }, { type: "laster" }, { type: "klar", vakt: VAKT_4127, kandidat: METTE.kandidat },
  ]);
});

test("forsinket feil for forrige URL meldes heller ikke", async () => {
  const svar = styrtFetch();
  const meldt = [];
  const avbryt = g.lastGodkjenning(4127, 6, (tilstand) => meldt.push(tilstand));
  avbryt();
  svar("/api/vakter/4127/kandidater/6", json(IKKE_FUNNET, 404));
  await nesteTick();
  assert.deepEqual(meldt, [{ type: "laster" }]);
});

test("svar fra en sesjon som er byttet ut, meldes ikke", async () => {
  const svar = styrtFetch();
  const meldt = [];
  g.lastGodkjenning(4127, 6, (tilstand) => meldt.push(tilstand));
  g.nySesjonsgenerasjon(); // Utlogging eller ny innlogging mens kallet pågår.
  svar("/api/vakter/4127/kandidater/6", json(JONAS));
  await nesteTick();
  assert.deepEqual(meldt, [{ type: "laster" }]);
});

// --- Tekster (UX-DR19, UX-DR23, beslutning 2A og 3A) -------------------------------

test("laster, feil, ikke funnet og datafeil har ulik tekst", () => {
  // To feilkoder deler tekst med vilje, så feiltekstene telles som én mengde.
  const feil = new Set([INGEN_KONTAKT, RESERVETEKST, ...Object.values(FEILTEKSTER)]);
  const egne = [t.laster, t.ikkeFunnet, t.datafeil];
  for (const tekst of egne) assert.ok(!feil.has(tekst), tekst);
  assert.equal(new Set(egne).size, egne.length);
  // Ikke samme tekst som kandidatlisten, så det er tydelig hvilken flate som feiler.
  assert.notEqual(t.datafeil, TEKSTER.kandidatflate.datafeil);
  assert.notEqual(t.laster, TEKSTER.kandidatflate.kandidaterLaster);
});

test("de faste tekstene fra spesifikasjonen", () => {
  assert.equal(t.statuslinje, "Ikke gjennomført — venter på eksplisitt godkjenning");
  assert.equal(t.ikkeLagret, "Godkjenningen lagres ikke ennå. Ingenting er endret.");
  assert.equal(t.ikkeFunnet, "Kandidaten kan ikke velges for denne vakten.");
  assert.equal(t.avbryt, "Avbryt");
  assert.equal(t.godkjenn, "Godkjenn erstatning");
  assert.equal(t.velg, "Velg");
  assert.equal(t.velgEtikett("Mette Solberg"), "Velg Mette Solberg");
  assert.equal(t.nivaaTag(4), "Nivå 4/4");
  assert.deepEqual(
    [TEKSTER.brodsmulesti.turnus, t.brodsmuleVakt(4127), t.brodsmuleKandidater, t.brodsmuleGodkjenning],
    ["Turnus", "Vakt #4127", "Kandidater", "Godkjenning"],
  );
});

test("bekreftelsen sier hvem som settes inn i hvilken vakt, nøytralt", () => {
  const b = t.bekreft;
  const setning = b.foer + "Mette Solberg" + b.inn + b.vakt(4127)
    + b.etter("Dagvakt", g.datoOgTidsrom(VAKT_4127.start, VAKT_4127.slutt)) + b.ingenEndring + t.godkjenn + b.slutt;
  assert.equal(
    setning,
    "Du er i ferd med å sette Mette Solberg inn i Vakt #4127 (Dagvakt, 27.09.2026, 07:00–15:00). "
      + "Ingen endring gjøres i turnusen før du trykker Godkjenn erstatning.",
  );
  // UX-DR23 og grensen mot 3.2: ingen utropstegn, ingen omtale av hvem som
  // byttes ut, og ingen registrering med navn.
  const alle = JSON.stringify(t, (_k, v) => (typeof v === "function" ? v(1, "x", "y") : v));
  assert.ok(!alle.includes("!"));
  for (const ord of ["i stedet for", "registreres", "Silje"]) assert.ok(!alle.includes(ord), ord);
});
