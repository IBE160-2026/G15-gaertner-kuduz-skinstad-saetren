import { TEKSTER } from "../tekster";

// Foreløpig startside etter innlogging. Vaktoversikten kommer i story 1.5.
export default function Startside() {
  return (
    <main className="innhold">
      <section className="panel">
        <h1 className="overskrift">{TEKSTER.startside.overskrift}</h1>
        <p className="brodtekst">{TEKSTER.startside.tekst}</p>
      </section>
    </main>
  );
}
