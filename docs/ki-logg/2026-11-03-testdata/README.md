# Kladdeskript for testdataene i story 1.2

Dokumentasjon av hvordan radene i `backend/adaptere/lagring/testdata.py` ble
skrevet. Skriptene kjøres ikke av appen eller testene, og de er ikke vedlikeholdt.
Se [KI-loggen](../2026-11-03-testdata.md).

- `data4.py`: siste versjon av turnusen, skrevet for hånd som ett ukemønster per
  ansatt og uke (35–40), for eksempel `"-MMKK--"`.
- `design.py`: sjekker et mønster mot de fire harde reglene for #4127 og #4189,
  reglene i hver ansatts egen turnus, Ulempepoeng i vinduet til #4127 og bemanning
  per døgn. Fra denne mappa: `python design.py data4.py`.
- `emit.py`: skriver mønstrene i `data4.py` ut som rader med vaktnummer
  (`historikk.txt` og `periode.txt`), som så ble limt inn i `testdata.py`.

Tidligere versjoner (`data1.py`–`data3.py`) og et lite hjelpeskript som byttet ut
enkeltuker mellom versjonene, er ikke tatt med.
