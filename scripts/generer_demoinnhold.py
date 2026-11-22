"""Genererer `backend/adaptere/ki/demoinnhold.json` for `DemoKiAdapter` (story 5.7, AD-6).

Innholdet dekker to ting, begge laget med den ekte `OpenRouterKiAdapter` og samme
prompt som live (aldri håndskrevet):

- Preferansetolkning for alle 15 fasittekstene i PRD §4.5 (`adaptere.lagring.testdata.PREFERANSER`).
- Avveining for de fire Gyldige kandidatene på vakt #4127, med referanse etter
  samme regel som ruten (P-07): nr. 1 mot nr. 2, de andre mot nr. 1. Alle fire har
  en referanse i dagens testdata.

Uten `--live` er dette en tørrkjøring: viser hva som ville blitt generert og gjør
ingen nettverkskall. `--live` bruker nøkkelen fra miljøet eller `.env`
(samme oppslag som `modelltest_openrouter.configuration`) og gjør 15 + 4 = 19
betalte kall mot OpenRouter, innenfor samme takt/begrenser (AD-7) som appen bruker.

`DemoKiAdapter` faktakontrollerer hvert Avveining-oppslag på nytt mot gjeldende,
uavrundede tall ved hver visning (P-06), så datafilen trenger ikke selve tallene —
bare kandidat- og referanse-ID og modellens rå svar. Endrer testdataene eller
vektene seg etter at filen ble generert, faller demo-modus automatisk tilbake til
mal-svar for den avveiningen, i stedet for å vise en foreldet sammenligning.

Kjøres fra repo-roten: `python scripts/generer_demoinnhold.py [--live]`.
"""

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import modelltest_openrouter as base  # noqa: E402 (sys.path må settes først)

from adaptere.ki import avveining  # noqa: E402
from adaptere.ki.demo import KONTRAKTSVERSJON  # noqa: E402
from adaptere.ki.openrouter import OpenRouterKiAdapter, Tolkefeil, les_jsoninnhold  # noqa: E402
from adaptere.lagring.database import lag_engine, lag_sessionmaker, opprett_skjema  # noqa: E402
from adaptere.lagring.kandidatgrunnlag import hent_kandidatgrunnlag  # noqa: E402
from adaptere.lagring.modeller import BrukerRad  # noqa: E402
from adaptere.lagring.testdata import ANSATTE, PREFERANSER, fyll_testdata, legg_til_turnusansvarlig  # noqa: E402
from domene.porter.rangering import TolketPreferanse  # noqa: E402
from domene.regelmotor.rangering import ranger  # noqa: E402
from domene.regelmotor.vurdering import vurder_kandidater  # noqa: E402
from domene.typer import Datafeil  # noqa: E402
from sqlalchemy import select  # noqa: E402

DATA = BACKEND / "adaptere" / "ki" / "demoinnhold.json"
VAKT = 4127
PREFERANSENUMMER = {ansatt_id: nr for ansatt_id, *_, nr in ANSATTE if nr is not None}


def _poeng(rad) -> dict:
    """Samme payload-form som `OpenRouterKiAdapter.forklar` (ikke eksportert derfra)."""
    return {"kandidat_id": rad.id, "plass": rad.plass,
            "poeng": {f: float(getattr(rad.eksakte_poeng, f)) for f in avveining.SCORENAVN}}


def rangert_grunnlag(engine):
    """De fire Gyldige kandidatene for vakt #4127, i rangert rekkefølge, uten tolkede
    preferanser (de settes separat fra de 15 live-tolkede fasittekstene)."""
    with lag_sessionmaker(engine).begin() as session:
        fyll_testdata(session)
        legg_til_turnusansvarlig(session, "demoinnhold-generator", "tilfeldig")
    with lag_sessionmaker(engine)() as session:
        bruker_id = session.scalars(select(BrukerRad.id)).one()
        grunnlag = hent_kandidatgrunnlag(session, bruker_id, VAKT)
    assert grunnlag is not None, f"vakt #{VAKT} finnes ikke i testdataene"
    return grunnlag


def gyldige_rangert(grunnlag, tolkede: dict):
    vurdering = vurder_kandidater(grunnlag.vakt, grunnlag.ansatte, grunnlag.datagrense, grunnlag.historikkstart)
    assert not isinstance(vurdering, Datafeil), "testdataene for #4127 gir datafeil, uventet"
    return ranger(vurdering, grunnlag.vakt, tolkede=tolkede)


def referanse_for(rangert: tuple, kandidat_id: int):
    """Samme regel som `avveining()`-ruten i `adaptere/api/main.py` (P-07)."""
    andre = (r for r in rangert if r.id != kandidat_id)
    return next(andre, None)


