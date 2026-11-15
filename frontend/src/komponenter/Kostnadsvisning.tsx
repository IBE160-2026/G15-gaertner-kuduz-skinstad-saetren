import type { Kostnad } from "../api";
import { timerOgMinutter } from "../format";
import { TEKSTER } from "../tekster";
import Varselmerke from "./Varselmerke";

const t = TEKSTER.kandidatflate;
const penger = new Intl.NumberFormat("nb-NO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** Kostnadsindikatoren (story 4.3, P-01–P-03). Overtid bruker samme Varselmerke som høy belastning (4.2). */
export default function Kostnadsvisning({ kostnad }: { kostnad: Kostnad }) {
  const varighet = (timer: number) => {
    const minutter = timer * 60;
    const avrundet = Math.round(minutter);
    return `${Math.abs(minutter - avrundet) > 1e-8 ? "ca. " : ""}${timerOgMinutter(avrundet)}`;
  };
  return <div className="kandidat-kostnad">
    <span>{t.kostnadOverskrift}: {penger.format(kostnad.total)} kr</span>
    {kostnad.overtidstimer > 0
      ? <Varselmerke>{t.kostnadOvertid}</Varselmerke>
      : <span className="kostnad-ordinaer">{t.kostnadOrdinaer}</span>}
    {kostnad.ordinære_timer > 0 && <span className="meta">{t.kostnadOrdinaer}: {t.kostnadDetalj(varighet(kostnad.ordinære_timer), penger.format(kostnad.ordinær_sats))}</span>}
    {kostnad.overtidstimer > 0 && <span className="meta">{t.kostnadOvertidDel}: {t.kostnadDetalj(varighet(kostnad.overtidstimer), penger.format(kostnad.overtidssats))}</span>}
  </div>;
}
