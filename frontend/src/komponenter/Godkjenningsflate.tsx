import { useEffect, useRef, useState, type MouseEvent } from "react";
import { datoOgKlokke, datoOgTidsrom, vaktlinje, vakttypenavn } from "../format";
import { lastGodkjenning, type Godkjenningstilstand } from "../godkjenning";
import { kandidatsti } from "../navigasjon";
import { TEKSTER } from "../tekster";
import Brodsmulesti from "./Brodsmulesti";

const t = TEKSTER.godkjenning;

type Props = {
  vaktnummer: number;
  ansattId: number;
  /** Til kandidatflaten for vakten, uten kall til API-et. */
  onTilbake: () => void;
};

// Egen flate med egen URL, ikke en dialog (UX-DR17). Første steg i den
// to-stegs godkjenningen: ingenting skrives før story 3.2 (FR12).
export default function Godkjenningsflate({ vaktnummer, ansattId, onTilbake }: Props) {
  const [tilstand, setTilstand] = useState<Godkjenningstilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const [trykket, setTrykket] = useState(false);
  const retryknapp = useRef<HTMLButtonElement>(null);

  useEffect(() => lastGodkjenning(vaktnummer, ansattId, setTilstand), [vaktnummer, ansattId, forsok]);

  useEffect(() => {
    if (tilstand.type === "feil") retryknapp.current?.focus();
  }, [tilstand]);

  // Vanlig lenke, så den kan åpnes i ny fane. Et vanlig klikk blir i appen.
  function tilbakeVedKlikk(e: MouseEvent<HTMLAnchorElement>) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    onTilbake();
  }
  const tilbakelenke = (
    <p className="godkjenning-tilbake">
      <a className="lenke" href={kandidatsti(vaktnummer)} onClick={tilbakeVedKlikk}>{t.tilbake}</a>
    </p>
  );

  if (tilstand.type === "avvist") return null;
  if (tilstand.type === "laster") return (
    <main className="innhold">
      <h1 className="visuelt-skjult">{t.overskrift}</h1>
      <p className="meta" role="status">{t.laster}</p>
    </main>
  );
  if (tilstand.type === "ikke_funnet") return (
    <main className="innhold"><section className="panel" role="alert">
      <h1 className="overskrift">{t.ikkeFunnet}</h1>
      {tilbakelenke}
    </section></main>
  );
  if (tilstand.type === "feil") return (
    <main className="innhold"><section className="panel" role="alert">
      <h1 className="visuelt-skjult">{t.overskrift}</h1>
      <p className="brodtekst">{tilstand.tekst}</p>
      <button ref={retryknapp} type="button" className="button-secondary" onClick={() => setForsok((n) => n + 1)}>
        {TEKSTER.provIgjen}
      </button>
    </section></main>
  );
  // Datafeil: ingen knapper for godkjenning (P-08).
  if (tilstand.type === "datafeil") return (
    <main className="innhold"><section className="panel datafeil" role="alert">
      <h1 className="overskrift">{t.overskrift}</h1>
      <p className="brodtekst datafeil-tekst">{t.datafeil}</p>
      <p className="meta">{t.datagrense(datoOgKlokke(tilstand.datagrense))}</p>
      {tilbakelenke}
    </section></main>
  );

  const { vakt, kandidat } = tilstand;
  const vakttype = vakttypenavn(vakt.vakttype);
  return <>
    <Brodsmulesti ledd={[
      { tekst: TEKSTER.brodsmulesti.turnus },
      { tekst: vakt.avdeling },
      { tekst: t.brodsmuleVakt(vakt.vaktnummer) },
      { tekst: t.brodsmuleKandidater },
      { tekst: t.brodsmuleGodkjenning, uthevet: true },
    ]} />
    <main className="innhold godkjenningsflate">
      <section className="panel vaktlinje">
        <div>
          <h1 className="overskrift">{t.vaktoverskrift(vakt.vaktnummer, vakttype, vakt.avdeling)}</h1>
          <p className="meta">{vaktlinje(vakt.start, vakt.slutt)}</p>
        </div>
        <span className="tag">{t.minstenivaa(vakt.minstenivå)}</span>
      </section>

      <h2 className="section-label">{t.valgtKandidat}</h2>
      <section className="panel kandidatkort" aria-labelledby="kandidatkort-navn">
        <h3 id="kandidatkort-navn" className="overskrift">{kandidat.navn}</h3>
        <p className="meta">{t.kompetanse}</p>
        <span className="tag">{t.nivaaTag(kandidat.kompetansenivå)}</span>
      </section>

      <section className="panel bekreftelsesboks" aria-labelledby="bekreft-tittel">
        <h2 id="bekreft-tittel" className="overskrift">{t.bekreftOverskrift}</h2>
        <p className="brodtekst">
          {t.bekreft.foer}<b>{kandidat.navn}</b>{t.bekreft.inn}<b>{t.bekreft.vakt(vakt.vaktnummer)}</b>
          {t.bekreft.etter(vakttype, datoOgTidsrom(vakt.start, vakt.slutt))}
          {t.bekreft.ingenEndring}<b>{t.godkjenn}</b>{t.bekreft.slutt}
        </p>
        <div className="bekreftelse-handlinger">
          <button type="button" className="button-secondary" onClick={onTilbake}>{t.avbryt}</button>
          {/* Beslutning 2A: aktiv før story 3.2, men uten kall til API-et. */}
          <button type="button" className="button-primary button-kompakt" onClick={() => setTrykket(true)}>
            {t.godkjenn}
          </button>
        </div>
        <p className="meta bekreftelse-melding" role="status">{trykket ? t.ikkeLagret : ""}</p>
      </section>
      <p className="meta statuslinje">{t.statuslinje}</p>
    </main>
  </>;
}
