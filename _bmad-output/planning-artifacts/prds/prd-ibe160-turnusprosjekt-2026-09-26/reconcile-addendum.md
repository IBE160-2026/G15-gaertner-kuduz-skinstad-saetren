---
title: "Reconciliation: PRD vs. addendum"
created: 2026-09-26
---

# Reconciliation: prd.md vs. addendum.md

Scope of this check (per instructions): only material from the addendum that should inform product
requirements / scope / success criteria, but is missing, contradicted, or watered down in the PRD.
Market research, competitor tables, reflection-report argumentation (§1, §4, bias discussion) and
course grading percentages (§5) are intentionally out of scope for the PRD and are **not** flagged
below even though they are absent from it — that absence is correct, not a gap.

## Checked and confirmed correctly reflected (no gap)

- **Hard-rule set (addendum §2):** addendum recommends exactly four rules for v1 — 11-hour rule,
  35-hour rule, colliding shifts, competence minimum — explicitly rejecting the larger table (max
  daily/weekly hours, overtime limits, shift-work weekly hours) as "et lite, godt testet utvalg...
  fire regler som beviselig fungerer er verdt mer enn tolv som er halvveis." PRD §4.2 / FR-2–FR-5
  implement exactly these four, and the `[ASSUMPTION]` note in §4.2 explicitly names the larger
  rule table as excluded. Correctly and fully reflected.
- **Rejected alternative — shift-swapping as core feature (addendum §3):** PRD §5 Ikke-mål carries
  the addendum's own reasoning nearly verbatim ("et annet problem enn sykefravær (dobbel
  regelvalidering, ansatt som initiativtaker, forutsetter forhandlingsflyt)"). Correctly reflected.
- **Rejected alternative — AI performing rule-checking/ranking (addendum §3):** PRD §5 Ikke-mål and
  §4.5's framing ("KI... beregner aldri Harde regler, arbeidstid eller kostnad, og kan aldri
  overstyre Rangeringen") both carry this forward, including the "lovkrav og kostnad må være
  reproduserbare" rationale. Correctly reflected.
- Two of the five addendum §6 "gjenstående avklaringer" are reflected as explicit PRD Open Questions:
  faglærer-confirmation on AI-as-grading-criterion (PRD §8 item 1) and soft-factor weighting (PRD §8
  item 2, plus FR-9's Note). Cost-model detail level is also carried forward (PRD §8 item 3).

## Gaps found

### Gap 1 — "arbeidsdeling og frister" dropped from Open Questions (low)

- **Addendum passage (§6, last row, "Åpne avklaringer"):** "Gjenstående: verifisere med faglærer om
  KI i produktet er vurderingskrav; konkret utvalg av harde regler; myke faktorer og vekting;
  detaljnivå i kostnadsmodell; **arbeidsdeling og frister**."
- **What's missing:** Four of the five remaining items are picked up somewhere in the PRD (see
  above). "Arbeidsdeling og frister" (division of work among the group / deadlines) does not appear
  anywhere in the PRD — not in §8 Åpne spørsmål, not elsewhere. It is silently dropped rather than
  carried forward or explicitly deferred.
- **Severity:** Low. This is a group-process/project-management item rather than a product
  requirement, so its absence from a product PRD is defensible — but since the addendum explicitly
  listed it as a still-open item, its disappearance should at minimum be a deliberate, noted decision
  rather than a silent omission.

### Gap 2 — Technical-quality success criteria not carried into §7 (medium)

- **Addendum passage (§6, "Suksesskriterier" row):** "Kriteriene for teknisk kvalitet (kjører fra
  rent repo, tester per hard regel, lekkasjetest mot KI-laget, feilhåndtering ved modellfeil) **bør
  tas videre i PRD/spec**." This is an explicit instruction (not reflection-report material) that a
  technical-quality tier of success criteria should be carried into the PRD alongside the
  product-level ones.
- **What's missing/watered down:** PRD §7 Suksesskriterier only carries a product-level tier
  (SM-1…SM-8 + counter-metrics). Of the four named technical-quality criteria: "tester per hard
  regel" is covered (SM-1/SM-5), "lekkasjetest mot KI-laget" is covered (SM-2), but **"kjører fra
  rent repo"** (clean-checkout/build reproducibility) does not appear anywhere in the PRD, and
  **"feilhåndtering ved modellfeil"** is only a consequence buried in FR-11, not elevated to an
  explicit, testable success metric in §7 the way the addendum's other three items were.
- **Severity:** Medium. The addendum flags this row specifically as content that should move forward
  into the PRD (unlike the market/competitor/reflection material it lists alongside it), so its
  partial omission is a real, addressable gap rather than an intentional exclusion.

### Gap 3 — Hard-rule-set confirmation not consolidated into Open Questions (low)

- **Addendum passage (§6):** lists "konkret utvalg av harde regler" as one of five still-open
  clarifications.
- **What's watered down:** The PRD does address this, but only as an inline `[ASSUMPTION]` in §4.2
  ("Bekreft at dette utvalget er riktig, eller om et annet sett skal prioriteres.") rather than as an
  entry in the consolidated §8 Åpne spørsmål list, where the other four related open items from the
  same addendum row all ended up. A reader scanning §8 for what's still open would miss this one.
- **Severity:** Low. Substance is present; only the placement/consolidation is inconsistent, creating
  a risk that this open item gets overlooked when the group works through §8 to close things out.

## Summary

3 gaps found, all addendum-explicit "carry forward" items that are either dropped or under-surfaced:
open-question consolidation (arbeidsdeling/frister; hard-rule-set confirmation) and one real content
gap (clean-repo/error-handling technical success criteria not elevated into §7). No contradictions
found — where the PRD does address addendum content (hard-rule set, rejected alternatives), it does
so faithfully.
