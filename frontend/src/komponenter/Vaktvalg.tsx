import { useEffect, useRef, useState } from "react";
import {
  ApiFeil, gjeldendeSesjonsgenerasjon, hentVaktoversikt,
  type BemannetVakt, type VaktSomManglerBemanning, type Vaktoversikt,
} from "../api";
import {
  datoOgKlokke, periodetekst, radklasser, tidsrom, ukedagOgDato, vakttypenavn, varsellinje,
} from "../format";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "../tekster";
import Brodsmulesti from "./Brodsmulesti";

type Props = { onVelgVakt: (vaktnummer: number) => void };

type Tilstand =
  | { type: "laster" }
  | { type: "feil"; tekst: string }
  // 401 er håndtert av sesjonsvarsleren i App (story 1.4).
  | { type: "avvist" }
  | { type: "klar"; data: Vaktoversikt };

const t = TEKSTER.vaktvalg;

// Vaktvalg (story 1.5, UX-DR5, UX-DR6). Erstatter plassholderen fra 1.3.
export default function Vaktvalg({ onVelgVakt }: Props) {
  const [tilstand, setTilstand] = useState<Tilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const retryknapp = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    let aktiv = true;
    const generasjon = gjeldendeSesjonsgenerasjon();
    setTilstand({ type: "laster" });
    hentVaktoversikt().then(
      (data) => {
        if (aktiv && generasjon === gjeldendeSesjonsgenerasjon()) setTilstand({ type: "klar", data });
      },
      (feil: unknown) => {
        if (!aktiv || generasjon !== gjeldendeSesjonsgenerasjon()) return;
        if (feil instanceof ApiFeil && feil.status === 401) {
          setTilstand({ type: "avvist" });
          return;
        }
        setTilstand({ type: "feil", tekst: feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT });
      },
    );
    return () => {
      aktiv = false;
    };
  }, [forsok]);

  useEffect(() => {
    if (tilstand.type === "feil") retryknapp.current?.focus();
  }, [tilstand]);

  if (tilstand.type === "avvist") return null;

  if (tilstand.type === "laster") {
    return (
      <main className="innhold">
        <h1 className="visuelt-skjult">{t.overskrift}</h1>
        <p className="meta" role="status">{t.laster}</p>
      </main>
    );
  }

  if (tilstand.type === "feil") {
    return (
      <main className="innhold">
        <h1 className="visuelt-skjult">{t.overskrift}</h1>
        <section className="panel" role="alert">
          <p className="brodtekst">{tilstand.tekst}</p>
          <button ref={retryknapp} type="button" className="button-secondary" onClick={() => setForsok((n) => n + 1)}>
            {TEKSTER.provIgjen}
          </button>
        </section>
      </main>
    );
  }

  const { data } = tilstand;
  return (
    <>
      <Brodsmulesti
        ledd={[
          { tekst: TEKSTER.brodsmulesti.turnus },
          { tekst: data.avdeling, uthevet: true },
          { tekst: periodetekst(data.periode_start, data.periode_slutt) },
        ]}
      />
      <main className="innhold">
        <h1 className="visuelt-skjult">{t.overskrift}</h1>

        <section aria-labelledby="krever-handling">
          <h2 id="krever-handling" className="section-label section-label-forste">{t.kreverHandling}</h2>
          {data.krever_handling.length === 0
            ? <p className="panel brodtekst">{t.ingenKreverHandling}</p>
            : data.krever_handling.map((vakt) => (
                <Varselboks key={vakt.vaktnummer} vakt={vakt} avdeling={data.avdeling} onVelgVakt={onVelgVakt} />
              ))}
        </section>

        <section aria-labelledby="bemannet">
          <h2 id="bemannet" className="section-label">{t.bemannet}</h2>
          {data.bemannet.length === 0
            ? <p className="panel brodtekst">{t.ingenBemannet}</p>
            : <Vakttabell vakter={data.bemannet} />}
        </section>

        <p className="fotnote">{t.fotnote(datoOgKlokke(data.sist_oppdatert), data.antall_ansatte)}</p>
      </main>
    </>
  );
}

function Varselboks({ vakt, avdeling, onVelgVakt }: {
  vakt: VaktSomManglerBemanning;
  avdeling: string;
  onVelgVakt: (vaktnummer: number) => void;
}) {
  const linje = varsellinje(vakt);
  return (
    <article className="alert-box">
      <div className="alert-box-venstre">
        <span className="alert-icon" aria-hidden="true">!</span>
        <div>
          <h3 className="alert-box-overskrift">{t.vaktoverskrift(vakt.vaktnummer, vakttypenavn(vakt.vakttype), avdeling)}</h3>
          <p className="alert-box-linje">
            {linje.foer}<strong className="alert-box-status">{linje.status}</strong>{linje.etter}
          </p>
        </div>
      </div>
      <button type="button" className="button-primary button-kompakt" onClick={() => onVelgVakt(vakt.vaktnummer)}>
        {t.velgVakt}
      </button>
    </article>
  );
}

function Vakttabell({ vakter }: { vakter: BemannetVakt[] }) {
  const k = t.kolonner;
  return (
    <div className="tabellbeholder" tabIndex={0} role="region" aria-labelledby="bemannet">
      <table className="tabell">
        <thead>
          <tr>
            <th scope="col">{k.vakt}</th>
            <th scope="col">{k.dato}</th>
            <th scope="col">{k.tid}</th>
            <th scope="col">{k.ansatt}</th>
            <th scope="col">{k.status}</th>
          </tr>
        </thead>
        <tbody>
          {vakter.map((vakt, i) => {
            const { rad, datoUthevet } = radklasser(vakter, i);
            return (
              <tr key={vakt.vaktnummer} className={rad}>
                <td className="vaktnummer">{t.vaktnummer(vakt.vaktnummer)}</td>
                <td className={datoUthevet ? "dato-uthevet" : undefined}>{ukedagOgDato(vakt.start)}</td>
                <td>
                  {tidsrom(vakt.start, vakt.slutt)}
                  <div className="undertekst">{vakttypenavn(vakt.vakttype)}</div>
                </td>
                <td className="ansattnavn">
                  {vakt.ansatt.navn}
                  <div className="undertekst">{t.ansattMeta(vakt.ansatt.stilling, vakt.ansatt.ansiennitet)}</div>
                </td>
                <td><span className="tag tag-status">{t.statusBemannet}</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
