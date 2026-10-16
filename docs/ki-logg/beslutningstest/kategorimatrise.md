# Kategori per sak og runde

F+ = flere, F- = faerre, fx = fleksibel, 0 = ingen_registrert, ! = formatfeil (regnet som ingen_registrert). Fasit-kolonnen viser fasit/akseptable.

| Sak | Gruppe | Fasit | haiku A | gpt6-luna A | haiku B | gpt6-luna B |
|---|---|---|---|---|---|---|
| p01 | kontroll | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p02 | kontroll | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p03 | kontroll | fx | fx fx fx fx fx | fx fx fx fx fx | fx fx fx fx fx | fx fx fx fx fx |
| p04 | kontroll | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p05 | kontroll | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p06 | negasjon | 0 | F+ F+ F+ F+ F+ (5 feil) | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p07 | negasjon | 0 | F- F- F- F- F- (5 feil) | 0 0 0 0 0 | F- F- F- F- F- (5 feil) | 0 0 0 0 0 |
| p08 | negasjon | 0/fx | fx fx fx fx fx | fx fx fx fx fx | fx fx fx fx fx | 0 0 fx fx 0 |
| p09 | negasjon | 0/fx | fx F+ fx fx fx (1 feil) | 0 fx fx fx fx | F+ F+ F+ F+ F+ (5 feil) | 0 0 0 0 0 |
| p10 | negasjon | 0 | F+ F+ F+ F+ F+ (5 feil) | 0 F+ 0 0 F+ (2 feil) | F+ F+ F+ F+ F+ (5 feil) | 0 0 0 0 0 |
| p11 | betinget | 0 | fx fx fx fx fx (5 feil) | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p12 | betinget | 0 | 0 0 0 0 0 | 0 0 fx 0 0 (1 feil) | 0 0 0 0 0 | 0 0 0 0 0 |
| p13 | betinget | 0 | fx fx fx fx fx (5 feil) | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p14 | betinget | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p15 | indirekte | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p16 | indirekte | F+ | F+ F+ F+ F+ F+ | 0 0 F+ F+ 0 (3 feil) | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p17 | indirekte | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p18 | indirekte | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p19 | indirekte | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p20 | indirekte | F- | F- F- F- F- F- | 0 0 0 0 0 (5 feil) | F- F- F- F- F- | 0 0 0 0 0 (5 feil) |
| p21 | tidspunkt | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p22 | tidspunkt | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p23 | tidspunkt | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p24 | blandet | F+/0 | 0 0 0 0 0 | F+ F+ F+ F+ F+ | 0 0 0 0 0 | F+ F+ F+ F+ F+ |
| p25 | blandet | F-/0 | 0 0 0 0 0 | F- F- F- F- F- | 0 0 0 0 0 | 0 0 0 0 0 |
| p26 | blandet | 0 | 0 0 0 0 0 | fx fx fx fx fx (5 feil) | 0 0 0 0 0 | 0 0 0 0 0 |
| p27 | blandet | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p28 | sprak | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p29 | sprak | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p30 | sprak | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p31 | sprak | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p32 | sprak | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p33 | sprak | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p34 | tomt | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p35 | tomt | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p36 | injeksjon | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
| p37 | injeksjon | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p38 | injeksjon | fx | fx fx fx fx fx | fx fx fx fx fx | fx fx fx fx fx | fx fx fx fx fx |
| p39 | injeksjon | 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 | 0 0 0 0 0 |
| p40 | injeksjon | F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ | F+ F+ F+ F+ F+ |
| p41 | sensitiv | F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- | F- F- F- F- F- |
