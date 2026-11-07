"""Fiktiv turnus for Kirurgisk sengepost, uke 39–40 2026 (story 1.2).

Kjøres fra `backend/`:

    python -m adaptere.lagring.testdata

Kommandoen oppretter tabellene som mangler, tømmer `bruker`, `turnus`, `vakt` og
`ansatt` og fyller dem på nytt i én transaksjon. Den kan kjøres så mange ganger man
vil uten å lage duplikater. Databasestien kommer fra `TURNUSHJELPEREN_DB`, ellers
`backend/turnushjelperen.db`.

Turnusansvarlig Kari Vestby (`kari.vestby`) får passordet i
`TURNUSHJELPEREN_PASSORD` når variabelen er satt (personlig passord, varianten ved
innlevering). Mangler den eller er den tom, lages et tilfeldig testpassord som
skrives ut og gjelder til neste kjøring (story 1.3, OP-10). Passordet lagres bare
som hash.

Alle navn er fiktive. Alle Vakter, også historikken 24.08–20.09, står som faste,
eksplisitte rader nedenfor. Ingenting lages av en generator eller et mønster i
kode (AV-10). Klokkeslettene kommer fra `VAKTTIDER` (AV-02).

`FASIT` er beregnet på forhånd og ikke hentet fra programmet (AV-07). Testene i
`tester/lagring/test_testdata.py` sjekker at dataene gir nøyaktig fasiten.
"""

import os
import secrets
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from adaptere.lagring.database import database_sti, lag_engine, lag_sessionmaker, opprett_skjema
from adaptere.lagring.brukere import hash_passord
from adaptere.lagring.modeller import OSLO, AnsattRad, BrukerRad, TurnusRad, VaktRad

AVDELING = "Kirurgisk sengepost"
PASSORD_VARIABEL = "TURNUSHJELPEREN_PASSORD"
TURNUSANSVARLIG_BRUKERNAVN = "kari.vestby"
TURNUSANSVARLIG_NAVN = "Kari Vestby"
TURNUS_ID = 1
# Halvåpent intervall [man. 21.09.2026 00:00, man. 05.10.2026 00:00).
PERIODE_START = datetime(2026, 9, 21, 0, 0, tzinfo=OSLO)
PERIODE_SLUTT = datetime(2026, 10, 5, 0, 0, tzinfo=OSLO)
SIST_OPPDATERT = datetime(2026, 9, 27, 6, 20, tzinfo=OSLO)

# Gruppevedtak 2026-11-02 (AV-02). Alle vakter er 8 timer. Natt slutter neste dag.
VAKTTIDER: dict[str, tuple[time, time]] = {
    "dag": (time(7, 0), time(15, 0)),
    "mellom": (time(10, 0), time(18, 0)),
    "kveld": (time(15, 0), time(23, 0)),
    "natt": (time(23, 0), time(7, 0)),
}

KOMPETANSENIVAER = {
    1: "Under opplæring",
    2: "Delvis opplært",
    3: "Kvalifisert",
    4: "Fullt kvalifisert",
}

# PRD §4.5, FR-10: preferansetekstene ordrett, med forventet poeng.
PREFERANSER: dict[int, tuple[str, int]] = {
    1: ("Jeg ønsker flere vakter denne uken.", 100),
    2: ("Jeg vil gjerne jobbe mer enn den oppsatte turnusen.", 100),
    3: ("Prioriter meg gjerne når det blir ledige ekstravakter.", 100),
    4: ("Jeg trenger ikke flere vakter, men tar gjerne en ekstra ved behov.", 75),
    5: ("Hvis dere mangler folk, stiller jeg gjerne på en ekstravakt.", 75),
    6: ("Jeg er positiv til ekstravakter, selv om jeg ikke aktivt ber om flere.", 75),
    7: ("Jeg har ingen ønsker om flere eller færre vakter.", 50),
    8: ("For meg spiller det ingen rolle om jeg får en ekstravakt.", 50),
    9: ("Jeg stiller meg nøytral til å jobbe utover den oppsatte turnusen.", 50),
    10: ("Jeg foretrekker å slippe ekstravakter, men kan ta en hvis det trengs.", 25),
    11: ("Spør helst andre først, men jeg er åpen for en ekstravakt ved bemanningsbehov.", 25),
    12: ("Jeg ønsker helst bare de oppsatte vaktene, men kan stille dersom dere mangler folk.", 25),
    13: ("Jeg ønsker ikke ekstravakter denne uken.", 0),
    14: ("Jeg ønsker færre vakter og ber om å slippe ekstraarbeid.", 0),
    15: ("Jeg ønsker kun å jobbe de vaktene som allerede står i turnusen.", 0),
}

# (id, navn, stilling, ansiennitet i år, timelønn kr, kompetanse, PRD-preferanse nr.)
# Kompetansen er nivå 1–4 per vakttype. Mangler nøkkelen, er den ansatte ikke
# opplært for vakttypen. `mellom` bruker nivået for `dag`.
ANSATTE: list[tuple[int, str, str, int, int, dict[str, int], int | None]] = [
    (1, "Silje Amundsen", "Sykepleier", 5, 360, {"dag": 3, "kveld": 3}, 10),
    (2, "Eirik Moen", "Spesialsykepleier", 12, 420, {"natt": 4}, None),
    (3, "Thomas Nygård", "Sykepleier", 1, 350, {"dag": 3, "kveld": 2, "natt": 3}, 13),
    (4, "Ingrid Dahl", "Sykepleier", 6, 385, {"dag": 4, "kveld": 4, "natt": 3}, 1),
    (5, "Mette Solberg", "Sykepleier", 9, 370, {"dag": 4, "kveld": 4, "natt": 4}, 5),
    (6, "Jonas Bakke", "Sykepleier", 3, 370, {"dag": 3, "kveld": 3, "natt": 3}, 4),
    (7, "Per Halvorsen", "Sykepleier", 4, 375, {"dag": 3, "kveld": 3, "natt": 3}, 7),
    (8, "Kristin Berg", "Spesialsykepleier", 15, 415, {"dag": 3, "kveld": 3, "natt": 4}, 2),
    (9, "Lars Haugen", "Sykepleier", 7, 380, {"dag": 3, "kveld": 3, "natt": 3}, 8),
    (10, "Nora Lie", "Sykepleier", 2, 355, {"dag": 3, "kveld": 3, "natt": 3}, None),
    (11, "Anders Strand", "Sykepleier", 8, 380, {"dag": 3, "kveld": 4, "natt": 3}, 11),
    (12, "Hanne Johansen", "Spesialsykepleier", 14, 410, {"dag": 4, "kveld": 4, "natt": 4}, 14),
    (13, "Ole Kristiansen", "Sykepleier", 10, 390, {"dag": 3, "kveld": 3, "natt": 3}, 3),
    (14, "Marte Eide", "Sykepleier", 5, 365, {"dag": 3, "kveld": 3, "natt": 3}, None),
    (15, "Sindre Lunde", "Sykepleier", 3, 360, {"dag": 3, "kveld": 3, "natt": 3}, 9),
    (16, "Camilla Ruud", "Sykepleier", 11, 395, {"dag": 4, "kveld": 3, "natt": 3}, 6),
    (17, "Henrik Aas", "Sykepleier", 6, 375, {"dag": 3, "kveld": 3, "natt": 3}, 12),
    (18, "Ida Pedersen", "Sykepleier", 2, 355, {"dag": 3, "kveld": 3, "natt": 3}, 15),
    (19, "Tone Brekke", "Helsefagarbeider", 9, 360, {"dag": 2, "kveld": 2}, None),
    (20, "Even Sandvik", "Helsefagarbeider", 1, 350, {"dag": 2, "kveld": 2, "natt": 1}, None),
    (21, "Line Moe", "Sykepleier", 1, 355, {"dag": 2, "kveld": 3, "natt": 3}, 1),
    (22, "Kjetil Fjeld", "Helsefagarbeider", 6, 360, {"dag": 2, "kveld": 2, "natt": 3}, 8),
    (23, "Astrid Holm", "Helsefagarbeider", 13, 375, {"dag": 2, "kveld": 2, "natt": 3}, None),
    (24, "Stian Vik", "Helsefagarbeider", 4, 355, {"dag": 2, "kveld": 2, "natt": 3}, 13),
    (25, "Martin Hagen", "Sykepleier", 2, 360, {"kveld": 3, "natt": 3}, 5),
]

