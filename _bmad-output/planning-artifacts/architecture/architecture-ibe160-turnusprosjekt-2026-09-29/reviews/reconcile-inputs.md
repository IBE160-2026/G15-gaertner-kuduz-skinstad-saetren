---
title: "Reconciliation Review — ARCHITECTURE-SPINE vs PRD & EXPERIENCE.md"
target: architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md
inputs:
  - prds/prd-ibe160-turnusprosjekt-2026-09-26/prd.md
  - ux-designs/ux-ibe160-turnusprosjekt-2026-09-26/EXPERIENCE.md
created: 2026-09-29
---

# Reconciliation Review

Method: read all three documents in full; checked the spine's AD-1..AD-5, Capability→Architecture Map, and Deferred list against PRD §1 (Visjon), §5 (Ikke-mål), §7 (Suksesskriterier), and EXPERIENCE.md's Voice and Tone, State Patterns, and Interaction Primitives sections, looking for prose-only requirements that the AD/table structure could have silently dropped.

## Finding 1 — SEVERITY: HIGH
**"Tolker" (interpret, feeds ranking) and "forklarer" (explain) are two distinct KI responsibilities in the PRD; the spine's port design only wires up one of them.**

PRD §1 states the KI layer does two things: "KI tolker de tekstbaserte preferansene **og** forklarer avveiningene" — interpretation and explanation are separate verbs. §3 confirms Ansattpreferanse is one of the **Myke faktorer that Rangering (§4.4) sorts by**, alongside kostnad, arbeidsbelastning and kompetansenærhet. FR-10 is explicit that "Tolkede preferanser sendes som strukturert input til Rangeringen (§4.4)" — i.e. interpreted preference must feed the ranking computation itself, not just the narrative.

The spine's AD-1 port (`RangertKandidat`) already carries `rangeringsplass` (the candidate's finished rank position) **and** the raw, uninterpreted Ansattpreferanse text, handed to `adaptere/ki` only for it "to interpret it" at that point ("for at KI skal tolke den"). The Structural Seed mermaid diagram shows a single one-directional arrow `Core -. RangertKandidat .-> KI`, with no port or data path in the other direction (interpreted-preference → `domene/regelmotor`, pre-ranking). As written, the architecture only supports KI interpreting preferences **after** ranking is already computed — which can only feed the Avveining narrative, not the rank order. That contradicts FR-10 and the §3 Myk faktor definition, and quietly narrows §1's two-verb framing down to one.

This is not caught by the Capability→Architecture Map (§4.4 row cites only AD-1/AD-2; §4.5 row cites AD-1 + config) because the map represents "lives in," not data flow, so the missing return path is invisible at that altitude. Note PRD's own SM-7 only tests preference use "i forklaringen," so the PRD's success-criteria table doesn't force this to surface either — it's a genuinely quiet drop, present in prose (§1, §3, FR-10) but never promoted to a binding rule.

**Recommendation:** Add an AD (or amend AD-1) establishing a second, pre-ranking data path: `adaptere/api` calls `adaptere/ki` to interpret raw Ansattpreferanse text into a structured value *before* invoking `domene/regelmotor`, which then takes that structured preference as one of its ranking inputs. This keeps `domene/regelmotor` free of any import on `adaptere/ki` (AD-1's static-import rule is preserved — it's a data dependency composed in `adaptere/api`, not a code dependency), but it needs to be stated, because right now the diagrams and the RangertKandidat field list actively suggest the opposite sequencing.

## Finding 2 — SEVERITY: MEDIUM
**AD-4's error envelope doesn't bind whether `melding` is shown to the user verbatim, risking a bypass of the Voice and Tone contract.**

EXPERIENCE.md § Voice and Tone establishes a hard principle: "systemet beskriver tilstand og begrunner tall — det formaner aldri og feirer aldri," with a Do/Don't table showing curated, specific Norwegian copy for every state (e.g. "Mangler bemanning" not "FEIL: ingen bemanning!"). AD-4 defines the technical error envelope as `{ "kode": string, "melding": string }` and calls `melding` a "menneskelesbar melding" (human-readable message) — wording that implies it is meant to be surfaced directly. Nothing in the spine states that `adaptere/web` must map `kode` to its own curated copy rather than rendering backend `melding` text as-is. If a future contributor treats `melding` as display-ready (a reasonable reading of "menneskelesbar"), raw exception/validation text (e.g. a framework-default message) could leak into the UI and violate the tone contract this document treats as load-bearing. The two special domain states (`ingen_gyldige_kandidater`, `avveining_feilet`) are correctly modeled as 200-status discriminators specifically to keep them distinct from errors and support the tone principle — so the spine clearly cares about this concern in one place but doesn't close the same gap for genuine HTTP-error `melding` text.

**Recommendation:** Either state explicitly that `adaptere/web` never renders `melding` directly (it maps `kode` → curated copy, `melding` is a dev/log-only fallback), or state that `melding` itself is written by `adaptere/api` to already comply with Voice and Tone. This is already partly flagged by the existing Deferred item "Feilenvelope-detaljer," but that item covers the *schema*, not this specific display-contract question — worth folding in explicitly.

## Checked, no gap found
- PRD §5 Ikke-mål: reviewed each excluded item (full turnus-generering, KI som beregner harde regler/kostnad/rangering, vaktbytte, full AML-etterlevelse, full lønnskostnad, ekte persondata, flere samtidige endringer, auto-gjennomføring uten Godkjenning, ansattportal/avansert auth/generell KI-chat) against the spine's Design Paradigm table, ERD, and source tree — none is structurally implied or enabled by the spine.
- EXPERIENCE.md § Interaction Primitives "bevisst utelatt: SMS-/varslingsutsendelse" — no notification adapter, queue, email/SMS integration, or port appears anywhere in the spine (Design Paradigm table, Stack, Structural Seed). Clean.
- EXPERIENCE.md § State Patterns — walked every row (Innlogging feilet, Beregner rangering, Ingen gyldige kandidater, Krever handling / ingen krever handling, Avvik fra anbefalt rangering, Godkjenning ikke gjennomført, Avveining feilet/tom/ubrukelig, Ikke innlogget/utløpt sesjon, Vellykket godkjenning) against AD-3/AD-4/AD-5 and the RangertKandidat/UtelukkelsesOppsummering ports. All are structurally supported except the progressive-loading transport for "Beregner rangering," which the spine already lists in Deferred (acknowledged, not silently dropped).
- PRD §7 Suksesskriterier — SM-1, SM-2 (spine literally cites SM-2 in AD-1's Prevents clause and adds a runtime invariant test beyond static import-linting for it), SM-3, SM-5 (spine's Europe/Oslo timezone rule explicitly cites SM-1/SM-5), SM-6, SM-8, SM-9 all have a clear structural home. SM-4 and SM-7 are achievable for the explanation path but SM-7's narrower framing ("i forklaringen") is what let Finding 1 stay hidden — see above.
