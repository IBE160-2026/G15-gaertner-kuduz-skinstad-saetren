"""Kandidatvurderingen: datafeilsjekk, alle harde regler og fast rekkefølge.

Grunnmønsteret for story 2.1–2.4. En ny hard regel legges inn som en `Regel` i
`REGLER`, med årsaken, sjekken og det regelen krever av grunnlaget. Vurderingen

1. tar bort den som var satt opp på Vakten (AV-06),
2. stopper med `Datafeil` før noen Kandidat vurderes, hvis grunnlaget er ukjent
   eller ugyldig (P-08). Vakten valideres først. Deretter regnes det samlede
   vinduet ut fra reglenes vinduer, og det må ligge innenfor datadekningen
   `[historikkstart, datagrense]`. Kandidatens vakter valideres bare innenfor
   vinduet (vedtak A5, PR #14),
3. vurderer hver Kandidat mot alle reglene og samler alle årsakene, uten å stoppe
   ved første brudd,
4. sorterer alfabetisk på navn i norsk rekkefølge, med id som likhetsbryter.

Alt er rent: ingen klokke, database, nett eller KI. Samme input gir samme output.
"""

import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

from domene.regelmotor import elleve_timer, kolliderende_vakt, kompetanse, trettifem_timer
from domene.typer import VAKTTYPER, Datafeil, Kandidat, Kandidatvurdering, Tidsrom, Utelukket, Vakt


@dataclass(frozen=True)
class Regel:
    """En hard regel.

    `bryter` avgjør om Kandidaten utelukkes. `vaktkrav` og `kandidatkrav` sier hva
    regelen trenger av grunnlaget, som tekst per feil. Tom liste betyr at
    grunnlaget holder.

    `vindu` er tidsrommet rundt Vakten der Kandidatens vakter kan påvirke regelen,
    i UTC, eller None når regelen ikke ser på vakter. Det kalles bare med en
    validert Vakt. Vaktene i vinduet må være gyldige, og vinduet må ligge innenfor
    datadekningen (P-08).
    """

    årsak: str
    bryter: Callable[[Kandidat, Vakt], bool]
    vaktkrav: Callable[[Vakt], list[str]]
    kandidatkrav: Callable[[Kandidat, Vakt], list[str]]
    vindu: Callable[[Vakt], Tidsrom | None]


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
        vindu=lambda _vakt: None,
    ),
    Regel(
        årsak=kolliderende_vakt.ÅRSAK,
        bryter=kolliderende_vakt.bryter_kollisjon,
        vaktkrav=lambda _vakt: [],
        kandidatkrav=lambda _kandidat, _vakt: [],
        vindu=kolliderende_vakt.vindu,
    ),
    Regel(
        årsak=elleve_timer.ÅRSAK,
        bryter=elleve_timer.bryter_elleve_timer,
        vaktkrav=lambda _vakt: [],
        kandidatkrav=lambda _kandidat, _vakt: [],
        vindu=elleve_timer.vindu,
    ),
    Regel(
        årsak=trettifem_timer.ÅRSAK,
        bryter=trettifem_timer.bryter_trettifem_timer,
        vaktkrav=lambda _vakt: [],
        kandidatkrav=lambda _kandidat, _vakt: [],
        vindu=trettifem_timer.vindu,
    ),
)


def _har_offset(tid: object) -> bool:
    return isinstance(tid, datetime) and tid.utcoffset() is not None


def vaktdatafeil(vakt: Vakt, datagrense: datetime, historikkstart: datetime) -> list[str]:
    """Krav til Vakten og datadekningen som gjelder alle reglene.

    Tidene sammenlignes i UTC. Med samme `tzinfo` sammenligner Python ellers
    veggklokka, og det blir feil i timen som går to ganger når sommertiden slutter.
    Om Vakten ligger innenfor datadekningen, avgjøres av vinduet (`vindusdatafeil`).
    """
    grunner: list[str] = []
    if vakt.vakttype not in VAKTTYPER:
        grunner.append(f"vakt {vakt.vaktnummer}: ukjent vakttype {vakt.vakttype!r}")
    tider = {"start": vakt.start, "slutt": vakt.slutt, "datagrense": datagrense, "historikkstart": historikkstart}
    uten_offset = [navn for navn, tid in tider.items() if not _har_offset(tid)]
    if uten_offset:
        grunner.append(f"vakt {vakt.vaktnummer}: {', '.join(uten_offset)} mangler tidssone")
        return grunner
    if not vakt.start.astimezone(UTC) < vakt.slutt.astimezone(UTC):
        grunner.append(f"vakt {vakt.vaktnummer}: start er ikke før slutt")
    return grunner


