// Inngang for godkjenning.test.mjs. godkjenning.ts, nySesjonsgenerasjon og
// navigasjonen buntes sammen, så testen bytter sesjonsgenerasjonen som
// godkjenning.ts faktisk leser.
export * from "../src/godkjenning";
export { nySesjonsgenerasjon } from "../src/api";
export { godkjenningFraSti, godkjenningssti, kandidatsti, vaktnummerFraSti } from "../src/navigasjon";
export { datoOgTidsrom } from "../src/format";
