---
title: "Reconciliation: prd.md vs product-brief.md"
created: 2026-09-26
---

# Reconciliation: PRD vs. Product Brief

**Inputs:**
- Derived doc: `prd.md` (PRD: Turnushjelperen, IBE160 Turnusprosjekt)
- Source: `product-brief.md` (Product Brief: IBE160 Turnusprosjekt)

## Method

Every substantive claim, requirement, scope boundary, and success criterion in `product-brief.md` was extracted and traced to its counterpart in `prd.md`. Additions the PRD makes beyond the brief (e.g., the four named hard rules, competence-closeness as a soft factor, JTBD framing, glossary, open questions) are expected elaboration and are not flagged.

## Overall finding

The PRD is a faithful and thorough derivation of the brief. Every item in the brief's Problemet, Løsningen, Suksesskriterier, and Omfang (both in-scope and out-of-scope) sections is represented in the PRD, generally 1:1 and often made more specific/testable (e.g., the brief's generic "arbeidstids-/hviletidsregler" becomes the concrete 11-hour and 35-hour rules; the brief's 10 success criteria map cleanly onto SM-1–SM-8). No contradictions were found. Two lower-severity gaps were identified, both concerning the brief's forward-looking/positioning content rather than its functional requirements.

## Gaps

### 1. Long-term vision (2–3 year roadmap) is not represented anywhere in the PRD

- **Severity:** Medium
- **Brief passage (§ Visjon):** "Dersom konseptet lykkes, kan løsningen i løpet av 2–3 år utvikles fra en prototype for enkeltstående turnusendringer til et bredere beslutningsstøttesystem for bemanningsplanlegging. En videreutviklet løsning kan håndtere større turnusplaner, flere samtidige endringer og et mer omfattende regelverk. Den kan integreres med eksisterende HR-, lønns- og turnussystemer og benytte faktiske kostnadsdata. Ansatte kan få egne brukerkontoer og bruke en KI-assistent til spørsmål som: «Hvem kan jeg bytte vakt med på tirsdag?», «Hvilke ledige vakter kan jeg ta?», «Hvor mye overtid har jeg denne måneden?» Turnusansvarlige kan samtidig få mer avansert analyse, scenarioevaluering og støtte ved større bemanningsendringer."
- **What's missing in the PRD:** The PRD has no future-vision/roadmap section. §5's "[NOTE FOR PM]" and §2.2 mention that an employee portal and more advanced auth/AI are stretch goals, but this only covers a fragment of the brief's vision (employee accounts). It omits the specific future capabilities the brief lists: handling larger turnus plans, multiple simultaneous changes, broader rule coverage, integration with real HR/payroll/turnus systems, use of actual cost data, the illustrative AI-assistant employee queries, and advanced scenario evaluation/analysis for turnusansvarlige. Since this content could inform architecture decisions about extensibility, its complete absence from the PRD (even as a brief "future considerations" pointer) is a genuine gap rather than expected PRD elaboration.
- **Note:** The PRD states it "bygger videre på product-brief.md og dens addendum.md," so this content may be intentionally deferred to the addendum — but that file was outside the scope of this comparison, and nothing in prd.md itself signals where this vision content lives.

### 2. The brief's explicit differentiation narrative ("hva gjør dette annerledes") is not carried into the PRD

- **Severity:** Low
- **Brief passage (§ Hva gjør dette annerledes):** "En enkel digital turnusløsning kan vise hvem som er ledig. En regelbasert løsning kan i tillegg filtrere bort ansatte som ikke oppfyller bestemte krav. Prosjektet går ett steg videre ved også å hjelpe brukeren med å sammenligne de gyldige kandidatene og forstå konsekvensene av valget. Løsningens særpreg ligger derfor ikke i en unik teknologi, men i kombinasjonen av: kontrollerbare regler + enkel kostnadsberegning + ansattpreferanser + forklarbar KI-støtte + menneskelig sluttbeslutning."
- **What's missing in the PRD:** PRD §1 (Visjon) restates the mechanism (rules filter, model ranks, AI explains, human decides) but never frames it comparatively against simpler alternatives (a plain availability-only tool, or a rules-only tool) or names the five-part combination as the product's specific differentiator. This is positioning/rationale rather than a functional requirement, so its omission does not affect buildability, but it is a substantive claim from the brief that a reader of the PRD alone would not learn.

## No contradictions found

No requirement, scope boundary, or success criterion in the brief is contradicted or watered down in the PRD. Notably:
- All "in scope" bullets (hard rules, soft-factor comparison, simplified cost model, preferences, AI interpretation/explanation, ranked list with justification, mandatory human approval, simple login) are present, each with a corresponding FR.
- All "out of scope" bullets (no full turnus generation/optimization, no legal-compliance guarantee, no full tariff/payroll rules, no full wage cost, no real personal data, no real system integration, no multi-change handling, no autonomous AI execution, no full employee portal/advanced auth, no general AI chat) are present in §5 and §6.2.
- All 10 success-criteria statements in the brief map onto SM-1 through SM-8 without loss of substance (several brief bullets are consolidated into one SM, which is normal PRD compression, not a gap).