# Vakter som mangler bemanning: vaktnummer → (satt opp, meldt fra, grunn).
MANGLER_BEMANNING: dict[int, tuple[int, datetime, str]] = {
    4127: (1, datetime(2026, 9, 27, 6, 14, tzinfo=OSLO), "sykemeldt"),  # Silje Amundsen
    4189: (2, datetime(2026, 9, 26, 21, 40, tzinfo=OSLO), "sykemeldt"),  # Eirik Moen
}

# Rader: (vaktnummer, startdato, vakttype, tildelt ansatt-id eller None, minstenivå).
# None betyr at vakten mangler bemanning, se MANGLER_BEMANNING.

# Historikk 24.08–20.09, vaktnummer #3000–#3999. Alle er tildelt og starter før
# periodestart. Brukes til hvileregler og Ulempepoeng, ikke til visning.
HISTORIKK: list[tuple[int, str, str, int | None, int]] = [
    # Uke 35
    # mandag 24.08
    (3000, "2026-08-24", "dag", 3, 2),  # Thomas Nygård
    (3001, "2026-08-24", "dag", 10, 2),  # Nora Lie
    (3002, "2026-08-24", "dag", 12, 2),  # Hanne Johansen
    (3003, "2026-08-24", "dag", 16, 2),  # Camilla Ruud
    (3004, "2026-08-24", "dag", 18, 2),  # Ida Pedersen
    (3005, "2026-08-24", "dag", 24, 2),  # Stian Vik
    (3006, "2026-08-24", "mellom", 1, 2),  # Silje Amundsen
    (3007, "2026-08-24", "mellom", 5, 2),  # Mette Solberg
    (3008, "2026-08-24", "mellom", 9, 2),  # Lars Haugen
    (3009, "2026-08-24", "mellom", 19, 2),  # Tone Brekke
    (3010, "2026-08-24", "kveld", 7, 2),  # Per Halvorsen
    (3011, "2026-08-24", "kveld", 13, 2),  # Ole Kristiansen
    (3012, "2026-08-24", "kveld", 15, 2),  # Sindre Lunde
    (3013, "2026-08-24", "kveld", 21, 2),  # Line Moe
    (3014, "2026-08-24", "natt", 2, 2),  # Eirik Moen
    (3015, "2026-08-24", "natt", 22, 2),  # Kjetil Fjeld
    (3016, "2026-08-24", "natt", 23, 2),  # Astrid Holm
    # tirsdag 25.08
    (3017, "2026-08-25", "dag", 3, 2),  # Thomas Nygård
    (3018, "2026-08-25", "dag", 4, 2),  # Ingrid Dahl
    (3019, "2026-08-25", "dag", 6, 2),  # Jonas Bakke
    (3020, "2026-08-25", "dag", 11, 2),  # Anders Strand
    (3021, "2026-08-25", "dag", 12, 2),  # Hanne Johansen
    (3022, "2026-08-25", "dag", 14, 2),  # Marte Eide
    (3023, "2026-08-25", "dag", 18, 2),  # Ida Pedersen
    (3024, "2026-08-25", "mellom", 1, 2),  # Silje Amundsen
    (3025, "2026-08-25", "mellom", 5, 2),  # Mette Solberg
    (3026, "2026-08-25", "mellom", 9, 2),  # Lars Haugen
    (3027, "2026-08-25", "mellom", 19, 2),  # Tone Brekke
    (3028, "2026-08-25", "kveld", 7, 2),  # Per Halvorsen
    (3029, "2026-08-25", "kveld", 13, 2),  # Ole Kristiansen
    (3030, "2026-08-25", "kveld", 15, 2),  # Sindre Lunde
    (3031, "2026-08-25", "kveld", 20, 2),  # Even Sandvik
    (3032, "2026-08-25", "kveld", 21, 2),  # Line Moe
    (3033, "2026-08-25", "kveld", 25, 2),  # Martin Hagen
    (3034, "2026-08-25", "natt", 2, 2),  # Eirik Moen
    (3035, "2026-08-25", "natt", 8, 2),  # Kristin Berg
    (3036, "2026-08-25", "natt", 23, 2),  # Astrid Holm
    # onsdag 26.08
    (3037, "2026-08-26", "dag", 4, 2),  # Ingrid Dahl
    (3038, "2026-08-26", "dag", 11, 2),  # Anders Strand
    (3039, "2026-08-26", "dag", 16, 2),  # Camilla Ruud
    (3040, "2026-08-26", "dag", 24, 2),  # Stian Vik
    (3041, "2026-08-26", "kveld", 10, 2),  # Nora Lie
    (3042, "2026-08-26", "kveld", 15, 2),  # Sindre Lunde
    (3043, "2026-08-26", "kveld", 20, 2),  # Even Sandvik
    (3044, "2026-08-26", "kveld", 25, 2),  # Martin Hagen
    (3045, "2026-08-26", "natt", 8, 2),  # Kristin Berg
    (3046, "2026-08-26", "natt", 17, 2),  # Henrik Aas
    # torsdag 27.08
    (3047, "2026-08-27", "dag", 4, 2),  # Ingrid Dahl
    (3048, "2026-08-27", "dag", 5, 2),  # Mette Solberg
    (3049, "2026-08-27", "dag", 6, 2),  # Jonas Bakke
    (3050, "2026-08-27", "dag", 14, 2),  # Marte Eide
    (3051, "2026-08-27", "dag", 19, 2),  # Tone Brekke
    (3052, "2026-08-27", "dag", 24, 2),  # Stian Vik
    (3053, "2026-08-27", "kveld", 1, 2),  # Silje Amundsen
    (3054, "2026-08-27", "kveld", 10, 2),  # Nora Lie
    (3055, "2026-08-27", "kveld", 11, 2),  # Anders Strand
    (3056, "2026-08-27", "kveld", 25, 2),  # Martin Hagen
    (3057, "2026-08-27", "natt", 17, 2),  # Henrik Aas
    (3058, "2026-08-27", "natt", 22, 2),  # Kjetil Fjeld
    # fredag 28.08
    (3059, "2026-08-28", "dag", 3, 2),  # Thomas Nygård
    (3060, "2026-08-28", "dag", 4, 2),  # Ingrid Dahl
    (3061, "2026-08-28", "dag", 5, 2),  # Mette Solberg
    (3062, "2026-08-28", "dag", 7, 2),  # Per Halvorsen
    (3063, "2026-08-28", "dag", 14, 2),  # Marte Eide
    (3064, "2026-08-28", "dag", 19, 2),  # Tone Brekke
    (3065, "2026-08-28", "dag", 20, 2),  # Even Sandvik
    (3066, "2026-08-28", "kveld", 1, 2),  # Silje Amundsen
    (3067, "2026-08-28", "kveld", 9, 2),  # Lars Haugen
    (3068, "2026-08-28", "kveld", 12, 2),  # Hanne Johansen
    (3069, "2026-08-28", "kveld", 23, 2),  # Astrid Holm
    (3070, "2026-08-28", "natt", 17, 2),  # Henrik Aas
    (3071, "2026-08-28", "natt", 22, 2),  # Kjetil Fjeld
    # lørdag 29.08
    (3072, "2026-08-29", "dag", 3, 2),  # Thomas Nygård
    (3073, "2026-08-29", "dag", 6, 2),  # Jonas Bakke
    (3074, "2026-08-29", "dag", 13, 2),  # Ole Kristiansen
    (3075, "2026-08-29", "kveld", 21, 2),  # Line Moe
    (3076, "2026-08-29", "natt", 2, 2),  # Eirik Moen
    (3077, "2026-08-29", "natt", 8, 2),  # Kristin Berg
    # søndag 30.08
    (3078, "2026-08-30", "dag", 13, 2),  # Ole Kristiansen
    (3079, "2026-08-30", "dag", 16, 2),  # Camilla Ruud
    (3080, "2026-08-30", "dag", 18, 2),  # Ida Pedersen
    (3081, "2026-08-30", "kveld", 21, 2),  # Line Moe
    (3082, "2026-08-30", "natt", 2, 2),  # Eirik Moen
    (3083, "2026-08-30", "natt", 8, 2),  # Kristin Berg
    # Uke 36
    # mandag 31.08
    (3084, "2026-08-31", "dag", 4, 2),  # Ingrid Dahl
    (3085, "2026-08-31", "dag", 6, 2),  # Jonas Bakke
    (3086, "2026-08-31", "dag", 10, 2),  # Nora Lie
    (3087, "2026-08-31", "dag", 17, 2),  # Henrik Aas
    (3088, "2026-08-31", "dag", 19, 2),  # Tone Brekke
    (3089, "2026-08-31", "dag", 20, 2),  # Even Sandvik
    (3090, "2026-08-31", "dag", 22, 2),  # Kjetil Fjeld
    (3091, "2026-08-31", "kveld", 11, 2),  # Anders Strand
    (3092, "2026-08-31", "kveld", 16, 2),  # Camilla Ruud
    (3093, "2026-08-31", "kveld", 25, 2),  # Martin Hagen
    (3094, "2026-08-31", "natt", 5, 2),  # Mette Solberg
    (3095, "2026-08-31", "natt", 8, 2),  # Kristin Berg
    (3096, "2026-08-31", "natt", 14, 2),  # Marte Eide
    (3097, "2026-08-31", "natt", 24, 2),  # Stian Vik
    # tirsdag 01.09
    (3098, "2026-09-01", "dag", 1, 2),  # Silje Amundsen
    (3099, "2026-09-01", "dag", 9, 2),  # Lars Haugen
    (3100, "2026-09-01", "dag", 10, 2),  # Nora Lie
    (3101, "2026-09-01", "dag", 12, 2),  # Hanne Johansen
    (3102, "2026-09-01", "dag", 13, 2),  # Ole Kristiansen
    (3103, "2026-09-01", "dag", 15, 2),  # Sindre Lunde
    (3104, "2026-09-01", "dag", 23, 2),  # Astrid Holm
    (3105, "2026-09-01", "kveld", 7, 2),  # Per Halvorsen
    (3106, "2026-09-01", "kveld", 11, 2),  # Anders Strand
    (3107, "2026-09-01", "kveld", 16, 2),  # Camilla Ruud
    (3108, "2026-09-01", "kveld", 18, 2),  # Ida Pedersen
    (3109, "2026-09-01", "kveld", 21, 2),  # Line Moe
    (3110, "2026-09-01", "kveld", 25, 2),  # Martin Hagen
    (3111, "2026-09-01", "natt", 3, 2),  # Thomas Nygård
    (3112, "2026-09-01", "natt", 5, 2),  # Mette Solberg
    (3113, "2026-09-01", "natt", 14, 2),  # Marte Eide
    (3114, "2026-09-01", "natt", 24, 2),  # Stian Vik
    # onsdag 02.09
    (3115, "2026-09-02", "dag", 1, 2),  # Silje Amundsen
    (3116, "2026-09-02", "dag", 4, 2),  # Ingrid Dahl
    (3117, "2026-09-02", "dag", 6, 2),  # Jonas Bakke
    (3118, "2026-09-02", "dag", 12, 2),  # Hanne Johansen
    (3119, "2026-09-02", "dag", 17, 2),  # Henrik Aas
    (3120, "2026-09-02", "dag", 19, 2),  # Tone Brekke
    (3121, "2026-09-02", "dag", 20, 2),  # Even Sandvik
    (3122, "2026-09-02", "dag", 22, 2),  # Kjetil Fjeld
    (3123, "2026-09-02", "dag", 23, 2),  # Astrid Holm
    (3124, "2026-09-02", "kveld", 7, 2),  # Per Halvorsen
    (3125, "2026-09-02", "kveld", 18, 2),  # Ida Pedersen
    (3126, "2026-09-02", "kveld", 21, 2),  # Line Moe
    (3127, "2026-09-02", "natt", 2, 2),  # Eirik Moen
    (3128, "2026-09-02", "natt", 3, 2),  # Thomas Nygård
    # torsdag 03.09
    (3129, "2026-09-03", "dag", 1, 2),  # Silje Amundsen
    (3130, "2026-09-03", "dag", 9, 2),  # Lars Haugen
    (3131, "2026-09-03", "dag", 11, 2),  # Anders Strand
    (3132, "2026-09-03", "dag", 17, 2),  # Henrik Aas
    (3133, "2026-09-03", "dag", 19, 2),  # Tone Brekke
    (3134, "2026-09-03", "kveld", 4, 2),  # Ingrid Dahl
    (3135, "2026-09-03", "kveld", 13, 2),  # Ole Kristiansen
    (3136, "2026-09-03", "natt", 2, 2),  # Eirik Moen
    (3137, "2026-09-03", "natt", 15, 2),  # Sindre Lunde
    # fredag 04.09
    (3138, "2026-09-04", "dag", 9, 2),  # Lars Haugen
    (3139, "2026-09-04", "dag", 12, 2),  # Hanne Johansen
    (3140, "2026-09-04", "dag", 16, 2),  # Camilla Ruud
    (3141, "2026-09-04", "dag", 19, 2),  # Tone Brekke
    (3142, "2026-09-04", "dag", 24, 2),  # Stian Vik
    (3143, "2026-09-04", "kveld", 4, 2),  # Ingrid Dahl
    (3144, "2026-09-04", "kveld", 6, 2),  # Jonas Bakke
    (3145, "2026-09-04", "kveld", 13, 2),  # Ole Kristiansen
    (3146, "2026-09-04", "kveld", 20, 2),  # Even Sandvik
    (3147, "2026-09-04", "kveld", 21, 2),  # Line Moe
    (3148, "2026-09-04", "natt", 15, 2),  # Sindre Lunde
    (3149, "2026-09-04", "natt", 25, 2),  # Martin Hagen
    # lørdag 05.09
    (3150, "2026-09-05", "dag", 5, 2),  # Mette Solberg
    (3151, "2026-09-05", "dag", 7, 2),  # Per Halvorsen
    (3152, "2026-09-05", "dag", 14, 2),  # Marte Eide
    (3153, "2026-09-05", "dag", 16, 2),  # Camilla Ruud
    (3154, "2026-09-05", "dag", 18, 2),  # Ida Pedersen
    (3155, "2026-09-05", "dag", 22, 2),  # Kjetil Fjeld
    (3156, "2026-09-05", "mellom", 10, 2),  # Nora Lie
    (3157, "2026-09-05", "kveld", 3, 2),  # Thomas Nygård
    (3158, "2026-09-05", "kveld", 21, 2),  # Line Moe
    (3159, "2026-09-05", "kveld", 23, 2),  # Astrid Holm
    (3160, "2026-09-05", "natt", 2, 2),  # Eirik Moen
    (3161, "2026-09-05", "natt", 8, 2),  # Kristin Berg
    # søndag 06.09
    (3162, "2026-09-06", "dag", 7, 2),  # Per Halvorsen
    (3163, "2026-09-06", "dag", 14, 2),  # Marte Eide
    (3164, "2026-09-06", "dag", 18, 2),  # Ida Pedersen
    (3165, "2026-09-06", "dag", 22, 2),  # Kjetil Fjeld
    (3166, "2026-09-06", "mellom", 10, 2),  # Nora Lie
    (3167, "2026-09-06", "kveld", 3, 2),  # Thomas Nygård
    (3168, "2026-09-06", "kveld", 5, 2),  # Mette Solberg
    (3169, "2026-09-06", "natt", 2, 2),  # Eirik Moen
    (3170, "2026-09-06", "natt", 8, 2),  # Kristin Berg
    # Uke 37
    # mandag 07.09
    (3171, "2026-09-07", "dag", 4, 2),  # Ingrid Dahl
    (3172, "2026-09-07", "dag", 18, 2),  # Ida Pedersen
    (3173, "2026-09-07", "dag", 20, 2),  # Even Sandvik
    (3174, "2026-09-07", "dag", 23, 2),  # Astrid Holm
    (3175, "2026-09-07", "dag", 24, 2),  # Stian Vik
    (3176, "2026-09-07", "mellom", 9, 2),  # Lars Haugen
    (3177, "2026-09-07", "mellom", 12, 2),  # Hanne Johansen
    (3178, "2026-09-07", "kveld", 1, 2),  # Silje Amundsen
    (3179, "2026-09-07", "kveld", 7, 2),  # Per Halvorsen
    (3180, "2026-09-07", "kveld", 15, 2),  # Sindre Lunde
    (3181, "2026-09-07", "natt", 2, 2),  # Eirik Moen
    (3182, "2026-09-07", "natt", 13, 2),  # Ole Kristiansen
    # tirsdag 08.09
    (3183, "2026-09-08", "dag", 3, 2),  # Thomas Nygård
    (3184, "2026-09-08", "dag", 4, 2),  # Ingrid Dahl
    (3185, "2026-09-08", "dag", 6, 2),  # Jonas Bakke
    (3186, "2026-09-08", "dag", 11, 2),  # Anders Strand
    (3187, "2026-09-08", "dag", 14, 2),  # Marte Eide
    (3188, "2026-09-08", "dag", 19, 2),  # Tone Brekke
    (3189, "2026-09-08", "dag", 20, 2),  # Even Sandvik
    (3190, "2026-09-08", "dag", 23, 2),  # Astrid Holm
    (3191, "2026-09-08", "mellom", 9, 2),  # Lars Haugen
    (3192, "2026-09-08", "mellom", 16, 2),  # Camilla Ruud
    (3193, "2026-09-08", "kveld", 1, 2),  # Silje Amundsen
    (3194, "2026-09-08", "kveld", 10, 2),  # Nora Lie
    (3195, "2026-09-08", "kveld", 15, 2),  # Sindre Lunde
    (3196, "2026-09-08", "kveld", 25, 2),  # Martin Hagen
    (3197, "2026-09-08", "natt", 5, 2),  # Mette Solberg
    (3198, "2026-09-08", "natt", 8, 2),  # Kristin Berg
    (3199, "2026-09-08", "natt", 22, 2),  # Kjetil Fjeld
    # onsdag 09.09
    (3200, "2026-09-09", "dag", 3, 2),  # Thomas Nygård
    (3201, "2026-09-09", "dag", 11, 2),  # Anders Strand
    (3202, "2026-09-09", "dag", 14, 2),  # Marte Eide
    (3203, "2026-09-09", "dag", 18, 2),  # Ida Pedersen
    (3204, "2026-09-09", "dag", 19, 2),  # Tone Brekke
    (3205, "2026-09-09", "dag", 24, 2),  # Stian Vik
    (3206, "2026-09-09", "mellom", 12, 2),  # Hanne Johansen
    (3207, "2026-09-09", "mellom", 16, 2),  # Camilla Ruud
    (3208, "2026-09-09", "kveld", 4, 2),  # Ingrid Dahl
    (3209, "2026-09-09", "kveld", 7, 2),  # Per Halvorsen
    (3210, "2026-09-09", "kveld", 10, 2),  # Nora Lie
    (3211, "2026-09-09", "kveld", 17, 2),  # Henrik Aas
    (3212, "2026-09-09", "kveld", 21, 2),  # Line Moe
    (3213, "2026-09-09", "kveld", 25, 2),  # Martin Hagen
    (3214, "2026-09-09", "natt", 5, 2),  # Mette Solberg
    (3215, "2026-09-09", "natt", 8, 2),  # Kristin Berg
    (3216, "2026-09-09", "natt", 22, 2),  # Kjetil Fjeld
    # torsdag 10.09
    (3217, "2026-09-10", "dag", 6, 2),  # Jonas Bakke
    (3218, "2026-09-10", "dag", 15, 2),  # Sindre Lunde
    (3219, "2026-09-10", "dag", 18, 2),  # Ida Pedersen
    (3220, "2026-09-10", "dag", 23, 2),  # Astrid Holm
    (3221, "2026-09-10", "kveld", 7, 2),  # Per Halvorsen
    (3222, "2026-09-10", "kveld", 17, 2),  # Henrik Aas
    (3223, "2026-09-10", "kveld", 20, 2),  # Even Sandvik
    (3224, "2026-09-10", "kveld", 21, 2),  # Line Moe
    (3225, "2026-09-10", "natt", 3, 2),  # Thomas Nygård
    (3226, "2026-09-10", "natt", 5, 2),  # Mette Solberg
    (3227, "2026-09-10", "natt", 8, 2),  # Kristin Berg
    (3228, "2026-09-10", "natt", 13, 2),  # Ole Kristiansen
    # fredag 11.09
    (3229, "2026-09-11", "dag", 1, 2),  # Silje Amundsen
    (3230, "2026-09-11", "dag", 10, 2),  # Nora Lie
    (3231, "2026-09-11", "dag", 16, 2),  # Camilla Ruud
    (3232, "2026-09-11", "dag", 19, 2),  # Tone Brekke
    (3233, "2026-09-11", "dag", 22, 2),  # Kjetil Fjeld
    (3234, "2026-09-11", "dag", 23, 2),  # Astrid Holm
    (3235, "2026-09-11", "dag", 24, 2),  # Stian Vik
    (3236, "2026-09-11", "kveld", 9, 2),  # Lars Haugen
    (3237, "2026-09-11", "kveld", 14, 2),  # Marte Eide
    (3238, "2026-09-11", "kveld", 17, 2),  # Henrik Aas
    (3239, "2026-09-11", "kveld", 21, 2),  # Line Moe
    (3240, "2026-09-11", "natt", 2, 2),  # Eirik Moen
    (3241, "2026-09-11", "natt", 13, 2),  # Ole Kristiansen
    # lørdag 12.09
    (3242, "2026-09-12", "dag", 1, 2),  # Silje Amundsen
    (3243, "2026-09-12", "dag", 4, 2),  # Ingrid Dahl
    (3244, "2026-09-12", "dag", 12, 2),  # Hanne Johansen
    (3245, "2026-09-12", "kveld", 9, 2),  # Lars Haugen
    (3246, "2026-09-12", "kveld", 11, 2),  # Anders Strand
    (3247, "2026-09-12", "natt", 2, 2),  # Eirik Moen
    (3248, "2026-09-12", "natt", 25, 2),  # Martin Hagen
    # søndag 13.09
    (3249, "2026-09-13", "dag", 1, 2),  # Silje Amundsen
    (3250, "2026-09-13", "dag", 4, 2),  # Ingrid Dahl
    (3251, "2026-09-13", "dag", 12, 2),  # Hanne Johansen
    (3252, "2026-09-13", "kveld", 11, 2),  # Anders Strand
    (3253, "2026-09-13", "natt", 2, 2),  # Eirik Moen
    (3254, "2026-09-13", "natt", 25, 2),  # Martin Hagen
    # Uke 38
    # mandag 14.09
    (3255, "2026-09-14", "dag", 1, 2),  # Silje Amundsen
    (3256, "2026-09-14", "dag", 3, 2),  # Thomas Nygård
    (3257, "2026-09-14", "dag", 4, 2),  # Ingrid Dahl
    (3258, "2026-09-14", "dag", 5, 2),  # Mette Solberg
    (3259, "2026-09-14", "dag", 6, 2),  # Jonas Bakke
    (3260, "2026-09-14", "dag", 12, 2),  # Hanne Johansen
    (3261, "2026-09-14", "dag", 15, 2),  # Sindre Lunde
    (3262, "2026-09-14", "dag", 19, 2),  # Tone Brekke
    (3263, "2026-09-14", "dag", 22, 2),  # Kjetil Fjeld
    (3264, "2026-09-14", "mellom", 17, 2),  # Henrik Aas
    (3265, "2026-09-14", "kveld", 10, 2),  # Nora Lie
    (3266, "2026-09-14", "kveld", 21, 2),  # Line Moe
    (3267, "2026-09-14", "natt", 2, 2),  # Eirik Moen
    (3268, "2026-09-14", "natt", 14, 2),  # Marte Eide
    (3269, "2026-09-14", "natt", 16, 2),  # Camilla Ruud
    # tirsdag 15.09
    (3270, "2026-09-15", "dag", 7, 2),  # Per Halvorsen
    (3271, "2026-09-15", "dag", 9, 2),  # Lars Haugen
    (3272, "2026-09-15", "dag", 12, 2),  # Hanne Johansen
    (3273, "2026-09-15", "dag", 19, 2),  # Tone Brekke
    (3274, "2026-09-15", "dag", 20, 2),  # Even Sandvik
    (3275, "2026-09-15", "mellom", 11, 2),  # Anders Strand
    (3276, "2026-09-15", "mellom", 18, 2),  # Ida Pedersen
    (3277, "2026-09-15", "kveld", 3, 2),  # Thomas Nygård
    (3278, "2026-09-15", "kveld", 10, 2),  # Nora Lie
    (3279, "2026-09-15", "kveld", 13, 2),  # Ole Kristiansen
    (3280, "2026-09-15", "kveld", 21, 2),  # Line Moe
    (3281, "2026-09-15", "kveld", 23, 2),  # Astrid Holm
    (3282, "2026-09-15", "natt", 16, 2),  # Camilla Ruud
    (3283, "2026-09-15", "natt", 17, 2),  # Henrik Aas
    (3284, "2026-09-15", "natt", 24, 2),  # Stian Vik
    # onsdag 16.09
    (3285, "2026-09-16", "dag", 1, 2),  # Silje Amundsen
    (3286, "2026-09-16", "dag", 6, 2),  # Jonas Bakke
    (3287, "2026-09-16", "dag", 7, 2),  # Per Halvorsen
    (3288, "2026-09-16", "dag", 9, 2),  # Lars Haugen
    (3289, "2026-09-16", "mellom", 11, 2),  # Anders Strand
    (3290, "2026-09-16", "mellom", 18, 2),  # Ida Pedersen
    (3291, "2026-09-16", "kveld", 4, 2),  # Ingrid Dahl
    (3292, "2026-09-16", "kveld", 13, 2),  # Ole Kristiansen
    (3293, "2026-09-16", "kveld", 23, 2),  # Astrid Holm
    (3294, "2026-09-16", "kveld", 25, 2),  # Martin Hagen
    (3295, "2026-09-16", "natt", 5, 2),  # Mette Solberg
    (3296, "2026-09-16", "natt", 8, 2),  # Kristin Berg
    # torsdag 17.09
    (3297, "2026-09-17", "dag", 1, 2),  # Silje Amundsen
    (3298, "2026-09-17", "dag", 11, 2),  # Anders Strand
    (3299, "2026-09-17", "dag", 19, 2),  # Tone Brekke
    (3300, "2026-09-17", "dag", 20, 2),  # Even Sandvik
    (3301, "2026-09-17", "dag", 24, 2),  # Stian Vik
    (3302, "2026-09-17", "kveld", 14, 2),  # Marte Eide
    (3303, "2026-09-17", "kveld", 15, 2),  # Sindre Lunde
    (3304, "2026-09-17", "kveld", 18, 2),  # Ida Pedersen
    (3305, "2026-09-17", "kveld", 21, 2),  # Line Moe
    (3306, "2026-09-17", "kveld", 25, 2),  # Martin Hagen
    (3307, "2026-09-17", "natt", 2, 2),  # Eirik Moen
    (3308, "2026-09-17", "natt", 5, 2),  # Mette Solberg
    (3309, "2026-09-17", "natt", 8, 2),  # Kristin Berg
    # fredag 18.09
    (3310, "2026-09-18", "dag", 3, 2),  # Thomas Nygård
    (3311, "2026-09-18", "dag", 4, 2),  # Ingrid Dahl
    (3312, "2026-09-18", "dag", 9, 2),  # Lars Haugen
    (3313, "2026-09-18", "dag", 10, 2),  # Nora Lie
    (3314, "2026-09-18", "dag", 17, 2),  # Henrik Aas
    (3315, "2026-09-18", "dag", 19, 2),  # Tone Brekke
    (3316, "2026-09-18", "dag", 23, 2),  # Astrid Holm
    (3317, "2026-09-18", "mellom", 12, 2),  # Hanne Johansen
    (3318, "2026-09-18", "kveld", 14, 2),  # Marte Eide
    (3319, "2026-09-18", "kveld", 15, 2),  # Sindre Lunde
    (3320, "2026-09-18", "kveld", 16, 2),  # Camilla Ruud
    (3321, "2026-09-18", "kveld", 20, 2),  # Even Sandvik
    (3322, "2026-09-18", "kveld", 21, 2),  # Line Moe
    (3323, "2026-09-18", "natt", 2, 2),  # Eirik Moen
    (3324, "2026-09-18", "natt", 25, 2),  # Martin Hagen
    # lørdag 19.09
    (3325, "2026-09-19", "dag", 3, 2),  # Thomas Nygård
    (3326, "2026-09-19", "dag", 6, 2),  # Jonas Bakke
    (3327, "2026-09-19", "dag", 10, 2),  # Nora Lie
    (3328, "2026-09-19", "mellom", 13, 2),  # Ole Kristiansen
    (3329, "2026-09-19", "kveld", 7, 2),  # Per Halvorsen
    (3330, "2026-09-19", "natt", 8, 2),  # Kristin Berg
    (3331, "2026-09-19", "natt", 22, 2),  # Kjetil Fjeld
    # søndag 20.09
    (3332, "2026-09-20", "dag", 10, 2),  # Nora Lie
    (3333, "2026-09-20", "dag", 12, 2),  # Hanne Johansen
    (3334, "2026-09-20", "dag", 18, 2),  # Ida Pedersen
    (3335, "2026-09-20", "mellom", 13, 2),  # Ole Kristiansen
    (3336, "2026-09-20", "kveld", 6, 2),  # Jonas Bakke
    (3337, "2026-09-20", "kveld", 7, 2),  # Per Halvorsen
    (3338, "2026-09-20", "natt", 15, 2),  # Sindre Lunde
    (3339, "2026-09-20", "natt", 22, 2),  # Kjetil Fjeld
]

