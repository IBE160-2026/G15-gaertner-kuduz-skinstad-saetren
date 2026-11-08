import { useEffect, useState } from "react";
import { ApiFeil, hentMeg, type Innlogget } from "./api";
import Appbar from "./komponenter/Appbar";
import LoggInn from "./komponenter/LoggInn";
import Startside from "./komponenter/Startside";
import { INGEN_KONTAKT, feiltekst } from "./tekster";

// Ingen router før story 1.4. Appen viser Logg inn eller den foreløpige
// startsiden etter svaret fra GET /api/meg.
export default function App() {
  // `undefined` til svaret fra /api/meg er kommet, `null` når ingen er innlogget.
  const [bruker, setBruker] = useState<Innlogget | null | undefined>(undefined);
  const [startfeil, setStartfeil] = useState<string | null>(null);

  useEffect(() => {
    let aktiv = true;
    hentMeg().then(
      (svar) => aktiv && setBruker(svar),
      (e: unknown) => {
        if (!aktiv) return;
        // 401 betyr bare at ingen er innlogget, og gir ingen melding.
        if (!(e instanceof ApiFeil)) setStartfeil(INGEN_KONTAKT);
        else if (e.status !== 401) setStartfeil(feiltekst(e.kode));
        setBruker(null);
      },
    );
    return () => {
      aktiv = false;
    };
  }, []);

  return (
    <>
      <Appbar bruker={bruker} />
      {bruker === null && <LoggInn onInnlogget={setBruker} startfeil={startfeil} />}
      {bruker && <Startside />}
    </>
  );
}
