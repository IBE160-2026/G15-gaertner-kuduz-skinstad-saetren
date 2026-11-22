"""`DemoKiAdapter`: samme porter som `OpenRouterKiAdapter`, uten nettverk (AD-6, story 5.7).

Lar appen kjøre fra et rent klonet repo uten `OPENROUTER_API_KEY` (SM-9): ingen
nettverkskall, ingen venting og ingen begrenser. Leser forhåndsgenererte svar fra
`demoinnhold.json`, laget av `scripts/generer_demoinnhold.py` med ekte,
betalte kall mot `OpenRouterKiAdapter` og samme prompt som live (se
`docs/ki-logg/`), ikke håndskrevet.

To slag innhold, aldri blandet:

- Preferansetolkning: oppslag på selve teksten. Treffer den ikke (ukjent tekst),
  gir `tolk` en endelig `Tolkefeil("ubrukelig")`, akkurat som et ubrukelig
  live-svar ville gjort (P-05, AD-6 punkt 1). Ingen kategori diktes opp.
- Avveining: oppslag på `(kandidat_id, referanse_id)`. Et treff faktakontrolleres
  på nytt mot *gjeldende* tall med samme `avveining.valider`/`tillatte_påstander`
  som live (P-06) — mønsteret er `ForhåndsgenerertTestadapter` i
  `tester/ki/test_avveining.py`. Består den ikke, eller finnes det intet oppslag,
  settes svaret sammen av kode fra allerede godkjente påstander (`mal`), aldri
  fritekst eller KI-generert (AD-6). Har kandidaten ingen myk faktor-påstand i det
  hele tatt, er svaret `None`, likt dagens live-kontrakt (ingen demo-spesiell feil).

`ki_kilde` for ruten: `adaptere/api/main.py` kan ikke lese et vanlig returnert
attributt trygt, fordi `forklar()` bare får returnere `list[str] | None`
(samme form som `Forklarer`-protokollen, AD-6). Kilden for *siste* kall på denne
tråden står i `siste_kilde`, i en `threading.local`, satt rett før `forklar()`
returnerer og lest av ruten rett etter (synkron rute, ingen mellomliggende kall
på samme tråd). To samtidige forespørsler kjører på to forskjellige tråder, hver
med sin egen lokale verdi, så det er ikke en delt tilstand mellom forespørsler.
`OpenRouterKiAdapter` er uendret og har ikke dette attributtet; ruten faller
tilbake til `"live"` når attributtet mangler.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Literal

from adaptere.ki import avveining
from adaptere.ki.openrouter import STANDARD_MODELL, Tolkefeil
from domene.porter.rangering import RangertKandidat, TolketPreferanse
from domene.regelmotor.rangering import PREFERANSEPOENG

logger = logging.getLogger(__name__)

DATAFIL = Path(__file__).with_name("demoinnhold.json")
# Heves når formen på demoinnhold.json endres, slik at et eldre eller ødelagt
# datasett aldri blir lest som om det var dette formatet (P-06: ingen foreldet
# sammenligning vises). Må stemme med `KONTRAKTSVERSJON` i
# `scripts/generer_demoinnhold.py`.
KONTRAKTSVERSJON = 1

KiKilde = Literal["forhandsgenerert", "mal"]


def _tom_data() -> dict:
    # Et nytt dict ved hver feil, ikke en delt singleton: flere DemoKiAdapter-
    # instanser (f.eks. i tester) skal aldri kunne aliasere samme mutable dict.
    return {"preferanser": {}, "avveininger": {}}


def _nøkkel(kandidat_id: int, referanse_id: int | None) -> str:
    return f"{kandidat_id}:{'' if referanse_id is None else referanse_id}"


def _les_data(sti: Path) -> dict:
    try:
        rått = json.loads(sti.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning(
            "Demoinnhold mangler (%s). Demo-modus viser bare maltekst og "
            "«kunne ikke tolkes». Generer det med scripts/generer_demoinnhold.py --live.",
            sti,
        )
        return _tom_data()
    except (OSError, ValueError) as feil:
        logger.warning("Demoinnhold er ugyldig (%s): %s. Demo-modus viser bare maltekst.", sti, type(feil).__name__)
        return _tom_data()
    if not isinstance(rått, dict) or rått.get("kontraktsversjon") != KONTRAKTSVERSJON:
        logger.warning(
            "Demoinnhold har feil eller manglende kontraktsversjon (%s). Demo-modus viser bare maltekst. "
            "Generer det på nytt med scripts/generer_demoinnhold.py --live.", sti,
        )
        return _tom_data()
    return rått


class DemoKiAdapter:
    """`Tolker` og `Forklarer` uten nettverk. Samme form som `OpenRouterKiAdapter`.

    `modell` er modellen forhåndsinnholdet ble generert med (kildelinjen i
    frontend, UX-DR27) — DemoKiAdapter kaller aldri selv noen modell.
    """

    def __init__(self, datafil: Path = DATAFIL) -> None:
        data = _les_data(datafil)
        preferanser = data.get("preferanser")
        avveininger = data.get("avveininger")
        self._preferanser: dict[str, dict] = preferanser if isinstance(preferanser, dict) else {}
        self._avveininger: dict[str, dict] = avveininger if isinstance(avveininger, dict) else {}
        modell = data.get("modell")
        self.modell: str = modell if isinstance(modell, str) and modell else STANDARD_MODELL
        self.generert: str = data.get("generert", "") if isinstance(data.get("generert", ""), str) else ""
        self._lokal = threading.local()

    def __repr__(self) -> str:
        return f"DemoKiAdapter(modell={self.modell!r})"

    @property
    def siste_kilde(self) -> KiKilde | None:
        """Kilden for siste `forklar()`-kall på *denne* tråden. Se moduldocstringen."""
        return getattr(self._lokal, "kilde", None)

    def tolk(self, tekst: str) -> TolketPreferanse | Tolkefeil:
        lagret = self._preferanser.get(tekst)
        if not isinstance(lagret, dict):
            return Tolkefeil("ubrukelig")
        kategori, begrunnelse, modell = lagret.get("kategori"), lagret.get("begrunnelse"), lagret.get("modell")
        if (not isinstance(kategori, str) or kategori not in PREFERANSEPOENG
                or not isinstance(begrunnelse, str) or not begrunnelse.strip()
                or not isinstance(modell, str) or not modell.strip()):
            return Tolkefeil("ubrukelig")
        return TolketPreferanse(kategori=kategori, begrunnelse=begrunnelse, modell=modell)

    def forklar(self, kandidat: RangertKandidat, referanse: RangertKandidat | None) -> list[str] | None:
        tillatte = avveining.tillatte_påstander(kandidat, referanse)
        if not any(p.myk_faktor for p in tillatte):
            # Likt dagens live-kontrakt: ingen myk faktor i det hele tatt gir `None`,
            # ikke en demo-spesifikk feil (AD-6, matrisen).
            self._lokal.kilde = None
            return None
        lagret = self._avveininger.get(_nøkkel(kandidat.id, referanse.id if referanse is not None else None))
        if isinstance(lagret, dict):
            svar = avveining.valider(lagret, tillatte)
            if svar is not None:
                self._lokal.kilde = "forhandsgenerert"
                return svar
            logger.info(
                "Forhåndsgenerert Avveining for kandidat %s består ikke faktakontrollen mot gjeldende "
                "tall. Bruker mal.", kandidat.id,
            )
        self._lokal.kilde = "mal"
        return self._mal(tillatte)

    @staticmethod
    def _mal(tillatte: list[avveining.Påstand]) -> list[str]:
        """Satt sammen av kode fra allerede godkjente påstander, aldri fritekst (AD-6).

        Regelpåstanden (hvorfor kandidaten kan ta vakten) først, deretter opp til to
        myke faktor-påstander (gjerne en styrke og en svakhet, som i live-prompten),
        i den rekkefølgen `tillatte_påstander` gir dem. Minst én myk er garantert av
        kontrollen i `forklar()`.
        """
        regler = [p.tekst for p in tillatte if p.felt.get("type") == "regler"]
        myke = [p.tekst for p in tillatte if p.myk_faktor][:2]
        return regler + myke