# Perioden 21.09–04.10, vaktnummer #4100–#4299. Numrene fra mockupene er beholdt:
# #4127, #4128, #4130, #4131, #4135, #4136 og #4189.
PERIODE: list[tuple[int, str, str, int | None, int]] = [
    # Uke 39
    # mandag 21.09
    (4100, "2026-09-21", "dag", 1, 2),  # Silje Amundsen
    (4101, "2026-09-21", "dag", 3, 2),  # Thomas Nygård
    (4102, "2026-09-21", "dag", 4, 2),  # Ingrid Dahl
    (4103, "2026-09-21", "dag", 5, 2),  # Mette Solberg
    (4104, "2026-09-21", "mellom", 9, 2),  # Lars Haugen
    (4105, "2026-09-21", "mellom", 12, 2),  # Hanne Johansen
    (4106, "2026-09-21", "kveld", 7, 2),  # Per Halvorsen
    (4107, "2026-09-21", "kveld", 16, 2),  # Camilla Ruud
    (4108, "2026-09-21", "kveld", 25, 2),  # Martin Hagen
    (4109, "2026-09-21", "natt", 2, 2),  # Eirik Moen
    (4110, "2026-09-21", "natt", 22, 2),  # Kjetil Fjeld
    (4111, "2026-09-21", "natt", 24, 2),  # Stian Vik
    # tirsdag 22.09
    (4112, "2026-09-22", "dag", 1, 2),  # Silje Amundsen
    (4113, "2026-09-22", "dag", 3, 2),  # Thomas Nygård
    (4114, "2026-09-22", "dag", 4, 2),  # Ingrid Dahl
    (4115, "2026-09-22", "dag", 6, 2),  # Jonas Bakke
    (4116, "2026-09-22", "dag", 14, 2),  # Marte Eide
    (4117, "2026-09-22", "mellom", 9, 2),  # Lars Haugen
    (4118, "2026-09-22", "mellom", 11, 2),  # Anders Strand
    (4119, "2026-09-22", "mellom", 12, 2),  # Hanne Johansen
    (4120, "2026-09-22", "kveld", 7, 2),  # Per Halvorsen
    (4121, "2026-09-22", "kveld", 16, 2),  # Camilla Ruud
    (4122, "2026-09-22", "kveld", 21, 2),  # Line Moe
    (4123, "2026-09-22", "natt", 2, 2),  # Eirik Moen
    (4124, "2026-09-22", "natt", 8, 2),  # Kristin Berg
    (4125, "2026-09-22", "natt", 22, 2),  # Kjetil Fjeld
    # onsdag 23.09
    (4126, "2026-09-23", "dag", 3, 2),  # Thomas Nygård
    (4129, "2026-09-23", "dag", 4, 2),  # Ingrid Dahl
    (4132, "2026-09-23", "dag", 5, 2),  # Mette Solberg
    (4133, "2026-09-23", "dag", 10, 2),  # Nora Lie
    (4134, "2026-09-23", "dag", 18, 2),  # Ida Pedersen
    (4137, "2026-09-23", "mellom", 11, 2),  # Anders Strand
    (4138, "2026-09-23", "mellom", 19, 2),  # Tone Brekke
    (4139, "2026-09-23", "kveld", 13, 2),  # Ole Kristiansen
    (4140, "2026-09-23", "kveld", 20, 2),  # Even Sandvik
    (4141, "2026-09-23", "kveld", 21, 2),  # Line Moe
    (4142, "2026-09-23", "kveld", 25, 2),  # Martin Hagen
    (4143, "2026-09-23", "natt", 2, 2),  # Eirik Moen
    (4144, "2026-09-23", "natt", 8, 2),  # Kristin Berg
    (4145, "2026-09-23", "natt", 24, 2),  # Stian Vik
    # torsdag 24.09
    (4146, "2026-09-24", "dag", 4, 2),  # Ingrid Dahl
    (4147, "2026-09-24", "dag", 6, 2),  # Jonas Bakke
    (4148, "2026-09-24", "dag", 10, 2),  # Nora Lie
    (4149, "2026-09-24", "dag", 14, 2),  # Marte Eide
    (4150, "2026-09-24", "dag", 18, 2),  # Ida Pedersen
    (4151, "2026-09-24", "mellom", 19, 2),  # Tone Brekke
    (4152, "2026-09-24", "mellom", 23, 2),  # Astrid Holm
    (4153, "2026-09-24", "kveld", 1, 2),  # Silje Amundsen
    (4154, "2026-09-24", "kveld", 11, 2),  # Anders Strand
    (4155, "2026-09-24", "kveld", 13, 2),  # Ole Kristiansen
    (4156, "2026-09-24", "kveld", 21, 2),  # Line Moe
    (4157, "2026-09-24", "natt", 8, 2),  # Kristin Berg
    (4158, "2026-09-24", "natt", 15, 2),  # Sindre Lunde
    (4159, "2026-09-24", "natt", 17, 2),  # Henrik Aas
    # fredag 25.09
    (4160, "2026-09-25", "dag", 14, 2),  # Marte Eide
    (4161, "2026-09-25", "dag", 18, 2),  # Ida Pedersen
    (4162, "2026-09-25", "dag", 20, 2),  # Even Sandvik
    (4163, "2026-09-25", "dag", 24, 2),  # Stian Vik
    (4164, "2026-09-25", "mellom", 19, 2),  # Tone Brekke
    (4165, "2026-09-25", "kveld", 1, 2),  # Silje Amundsen
    (4166, "2026-09-25", "kveld", 11, 2),  # Anders Strand
    (4167, "2026-09-25", "kveld", 23, 2),  # Astrid Holm
    (4168, "2026-09-25", "natt", 15, 2),  # Sindre Lunde
    (4169, "2026-09-25", "natt", 17, 2),  # Henrik Aas
    (4170, "2026-09-25", "natt", 25, 2),  # Martin Hagen
    # lørdag 26.09
    (4171, "2026-09-26", "dag", 12, 2),  # Hanne Johansen
    (4172, "2026-09-26", "dag", 20, 2),  # Even Sandvik
    (4173, "2026-09-26", "dag", 22, 2),  # Kjetil Fjeld
    (4174, "2026-09-26", "mellom", 16, 2),  # Camilla Ruud
    (4175, "2026-09-26", "kveld", 10, 2),  # Nora Lie
    (4176, "2026-09-26", "natt", 9, 2),  # Lars Haugen
    # søndag 27.09
    (4127, "2026-09-27", "dag", None, 3),  # mangler bemanning
    (4177, "2026-09-27", "dag", 12, 2),  # Hanne Johansen
    (4178, "2026-09-27", "dag", 13, 2),  # Ole Kristiansen
    (4179, "2026-09-27", "dag", 14, 2),  # Marte Eide
    (4180, "2026-09-27", "dag", 15, 2),  # Sindre Lunde
    (4181, "2026-09-27", "dag", 16, 2),  # Camilla Ruud
    (4182, "2026-09-27", "mellom", 17, 2),  # Henrik Aas
    (4183, "2026-09-27", "mellom", 18, 2),  # Ida Pedersen
    (4128, "2026-09-27", "kveld", 7, 2),  # Per Halvorsen
    (4184, "2026-09-27", "natt", 8, 2),  # Kristin Berg
    # Uke 40
    # mandag 28.09
    (4130, "2026-09-28", "dag", 5, 2),  # Mette Solberg
    (4185, "2026-09-28", "dag", 11, 2),  # Anders Strand
    (4186, "2026-09-28", "dag", 12, 2),  # Hanne Johansen
    (4187, "2026-09-28", "dag", 13, 2),  # Ole Kristiansen
    (4188, "2026-09-28", "dag", 22, 2),  # Kjetil Fjeld
    (4190, "2026-09-28", "mellom", 17, 2),  # Henrik Aas
    (4191, "2026-09-28", "mellom", 23, 2),  # Astrid Holm
    (4192, "2026-09-28", "kveld", 7, 2),  # Per Halvorsen
    (4193, "2026-09-28", "kveld", 10, 2),  # Nora Lie
    (4194, "2026-09-28", "kveld", 25, 2),  # Martin Hagen
    (4189, "2026-09-28", "natt", None, 3),  # mangler bemanning
    (4131, "2026-09-28", "natt", 3, 2),  # Thomas Nygård
    (4195, "2026-09-28", "natt", 8, 2),  # Kristin Berg
    # tirsdag 29.09
    (4135, "2026-09-29", "dag", 6, 2),  # Jonas Bakke
    (4196, "2026-09-29", "dag", 14, 2),  # Marte Eide
    (4197, "2026-09-29", "dag", 15, 2),  # Sindre Lunde
    (4198, "2026-09-29", "dag", 16, 2),  # Camilla Ruud
    (4199, "2026-09-29", "dag", 24, 2),  # Stian Vik
    (4200, "2026-09-29", "mellom", 9, 2),  # Lars Haugen
    (4201, "2026-09-29", "mellom", 18, 2),  # Ida Pedersen
    (4136, "2026-09-29", "kveld", 4, 2),  # Ingrid Dahl
    (4202, "2026-09-29", "kveld", 10, 2),  # Nora Lie
    (4203, "2026-09-29", "kveld", 25, 2),  # Martin Hagen
    (4204, "2026-09-29", "natt", 3, 2),  # Thomas Nygård
    (4205, "2026-09-29", "natt", 8, 2),  # Kristin Berg
    (4206, "2026-09-29", "natt", 21, 2),  # Line Moe
    # onsdag 30.09
    (4207, "2026-09-30", "dag", 5, 2),  # Mette Solberg
    (4208, "2026-09-30", "dag", 6, 2),  # Jonas Bakke
    (4209, "2026-09-30", "dag", 11, 2),  # Anders Strand
    (4210, "2026-09-30", "dag", 14, 2),  # Marte Eide
    (4211, "2026-09-30", "dag", 16, 2),  # Camilla Ruud
    (4212, "2026-09-30", "dag", 19, 2),  # Tone Brekke
    (4213, "2026-09-30", "dag", 24, 2),  # Stian Vik
    (4214, "2026-09-30", "mellom", 9, 2),  # Lars Haugen
    (4215, "2026-09-30", "mellom", 17, 2),  # Henrik Aas
    (4216, "2026-09-30", "mellom", 18, 2),  # Ida Pedersen
    (4217, "2026-09-30", "kveld", 4, 2),  # Ingrid Dahl
    (4218, "2026-09-30", "kveld", 20, 2),  # Even Sandvik
    (4219, "2026-09-30", "natt", 7, 2),  # Per Halvorsen
    (4220, "2026-09-30", "natt", 21, 2),  # Line Moe
    (4221, "2026-09-30", "natt", 22, 2),  # Kjetil Fjeld
    # torsdag 01.10
    (4222, "2026-10-01", "dag", 1, 2),  # Silje Amundsen
    (4223, "2026-10-01", "dag", 5, 2),  # Mette Solberg
    (4224, "2026-10-01", "dag", 11, 2),  # Anders Strand
    (4225, "2026-10-01", "dag", 16, 2),  # Camilla Ruud
    (4226, "2026-10-01", "dag", 19, 2),  # Tone Brekke
    (4227, "2026-10-01", "dag", 23, 2),  # Astrid Holm
    (4228, "2026-10-01", "kveld", 12, 2),  # Hanne Johansen
    (4229, "2026-10-01", "kveld", 15, 2),  # Sindre Lunde
    (4230, "2026-10-01", "kveld", 20, 2),  # Even Sandvik
    (4231, "2026-10-01", "natt", 7, 2),  # Per Halvorsen
    (4232, "2026-10-01", "natt", 22, 2),  # Kjetil Fjeld
    (4233, "2026-10-01", "natt", 25, 2),  # Martin Hagen
    # fredag 02.10
    (4234, "2026-10-02", "dag", 1, 2),  # Silje Amundsen
    (4235, "2026-10-02", "dag", 3, 2),  # Thomas Nygård
    (4236, "2026-10-02", "dag", 10, 2),  # Nora Lie
    (4237, "2026-10-02", "dag", 17, 2),  # Henrik Aas
    (4238, "2026-10-02", "dag", 18, 2),  # Ida Pedersen
    (4239, "2026-10-02", "dag", 23, 2),  # Astrid Holm
    (4240, "2026-10-02", "kveld", 12, 2),  # Hanne Johansen
    (4241, "2026-10-02", "kveld", 13, 2),  # Ole Kristiansen
    (4242, "2026-10-02", "kveld", 14, 2),  # Marte Eide
    (4243, "2026-10-02", "kveld", 15, 2),  # Sindre Lunde
    (4244, "2026-10-02", "kveld", 19, 2),  # Tone Brekke
    (4245, "2026-10-02", "kveld", 21, 2),  # Line Moe
    (4246, "2026-10-02", "natt", 8, 2),  # Kristin Berg
    (4247, "2026-10-02", "natt", 24, 2),  # Stian Vik
    (4248, "2026-10-02", "natt", 25, 2),  # Martin Hagen
    # lørdag 03.10
    (4249, "2026-10-03", "dag", 3, 2),  # Thomas Nygård
    (4250, "2026-10-03", "dag", 4, 2),  # Ingrid Dahl
    (4251, "2026-10-03", "dag", 9, 2),  # Lars Haugen
    (4252, "2026-10-03", "dag", 10, 2),  # Nora Lie
    (4253, "2026-10-03", "dag", 18, 2),  # Ida Pedersen
    (4254, "2026-10-03", "kveld", 6, 2),  # Jonas Bakke
    (4255, "2026-10-03", "kveld", 13, 2),  # Ole Kristiansen
    (4256, "2026-10-03", "kveld", 14, 2),  # Marte Eide
    (4257, "2026-10-03", "kveld", 21, 2),  # Line Moe
    (4258, "2026-10-03", "natt", 8, 2),  # Kristin Berg
    (4259, "2026-10-03", "natt", 15, 2),  # Sindre Lunde
    (4260, "2026-10-03", "natt", 24, 2),  # Stian Vik
    # søndag 04.10
    (4261, "2026-10-04", "dag", 4, 2),  # Ingrid Dahl
    (4262, "2026-10-04", "dag", 9, 2),  # Lars Haugen
    (4263, "2026-10-04", "dag", 20, 2),  # Even Sandvik
    (4264, "2026-10-04", "kveld", 6, 2),  # Jonas Bakke
    (4265, "2026-10-04", "natt", 12, 2),  # Hanne Johansen
]

