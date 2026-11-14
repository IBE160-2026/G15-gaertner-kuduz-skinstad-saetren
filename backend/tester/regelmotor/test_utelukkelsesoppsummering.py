"""`lag_utelukkelsesoppsummering` (story 2.5, UX-DR15).

Bare enhetsdata i domenet. Fasiten for #4127 og #4189 testes gjennom API-et i
`tester/api/test_kandidater.py`. Import-forbudet mot `adaptere` for hele `domene/`
dekkes av `tester/test_arkitektur.py` og dupliseres ikke her.
"""

from domene.porter.utelukkelse import EkskludertKandidat, RegelAntall, UtelukkelsesOppsummering
from domene.regelmotor.vurdering import REGLER, Regel, lag_utelukkelsesoppsummering
from domene.typer import Kandidat, Kandidatvurdering, Utelukket


def kandidat(id: int, navn: str) -> Kandidat:
    return Kandidat(id=id, navn=navn, kompetanse={})


def test_ingen_utelukkede_gir_tom_oppsummering() -> None:
    vurdering = Kandidatvurdering(gyldige=(kandidat(1, "Ada"),), utelukkede=())

    oppsummering = lag_utelukkelsesoppsummering(vurdering)

    assert oppsummering == UtelukkelsesOppsummering(
        totalt=0,
        per_regel=tuple(RegelAntall(årsak=regel.årsak, antall=0) for regel in REGLER),
        utelukkede=(),
    )


def test_én_regel_telles_i_totalen_og_under_regelen() -> None:
    a, b = kandidat(1, "Ada"), kandidat(2, "Bea")
    vurdering = Kandidatvurdering(
        gyldige=(),
        utelukkede=(
            Utelukket(kandidat=a, årsaker=("kompetanse-minstekrav",)),
            Utelukket(kandidat=b, årsaker=("kolliderende vakt",)),
        ),
    )

    oppsummering = lag_utelukkelsesoppsummering(vurdering)

    assert oppsummering.totalt == 2
    per_regel = {r.årsak: r.antall for r in oppsummering.per_regel}
    assert per_regel == {
        "kompetanse-minstekrav": 1,
        "kolliderende vakt": 1,
        "11-timersregelen": 0,
        "35-timersregelen": 0,
    }
    assert oppsummering.utelukkede == (
        EkskludertKandidat(id=1, navn="Ada", årsaker=("kompetanse-minstekrav",)),
        EkskludertKandidat(id=2, navn="Bea", årsaker=("kolliderende vakt",)),
    )


def test_flere_årsaker_på_samme_kandidat_telles_én_gang_i_totalen_og_under_hver_regel() -> None:
    # Seeden har ingen slike tilfeller (bevisst), så dette dekkes med enhetsdata.
    kari = kandidat(1, "Kari Nordmann")
    vurdering = Kandidatvurdering(
        gyldige=(),
        utelukkede=(Utelukket(kandidat=kari, årsaker=("kolliderende vakt", "35-timersregelen")),),
    )

    oppsummering = lag_utelukkelsesoppsummering(vurdering)

    assert oppsummering.totalt == 1
    per_regel = {r.årsak: r.antall for r in oppsummering.per_regel}
    # Summen per regel (2) er større enn totalen (1).
    assert per_regel["kolliderende vakt"] == 1
    assert per_regel["35-timersregelen"] == 1
    assert sum(per_regel.values()) > oppsummering.totalt
    (eneste,) = oppsummering.utelukkede
    assert eneste.årsaker == ("kolliderende vakt", "35-timersregelen")


def test_rekkefølgen_i_per_regel_følger_regler() -> None:
    vurdering = Kandidatvurdering(gyldige=(), utelukkede=())
    oppsummering = lag_utelukkelsesoppsummering(vurdering)

    assert [r.årsak for r in oppsummering.per_regel] == [regel.årsak for regel in REGLER]


def test_egen_regelliste_brukes_når_den_sendes_inn() -> None:
    ekstra = Regel(
        årsak="testregel", bryter=lambda _k, _v: True, vaktkrav=lambda _v: [],
        kandidatkrav=lambda _k, _v: [], vindu=lambda _v: None,
    )
    a = kandidat(1, "Ada")
    vurdering = Kandidatvurdering(gyldige=(), utelukkede=(Utelukket(kandidat=a, årsaker=("testregel",)),))

    oppsummering = lag_utelukkelsesoppsummering(vurdering, regler=(ekstra,))

    assert oppsummering.per_regel == (RegelAntall(årsak="testregel", antall=1),)


def test_utelukkede_beholder_rekkefølgen_fra_vurderingen() -> None:
    # `vurdering.utelukkede` er allerede alfabetisk sortert av regelmotoren; her
    # kontrolleres bare at byggefunksjonen ikke sorterer på nytt.
    b, a = kandidat(2, "Bea"), kandidat(1, "Ada")
    vurdering = Kandidatvurdering(
        gyldige=(),
        utelukkede=(
            Utelukket(kandidat=b, årsaker=("kompetanse-minstekrav",)),
            Utelukket(kandidat=a, årsaker=("kompetanse-minstekrav",)),
        ),
    )

    oppsummering = lag_utelukkelsesoppsummering(vurdering)

    assert [u.navn for u in oppsummering.utelukkede] == ["Bea", "Ada"]
