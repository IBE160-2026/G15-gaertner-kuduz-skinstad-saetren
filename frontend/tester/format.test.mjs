// Fester den nøyaktige teksten fra format.ts (story 1.5). Alt skal vises i
// Europe/Oslo uansett tidssonen testen kjøres i. Gruppas maskiner går i
// Oslo-tid, så den siste testen kjører hele fila på nytt i en underprosess med
// TZ=America/New_York. Ellers ville testene bestått selv uten `timeZone`.
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { build } from "rolldown";

async function lastTs(sti) {
  const resultat = await build({ input: fileURLToPath(new URL(sti, import.meta.url)) });
  const js = resultat.output[0].code;
  return import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
}

const f = await lastTs("../src/format.ts");

// #4127 og #4189 slik API-et sender dem.
const V4127 = {
  vaktnummer: 4127, vakttype: "dag",
  start: "2026-09-27T07:00:00+02:00", slutt: "2026-09-27T15:00:00+02:00",
  satt_opp: "Silje Amundsen", meldt_fra: "2026-09-27T06:14:00+02:00", grunn: "sykemeldt",
};
const V4189 = {
  vaktnummer: 4189, vakttype: "natt",
  start: "2026-09-28T23:00:00+02:00", slutt: "2026-09-29T07:00:00+02:00",
  satt_opp: "Eirik Moen", meldt_fra: "2026-09-26T21:40:00+02:00", grunn: "sykemeldt",
};

test("brødsmule for valgt vakt bruker dato i Oslo", () => {
  assert.equal(f.vaktBrodsmule(4127, "dag", V4127.start), "Vakt #4127 — Dagvakt 27.09.2026");
  assert.equal(f.vaktBrodsmule(4189, "natt", "2026-09-28T21:00:00Z"), "Vakt #4189 — Nattevakt 28.09.2026");
});

test("ukedag og dato med stor forbokstav og tosifret dag og måned", () => {
  assert.equal(f.ukedagOgDato(V4127.start), "Søndag 27.09.2026");
  assert.equal(f.ukedagOgDato(V4189.start), "Mandag 28.09.2026");
  assert.equal(f.ukedagOgDato("2026-10-01T07:00:00+02:00"), "Torsdag 01.10.2026");
  // Samme tidspunkt i UTC gir datoen i Oslo, ikke i UTC.
  assert.equal(f.ukedagOgDato("2026-09-27T22:30:00Z"), "Mandag 28.09.2026");
});

test("tidsrom og varighet, også over døgnskifte", () => {
  assert.equal(f.tidsrom(V4127.start, V4127.slutt), "07:00–15:00 (8 t)");
  assert.equal(f.tidsrom(V4189.start, V4189.slutt), "23:00–07:00 (8 t)");
  // Utenlandsk offset vises i Oslo-tid.
  assert.equal(f.tidsrom("2026-09-28T21:00:00Z", "2026-09-29T05:00:00Z"), "23:00–07:00 (8 t)");
  // Varighet som ikke er hele timer, med desimalkomma.
  assert.equal(f.tidsrom("2026-09-28T07:00:00+02:00", "2026-09-28T14:30:00+02:00"), "07:00–14:30 (7,5 t)");
});

test("varighet er reell tid over sommertidsskiftet 25.10.2026", () => {
  // Klokka stilles fra 03:00 til 02:00, så natta er 9 timer.
  assert.equal(f.tidsrom("2026-10-24T23:00:00+02:00", "2026-10-25T07:00:00+01:00"), "23:00–07:00 (9 t)");
  assert.equal(f.tidsrom("2026-10-25T07:00:00+01:00", "2026-10-25T15:00:00+01:00"), "07:00–15:00 (8 t)");
  // Våren: 29.03.2026 stilles klokka fram, så natta er 7 timer.
  assert.equal(f.tidsrom("2026-03-28T23:00:00+01:00", "2026-03-29T07:00:00+02:00"), "23:00–07:00 (7 t)");
});

test("periodetekst med ISO-uker", () => {
  assert.equal(f.periodetekst("2026-09-21T00:00:00+02:00", "2026-10-05T00:00:00+02:00"), "Uke 39–40, 2026");
  assert.equal(f.periodetekst("2026-09-21T00:00:00+02:00", "2026-09-28T00:00:00+02:00"), "Uke 39, 2026");
  assert.equal(f.periodetekst("2026-12-21T00:00:00+01:00", "2027-01-11T00:00:00+01:00"), "Uke 52, 2026 – uke 1, 2027");
  // 01.01.2027 er fredag i ISO-uke 53 av 2026, så ISO-året er 2026, ikke 2027.
  assert.equal(f.periodetekst("2027-01-01T00:00:00+01:00", "2027-01-04T00:00:00+01:00"), "Uke 53, 2026");
  assert.equal(f.periodetekst("2027-01-01T00:00:00+01:00", "2027-01-11T00:00:00+01:00"), "Uke 53, 2026 – uke 1, 2027");
});

test("ISO-uke ved årsskifter", () => {
  assert.deepEqual(f.isoUke({ aar: 2026, maaned: 9, dag: 21 }), { uke: 39, aar: 2026 });
  assert.deepEqual(f.isoUke({ aar: 2026, maaned: 10, dag: 4 }), { uke: 40, aar: 2026 });
  assert.deepEqual(f.isoUke({ aar: 2024, maaned: 12, dag: 30 }), { uke: 1, aar: 2025 });
  assert.deepEqual(f.isoUke({ aar: 2021, maaned: 1, dag: 3 }), { uke: 53, aar: 2020 });
});

