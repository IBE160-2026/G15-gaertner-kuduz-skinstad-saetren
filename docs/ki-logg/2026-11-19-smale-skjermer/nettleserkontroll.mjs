// Nettleserkontroll for story 4.6 (smale nettleservinduer). Headless Chrome via Chrome
// DevTools Protocol, med Node 26 og den innebygde `WebSocket`, etter mønsteret fra
// story 1.5 (../2026-11-08-vaktoversikt/cdp.mjs). Kontrollerer det jsdom ikke kan se:
// siderulling, de faste kolonnene i rangeringstabellen, klipping, fokus og at tilstanden
// står når vindusbredden endres.
//
// Bruk: node nettleserkontroll.mjs <CDP-port> <mappe for skjermbilder> <testpassord>
// Forutsetter backend på 8000 mot en midlertidig testdatabase og Vite på 5173.
import { writeFileSync } from "node:fs";
import path from "node:path";

const [PORT = "9333", UT = ".", PASSORD] = process.argv.slice(2);
const BASE = "http://localhost:5173";
const vent = (ms) => new Promise((r) => setTimeout(r, ms));

const sider = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(sider.find((s) => s.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const ventende = new Map();
const konsollfeil = [];
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && ventende.has(m.id)) { ventende.get(m.id)(m); ventende.delete(m.id); }
  if (m.method === "Runtime.exceptionThrown") konsollfeil.push(m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
    konsollfeil.push(m.params.args.map((a) => a.value ?? a.description).join(" "));
  }
});
function cdp(method, params = {}) {
  return new Promise((r) => { const n = ++id; ventende.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
}
async function ev(uttrykk) {
  const s = await cdp("Runtime.evaluate", { expression: uttrykk, returnByValue: true, awaitPromise: true });
  if (s.result.exceptionDetails) throw new Error(JSON.stringify(s.result.exceptionDetails));
  return s.result.result.value;
}
async function ventPå(uttrykk, forsok = 75) {
  for (let i = 0; i < forsok; i++) { if (await ev(`!!(${uttrykk})`)) return true; await vent(200); }
  throw new Error(`Ventet forgjeves på ${uttrykk}`);
}
async function tast(key, code, keyCode, modifiers = 0) {
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode: keyCode, modifiers });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode, modifiers });
}
// Vindushøyden er 700 px, så Vaktvalg og kandidatflaten får et loddrett rullefelt som tar
// bredde fra siden, slik et vanlig vindu side om side gjør. Med 900 px kunne kandidatflaten
// få plass uten rullefelt, og da så ikke kontrollen at ulempekolonnen gled under de faste
// kolonnene (Mithads funn i PR #32, 2026-11-19).
const HØYDE = 700;
// Hele siden: vinduet gjøres midlertidig like høyt som innholdet. `captureBeyondViewport`
// ble ikke brukt, fordi skjermbildet da ble tatt med standard skriftstørrelse.
let nå = { px: 1600, skrift: 16 };
async function bilde(navn, bareSynsfelt = false) {
  const høyde = bareSynsfelt ? HØYDE : Math.ceil(await ev("document.documentElement.scrollHeight"));
  await cdp("Emulation.setDeviceMetricsOverride", { width: nå.px, height: Math.max(høyde, HØYDE), deviceScaleFactor: 1, mobile: false });
  await vent(200);
  const s = await cdp("Page.captureScreenshot", { format: "png" });
  writeFileSync(path.join(UT, `${navn}.png`), Buffer.from(s.result.data, "base64"));
  await cdp("Emulation.setDeviceMetricsOverride", { width: nå.px, height: HØYDE, deviceScaleFactor: 1, mobile: false });
  await vent(200);
}
async function bredde(px, skrift = 16) {
  nå = { px, skrift };
  await cdp("Emulation.setDeviceMetricsOverride", { width: px, height: HØYDE, deviceScaleFactor: 1, mobile: false });
  await cdp("Page.setFontSizes", { fontSizes: { standard: skrift } });
  await vent(300);
}
async function gåTil(sti, klar) {
  await cdp("Page.navigate", { url: BASE + sti });
  await ventPå(klar);
}

