"""SQLAlchemy-modellene for Turnus, Vakt og Ansatt.

Lagringsadapteren eier skjemaet alene (AD-5). Domenet importerer aldri herfra.
"""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

OSLO = ZoneInfo("Europe/Oslo")
UTC = ZoneInfo("UTC")

VAKTTYPER = ("dag", "mellom", "kveld", "natt")


class OsloTid(TypeDecorator[datetime]):
    """Tidspunkt lagret som ISO 8601 i UTC, lest tilbake i Europe/Oslo.

    Naive `datetime` avvises, fordi det ikke går å vite hvilken tidssone de
    gjelder. Verdien leses alltid tilbake med `ZoneInfo("Europe/Oslo")`, aldri
    med fast offset, slik at aritmetikk over sommertidsskiftet blir riktig.
    UTC-teksten gjør at sortering og intervallsøk i SQL følger tidslinjen.
    """

    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise TypeError(f"OsloTid krever datetime, fikk {type(value).__name__}")
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("OsloTid avviser naiv datetime; oppgi tidssone")
        return value.astimezone(UTC).isoformat()

    def process_result_value(self, value: Any, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value).astimezone(OSLO)


class Base(DeclarativeBase):
    pass


class TurnusRad(Base):
    __tablename__ = "turnus"

    id: Mapped[int] = mapped_column(primary_key=True)
    avdeling: Mapped[str] = mapped_column(String(100))
    # Halvåpent intervall [periode_start, periode_slutt). En Vakt hører til
    # perioden når den starter innenfor (AV-03).
    periode_start: Mapped[datetime] = mapped_column(OsloTid)
    periode_slutt: Mapped[datetime] = mapped_column(OsloTid)
    sist_oppdatert: Mapped[datetime] = mapped_column(OsloTid)

    vakter: Mapped[list["VaktRad"]] = relationship(back_populates="turnus")


class AnsattRad(Base):
    __tablename__ = "ansatt"
    __table_args__ = (
        CheckConstraint("ansiennitet >= 0", name="ansiennitet_ikke_negativ"),
        CheckConstraint("timelønn > 0", name="timelonn_positiv"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    navn: Mapped[str] = mapped_column(String(100))
    stilling: Mapped[str] = mapped_column(String(50))
    # År.
    ansiennitet: Mapped[int]
    # Ordinær sats i hele kroner per time. Overtidssatsen regnes ut og lagres ikke.
    timelønn: Mapped[int]
    # {"dag" | "kveld" | "natt": nivå 1–4}. Mangler nøkkelen, er den ansatte ikke
    # opplært for vakttypen. `mellom` bruker nivået for `dag`.
    kompetanse: Mapped[dict[str, int]] = mapped_column(JSON)
    preferanse: Mapped[str | None] = mapped_column(Text)


class VaktRad(Base):
    __tablename__ = "vakt"
    __table_args__ = (
        CheckConstraint(
            "vakttype IN (" + ", ".join(f"'{t}'" for t in VAKTTYPER) + ")",
            name="gyldig_vakttype",
        ),
        CheckConstraint("minstenivå BETWEEN 1 AND 4", name="gyldig_minstenivaa"),
        CheckConstraint(
            "(mangler_bemanning = 1 AND tildelt_ansatt_id IS NULL)"
            " OR (mangler_bemanning = 0 AND tildelt_ansatt_id IS NOT NULL)",
            name="tildelt_eller_mangler_bemanning",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    turnus_id: Mapped[int] = mapped_column(ForeignKey("turnus.id"))
    vaktnummer: Mapped[int] = mapped_column(unique=True)
    vakttype: Mapped[str] = mapped_column(String(10))
    start: Mapped[datetime] = mapped_column(OsloTid)
    slutt: Mapped[datetime] = mapped_column(OsloTid)
    minstenivå: Mapped[int]
    tildelt_ansatt_id: Mapped[int | None] = mapped_column(ForeignKey("ansatt.id"))
    mangler_bemanning: Mapped[bool]
    # Fylles bare når vakten mangler bemanning: hvem som var satt opp, og når og
    # hvorfor vedkommende meldte fra.
    satt_opp_ansatt_id: Mapped[int | None] = mapped_column(ForeignKey("ansatt.id"))
    meldt_fra: Mapped[datetime | None] = mapped_column(OsloTid)
    meldt_fra_grunn: Mapped[str | None] = mapped_column(String(100))

    turnus: Mapped[TurnusRad] = relationship(back_populates="vakter")
    tildelt_ansatt: Mapped[AnsattRad | None] = relationship(
        foreign_keys=[tildelt_ansatt_id]
    )
    satt_opp_ansatt: Mapped[AnsattRad | None] = relationship(
        foreign_keys=[satt_opp_ansatt_id]
    )