test("vakttyper", () => {
  assert.equal(f.vakttypenavn("dag"), "Dagvakt");
  assert.equal(f.vakttypenavn("mellom"), "Mellomvakt");
  assert.equal(f.vakttypenavn("kveld"), "Kveldsvakt");
  assert.equal(f.vakttypenavn("natt"), "Nattevakt");
});

test("tidspunktet for melding: samme dag og annen dag", () => {
  assert.equal(f.meldtFraTidspunkt(V4127.meldt_fra, V4127.start), "kl. 06:14");
  assert.equal(f.meldtFraTidspunkt(V4189.meldt_fra, V4189.start), "26.09 kl. 21:40");
});

test("linja i varselboksen", () => {
  const a = f.varsellinje(V4127);
  assert.equal(a.foer + a.status + a.etter,
    "Søndag 27.09.2026 · 07:00–15:00 (8 t) · Mangler bemanning — Silje Amundsen meldt fra sykemeldt kl. 06:14");
  assert.equal(a.status, "Mangler bemanning");
  const b = f.varsellinje(V4189);
  assert.equal(b.foer + b.status + b.etter,
    "Mandag 28.09.2026 · 23:00–07:00 (8 t) · Mangler bemanning — Eirik Moen meldt fra sykemeldt 26.09 kl. 21:40");
  const uten = f.varsellinje({ ...V4127, satt_opp: null, meldt_fra: null, grunn: null });
  assert.equal(uten.etter, "");
  assert.equal(f.varsellinje({ ...V4127, grunn: null }).etter, " — Silje Amundsen meldt fra kl. 06:14");
  assert.equal(f.varsellinje({ ...V4127, meldt_fra: null }).etter, " — Silje Amundsen meldt fra sykemeldt");
  assert.equal(f.varsellinje({ ...V4127, grunn: null, meldt_fra: null }).etter, " — Silje Amundsen meldt fra");
  assert.doesNotMatch(a.foer + a.status + a.etter, /!/);
});

test("fotnotens tidspunkt", () => {
  assert.equal(f.datoOgKlokke("2026-09-27T06:20:00+02:00"), "27.09.2026 06:20");
  assert.equal(f.datoOgKlokke("2026-09-26T22:05:00Z"), "27.09.2026 00:05");
});

test("erNyttDogn etter startdato i Oslo", () => {
  assert.equal(f.erNyttDogn(undefined, V4127.start), true);
  assert.equal(f.erNyttDogn(null, V4127.start), true);
  assert.equal(f.erNyttDogn("2026-09-27T07:00:00+02:00", "2026-09-27T23:00:00+02:00"), false);
  // Nattevakten 27.09 23:00 hører til 27.09, så dagvakten 28.09 er et nytt døgn.
  assert.equal(f.erNyttDogn("2026-09-27T23:00:00+02:00", "2026-09-28T07:00:00+02:00"), true);
  // 22:30 UTC er 00:30 i Oslo neste dag.
  assert.equal(f.erNyttDogn("2026-09-27T21:00:00Z", "2026-09-27T22:30:00Z"), true);
});

test("radklasser: fet dato på første rad i hvert døgn, linje bare ved døgnskifte, row-alt annenhver", () => {
  const vakter = [
    { start: "2026-09-21T07:00:00+02:00" }, // 0: første rad
    { start: "2026-09-21T15:00:00+02:00" }, // 1: samme døgn
    { start: "2026-09-21T23:00:00+02:00" }, // 2: samme døgn (natt hører til startdatoen)
    { start: "2026-09-22T07:00:00+02:00" }, // 3: nytt døgn
    { start: "2026-09-22T15:00:00+02:00" }, // 4: samme døgn
  ];
  assert.deepEqual(vakter.map((_, i) => f.radklasser(vakter, i)), [
    { rad: undefined, datoUthevet: true },
    { rad: "row-alt", datoUthevet: false },
    { rad: undefined, datoUthevet: false },
    { rad: "row-alt dogn-start", datoUthevet: true },
    { rad: undefined, datoUthevet: false },
  ]);
  const toDogn = [{ start: "2026-09-21T07:00:00+02:00" }, { start: "2026-09-22T07:00:00+02:00" }, { start: "2026-09-23T07:00:00+02:00" }];
  assert.equal(f.radklasser(toDogn, 2).rad, "dogn-start");
});

const ANNEN_SONE = "America/New_York";

if (process.env.FORMAT_TEST_SONE) {
  test("underprosessen kjører i en annen tidssone enn Oslo", () => {
    assert.equal(Intl.DateTimeFormat().resolvedOptions().timeZone, ANNEN_SONE);
    assert.notEqual(new Date("2026-09-27T12:00:00Z").getHours(), 14);
  });
} else {
  test(`samme tester består med TZ=${ANNEN_SONE}`, () => {
    // TZ settes i env for underprosessen, så det virker også på Windows.
    const env = { ...process.env, TZ: ANNEN_SONE, FORMAT_TEST_SONE: "1" };
    delete env.NODE_TEST_CONTEXT;
    const resultat = spawnSync(process.execPath, ["--test", fileURLToPath(import.meta.url)], {
      env, encoding: "utf-8",
    });
    assert.equal(resultat.status, 0, resultat.stdout + resultat.stderr);
    assert.match(resultat.stdout, /# fail 0|ℹ fail 0/);
  });
}
