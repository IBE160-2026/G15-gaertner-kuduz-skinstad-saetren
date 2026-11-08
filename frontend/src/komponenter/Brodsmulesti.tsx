import { Fragment } from "react";
import { TEKSTER } from "../tekster";

export type Ledd = { tekst: string; uthevet?: boolean };

type Props = { ledd: readonly Ledd[] };

// Stripe over hele bredden under appbaren, innholdet høyst 1180px (UX-DR3,
// AV-14). Brukes også av kandidatflaten i story 1.6.
export default function Brodsmulesti({ ledd }: Props) {
  return (
    <nav className="brodsmulesti" aria-label={TEKSTER.brodsmulesti.etikett}>
      <p className="brodsmulesti-innhold">
        {ledd.map((l, i) => (
          <Fragment key={i}>
            {i > 0 && <span aria-hidden="true"> &gt; </span>}
            {l.uthevet ? <b>{l.tekst}</b> : <span>{l.tekst}</span>}
          </Fragment>
        ))}
      </p>
    </nav>
  );
}
