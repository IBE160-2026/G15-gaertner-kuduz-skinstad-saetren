# Handoff: komponenttester for frontend

**Laget:** 2026-11-14 av Johannes W. Gaertner (med Claude Code), etter vurdering og prøveoppsett i økten
[984-…-bards-tilbakemelding-prd-og-arkitektur](../../.logs/johagartnerhimolde/984-2026-11-14-10-10-03-bards-tilbakemelding-prd-og-arkitektur.md).
**Til:** en ny økt i et nytt kontekstvindu. Les hele fila før du gjør noe.

## Mål

Innfør automatiske komponenttester for frontend, med to hensikter:

1. **Spare tid og unngå diskusjoner.** I dag kontrolleres koblingen i komponentene for hånd i
   nettleseren i hver story, og feil oppdages sent, ofte i PR-gjennomgang hos et annet
   gruppemedlem (Kims funn om «Avbryt» i PR #16 er et eksempel). Tester skal erstatte så mye
   av den manuelle kontrollen som mulig, og fange feil før PR.
2. **Bedre dokumentasjon av testing.** Kriterium 3 i [sensorveiledningen](../../docs/emne/sensorveiledning-del-1.md)
   (Kvalitetssikring og testing, 15 %) gir A–B når testene «dekker sentral logikk» og kvalitetssikringen er
   «systematisk og dokumentert», og C når «dekningen er ujevn». Backend er sterk. Frontend er det svake punktet.
   Sensor ser også etter «dokumenterte manuelle tester eller testplaner der automatiske tester ikke er hensiktsmessige».

**Arbeidet gjøres i en egen branch med PR** (Johannes' valg). Det binder hele gruppa (nytt felles
oppsett og ny testkonvensjon), så etter Policy i AGENTS.md skal et annet gruppemedlem gå gjennom PR-en.

## Slik starter du

1. Les `AGENTS.md`, denne fila, `docs/emne/sensorveiledning-del-1.md` (kriterium 3) og
   `_bmad-output/implementation-artifacts/deferred-work.md`.
2. `git pull` på `main`, og opprett branchen `frontend-komponenttester` (navnet kan endres).
   Denne fila er ikke committet. Ta den med i første commit på branchen.
3. Kjør `bmad-build` med denne fila som oppgave. AGENTS.md krever underagenter: én samler kontekst,
   og egne agenter gjennomgår koden uten å ha sett implementeringen.
4. Avklar spørsmålene under «Beslutninger» med Johannes før spesifikasjonen godkjennes.

## Dagens tilstand (2026-11-14, `main` på `589aba5`)

- **Backend:** 412 pytest-tester, én testmodul per hard regel, import-linter for AD-1/AD-2.
- **Frontend:** `npm run test` kjører `node --test`, som finner `tester/*.test.mjs`. Det er 4 testfiler
  (`sesjon`, `format`, `kandidater`, `godkjenning`) med 48 tester. De tester bare rene moduler
  (`src/*.ts`) med en falsk `fetch`, og bunter TypeScript med `rolldown` til en `data:`-URL
  (`tester/kandidater-bunt.ts`, `tester/godkjenning-bunt.ts`). **Ingen test rendrer en komponent.**
- **CI:** `.github/workflows/frontend-tester.yml` kjører `npm ci`, `npm run build` og `npm run test`
  med Node 22.12 (laveste versjon vi lover) og `lts/*`. Endres `npm run test`, plukker CI det opp av seg selv.
- **Arkitektur:** Testing-raden i `ARCHITECTURE-SPINE.md` (linje ~111) nevner bare pytest.
- **README:** «### Tester» (linje ~232) beskriver `node --test` og lister testfilene.
- **Versjoner:** React 19.3.0, Vite 8.3.1, `@vitejs/plugin-react` 6.1.2, TypeScript 7.0.2, rolldown 1.2.14.
  Alle avhengigheter er låst eksakt i `package.json`.

## Utsatte punkter som skyldes manglende komponentrigg

Disse er i dag bare dekket av manuell nettleserkontroll, eller ikke i det hele tatt:

| Story | Hva mangler | Kilde |
|---|---|---|
| 1.5 | Feil-, «Prøv igjen»- og 401-tilstandene i `Vaktvalg`. Feiltilstanden er ikke kontrollert i nettleser heller | `deferred-work.md` l. ~5, spec 1.5 Review #11 |
| 2.1 | Tilstandene og «Prøv igjen» i `Kandidatliste`. Fjernes `forsok` fra `useEffect`, er alt grønt | `deferred-work.md` l. ~11 |
| 2.4 | Grenen for tom liste i `Kandidatliste`. En snudd betingelse (`!== 0`) går gjennom alle testene | `deferred-work.md` l. ~42 |
| 2.5 | Ingen Ekskludert-boks ved 0 utelukkede; «Vis full liste» lukket → åpen → lukket med `aria-expanded` | spec 2.5 Review Triage (avvist pga. manglende rigg) |
| 3.1 | «Velg» sender riktig id, ruten i `App` viser godkjenningsflaten, «Godkjenn erstatning» gjør ingen kall, datafeil og 404 viser ingen godkjenningsknapper, «Avbryt» går tilbake | `deferred-work.md` l. ~34, spec 3.1 VG1 |

Når et punkt er dekket av en test, oppdateres punktet i `deferred-work.md` (ikke slett, skriv at det er løst og hvor).

## Resultat fra prøveoppsettet (2026-11-14)

Prøvd i en kopi av `frontend/` utenfor repoet. Alt bestod.

| Pakke | Versjon | Merknad |
|---|---|---|
| `vitest` | 5.1.0 | peer: Vite ^6/^7/^8 |
| `@testing-library/react` | 16.3.3 | peer: React ^18/^19 |
| `@testing-library/dom` | 10.4.2 | |
| `@testing-library/user-event` | 14.6.10 | |
| `jsdom` | **28.1.0** | **Ikke 30 eller 31:** de krever Node ^22.22.2 og bryter løftet om Node 22.12. 28.1.0 krever ^22.12.0 |
| (alternativ) `happy-dom` | 21.0.4 | Node >=20. Raskere (2 mot 4 s), men mindre standardtro |

- Begge miljøene bestod på Node 26.7 og på Node 22.12 (`npx -y -p node@22.12.0 node node_modules/vitest/vitest.mjs run`).
- En mutasjon der «Godkjenn» hentet data på nytt, ga rød test («called 1 times, but got 2 times»).
- `tsc` (TS 7.0.2) godtok testfilene. `node --test` kjørte fortsatt bare de 48 gamle testene, og `npm run build` bestod.
- `npm ls` viste ingen ugyldige peer-avhengigheter, bare valgfrie som mangler.
- Johannes sa at kravet om Node 22.12 kan heves hvis det er enklere. Det er ikke nødvendig med jsdom 28.1.0.

Oppsettet som virket:

```ts
// frontend/vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    // Avgrenset, så Vitest ikke prøver å kjøre node:test-filene (*.test.mjs).
    include: ["tester/komponenter/**/*.test.tsx"],
  },
});
```

```tsx
// frontend/tester/komponenter/godkjenningsflate.test.tsx (prøveversjon)
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Godkjenningsflate from "../../src/komponenter/Godkjenningsflate";
import Kandidatflate from "../../src/komponenter/Kandidatflate";
import { TEKSTER } from "../../src/tekster";

const t = TEKSTER.godkjenning;
const SVAR = {
  status: "ok",
  vakt: { avdeling: "Kirurgisk sengepost", vaktnummer: 4127, vakttype: "dag",
    start: "2026-09-27T07:00:00+02:00", slutt: "2026-09-27T15:00:00+02:00", "minstenivå": 3 },
  kandidat: { id: 6, navn: "Jonas Bakke", "kompetansenivå": 3 },
};
const json = (k: unknown) => new Response(JSON.stringify(k), { status: 200, headers: { "Content-Type": "application/json" } });

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

test("Godkjenn gjør ingen kall og viser 2A-linjen; Avbryt kaller onTilbake", async () => {
  const fetch = vi.fn(async (_url: string) => json(SVAR));
  vi.stubGlobal("fetch", fetch);
  const onTilbake = vi.fn();
  render(<Godkjenningsflate vaktnummer={4127} ansattId={6} onTilbake={onTilbake} />);

  expect(await screen.findByRole("heading", { name: "Jonas Bakke" })).toBeTruthy();
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(String(fetch.mock.calls[0][0])).toBe("/api/vakter/4127/kandidater/6");

  await userEvent.click(screen.getByRole("button", { name: t.godkjenn }));
  expect(screen.getByRole("status").textContent).toBe(t.ikkeLagret);
  expect(fetch).toHaveBeenCalledTimes(1);

  await userEvent.click(screen.getByRole("button", { name: t.avbryt }));
  expect(onTilbake).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledTimes(1);
});

test("Velg i kandidatlisten sender riktig vakt og id", async () => {
  vi.stubGlobal("fetch", vi.fn(async (url: string) => String(url).endsWith("/kandidater")
    ? json({ status: "ok", kandidater: [{ id: 5, navn: "Mette Solberg", "kompetansenivå": 3 }, { id: 6, navn: "Jonas Bakke", "kompetansenivå": 3 }],
             utelukkelser: { totalt: 0, per_regel: [], utelukkede: [] } })
    : json(SVAR.vakt)));
  const onVelg = vi.fn();
  render(<Kandidatflate vaktnummer={4127} onVelg={onVelg} />);
  await userEvent.click(await screen.findByRole("button", { name: t.velgEtikett("Jonas Bakke") }));
  expect(onVelg).toHaveBeenCalledWith(4127, 6);
});
```

Merk: `/api/vakter/{nr}` svarer med et flatt `Vaktdetaljer`-objekt uten `status` (se `src/api.ts`).
Bruk typene i `src/api.ts` til testdataene, så feil form fanges av `tsc`.

## Foreslått omfang

**Del 1 – Oppsett**
- Installer pakkene over med `npm install -D -E` (eksakte versjoner). `package-lock.json` oppdateres.
- `vitest.config.ts` som over, og et `tsconfig` for testene (for eksempel `tsconfig.test.json` som
  utvider `tsconfig.json` og tar med `tester/komponenter`). Vurder at `npm run build` også typesjekker testene.
- `npm run test` kjører begge: for eksempel `"test": "node --test && vitest run"`. Én felles
  kommando, så README, CI og gruppa ikke må lære noe nytt. De 48 eksisterende testene flyttes **ikke** nå.
- Felles hjelpere i `tester/komponenter/` (for eksempel `json()`, falsk `fetch` per URL og testdata
  bygget på typene i `src/api.ts`), så nye tester blir korte.
- Kontroller at det virker på Node 22.12, i CI og lokalt på Windows (`npm.cmd`), og i Git Bash.

**Del 2 – Tester for de utsatte punktene**
Alle fem radene i tabellen over. Hver test skal kunne feile: gjør en mutasjon per test eller gruppe
(som i backend-storyene) og noter resultatet i KI-loggen. Det er det sterkeste beviset for sensor.

**Del 3 – Dokumentasjon (hensikt 2)**
- **En testoversikt**, for eksempel `docs/testing.md` (plassering avgjøres): hva som testes automatisk
  (backend per regel, API, frontend-logikk, komponenter) og hva som fortsatt er manuelt og hvorfor
  (layout og 360 px, farger og fokusmarkering, forståelsestesten i P-13). Med kommandoer og lenker til
  testfilene. Dette er «testplan der automatiske tester ikke er hensiktsmessige» fra sensorveiledningen.
- **En kortere manuell sjekkliste** for nettleserkontrollen i senere stories: bare det jsdom ikke kan.
  Det er det som sparer tid (hensikt 1). Vurder om «Manual checks» i spesifikasjonsmalen eller
  `bmad-build`-tilpasningen skal peke på den.
- README «### Tester», AGENTS.md «Kjøring og verifisering», Testing-raden i ARCHITECTURE-SPINE,
  `deferred-work.md`, vurderingsmatrisen (milepæl med lenker til bevis) og KI-logg
  `docs/ki-logg/<dato>-komponenttester.md`.
- Registrer arbeidet som **OP-16** i `docs/beslutninger/avklaringspunkter.md` (tabellen i §2 og en seksjon i §11).
  OP-15 er siste brukte. NB: ingen tom linje mellom tabellradene.

**Utenfor omfang nå:** Playwright/ende-til-ende i CI. Kan vurderes ved story 4.6 (smalere skjermer)
eller som røyktest før innlevering. Mithad brukte `playwright-core` i et eget skript i 2.5
(`docs/ki-logg/2026-11-13-ekskludert-boks/nettleserkontroll.mjs`) som kan være utgangspunkt.

## Beslutninger å avklare med Johannes

1. **jsdom 28.1.0 eller happy-dom 21.0.4?** Anbefaling: jsdom 28.1.0.
2. **Flytte de 48 eksisterende testene til Vitest?** Anbefaling: nei nå. Én kommando kjører begge.
3. **Omfang av del 2:** alle fem utsatte punkter (anbefalt, for hensikt 1), eller bare 3.1 og 2.4?
4. **Hvor testoversikten og den manuelle sjekklisten skal ligge.**
5. **Hvem i gruppa går gjennom PR-en.**

## Fallgruver

- PowerShell: bruk `npm.cmd` og `npx.cmd` (AGENTS.md).
- `node --test` uten argument finner alle `*.test.{js,mjs,cjs}` (kontroller om Node-versjonen også tar med `.ts`) rekursivt
  utenom `node_modules`. Vitest-filene må hete `*.test.tsx` og ligge der `include` peker, ellers kan
  verktøyene prøve å kjøre hverandres filer. Kontroller at `node --test` fortsatt gir 48 tester.
- Bruk `vi.stubGlobal("fetch", …)` og `vi.unstubAllGlobals()` + `cleanup()` i `afterEach`.
- `src/api.ts` har modulnivå-tilstand for sesjonsgenerasjonen (`nySesjonsgenerasjon`, l. ~97), og
  `App` bruker `window.history`. Tester som går på tvers av sesjon eller ruter må nullstille dette.
- Finn elementer etter rolle og tilgjengelig navn (`getByRole`) med tekstene fra `src/tekster.ts`,
  ikke CSS-klasser. Da følger testene UX-tekstene og tåler omstrukturering.
- jsdom gjør ingen layout. Ikke prøv å teste bredde, farger eller synlighet via CSS.
- Filene i arbeidstreet har CRLF. Python-skript som endrer filer bør bevare linjeskiftene.
- Kode og testtekster kan være på engelsk, men dokumentasjon, commit-meldinger og UI er på bokmål.
- Generert kode som måtte rettes, skal beskrives i commit-meldingen og i KI-loggen (Policy).

## Ferdig når

- `npm.cmd run test` kjører både de 48 gamle testene og de nye komponenttestene, og alt består
  lokalt og i CI på Node 22.12 og `lts/*`. `npm.cmd run build` består.
- De fem utsatte punktene (eller det avklarte omfanget) har tester som er vist å kunne feile.
- Testoversikten, den manuelle sjekklisten, README, AGENTS.md, arkitekturen, `deferred-work.md`,
  vurderingsmatrisen, OP-16 og KI-loggen er oppdatert.
- PR er opprettet (etter Johannes' valg) og gjennomgått av et annet gruppemedlem.
- Sesjonsloggen er skrevet og committet (`sesjonslogg`), og punktet om komponentrigg i
  `.logs/johagartnerhimolde/issues.md` er lukket.