# Fasit beregnet på forhånd (AV-07). For hver vakt: ansattnavn → regelen som
# utelukker vedkommende, eller "gyldig". Den som var satt opp, er ikke med
# (AV-06), så hver vakt har 24 kandidater. Ingen bryter mer enn én regel.
#
# "rangering" for #4127 er beregnet med vektene 40/20/15/25 og formlene i PRD
# §4.4 (kontrollert etter KS-02), med uavrundet totalscore (K-03). Ved lik
# totalscore avgjør stigende ansatt-ID (AV-05). Inputene står ved siden av, så
# testene kan sjekke at dataene gir nøyaktig dem. Selve rangeringen testes i
# story 4.4.
#   kostnad = 8 t til ordinær sats, timer over 36 i uka til 150 %
#   kostnadspoeng og timepoeng: min–maks blant de gyldige (lavest = 100)
#   Ulempescore = 100 × (1 − Ulempepoeng / 300)
#   Jonas:  0,40 × 84,7619 + 0,20 × 100 + 0,15 × 86,6667 + 0,25 × 75 = 85,6548
#   Mette:  0,40 × 84,7619 + 0,20 × 100 + 0,15 × 40,0000 + 0,25 × 75 = 78,6548
#   Thomas: 0,40 × 100     + 0,20 × 50  + 0,15 × 60,0000 + 0,25 × 0  = 59,0
#   Ingrid: 0,40 × 0       + 0,20 × 0   + 0,15 × 80,0000 + 0,25 × 100 = 37,0
# Jonas og Mette skiller seg bare på Ulempebelastningen: 0,15 × 46,67 = 7,0 (AV-12).
FASIT: dict[int, dict] = {
    4127: {
        "utfall": {
            "Eirik Moen": "kompetanse",
            "Thomas Nygård": "gyldig",
            "Ingrid Dahl": "gyldig",
            "Mette Solberg": "gyldig",
            "Jonas Bakke": "gyldig",
            "Per Halvorsen": "elleve-timer",  # #4128 kveld 27.09, 0 t hvile etter
            "Kristin Berg": "elleve-timer",  # natt 27.09 23:00, 8 t etter
            "Lars Haugen": "elleve-timer",  # natt 26.09 23:00–27.09 07:00, 0 t før
            "Nora Lie": "elleve-timer",  # kveld 26.09, 8 t før
            "Anders Strand": "trettifem-timer",  # lengste fri i uke 39 blir 34 t
            "Hanne Johansen": "kolliderende",  # dag 27.09
            "Ole Kristiansen": "kolliderende",  # dag 27.09
            "Marte Eide": "kolliderende",  # dag 27.09
            "Sindre Lunde": "kolliderende",  # dag 27.09
            "Camilla Ruud": "kolliderende",  # dag 27.09
            "Henrik Aas": "kolliderende",  # mellom 27.09
            "Ida Pedersen": "kolliderende",  # mellom 27.09
            "Tone Brekke": "kompetanse",
            "Even Sandvik": "kompetanse",
            "Line Moe": "kompetanse",
            "Kjetil Fjeld": "kompetanse",
            "Astrid Holm": "kompetanse",
            "Stian Vik": "kompetanse",
            "Martin Hagen": "kompetanse",  # mangler nivå for dag
        },
        "rangering": [
            {
                "navn": "Jonas Bakke",
                "timelønn": 370,
                "timer_uke": 16,
                "preferansepoeng": 75,
                "ulempepoeng": 40,
                "kostnad": 2960,
                "totalscore": 85.65476190476191,
            },
            {
                "navn": "Mette Solberg",
                "timelønn": 370,
                "timer_uke": 16,
                "preferansepoeng": 75,
                "ulempepoeng": 180,
                "kostnad": 2960,
                "totalscore": 78.65476190476191,
            },
            {
                "navn": "Thomas Nygård",
                "timelønn": 350,
                "timer_uke": 24,
                "preferansepoeng": 0,
                "ulempepoeng": 120,
                "kostnad": 2800,
                "totalscore": 59.0,
            },
            {
                "navn": "Ingrid Dahl",
                "timelønn": 385,
                "timer_uke": 32,
                "preferansepoeng": 100,
                "ulempepoeng": 60,
                "kostnad": 3850,  # 4 t ordinær + 4 t overtid
                "totalscore": 37.0,
            },
        ],
    },
    4189: {
        "utfall": {
            "Silje Amundsen": "kompetanse",  # mangler nivå for natt
            "Thomas Nygård": "kolliderende",  # #4131
            "Ingrid Dahl": "elleve-timer",  # #4136 kveld 29.09, 8 t
            "Mette Solberg": "elleve-timer",  # #4130 dag 28.09, 8 t
            "Jonas Bakke": "elleve-timer",  # #4135 dag 29.09, 0 t
            "Per Halvorsen": "elleve-timer",  # kveld 28.09, 0 t
            "Kristin Berg": "kolliderende",  # natt 28.09
            "Lars Haugen": "elleve-timer",  # mellom 29.09, 3 t
            "Nora Lie": "elleve-timer",  # kveld 28.09 og 29.09
            "Anders Strand": "elleve-timer",  # dag 28.09, 8 t
            "Hanne Johansen": "elleve-timer",  # dag 28.09, 8 t
            "Ole Kristiansen": "elleve-timer",  # dag 28.09, 8 t
            "Marte Eide": "elleve-timer",  # dag 29.09, 0 t
            "Sindre Lunde": "elleve-timer",  # dag 29.09, 0 t
            "Camilla Ruud": "elleve-timer",  # dag 29.09, 0 t
            "Henrik Aas": "elleve-timer",  # mellom 28.09, 5 t
            "Ida Pedersen": "elleve-timer",  # mellom 29.09, 3 t
            "Tone Brekke": "kompetanse",  # mangler nivå for natt
            "Even Sandvik": "kompetanse",  # natt nivå 1
            "Line Moe": "trettifem-timer",  # lengste fri i uke 40 blir 32 t
            "Kjetil Fjeld": "elleve-timer",  # dag 28.09, 8 t
            "Astrid Holm": "elleve-timer",  # mellom 28.09, 5 t
            "Stian Vik": "elleve-timer",  # dag 29.09, 0 t
            "Martin Hagen": "elleve-timer",  # kveld 28.09 og 29.09
        },
        "rangering": [],
    },
}


