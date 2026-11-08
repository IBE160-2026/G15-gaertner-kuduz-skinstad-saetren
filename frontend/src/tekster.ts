// All brukertekst i frontend (UX-DR23). Feiltekster slås opp på API-ets `kode`;
// `melding` fra API-et vises aldri (AD-4).

export const FEILTEKSTER: Readonly<Record<string, string>> = {
  feil_innlogging: "Feil brukernavn eller passord",
  mangler_sesjon: "Du er ikke innlogget.",
  ugyldig_foresporsel: "Forespørselen ble avvist. Last siden på nytt.",
  ikke_funnet: "Fant ikke det du ba om.",
  metode_ikke_tillatt: "Forespørselen ble avvist. Last siden på nytt.",
  intern_feil: "Feil på serveren. Er testdataene lastet? Se README.",
};

export const RESERVETEKST = "Noe gikk galt. Prøv igjen.";
export const INGEN_KONTAKT = "Får ikke kontakt med serveren.";

export function feiltekst(kode: string): string {
  return Object.hasOwn(FEILTEKSTER, kode) ? FEILTEKSTER[kode] : RESERVETEKST;
}

export const TEKSTER = {
  merkevare: "TURNUSHJELPEREN",
  ikkeInnlogget: "Ikke innlogget",
  innlogget: (navn: string, avdeling: string) =>
    `Innlogget: ${navn} (turnusansvarlig) · Avdeling ${avdeling}`,

  loggInn: {
    overskrift: "Logg inn",
    undertekst: "Beslutningsstøtte for gjenbemanning av vakter. Kun for turnusansvarlig.",
    brukernavn: "Brukernavn",
    passord: "Passord",
    knapp: "Logg inn",
    rollenotat: {
      etikett: "Én rolle:",
      foer: " Turnushjelperen har i denne versjonen kun tilgang for ",
      rolle: "turnusansvarlig",
      etter: ". Ansatte logger ikke inn her og registrerer ikke egne preferanser selv.",
    },
    registrering: "Ingen selvbetjent registrering eller passordgjenoppretting i denne versjonen.",
  },

  // Hvilket passord som gjelder, fra GET /api/innloggingsinfo. Selve passordet
  // vises aldri.
  passordvarianter: {
    tilfeldig: {
      tag: "Testpassord",
      meta: "Laget tilfeldig av testdatakommandoen og står i terminalen.",
    },
    personlig: {
      tag: "Personlig passord",
      meta: "Valgt med TURNUSHJELPEREN_PASSORD.",
    },
    ingen: {
      tag: "Ingen bruker",
      meta: "Last testdataene først, se README.",
    },
  },

  startside: {
    overskrift: "Vaktoversikt",
    tekst: "Vaktoversikten kommer i en senere versjon.",
  },
} as const;
