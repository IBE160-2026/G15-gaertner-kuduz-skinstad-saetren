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
  loggUt: "Logg ut",
  sesjonUtlopt: "Sesjonen er utløpt. Logg inn på nytt.",
  utloggingFeilet: "Fikk ikke bekreftet utloggingen. Prøv igjen.",
  provIgjen: "Prøv igjen",
  sideIkkeFunnet: "Fant ikke siden.",
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

  // Vaktvalg (story 1.5, UX-DR5, UX-DR6, UX-DR23).
  vaktvalg: {
    overskrift: "Vaktvalg",
    laster: "Henter vaktene …",
    kreverHandling: "Krever handling",
    ingenKreverHandling: "Ingen vakter krever handling nå",
    bemannet: "Øvrige vakter denne perioden — bemannet",
    ingenBemannet: "Ingen bemannede vakter i perioden",
    velgVakt: "Velg vakt — finn erstatter →",
    statusBemannet: "Bemannet",
    kolonner: { vakt: "Vakt", dato: "Dato", tid: "Tid", ansatt: "Ansatt", status: "Status" },
    vaktoverskrift: (nr: number, vakttype: string, avdeling: string) =>
      `Vakt #${nr} — ${vakttype}, ${avdeling}`,
    vaktnummer: (nr: number) => `#${nr}`,
    ansattMeta: (stilling: string, ansiennitet: number) => `${stilling} · ${ansiennitet} år ansiennitet`,
    fotnote: (oppdatert: string, antall: number) =>
      `Turnus oppdatert ${oppdatert} · ${antall} ansatte totalt i avdelingen`,
  },

  kandidatflate: {
    overskrift: (nummer: number) => `Vakt #${nummer}`,
    laster: "Henter vakten …",
    brodsmule: (nummer: number, vakttype: string, dato: string) => `Vakt #${nummer} — ${vakttype} ${dato}`,
    avdeling: "Avdeling",
    vakttype: "Vakttype",
    tidspunkt: "Tidspunkt",
    start: (tid: string) => `Start: ${tid}`,
    slutt: (tid: string) => `Slutt: ${tid}`,
    kompetanse: "Kompetansekrav",
    minstenivaa: (nivaa: number) => `Minstenivå ${nivaa} av 4`,
    // Kandidatlisten (story 2.1).
    kandidaterOverskrift: "Gyldige kandidater",
    // Tom liste (story 2.4, beslutning B). Story 2.6 erstatter den med tomtilstanden.
    ingenGyldige: "Ingen gyldige kandidater for denne vakten.",
    kandidaterLaster: "Henter kandidatene …",
    nivaaTag: (nivaa: number) => `Nivå ${nivaa}/4`,
    datafeil: "Kan ikke beregne kandidater fordi nødvendig turnusgrunnlag mangler.",
    datagrense: (tid: string) => `Turnusgrunnlaget går til ${tid}.`,
  },

  // Ekskludert-boksen (story 2.5, UX-DR15). Egen mal per årsak: grammatikken er
  // ulik per regel («kolliderende vakt» har ikke «brudd på»). Nøkkelen er
  // regelmotorens eksakte årsaksstreng, ikke en generert tekst.
  ekskludertBoks: {
    totaltUtelukket: (n: number) => `${n} utelukket av harde regler`,
    // Pil-glyfen rendres for seg i et `aria-hidden`-element (som Brodsmulesti og
    // Vaktvalg gjør for andre dekorative tegn), så denne teksten er bare det
    // skjermlesere skal lese opp.
    visFullListe: "Vis full liste",
    skjulFullListe: "Skjul full liste",
    årsaksmaler: {
      "kompetanse-minstekrav": (n: number) => `${n} under kompetanse-minstekrav`,
      "kolliderende vakt": (n: number) => `${n} kolliderende vakt`,
      "11-timersregelen": (n: number) => `${n} brudd på 11-timersregelen`,
      "35-timersregelen": (n: number) => `${n} brudd på 35-timersregelen`,
    } as Record<string, (n: number) => string>,
  },

  brodsmulesti: {
    etikett: "Brødsmulesti",
    turnus: "Turnus",
  },

  // Byggesteiner for format.ts.
  format: {
    ukedager: ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"],
    vakttyper: { dag: "Dagvakt", mellom: "Mellomvakt", kveld: "Kveldsvakt", natt: "Nattevakt" },
    timer: "t",
    kl: "kl.",
    uke: "Uke",
    meldtFra: "meldt fra",
    manglerBemanning: "Mangler bemanning",
  },
} as const;
