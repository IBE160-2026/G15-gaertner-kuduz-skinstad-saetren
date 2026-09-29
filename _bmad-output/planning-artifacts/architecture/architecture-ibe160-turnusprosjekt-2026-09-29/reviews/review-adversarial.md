---
title: "Adversarial Review — ARCHITECTURE-SPINE.md (Turnushjelperen)"
status: draft
created: '2026-09-29'
reviewer: adversarial-subagent
target: _bmad-output/planning-artifacts/architecture/architecture-ibe160-turnusprosjekt-2026-09-29/ARCHITECTURE-SPINE.md
method: >
  For each AD and each Deferred/[ASSUMPTION] item, construct two builders (of the four group
  members) who each follow the letter of the spine but make a different, locally-reasonable
  choice at the point the spine is silent or unenforceable, and show the resulting artifact
  cannot integrate.
---

# Adversarial Review — Architecture Spine

**11 incompatibility pairs found.** Ranked by severity below, full detail follows.

## Most serious (top 5)

1. **AD-1's Rule is a static import check, not a runtime data check** — a domain-core builder who models `Kandidat` with a `gyldig: bool` flag (which the ERD note explicitly permits) instead of two disjoint types lets an API-adapter builder legally forward the *full* candidate list — including hard-rule-excluded ones — into the KI adapter's `RangertKandidat` port with `gyldig=false`. No import is violated, so AD-1's mechanical test passes, yet SM-2 ("an excluded candidate is never recommended by AI") is broken at runtime.
2. **AD-3's password-hashing clause is directionally ambiguous** ("kun i autentiseringslaget til `adaptere/api`/`adaptere/lagring`") — one builder puts hashing in the API layer and passes a hash down; another puts hashing in the storage layer and expects to receive plaintext. Whichever pairing occurs, one of the two either stores plaintext or double-hashes, silently.
3. **AD-1 walls the KI adapter off from excluded candidates, but nothing in the spine assigns ownership of the "Ekskludert-boks" exclusion summary** (count + per-rule breakdown, required by EXPERIENCE.md) to any module. One builder invents an export from `domene/regelmotor` straight to `adaptere/api`; another (reading AD-1 literally) assumes exclusion detail simply isn't available outside the domain core and stubs the box. Neither talked to the other; the box either doesn't render or two incompatible endpoints get built.
4. **`RangertKandidat` — the one port the whole paradigm hinges on — has no defined fields** (the ERD explicitly declines to specify them). A domain-core builder ships only absolute values (cost, workload hours, competency level); the KI-adapter builder needs *relative* deltas ("this candidate is X kr cheaper than the cheapest," "Y levels from full qualification") to write FR-11's "what pulls it up / down" explanation without re-deriving ranking logic itself — which AD-1 forbids. One of them is guaranteed to be wrong.
5. **AD-4 decides *that* "ingen gyldige kandidater" and "Avveining feilet" are 200-responses, not *what shape* they take.** One builder returns `[]` (empty candidate array) for FR-6 and a `null` `avveining` field per candidate for FR-11; another builder returns an explicit `{status: "ingen_kandidater"}` wrapper and a top-level `avveining_status` enum. Both satisfy the Rule's letter ("not an HTTP error"); the frontend built against one shape crashes or silently misrenders against the other.

## Full findings

### F1 — AD-1's Rule only checks imports, not payload contents (breaks SM-2)

