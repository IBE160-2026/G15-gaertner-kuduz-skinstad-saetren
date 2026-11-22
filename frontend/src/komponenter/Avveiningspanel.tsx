import { useEffect, useState } from "react";
import { gjeldendeSesjonsgenerasjon, hentAvveining, type Avveiningssvar, type Faktor, type RangertKandidat } from "../api";
import { timerOgMinutter, énDesimal } from "../format";
import { gyldigAvveining, preferansetekst } from "../kandidater";
import { TEKSTER } from "../tekster";

const t = TEKSTER.kandidatflate.avveining;
const tall = new Intl.NumberFormat("nb-NO", { maximumFractionDigits: 1 });
const kroner = new Intl.NumberFormat("nb-NO", { style: "currency", currency: "NOK" });
type Live = Extract<Avveiningssvar, {status: "ok"}>;

export default function Avveiningspanel({ vaktnummer, kandidat, merke }: {
  vaktnummer: number; kandidat: RangertKandidat; merke: string;
}) {
  const [svar, settSvar] = useState<Live | "laster" | "reserve">("laster");
  const id = kandidat.id;
  const sesjon = gjeldendeSesjonsgenerasjon();
  useEffect(() => {
    let aktiv = true;
    const gjelder = () => aktiv && sesjon === gjeldendeSesjonsgenerasjon();
    // Ved StrictMode-opprydding før første mikrooppgave skal bare den aktive effekten sende kallet.
    async function last() {
      if (!gjelder()) return;
      try {
        const data = await hentAvveining(vaktnummer, id);
        if (gjelder()) settSvar(gyldigAvveining(data, vaktnummer, id, merke) ? data : "reserve");
      } catch {
        if (gjelder()) settSvar("reserve");
      }
    }
    void Promise.resolve().then(last);
    return () => { aktiv = false; };
  }, [vaktnummer, id, merke, sesjon]);

  const u = kandidat.ulempebelastning;
  const fakta: [Faktor, string][] = [
    ["kostnad", kroner.format(kandidat.kostnad.total)],
    ["timebelastning", `${timerOgMinutter(kandidat.minutter_i_uka)} t:min i uka (${tall.format(kandidat.timebelastning_prosent)} %)`],
    ["ulempe", `${tall.format(u.poeng)} ulempepoeng · ${TEKSTER.kandidatflate.ulempeFordeling(
      tall.format(u.kveldstimer), tall.format(u.helgetimer), tall.format(u.natttimer))}`],
    ["preferanse", `${preferansetekst(kandidat)} · ${TEKSTER.kandidatflate.preferansePoeng(énDesimal.format(kandidat.preferansepoeng))}`],
  ];
  return <section className="avveiningspanel" aria-label={t.tittel(kandidat.navn)}>
    <h3 className="overskrift">{t.tittel(kandidat.navn)}</h3>
    <div role="status" aria-live="polite">{svar === "reserve" && <p>{t.reservetekst}</p>}</div>
    <p>{t.kvalifisert}</p>
    <p className="meta">{t.sammenligning(énDesimal.format(kandidat.totalscore))}</p>
    <dl>{fakta.map(([faktor, verdi]) => {
      const retning = kandidat.faktorretninger[faktor];
      const poeng = faktor === "preferanse" ? kandidat.preferansepoeng : kandidat.faktorpoeng[faktor];
      return <div key={faktor}>
        <dt>{t[faktor]}</dt>
        <dd>{verdi} {retning && <span className={`retning-${retning}`}>
          <span>{t[retning]}</span> · {énDesimal.format(poeng)} {t.poengnavn[faktor]}
        </span>}</dd>
      </div>;
    })}</dl>
    <div aria-live="polite">
      {typeof svar === "object" && svar.paastander.map((tekst) => <p key={tekst}>{tekst}</p>)}
      {svar !== "reserve" && <p className="meta">{svar === "laster" ? t.laster : t.kilde(svar.modell)}</p>}
    </div>
    {svar === "reserve" && <p className="meta">{t.reserve}</p>}
  </section>;
}
