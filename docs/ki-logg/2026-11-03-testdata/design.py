"""Scratch design checker for story 1.2 seed data. Not part of the repo."""
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import sys

OSLO = ZoneInfo("Europe/Oslo")
TIDER = {"D": (7, 15, "dag"), "M": (10, 18, "mellom"), "K": (15, 23, "kveld"), "N": (23, 7, "natt")}
START = date(2026, 8, 24)  # mandag uke 35
H = timedelta(hours=1)

# kompetanse
KOMP = {}
# schedules: 6 weeks (35..40), Mon..Sun, letters D M K N -
S = {}

def p(navn, komp, *uker):
    KOMP[navn] = komp
    s = "".join(u.replace(" ", "") for u in uker)
    assert len(s) == 42, (navn, len(s), s)
    S[navn] = s

#        uke35    uke36    uke37    uke38    uke39    uke40
exec(open(sys.argv[1], encoding="utf-8").read())

def intervall(d, t):
    a, b, _ = TIDER[t]
    s = datetime(d.year, d.month, d.day, a, tzinfo=OSLO)
    e = datetime(d.year, d.month, d.day, b, tzinfo=OSLO)
    if b <= a:
        e = datetime.combine(d + timedelta(days=1), datetime.min.time()).replace(hour=b, tzinfo=OSLO)
    return s, e

def vakter(navn):
    out = []
    for i, c in enumerate(S[navn]):
        if c != "-":
            d = START + timedelta(days=i)
            s, e = intervall(d, c)
            out.append((s, e, c, d))
    return out

def utc(x):
    return x.astimezone(ZoneInfo("UTC"))

def timer(a, b):
    return (utc(b) - utc(a)).total_seconds() / 3600

def ukestart(t):
    d = t.date() - timedelta(days=t.weekday())
    return datetime(d.year, d.month, d.day, tzinfo=OSLO)

def lengste_fri(intervaller, uke):
    ue = datetime.combine(uke.date() + timedelta(days=7), datetime.min.time()).replace(tzinfo=OSLO)
    iv = sorted((max(s, uke), min(e, ue)) for s, e in intervaller if s < ue and e > uke)
    best, cur = 0, uke
    for s, e in iv:
        if s > cur:
            best = max(best, timer(cur, s))
        cur = max(cur, e)
    best = max(best, timer(cur, ue))
    return best

def uker_berort(s, e):
    w = ukestart(s)
    out = []
    while w < e:
        out.append(w)
        w = datetime.combine(w.date() + timedelta(days=7), datetime.min.time()).replace(tzinfo=OSLO)
    return out

def regler(navn, ts, te, ttype, minst):
    v = [(s, e) for s, e, *_ in vakter(navn)]
    brudd = set()
    k = KOMP[navn].get("dag" if ttype == "mellom" else ttype)
    if k is None or k < minst:
        brudd.add("kompetanse")
    if any(s < te and ts < e for s, e in v):
        brudd.add("kolliderende")
    ikke = [(s, e) for s, e in v if not (s < te and ts < e)]
    foer = [e for s, e in ikke if e <= ts]
    etter = [s for s, e in ikke if s >= te]
    if (foer and timer(max(foer), ts) < 11) or (etter and timer(te, min(etter)) < 11):
        brudd.add("elleve")
    for w in uker_berort(ts, te):
        if lengste_fri(v + [(ts, te)], w) < 35:
            brudd.add("trettifem")
    return brudd

KAT = {"natt": 3, "helg": 2, "kveld": 1, "dag": 0}
def kat(t):
    if t.hour >= 22 or t.hour < 6:
        return "natt"
    if t.weekday() >= 5:
        return "helg"
    if t.hour >= 18:
        return "kveld"
    return "dag"

def ulempe(navn, ts):
    ws = utc(ts) - timedelta(hours=672)
    tot = 0
    for s, e, *_ in vakter(navn):
        a = max(utc(s), ws); b = min(utc(e), utc(ts))
        t = a
        while t < b:
            tot += KAT[kat(t.astimezone(OSLO))] / 60
            t += timedelta(minutes=1)
    return round(tot, 4)

def globalsjekk():
    feil = []
    for n in S:
        v = vakter(n)
        for (s1, e1, *_), (s2, e2, *_) in zip(v, v[1:]):
            if timer(e1, s2) < 11:
                feil.append(f"{n}: hvile {timer(e1, s2)} t {s1:%d.%m %H} -> {s2:%d.%m %H}")
        uker = sorted({w for s, e, *_ in v for w in uker_berort(s, e)})
        for w in uker:
            lf = lengste_fri([(s, e) for s, e, *_ in v], w)
            if lf < 35:
                feil.append(f"{n}: uke {w:%d.%m} lengste fri {lf}")
    return feil

if __name__ == "__main__":
    for f in globalsjekk():
        print("GLOBAL", f)
    t4127 = intervall(date(2026, 9, 27), "D")
    t4189 = intervall(date(2026, 9, 28), "N")
    print("#4127")
    from collections import Counter
    c = Counter()
    for n in S:
        if n == SATT_4127: continue
        b = regler(n, *t4127, "dag", 3)
        c[tuple(sorted(b)) or ("gyldig",)] += 1
        u = ulempe(n, t4127[0])
        print(f"  {n:18} {sorted(b) or 'GYLDIG'}  ulempe={u}")
    print(" ", dict(c))
    print("#4189")
    c = Counter()
    for n in S:
        if n == SATT_4189: continue
        b = regler(n, *t4189, "natt", 3)
        c[tuple(sorted(b)) or ("gyldig",)] += 1
        print(f"  {n:18} {sorted(b) or 'GYLDIG'}")
    print(" ", dict(c))
    # staffing per day
    print("bemanning")
    for i in range(42):
        d = START + timedelta(days=i)
        cnt = Counter(S[n][i] for n in S)
        print(f"  {d:%a %d.%m}  D{cnt['D']} M{cnt['M']} K{cnt['K']} N{cnt['N']}  tot {42 and sum(cnt[x] for x in 'DMKN')}")
    # hours per week per person
    print("timer per uke (etter start)")
    for n in S:
        hs = []
        for w in range(6):
            hs.append(sum(8 for c in S[n][w*7:(w+1)*7] if c != '-'))
        print(f"  {n:18} {hs}")
