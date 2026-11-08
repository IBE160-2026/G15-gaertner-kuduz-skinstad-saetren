// Liten CDP-driver for røyktest av Vaktvalg i headless Chrome.
import { writeFileSync } from "node:fs";

const PORT = process.argv[2] ?? "9333";
const UT = process.argv[3];
const PASSORD = process.argv[4];
const vent = (ms) => new Promise((r) => setTimeout(r, ms));

const sider = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const side = sider.find((s) => s.type === "page");
const ws = new WebSocket(side.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const ventende = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && ventende.has(m.id)) { ventende.get(m.id)(m); ventende.delete(m.id); }
});
function cdp(method, params = {}) {
  return new Promise((r) => { const n = ++id; ventende.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
}
async function ev(uttrykk) {
  const s = await cdp("Runtime.evaluate", { expression: uttrykk, returnByValue: true, awaitPromise: true });
  if (s.result.exceptionDetails) throw new Error(JSON.stringify(s.result.exceptionDetails));
  return s.result.result.value;
}
async function tast(key, code, keyCode, text) {
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode: keyCode, text });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode });
}
async function bilde(navn) {
  const s = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(`${UT}/${navn}.png`, Buffer.from(s.result.data, "base64"));
}

await cdp("Page.enable");
await cdp("Network.enable");
await cdp("Runtime.enable");

async function loggInn() {
  await cdp("Network.clearBrowserCookies");
  await cdp("Page.navigate", { url: "http://localhost:5173/logg-inn" });
  for (let i = 0; i < 50 && !(await ev(`!!document.getElementById("brukernavn")`)); i++) await vent(200);
  await ev(`(() => {
    const sett = (el, v) => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(el, v); el.dispatchEvent(new Event("input", { bubbles: true })); };
    sett(document.getElementById("brukernavn"), "kari.vestby");
    sett(document.getElementById("passord"), ${JSON.stringify(PASSORD)});
    document.querySelector("form").requestSubmit();
  })()`);
  for (let i = 0; i < 50 && !(await ev(`!!document.querySelector(".fotnote")`)); i++) await vent(200);
}

const rapport = {};
for (const [bredde, skrift] of (process.env.BARE_TASTATUR ? [] : [[1600, 16], [360, 20]])) {
  await cdp("Emulation.setDeviceMetricsOverride", { width: bredde, height: 900, deviceScaleFactor: 1, mobile: false });
  await cdp("Page.setFontSizes", { fontSizes: { standard: skrift } });
  await loggInn();
  rapport[`${bredde}px/${skrift}px`] = await ev(`(() => {
    const rader = [...document.querySelectorAll(".tabell tbody tr")];
    const beholder = document.querySelector(".tabellbeholder");
    const klippet = [...document.querySelectorAll(".alert-box *, .tabell td, .brodsmulesti, .fotnote")]
      .filter((el) => el.scrollHeight > el.clientHeight + 1 && getComputedStyle(el).overflow !== "visible").length;
    return {
      sti: location.pathname,
      sideRullerVannrett: document.documentElement.scrollWidth > window.innerWidth,
      tabellRuller: beholder ? beholder.scrollWidth > beholder.clientWidth : null,
      brodsmule: document.querySelector("nav.brodsmulesti")?.innerText,
      brodsmuleUthevet: document.querySelector("nav.brodsmulesti b")?.innerText,
      h1: document.querySelector("h1")?.innerText,
      h2: [...document.querySelectorAll("h2")].map((h) => h.innerText),
      h3: [...document.querySelectorAll("h3")].map((h) => h.innerText),
      linjer: [...document.querySelectorAll(".alert-box-linje")].map((p) => p.innerText),
      status: [...document.querySelectorAll(".alert-box-status")].map((s) => getComputedStyle(s).color + " " + getComputedStyle(s).fontWeight),
      knapper: [...document.querySelectorAll(".alert-box button")].map((b) => b.innerText),
      rader: rader.length,
      forsteRadDognStart: rader[0]?.classList.contains("dogn-start"),
      forsteRadDatoFet: rader[0]?.children[1].classList.contains("dato-uthevet"),
      dognStart: rader.filter((r) => r.classList.contains("dogn-start")).length,
      rowAlt: rader.filter((r) => r.classList.contains("row-alt")).length,
      forsteRad: rader[0]?.innerText,
      tagFarge: getComputedStyle(document.querySelector(".tag-status")).color,
      fotnote: document.querySelector(".fotnote")?.innerText,
      klippet,
      utropstegn: document.querySelector("main").innerText.replace(/^!$/gm, "").includes("!"),
    };
  })()`);
  await bilde(`topp-${bredde}-${skrift}`);
}

// Tastatur: tab fram til første «Velg vakt» og trykk enter.
await cdp("Emulation.setDeviceMetricsOverride", { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
await cdp("Page.setFontSizes", { fontSizes: { standard: 16 } });
await loggInn();
const fokus = [];
for (let i = 0; i < 6; i++) {
  await tast("Tab", "Tab", 9);
  fokus.push(await ev("document.activeElement.innerText || document.activeElement.tagName"));
}
rapport.tastaturFokus = fokus;
// Fokus står på andre «Velg vakt» hvis rekkefølgen er Logg ut, Velg 1, Velg 2.
await ev(`[...document.querySelectorAll(".alert-box button")][0].focus()`);
await tast("Enter", "Enter", 13, String.fromCharCode(13));
await vent(500);
rapport.etterEnter = await ev(`({ sti: location.pathname, tekst: document.querySelector("main")?.innerText })`);
await cdp("Page.navigate", { url: "http://localhost:5173/turnus/kirurgisk-sengepost" });
for (let i = 0; i < 50 && !(await ev(`!!document.querySelector(".fotnote")`)); i++) await vent(200);
await ev(`[...document.querySelectorAll(".alert-box button")][1].focus()`);
await tast("Enter", "Enter", 13, String.fromCharCode(13));
await vent(500);
rapport.etterEnter2 = await ev(`({ sti: location.pathname, tekst: document.querySelector("main")?.innerText })`);

console.log(JSON.stringify(rapport, null, 2));
ws.close();
process.exit(0);
