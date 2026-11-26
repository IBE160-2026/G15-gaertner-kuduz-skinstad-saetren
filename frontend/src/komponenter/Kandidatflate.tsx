import { useEffect, useRef, useState, type RefObject } from "react";
import {
  ApiFeil,
  gjeldendeSesjonsgenerasjon,
  hentVaktdetaljer,
  hentKandidater,
  lagrePreferanse,
  provPreferanse,
  type LagrePreferanseStatus,
  type RangertKandidat,
  type Ulempebelastning,
  type UtelukkelsesOppsummering,
  type Vaktdetaljer,
} from "../api";
import { datoOgKlokke, timerOgMinutter, vaktBrodsmule, vakttypenavn, énDesimal } from "../format";
import {
  SYNLIGE_KANDIDATER, ekskludertBoksTekst, ekskludertRadTekst, lastKandidater, preferansetekst, synligeKandidater,
  tilstandFraSvar, tilstandFraFeil,
  type Kandidattilstand,
} from "../kandidater";
import { INGEN_KONTAKT, TEKSTER, feiltekst } from "../tekster";
import Brodsmulesti from "./Brodsmulesti";
import Avveiningspanel from "./Avveiningspanel";
import Kostnadsvisning from "./Kostnadsvisning";
import Varselmerke from "./Varselmerke";

type Tilstand =
  | { type: "laster" }
  | { type: "avvist" }
  | { type: "ikke_funnet" }
  | { type: "feil"; tekst: string }
  | { type: "klar"; data: Vaktdetaljer };

const t = TEKSTER.kandidatflate;

type Props = {
  vaktnummer: number;
  /** Til godkjenningsflaten for Kandidaten (story 3.1). */
  onVelg: (vaktnummer: number, ansattId: number) => void;
  /** Fra `/api/meg`. Viser demomerknaden når preferanseteksten endres (story 5.9). */
  demomodus?: boolean;
};

export default function Kandidatflate({ vaktnummer, onVelg, demomodus = false }: Props) {
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
      <Kandidatliste vaktnummer={data.vaktnummer} demomodus={demomodus} onVelg={(ansattId) => onVelg(data.vaktnummer, ansattId)} />
    </main>
  </>;
}

const rp = t.redigerPreferanse;

// `ikke_gyldig`: PUT ga 404 fordi kandidaten ikke lenger er gyldig for vakten.
const LAGRET_MELDING: Record<Exclude<LagrePreferanseStatus, "uendret"> | "ikke_gyldig", string> = {
  tolket: t.tolket, feilet: t.tolkefeil, endret: t.tolkEndret, ingen: rp.ingen, venter: rp.venter,
  ikke_gyldig: rp.ikkeGyldig,
};

