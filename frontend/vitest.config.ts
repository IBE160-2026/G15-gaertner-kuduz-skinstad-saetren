import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

// Komponenttester (Vitest, Testing Library, jsdom). Utvider vite.config.ts, så
// plugins, alias og define er de samme i testene som i appen. De rene
// modultestene (tester/*.test.mjs) kjøres fortsatt av `node --test`.
// `npm run test` kjører begge.
export default mergeConfig(viteConfig, defineConfig({
  test: {
    environment: "jsdom",
    // Avgrenset, så Vitest ikke prøver å kjøre node:test-filene (*.test.mjs).
    include: ["tester/komponenter/**/*.test.tsx"],
    // Felles oppsett og opprydding for hver test.
    setupFiles: ["tester/komponenter/oppsett.ts"],
    // Over asyncUtilTimeout (5 s i oppsett.ts), så en treg maskin gir en
    // tydelig feil fra findBy… og ikke et tidsavbrudd for hele testen.
    testTimeout: 20_000,
    // Én testfil om gangen. jsdom bruker mye minne. På en maskin med 7,7 GB
    // RAM ga flere arbeidere ingen gevinst (17,2 mot 16,6 s), og fire samtidige
    // kjøringer feilet med tidsavbrudd. Med én arbeider besto de. Overstyres med
    // `npx vitest run --maxWorkers=4` på en sterk maskin (se docs/testing.md).
    maxWorkers: 1,
  },
}));
