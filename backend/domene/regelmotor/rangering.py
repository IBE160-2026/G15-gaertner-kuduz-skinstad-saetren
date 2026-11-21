"""Rangering av Gyldige kandidater (FR9, PRD §4.4, story 4.4).

Totalscore = 0,40 × kostnadspoeng + 0,20 × timebelastningspoeng
           + 0,15 × Ulempescore + 0,25 × preferansepoeng.

- Kostnad (som `float`, referatet §11) og timer i startuka normaliseres med
  min–maks over alle Gyldige: lavest gir 100, høyest 0. Er alle like, også når
  bare én er gyldig, får alle 50 for faktoren (AV-05).
- Ulempescoren har fast skala: maks(0, 100 × (1 − poeng / tak)), med taket fra
  parameterne (AV-11). Den regnes på nytt her, så et annet tak virker.
- Preferansen gir 100/75/50/25/0 etter tolket kategori. Uten tolkning gir den 50
  med egen status (P-05). Kompetanse gir ingen poeng (FR2).

Alle faktorpoeng og totalscoren regnes eksakt med `Fraction` fra inndataene, slik
de faktisk er lagret som `float` eller `timedelta`. Lik totalscore betyr eksakt lik
`Fraction`, uten toleranse, og da sorteres det på stigende ansatt-ID (AV-05, K-03,
vedtatt av Johannes 2026-11-15). Verdiene gjøres om til `float` først i porten.

Ren Python uten KI, klokke eller database (AD-1, NFR1). Samme input gir samme
rekkefølge uansett rekkefølgen kandidatene kommer inn i.
"""

import math
from collections.abc import Mapping, Set
from dataclasses import dataclass, fields
from datetime import timedelta
from fractions import Fraction
from types import MappingProxyType

from domene.porter.rangering import EksaktePoeng, RangertKandidat, TolketPreferanse, Tolkestatus
from domene.regelmotor import ulempebelastning
from domene.regelmotor.kompetanse import kompetansenivå
from domene.regelmotor.kostnad import beregn_kostnad
from domene.regelmotor.timebelastning import timebelastning
from domene.regelmotor.timer_i_uka import timer_i_startuka
from domene.typer import Kandidat, Kandidatvurdering, Vakt

# PRD §4.5, FR-10. Nøklene er kategoriene fra modelltestene (`scripts/modelltest_prd_fasit.json`).
PREFERANSEPOENG: Mapping[str, int] = MappingProxyType({
    "onsker_flere": 100,
    "positiv_ved_behov": 75,
    "noytral": 50,
    "foretrekker_a_slippe": 25,
    "vil_unnga": 0,
})
# Midlertidige poeng uten tolkning, og faktorpoeng når alle har lik verdi (P-05, AV-05).
MIDTPOENG = Fraction(50)
_MIKROSEKUND = timedelta(microseconds=1)


def _er_brøk(verdi: object) -> bool:
    return isinstance(verdi, (Fraction, int)) and not isinstance(verdi, bool)


@dataclass(frozen=True)
class Rangeringsparametere:
    """Vektene og ulempetaket (AV-11). Navngitte domeneparametere, ikke miljøvariabler.

    Vektene er `Fraction` (eller heltall), så summen er eksakt. `Fraction(0.4)` er
    ikke 2/5, og derfor avvises `float`. Vektene må være ikke-negative og summere
    til 1, slik at totalscoren holder seg på 0–100.
    """

    kostnadsvekt: Fraction = Fraction(2, 5)
    timebelastningsvekt: Fraction = Fraction(1, 5)
    ulempevekt: Fraction = Fraction(3, 20)
    preferansevekt: Fraction = Fraction(1, 4)
    tak: float = ulempebelastning.STANDARD_TAK

    def __post_init__(self) -> None:
        vekter = [getattr(self, f.name) for f in fields(self) if f.name.endswith("vekt")]
        if not all(_er_brøk(v) and v >= 0 for v in vekter):
            raise ValueError("vektene må være ikke-negative Fraction eller heltall")
        if sum(vekter) != 1:
            raise ValueError("vektene må summere til 1")
        tak = self.tak
        if (isinstance(tak, bool) or not isinstance(tak, (int, float, Fraction))
                or not math.isfinite(tak) or tak <= 0):
            raise ValueError("tak må være et positivt, endelig tall")


STANDARD_PARAMETERE = Rangeringsparametere()
_INGEN_TOLKNINGER: Mapping[int, TolketPreferanse] = MappingProxyType({})


def minmaks(verdier: Mapping[int, Fraction]) -> dict[int, Fraction]:
    """Lavest verdi gir 100, høyest 0, lineært imellom. Like verdier gir 50 for alle (AV-05)."""
    if not verdier:
        return {}
    lav, høy = min(verdier.values()), max(verdier.values())
    if lav == høy:
        return dict.fromkeys(verdier, MIDTPOENG)
    return {nøkkel: 100 * (høy - verdi) / (høy - lav) for nøkkel, verdi in verdier.items()}


def ulempescore(poeng: float, tak: float) -> Fraction:
    """maks(0, 100 × (1 − poeng / tak)), eksakt fra `float`-verdiene (AV-11)."""
    return max(Fraction(0), 100 * (1 - Fraction(poeng) / Fraction(tak)))


def totalscore(
    kostnadspoeng: Fraction,
    timebelastningspoeng: Fraction,
    ulempescore_: Fraction,
    preferansepoeng: Fraction,
    parametere: Rangeringsparametere = STANDARD_PARAMETERE,
) -> Fraction:
    """Den vektede summen av de fire faktorene, eksakt (PRD §4.4)."""
    p = parametere
    return (p.kostnadsvekt * kostnadspoeng + p.timebelastningsvekt * timebelastningspoeng
            + p.ulempevekt * ulempescore_ + p.preferansevekt * preferansepoeng)


