import assert from "node:assert/strict";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { build } from "rolldown";

async function lastTs(sti) {
  const resultat = await build({ input: fileURLToPath(new URL(sti, import.meta.url)) });
  const js = resultat.output[0].code;
  return import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
}

function styrtSvar() {
  let fullfoer;
  const svar = new Promise((resolve) => { fullfoer = resolve; });
  return { svar, fullfoer };
}

test("direkte URL og gyldig sesjon beholder bare kjente mål", async () => {
  const navigasjon = await lastTs("../src/navigasjon.ts");
  assert.equal(navigasjon.maalEtterBekreftetSesjon("/logg-inn"), navigasjon.OVERSIKT_STI);
  assert.equal(navigasjon.maalEtterBekreftetSesjon("/"), navigasjon.OVERSIKT_STI);
  assert.equal(navigasjon.maalEtterBekreftetSesjon("/ukjent"), "/ukjent");
  const historikk = [];
  globalThis.window = {
    location: { pathname: "/ukjent" },
    history: { replaceState: (_a, _b, sti) => historikk.push(sti) },
  };
  navigasjon.naviger("/logg-inn", true);
  assert.deepEqual(historikk, ["/logg-inn"]);
  delete globalThis.window;
});

test("forsinket 401 fra gammel sesjon varsler ikke etter ny innlogging", async () => {
  const api = await lastTs("../src/api.ts");
  const vent = styrtSvar();
  globalThis.fetch = () => vent.svar;
  let varsler = 0;
  api.settSesjonsvarsler(() => { varsler += 1; });
  const gammeltKall = api.hentMeg();
  api.nySesjonsgenerasjon(); // Ny innlogging er bekreftet.
  vent.fullfoer(new Response("", { status: 401 }));
  await assert.rejects(gammeltKall, (feil) => feil.status === 401);
  assert.equal(varsler, 0);
  delete globalThis.fetch;
});

test("forsinket /api/meg etter utlogging kan skilles fra gjeldende sesjon", async () => {
  const api = await lastTs("../src/api.ts");
  const vent = styrtSvar();
  globalThis.fetch = () => vent.svar;
  const generasjon = api.gjeldendeSesjonsgenerasjon();
  const gammeltKall = api.hentMeg();
  api.nySesjonsgenerasjon(); // Utlogging sperrer videre visning.
  vent.fullfoer(new Response(JSON.stringify({ navn: "Kari", avdeling: "Kirurgisk sengepost" }), {
    status: 200, headers: { "Content-Type": "application/json" },
  }));
  await gammeltKall;
  assert.notEqual(generasjon, api.gjeldendeSesjonsgenerasjon());
  delete globalThis.fetch;
});