const feil = [];
function sjekk(navn, ok, detaljer) {
  console.log(`[${ok ? "OK" : "FEIL"}] ${navn}${detaljer === undefined ? "" : " — " + (typeof detaljer === "string" ? detaljer : JSON.stringify(detaljer))}`);
  if (!ok) feil.push(navn);
}

await cdp("Page.enable");
await cdp("Runtime.enable");
await cdp("Network.enable");

async function loggInn() {
  await cdp("Network.clearBrowserCookies");
  await gåTil("/logg-inn", `document.getElementById("brukernavn")`);
}
async function sendInnlogging() {
  await ev(`(() => {
    const sett = (el, v) => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(el, v); el.dispatchEvent(new Event("input", { bubbles: true })); };
    sett(document.getElementById("brukernavn"), "kari.vestby");
    sett(document.getElementById("passord"), ${JSON.stringify(PASSORD)});
    document.querySelector("form").requestSubmit();
  })()`);
  await ventPå(`document.querySelector(".fotnote")`);
}

// Felles målinger for en flate: siderulling, klippet innhold og handlinger utenfor vinduet.
// Elementer som skal klippe (skjult tekst, belastningslinja, rullebeholderen) er unntatt.
const MÅL_FLATE = `(() => {
  const unntak = ".visuelt-skjult, .belastningslinje, .tabellbeholder";
  const klippet = [...document.querySelectorAll("body *")]
    .filter((el) => !el.matches(unntak) && !el.closest(".visuelt-skjult"))
    .filter((el) => { const s = getComputedStyle(el); return s.overflowX !== "visible" || s.overflowY !== "visible"; })
    .filter((el) => el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)
    .map((el) => el.className || el.tagName);
  // Handlinger utenfor rullebeholderen må stå helt innenfor vinduet.
  const utenfor = [...document.querySelectorAll("button, a[href], input, [tabindex='0']")]
    .filter((el) => !el.closest(".tabellbeholder") || el.matches(".tabellbeholder"))
    .filter((el) => { const r = el.getBoundingClientRect(); return r.width > 0 && (r.left < 0 || r.right > window.innerWidth + 0.5); })
    .map((el) => el.innerText || el.getAttribute("aria-label") || el.tagName);
  // Tekst som går ut over sin egen boks (nowrap uten plass) i paneler og kort.
  const overløp = [...document.querySelectorAll(".panel, .login-card, .alert-box, .avviksnotat, .ekskludert-boks, .bekreftelsesboks, .brodsmulesti, .appbar")]
    .filter((el) => el.scrollWidth > el.clientWidth + 1).map((el) => el.className);
  return {
    // clientWidth er bredden uten loddrett rullefelt. Med innerWidth ville inntil 15 px
    // vannrett overløp ikke synes når siden har rullefelt.
    sideBredde: document.documentElement.scrollWidth, vindu: document.documentElement.clientWidth,
    rullefelt: window.innerWidth - document.documentElement.clientWidth,
    sideRuller: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    klippet, utenfor, overløp,
  };
})()`;

function sjekkFlate(navn, m) {
  sjekk(`${navn}: siden ruller ikke vannrett`, !m.sideRuller, `${m.sideBredde} av ${m.vindu} px${m.rullefelt ? `, loddrett rullefelt ${m.rullefelt} px` : ""}`);
  sjekk(`${navn}: ingenting klippet`, m.klippet.length === 0 && m.overløp.length === 0, { klippet: m.klippet, overløp: m.overløp });
  sjekk(`${navn}: alle handlinger innenfor vinduet`, m.utenfor.length === 0, m.utenfor);
}