def tidsrom(dato: date, vakttype: str) -> tuple[datetime, datetime]:
    """Start og slutt for en vakt som starter på `dato`, i Europe/Oslo."""
    fra, til = VAKTTIDER[vakttype]
    start = datetime.combine(dato, fra, tzinfo=OSLO)
    sluttdato = dato + timedelta(days=1) if til <= fra else dato
    return start, datetime.combine(sluttdato, til, tzinfo=OSLO)


def _vaktrad(vaktnummer: int, dato: str, vakttype: str, ansatt_id: int | None, minstenivå: int) -> VaktRad:
    start, slutt = tidsrom(date.fromisoformat(dato), vakttype)
    rad = VaktRad(
        turnus_id=TURNUS_ID,
        vaktnummer=vaktnummer,
        vakttype=vakttype,
        start=start,
        slutt=slutt,
        minstenivå=minstenivå,
        tildelt_ansatt_id=ansatt_id,
        mangler_bemanning=ansatt_id is None,
    )
    if ansatt_id is None:
        rad.satt_opp_ansatt_id, rad.meldt_fra, rad.meldt_fra_grunn = MANGLER_BEMANNING[vaktnummer]
    return rad


def fyll_testdata(session: Session) -> dict[str, int]:
    """Tømmer de fire tabellene og fyller `turnus`, `ansatt` og `vakt`.

    `bruker` tømmes først på grunn av fremmednøkkelen til `turnus`, og fylles av
    `legg_til_turnusansvarlig`.

    Kalleren eier transaksjonen, slik at tømming og fylling blir én enhet.
    Dette er den eneste kodeveien som markerer en vakt som bemannet, inntil
    skrivefunksjonen for Godkjenning kommer i Epic 3.
    """
    session.execute(delete(BrukerRad))
    session.execute(delete(VaktRad))
    session.execute(delete(AnsattRad))
    session.execute(delete(TurnusRad))

    session.add(
        TurnusRad(
            id=TURNUS_ID,
            avdeling=AVDELING,
            periode_start=PERIODE_START,
            periode_slutt=PERIODE_SLUTT,
            sist_oppdatert=SIST_OPPDATERT,
        )
    )
    for ansatt_id, navn, stilling, ansiennitet, timelønn, kompetanse, preferanse in ANSATTE:
        session.add(
            AnsattRad(
                id=ansatt_id,
                navn=navn,
                stilling=stilling,
                ansiennitet=ansiennitet,
                timelønn=timelønn,
                kompetanse=dict(kompetanse),
                preferanse=PREFERANSER[preferanse][0] if preferanse else None,
            )
        )
    session.flush()
    session.add_all(_vaktrad(*rad) for rad in HISTORIKK + PERIODE)
    session.flush()

    return {
        "turnus": session.scalar(select(func.count()).select_from(TurnusRad)),
        "ansatt": session.scalar(select(func.count()).select_from(AnsattRad)),
        "vakt": session.scalar(select(func.count()).select_from(VaktRad)),
    }


