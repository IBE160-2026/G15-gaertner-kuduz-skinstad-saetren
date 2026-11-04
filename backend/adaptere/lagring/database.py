"""Tilkobling til SQLite-databasen og oppretting av skjemaet (AD-5)."""

import os
from pathlib import Path

from sqlalchemy import URL, Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

MILJOVARIABEL = "TURNUSHJELPEREN_DB"

# backend/turnushjelperen.db, uavhengig av arbeidsmappen.
STANDARD_STI = Path(__file__).resolve().parents[2] / "turnushjelperen.db"


def database_sti(sti: str | os.PathLike[str] | None = None) -> Path:
    """Stien til databasefilen.

    Rekkefølge: argumentet, deretter `TURNUSHJELPEREN_DB`, deretter
    `backend/turnushjelperen.db`. En relativ sti tolkes fra arbeidsmappen.
    """
    if sti is None:
        sti = os.environ.get(MILJOVARIABEL) or None
    if sti is None:
        return STANDARD_STI
    return Path(sti).resolve()


def lag_engine(sti: str | os.PathLike[str] | None = None) -> Engine:
    fil = database_sti(sti)
    fil.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(URL.create("sqlite", database=str(fil)))

    @event.listens_for(engine, "connect")
    def _slaa_paa_fremmednokler(dbapi_tilkobling, _post) -> None:
        # SQLite håndhever ikke fremmednøkler uten denne innstillingen.
        markor = dbapi_tilkobling.cursor()
        markor.execute("PRAGMA foreign_keys=ON")
        markor.close()

    return engine


def lag_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


def opprett_skjema(engine: Engine) -> None:
    """Oppretter tabellene som mangler. Endrer ikke eksisterende tabeller."""
    from adaptere.lagring.modeller import Base

    Base.metadata.create_all(engine)