// De faste kolonnene, målt i to rulleposisjoner: helt til høyre, og med ulempekolonnen
// rullet inn rett ved siden av «Kandidat». `elementFromPoint` viser hva som faktisk ligger
// øverst: midt i «Nr.» og «Kandidat» skal det være cellene selv, og midt i den synlige
// delen av hver annen celle skal det være den cellen, ikke en fast celle.
const MÅL_TABELL = `(() => {
  const b = document.querySelector(".rangeringstabell");
  // Hele tabellen i synsfeltet: med 700 px vindushøyde ligger de nederste radene ellers
  // under kanten, og der gir elementFromPoint ingen celle.
  b.scrollIntoView({ block: "start" });
  const før = { scrollWidth: b.scrollWidth, clientWidth: b.clientWidth };
  const rader = [...b.querySelectorAll("tr")];
  const rot = getComputedStyle(document.documentElement);
  const tokenPx = parseFloat(rot.getPropertyValue("--rank-column-width")) * parseFloat(rot.fontSize);
  const førsteBredde = rader[0].children[0].getBoundingClientRect().width;
  const kandidatTokenPx = parseFloat(rot.getPropertyValue("--candidate-column-width")) * parseFloat(rot.fontSize);
  const andreBredde = rader[0].children[1].getBoundingClientRect().width;
  const br = b.getBoundingClientRect();
  const innenfor = (celle, x, y) => { const el = document.elementFromPoint(x, y); return !!el && celle.contains(el); };
  const midt = (r) => (r.top + r.bottom) / 2;
  const s = (el) => getComputedStyle(el);
  const mål = () => rader.map((tr) => {
    const [nr, kandidat, ...andre] = tr.children;
    const rn = nr.getBoundingClientRect(), rk = kandidat.getBoundingClientRect();
    const fastHøyre = rk.right;
    // Den synlige delen av hver celle til høyre for de faste: midtpunktet skal være cellen selv.
    const overlapp = andre.filter((c) => {
      const r = c.getBoundingClientRect();
      const v = Math.max(r.left, fastHøyre + 1), h = Math.min(r.right, br.right - 1);
      return h - v > 2 && !innenfor(c, (v + h) / 2, midt(r));
    }).map((c) => c.cellIndex);
    const ru = tr.children[5].getBoundingClientRect();
    return {
      tekst: kandidat.innerText.split("\\n")[0],
      nrVenstre: Math.round(rn.left - br.left - b.clientLeft),
      gapNrKandidat: Math.round((rk.left - rn.right) * 10) / 10,
      fasteØverst: innenfor(nr, (rn.left + rn.right) / 2, midt(rn)) && innenfor(kandidat, (rk.left + rk.right) / 2, midt(rk)),
      overlapp,
      ulempeHelt: ru.left >= fastHøyre - 0.5 && ru.right <= br.right - b.clientLeft + 0.5,
      nrBg: s(nr).backgroundColor, kandidatBg: s(kandidat).backgroundColor,
      rowAlt: tr.classList.contains("row-alt"), th: nr.tagName === "TH",
      kantHøyre: s(kandidat).borderRightStyle + " " + s(kandidat).borderRightWidth + " " + s(kandidat).borderRightColor,
      nrKlippet: nr.scrollWidth > nr.clientWidth + 1 || [...nr.querySelectorAll("*")].some((e) => e.getBoundingClientRect().right > rn.right + 0.5),
    };
  });
  b.scrollLeft = b.scrollWidth;
  const helt = { scrollLeft: b.scrollLeft, rader: mål() };
  // Rull tilbake til ulempekolonnen starter der «Kandidat» slutter.
  const u = rader[1].children[5].getBoundingClientRect(), k = rader[1].children[1].getBoundingClientRect();
  b.scrollLeft = b.scrollLeft + (u.left - k.right);
  const ulempe = { scrollLeft: b.scrollLeft, rader: mål() };
  b.scrollLeft = b.scrollWidth;
  const farge = (v) => { const d = document.createElement("span"); d.style.color = "var(" + v + ")"; document.body.append(d); const c = getComputedStyle(d).color; d.remove(); return c; };
  return {
    før, tokenPx, førsteBredde, kandidatTokenPx, andreBredde, helt, ulempe,
    farger: { panel: farge("--color-bg-panel"), alt: farge("--color-row-alt"), header: farge("--color-column-header-bg"), border: farge("--color-border") },
  };
})()`;