- **Who:** Domain-core builder (A) vs. API-adapter builder (B).
- **A's reasonable choice:** The ERD note says "Gyldig kandidat er en beregnet tilstand på Kandidat" — not a separate entity. So A implements one `Kandidat`/`RangertKandidat` Pydantic type with a `gyldig: bool` (and `utelukkelses_grunn: str | None`) computed field, rather than two disjoint types. This is the literal, ERD-faithful reading.
- **B's reasonable choice:** B, composing `adaptere/api`, needs *all* candidates (valid and excluded) in one place anyway to build the Ekskludert-boks summary (F3 below). Seeing that `RangertKandidat` already carries a `gyldig` flag, B forwards the full list — the same port type — into the KI adapter for Avveining generation, trusting the KI adapter to filter by the flag itself.
- **Why it breaks:** AD-1's Rule is stated as "`adaptere/ki` mottar utelukkende data formet som porten ... kun Gyldige kandidater" — but the *mechanism* the AD names for enforcement is "et import-linter-kontrakt eller en test... som feiler dersom `domene/regelmotor` importerer `adaptere/ki`." That test only catches the domain core reaching into the KI adapter, or an illegal import — not the API adapter passing an over-broad payload through a legally-shaped port object at runtime. Both A and B satisfy every checkable rule in the spine. SM-2 ("en Kandidat utelukket av en Hard regel blir aldri anbefalt av KI") still fails the first time an excluded candidate slips through with `gyldig=false` and the KI adapter (built by a third person, trusting the port contract) doesn't defensively re-filter.
- **AD-fix:** Add an explicit Rule to AD-1: "`RangertKandidat` instances passed to `adaptere/ki` MUST be a distinct type (or a separately constructed, filtered list) that structurally cannot represent an excluded candidate — no `gyldig`/exclusion field exists on the type the KI adapter receives." Pair with a test that asserts the KI-facing port type has no exclusion-related field, and/or a runtime assertion in the KI adapter's entry point that raises if list length exceeds the confirmed-valid count.

### F2 — AD-3 password-hashing location is ambiguous (plaintext-storage risk)