def preferanse(
    kandidat: Kandidat, tolkede: Mapping[int, TolketPreferanse], feilede: Set[int],
) -> tuple[Fraction, Tolkestatus, TolketPreferanse | None]:
    """Preferansepoeng og tolkestatus for én Kandidat (P-05).

    Uten registrert tekst (None, tom eller bare mellomrom) er statusen «ingen
    registrert», også om det finnes en gammel tolkning. En lagret tolkning gir
    kategoriens poeng. En kategori som ikke finnes i `PREFERANSEPOENG`, er en
    ugyldig tolkning og følger feilflyten, som en Kandidat i `feilede`. Ellers
    venter teksten på tolkning. Ingen status utelukker Kandidaten.
    """
    tekst = kandidat.preferanse
    if tekst is None or not tekst.strip():
        return MIDTPOENG, Tolkestatus.INGEN_REGISTRERT, None
    tolkning = tolkede.get(kandidat.id)
    if tolkning is not None:
        if tolkning.kategori in PREFERANSEPOENG:
            return Fraction(PREFERANSEPOENG[tolkning.kategori]), Tolkestatus.TOLKET, tolkning
        return MIDTPOENG, Tolkestatus.KUNNE_IKKE_TOLKES, None
    if kandidat.id in feilede:
        return MIDTPOENG, Tolkestatus.KUNNE_IKKE_TOLKES, None
    return MIDTPOENG, Tolkestatus.VENTER_PAA_TOLKNING, None


def ranger(
    vurdering: Kandidatvurdering,
    vakt: Vakt,
    tolkede: Mapping[int, TolketPreferanse] = _INGEN_TOLKNINGER,
    feilede: Set[int] = frozenset(),
    parametere: Rangeringsparametere = STANDARD_PARAMETERE,
) -> tuple[RangertKandidat, ...]:
    """Ranger alle Gyldige kandidater i `vurdering`, høyest totalscore først.

    Bare `vurdering.gyldige` rangeres. Utelukkede er en egen type og kan ikke komme
    med (NFR2). `tolkede` og `feilede` gjelder per ansatt-ID, og ID-er som ikke er
    gyldige, ignoreres. Krever at vurderingen kommer fra `vurder_kandidater`, så
    grunnlaget er validert (P-08). Ingen Gyldige gir en tom tuple.
    """
    gyldige = sorted(vurdering.gyldige, key=lambda k: k.id)
    kostnader = {k.id: beregn_kostnad(k, vakt) for k in gyldige}
    timer = {k.id: timer_i_startuka(k, vakt) for k in gyldige}

    kostnadspoeng = minmaks({i: Fraction(float(kostnad.total)) for i, kostnad in kostnader.items()})
    timepoeng = minmaks({i: Fraction(tid // _MIKROSEKUND) for i, tid in timer.items()})

    beregnet = []
    for k in gyldige:
        ulempe = vurdering.ulempe_per_kandidat[k.id]
        score = ulempescore(ulempe.poeng, parametere.tak)
        pref, status, tolkning = preferanse(k, tolkede, feilede)
        total = totalscore(kostnadspoeng[k.id], timepoeng[k.id], score, pref, parametere)
        beregnet.append((k, total, score, pref, status, tolkning))

    # Synkende totalscore, så stigende ansatt-ID ved eksakt lik `Fraction` (AV-05, K-03).
    beregnet.sort(key=lambda rad: (-rad[1], rad[0].id))

    resultat = []
    aktive_faktorer = frozenset(navn for navn, vekt in (
        ("kostnad", parametere.kostnadsvekt), ("timebelastning", parametere.timebelastningsvekt),
        ("ulempe", parametere.ulempevekt), ("preferanse", parametere.preferansevekt),
    ) if vekt > 0)
    for plass, (k, total, score, pref, status, tolkning) in enumerate(beregnet, start=1):
        kostnad = kostnader[k.id]
        ulempe = vurdering.ulempe_per_kandidat[k.id]
        belastning = timebelastning(timer[k.id])
        nivå = kompetansenivå(k, vakt)
        if nivå is None:
            raise ValueError(f"ansatt {k.id} er gyldig uten kompetansenivå for vakttypen")
        resultat.append(RangertKandidat(
            plass=plass, id=k.id, navn=k.navn, stilling=k.stilling, ansiennitet=k.ansiennitet,
            kompetansenivå=nivå,
            kostnad=float(kostnad.total), ordinære_timer=float(kostnad.ordinære_timer),
            overtidstimer=float(kostnad.overtidstimer),
            kostnadstype="inkluderer_overtid" if kostnad.overtidstimer > 0 else "ordinær",
            timer_i_uka=timer[k.id] / timedelta(hours=1),
            timebelastning_prosent=belastning.prosent, høy_belastning=belastning.høy,
            ulempepoeng=ulempe.poeng, kveldstimer=ulempe.kveldstimer, helgetimer=ulempe.helgetimer,
            natttimer=ulempe.natttimer,
            kostnadspoeng=float(kostnadspoeng[k.id]), timebelastningspoeng=float(timepoeng[k.id]),
            ulempescore=float(score), preferansepoeng=float(pref), totalscore=float(total),
            tolkestatus=status, tolket_preferanse=tolkning,
            eksakte_poeng=EksaktePoeng(kostnadspoeng[k.id], timepoeng[k.id], score, pref, total),
            aktive_faktorer=aktive_faktorer,
        ))
    return tuple(resultat)
