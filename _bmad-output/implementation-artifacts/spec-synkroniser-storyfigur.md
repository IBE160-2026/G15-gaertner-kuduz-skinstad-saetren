---
title: 'Synkroniser storyfigur med sprintstatus'
type: 'chore'
created: '2026-11-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Figuren kan vise foreldet status når sprintstatus endres, og farge og tekst kan motsi hverandre.

**Approach:** Lag et skript som oppdaterer figurens status fra sprintstatus og en CI-kontroll som varsler når de ikke stemmer. Dokumenter hvordan skriptet kjøres, og bevar beskrivende avhengighetstekster.

</frozen-after-approval>

## Implementation Notes

- `scripts/synkroniser_storyfigur.py` leser bare `development_status`, kontrollerer entydig mapping og oppdaterer status uten å overskrive avhengighetsnotater. CI kjører tester og kontrollmodus; README beskriver kommandoen.
- Figuren har fått korrekte statustekster, 30 stories i beskrivelsen og ingen foreldet statusdato. Automatiske tester og `--sjekk` bestod.

## Review Triage Log

- Medium, rettet: en status med ekstra ord kunne bli godtatt; hele verdien valideres nå.
- Medium, rettet: tom duplikatlinje kunne bli oversett; storylinjer må nå ha gyldig format og unike ID-er.
- Medium, rettet: en ekstra `development_status` kunne bli oversett; nøyaktig én kreves.
- Medium, rettet: kommandolinjens kontroll- og skrivemodus manglet samlet test; begge er nå testet med midlertidige filer.
