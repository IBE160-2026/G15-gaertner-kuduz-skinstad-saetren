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
    """Engine mot SQLite-filen, med fremmednøkler slått på.

    Transaksjonene bygger på standardoppførselen til Pythons `sqlite3`
    (`isolation_level=""`, `autocommit=LEGACY_TRANSACTION_CONTROL`), som
    SQLAlchemy lar stå. Driveren starter da en transaksjon selv bare før
    INSERT/UPDATE/DELETE, ikke før SELECT, og godtar en eksplisitt `BEGIN` fra
    koden. To steder bruker dette:

    - GET-grunnlaget i `adaptere/api/main.py` kjører `BEGIN`, slik at visning og
      grunnlagsmerke leses fra samme øyeblikk (P-09).
    - `lagre_godkjenning` i `adaptere/lagring/godkjenninger.py` kjører
      `BEGIN IMMEDIATE`, slik at skrivelåsen tas før regelkontroll og skriving
      (AD-5). Driveren starter ikke en ny transaksjon før UPDATE, fordi en allerede
      er åpen, og `session.commit()` avslutter den. `lagre_tekst` i
      `adaptere/lagring/preferansetolkning.py` gjør det samme (story 5.9).

    Ikke sett `isolation_level`, `autocommit` eller `execution_options` på engine
    eller tilkobling uten å gå gjennom begge stedene. Med `autocommit=False` åpner
    driveren selv en transaksjon, og den eksplisitte `BEGIN` feiler med «cannot
    start a transaction within a transaction» (kontrollert 2026-11-15). Med
    SQLAlchemys `"AUTOCOMMIT"` virker de to eksplisitte transaksjonene fortsatt.
    Driveren starter da ingen transaksjon av seg selv, så andre skriveveier uten
    eksplisitt `BEGIN` blir committet setning for setning. Testdataene, som tømmer
    og fyller tabellene i én transaksjon, blir da ikke lenger atomiske. Testene i `tester/api/test_godkjenningsgrunnlag.py`
    (snapshot, skrivelås, rollback og samtidige POST) bruker begge kodestedene.
    """
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
