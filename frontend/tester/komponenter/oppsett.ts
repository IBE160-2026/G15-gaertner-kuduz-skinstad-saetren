// Oppsett for alle komponenttester, registrert i `test.setupFiles` i
// vitest.config.ts. Gjelder hver testfil uten at den må importere noe.
import { afterEach, expect, vi } from "vitest";
import { cleanup, configure } from "@testing-library/react";
import { settSesjonsvarsler } from "../../src/api";
import { hentOgNullstillUventede } from "./hjelpere";

// Kjeden /api/meg → /api/vaktoversikt → innlogging kan ta mer enn standarden
// på 1000 ms når maskinen er under last.
configure({ asyncUtilTimeout: 5000 });

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  // App registrerer sesjonsvarsleren på modulnivå i src/api.ts.
  settSesjonsvarsler(null);
  // App leser og endrer stien. Neste test starter fra roten.
  window.history.replaceState(null, "", "/");
  expect(hentOgNullstillUventede(), "kall uten svar satt opp i testen").toEqual([]);
});
