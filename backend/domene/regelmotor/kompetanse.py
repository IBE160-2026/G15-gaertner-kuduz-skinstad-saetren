"""Hard regel: kompetanse-minstekrav (FR2, story 2.1).

En Kandidat er gyldig når nivået for vakttypen er lik eller høyere enn Vaktens
minstenivå. Mellomvakten bruker nivået for dag (AV-02). Mangler nivået, er
Kandidaten ikke opplært for vakttypen og utelukkes. Minstekravet senkes aldri.
"""

from collections.abc import Mapping

from domene.typer import Kandidat, Vakt

ÅRSAK = "kompetanse-minstekrav"

# Nivåene 1–4: Under opplæring, Delvis opplært, Kvalifisert, Fullt kvalifisert.
LAVESTE_NIVÅ = 1
HØYESTE_NIVÅ = 4


def er_nivå(verdi: object) -> bool:
    """Et heltall 1–4. `True` og `"3"` er ikke nivåer."""
    return type(verdi) is int and LAVESTE_NIVÅ <= verdi <= HØYESTE_NIVÅ


def kompetansenøkkel(vakttype: str) -> str:
    """Nøkkelen i `Kandidat.kompetanse` for vakttypen. `mellom` bruker `dag`."""
    return "dag" if vakttype == "mellom" else vakttype


def kompetansenivå(kandidat: Kandidat, vakt: Vakt) -> int | None:
    """Kandidatens nivå for Vaktens vakttype, eller None når nivået mangler."""
    nivå = kandidat.kompetanse.get(kompetansenøkkel(vakt.vakttype))
    return nivå if er_nivå(nivå) else None


def bryter_kompetanse(kandidat: Kandidat, vakt: Vakt) -> bool:
    nivå = kompetansenivå(kandidat, vakt)
    return nivå is None or nivå < vakt.minstenivå


def kompetansedatafeil(kandidat: Kandidat, _vakt: Vakt) -> list[str]:
    """Det regelen krever av Kandidatens data: nivåer som er heltall 1–4.

    En manglende nøkkel er ikke en datafeil, men en utelukkelse.
    """
    if not isinstance(kandidat.kompetanse, Mapping):
        return [f"ansatt {kandidat.id}: kompetanse er ikke en tabell"]
    return [
        f"ansatt {kandidat.id}: kompetanse[{nøkkel!r}] = {verdi!r} er ikke et nivå 1–4"
        for nøkkel, verdi in kandidat.kompetanse.items()
        if not er_nivå(verdi)
    ]
