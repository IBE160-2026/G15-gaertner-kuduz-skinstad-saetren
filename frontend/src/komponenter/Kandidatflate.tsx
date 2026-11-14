import { useEffect, useRef, useState } from "react";
import {
  ApiFeil,
  gjeldendeSesjonsgenerasjon,
  hentVaktdetaljer,
  type UtelukkelsesOppsummering,
  type Vaktdetaljer,
} from "../api";
import { datoOgKlokke, vaktBrodsmule, vakttypenavn } from "../format";
import { ekskludertBoksTekst, ekskludertRadTekst, lastKandidater, type Kandidattilstand } from "../kandidater";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "../tekster";
import Brodsmulesti from "./Brodsmulesti";

type Tilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "ikke_funnet" }
  | { type: "feil"; tekst: string }
  | { type: "klar"; data: Vaktdetaljer };

const t = TEKSTER.kandidatflate;

type Props = {
  vaktnummer: number;
  /** Til godkjenningsflaten for Kandidaten (story 3.1). */
  onVelg: (vaktnummer: number, ansattId: number) => void;
};

export default function Kandidatflate({ vaktnummer, onVelg }: Props) {
  const [tilstand, setTilstand] = useState<Tilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const retryknapp = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    let aktiv = true;
    const generasjon = gjeldendeSesjonsgenerasjon();
    setTilstand({ type: "laster" });
    hentVaktdetaljer(vaktnummer).then(
      (data) => {
        if (aktiv && generasjon === gjeldendeSesjonsgenerasjon()) setTilstand({ type: "klar", data });
      },
      (feil: unknown) => {
        if (!aktiv || generasjon !== gjeldendeSesjonsgenerasjon()) return;
        if (feil instanceof ApiFeil && feil.status === 401) setTilstand({ type: "avvist" });
        else if (feil instanceof ApiFeil && feil.status === 404) setTilstand({ type: "ikke_funnet" });
        else setTilstand({ type: "feil", tekst: feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT });
      },
    );
    return () => { aktiv = false; };
  }, [vaktnummer, forsok]);

  useEffect(() => {
    if (tilstand.type === "feil") retryknapp.current?.focus();
  }, [tilstand]);

  if (tilstand.type === "avvist") return null;
  if (tilstand.type === "laster") return (
    <main className="innhold">
      <h1 className="visuelt-skjult">{t.overskrift(vaktnummer)}</h1>
      <p className="meta" role="status">{t.laster}</p>
    </main>
  );
  if (tilstand.type === "ikke_funnet") return (
    <main className="innhold"><section className="panel" role="alert">
      <h1 className="overskrift">{feiltekst("ikke_funnet")}</h1>
    </section></main>
  );
  if (tilstand.type === "feil") return (
    <main className="innhold"><section className="panel" role="alert">
      <h1 className="visuelt-skjult">{t.overskrift(vaktnummer)}</h1>
      <p className="brodtekst">{tilstand.tekst}</p>
      <button ref={retryknapp} type="button" className="button-secondary" onClick={() => setForsok((n) => n + 1)}>
        {TEKSTER.provIgjen}
      </button>
    </section></main>
  );

  const { data } = tilstand;
  return <>
    <Brodsmulesti ledd={[
      { tekst: TEKSTER.brodsmulesti.turnus },
      { tekst: data.avdeling },
      { tekst: vaktBrodsmule(data.vaktnummer, data.vakttype, data.start), uthevet: true },
    ]} />
    <main className="innhold kandidatflate">
      <h1 className="overskrift">{t.overskrift(data.vaktnummer)}</h1>
      <section className="panel" aria-label={t.overskrift(data.vaktnummer)}>
        <dl className="vaktdetaljer">
          <div><dt>{t.avdeling}</dt><dd>{data.avdeling}</dd></div>
          <div><dt>{t.vakttype}</dt><dd>{vakttypenavn(data.vakttype)}</dd></div>
          <div><dt>{t.tidspunkt}</dt><dd>{t.start(datoOgKlokke(data.start))}<br />{t.slutt(datoOgKlokke(data.slutt))}</dd></div>
          <div><dt>{t.kompetanse}</dt><dd>{t.minstenivaa(data.minstenivå)}</dd></div>
        </dl>
      </section>
      <Kandidatliste vaktnummer={data.vaktnummer} onVelg={(ansattId) => onVelg(data.vaktnummer, ansattId)} />
    </main>
  </>;
}

