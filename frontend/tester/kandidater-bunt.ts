// Inngang for kandidater.test.mjs. kandidater.ts og nySesjonsgenerasjon buntes
// sammen, så testen bytter sesjonsgenerasjonen som kandidater.ts faktisk leser.
export * from "../src/kandidater";
export { nySesjonsgenerasjon } from "../src/api";
