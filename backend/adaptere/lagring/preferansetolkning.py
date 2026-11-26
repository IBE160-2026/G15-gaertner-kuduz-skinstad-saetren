"""Lagring og lesing av preferansetolkninger på `ansatt` (story 5.1, AD-2, AD-5, P-05).

Lagringsadapteren lager aldri en ny tolkning. Den lagrer sluttresultatet fra
`adaptere/ki` og deserialiserer en tidligere lagret, vellykket verdi for samme
Ansatt og samme tekst. En lagret verdi brukes bare når alt stemmer: formatversjon
`TOLKEFORMAT`, hash lik SHA-256 av gjeldende tekst, kategori i `PREFERANSEPOENG`,
ikke-tom begrunnelse og modell, og ingen feil samtidig. Alt annet gir
`venter_paa_tolkning`, og teksten tolkes på nytt ved neste oppstart.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from adaptere.lagring.modeller import AnsattRad
from domene.porter.rangering import TolketPreferanse
from domene.regelmotor.rangering import PREFERANSEPOENG

TOLKEFORMAT = 1


def teksthash(tekst: str) -> str:
    return sha256(tekst.encode("utf-8")).hexdigest()


def har_tekst(tekst: str | None) -> bool:
    return tekst is not None and bool(tekst.strip())


def _ikke_tom(verdi: object) -> bool:
    return isinstance(verdi, str) and bool(verdi.strip())


def les_tolkning(rad: AnsattRad) -> TolketPreferanse | Literal["feilet"] | None:
    """Gyldig lagret tolkning, `"feilet"` for en gyldig lagret feil, ellers None (venter).

    None gjelder også rader uten tekst; domenet gir dem `ingen_registrert`.
    """
    tekst = rad.preferanse
    if not har_tekst(tekst) or rad.tolkeformat != TOLKEFORMAT:
        return None
    assert tekst is not None
    if rad.tolket_teksthash != teksthash(tekst):
        return None
    tolket = (rad.tolket_kategori, rad.tolket_begrunnelse, rad.tolket_modell)
    if _ikke_tom(rad.tolkefeil):
        return "feilet" if tolket == (None, None, None) else None
    if rad.tolkefeil is not None:
        return None
    if (rad.tolket_kategori not in PREFERANSEPOENG or not _ikke_tom(rad.tolket_begrunnelse)
            or not _ikke_tom(rad.tolket_modell)):
        return None
    assert rad.tolket_kategori is not None and rad.tolket_begrunnelse is not None and rad.tolket_modell is not None
    return TolketPreferanse(
        kategori=rad.tolket_kategori, begrunnelse=rad.tolket_begrunnelse, modell=rad.tolket_modell,
    )


@dataclass(frozen=True)
class Tolkninger:
    tolkede: dict[int, TolketPreferanse]
    feilede: frozenset[int]


def tolkninger(rader: Iterable[AnsattRad]) -> Tolkninger:
    """`tolkede` og `feilede` for `ranger`, fra de samme radene som Kandidatene."""
    tolkede: dict[int, TolketPreferanse] = {}
    feilede: set[int] = set()
    for rad in rader:
        tolkning = les_tolkning(rad)
        if isinstance(tolkning, TolketPreferanse):
            tolkede[rad.id] = tolkning
        elif tolkning == "feilet":
            feilede.add(rad.id)
    return Tolkninger(tolkede=tolkede, feilede=frozenset(feilede))


def ventende_tekster(session: Session) -> list[tuple[int, str]]:
    """(ansatt-id, tekst) for hver registrert tekst uten gyldig tolkning eller med feil.

    En per Ansatt, også når to har samme tekst. Lagrede feil tas med, så de prøves
    på nytt ved neste oppstart.
    """
    return [
        (rad.id, rad.preferanse)
        for rad in session.scalars(select(AnsattRad).order_by(AnsattRad.id))
        if rad.preferanse is not None and har_tekst(rad.preferanse)
        and not isinstance(les_tolkning(rad), TolketPreferanse)
    ]


def tilstandsmerke(rad: AnsattRad) -> tuple[object, ...]:
    """Tolkningskolonnene og `preferanseversjon`, i samme rekkefølge som `_MERKEKOLONNER`."""
    return (rad.tolket_teksthash, rad.tolkeformat, rad.tolket_kategori,
            rad.tolket_begrunnelse, rad.tolket_modell, rad.tolkefeil, rad.preferanseversjon)


_MERKEKOLONNER = (AnsattRad.tolket_teksthash, AnsattRad.tolkeformat, AnsattRad.tolket_kategori,
                  AnsattRad.tolket_begrunnelse, AnsattRad.tolket_modell, AnsattRad.tolkefeil,
                  AnsattRad.preferanseversjon)


def lagre_resultat(
    okter: sessionmaker[Session], ansatt_id: int, tekst: str, resultat: TolketPreferanse | str,
    forventet: tuple[object, ...] | None = None, *, versjon: int | None = None,
) -> bool:
    """Lagrer sluttresultatet for `tekst`. `resultat` er tolkningen eller feiltypen.

    Én betinget UPDATE i en kort transaksjon, åpnet etter KI-kallet. Er teksten
    eller `preferanseversjon` endret siden den ble lest, treffer den 0 rader,
    resultatet forkastes og funksjonen gir False. Versjonen sammenlignes alltid
    (story 5.9): enten som del av `forventet` fra `tilstandsmerke`, eller som
    `versjon` når `forventet` mangler. Uten noen av dem avvises kallet. Suksess
    nullstiller `tolkefeil`; feil nullstiller kategori, begrunnelse og modell.
    """
    if forventet is None and versjon is None:
        raise ValueError("forventet eller versjon må oppgis, så et svar på en eldre versjon forkastes")
    if isinstance(resultat, TolketPreferanse):
        verdier = {"tolket_kategori": resultat.kategori, "tolket_begrunnelse": resultat.begrunnelse,
                   "tolket_modell": resultat.modell, "tolkefeil": None}
    else:
        if not _ikke_tom(resultat):
            raise ValueError("feiltypen kan ikke være tom")
        verdier = {"tolket_kategori": None, "tolket_begrunnelse": None, "tolket_modell": None,
                   "tolkefeil": resultat}
    with okter.begin() as session:
        sporring = update(AnsattRad).where(AnsattRad.id == ansatt_id, AnsattRad.preferanse == tekst)
        if forventet is not None:
            for kolonne, verdi in zip(_MERKEKOLONNER, forventet, strict=True):
                sporring = sporring.where(kolonne == verdi)
        if versjon is not None:
            sporring = sporring.where(AnsattRad.preferanseversjon == versjon)
        utfall = session.execute(sporring.values(**verdier, tolket_teksthash=teksthash(tekst), tolkeformat=TOLKEFORMAT))
        return utfall.rowcount == 1


def normaliser_tekst(tekst: str) -> str | None:
    """Trimmet tekst, eller None når den er tom (story 5.9: «Ingen registrert»)."""
    trimmet = tekst.strip()
    return trimmet or None


def lagre_tekst(
    okter: sessionmaker[Session], ansatt_id: int, tekst: str,
    tillatt: Callable[[Session], bool] | None = None,
) -> int | Literal["uendret", "ikke_funnet"]:
    """Lagrer en ny preferansetekst for Ansatt `ansatt_id` (story 5.9, P-10B).

    Én skrivetransaksjon (`BEGIN IMMEDIATE`, AD-5). `tillatt` kjøres først i samme
    transaksjon; gir den False, eller finnes ikke Ansatt, endres ingenting og
    svaret er `"ikke_funnet"`. Teksten trimmes, og tom tekst lagres som None. Er
    den lik den lagrede, er kallet en no-op og svaret `"uendret"`. Ellers lagres
    teksten, alle `tolket_*`-kolonner, `tolkefeil` og `tolkeformat` nullstilles, og
    `preferanseversjon` øker med 1. Svaret er den nye versjonen.
    """
    ny = normaliser_tekst(tekst)
    with okter() as session:
        session.connection().exec_driver_sql("BEGIN IMMEDIATE")
        if tillatt is not None and not tillatt(session):
            return "ikke_funnet"
        rad = session.get(AnsattRad, ansatt_id)
        if rad is None:
            return "ikke_funnet"
        if rad.preferanse == ny:
            return "uendret"
        versjon = rad.preferanseversjon + 1
        session.execute(update(AnsattRad).where(AnsattRad.id == ansatt_id).values(
            preferanse=ny, preferanseversjon=versjon, tolket_kategori=None, tolket_begrunnelse=None,
            tolket_modell=None, tolket_teksthash=None, tolkefeil=None, tolkeformat=None,
        ))
        session.commit()
        return versjon
