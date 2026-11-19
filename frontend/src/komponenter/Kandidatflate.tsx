import { useEffect, useRef, useState, type RefObject } from "react";
import {
  ApiFeil,
  gjeldendeSesjonsgenerasjon,
  hentVaktdetaljer,
  hentKandidater,
  provPreferanse,
  type RangertKandidat,
  type Ulempebelastning,
  type UtelukkelsesOppsummering,
  type Vaktdetaljer,
} from "../api";
import { datoOgKlokke, timerOgMinutter, vaktBrodsmule, vakttypenavn } from "../format";
import {
  SYNLIGE_KANDIDATER, ekskludertBoksTekst, ekskludertRadTekst, lastKandidater, preferansetekst, synligeKandidater,
  tilstandFraSvar, tilstandFraFeil,
  type Kandidattilstand,
} from "../kandidater";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "../tekster";
import Brodsmulesti from "./Brodsmulesti";
import Kostnadsvisning from "./Kostnadsvisning";
import Varselmerke from "./Varselmerke";

type Tilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "ikke_funnet" }
  | { type: "feil"; tekst: string }
  | { type: "klar"; data: Vaktdetaljer };

const t = TEKSTER.kandidatflate;
const tall = new Intl.NumberFormat("nb-NO", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

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
export function Kandidatliste({ vaktnummer, onVelg }: { vaktnummer: number; onVelg: (ansattId: number) => void }) {
  const [tilstand, setTilstand] = useState<Kandidattilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const retryknapp = useRef<HTMLButtonElement>(null);

  const [paagar, setPaagar] = useState(false);
  const [melding, setMelding] = useState("");
  const visningsversjon = useRef(0);
  const opptatt = useRef(false);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const fokuserFeil = useRef(true);
  useEffect(() => {
    visningsversjon.current += 1;
    opptatt.current = false;
    setPaagar(false);
    setMelding("");
    fokuserFeil.current = true;
    return () => { visningsversjon.current += 1; };
  }, [vaktnummer]);

  useEffect(() => lastKandidater(vaktnummer, setTilstand), [vaktnummer, forsok]);

  async function provPreferanseHandling(id: number) {
    if (opptatt.current) return;
    opptatt.current = true;
    const generasjon = gjeldendeSesjonsgenerasjon();
    const versjon = visningsversjon.current;
    const gyldig = () => versjon === visningsversjon.current && generasjon === gjeldendeSesjonsgenerasjon();
    setPaagar(true);
    setMelding(t.tolker);
    statusRef.current?.focus();
    try {
      const svar = await provPreferanse(vaktnummer, id);
      if (!gyldig()) return;
      const kandidater = await hentKandidater(vaktnummer);
      if (!gyldig()) return;
      setTilstand(tilstandFraSvar(kandidater));
      setMelding(svar.status === "tolket" ? t.tolket : svar.status === "feilet" ? t.tolkefeil : t.tolkEndret);
    } catch (feil) {
      if (!gyldig()) return;
      fokuserFeil.current = document.activeElement === statusRef.current;
      setTilstand(tilstandFraFeil(feil));
    } finally {
      if (gyldig()) { opptatt.current = false; setPaagar(false); }
    }
  }

  useEffect(() => {
    if (tilstand.type === "feil" && fokuserFeil.current) retryknapp.current?.focus();
  }, [tilstand]);

  if (tilstand.type === "avvist") return null;

  const overskrift = <h2 id="kandidater-tittel" className="overskrift">{t.kandidaterOverskrift}</h2>;

  if (tilstand.type === "laster") return (
    <section className="panel kandidater kandidater-laster" aria-labelledby="kandidater-tittel">
      {overskrift}
      <p className="meta kandidater-status" role="status">{t.kandidaterLaster}</p>
    </section>
  );
  if (tilstand.type === "feil") return (
    <section className="panel kandidater kandidater-feil" aria-labelledby="kandidater-tittel">
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
    <section className="panel kandidater kandidater-datafeil datafeil" aria-labelledby="kandidater-tittel">
      {overskrift}
      <div role="alert">
        <p className="brodtekst datafeil-tekst">{t.datafeil}</p>
        <p className="meta">{t.datagrense(datoOgKlokke(tilstand.datagrense))}</p>
      </div>
    </section>
  );

  // Tomtilstanden (story 2.6, UX-DR16, P-11): ikon, tekst, Ekskludert-boks og ren innleietekst.
  if (tilstand.type === "ingen_gyldige") return (
    <section className="panel kandidater tomtilstand" aria-labelledby="kandidater-tittel">
      {overskrift}
      <div className="tomtilstand-innhold" role="status">
        <span className="alert-icon" aria-hidden="true">!</span>
        <p className="brodtekst">{t.ingenGyldige}</p>
      </div>
      <EkskludertBoks oppsummering={tilstand.utelukkelser} />
      <p className="meta tomtilstand-innleie">{t.innleie}</p>
    </section>
  );

  return (
    <section className="panel kandidater kandidater-klar" aria-labelledby="kandidater-tittel">
      {overskrift}
      <p className="meta">{t.ulempePeriode}</p>
      <p role="status" tabIndex={-1} ref={statusRef}>{melding}</p>
      <Rangeringstabell kandidater={tilstand.kandidater} onVelg={onVelg} paagar={paagar} onProv={provPreferanseHandling} />
      <EkskludertBoks oppsummering={tilstand.utelukkelser} />
    </section>
  );
}

// Rangeringstabellen (story 4.4, UX-DR7–DR11). Erstatter den alfabetiske listen fra
// 2.1. De fem øverste vises uten ekstra handling (SM-3); «Vis alle gyldige kandidater»
// viser resten og flytter fokus til den første nye raden. Samme knapp lukker listen
// igjen til de fem øverste, og fokus blir stående på knappen. Monteres på nytt ved hver
// lasting, så valget nullstilles for en ny vakt.
const k = t.kolonner;

function Rangeringstabell({ kandidater, onVelg, paagar, onProv }: { kandidater: RangertKandidat[]; onVelg: (ansattId: number) => void; paagar: boolean; onProv: (id: number) => void }) {
  const [visAlle, setVisAlle] = useState(false);
  const førsteNye = useRef<HTMLButtonElement>(null);
  const synlige = synligeKandidater(kandidater, visAlle);

  useEffect(() => {
    if (visAlle) førsteNye.current?.focus();
  }, [visAlle]);

  return <>
    <div className="tabellbeholder rangeringstabell" tabIndex={0} role="region" aria-label={t.rangeringstabell}>
      <table className="tabell">
        <thead>
          <tr>
            <th scope="col">{k.plass}</th>
            <th scope="col">{k.kandidat}</th>
            <th scope="col">{k.kompetanse}</th>
            <th scope="col">{k.kostnad}</th>
            <th scope="col">{k.timebelastning}</th>
            <th scope="col">{k.ulempe}</th>
            <th scope="col">{k.preferanse}</th>
            <th scope="col"><span className="visuelt-skjult">{k.handling}</span></th>
          </tr>
        </thead>
        <tbody>
          {synlige.map((kandidat, i) => (
            <Kandidatrad
              key={kandidat.id} kandidat={kandidat} alt={i % 2 === 1} onVelg={onVelg} paagar={paagar} onProv={onProv}
              knappRef={i === SYNLIGE_KANDIDATER ? førsteNye : undefined}
            />
          ))}
        </tbody>
      </table>
    </div>
    {kandidater.length > SYNLIGE_KANDIDATER && (
      <div className="vis-alle">
        <p className="meta">
          {visAlle ? t.viserAlle(kandidater.length) : t.viserAv(SYNLIGE_KANDIDATER, kandidater.length)}
        </p>
        {/* Samme knapp i begge tilstander, så fokus blir stående på den når listen lukkes. */}
        <button type="button" className="button-secondary" aria-expanded={visAlle} onClick={() => setVisAlle((v) => !v)}>
          {visAlle ? t.visFærre(SYNLIGE_KANDIDATER) : t.visAlle}
        </button>
      </div>
    )}
  </>;
}

// Timebelastningslinjen med synlig timetall og skjermlesertekst (story 4.2), og
// ulempeindikatoren med poeng og kveld/helg/natt-fordeling (story 4.7). Skilt ut
// av `Kandidatrad` (story 4.5) for gjenbruk i godkjenningsflatens kandidatkort og
// avviksnotat. Et `Fragment` holder DOM-en identisk med den tidligere inline-JSX-en.
export function Belastningslinje(
  { minutter, prosent, høy }: { minutter: number; prosent: number; høy: boolean },
) {
  return <>
    <span className="timer-i-uka">
      <span aria-hidden="true">{t.timerIUka(timerOgMinutter(minutter))}</span>
      <span className="visuelt-skjult">{t.timerIUkaOpplest(timerOgMinutter(minutter))}</span>
    </span>
    <span className="belastning">
      <span className="belastningslinje" aria-hidden="true">
        <span
          className={høy ? "belastningsfyll hoy" : "belastningsfyll"}
          style={{ width: `${Math.min(Math.max(prosent, 0), 100)}%` }}
        />
      </span>
      {høy && <Varselmerke>{t.hoyBelastning}</Varselmerke>}
    </span>
  </>;
}

export function Ulempeindikator({ ulempe }: { ulempe: Ulempebelastning }) {
  return (
    <div className="kandidat-ulempe">
      <span>{t.ulempePoeng(tall.format(ulempe.poeng))}</span>
      <span className="meta">{t.ulempeFordeling(
        tall.format(ulempe.kveldstimer),
        tall.format(ulempe.helgetimer),
        tall.format(ulempe.natttimer),
      )}</span>
    </div>
  );
}

type RadProps = {
  kandidat: RangertKandidat;
  alt: boolean;
  onVelg: (ansattId: number) => void;
  knappRef?: RefObject<HTMLButtonElement | null>;
  paagar: boolean;
  onProv: (id: number) => void;
};

function Kandidatrad({ kandidat: r, alt, onVelg, knappRef, paagar, onProv }: RadProps) {
  return (
    <tr className={alt ? "row-alt" : undefined}>
      <td>
        <span className="rank-badge">{r.plass}</span>
        <div className="undertekst">{t.totalscore(tall.format(r.totalscore))}</div>
      </td>
      <td>
        <span className="ansattnavn">{r.navn}</span>
        <div className="undertekst">{t.kandidatMeta(r.stilling, r.ansiennitet)}</div>
      </td>
      <td><span className="tag">{t.nivaaTag(r.kompetansenivå)}</span></td>
      <td><Kostnadsvisning kostnad={r.kostnad} /></td>
      <td>
        <Belastningslinje minutter={r.minutter_i_uka} prosent={r.timebelastning_prosent} høy={r.hoy_belastning} />
      </td>
      <td>
        <Ulempeindikator ulempe={r.ulempebelastning} />
      </td>
      <td className="preferansecelle">
        <span className="tag">{preferansetekst(r)}</span>
        <div className="undertekst">{t.preferansePoeng(tall.format(r.preferansepoeng))}</div>
        {r.tolkestatus === "kunne_ikke_tolkes" && <button type="button" className="button-secondary button-kompakt" disabled={paagar} aria-label={t.provPreferanse(r.navn)} onClick={() => onProv(r.id)}>{TEKSTER.provIgjen}</button>}
      </td>
      <td>
        <button
          ref={knappRef} type="button" disabled={paagar} className="button-secondary button-kompakt"
          aria-label={TEKSTER.godkjenning.velgEtikett(r.navn)} onClick={() => onVelg(r.id)}
        >
          {TEKSTER.godkjenning.velg}
        </button>
      </td>
    </tr>
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
