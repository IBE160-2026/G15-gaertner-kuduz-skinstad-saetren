"""Én felles begrenser for alle KI-kall mot OpenRouter (AD-7, story 5.1).

Høyst `per_minutt` kall startet i et glidende vindu på 60 s og høyst `samtidige`
kall på én gang. Bygd på prototypen `MinuteLimiter` i `scripts/modelltest_robusthet.py`.
Klokke og `sleep` kan byttes ut, så testene verken venter eller bruker nettverk.
Begrenseren er trådsikker og skal deles av alle KI-funksjoner i samme prosess.
"""

import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

VINDU_S = 60.0


class TidsbudsjettOpbrukt(Exception):
    """Ventingen på plass i begrenseren ville gått forbi fristen."""


class Begrenser:
    def __init__(
        self,
        per_minutt: int,
        samtidige: int,
        klokke: Callable[[], float] = time.monotonic,
        sov: Callable[[float], None] = time.sleep,
    ) -> None:
        self.per_minutt = per_minutt
        self._klokke = klokke
        self._sov = sov
        self._samtidige = threading.BoundedSemaphore(samtidige)
        self._starter: list[float] = []
        self._lås = threading.Lock()

    @contextmanager
    def plass(self, frist: float | None) -> Iterator[None]:
        """Holder én plass mens blokken kjører. `frist` er på samme monotone klokke.

        Gir `TidsbudsjettOpbrukt` uten å vente når ventingen ville gått forbi fristen.
        Ventingen på en samtidig plass bruker semaforens egen tidsgrense.
        """
        køtid = None if frist is None else max(0.0, frist - self._klokke())
        if not self._samtidige.acquire(timeout=køtid):
            raise TidsbudsjettOpbrukt
        try:
            self._ta_start(frist)
            yield
        finally:
            self._samtidige.release()

    def _ta_start(self, frist: float | None) -> None:
        while True:
            with self._lås:
                nå = self._klokke()
                self._starter = [t for t in self._starter if nå - t < VINDU_S]
                if len(self._starter) < self.per_minutt:
                    self._starter.append(nå)
                    return
                vent = VINDU_S - (nå - self._starter[0])
            if frist is not None and nå + vent > frist:
                raise TidsbudsjettOpbrukt
            self._sov(vent)