- **Who:** Storage-adapter builder (C) vs. API-adapter builder (D).
- **C's reasonable choice:** "Lagringsadapteren eier databaseskjemaet" (AD-5) and the phrase "hashing skjer... i `adaptere/api`/`adaptere/lagring`" reads to C as "the storage layer is a valid place to do it" — so C's repository's `create_user`/`verify_password` methods hash on write and compare-hash on read, expecting plaintext in.
- **D's reasonable choice:** D reads the same clause as "hashing is an API-layer *auth* concern" (matching "autentiseringslaget") and hashes the password in `adaptere/api`'s login/seed-user service before ever calling the repository, expecting storage to persist the hash as-is and never re-hash.
- **Why it breaks:** Whichever module is built and integrated second either (a) stores a plaintext password because storage expected an already-hashed value and treated it as opaque, or (b) double-hashes so no login ever succeeds. Because the AD names *two* legal locations ("api/lagring") without saying which one actually performs the hash, both builders can point at the AD text as justification for their choice.
- **AD-fix:** AD-3 Rule should name exactly one hashing boundary, e.g.: "Password hashing occurs exclusively in `adaptere/api`'s auth service, before any call into `adaptere/lagring`; `adaptere/lagring` never receives or stores anything but the final hash and MUST reject (not silently accept) a value that doesn't match the expected hash format." Make it checkable with a repository-level test/type (e.g. a `PasswordHash` newtype the repo accepts, a raw `str` it doesn't).

### F3 — No module owns the exclusion-summary export (Ekskludert-boks)

- **Who:** Domain-core builder (A) vs. API-adapter builder (B) again, independently of F1.
- **A's reasonable choice:** Reading AD-1 literally ("prevents KI... får se en Kandidat som er utelukket"), A treats "excluded candidates" as strictly internal to `domene/regelmotor` — nothing in the Capability→Architecture Map assigns "count and reasons for excluded candidates" anywhere, so A's `regelmotor` only returns the filtered valid list plus a bare count, no per-rule breakdown.
- **B's reasonable choice:** B is building the Kandidatrangering endpoint and knows EXPERIENCE.md's Ekskludert-boks requires "oppsummerer antall og fordeling per Hard regel" with a "Vis full liste ▾" detail view — so B assumes the domain core obviously exposes a second port/method returning per-candidate exclusion reasons, and designs the API response shape around it.
- **Why it breaks:** A never built that export (nothing in the spine required it — the Capability Map only cites AD-1/AD-2/Testing for §4.2, none of which mention an exclusion-detail export). B's endpoint has nothing to call. Either the UI requirement silently degrades to "21 excluded, no breakdown," or B reinvents rule-checking logic in the API layer to reconstruct reasons — duplicating (and risking drifting from) the domain core's Hard-rule logic, which is exactly what AD-1/AD-2 exist to prevent.
- **AD-fix:** Add a Rule (new AD or extend AD-1) that `domene/porter` must define an explicit exclusion-detail port (e.g. `UtelukketKandidat { ansatt_id, grunn: HardRegelType }`) returned alongside `RangertKandidat`, consumed only by `adaptere/api` (never `adaptere/ki`), and add it to the Capability→Architecture Map row for §4.2.

### F4 — `RangertKandidat` has no defined fields (ERD explicitly punts)

- **Who:** Domain-core builder (A) vs. KI-adapter builder (E).
- **A's reasonable choice:** Ships `RangertKandidat` with the values needed to *render a table*: `kandidat_id`, `rangering_plassering`, `kostnad_kr`, `kostnad_type` (ordinær/overtid), `arbeidsbelastning_timer`, `kompetansenivå`. All correct, all traceable to FR-7/FR-8/FR-9.
- **E's reasonable choice:** To satisfy FR-11 ("hva trekker opp, hva som trekker ned... aldri en anbefaling uten gyldig grunnlag"), E needs comparative/derived signals to write a faithful explanation without re-judging the ranking — e.g. `kostnad_differanse_til_billigste`, `kompetanse_avstand_til_full_kvalifisering`, `arbeidsbelastning_rangering_blant_gyldige`. E assumes these are already on the port, since AD-1 forbids the KI adapter from computing anything the domain core is responsible for.
- **Why it breaks:** The fields E needs don't exist on A's model. E is now stuck choosing between (a) asking Gemini to eyeball raw absolute numbers across candidates and infer comparisons itself — which risks contradicting the actual `Rangering` ordering the domain core already computed, silently breaking "Avveining must be consistent with Rangering," or (b) computing the deltas itself in `adaptere/ki`, which is exactly the "KI beregner Rangering" violation AD-1 and PRD §5 (Ikke-mål) forbid. Both options are visible only at integration time.
- **AD-fix:** AD-1 (or a new AD) should pin the actual field list of `RangertKandidat`, explicitly including pre-computed relative/comparative fields the KI adapter is allowed to narrate but not derive, e.g.: "`RangertKandidat` MUST include, per candidate, at minimum: absolute values (cost, workload, competency) AND domain-computed deltas relative to the rest of the valid set (cheapest-cost delta, competency-distance-to-full-qualification, workload percentile). `adaptere/ki` may only prose-ify fields present on the port; it computes no new comparison."

### F5 — AD-4 mandates one *envelope*, not one *empty/fallback shape*

- **Who:** API-adapter builder (B) vs. Web-adapter builder (F).
- **B's reasonable choice:** For FR-6 ("ingen gyldige kandidater"), B returns `200 {"kandidater": []}` — literally the normal Rangering response with a zero-length list, since AD-4 only mandates a shared envelope for actual *errors*, and this isn't one. For FR-11 fallback, B sets `avveining: null` on the candidate object when Gemini fails.
- **F's reasonable choice:** F, reading the same AD-4 clause ("gyldig 200-svar med eksplisitt tomt/reserve-innhold, nettopp for å holdes atskilt") as implying a *distinguishable, explicit* state (not just an empty array indistinguishable from "haven't loaded yet" or "vakt has zero employees configured"), builds the frontend expecting `{"status": "ingen_gyldige_kandidater"}` for FR-6, and an explicit `{"avveining_status": "feilet", "reservetekst": "..."}` object for FR-11 fallback (not `null`, which F's code reads as "avveining still loading," per the progressive-loading assumption in EXPERIENCE.md).
- **Why it breaks:** F's frontend can't distinguish B's `[]` from a loading state or a genuinely-zero-employee edge case, and renders nothing or a spinner forever instead of the mandated "ikke en feil" message (violating the FR-6 testable consequence directly). F's `null`-vs-loading confusion for Avveining similarly risks showing an infinite "beregner..." spinner instead of the reserve text mandated by FR-11.
- **AD-fix:** Extend AD-4's Deferred item into a decided Rule now: pin the exact JSON shape for both empty-states, e.g. explicit discriminated status fields (`{"status": "ok"|"ingen_gyldige_kandidater", "kandidater": [...]}`) and `{"avveining": {"status": "ok"|"feilet"|"lastes", "tekst": "..."}}`) — not implicit emptiness/nullness — so "no data" and "explicit empty" are never structurally the same value.

### F6 — Avveining: persisted entity (per ERD) vs. regenerated-per-request (per no AD)

- **Who:** Storage-adapter builder (C) vs. KI-adapter builder (E).
- **C's reasonable choice:** The spine's own ERD shows `RANGERING ||--o{ AVVEINING : forklares_av` as a first-class relationship, and AD-5 gives `adaptere/lagring` ownership of the schema. C builds an `AVVEINING` table, persisting each generated explanation tied to a `Rangering` snapshot, since that's what the ERD depicts.
- **E's reasonable choice:** Nothing in AD-1–AD-5 says AI output is persisted; AD-1 frames the KI adapter as a stateless consumer of the port ("Ser kun det porten eksponerer"), so E treats Avveining generation as a pure, on-demand call to Gemini triggered fresh every time the Kandidatrangering view loads — no write path to storage was ever wired up, because no AD assigned that responsibility to the KI adapter (which per AD-2 can't own storage access anyway — only `adaptere/api` composes both).
- **Why it breaks:** C's `AVVEINING` table stays permanently empty (nobody writes to it) while E regenerates text on every request. Consequence surfaces at the Godkjenning screen: the Avviksnotat needs to show the *same* top-ranked candidate's Avveining that Kari saw during Kandidatrangering (EXPERIENCE.md UJ-1 step 6), but if it's regenerated fresh (non-deterministic LLM output) rather than fetched from the persisted snapshot, the text Kari confirms against may differ from what she originally read — undermining the "begrunnet valg" the whole product exists to support, and silently contradicts the ERD's own modeling.
- **AD-fix:** New AD: "An `Avveining` is generated once per Rangering computation and persisted by `adaptere/lagring` keyed to that Rangering snapshot; `adaptere/api` reads the persisted Avveining for any subsequent view (including Godkjenning) rather than re-invoking `adaptere/ki`. Regeneration only happens on a new Rangering (i.e., a new vakt-valg), never on re-navigation to an already-computed one."