// Hentes automatisk når vakten er lastet (story 2.1). Bare Gyldige kandidater.
export function Kandidatliste({ vaktnummer, onVelg, demomodus = false }: { vaktnummer: number; onVelg: (ansattId: number) => void; demomodus?: boolean }) {
  const [tilstand, setTilstand] = useState<Kandidattilstand>({ type: "laster" });
  const [forsok, setForsok] = useState(0);
  const retryknapp = useRef<HTMLButtonElement>(null);

  const [paagar, setPaagar] = useState(false);
  const [melding, setMelding] = useState("");
  const visningsversjon = useRef(0);
  const opptatt = useRef(false);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const fokuserFeil = useRef(true);
  // Høyst én preferansetekst redigeres om gangen (story 5.9).
  const [redigerId, setRedigerId] = useState<number | null>(null);
  useEffect(() => {
    visningsversjon.current += 1;
    opptatt.current = false;
    setPaagar(false);
    setMelding("");
    setRedigerId(null);
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

  // Story 5.9: samme mønster som «Prøv igjen». Statuslinjen får fokus, og et sent svar
  // etter vaktbytte eller ny sesjon vises ikke. 422 beholder tekstfeltet åpent.
  async function lagrePreferanseHandling(id: number, tekst: string) {
    if (opptatt.current) return;
    opptatt.current = true;
    const generasjon = gjeldendeSesjonsgenerasjon();
    const versjon = visningsversjon.current;
    const gyldig = () => versjon === visningsversjon.current && generasjon === gjeldendeSesjonsgenerasjon();
    setPaagar(true);
    setMelding(rp.lagrer);
    statusRef.current?.focus();
    try {
      let svar: { status: LagrePreferanseStatus | "ikke_gyldig" };
      try {
        svar = await lagrePreferanse(vaktnummer, id, tekst);
      } catch (feil) {
        if (feil instanceof ApiFeil && feil.status === 422) {
          if (gyldig()) setMelding(rp.avvist(feiltekst(feil.kode)));
          return;
        }
        // Kandidaten er ikke lenger gyldig: lukk feltet og vis den oppdaterte rangeringen.
        if (feil instanceof ApiFeil && feil.status === 404) svar = { status: "ikke_gyldig" };
        else throw feil;
      }
      if (!gyldig()) return;
      if (svar.status === "uendret") {
        setRedigerId(null);
        setMelding(rp.uendret);
        return;
      }
      const kandidater = await hentKandidater(vaktnummer);
      if (!gyldig()) return;
      setRedigerId(null);
      setTilstand(tilstandFraSvar(kandidater));
      setMelding(LAGRET_MELDING[svar.status]);
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
      <h2 id="kandidater-tittel" className="overskrift">{t.datafeilOverskrift}</h2>
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
      <p className="brodtekst tomtilstand-innleie">{t.innleie}</p>
      <EkskludertBoks oppsummering={tilstand.utelukkelser} />
    </section>
  );

  return (
    <section className="panel kandidater kandidater-klar" aria-labelledby="kandidater-tittel">
      {overskrift}
      <p className="meta">{t.ulempePeriode}</p>
      <p role="status" tabIndex={-1} ref={statusRef}>{melding}</p>
      <Rangeringstabell
        vaktnummer={vaktnummer} kandidater={tilstand.kandidater} onVelg={onVelg} paagar={paagar} onProv={provPreferanseHandling}
        redigering={{ id: redigerId, demomodus, onApne: setRedigerId, onLukk: () => setRedigerId(null), onLagre: lagrePreferanseHandling }}
      />
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

type Redigering = {
  id: number | null;
  demomodus: boolean;
  onApne: (id: number) => void;
  onLukk: () => void;
  onLagre: (id: number, tekst: string) => void;
};

function Rangeringstabell({ vaktnummer, kandidater, onVelg, paagar, onProv, redigering }: { vaktnummer: number; kandidater: RangertKandidat[]; onVelg: (ansattId: number) => void; paagar: boolean; onProv: (id: number) => void; redigering: Redigering }) {
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
            <th scope="col" className="fast-nr">{k.plass}</th>
            <th scope="col" className="fast-kandidat">{k.kandidat}</th>
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
              key={`${vaktnummer}/${kandidat.id}/${kandidat.grunnlagsmerke}/${gjeldendeSesjonsgenerasjon()}`}
              vaktnummer={vaktnummer} kandidat={kandidat} alt={i % 2 === 1} onVelg={onVelg} paagar={paagar} onProv={onProv}
              redigering={redigering}
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
      <span>{t.ulempePoeng(énDesimal.format(ulempe.poeng))}</span>
      <span className="meta">{t.ulempeFordeling(
        énDesimal.format(ulempe.kveldstimer),
        énDesimal.format(ulempe.helgetimer),
        énDesimal.format(ulempe.natttimer),
      )}</span>
    </div>
  );
}

type RadProps = {
  vaktnummer: number;
  kandidat: RangertKandidat;
  alt: boolean;
  onVelg: (ansattId: number) => void;
  knappRef?: RefObject<HTMLButtonElement | null>;
  paagar: boolean;
  onProv: (id: number) => void;
  redigering: Redigering;
};

function Kandidatrad({ vaktnummer, kandidat: r, alt, onVelg, knappRef, paagar, onProv, redigering }: RadProps) {
  const [panel, settPanel] = useState<"åpent" | "skjult" | "uåpnet">(r.plass === 1 ? "åpent" : "uåpnet");
  const åpent = panel === "åpent";
  const panelId = `avveining-${r.id}`;
  return <>
    <tr className={alt ? "row-alt" : undefined}>
      <td className="fast-nr">
        <span className="rank-badge">{r.plass}</span>
        <div className="undertekst">{t.totalscore(énDesimal.format(r.totalscore))}</div>
      </td>
      <td className="fast-kandidat">
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
        <div className="undertekst">{t.preferansePoeng(énDesimal.format(r.preferansepoeng))}</div>
        {r.tolkestatus === "kunne_ikke_tolkes" && <button type="button" className="button-secondary button-kompakt" disabled={paagar} aria-label={t.provPreferanse(r.navn)} onClick={() => onProv(r.id)}>{TEKSTER.provIgjen}</button>}
        <Preferanseredigering kandidat={r} paagar={paagar} redigering={redigering} />
      </td>
      <td>
        <button
          ref={knappRef} type="button" disabled={paagar} className="button-secondary button-kompakt"
          aria-label={TEKSTER.godkjenning.velgEtikett(r.navn)} onClick={() => onVelg(r.id)}
        >
          {TEKSTER.godkjenning.velg}
        </button>
        <button type="button" className="avveining-knapp" aria-expanded={åpent} aria-controls={panelId}
          aria-label={åpent ? t.avveining.skjulEtikett(r.navn) : t.avveining.visEtikett(r.navn)}
          onClick={() => settPanel(åpent ? "skjult" : "åpent")}>
          {åpent ? t.avveining.skjul : t.avveining.vis}
        </button>
      </td>
    </tr>
    <tr hidden={!åpent} id={panelId}>
      <td colSpan={8} className="avveining-celle">
        {panel !== "uåpnet" && <Avveiningspanel vaktnummer={vaktnummer} kandidat={r} merke={r.grunnlagsmerke} />}
      </td>
    </tr>
  </>;
}

// «Endre» i preferansecellen (story 5.9, P-10B). Tekstfeltet er forhåndsutfylt med
// råteksten. Lagre sender teksten; Avbryt (eller Esc) lukker feltet uten å lagre og gir
// fokus tilbake til «Endre». Raden monteres på nytt når merket endres etter lagring.
function Preferanseredigering({ kandidat: r, paagar, redigering }: { kandidat: RangertKandidat; paagar: boolean; redigering: Redigering }) {
  const åpen = redigering.id === r.id;
  const [utkast, setUtkast] = useState(r.preferansetekst ?? "");
  const felt = useRef<HTMLTextAreaElement>(null);
  const endreknapp = useRef<HTMLButtonElement>(null);
  const tilbakeTilEndre = useRef(false);
  const hjelpId = `preferanse-hjelp-${r.id}`;

  useEffect(() => {
    if (åpen) felt.current?.focus();
    else if (tilbakeTilEndre.current) {
      tilbakeTilEndre.current = false;
      endreknapp.current?.focus();
    }
  }, [åpen]);

  function avbryt() {
    tilbakeTilEndre.current = true;
    setUtkast(r.preferansetekst ?? "");
    redigering.onLukk();
  }

  if (!åpen) return (
    <button
      ref={endreknapp} type="button" className="button-secondary button-kompakt" disabled={paagar}
      aria-label={rp.endreEtikett(r.navn)}
      onClick={() => { setUtkast(r.preferansetekst ?? ""); redigering.onApne(r.id); }}
    >
      {rp.endre}
    </button>
  );

  return (
    <form
      className="preferanse-redigering" onSubmit={(e) => { e.preventDefault(); redigering.onLagre(r.id, utkast); }}
      onKeyDown={(e) => { if (e.key === "Escape") { e.preventDefault(); avbryt(); } }}
    >
      <textarea
        ref={felt} aria-label={rp.feltEtikett(r.navn)} aria-describedby={hjelpId} maxLength={500}
        value={utkast} disabled={paagar}
        onChange={(e) => setUtkast(e.target.value)}
      />
      <div id={hjelpId} className="undertekst">
        <span>{rp.hjelp}</span>
        {redigering.demomodus && <> <span>{rp.demo}</span></>}
      </div>
      <div className="preferanse-handlinger">
        <button type="submit" className="button-secondary button-kompakt" disabled={paagar} aria-label={rp.lagreEtikett(r.navn)}>
          {rp.lagre}
        </button>
        <button type="button" className="button-secondary button-kompakt" disabled={paagar} aria-label={rp.avbrytEtikett(r.navn)} onClick={avbryt}>
          {rp.avbryt}
        </button>
      </div>
    </form>
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
