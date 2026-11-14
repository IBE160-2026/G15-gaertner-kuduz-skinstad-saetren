import { chromium } from "playwright-core";
import fs from "node:fs";

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = "http://localhost:5173";
const SHOT_DIR = "C:/Users/FREDRI~1/AppData/Local/Temp/claude/6beb21c8d2d4a891/b0b1c5e4-d2a4-4ebc-96d6-2260d58a7a81/scratchpad/pw/skjermbilder";
fs.mkdirSync(SHOT_DIR, { recursive: true });

const resultat = { feil: [] };
function sjekk(navn, betingelse, detaljer) {
  const status = betingelse ? "OK" : "FEIL";
  console.log(`[${status}] ${navn}${detaljer ? " — " + detaljer : ""}`);
  if (!betingelse) resultat.feil.push(navn);
}

const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const consoleFeil = [];

async function nyKontekst(bredde = 1280, hoyde = 900) {
  const ctx = await browser.newContext({ viewport: { width: bredde, height: hoyde } });
  const side = await ctx.newPage();
  side.on("console", (msg) => {
    if (msg.type() !== "error") return;
    // Nettverksfeil for forventede statuskoder (401 før innlogging, manglende
    // favicon) logges av nettleseren selv som "error" uten å være et JS-unntak.
    if (/Failed to load resource/.test(msg.text())) return;
    consoleFeil.push(msg.text());
  });
  side.on("pageerror", (err) => consoleFeil.push(String(err)));
  return { ctx, side };
}

async function loggInn(side) {
  await side.goto(BASE, { waitUntil: "domcontentloaded" });
  await side.waitForSelector('input[name="brukernavn"], input#brukernavn, input[type="text"]', { timeout: 15000 });
  const brukernavnFelt = side.locator('input[name="brukernavn"], input#brukernavn, input[type="text"]').first();
  const passordFelt = side.locator('input[name="passord"], input#passord, input[type="password"]').first();
  await brukernavnFelt.fill("kari.vestby");
  await passordFelt.fill("Nettleserkontroll123!");
  await passordFelt.press("Enter");
  await side.waitForURL(/turnus\//, { timeout: 15000 });
}

async function kontrollerVakt(side, vaktnummer, forventetTekst) {
  await side.goto(`${BASE}/vakt/${vaktnummer}/kandidater`, { waitUntil: "domcontentloaded" });
  await side.waitForSelector(".ekskludert-boks", { timeout: 15000 });
  const boksTekst = (await side.locator(".ekskludert-boks .brodtekst").innerText()).trim();
  sjekk(`#${vaktnummer}: Ekskludert-boksens tekst`, boksTekst === forventetTekst, `fikk: "${boksTekst}"`);

  const knapp = side.locator(".ekskludert-boks button");
  const forAria = await knapp.getAttribute("aria-expanded");
  sjekk(`#${vaktnummer}: knappen starter lukket (aria-expanded=false)`, forAria === "false", `fikk: ${forAria}`);

  const listeSynligFor = await side.locator(".ekskludert-liste").count();
  sjekk(`#${vaktnummer}: full listen er ikke i DOM-en før åpning`, listeSynligFor === 0);

  // Tastaturbetjening: fokuser knappen direkte og trykk Enter (tab-rekkefølgen testes ikke her).
  await knapp.focus();
  await side.keyboard.press("Enter");
  await side.waitForSelector(".ekskludert-liste", { timeout: 5000 });
  const etterAria = await knapp.getAttribute("aria-expanded");
  sjekk(`#${vaktnummer}: aria-expanded blir true etter Enter`, etterAria === "true", `fikk: ${etterAria}`);

  const radAntall = await side.locator(".ekskludert-liste li").count();
  const forventetAntall = Number(forventetTekst.match(/^(\d+)/)[1]);
  sjekk(`#${vaktnummer}: full listen har ${forventetAntall} rader`, radAntall === forventetAntall, `fikk: ${radAntall}`);

  await side.screenshot({ path: `${SHOT_DIR}/vakt-${vaktnummer}-apen.png`, fullPage: true });

  // Lukk igjen med tastatur.
  await knapp.focus();
  await side.keyboard.press("Enter");
  await side.waitForSelector(".ekskludert-liste", { state: "detached", timeout: 5000 });
  const lukketAria = await knapp.getAttribute("aria-expanded");
  sjekk(`#${vaktnummer}: lukkes igjen med Enter`, lukketAria === "false", `fikk: ${lukketAria}`);
}

try {
  const { side } = await nyKontekst(1280, 900);
  await loggInn(side);

  await kontrollerVakt(
    side, 4127,
    "20 utelukket av harde regler · 8 under kompetanse-minstekrav · 7 kolliderende vakt · 4 brudd på 11-timersregelen · 1 brudd på 35-timersregelen",
  );
  await kontrollerVakt(
    side, 4189,
    "24 utelukket av harde regler · 3 under kompetanse-minstekrav · 2 kolliderende vakt · 18 brudd på 11-timersregelen · 1 brudd på 35-timersregelen",
  );

  // 360 px bredde: ingen vannrett siderulling, og boksen er fortsatt lesbar.
  await side.setViewportSize({ width: 360, height: 800 });
  await side.goto(`${BASE}/vakt/4127/kandidater`, { waitUntil: "domcontentloaded" });
  await side.waitForSelector(".ekskludert-boks", { timeout: 15000 });
  const { scrollWidth, clientWidth } = await side.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  sjekk("360 px: ingen vannrett siderulling", scrollWidth <= clientWidth + 1, `scrollWidth=${scrollWidth} clientWidth=${clientWidth}`);
  await side.screenshot({ path: `${SHOT_DIR}/vakt-4127-360px.png`, fullPage: true });

  sjekk("Ingen konsollfeil underveis", consoleFeil.length === 0, consoleFeil.join(" | "));
} catch (e) {
  console.error("UVENTET FEIL:", e);
  resultat.feil.push("uventet feil: " + e.message);
} finally {
  await browser.close();
}

console.log("\n=== OPPSUMMERING ===");
if (resultat.feil.length === 0) {
  console.log("Alle kontroller besto.");
  process.exit(0);
} else {
  console.log("Feilet:", resultat.feil.join("; "));
  process.exit(1);
}
