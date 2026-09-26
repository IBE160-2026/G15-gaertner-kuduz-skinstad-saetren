# PRD Quality Review — PRD: Turnushjelperen (prd-ibe160-turnusprosjekt-2026-09-26)

## Overall verdict

This PRD is unusually disciplined for the stakes involved: it has a real thesis (deterministic rules own hard compliance, AI owns explanation, human owns approval), features and success metrics that trace back to that thesis, and non-goals that are argued rather than just listed. The main risks are structural, not rhetorical: §0 promises an assumptions index in "§9" that does not exist anywhere in the document, and two load-bearing FRs (FR-9's soft-factor weighting, FR-7's cost-rate detail) are left genuinely unresolved — honestly flagged in §8, but still meaning an engineer cannot fully implement ranking or costing from this PRD alone. Everything else — glossary discipline, ID continuity, testable FR consequences — holds up well for a 4-person exam-project PRD.

## Decision-readiness — strong

Trade-offs are named with what was given up, not smoothed over. §4.2 states outright that daily/weekly max-hours rules and overtime limits are excluded from v1 because "addendum anbefaler et lite bevist utvalg fremfor et stort halvveis" — a real scope trade, not a soft "we prioritized." §5's non-goals each carry a rejected-alternative rationale (e.g., shift-swap "vurdert og forkastet... det er et annet problem enn sykefravær," AI-does-ranking "vurdert og forkastet... loven krever determinisme"), cross-checked against `addendum.md` §3 and confirmed accurate.

§8's four open questions are genuinely open — item 2 (soft-factor weighting) and item 3 (cost-model detail) have no answer buried in the next sentence, and item 1 (whether AI-in-product is a grading requirement) carries real stakes for scope and is tagged with urgency ("Bør avklares før proposal leveres"). The two `[NOTE FOR PM]` callouts (§4.4, §5) sit at genuine unresolved tensions (ranking weights; ansattportal as stretch goal) rather than at safe checkpoints.

### Findings
None — no findings needed at this rigor level.

## Substance over theater — strong

Only one persona (Kari) and one UJ, matched to the single-operator shape — no persona padding. The Vision (§1) is specific to this product's actual mechanism ("harde regler... filtrerer... en enkel og reproduserbar modell rangerer... KI tolker... forklarer") and could not swap into an unrelated PRD unchanged. Feature-specific NFRs are genuinely testable invariants ("En Kandidat utelukket av en Hard regel skal aldri kunne opptre i Rangeringen... eller nevnes av KI-forklaringen") rather than "must be scalable/secure" boilerplate — this is the opposite of NFR theater.

### Findings
None.

## Strategic coherence — strong

The thesis (rules own determinism, AI owns explanation, human owns the final call) is stated in §1 and never contradicted downstream. Feature order (§4.1→§4.6) follows the thesis, not ease-of-build. Success metrics validate the thesis rather than measuring activity: SM-2 ("En Kandidat utelukket av en Hard regel blir aldri anbefalt av KI") tests the rules/AI boundary directly; SM-6 ("den billigste Kandidaten ikke nødvendigvis rangeres høyest") tests that ranking isn't cost-only. Counter-metrics SM-C1 and SM-C2 are present and specifically guard against gaming the primary metrics (rule-count inflation without test coverage; response-speed over correctness) — exactly what the rubric asks for and often missing.

### Findings
None.

## Done-ness clarity — adequate

Most FRs carry concrete, testable consequences with quantified thresholds ("100 % av Kandidatene med Kompetansenivå under minstekravet filtreres bort i definerte testscenarioer," reproducibility conditions on FR-4, FR-7, FR-9). This is the PRD's strongest dimension mechanically.

However, two structurally central FRs are not actually buildable as written:

### Findings
- **medium** FR-9 ranking has no resolved weighting (§4.4, FR-9) — The FR's consequences describe ordinal properties (cheapest candidate not always top, competence-nearness wins when no candidate is fully qualified) but the actual weighting formula is explicitly unresolved: "Den konkrete vektingen mellom kostnad, arbeidsbelastning, preferanser og kompetansenærhet er ikke fullt bestemt" (`[NOTE FOR PM]`, §4.4) and repeated as Open Question #2 (§8). An engineer cannot implement the ranking algorithm from this PRD alone. *Fix:* resolve the weighting (even a simple ordered tie-break scheme) before architecture/epics, or explicitly hand it to architecture as a designed-there decision.
- **medium** FR-7 cost model detail undetermined (§4.3, FR-7) — "Konkret detaljnivå i kostnadsmodellen... nøyaktig hvilke satser og betingelser som skiller ordinær kostnad fra overtidskostnad" is listed as Open Question #3. Same shape as above: honestly flagged, but "done" for FR-7 isn't yet defined. *Fix:* pin down at minimum a threshold rule (e.g., hours-per-week trigger) before implementation starts.
- **low** Un-bounded adjectives in two FR consequences (FR-6, FR-11) — FR-6 requires the system to "tydelig informere" and the interface to "skille synlig" between no-valid-candidates and a loading/error state; FR-11 requires "en tydelig feilmelding" on LLM failure. "Tydelig"/"synlig" (clearly/visibly) are adjectives without a bound, though each is paired with a concrete behavioral requirement (distinct states; never a groundless recommendation; never crash), which limits the risk. *Fix:* if UX spec doesn't already pin this down, add one sentence per FR naming the distinguishing UI signal.

