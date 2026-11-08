import { useEffect, useRef, useState } from "react";
import {
  ApiFeil, gjeldendeSesjonsgenerasjon, hentMeg, loggUt,
  nySesjonsgenerasjon, settSesjonsvarsler, type Innlogget,
} from "./api";
import Appbar from "./komponenter/Appbar";
import LoggInn from "./komponenter/LoggInn";
import Vaktvalg from "./komponenter/Vaktvalg";
import { INNLOGGING_STI, OVERSIKT_STI, maalEtterBekreftetSesjon, naviger } from "./navigasjon";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "./tekster";

export default function App() {
  const [bruker, setBruker] = useState<Innlogget | null | undefined>(undefined);
  const [startfeil, setStartfeil] = useState<string | null>(null);
  const [kontrollfeil, setKontrollfeil] = useState(false);
  const [navigasjonsfeil, setNavigasjonsfeil] = useState<string | null>(null);
  const [sti, setSti] = useState(window.location.pathname);
  const bekreftetSesjon = useRef(false);
  const utloggingSperrer = useRef(false);
  const utloggingVenter = useRef(false);
  const retryknapp = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (kontrollfeil || navigasjonsfeil) retryknapp.current?.focus();
  }, [kontrollfeil, navigasjonsfeil]);

  function visInnlogging(utlopt: boolean) {
    nySesjonsgenerasjon();
    setBruker(null);
    setKontrollfeil(false);
    setNavigasjonsfeil(null);
    setStartfeil(utlopt && bekreftetSesjon.current ? TEKSTER.sesjonUtlopt : null);
    bekreftetSesjon.current = false;
    utloggingSperrer.current = false;
    naviger(INNLOGGING_STI, true);
    setSti(INNLOGGING_STI);
  }

  function kontroller() {
    if (utloggingSperrer.current) return;
    const generasjon = nySesjonsgenerasjon();
    setBruker(undefined);
    setKontrollfeil(false);
    setStartfeil(null);
    setNavigasjonsfeil(null);
    hentMeg().then(
      (svar) => {
        if (generasjon !== gjeldendeSesjonsgenerasjon()) return;
        bekreftetSesjon.current = true;
        setBruker(svar);
        const nySti = maalEtterBekreftetSesjon(window.location.pathname);
        naviger(nySti, true);
        setSti(nySti);
      },
      (feil: unknown) => {
        if (generasjon !== gjeldendeSesjonsgenerasjon()) return;
        if (feil instanceof ApiFeil && feil.status === 401) {
          visInnlogging(true);
          return;
        }
        setNavigasjonsfeil(feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT);
      },
    );
  }

  useEffect(() => {
    settSesjonsvarsler(() => visInnlogging(true));
    const vedNavigasjon = () => kontroller();
    window.addEventListener("popstate", vedNavigasjon);
    kontroller();
    return () => {
      settSesjonsvarsler(null);
      window.removeEventListener("popstate", vedNavigasjon);
      nySesjonsgenerasjon();
    };
  }, []);

  function innlogget(svar: Innlogget) {
    nySesjonsgenerasjon();
    bekreftetSesjon.current = true;
    setBruker(svar);
    setStartfeil(null);
    setNavigasjonsfeil(null);
    naviger(OVERSIKT_STI);
    setSti(OVERSIKT_STI);
  }

  function velgVakt(vaktnummer: number) {
    const nySti = `/vakt/${vaktnummer}/kandidater`;
    naviger(nySti);
    setSti(nySti);
  }

  async function loggUtNaa() {
    if (utloggingVenter.current) return;
    utloggingSperrer.current = true;
    utloggingVenter.current = true;
    const generasjon = nySesjonsgenerasjon();
    setBruker(undefined);
    setKontrollfeil(false);
    try {
      await loggUt();
      if (generasjon === gjeldendeSesjonsgenerasjon()) visInnlogging(false);
    } catch (feil) {
      if (generasjon !== gjeldendeSesjonsgenerasjon()) return;
      if (feil instanceof ApiFeil && feil.status === 401) {
        visInnlogging(true);
      } else {
        setKontrollfeil(true);
      }
    } finally {
      utloggingVenter.current = false;
    }
  }

  return (
    <>
      <Appbar bruker={bruker} onLoggUt={loggUtNaa} />
      {kontrollfeil && (
        <main className="innhold">
          <section className="panel" role="alert">
            <p className="brodtekst">{TEKSTER.utloggingFeilet}</p>
            <button ref={retryknapp} className="button-secondary" onClick={loggUtNaa}>{TEKSTER.provIgjen}</button>
          </section>
        </main>
      )}
      {navigasjonsfeil && (
        <main className="innhold">
          <section className="panel" role="alert">
            <p className="brodtekst">{navigasjonsfeil}</p>
            <button ref={retryknapp} className="button-secondary" onClick={kontroller}>{TEKSTER.provIgjen}</button>
          </section>
        </main>
      )}
      {bruker === null && <LoggInn onInnlogget={innlogget} onForsinketInnlogging={kontroller} startfeil={startfeil} />}
      {bruker && sti === OVERSIKT_STI && <Vaktvalg onVelgVakt={velgVakt} />}
      {bruker && sti !== OVERSIKT_STI && (
        <main className="innhold"><section className="panel">
          <h1 className="overskrift">{TEKSTER.sideIkkeFunnet}</h1>
        </section></main>
      )}
    </>
  );
}
