---
title: "Review: ARCHITECTURE-SPINE.md (rubric — good-spine checklist)"
target: ../ARCHITECTURE-SPINE.md
reviewer: architecture-review (checklist pass)
created: 2026-09-29
---

# Gate Verdict

**PASS with conditions** — the spine fixes the one truly critical divergence point (the KI/domain boundary, mechanically enforced) and traces every FR, but two of its Deferred items sit on a live cross-adapter contract seam (API↔web error envelope; JWT renewal) rather than inside a single owned module, and the operational envelope is silent on one concrete, already-known constraint (Gemini API rate limits) — these should be tightened before epics/stories are cut, not treated as pure implementation detail.

---

## Findings

### HIGH

**H-1. Error envelope's exact schema is Deferred, but it is a cross-adapter contract, not an internal detail.**
- **Location:** AD-4 (lines 65–69) and Deferred (line 172): "Feilenvelope-skjema (AD-4) — at det finnes én form er besluttet; eksakte feltnavn er ikke."
- **Why it matters:** `adaptere/api` and `adaptere/web` are two separately buildable driving/driven-facing units per the hexagonal split. Unlike the cost-model or soft-factor-weighting deferrals (which stay entirely inside `domene/regelmotor`, a single module/story), an unresolved field schema for the *only* error contract between backend and frontend is exactly the kind of thing that lets two independently-built units diverge incompatibly (one team implements `{code, message}`, the other expects `{error_code, detail}`). This is also the contract EXPERIENCE.md leans on to distinguish real errors from "no valid candidates" (FR-6) — a soft requirement with real behavioral stakes.
- **Suggested fix:** Pull the field names into AD-4's Rule now (even a minimal `{ "error_code": str, "message": str }` shape), or explicitly gate "no `adaptere/web` error-handling story starts before this is fixed" in the Deferred entry.

### MEDIUM

**M-1. JWT renewal policy deferred, but it is also a two-adapter behavioral contract.**
- **Location:** AD-3 (lines 59–63) and Deferred (line 170): "kun at JWT er representasjonsformen er besluttet."
- **Why it matters:** Whether the token silently renews, forces re-login, or has no renewal at all changes what `adaptere/web` must build (an interceptor/refresh flow vs. a bare 401→redirect). If web is built assuming silent refresh and api never implements it, sessions will behave inconsistently — a genuine cross-unit divergence, not just a missing constant like the exact TTL value.
- **Suggested fix:** AD-3's Rule should at minimum state the renewal *strategy* (e.g., "no silent renewal in v1; expired token → 401 → re-login"), leaving only the TTL number itself in Deferred.

**M-2. Gemini API operational resilience is unaddressed anywhere in the spine.**
- **Location:** `.memlog.md` line 13 records "1500 req/dag/15 req/min" as the reason Gemini was chosen; the spine's Stack table (line 95) and Deferred (line 169) only note the model version is unpinned — no AD, Consistency Convention, or Deferred entry covers retry/backoff/rate-limit handling in `adaptere/ki`.
- **Why it matters:** This is the operational/environmental envelope the checklist calls out explicitly. A concrete, already-known external constraint (15 req/min) is exactly the sort of thing that should at least be named as an open question, since two builders could independently choose incompatible failure-handling behavior in `adaptere/ki` (silent retry vs. immediate fallback text) that changes what FR-11's "Avveining feilet" fallback actually triggers on.
- **Suggested fix:** Add one line to Deferred (or fold into AD-1's `adaptere/ki` scope) naming rate-limit/retry handling as an open question.

**M-3. AD-2's enforcement is weaker than AD-1's — stated as a rule, not mechanized.**
- **Location:** AD-2 (lines 43–47) vs. AD-1 (line 41, which names a concrete import-linter/test mechanism).
- **Why it matters:** The checklist requires every AD's Rule be *enforceable*, not just stated. AD-1 sets the bar (a test that fails if `domene/regelmotor` imports `adaptere/ki`); AD-2 generalizes the same "adapters depend on domene/*, never reverse" principle to `adaptere/api` and `adaptere/lagring` but gives no equivalent mechanical check — only the Testing convention row references the AD-1-specific test. A reverse dependency from `adaptere/lagring` or `adaptere/api` into domain internals could creep in undetected.
- **Suggested fix:** Extend the Testing convention (or AD-2's own Rule) to require the same import-linter check for all adapters, not only `adaptere/ki`.

### LOW

**L-1. Stack table version numbers are asserted "verified" but unusually high — worth a spot-check.**
- **Location:** Stack table (lines 88–96): FastAPI 0.141.1, Vite 8.3.1.
- **Why it matters:** SM-9 ("bygges og kjøres fra et rent klonet repo, uten manuelle unntak") depends on these pins being real, installable versions. FastAPI has historically stayed in the 0.1xx range for years at a much lower minor number, and Vite reaching major version 8 implies an accelerated release cadence; neither is impossible by 2026-09-29 but both are far enough from expected trajectories to warrant a second look before anyone runs `pip install fastapi==0.141.1`.
- **Suggested fix:** Re-run the version check (or have a team member confirm from PyPI/npm directly) before scaffolding.

---

## Checklist Items That Passed Cleanly

- **Divergence points for the level below:** the one PRD-critical, testable invariant (SM-2: KI can never see/override an excluded candidate) is fixed by AD-1 with a genuinely mechanical enforcement (import test), not just a stated convention.
- **PRD coverage:** every FR (FR-1 through FR-13) is traceable in the Capability → Architecture Map; no orphaned capability found.
- **Deferred items that are correctly internal-only (no divergence risk):** soft-factor weighting and cost-model detail live entirely inside `domene/regelmotor`, a single-owner module — deferring them doesn't let two independently-built units diverge, since only one unit implements the rule.
- **Deployment/hosting dimension:** not silent — explicitly decided as "local-only for v1" with hosting itself correctly placed in Deferred (Render mentioned as a non-committed option).