function sjekkTabell(navn, t, ulempeHeltVedHøyre) {
  sjekk(`${navn}: tabellen ruller i beholderen`, t.før.scrollWidth > t.før.clientWidth && t.helt.scrollLeft > 0, t.før);
  sjekk(`${navn}: «Nr.» er like bred som tokenet`, Math.abs(t.førsteBredde - t.tokenPx) <= 0.5, `${t.førsteBredde} mot ${t.tokenPx} px`);
  sjekk(`${navn}: «Kandidat» er like bred som tokenet`, Math.abs(t.andreBredde - t.kandidatTokenPx) <= 0.5, `${t.andreBredde} mot ${t.kandidatTokenPx} px`);
  for (const [hvor, m] of [["rullet helt til høyre", t.helt], ["rullet til ulempekolonnen", t.ulempe]]) {
    const rader = m.rader;
    sjekk(`${navn}, ${hvor}: «Nr.» står ytterst til venstre i hver rad`, rader.every((r) => r.nrVenstre === 0), rader.map((r) => r.nrVenstre));
    sjekk(`${navn}, ${hvor}: «Kandidat» følger rett etter «Nr.»`, rader.every((r) => Math.abs(r.gapNrKandidat) <= 0.5), rader.map((r) => r.gapNrKandidat));
    sjekk(`${navn}, ${hvor}: de faste cellene ligger øverst`, rader.every((r) => r.fasteØverst));
    sjekk(`${navn}, ${hvor}: ingen synlig celle dekkes av de faste`, rader.every((r) => r.overlapp.length === 0), rader.map((r) => r.overlapp));
  }
  sjekk(`${navn}: ulempekolonnen helt synlig ved siden av «Kandidat»`, t.ulempe.rader.every((r) => r.ulempeHelt), `scrollLeft ${t.ulempe.scrollLeft}`);
  const ulempeHelt = t.helt.rader.every((r) => r.ulempeHelt);
  if (ulempeHeltVedHøyre) sjekk(`${navn}, rullet helt til høyre: ulempe og preferanse står ved siden av de faste`, ulempeHelt);
  else console.log(`[INFO] ${navn}, rullet helt til høyre: ulempekolonnen ${ulempeHelt ? "helt synlig" : "delvis under de faste kolonnene"}`);
  const rader = t.helt.rader;
  const bgOk = rader.every((r) => {
    const forventet = r.th ? t.farger.header : r.rowAlt ? t.farger.alt : t.farger.panel;
    return r.nrBg === forventet && r.kandidatBg === forventet;
  });
  sjekk(`${navn}: ugjennomsiktig bakgrunn som følger raden`, bgOk, rader.map((r) => `${r.th ? "th" : r.rowAlt ? "alt" : "-"} ${r.nrBg}`).join(" | "));
  sjekk(`${navn}: skillelinje til høyre for «Kandidat»`,
    rader.every((r) => r.kantHøyre === `solid 1px ${t.farger.border}`), rader[0].kantHøyre);
  sjekk(`${navn}: totalscoren i «Nr.» klippes ikke`, rader.every((r) => !r.nrKlippet));
}

