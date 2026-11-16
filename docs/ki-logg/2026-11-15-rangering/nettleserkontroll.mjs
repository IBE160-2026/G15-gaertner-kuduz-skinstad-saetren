// Nettleserkontroll for story 4.4 (rangeringstabellen). Headless Chrome via playwright-core
// mot egen backend (port 8001, midlertidig database med testdata) og Vite (port 5174).
// Kontrollerer det komponenttestene i jsdom ikke kan se: beregnet CSS, rulling og synlig fokus.
import { chromium } from "playwright-core";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = "http://localhost:5174";
// Skjermbildene skal ikke i repoet: temp-mappen, eller mappen i SKJERMBILDER.
const SHOT_DIR = process.env.SKJERMBILDER ?? path.join(os.tmpdir(), "nettleserkontroll-4-4");
fs.mkdirSync(SHOT_DIR, { recursive: true });

const feil = [];
function sjekk(navn, ok, detaljer = "") {
  console.log(`[${ok ? "OK" : "FEIL"}] ${navn}${detaljer ? " — " + detaljer : ""}`);
  if (!ok) feil.push(navn);
}

const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const konsollfeil = [];

async function nySide(bredde, hoyde = 900) {
  const ctx = await browser.newContext({ viewport: { width: bredde, height: hoyde } });
  const side = await ctx.newPage();
  side.on("console", (m) => { if (m.type() === "error" && !/Failed to load resource/.test(m.text())) konsollfeil.push(m.text()); });
  side.on("pageerror", (e) => konsollfeil.push(String(e)));
  await side.goto(BASE, { waitUntil: "domcontentloaded" });
  await side.fill("#brukernavn", "kari.vestby");
  await side.fill("#passord", "Nettleserkontroll123!");
  await side.press("#passord", "Enter");
  await side.waitForURL(/turnus\//, { timeout: 15000 });
  return side;
}

async function åpne4127(side) {
  await side.goto(`${BASE}/vakt/4127/kandidater`, { waitUntil: "domcontentloaded" });
  await side.waitForSelector(".rangeringstabell tbody tr", { timeout: 15000 });
}

const sideRuller = (side) => side.evaluate(() => ({
  scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth,
}));

const fokusStil = (side) => side.evaluate(() => {
  const el = document.activeElement;
  const s = getComputedStyle(el);
  return {
    etikett: el.getAttribute("aria-label") ?? el.textContent.trim(),
    fokusSynlig: el.matches(":focus-visible"),
    outline: `${s.outlineStyle} ${s.outlineWidth} ${s.outlineColor}`,
  };
});

try {
  // 1. 1600 px: rekkefølge, rank-badge, row-alt, ingen siderulling.
  const side = await nySide(1600);
  await åpne4127(side);
  const navn = await side.locator(".rangeringstabell tbody tr .ansattnavn").allInnerTexts();
  sjekk("#4127: rekkefølge Jonas, Mette, Thomas, Ingrid",
    JSON.stringify(navn) === JSON.stringify(["Jonas Bakke", "Mette Solberg", "Thomas Nygård", "Ingrid Dahl"]), navn.join(", "));
  const plasser = await side.locator(".rank-badge").allInnerTexts();
  sjekk("#4127: plassnummer 1–4", plasser.join(",") === "1,2,3,4", plasser.join(","));

  const badge = await side.locator(".rank-badge").first().evaluate((el) => {
    const s = getComputedStyle(el);
    return { farge: s.color, størrelse: s.fontSize, vekt: s.fontWeight };
  });
  const accent = await side.evaluate(() => {
    const d = document.createElement("span"); d.style.color = "var(--color-accent)"; document.body.append(d);
    const c = getComputedStyle(d).color; d.remove(); return c;
  });
  sjekk("rank-badge i accent", badge.farge === accent, `${badge.farge} (accent ${accent})`);
  sjekk("rank-badge 14px", badge.størrelse === "14px", badge.størrelse);
  sjekk("rank-badge fet", Number(badge.vekt) >= 700, badge.vekt);

  const bakgrunner = await side.locator(".rangeringstabell tbody tr").evaluateAll((rader) =>
    rader.map((r) => ({ alt: r.classList.contains("row-alt"), bg: getComputedStyle(r).backgroundColor })));
  sjekk("row-alt på rad 2 og 4", bakgrunner.map((b) => b.alt).join(",") === "false,true,false,true",
    bakgrunner.map((b) => `${b.alt ? "alt" : "-"} ${b.bg}`).join(" | "));
  sjekk("row-alt gir egen bakgrunn", bakgrunner[1].bg !== bakgrunner[0].bg, `${bakgrunner[1].bg} mot ${bakgrunner[0].bg}`);

  const tekster = await side.locator(".rangeringstabell tbody tr").first().innerText();
  sjekk("rad 1 har totalscore, meta og preferansetagg",
    /79,4 poeng/.test(tekster) && /Sykepleier · 3 år ansiennitet/.test(tekster) && /Preferanse venter på tolkning/.test(tekster) && /50,0 poeng/.test(tekster),
    tekster.replace(/\s+/g, " "));

  const r1600 = await sideRuller(side);
  sjekk("1600 px: siden ruller ikke vannrett", r1600.scrollWidth <= r1600.clientWidth, JSON.stringify(r1600));
  const tabell1600 = await side.locator(".rangeringstabell").evaluate((el) => ({ scrollWidth: el.scrollWidth, clientWidth: el.clientWidth }));
  sjekk("1600 px: alle kolonner synlige uten rulling i tabellen", tabell1600.scrollWidth <= tabell1600.clientWidth, JSON.stringify(tabell1600));
  await side.screenshot({ path: `${SHOT_DIR}/4127-1600px.png`, fullPage: true });

  // 2. Fokus med tastatur: fra tabellbeholderen, Tab til Velg for Jonas.
  await side.locator(".rangeringstabell").focus();
  const beholderFokus = await fokusStil(side);
  sjekk("tabellbeholderen har synlig fokusmarkering", beholderFokus.fokusSynlig && beholderFokus.outline.startsWith("solid"), beholderFokus.outline);
  await side.keyboard.press("Tab");
  const velgFokus = await fokusStil(side);
  sjekk("Tab gir synlig fokus på Velg for Jonas",
    /Jonas Bakke/.test(velgFokus.etikett) && velgFokus.fokusSynlig && velgFokus.outline.startsWith("solid"),
    `${velgFokus.etikett}: ${velgFokus.outline}`);
  await side.locator(".rangeringstabell").screenshot({ path: `${SHOT_DIR}/4127-fokus-velg.png` });

  // 3. 1080 px: tabellen ruller i egen beholder, ikke siden.
  for (const bredde of [1080, 960, 680]) {
    await side.setViewportSize({ width: bredde, height: 900 });
    await åpne4127(side);
    const rs = await sideRuller(side);
    const beholder = await side.locator(".rangeringstabell").evaluate((el) => ({
      overflowX: getComputedStyle(el).overflowX, scrollWidth: el.scrollWidth, clientWidth: el.clientWidth,
    }));
    const kritisk = bredde === 1080;
    const ok = rs.scrollWidth <= rs.clientWidth && beholder.overflowX === "auto";
    console.log(`${kritisk ? "" : "(info, story 4.6) "}${bredde} px: side ${JSON.stringify(rs)}, beholder ${JSON.stringify(beholder)}`);
    if (kritisk) sjekk("1080 px: siden ruller ikke vannrett, tabellen har egen rulling", ok);
    await side.screenshot({ path: `${SHOT_DIR}/4127-${bredde}px.png`, fullPage: true });
  }

  // 4. «Vis alle» og «Vis bare de 5 øverste» med syv kandidater. Seeden har bare fire
  //    gyldige på #4127, så svaret utvides med tre konstruerte rader i nettleseren.
  const side2 = await nySide(1600);
  await side2.route("**/api/vakter/4127/kandidater", async (route) => {
    const svar = await route.fetch();
    const data = await svar.json();
    const mal = data.kandidater[3];
    const ekstra = [1, 2, 3].map((n) => ({
      ...mal, id: 900 + n, navn: `Konstruert kandidat ${n}`, plass: 4 + n, totalscore: mal.totalscore - n,
    }));
    await route.fulfill({ response: svar, json: { ...data, kandidater: [...data.kandidater, ...ekstra] } });
  });
  await åpne4127(side2);
  sjekk("7 kandidater: fem rader vises først", (await side2.locator(".rangeringstabell tbody tr").count()) === 5);
  const visAlle = side2.getByRole("button", { name: "Vis alle gyldige kandidater" });
  await visAlle.focus();
  await side2.keyboard.press("Tab"); await side2.keyboard.press("Shift+Tab"); // tastaturfokus, så :focus-visible gjelder
  const visAlleFokus = await fokusStil(side2);
  sjekk("«Vis alle» har synlig fokus", visAlleFokus.fokusSynlig && visAlleFokus.outline.startsWith("solid"), visAlleFokus.outline);
  await side2.screenshot({ path: `${SHOT_DIR}/vis-alle-lukket-fokus.png`, fullPage: true });

  await side2.keyboard.press("Enter");
  sjekk("Enter viser alle 7", (await side2.locator(".rangeringstabell tbody tr").count()) === 7);
  const rad6Fokus = await fokusStil(side2);
  sjekk("fokus på Velg i rad 6, synlig", /Konstruert kandidat 2/.test(rad6Fokus.etikett) && rad6Fokus.fokusSynlig, `${rad6Fokus.etikett}: ${rad6Fokus.outline}`);
  await side2.screenshot({ path: `${SHOT_DIR}/vis-alle-apen-fokus-rad-6.png`, fullPage: true });

  const visFærre = side2.getByRole("button", { name: "Vis bare de 5 øverste" });
  await visFærre.focus();
  await side2.keyboard.press("Tab"); await side2.keyboard.press("Shift+Tab");
  await side2.keyboard.press("Enter");
  sjekk("«Vis bare de 5 øverste» lukker til fem", (await side2.locator(".rangeringstabell tbody tr").count()) === 5);
  const etterLukk = await fokusStil(side2);
  sjekk("fokus blir stående på knappen, synlig", /Vis alle gyldige kandidater/.test(etterLukk.etikett) && etterLukk.fokusSynlig, `${etterLukk.etikett}: ${etterLukk.outline}`);
  const r2 = await sideRuller(side2);
  sjekk("siden ruller ikke vannrett med 7 rader", r2.scrollWidth <= r2.clientWidth, JSON.stringify(r2));
  await side2.screenshot({ path: `${SHOT_DIR}/vis-alle-lukket-igjen-fokus.png`, fullPage: true });

  // 5. #4189 er uendret: tomtilstand uten tabell.
  await side.setViewportSize({ width: 1600, height: 900 });
  await side.goto(`${BASE}/vakt/4189/kandidater`, { waitUntil: "domcontentloaded" });
  await side.waitForSelector(".tomtilstand", { timeout: 15000 });
  sjekk("#4189: tomtilstand uten rangeringstabell", (await side.locator(".rangeringstabell").count()) === 0);
  await side.screenshot({ path: `${SHOT_DIR}/4189-1600px.png`, fullPage: true });

  sjekk("ingen konsollfeil", konsollfeil.length === 0, konsollfeil.join(" | "));
} catch (e) {
  console.error("UVENTET FEIL:", e);
  feil.push("uventet feil: " + e.message);
} finally {
  await browser.close();
}

console.log(feil.length ? `\nFeilet: ${feil.join("; ")}` : "\nAlle kontroller besto.");
process.exit(feil.length ? 1 : 0);