### F7 — AD-2's state-mutation Rule is enforced by convention, not mechanism

- **Who:** Storage-adapter builder (C) vs. a later API-adapter contributor (G, e.g. the 4th group member adding a "quick reassign" endpoint or admin utility).
- **C's reasonable choice:** Per the Consistency Conventions row ("Ingen mutasjon av Turnus-/Vakt-tilstand uten eksplisitt Godkjenning... håndheves i `adaptere/api`, aldri i frontend alene"), C builds a plain repository method `oppdater_vakt_ansatt(vakt_id, ansatt_id)` with no Godkjenning-state precondition, because the Rule explicitly assigns enforcement to the API layer — not to storage. This is a completely correct reading of the AD.
- **G's reasonable choice:** Later, building or extending `adaptere/api`, G adds a convenience path (e.g. a test-data seeding endpoint, or a "fix a mistake" admin action) that calls `oppdater_vakt_ansatt` directly without routing through the two-step Godkjenning flow, because nothing stops it — there's no Godkjenning-state check in the one place that actually could enforce it mechanically (the repository/schema), and G isn't touching the "real" Godkjenning endpoint so doesn't re-read that Rule.
- **Why it breaks:** The invariant "Ingen endring i Turnusen anses gjennomført før Godkjenning er gitt" (FR-12, SM-8) is a testable PRD invariant, but the spine's Rule for it names an enforcement *location* (a layer, "adaptere/api") rather than an enforcement *mechanism* (a check that fails loudly if violated). This is a discipline-based rule masquerading as an architectural one — nothing is checkable in CI the way AD-1's import-linter test is. Two builders working in good faith, months apart, can easily reintroduce an unguarded mutation path.
- **AD-fix:** Make AD-2's state row mechanically checkable, e.g.: require a domain-level `Godkjenning`-gated write path — `adaptere/lagring` should expose no bare "set employee on vakt" mutation at all, only a `godkjenn_erstatning(godkjenning: Godkjenning)` operation that requires a valid `Godkjenning` value object as a parameter, making the unguarded call a type error, not just a convention violation. Add a test asserting no other public write method exists on the Vakt repository.