## Scope honesty — adequate

§5 Non-Goals is unusually strong: every exclusion carries a reasoned rationale rather than a bare list, and two items are traced to specific addendum decisions (verified accurate against `addendum.md` §3). `[NOTE FOR PM]` callouts land on real deferred decisions. Three inline `[ASSUMPTION]` tags exist (§2.3 edge-case presentation, §2.3 Kari persona fictionality, §4.2 rule-set scope) and each is a genuine inference, not a rubber-stamp.

### Findings
- **high** Assumptions Index promised but absent (§0 vs. document structure) — §0 states "antakelser er merket `[ASSUMPTION]` inline og samlet i §9," but the document has no §9; it ends at §8 Åpne spørsmål. The three inline `[ASSUMPTION]` tags (lines with Kari's persona, the "ingen gyldige kandidater" edge case, and the v1 hard-rule subset) are consequently un-indexed — a reader cannot audit the full assumption set from one place, contradicting the document's own stated structure. *Fix:* add §9 with all three assumptions, or correct §0's cross-reference if the index was intentionally dropped.

## Downstream usability — strong

Glossary (§3) is thorough and terms are used with consistent capitalization throughout the FRs (Kandidat, Gyldig kandidat, Hard regel, Myk faktor, Rangering, Godkjenning all track their definitions). FR IDs (FR-1–FR-13) and SM IDs (SM-1–SM-8, SM-C1–SM-C2) are contiguous with no gaps or duplicates. Cross-references resolve correctly — "Validerer FR-2 til FR-5," "Validerer FR-9, FR-11" etc. all point to FRs that exist and match the claimed content. UJ-1 has a named protagonist (Kari) carrying context through entry state, path, climax, resolution, and edge case.

### Findings
- **low** One dangling cross-reference (§0 → non-existent §9) — same defect as the Scope Honesty finding above; flagged here because it's also a downstream-traceability break, not just a scope-honesty one.

## Shape fit — strong

Correctly shaped as a capability spec for a single-operator internal tool: one persona, one UJ, no forced multi-stakeholder framing despite the product touching ~25 fictional employees (who are explicitly non-users, §2.2). Success metrics are operational/product-behavior metrics (SM-1–SM-8), not vanity engagement metrics, appropriate for a decision-support tool with one user role. Rigor is calibrated to a graded exam project — testable consequences and invariants are present without being over-engineered with enterprise-grade NFR sections the product doesn't need.

### Findings
None.

## Mechanical notes

- **Glossary drift:** none found — domain nouns (Turnus, Vakt, Kandidat, Gyldig kandidat, Hard regel, Myk faktor, Ansattpreferanse, Rangering, Avveining, Godkjenning) are capitalized and used identically across sections.
- **ID continuity:** FR-1 through FR-13 contiguous, no gaps/duplicates. SM-1–SM-8 plus SM-C1/SM-C2 contiguous. UJ-1 is the only UJ, consistent with a single-operator product.
- **Assumptions Index roundtrip — broken:** §0 claims assumptions are "samlet i §9"; no §9 exists in the document (it ends at §8). The three inline `[ASSUMPTION]` tags (§2.3 ×2, §4.2 ×1) are not indexed anywhere. See Scope Honesty finding above for the fix.
- **UJ protagonist naming:** UJ-1's protagonist Kari is named and carries context (department size, situation) inline — meets the bar.
- **Addendum traceability:** all addendum cross-references checked against `brief-ibe160-turnushjelperen-2026-09-08/addendum.md` (§2 rule thresholds, §3 rejected alternatives, §5 course-requirement interpretation) and found accurate. One item from addendum §6 ("kjører fra rent repo" as a technical-quality criterion) was not carried into the PRD's success criteria — likely intentional (belongs to architecture/CI rather than product requirements), but worth a conscious check before sprint planning.