def rått_avveiningssvar(adapter: OpenRouterKiAdapter, kandidat, referanse):
    """Modellens rå, ikke-validerte svar: det er dette `DemoKiAdapter` lagrer og
    faktakontrollerer på nytt ved hvert oppslag (P-06), ikke den ferdige teksten.

    Dupliserer formen på forespørselen fra `OpenRouterKiAdapter.forklar` (den
    metoden returnerer bare den validerte teksten eller `None`, aldri råsvaret).

    `None` her betyr at selve kallet mislyktes (nettverk, tidsbudsjett, ubrukelig
    svar). `main()` sjekker «ingen myk faktor» selv, *før* den kaller denne
    funksjonen, nettopp for å skille det gyldige utfallet (ingenting å generere)
    fra en reell feil her. Kalles funksjonen direkte uten den sjekken, gir ingen
    myk faktor også `None`, likt live-kontrakten.
    """
    tillatte = avveining.tillatte_påstander(kandidat, referanse)
    if not any(p.myk_faktor for p in tillatte):
        return None, tillatte
    data = {"kandidat": _poeng(kandidat), "referanse": _poeng(referanse) if referanse else None,
            "tillatte": [p.felt for p in tillatte]}
    forespørsel = adapter._forespørsel("avveining", avveining.PROMPT, data, avveining.skjema())  # noqa: SLF001
    svar = adapter._send(forespørsel, None)  # noqa: SLF001
    if isinstance(svar, Tolkefeil):
        return None, tillatte
    return les_jsoninnhold(svar, krev_unike_felt=True), tillatte


def main() -> int:
    # Uten dette skriver Python cp1252 gjennom en pipe på Windows, og de norske
    # tegnene blir feil i Git Bash (samme fallgruve som `adaptere.lagring.testdata`).
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send betalte modellkall mot OpenRouter.")
    parser.add_argument("--model", choices=["openai/gpt-6-luna"], default="openai/gpt-6-luna",
                        help="Bare Luna er godkjent for demoinnhold (AD-7, docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md).")
    args = parser.parse_args()

    if not args.live:
        print(f"Tørrkjøring: {len(PREFERANSER)} preferansetekster + 4 Avveininger (vakt #{VAKT}) mot "
             f"{args.model}, ingen nettverk eller nøkkel leses.")
        print(f"Ville skrevet: {DATA.relative_to(ROOT)}")
        return 0

    key, model = base.configuration(args.model)
    adapter = OpenRouterKiAdapter(key, model)

    print(f"Tolker {len(PREFERANSER)} fasittekster (PRD §4.5) med {model} ...")
    preferanser: dict[str, dict] = {}
    for nr, (tekst, _forventet_poeng) in PREFERANSER.items():
        resultat = adapter.tolk(tekst)
        if isinstance(resultat, Tolkefeil):
            print(f"FEIL ved tekst {nr}: {resultat.feiltype}", file=sys.stderr)
            return 2
        preferanser[tekst] = {"kategori": resultat.kategori, "begrunnelse": resultat.begrunnelse,
                              "modell": resultat.modell}
        print(f"  {nr:>2}. {resultat.kategori}")

    tempsti = BACKEND / f"_demoinnhold_tmp_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}.db"
    engine = lag_engine(tempsti)
    try:
        opprett_skjema(engine)
        grunnlag = rangert_grunnlag(engine)
        tolkede = {}
        for ansatt_id, nr in PREFERANSENUMMER.items():
            tekst = PREFERANSER[nr][0]
            lagret = preferanser[tekst]
            tolkede[ansatt_id] = TolketPreferanse(**lagret)
        rangert = gyldige_rangert(grunnlag, tolkede)
    finally:
        engine.dispose()
        tempsti.unlink(missing_ok=True)

    print(f"Genererer Avveininger for {len(rangert)} Gyldige kandidater på vakt #{VAKT} ...")
    avveininger: dict[str, dict] = {}
    for kandidat in rangert:
        referanse = referanse_for(rangert, kandidat.id)
        tillatte = avveining.tillatte_påstander(kandidat, referanse)
        if not any(p.myk_faktor for p in tillatte):
            # Gyldig utfall, likt live-kontrakten (ikke en feil): ingen myk faktor i det
            # hele tatt gir alltid `None` fra `forklar()`, så det er ikke noe å generere
            # eller lagre for denne kandidaten.
            print(f"  kandidat {kandidat.id} ({kandidat.navn}): ingen myk faktor, ingen Avveining å lagre")
            continue
        rått, _ = rått_avveiningssvar(adapter, kandidat, referanse)
        if rått is None:
            print(f"FEIL ved Avveining for kandidat {kandidat.id} ({kandidat.navn}): ingen bruksbart svar",
                 file=sys.stderr)
            return 2
        if avveining.valider(rått, tillatte) is None:
            print(f"ADVARSEL: Avveining for kandidat {kandidat.id} ({kandidat.navn}) består ikke "
                 "faktakontrollen og lagres ikke; demo faller tilbake til mal for denne.", file=sys.stderr)
            continue
        nøkkel = f"{kandidat.id}:{'' if referanse is None else referanse.id}"
        avveininger[nøkkel] = rått
        print(f"  kandidat {kandidat.id} ({kandidat.navn}) mot referanse "
             f"{referanse.id if referanse else None}: lagret")

    data = {
        "kontraktsversjon": KONTRAKTSVERSJON,
        "modell": model,
        "generert": date.today().isoformat(),
        "kommando": "python scripts/generer_demoinnhold.py --live",
        "preferanser": preferanser,
        "avveininger": avveininger,
    }
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Skrevet: {DATA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