### F8 — "Beregner rangering" progressive-loading [ASSUMPTION] has no protocol decision behind it

- **Who:** Web-adapter builder (F) vs. API-adapter builder (B).
- **F's reasonable choice:** EXPERIENCE.md's own suggestion ("rad/rangering vises umiddelbart... hver Avveining lastes progressivt per rad") reads to F as a streaming UI, so F implements an `EventSource`/SSE client expecting the ranked-list endpoint to stream per-row Avveining updates over one open connection.
- **B's reasonable choice:** B, with no AD assigning a transport mechanism (Deferred/[ASSUMPTION] only, per spine's own Deferred list), implements the simplest thing that satisfies FR-9/FR-11 as two ordinary REST calls: `GET /rangering` (fast, no Avveining) then `GET /rangering/{id}/avveining` polled or fired once per row by the frontend on row-expand.
- **Why it breaks:** F's client opens a connection expecting a stream that B's endpoint never provides (plain JSON, connection closes immediately) — no incremental updates ever arrive, and depending on F's implementation this either silently stalls the "expanded by default" top-ranked row's Avveining forever (contradicting the explicit UX requirement that it's expanded on load) or throws on the unexpected content-type.
- **AD-fix:** Promote this from [ASSUMPTION] to a Rule in AD-4 or a new AD: pin the transport (e.g. "the ranking endpoint returns the full candidate list synchronously without Avveining; each row's Avveining is fetched via a separate, individually-cacheable `GET`, invoked by the frontend per row — no server-sent-events/streaming in v1").

### F9 — Timezone handling gap threatens SM-5 reproducibility for the two time-based Hard rules

- **Who:** Domain-core builder (A) vs. Storage-adapter builder (C).
- **A's reasonable choice:** Implements 11-timersregelen/35-timersregelen math (FR-4/FR-5) treating all `Vakt` start/end `datetime`s as timezone-aware UTC internally, since that's the safest default for a "ren Python" deterministic core.
- **C's reasonable choice:** Persists `Vakt.start`/`Vakt.slutt` as naive local-time `DATETIME` columns in SQLite (SQLite has no native timezone type, and the spine only says "ISO 8601... tidssonehåndtering er ikke detaljert — se Deferred"), and the conversion-in-`adaptere/lagring` step (mandated by AD-5) passes them through to domain types without attaching a timezone.
- **Why it breaks:** A's rest-hour math silently operates on values C never intended as UTC (they're local Europe/Oslo wall-clock time). Each builder's own unit tests pass in isolation (A tests against UTC fixtures they wrote themselves; C never round-trips through the actual rule logic). Only at integration — and only near a DST boundary or for a wide enough set of real-shaped test data — does SM-5's "samme input gir samme resultat" and SM-1's "100% filtrert i definerte testscenarioer" quietly produce an off-by-one-hour miscalculation that could wrongly admit or exclude a candidate under FR-4/FR-5, a testable invariant nobody's test actually catches because both sides tested against their own assumption.
- **AD-fix:** Add a Rule to the Data & formats convention row (replacing the current Deferred note): "All `datetime` values crossing the `adaptere/lagring` ↔ `domene` boundary are timezone-aware and normalized to UTC by `adaptere/lagring` at the point of conversion (per AD-5); `domene/regelmotor` never accepts or stores a naive datetime — enforce with a type check/assertion at the port boundary." Add a DST-boundary test case to the required per-Hard-rule test module (Testing convention row).

### F10 — Myke faktor weighting (Deferred) breaks if split across two contributors on the same module

