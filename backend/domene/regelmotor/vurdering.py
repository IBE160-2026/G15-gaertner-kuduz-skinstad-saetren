"""Kandidatvurderingen: datafeilsjekk, alle harde regler og fast rekkefølge.

Grunnmønsteret for story 2.1–2.4. En ny hard regel legges inn som en `Regel` i
`REGLER`, med årsaken, sjekken og det regelen krever av grunnlaget. Vurderingen

1. tar bort den som var satt opp på Vakten (AV-06),
2. stopper med `Datafeil` før noen Kandidat vurderes, hvis grunnlaget er ukjent
   eller ugyldig (P-08),
3. vurderer hver Kandidat mot alle reglene og samler alle årsakene, uten å stoppe
   ved første brudd,
4. sorterer alfabetisk på navn i norsk rekkefølge, med id som likhetsbryter.

Alt er rent: ingen klokke, database, nett eller KI. Samme input gir samme output.
"""

import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

from domene.regelmotor import kompetanse
from domene.typer import VAKTTYPER, Datafeil, Kandidat, Kandidatvurdering, Utelukket, Vakt


@dataclass(frozen=True)
class Regel:
    """En hard regel.

    `bryter` avgjør om Kandidaten utelukkes. `vaktkrav` og `kandidatkrav` sier hva
    regelen trenger av grunnlaget, som tekst per feil. Tom liste betyr at
    grunnlaget holder.
    """

    årsak: str
    bryter: Callable[[Kandidat, Vakt], bool]
    vaktkrav: Callable[[Vakt], list[str]]
    kandidatkrav: Callable[[Kandidat, Vakt], list[str]]


def _minstenivå_krav(vakt: Vakt) -> list[str]:
    if kompetanse.er_nivå(vakt.minstenivå):
        return []
    return [f"vakt {vakt.vaktnummer}: minstenivå {vakt.minstenivå!r} er ikke et nivå 1–4"]


REGLER: tuple[Regel, ...] = (
    Regel(
        årsak=kompetanse.ÅRSAK,
        bryter=kompetanse.bryter_kompetanse,
        vaktkrav=_minstenivå_krav,
        kandidatkrav=kompetanse.kompetansedatafeil,
    ),
)


def _har_offset(tid: object) -> bool:
    return isinstance(tid, datetime) and tid.utcoffset() is not None


def vaktdatafeil(vakt: Vakt, datagrense: datetime) -> list[str]:
    """Krav til Vakten som gjelder alle reglene.

    Tidene sammenlignes i UTC. Med samme `tzinfo` sammenligner Python ellers
    veggklokka, og det blir feil i timen som går to ganger når sommertiden slutter.
    """
    grunner: list[str] = []
    if vakt.vakttype not in VAKTTYPER:
        grunner.append(f"vakt {vakt.vaktnummer}: ukjent vakttype {vakt.vakttype!r}")
    tider = {"start": vakt.start, "slutt": vakt.slutt, "datagrense": datagrense}
    uten_offset = [navn for navn, tid in tider.items() if not _har_offset(tid)]
    if uten_offset:
        grunner.append(f"vakt {vakt.vaktnummer}: {', '.join(uten_offset)} mangler tidssone")
        return grunner
    start, slutt, grense = (tid.astimezone(UTC) for tid in tider.values())
    if not start < slutt:
        grunner.append(f"vakt {vakt.vaktnummer}: start er ikke før slutt")
    if slutt > grense:
        grunner.append(f"vakt {vakt.vaktnummer}: slutter etter datagrensen {datagrense.isoformat()}")
    return grunner


# Norsk alfabet: æ, ø og å kommer etter z. Bokstaver med andre tegn over seg
# sorteres som grunnbokstaven (é som e). ä, ö og ü følger norsk praksis.
_ALFABET = "abcdefghijklmnopqrstuvwxyzæøå"
_PLASS = {bokstav: indeks for indeks, bokstav in enumerate(_ALFABET)}
_SOM = {"ä": "æ", "ö": "ø", "ü": "y"}


def _tegnnøkkel(tegn: str) -> tuple[int, int]:
    tegn = _SOM.get(tegn, tegn)
    if tegn not in _PLASS:
        tegn = unicodedata.normalize("NFD", tegn)[0]
    if tegn in _PLASS:
        return (1, _PLASS[tegn])
    # Mellomrom, bindestrek og andre tegn kommer før bokstavene.
    return (0, ord(tegn))


def norsk_sorteringsnøkkel(kandidat: Kandidat) -> tuple[tuple[tuple[int, int], ...], str, int]:
    """Alfabetisk på navn i norsk rekkefølge, uavhengig av maskinens locale.

    Navnet normaliseres til NFC først, så «Å» skrevet som A + ring (U+030A)
    sorteres som å. «aa» sorteres som to a-er, ikke som å: «Nygaard» kommer før
    «Nygård». Navn som bare skiller seg på store og små bokstaver, ordnes på
    teksten, og helt like navn på id.
    """
    navn = unicodedata.normalize("NFC", kandidat.navn)
    return (tuple(_tegnnøkkel(t) for t in navn.casefold()), navn, kandidat.id)


def vurder_kandidater(
    vakt: Vakt,
    ansatte: Iterable[Kandidat],
    datagrense: datetime,
    regler: tuple[Regel, ...] = REGLER,
) -> Kandidatvurdering | Datafeil:
    """Vurder alle Ansatte unntatt den som var satt opp, mot alle reglene.

    `datagrense` er der turnusgrunnlaget slutter. En Vakt som slutter etter den,
    kan ikke vurderes (P-08).
    """
    grunnlag = sorted(
        (ansatt for ansatt in ansatte if ansatt.id != vakt.satt_opp_ansatt_id),
        key=norsk_sorteringsnøkkel,
    )

    grunner = vaktdatafeil(vakt, datagrense)
    grunner += [g for regel in regler for g in regel.vaktkrav(vakt)]
    grunner += [g for kandidat in grunnlag for regel in regler for g in regel.kandidatkrav(kandidat, vakt)]
    if grunner:
        return Datafeil(datagrense=datagrense, grunner=tuple(grunner))

    gyldige: list[Kandidat] = []
    utelukkede: list[Utelukket] = []
    for kandidat in grunnlag:
        årsaker = tuple(regel.årsak for regel in regler if regel.bryter(kandidat, vakt))
        if årsaker:
            utelukkede.append(Utelukket(kandidat=kandidat, årsaker=årsaker))
        else:
            gyldige.append(kandidat)
    return Kandidatvurdering(gyldige=tuple(gyldige), utelukkede=tuple(utelukkede))
