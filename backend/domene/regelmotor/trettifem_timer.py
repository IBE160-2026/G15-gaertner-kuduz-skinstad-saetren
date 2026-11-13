"""Hard regel: 35-timersregelen, ukentlig fri (FR5, AV-04, story 2.4).

En Kandidat utelukkes når en kalenderuke som Vakten berører, ikke lenger har
35 timer sammenhengende fri etter at Vakten er lagt til. Nøyaktig 35 t er gyldig.

Uka går fra mandag 00:00 til neste mandag 00:00 på veggklokka i `Europe/Oslo`.
Grensene settes i Oslo-tid og regnes så om til UTC, så uker med sommertidsskifte
har 167 eller 169 faktiske timer. Berørte uker er ukene som det halvåpne
`[start, slutt)` til Vakten overlapper: en Vakt som slutter nøyaktig mandag
00:00, berører bare én uke.

Fri regnes fra unionen av Kandidatens gyldige vakter og Vakten, klippet til uka,
også fra ukestart til første vakt og fra siste vakt til ukeslutt. Fri over
ukeskiftet teller bare med delen innenfor uka. All tid er faktisk forløpt tid i
UTC. Det er samme semantikk som `bryter_trettifem_timer` i fasiten
(`tester/lagring/test_testdata.py`).

En egen vakt som overlapper Vakten, telles med i unionen (beslutning A, Ragnhild
2026-11-11, OP-14). Det skiller seg fra 1A for 11 t, men følger fasiten (AV-07).
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from domene.regelmotor.elleve_timer import gyldig_tidsrom
from domene.typer import Kandidat, Tidsrom, Vakt

ÅRSAK = "35-timersregelen"
MINSTE_FRI = timedelta(hours=35)
OSLO = ZoneInfo("Europe/Oslo")


def _mandag_kl_null(mandag: date) -> datetime:
    """Mandag 00:00 på veggklokka i Oslo, som UTC."""
    return datetime.combine(mandag, time(0), tzinfo=OSLO).astimezone(UTC)


def _mandag_i_uka(tid: datetime) -> date:
    lokal = tid.astimezone(OSLO).date()
    return lokal - timedelta(days=lokal.weekday())


def berørte_uker(vakt: Vakt) -> list[Tidsrom]:
    """Kalenderukene `[mandag 00:00, neste mandag 00:00)` som Vakten overlapper, i UTC.

    Neste mandag finnes ved å legge 7 dager til datoen, ikke til et tidspunkt, så
    uka får 167 eller 169 faktiske timer over sommertidsskiftene.
    """
    slutt = vakt.slutt.astimezone(UTC)
    mandag = _mandag_i_uka(vakt.start)
    uker = [Tidsrom(_mandag_kl_null(mandag), _mandag_kl_null(mandag + timedelta(days=7)))]
    while uker[-1].slutt < slutt:
        mandag += timedelta(days=7)
        uker.append(Tidsrom(_mandag_kl_null(mandag), _mandag_kl_null(mandag + timedelta(days=7))))
    return uker


def lengste_fri(vakter: list[Tidsrom], uke: Tidsrom) -> timedelta:
    """Lengste sammenhengende fri i uka, regnet fra unionen av vaktene klippet til uka.

    Vaktene må være gyldige tidsrom med tidssone. Alt regnes i UTC.
    """
    uke_start, uke_slutt = uke.start.astimezone(UTC), uke.slutt.astimezone(UTC)
    klippet = sorted(
        (max(v.start.astimezone(UTC), uke_start), min(v.slutt.astimezone(UTC), uke_slutt))
        for v in vakter
        if v.start.astimezone(UTC) < uke_slutt and uke_start < v.slutt.astimezone(UTC)
    )
    lengste, fri_fra = timedelta(0), uke_start
    for start, slutt in klippet:
        if start > fri_fra:
            lengste = max(lengste, start - fri_fra)
        fri_fra = max(fri_fra, slutt)
    return max(lengste, uke_slutt - fri_fra)


def bryter_trettifem_timer(kandidat: Kandidat, vakt: Vakt) -> bool:
    """Om en berørt uke får under 35 t sammenhengende fri med Vakten lagt til.

    Forutsetning: kalles via `vurder_kandidater`, eller etter at
    `kandidatvaktdatafeil` har godkjent Kandidatens vakter i vinduet. Ugyldige
    vakter hoppes over her, så kalt direkte blir ugyldige vakter i vinduet ikke
    oppdaget (gjelder for eksempel en ny regelkontroll ved Godkjenning i Epic 3).
    """
    vakter = [egen for egen in kandidat.vakter if gyldig_tidsrom(egen)]
    vakter.append(Tidsrom(vakt.start, vakt.slutt))
    return any(lengste_fri(vakter, uke) < MINSTE_FRI for uke in berørte_uker(vakt))


def vindu(vakt: Vakt) -> Tidsrom:
    """Vakter i de berørte ukene kan påvirke regelen. Regnet i UTC.

    `[mandag i første berørte uke, mandag etter siste berørte uke)`.
    """
    uker = berørte_uker(vakt)
    return Tidsrom(start=uker[0].start, slutt=uker[-1].slutt)