def legg_til_turnusansvarlig(session: Session, passord: str, passord_kilde: str) -> None:
    """Legger til Kari Vestby med passordet som hash. Kjøres etter `fyll_testdata`."""
    session.add(
        BrukerRad(
            brukernavn=TURNUSANSVARLIG_BRUKERNAVN,
            navn=TURNUSANSVARLIG_NAVN,
            passord_hash=hash_passord(passord),
            passord_kilde=passord_kilde,
            turnus_id=TURNUS_ID,
        )
    )
    session.flush()


def velg_passord() -> tuple[str, str]:
    """Passordet og kilden: personlig fra miljøet, ellers et tilfeldig testpassord."""
    personlig = os.environ.get(PASSORD_VARIABEL) or None
    if personlig is not None:
        return personlig, "personlig"
    return secrets.token_urlsafe(9), "tilfeldig"


def main() -> None:
    passord, passord_kilde = velg_passord()
    engine = lag_engine()
    opprett_skjema(engine)
    with lag_sessionmaker(engine).begin() as session:
        radtall = fyll_testdata(session)
        legg_til_turnusansvarlig(session, passord, passord_kilde)
        brukere = session.scalar(select(func.count()).select_from(BrukerRad))
    print(f"Database: {database_sti()}")
    for tabell, antall in radtall.items():
        print(f"{tabell}: {antall}")
    print(f"  herav {len(PERIODE)} vakter i perioden og {len(HISTORIKK)} i historikken")
    print(f"bruker: {brukere}")
    print(f"Brukernavn: {TURNUSANSVARLIG_BRUKERNAVN}")
    if passord_kilde == "personlig":
        print(f"Passord: personlig, fra {PASSORD_VARIABEL}")
    else:
        print(f"Passord: tilfeldig testpassord, gjelder til neste kjøring: {passord}")


if __name__ == "__main__":
    main()
