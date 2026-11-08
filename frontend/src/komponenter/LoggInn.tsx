import { useEffect, useRef, useState, type FormEvent } from "react";
import { ApiFeil, gjeldendeSesjonsgenerasjon, hentInnloggingsinfo, loggInn, type Innlogget, type PassordKilde } from "../api";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "../tekster";

type Props = {
  onInnlogget: (bruker: Innlogget) => void;
  onForsinketInnlogging: () => void;
  // Feil fra GET /api/meg ved oppstart, for eksempel at API-et ikke svarer.
  startfeil: string | null;
};

function tekstForFeil(feil: unknown): string {
  return feil instanceof ApiFeil ? feiltekst(feil.kode) : INGEN_KONTAKT;
}

export default function LoggInn({ onInnlogget, onForsinketInnlogging, startfeil }: Props) {
  const [brukernavn, setBrukernavn] = useState("");
  const [passord, setPassord] = useState("");
  const [feil, setFeil] = useState<string | null>(null);
  const [infofeil, setInfofeil] = useState<string | null>(null);
  // `undefined` til svaret fra /api/innloggingsinfo er kommet.
  const [kilde, setKilde] = useState<PassordKilde | undefined>(undefined);
  const sender = useRef(false);
  const passordfelt = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let aktiv = true;
    hentInnloggingsinfo().then(
      (svar) => aktiv && setKilde(svar),
      (e: unknown) => aktiv && setInfofeil(tekstForFeil(e)),
    );
    return () => {
      aktiv = false;
    };
  }, []);

  async function send(hendelse: FormEvent<HTMLFormElement>) {
    hendelse.preventDefault();
    if (sender.current) return;
    sender.current = true;
    const generasjon = gjeldendeSesjonsgenerasjon();
    try {
      // Feltet beholder det som er skrevet, men mellomrom fra autoutfylling sendes ikke.
      const svar = await loggInn(brukernavn.trim(), passord);
      if (generasjon === gjeldendeSesjonsgenerasjon()) onInnlogget(svar);
      else onForsinketInnlogging(); // Svaret kan ha satt en ny cookie i nettleseren.
    } catch (e) {
      setFeil(tekstForFeil(e));
      setPassord("");
      passordfelt.current?.focus();
    } finally {
      sender.current = false;
    }
  }

  const variant =
    kilde === undefined ? null : TEKSTER.passordvarianter[kilde ?? "ingen"];
  const t = TEKSTER.loggInn;
  const melding = feil ?? startfeil ?? infofeil;

  return (
    <main className="innloggingsflate">
      <section className="login-card">
        <h1 className="overskrift">{t.overskrift}</h1>
        <p className="login-card-undertekst">{t.undertekst}</p>

        <form onSubmit={send}>
          <div className="felt">
            <label htmlFor="brukernavn">{t.brukernavn}</label>
            <input
              id="brukernavn"
              autoFocus
              name="brukernavn"
              type="text"
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              value={brukernavn}
              onChange={(e) => setBrukernavn(e.target.value)}
            />
          </div>
          <div className="felt">
            <label htmlFor="passord">{t.passord}</label>
            <input
              id="passord"
              name="passord"
              type="password"
              autoComplete="current-password"
              ref={passordfelt}
              value={passord}
              onChange={(e) => setPassord(e.target.value)}
            />
          </div>

          {melding && (
            <p className="skjemafeil" role="alert">
              {melding}
            </p>
          )}

          <button type="submit" className="button-primary">
            {t.knapp}
          </button>
        </form>

        <p className="rollenotat">
          <strong>{t.rollenotat.etikett}</strong>
          {t.rollenotat.foer}
          <strong>{t.rollenotat.rolle}</strong>
          {t.rollenotat.etter}
        </p>

        {variant && (
          <div className="passordvariant">
            <span className="tag">{variant.tag}</span>
            <p className="meta">{variant.meta}</p>
          </div>
        )}

        <p className="meta registreringsnotat">{t.registrering}</p>
      </section>
    </main>
  );
}
