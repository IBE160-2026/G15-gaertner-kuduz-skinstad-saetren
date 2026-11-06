# G15 — Prompt Patrol

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Medlemmer

- Johannes W Gaertner
- Mithad Kuduz
- Kim O Skinstad
- Ragnhild Sætren

## Planleggingsgrunnlag

- [Product brief](product-brief.md) – eneste gjeldende brief for prosjektet.
- [PRD](_bmad-output/planning-artifacts/prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md) – krav til
  funksjonalitet, harde regler og rangering.
- UX: [DESIGN](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/DESIGN.md)
  beskriver hvordan appen ser ut, og
  [EXPERIENCE](_bmad-output/planning-artifacts/ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md)
  hvordan den oppfører seg.
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md)
  – tekniske beslutninger (AD-1 og videre) som holder delene konsistente.
- [Epics og stories](_bmad-output/planning-artifacts/epics.md) – oppdelingen av arbeidet. Fremdriften
  står i [sprintstatus](_bmad-output/implementation-artifacts/sprint-status.yaml).
- [Beslutningsreferat](docs/beslutninger/avklaringspunkter.md) – gruppevedtak (AV-, K-, OP- og KS-punkter)
  fra møtet 2026-11-02 og senere oppdateringer.

## Modelltest før KI-integrasjonen

Gruppa har valgt `openai/gpt-6-luna` via OpenRouter etter disse testene:

- [Haiku 5.5 alene](docs/ki-logg/2026-10-15-modelltest-haiku.md) og
  [sammenligning med Luna, Mistral og Gemma](docs/ki-logg/2026-10-15-modellsammenligning.md), 15. oktober.
- [Forhåndsregistrert beslutningstest Haiku mot Luna](docs/ki-logg/2026-10-16-beslutningstest-haiku-luna.md)
  og [robusthetstest av Luna](docs/ki-logg/2026-10-16-robusthet-luna.md), 16. oktober.

[Testveiledningen](docs/modelltest-openrouter.md) beskriver de isolerte Python-testene.

## Kjøre appen

Appen er foreløpig et skjelett: en backend med helsesjekk og testdata og en tom frontend.
Du trenger Python 3.12 eller nyere og Node 20.19 eller nyere. Backend og testene er
kjørt med Python 3.12.5 og 3.15.2 på Windows (2026-11-04). Kommandoene under er
for Windows. På macOS/Linux bytter du `.venv\Scripts\python` med `.venv/bin/python`.

På Windows er en filsti begrenset til 260 tegn, med mindre lange stier er slått på. Den
lengste filen i repoet har en sti på 125 tegn, så stien du kloner til, bør være kortere
enn ca. 130 tegn. Ellers kan checkout feile med «Filename too long», og `python -m venv`
kan feile i `ensurepip`. Det gjelder også git-worktrees, for eksempel når agenter
jobber i en egen kopi. `git config --global core.longpaths true` løser det for git. For
Python må lange stier slås på i Windows, og det krever administratorrettigheter.

Backend, fra mappa `backend/`:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m uvicorn adaptere.api.main:app --reload
```

Helsesjekken svarer på http://127.0.0.1:8000/api/helse. Testene kjøres med
`.venv\Scripts\python -m pytest`.

Fiktive testdata (Kirurgisk sengepost, uke 39–40 2026, 25 ansatte) legges inn med
`.venv\Scripts\python -m adaptere.lagring.testdata`, også fra `backend/`. Kommandoen
tømmer og fyller tabellene på nytt og kan kjøres flere ganger. Databasen havner i
`backend/turnushjelperen.db`, med mindre miljøvariabelen `TURNUSHJELPEREN_DB` peker et
annet sted. Slett filen hvis skjemaet er endret.

Frontend, fra mappa `frontend/` i en egen terminal:

```
npm install
npm run dev
```

Åpne http://localhost:5173.

## Vurderingsgrunnlag

- [Sensorveiledning del 1](docs/emne/sensorveiledning-del-1.md) – tekstgjengivelse med sidereferanser og lenke til original PDF.
- [Vurderingsmatrise](docs/emne/vurderingsmatrise.md) – tiltak, dokumenterte bevis og arbeid som gjenstår.
