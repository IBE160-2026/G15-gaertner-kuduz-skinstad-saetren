"""Identiteten til et forhåndsgenerert svar (AD-6), felles for generator og API."""

import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256

from domene.porter.rangering import RangertKandidat
from domene.typer import Kandidat, Vakt

KONTRAKTSVERSJON = 2


def _jsonverdi(verdi: object):
    if is_dataclass(verdi):
        return {felt.name: getattr(verdi, felt.name) for felt in fields(verdi)}
    if isinstance(verdi, Mapping):
        return dict(verdi)
    if isinstance(verdi, Fraction):
        return [verdi.numerator, verdi.denominator]
    if isinstance(verdi, frozenset):
        return sorted(verdi)
    if isinstance(verdi, datetime):
        return verdi.astimezone(UTC).isoformat()
    raise TypeError(f"Ukjent type i forklaringsgrunnlaget: {type(verdi).__name__}")


def forklaringsnøkkel(vakt: Vakt, kandidat: Kandidat, rangert: RangertKandidat,
                     referanse: RangertKandidat | None) -> str:
    fakta = [KONTRAKTSVERSJON, vakt, kandidat, rangert, referanse]
    data = json.dumps(fakta, default=_jsonverdi, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(data.encode("utf-8")).hexdigest()
