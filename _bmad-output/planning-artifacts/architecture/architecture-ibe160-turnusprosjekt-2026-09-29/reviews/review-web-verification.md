---
name: 'Web Verification Review — Turnushjelperen Architecture Spine'
type: review
target: architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md
reviewed_against: architecture-ibe160-turnusprosjekt-2026-09-29/.memlog.md
date: 2026-09-29
---

# Web Verification Review

## Verdict

**Conditionally sound.** Three of the four pinned versions independently re-verified as accurate. One version claim (TypeScript) is stale/misleading. The Gemini free-tier figure cited as fact is more volatile and model-dependent than the memlog implies. No fabricated library or nonexistent version number found. Recommend correcting the TypeScript line and adding a caveat to the Gemini figure before treating the Stack table as final.

## Independently Re-Verified (via live web search, 2026-09-29)

| Claim | Status | Evidence |
| --- | --- | --- |
| FastAPI 0.141.1 | **Confirmed** | PyPI JSON API (`pypi.org/pypi/fastapi/json`) and GitHub releases both show 0.141.1 as latest, released 2026-07-29; no newer release since. Real version number, not a hallucination. |
| React 19.3.0 | **Confirmed** | Released 2026-09-09 per npm/GitHub; still latest as of today. |
| Vite 8.3.1 | **Confirmed** | Released 2026-09-24 per Vite's own release page; still latest. |
| SQLAlchemy compatibility (not version-pinned in spine) | **Consistent, correctly deferred** | SQLAlchemy 2.0.x is the current, Python 3.13/FastAPI-compatible line. Spine correctly leaves the exact version to Deferred rather than asserting a number — no contradiction found. |

## Findings

### 1. TypeScript "5.9+" is out of date (Medium severity)
The spine/memlog state "TypeScript 5.9+" as the recommended version for the React+Vite stack. Independent search shows the ecosystem has moved substantially since: **TypeScript 6.0 shipped March 2026**, and **TypeScript 7.0 — a full Go-based rewrite, ~8–10x faster — shipped around June 2026** and is now the current stable line, with 7.1 due autumn 2026. Citing "5.9+" understates current reality by two major versions. This wasn't caught by the memlog's own citation, meaning the TS claim likely wasn't actually checked against the web with the same rigor as FastAPI/React/Vite (those three checked out cleanly; this one didn't). Recommend the team re-check what `npm create vite@latest -- --template react-ts` actually pins today and update the Stack table accordingly, or explicitly note "5.9+" as a floor, not a current recommendation.

### 2. Gemini free-tier "1500 req/dag" is model-dependent and already partly stale (Medium severity)
The memlog states "1500 req/dag/15 req/min" as a confirmed fact. Current (2026-09-29) sources conflict: some report 1,500 RPD for "Gemini 3 Flash," but others report the **newer Flash models (3.5–3.8 Flash) now provide only ~20 free requests/day**, with Flash-Lite variants at ~500/day, and **Pro-tier models moved behind billing entirely since April 2026**. Google also no longer publishes fixed universal limits — quotas are viewable per-project in AI Studio and vary by model. Since the spine correctly defers the specific Gemini model choice (see Deferred section), the "1500/day" figure risks being read as a settled fact when it's actually contingent on which model gets picked later — and may not hold for whichever model the team ends up choosing. Recommend re-verifying the actual quota at the moment the team selects a specific Gemini model.

### 3. JWT + FastAPI + React: sound combination, but one security nuance not surfaced (Low severity)
No blocking issues found with this combination as an architecture choice — it remains standard and current. However, current best practice (2026) favors an in-memory access token + httpOnly-cookie refresh token over a bearer token stored in localStorage/persistent client storage, specifically to reduce XSS token-theft exposure. AD-3 correctly defers "nøyaktig token-innhold, utløpstid og fornyelsespolicy," but does not mention *where* `adaptere/web` stores the JWT client-side. Since this is already Deferred, it's not a spine defect, but worth flagging so the eventual decision considers httpOnly-cookie vs. localStorage explicitly rather than defaulting to the common-but-weaker localStorage pattern.

### 4. Design paradigm (Hexagonal / Ports & Adapters) — no issue
Well-established, still-current pattern; no version/currency risk applies here since it's not a versioned library claim.

## Spot-Check Method
Ran 7 independent web searches covering FastAPI's PyPI JSON metadata, GitHub release tags, React/Vite release notes, TypeScript release history and ecosystem-adoption status, Gemini API rate-limit documentation/analyses, SQLAlchemy/Python 3.13 compatibility, and current JWT-storage best practice for React SPAs — rather than relying on the memlog's citation alone.