- **Who:** Two contributors both touching `domene/regelmotor` — one implementing the Hard rules (FR-2–FR-5) and cost/workload calculation (FR-7/FR-8), another implementing FR-9's ranking/weighting.
- **Each one's reasonable choice:** The Deferred item explicitly states only that "kompetansenærhet skal telle tungt når ingen Kandidat er fullt kvalifisert" is settled — everything else about relative weighting is open, "avklares av gruppen før implementasjon." Absent that group conversation actually happening before both people start coding, one contributor might weight cost most heavily (over-indexing on FR-9's "billigste ikke rangeres høyest" test case, but only by a small margin), while the other weights workload-balancing most heavily — both satisfy every *testable consequence* FR-9 lists (cheapest-not-always-top holds either way; competency-closest-wins-when-none-fully-qualified holds either way) yet produce materially different, non-reconcilable rankings if their two implementations are ever merged/reconciled rather than one simply overwriting the other.
- **Why it breaks:** This isn't hidden — the spine already flags it as Deferred — but it's flagged as a *content* decision ("avklares av gruppen"), not tied to any process or artifact that would catch two people independently writing conflicting weighting code before that conversation happens. Nothing in the spine says "only one person touches `domene/regelmotor`'s ranking function" or requires the weighting formula to be captured in a checked-in, single-source config/constant before either starts.
- **AD-fix:** Not a new AD so much as tightening the existing Deferred item into a process gate: state explicitly that no implementation of FR-9's weighting begins until the weighting is captured as a single, named, checked-in artifact (e.g. a `VEKTING` constant/table in `domene/regelmotor` with one commit, one owner) — i.e., make the Deferred item block the relevant Capability→Architecture Map row until resolved, the same way AD-1/AD-2 already gate §4.2–§4.4.

### F11 — JWT expiry/renewal (Deferred) leaves "utløpt sesjon" behaviorally undefined across two adapters

- **Who:** API-adapter builder (B) vs. Web-adapter builder (F).
- **B's reasonable choice:** Ships JWTs with a short, hardcoded expiry (e.g. 20 minutes) and no refresh endpoint, since AD-3 defers "nøyaktig token-innhold, utløpstid og fornyelsespolicy."
- **F's reasonable choice:** Builds the "Ikke innlogget / utløpt sesjon" state (EXPERIENCE.md State Patterns row) assuming a silent-refresh pattern exists — catches a 401, attempts a token refresh transparently, and only redirects to Logg inn if that refresh also fails — because that's the common pattern for this state and nothing in the spine rules it out.
- **Why it breaks:** F's silent-refresh call hits a `/refresh`-shaped endpoint that B never built (404/405), so every session expiry becomes an unhandled error rather than the clean redirect-to-login the state pattern promises — during, plausibly, the middle of Kari reviewing a Kandidatrangering, the exact moment the UX doc is most emphatic about not confusing errors with normal states.
- **AD-fix:** Resolve the Deferred item with a minimal Rule now rather than at implementation time: "No refresh/renewal endpoint in v1; JWT expiry is fixed at N minutes; the web adapter treats any 401 as an immediate, unconditional redirect to Logg inn — no silent retry." This is a one-line decision that closes a real, currently-open behavioral fork.

## Summary table

| # | AD / gap | Builders | Breaks |
|---|---|---|---|
| F1 | AD-1 Rule (static import check only) | domain core / API adapter | SM-2 invariant |
| F2 | AD-3 hashing location ambiguity | storage / API adapter | plaintext password or double-hash |
| F3 | Silent gap: exclusion-summary ownership | domain core / API adapter | Ekskludert-boks unbuildable or duplicated logic |
| F4 | `RangertKandidat` fields undefined | domain core / KI adapter | FR-11 explanation inconsistent with Rangering |
| F5 | AD-4 envelope vs. empty/fallback shape | API adapter / web adapter | FR-6/FR-11 empty-states unrenderable |
| F6 | Avveining persistence undecided | storage / KI adapter | Godkjenning shows different text than Kandidatrangering |
| F7 | AD-2 state-mutation enforced by convention | storage / API adapter (later) | FR-12/SM-8 bypassable, no mechanical check |
| F8 | "Beregner rangering" transport [ASSUMPTION] | web adapter / API adapter | streaming client vs. plain REST server |
| F9 | Timezone handling deferred | domain core / storage | SM-1/SM-5 reproducibility silently wrong near DST |
| F10 | Myke faktor weighting (Deferred) split across contributors | two `regelmotor` contributors | conflicting rankings, both pass FR-9 tests |
| F11 | JWT expiry/renewal (Deferred) | API adapter / web adapter | "utløpt sesjon" state breaks mid-session |
