"""Strukturerte påstander om allerede beregnede fakta (FR-11, P-06/P-07).

Modellen velger blant sanne påstander. Ved mottak sammenlignes hele svaret
med de samme tillatte påstandene, også for en eventuell forhåndsgenerert tekst.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import Literal

from domene.porter.rangering import RangertKandidat

FAKTORNAVN = {
    "kostnad": "Kostnadspoengene",
    "timebelastning": "Timebelastningspoengene",
    "ulempe": "Ulempescoren",
    "preferanse": "Preferansepoengene",
}
SCORENAVN = {**FAKTORNAVN, "total": "Totalscoren"}
PROMPT = """Velg korte, relevante påstander fra listen over tillatte påstander for denne kandidaten.
Velg minst én påstand om en myk faktor. Vis gjerne både en styrke og en svakhet.
Kopier de valgte objektene uendret til paastander. Ikke skriv fritekst eller beregn nye fakta."""

Retning = Literal["opp", "ned"]


def faktorretninger(kandidat: RangertKandidat) -> dict[str, Retning]:
    """Egne faktorpoeng mot egen eksakt total. Nullvekt har ingen retning."""
    resultat: dict[str, Retning] = {}
    poeng = kandidat.eksakte_poeng
    for faktor in FAKTORNAVN:
        verdi = getattr(poeng, faktor)
        if faktor in kandidat.aktive_faktorer and verdi != poeng.total:
            resultat[faktor] = "opp" if verdi > poeng.total else "ned"
    return resultat


def skjema() -> dict:
    def objekt(felt):
        return {"type": "object", "properties": felt, "required": list(felt), "additionalProperties": False}

    def valg(*verdier):
        return {"type": "string", "enum": list(verdier)}

    kandidat = {"kandidat_id": {"type": "integer"}}
    regler = objekt({"type": valg("regler"), **kandidat})
    egen = objekt({"type": valg("egen"), **kandidat, "faktor": valg(*FAKTORNAVN), "retning": valg("opp", "ned")})
    sammenligning = objekt({
        "type": valg("sammenligning"), **kandidat, "referanse_id": {"type": "integer"},
        "faktor": valg(*SCORENAVN), "retning": valg("høyere", "lavere", "lik"),
    })
    return objekt({"paastander": {"type": "array", "items": {"anyOf": [regler, egen, sammenligning]}}})


@dataclass(frozen=True)
class Påstand:
    felt: dict[str, str | int]
    tekst: str
    myk_faktor: bool = False  # Teller mot kravet om en myk faktor med positiv vekt.


def _poeng(verdi: Fraction) -> str:
    # Samme numeriske visningsverdi og avrunding som Intl.NumberFormat i tabellen.
    vist = Decimal(str(float(verdi))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return str(vist).replace(".", ",")


def tillatte_påstander(kandidat: RangertKandidat, referanse: RangertKandidat | None) -> list[Påstand]:
    identitet = {"kandidat_id": kandidat.id}
    poeng = kandidat.eksakte_poeng
    tillatte = [Påstand({"type": "regler", **identitet},
                        f"{kandidat.navn} oppfyller kompetansekravet, har ingen kolliderende vakt "
                        "og oppfyller 11- og 35-timersreglene i prototypen.")]
    for faktor, retning in faktorretninger(kandidat).items():
        verdi = _poeng(getattr(poeng, faktor))
        tillatte.append(Påstand({"type": "egen", **identitet, "faktor": faktor, "retning": retning},
                                f"{FAKTORNAVN[faktor]} ({verdi}) trekker {retning} "
                                f"sammenholdt med egen totalscore ({_poeng(poeng.total)}) før avrunding.",
                                myk_faktor=True))
    if referanse is not None:
        for faktor, navn in SCORENAVN.items():
            egen, annen = getattr(poeng, faktor), getattr(referanse.eksakte_poeng, faktor)
            retning = "lik" if egen == annen else "høyere" if egen > annen else "lavere"
            forhold = {"lik": "på samme nivå som", "høyere": "høyere enn", "lavere": "lavere enn"}[retning]
            tillatte.append(Påstand({
                "type": "sammenligning", **identitet, "referanse_id": referanse.id, "faktor": faktor,
                "retning": retning,
            }, f"{navn} er {forhold} hos {referanse.navn} før avrunding "
               f"({_poeng(egen)} mot {_poeng(annen)}).", myk_faktor=faktor in kandidat.aktive_faktorer))
    return tillatte


def valider(svar: object, tillatte: list[Påstand]) -> list[str] | None:
    if not isinstance(svar, dict) or set(svar) != {"paastander"} or not isinstance(svar["paastander"], list):
        return None
    valgte = []
    for felt in svar["paastander"]:
        if not isinstance(felt, dict) or type(felt.get("kandidat_id")) is not int:
            return None
        if "referanse_id" in felt and type(felt["referanse_id"]) is not int:
            return None
        treff = next((p for p in tillatte if p.felt == felt), None)
        if treff is None:
            return None
        if treff not in valgte:
            valgte.append(treff)
    return [p.tekst for p in valgte] if any(p.myk_faktor for p in valgte) else None