// Hentes automatisk når vakten er lastet (story 2.1). Bare Gyldige kandidater.
function Kandidatliste({ vaktnummer, onVelg }: { vaktnummer: number; onVelg: (ansattId: number) => void }) {
  const [tilstand, setTilstand] = useState<Kandidattilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const retryknapp = useRef<HTMLButtonElement>(null);

  useEffect(() => lastKandidater(vaktnummer, setTilstand), [vaktnummer, forsok]);

  useEffect(() => {
    if (tilstand.type === "feil") retryknapp.current?.focus();
  }, [tilstand]);

  if (tilstand.type === "avvist") return null;

  const overskrift = <h2 id="kandidater-tittel" className="overskrift">{t.kandidaterOverskrift}</h2>;

  if (tilstand.type === "laster") return (
    <section className="panel kandidater" aria-labelledby="kandidater-tittel">
      {overskrift}
      <p className="meta kandidater-status" role="status">{t.kandidaterLaster}</p>
    </section>
  );
  if (tilstand.type === "feil") return (
    <section className="panel kandidater" aria-labelledby="kandidater-tittel">
      {overskrift}
      <div role="alert">
        <p className="brodtekst kandidater-status">{tilstand.tekst}</p>
        <button ref={retryknapp} type="button" className="button-secondary" onClick={() => setForsok((n) => n + 1)}>
          {TEKSTER.provIgjen}
        </button>
      </div>
    </section>
  );
  if (tilstand.type === "datafeil") return (
    <section className="panel kandidater datafeil" aria-labelledby="kandidater-tittel">
      {overskrift}
      <div role="alert">
        <p className="brodtekst datafeil-tekst">{t.datafeil}</p>
        <p className="meta">{t.datagrense(datoOgKlokke(tilstand.datagrense))}</p>
      </div>
    </section>
  );

  // Tom liste: nøytral tekst i meta-stil til story 2.6 (beslutning B).
  if (tilstand.kandidater.length === 0) return (
    <section className="panel kandidater" aria-labelledby="kandidater-tittel">
      {overskrift}
      <p className="meta kandidater-status" role="status">{t.ingenGyldige}</p>
      <EkskludertBoks oppsummering={tilstand.utelukkelser} />
    </section>
  );

  return (
    <section className="panel kandidater" aria-labelledby="kandidater-tittel">
      {overskrift}
      <ul className="kandidatliste">
        {tilstand.kandidater.map((k) => (
          <li key={k.id}>
            <span className="ansattnavn">{k.navn}</span>
            <span className="tag">{t.nivaaTag(k.kompetansenivå)}</span>
            <button
              type="button" className="button-secondary button-kompakt"
              aria-label={TEKSTER.godkjenning.velgEtikett(k.navn)} onClick={() => onVelg(k.id)}
            >
              {TEKSTER.godkjenning.velg}
            </button>
          </li>
        ))}
      </ul>
      <EkskludertBoks oppsummering={tilstand.utelukkelser} />
    </section>
  );
}

// Ekskludert-boksen (story 2.5, UX-DR15). Vist bare når noen er utelukket, enten
// listen over Gyldige er tom (#4189) eller ikke (#4127).
const ek = TEKSTER.ekskludertBoks;

function EkskludertBoks({ oppsummering }: { oppsummering: UtelukkelsesOppsummering }) {
  const [åpen, setÅpen] = useState(false);

  if (oppsummering.totalt === 0) return null;

  return (
    <div className="ekskludert-boks">
      <p className="brodtekst">{ekskludertBoksTekst(oppsummering)}</p>
      <button type="button" className="button-secondary" aria-expanded={åpen} onClick={() => setÅpen((v) => !v)}>
        {åpen ? ek.skjulFullListe : ek.visFullListe} <span aria-hidden="true">{åpen ? "▴" : "▾"}</span>
      </button>
      {åpen && (
        <ul className="ekskludert-liste">
          {oppsummering.utelukkede.map((kandidat) => (
            <li key={kandidat.id}>{ekskludertRadTekst(kandidat)}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