def samlet_vindu(vakt: Vakt, regler: tuple[Regel, ...]) -> Tidsrom:
    """Det minste tidsrommet i UTC som dekker Vakten og alle reglenes vinduer.

    Vakten er alltid med, så datadekningen sjekkes også når ingen regel har vindu.
    Krever en validert Vakt.
    """
    vinduer = [Tidsrom(vakt.start.astimezone(UTC), vakt.slutt.astimezone(UTC))]
    vinduer += [v for regel in regler if (v := regel.vindu(vakt)) is not None]
    return Tidsrom(
        start=min(v.start.astimezone(UTC) for v in vinduer),
        slutt=max(v.slutt.astimezone(UTC) for v in vinduer),
    )


def vindusdatafeil(vakt: Vakt, vindu: Tidsrom, datagrense: datetime, historikkstart: datetime) -> list[str]:
    """Vinduet er dekket når `historikkstart <= start` og `slutt <= datagrense` (P-08)."""
    grunner: list[str] = []
    if vindu.start < historikkstart.astimezone(UTC):
        grunner.append(
            f"vakt {vakt.vaktnummer}: vinduet starter {vindu.start.isoformat()}, "
            f"før historikkstarten {historikkstart.isoformat()}"
        )
    if vindu.slutt > datagrense.astimezone(UTC):
        grunner.append(
            f"vakt {vakt.vaktnummer}: vinduet slutter {vindu.slutt.isoformat()}, "
            f"etter datagrensen {datagrense.isoformat()}"
        )
    return grunner


def _egen_vakt_datafeil(kandidat: Kandidat, indeks: int, egen: object, vindu: Tidsrom) -> list[str]:
    """Det reglene krever av én av Kandidatens vakter, avgrenset til vinduet (P-08, A5).

    En vakt som ikke er et tidsrom eller mangler tidssone, kan ikke plasseres i tid
    og gir alltid datafeil. En vakt der `start >= slutt` gir datafeil bare når det
    lukkede tidsrommet mellom de to tidene overlapper det halvåpne vinduet: et punkt
    i vinduets start er innenfor, et punkt i vinduets slutt er utenfor.
    """
    ref = f"ansatt {kandidat.id}: vakt nr. {indeks + 1} i grunnlaget"
    if not isinstance(egen, Tidsrom):
        return [f"{ref} er ikke et tidsrom"]
    uten_offset = [navn for navn, tid in (("start", egen.start), ("slutt", egen.slutt)) if not _har_offset(tid)]
    if uten_offset:
        return [f"{ref}: {', '.join(uten_offset)} mangler tidssone"]
    start, slutt = egen.start.astimezone(UTC), egen.slutt.astimezone(UTC)
    if start < slutt:
        return []
    første, siste = min(start, slutt), max(start, slutt)
    if første < vindu.slutt and siste >= vindu.start:
        return [f"{ref}: start er ikke før slutt"]
    return []


def kandidatvaktdatafeil(kandidat: Kandidat, vindu: Tidsrom) -> list[str]:
    """Datafeil i Kandidatens vakter som kan påvirke reglene. Resten ignoreres."""
    return [g for i, egen in enumerate(kandidat.vakter) for g in _egen_vakt_datafeil(kandidat, i, egen, vindu)]


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
    historikkstart: datetime,
    regler: tuple[Regel, ...] = REGLER,
) -> Kandidatvurdering | Datafeil:
    """Vurder alle Ansatte unntatt den som var satt opp, mot alle reglene.

    Turnusgrunnlaget dekker `[historikkstart, datagrense]`. Ligger det samlede
    vinduet rundt Vakten utenfor, kan Vakten ikke vurderes (P-08). `Datafeil`
    oppgir alltid `datagrense`, også når det er historikkstarten som ikke holder.
    """
    grunnlag = sorted(
        (ansatt for ansatt in ansatte if ansatt.id != vakt.satt_opp_ansatt_id),
        key=norsk_sorteringsnøkkel,
    )

    # 1. Vakten først. Er tidene ugyldige, regnes ikke noe vindu ut.
    vaktgrunner = vaktdatafeil(vakt, datagrense, historikkstart)
    grunner = vaktgrunner + [g for regel in regler for g in regel.vaktkrav(vakt)]
    grunner += [g for kandidat in grunnlag for regel in regler for g in regel.kandidatkrav(kandidat, vakt)]
    if not vaktgrunner:
        # 2–4. Det samlede vinduet, datadekningen og Kandidatens vakter i vinduet.
        vindu = samlet_vindu(vakt, regler)
        grunner += vindusdatafeil(vakt, vindu, datagrense, historikkstart)
        grunner += [g for kandidat in grunnlag for g in kandidatvaktdatafeil(kandidat, vindu)]
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
