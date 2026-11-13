// Tilstandene til kandidatlisten (story 2.1). Det finnes ingen komponenttestrigg,
// så testene går mot den rene logikken i src/kandidater.ts med en falsk fetch.
import assert from "node:assert/strict";
import test, { afterEach } from "node:test";
import { fileURLToPath } from "node:url";
import { build } from "rolldown";

async function lastTs(sti) {
  const resultat = await build({ input: fileURLToPath(new URL(sti, import.meta.url)) });
  const js = resultat.output[0].code;
  return import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
}

const k = await lastTs("./kandidater-bunt.ts");
const { TEKSTER, INGEN_KONTAKT, FEILTEKSTER } = await lastTs("../src/tekster.ts");
const t = TEKSTER.kandidatflate;

function json(kropp, status = 200) {
  return new Response(JSON.stringify(kropp), { status, headers: { "Content-Type": "application/json" } });
}

/** fetch som svarer først når testen sier fra, per URL. */
function styrtFetch() {
  const ventende = new Map();
  globalThis.fetch = (url) => new Promise((resolve) => ventende.set(String(url), resolve));
  return (url, respons) => ventende.get(url)(respons);
}

// Testene bytter ut fetch. Node sin egen settes tilbake etter hver test, også når
// testen feiler, så en fetch som aldri svarer ikke blir hengende igjen.
const NODE_FETCH = globalThis.fetch;
afterEach(() => { globalThis.fetch = NODE_FETCH; });

const nesteTick = () => new Promise((resolve) => setTimeout(resolve, 0));

const OK_4127 = { status: "ok", kandidater: [{ id: 11, navn: "Anders Strand", kompetansenivå: 3 }] };
const OK_4189 = { status: "ok", kandidater: [{ id: 4, navn: "Ingrid Dahl", kompetansenivå: 3 }] };
const DATAFEIL = { status: "datafeil", kode: "mangler_turnusgrunnlag", datagrense: "2026-10-05T00:00:00+02:00" };

test("svar blir klar, datafeil eller feil, aldri en tom liste ved ukjent status", () => {
  assert.deepEqual(k.tilstandFraSvar(OK_4127), { type: "klar", kandidater: OK_4127.kandidater });
  assert.deepEqual(k.tilstandFraSvar(DATAFEIL), { type: "datafeil", datagrense: DATAFEIL.datagrense });
  assert.equal(k.tilstandFraSvar({ status: "noe_nytt" }).type, "feil");
});

test("feil gir egen tekst fra tekstlista, og 401 viser ingenting", async () => {
  // Gjennom fetch, så ApiFeil kommer fra samme bunt som kandidater.ts.
  const tilfeller = [
    [json({ kode: "intern_feil", melding: "Uventet feil på serveren." }, 500), { type: "feil", tekst: FEILTEKSTER.intern_feil }],
    [json({ kode: "ikke_funnet", melding: "Fant ikke ressursen." }, 404), { type: "feil", tekst: FEILTEKSTER.ikke_funnet }],
    [json({ kode: "mangler_sesjon", melding: "Ingen gyldig sesjon." }, 401), { type: "avvist" }],
    [new Response("<html>", { status: 502 }), { type: "feil", tekst: INGEN_KONTAKT }],
  ];
  for (const [respons, forventet] of tilfeller) {
    const svar = styrtFetch();
    const meldt = [];
    k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
    svar("/api/vakter/4127/kandidater", respons);
    await nesteTick();
    assert.deepEqual(meldt.at(-1), forventet);
  }
  globalThis.fetch = () => Promise.reject(new TypeError("nett"));
  const meldt = [];
  k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "feil", tekst: INGEN_KONTAKT });
});

test("laster, feil, datafeil og tom liste har ulik tekst", () => {
  // To feilkoder deler tekst med vilje, så feiltekstene telles som én mengde.
  const feil = new Set([INGEN_KONTAKT, ...Object.values(FEILTEKSTER)]);
  const tilstander = [t.kandidaterLaster, t.datafeil, t.ingenGyldige];
  for (const tekst of tilstander) assert.ok(!feil.has(tekst), tekst);
  assert.equal(new Set(tilstander).size, tilstander.length);
  assert.equal(t.datafeil, "Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.");
  assert.equal(t.ingenGyldige, "Ingen gyldige kandidater for denne vakten.");
});

test("den midlertidige merknaden er fjernet (story 2.4)", async () => {
  assert.equal(t.midlertidigMerknad, undefined);
  const { readFile } = await import("node:fs/promises");
  const flate = await readFile(new URL("../src/komponenter/Kandidatflate.tsx", import.meta.url), "utf-8");
  assert.ok(!flate.includes("midlertidigMerknad"));
  assert.ok(flate.includes("t.ingenGyldige"));
});

test("tom liste fra API-et blir klar med tom liste, ikke datafeil", async () => {
  // Til story 2.6 svarer API-et status ok med tom liste når ingen er gyldige.
  const svar = styrtFetch();
  const meldt = [];
  k.lastKandidater(4189, (tilstand) => meldt.push(tilstand));
  svar("/api/vakter/4189/kandidater", json({ status: "ok", kandidater: [] }));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "klar", kandidater: [] });
});

test("taggen viser nivået av fire", () => {
  assert.equal(t.nivaaTag(3), "Nivå 3/4");
  assert.equal(t.nivaaTag(4), "Nivå 4/4");
});

test("listen hentes straks og meldes etter laster", async () => {
  const svar = styrtFetch();
  const meldt = [];
  k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
  assert.deepEqual(meldt, [{ type: "laster" }]);

  svar("/api/vakter/4127/kandidater", json(OK_4127));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "klar", kandidater: OK_4127.kandidater });
});

test("datafeil fra API-et blir datafeil, ikke tom liste", async () => {
  const svar = styrtFetch();
  const meldt = [];
  k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
  svar("/api/vakter/4127/kandidater", json(DATAFEIL));
  await nesteTick();
  assert.deepEqual(meldt.at(-1), { type: "datafeil", datagrense: DATAFEIL.datagrense });
});

test("forsinket svar for forrige vakt erstatter ikke den aktive (P-09)", async () => {
  const svar = styrtFetch();
  const meldt = [];
  const meld = (tilstand) => meldt.push(tilstand);

  const avbryt4127 = k.lastKandidater(4127, meld);
  avbryt4127(); // Vaktbytte: komponenten ryddes opp.
  k.lastKandidater(4189, meld);

  svar("/api/vakter/4189/kandidater", json(OK_4189));
  await nesteTick();
  svar("/api/vakter/4127/kandidater", json(OK_4127));
  await nesteTick();

  assert.deepEqual(meldt, [{ type: "laster" }, { type: "laster" }, { type: "klar", kandidater: OK_4189.kandidater }]);
});

test("forsinket feil for forrige vakt meldes heller ikke", async () => {
  const svar = styrtFetch();
  const meldt = [];
  const avbryt = k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
  avbryt();
  svar("/api/vakter/4127/kandidater", json({ kode: "intern_feil", melding: "x" }, 500));
  await nesteTick();
  assert.deepEqual(meldt, [{ type: "laster" }]);
});

test("svar fra en sesjon som er byttet ut, meldes ikke (P-09)", async () => {
  const svar = styrtFetch();
  const meldt = [];
  k.lastKandidater(4127, (tilstand) => meldt.push(tilstand));
  k.nySesjonsgenerasjon(); // Utlogging eller ny innlogging mens kallet pågår.
  svar("/api/vakter/4127/kandidater", json(OK_4127));
  await nesteTick();
  assert.deepEqual(meldt, [{ type: "laster" }]);
});
