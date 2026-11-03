import re
from datetime import date, timedelta
s = open('data4.py', encoding='utf-8').read()
navn = re.findall(r'p\("([^"]+)"', s)
rows = {}
for line in s.split('\n'):
    m = re.match(r'p\("([^"]+)"', line)
    if m:
        rows[m.group(1)] = "".join(re.findall(r'"([DMKN-]{7})"', line))
ID = {n: i + 1 for i, n in enumerate(navn)}
TYPE = {"D": "dag", "M": "mellom", "K": "kveld", "N": "natt"}
ORD = {"D": 0, "M": 1, "K": 2, "N": 3}
START = date(2026, 8, 24)
vakter = []
for n, sch in rows.items():
    for i, c in enumerate(sch):
        if c != "-":
            vakter.append((START + timedelta(days=i), ORD[c], ID[n], TYPE[c], n))
vakter.append((date(2026, 9, 27), 0, 0, "dag", None))
vakter.append((date(2026, 9, 28), 3, 0, "natt", None))
vakter.sort()
RES = {("2026-09-27", "kveld", 7): 4128, ("2026-09-28", "dag", 5): 4130, ("2026-09-28", "natt", 3): 4131,
       ("2026-09-29", "dag", 6): 4135, ("2026-09-29", "kveld", 4): 4136, ("2026-09-27", "dag", None): 4127,
       ("2026-09-28", "natt", None): 4189}
assert ID["Per Halvorsen"] == 7 and ID["Mette Solberg"] == 5 and ID["Thomas Nygård"] == 3
assert ID["Jonas Bakke"] == 6 and ID["Ingrid Dahl"] == 4
hist = [v for v in vakter if v[0] < date(2026, 9, 21)]
per = [v for v in vakter if v[0] >= date(2026, 9, 21)]
out = []
DAG = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
def block(liste, nr0, reserved):
    nr = nr0
    used = set(reserved.values())
    cur = None
    lines = []
    for d, _, aid, t, n in liste:
        if d != cur:
            cur = d
            if d.weekday() == 0:
                lines.append(f"    # Uke {d.isocalendar()[1]}")
            lines.append(f"    # {DAG[d.weekday()]} {d:%d.%m}")
        key = (d.isoformat(), t, n and aid)
        if key in reserved:
            v = reserved[key]
        else:
            while nr in used:
                nr += 1
            v = nr
            nr += 1
        a = "None" if n is None else str(aid)
        minst = 3 if n is None else 2
        kom = "mangler bemanning" if n is None else n
        lines.append(f'    ({v}, "{d.isoformat()}", "{t}", {a}, {minst}),  # {kom}')
    return lines, nr
res = {k: v for k, v in RES.items()}
res2 = {}
for (d, t, a), v in RES.items():
    res2[(d, t, a)] = v
h, last = block(hist, 3000, {})
p, lastp = block(per, 4100, res2)
open('historikk.txt', 'w', encoding='utf-8').write("\n".join(h) + "\n")
open('periode.txt', 'w', encoding='utf-8').write("\n".join(p) + "\n")
print(len(hist), last, len(per), lastp)