try {
  // 1. Alle fire flatene ved 1600, 1080, 960 og 680 px, og 680 px med «Stor» skrift (20 px).
  for (const [px, skrift] of [[1600, 16], [1080, 16], [960, 16], [680, 16], [680, 20]]) {
    const n = `${px} px/${skrift}`;
    await bredde(px, skrift);
    await loggInn();
    sjekkFlate(`Logg inn ${n}`, await ev(MÅL_FLATE));
    if (px !== 1600 && skrift === 16) await bilde(`logg-inn-${px}`);
    await sendInnlogging();
    sjekkFlate(`Vaktvalg ${n}`, await ev(MÅL_FLATE));
    if (px !== 1600 && skrift === 16) await bilde(`vaktvalg-${px}`, true); // Vaktvalg er lang: bare synsfeltet.

    await gåTil("/vakt/4127/kandidater", `document.querySelector(".rangeringstabell tbody tr")`);
    sjekkFlate(`Kandidatflate ${n}`, await ev(MÅL_FLATE));
    const navn = await ev(`[...document.querySelectorAll(".rangeringstabell tbody .ansattnavn")].map((e) => e.innerText)`);
    sjekk(`Kandidatflate ${n}: #4127 Jonas, Mette, Thomas, Ingrid`, navn.join(",") === "Jonas Bakke,Mette Solberg,Thomas Nygård,Ingrid Dahl", navn.join(", "));
    // Med fast bredde på «Kandidat» får tabellen plass uten rulling også ved 1080 px.
    const tabellRuller = await ev(`(() => { const b = document.querySelector(".rangeringstabell"); return b.scrollWidth > b.clientWidth; })()`);
    if (px === 1600 || (px === 1080 && !tabellRuller)) {
      const b = await ev(`(() => { const b = document.querySelector(".rangeringstabell"); return { scrollWidth: b.scrollWidth, clientWidth: b.clientWidth, kolonner: b.querySelectorAll("thead th").length }; })()`);
      sjekk(`Kandidatflate ${n}: alle ${b.kolonner} kolonner synlige uten rulling i tabellen`, b.scrollWidth <= b.clientWidth && b.kolonner === 8, b);
      if (skrift === 16) await bilde(`kandidatflate-${px}`);
    } else {
      if (skrift === 16) await bilde(`kandidatflate-${px}`);
      const tabell = await ev(MÅL_TABELL);
      sjekkTabell(`Kandidatflate ${n}`, tabell, skrift === 16);
      if (px === 680 && skrift === 16) {
        // Det verste tilfellet AC3 skal tåle: smalt vindu med loddrett rullefelt på siden.
        const felt = await ev(`window.innerWidth - document.documentElement.clientWidth`);
        sjekk(`Kandidatflate ${n}: siden har loddrett rullefelt, så kontrollen over gjelder det trangeste tilfellet`, felt > 0, `${felt} px`);
        // Tidlig varsel for Epic 5 (ikke et krav i 4.6): legg «Skjul begrunnelse ▴» inn i
        // siste kolonne og regn ut hvor mye plass som er igjen ved siden av de faste.
        const e5 = await ev(`(() => {
          const b = document.querySelector(".rangeringstabell");
          const lagt = [...b.querySelectorAll("tbody tr")].map((tr) => { const s = document.createElement("span"); s.className = "link"; s.textContent = " Skjul begrunnelse ▴"; tr.lastElementChild.append(s); return s; });
          const th = [...b.querySelectorAll("thead th")].map((c) => c.getBoundingClientRect().width);
          const igjen = b.clientWidth - th[0] - th[1] - th.slice(5).reduce((a, x) => a + x, 0);
          lagt.forEach((s) => s.remove());
          return Math.round(igjen);
        })()`);
        console.log(`[INFO] ${n}: med en simulert Epic 5-lenke i siste kolonne er det ${e5} px til overs ved siden av de faste kolonnene, rullet helt til høyre`);
      }
      await bilde(skrift === 16 ? `kandidatflate-${px}-rullet` : `kandidatflate-${px}-stor-skrift-rullet`);
      if (skrift === 20) {
        // Med større skrift går ulempekolonnen delvis under de faste når tabellen er rullet
        // helt til høyre. Bildet viser at den kan rulles fram helt, ved siden av «Kandidat».
        await ev(`document.querySelector(".rangeringstabell").scrollLeft = ${tabell.ulempe.scrollLeft}`);
        await bilde(`kandidatflate-${px}-stor-skrift-ulempe`);
      }
    }

    await gåTil("/vakt/4127/godkjenning/5", `document.querySelector(".avviksnotat")`);
    sjekkFlate(`Godkjenning (Mette) ${n}`, await ev(MÅL_FLATE));
    const g = await ev(`(() => {
      const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right)]; };
      return { kort: r(".kandidatkort"), avvik: r(".avviksnotat"), bekreft: r(".bekreftelsesboks"), vindu: window.innerWidth };
    })()`);
    sjekk(`Godkjenning (Mette) ${n}: kort, avviksnotat og bekreftelse innenfor vinduet`,
      [g.kort, g.avvik, g.bekreft].every((x) => x && x[0] >= 0 && x[1] <= g.vindu), g);
    if (px !== 1600 && skrift === 16) await bilde(`godkjenning-mette-${px}`);
    if (skrift === 20) await bilde("godkjenning-mette-680-stor-skrift");
  }

  // 2. Tastatur ved 680 px: tab fra tabellbeholderen gjennom Velg-knappene. Knappen med
  //    fokus skal stå til høyre for de faste kolonnene, med synlig fokusramme.
  await bredde(680);
  await gåTil("/vakt/4127/kandidater", `document.querySelector(".rangeringstabell tbody tr")`);
  await ev(`document.querySelector(".rangeringstabell").focus()`);
  await tast("Tab", "Tab", 9); await tast("Tab", "Tab", 9, 8); // tastaturfokus, så :focus-visible gjelder
  const fokus = [];
  const MÅL_FOKUS = `(() => {
    const el = document.activeElement, s = getComputedStyle(el), r = el.getBoundingClientRect();
    const b = document.querySelector(".rangeringstabell").getBoundingClientRect();
    const tr = el.closest("tr");
    const fastHøyre = tr ? tr.children[1].getBoundingClientRect().right : b.left;
    const ramme = parseFloat(s.outlineWidth) + parseFloat(s.outlineOffset);
    return {
      etikett: el.getAttribute("aria-label") ?? el.className, synlig: el.matches(":focus-visible"),
      outline: s.outlineStyle + " " + s.outlineWidth,
      fri: r.left - ramme >= fastHøyre - 0.5 && r.right + ramme <= b.right + 0.5,
    };
  })()`;
  fokus.push(await ev(MÅL_FOKUS));
  for (let i = 0; i < 4; i++) { await tast("Tab", "Tab", 9); await vent(150); fokus.push(await ev(MÅL_FOKUS)); }
  for (let i = 0; i < 3; i++) { await tast("Tab", "Tab", 9, 8); await vent(150); fokus.push(await ev(MÅL_FOKUS)); }
  sjekk("Tastatur 680 px: fokus synlig på beholderen og hver Velg", fokus.every((f) => f.synlig && f.outline.startsWith("solid")), fokus.map((f) => f.etikett).join(" | "));
  sjekk("Tastatur 680 px: fokusrammen skjules ikke av de faste kolonnene", fokus.slice(1).every((f) => f.fri), fokus.map((f) => f.fri));
  await bilde("kandidatflate-680-fokus-velg");

  // 3. Endret vindusbredde med «Vis alle» og «Vis full liste» åpne. Seeden har bare fire
  //    gyldige på #4127, så svaret utvides i nettleseren med tre konstruerte rader
  //    («Konstruert kandidat 1–3», plass 5–7). Alle kall telles.
  const { result: skript } = await cdp("Page.addScriptToEvaluateOnNewDocument", { source: `
    window.__kall = [];
    const ekte = window.fetch.bind(window);
    window.fetch = async (input, init) => {
      const url = String(input instanceof Request ? input.url : input), metode = (init && init.method) || "GET";
      window.__kall.push(metode + " " + url);
      const svar = await ekte(input, init);
      if (metode === "GET" && /\\/api\\/vakter\\/4127\\/kandidater$/.test(url) && svar.ok) {
        const data = await svar.clone().json();
        if (data.status === "ok") {
          const mal = data.kandidater[data.kandidater.length - 1];
          for (const n of [1, 2, 3]) data.kandidater.push({ ...mal, id: 900 + n, navn: "Konstruert kandidat " + n, plass: mal.plass + n, totalscore: mal.totalscore - n });
          return new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } });
        }
      }
      return svar;
    };` });
  await bredde(1600);
  await gåTil("/vakt/4127/kandidater", `document.querySelectorAll(".rangeringstabell tbody tr").length === 5`);
  await ev(`[...document.querySelectorAll("button")].find((b) => b.innerText === "Vis alle gyldige kandidater").click()`);
  await ev(`[...document.querySelectorAll(".ekskludert-boks button")][0].click()`);
  const MÅL_TILSTAND = `(() => ({
    sti: location.pathname,
    rader: document.querySelectorAll(".rangeringstabell tbody tr").length,
    visAlle: [...document.querySelectorAll(".vis-alle button")].map((b) => b.getAttribute("aria-expanded")).join(),
    fullListe: document.querySelector(".ekskludert-boks button").getAttribute("aria-expanded"),
    utelukkede: document.querySelectorAll(".ekskludert-liste li").length,
    kall: window.__kall.length,
  }))()`;
  const start = await ev(MÅL_TILSTAND);
  const underveis = [];
  for (const px of [1080, 960, 680, 1600]) { await bredde(px); underveis.push({ px, ...(await ev(MÅL_TILSTAND)) }); }
  sjekk("Vindusendring: «Vis alle» og «Vis full liste» åpne og samme rader, uten ny henting",
    start.rader === 7 && start.visAlle === "true" && start.fullListe === "true" &&
    underveis.every((u) => u.sti === start.sti && u.rader === 7 && u.visAlle === "true" && u.fullListe === "true" && u.utelukkede === start.utelukkede && u.kall === start.kall),
    { start, underveis });
  await bredde(680);
  await bilde("kandidatflate-680-vis-alle-og-full-liste");

  await gåTil("/vakt/4127/godkjenning/5", `document.querySelector(".avviksnotat")`);
  await bredde(1600);
  const gStart = await ev(`({ sti: location.pathname, navn: document.querySelector(".kandidatkort h3").innerText, kall: window.__kall.length })`);
  const gUnderveis = [];
  for (const px of [680, 1600]) {
    await bredde(px);
    gUnderveis.push(await ev(`({ sti: location.pathname, navn: document.querySelector(".kandidatkort h3")?.innerText, avvik: !!document.querySelector(".avviksnotat"), kall: window.__kall.length })`));
  }
  sjekk("Vindusendring: valgt kandidat og avviksnotat på Godkjenning står, uten ny henting",
    gUnderveis.every((u) => u.sti === gStart.sti && u.navn === "Mette Solberg" && u.avvik && u.kall === gStart.kall), { gStart, gUnderveis });
  await cdp("Page.removeScriptToEvaluateOnNewDocument", { identifier: skript.identifier });

  sjekk("Ingen konsollfeil", konsollfeil.length === 0, konsollfeil);
} catch (e) {
  console.error("UVENTET FEIL:", e);
  feil.push("uventet feil: " + e.message);
}

console.log(feil.length ? `\nFeilet: ${feil.join("; ")}` : "\nAlle kontroller besto.");
ws.close();
process.exit(feil.length ? 1 : 0);
