"""Regneeksempler for Ulempemodellen (PRD §4.3, FR-14, story 4.7).

Grunnlaget for taket på 300 Ulempepoeng: regner ut Ulempepoeng over fire uker for
typiske turnusprofiler og viser Ulempescore med tak 240, 300 og 432. Dette er et
planleggingsverktøy, ikke domenekoden i story 4.7. Kjøres uten nettverk og nøkkel:

    python scripts/ulempe_regneeksempler.py                  # gjeldende vakttider
    python scripts/ulempe_regneeksempler.py --vakttider 2026-10-30

Profilene teller vakter per fire uker. Brøkdeler (for eksempel 1,33 helgevakter)
er snitt over en lengre rotasjon. Eksempeluka er 21.–27.09.2026, uten
sommertidsovergang, så naiv lokal tid gir samme resultat som Europe/Oslo.
"""

import argparse
from datetime import datetime, timedelta

# Poeng per time og prioritet natt > helg > kveld > dag (PRD §4.3).
NATT, HELG, KVELD, DAG = "natt", "helg", "kveld", "dag"
POENG = {NATT: 3, HELG: 2, KVELD: 1, DAG: 0}

# Vakttider som (start, slutt) i desimaltimer; slutt < start betyr over midnatt.
VAKTTIDER = {
    # Gjeldende, besluttet av gruppa 2026-11-02 (samme som mockupene).
    "2026-11-02": {"dag": (7, 15), "kveld": (15, 23), "natt": (23, 7)},
    # Antagelsen i story 1.2 fra 2026-10-30, erstattet 2026-11-02.
    "2026-10-30": {"dag": (7, 15), "kveld": (15, 22.5), "natt": (22, 7.5)},
}

MANDAG = datetime(2026, 9, 21)
LORDAG = datetime(2026, 9, 26)

# Vakter per fire uker: (hverdag dag, kveld, natt, helg dag, kveld, natt).
PROFILER = {
    "A Ren dag, ingen helg (100 %)": (18, 0, 0, 0, 0, 0),
    "B Dag/kveld, hver 3. helg (100 %)": (10, 5, 0, 1, 1.67, 0),
    "C Dag/kveld, hver 2. helg (100 %)": (8, 6, 0, 2, 2, 0),
    "D Tredelt, hver 3. helg, 3 netter (100 %)": (8, 4, 3, 1.33, 1.33, 0),
    "E Tredelt, hver 2. helg, 4 netter (100 %)": (6, 4, 2, 2, 2, 2),
    "F Kveld/natt-tung, hver 2. helg, 8 netter (100 %)": (0, 6, 6, 0, 2, 2),
    "G Fast natt, 15 netter (100 %)": (0, 0, 11, 0, 0, 4),
    "H Deltid 50 %, dag/kveld, hver 3. helg": (4, 3, 0, 1, 0.67, 0),
    "I Helgestilling, bare helg, dag/kveld": (0, 0, 0, 4, 4, 0),
}
TAK = (240, 300, 432)


def kategori(t):
    if t.hour >= 22 or t.hour < 6:
        return NATT
    if t.weekday() >= 5:
        return HELG
    if t.hour >= 18:
        return KVELD
    return DAG


def timer_per_kategori(start, slutt):
    """Timer i hver kategori, med minuttoppløsning."""
    timer = dict.fromkeys(POENG, 0.0)
    t = start
    while t < slutt:
        timer[kategori(t)] += 1 / 60
        t += timedelta(minutes=1)
    return timer


def vakt(dag, start, slutt):
    s = dag + timedelta(hours=start)
    e = dag + timedelta(hours=slutt)
    if slutt <= start:
        e += timedelta(days=1)
    return s, e


def poeng(timer):
    return sum(POENG[k] * h for k, h in timer.items())


def ulempescore(p, tak):
    return max(0.0, 100 * (1 - p / tak))


def profil(tider, antall):
    """Samlede timer per kategori og arbeidstimer for en profil over fire uker."""
    sum_timer = dict.fromkeys(POENG, 0.0)
    arbeid = 0.0
    for (dag, navn), n in zip(
        [(MANDAG, v) for v in tider] + [(LORDAG, v) for v in tider], antall
    ):
        s, e = vakt(dag, *tider[navn])
        for k, h in timer_per_kategori(s, e).items():
            sum_timer[k] += n * h
        arbeid += n * (e - s).total_seconds() / 3600
    return sum_timer, arbeid


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vakttider", choices=VAKTTIDER, default="2026-11-02")
    tider = VAKTTIDER[parser.parse_args().vakttider]

    print("Vakttider:", ", ".join(f"{n} {a:g}–{b:g}" for n, (a, b) in tider.items()))
    for navn in tider:
        for etikett, dag in (("hverdag", MANDAG), ("helg", LORDAG)):
            print(f"  {navn:6} {etikett:8} {poeng(timer_per_kategori(*vakt(dag, *tider[navn]))):5.1f} p")
    print()
    print(f"{'Profil':50} {'timer':>6} {'poeng':>6}  kveld/helg/natt t   "
          + "  ".join(f"tak {t}" for t in TAK))
    for navn, antall in PROFILER.items():
        timer, arbeid = profil(tider, antall)
        p = poeng(timer)
        # Fordelingen skal alltid summere til poengene (PRD §4.3).
        assert abs(timer[KVELD] + 2 * timer[HELG] + 3 * timer[NATT] - p) < 1e-6
        fordeling = f"{timer[KVELD]:5.1f}/{timer[HELG]:5.1f}/{timer[NATT]:5.1f}"
        score = "  ".join(f"{ulempescore(p, t):7.1f}" for t in TAK)
        print(f"{navn:50} {arbeid:6.0f} {p:6.0f}  {fordeling}  {score}")
    print()
    print("Teoretisk tak uten overtid: 36 t × 4 uker × 3 p =", 36 * 4 * 3)


if __name__ == "__main__":
    main()
