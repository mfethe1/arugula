# memU Health Sweep Action Plan for ARUGULA

## Purpose
Consolidate recent memU health-sweep findings into a short execution plan that lets ARUGULA run memU-first improvement loops with clean evidence, stable contracts, and merge discipline.

## Consolidated findings from current docs + sweep history

### What is already true
- ARUGULA already prioritizes **memU first** before expanding to other projects (`docs/PRIORITY_PLAN.md`).
- A first memU replay run exists (`runs/evidence/memu.jsonl`) with replay completion evidence.
- The canonical memU proof gate is explicit: every sweep should capture **status + request_id + payload_hash + route/path** (`../docs/memory-system.md`).

### What remains unstable
1. **Auth/header drift**
   - Some docs say `X-API-Key` is canonical (`../docs/memory-system.md`).
   - Other docs say `X-MemU-Key` is primary/canonical (`../docs/memu.md`, `../docs/memu_quickstart.md`, `../docs/MEMU_CONTRACT.md`).
   - Sweep history shows repeated 401/422 confusion tied to this drift.
2. **Route compatibility drift**
   - Canonical endpoints may be healthy while legacy `/api/v1/memu/store/search` still returns 404.
   - OpenAPI availability has also drifted across sweeps (200/500/404 in history).
3. **Search contract ambiguity**
   - Validation behavior has varied between `query`, `query_embedding`, and dimension-mismatch failures.
   - Some rate-limit or validation failures were surfaced as 500s instead of clean 4xx/429 behavior.
4. **Sweep noise / NOOP risk**
   - Historical sweeps repeated the same evidence without changing deployment state.
   - Current standard already warns to reduce repeated identical sweeps.
5. **ARUGULA evidence is not yet a full operating loop**
   - Replay proof exists, but the sweep output is not yet normalized into a stable mutation backlog, owner map, and promotion gate.

## Execution goal
Get memU to a state where ARUGULA can run two clean replay/shadow-quality loops with one retained or clearly rejected mutation, using stable transport, stable contract checks, and auditable evidence.

---

## Phased plan

### Phase 0 — Freeze the contract surface (P0)
**Owner:** Macklemore  
**Support:** Lenny

**Objective**
Make the memU API contract unambiguous before changing retrieval logic.

**Actions**
- Pick one canonical auth header for production clients (`X-MemU-Key` is the better choice because it is already the explicit memU-specific header in `memu.md` and `MEMU_CONTRACT.md`).
- Keep the secondary header only as a documented compatibility path with an expiration note.
- Publish one canonical route matrix for:
  - `/health`
  - `/search`
  - `/search-text`
  - `/upsert`
  - `/add`
  - `/recent`
  - legacy `/api/v1/memu/store/search`
- Lock the accepted request shapes for text search vs embedding search.
- Ensure OpenAPI exposes the real contract or explicitly document why not.

**Dependencies**
- Railway memU deployment access
- ability to update memU docs + API behavior together

**Risks**
- Fixing docs without fixing runtime will create more drift.
- Removing compatibility too early will break stale clients and old sweep scripts.

**Exit criteria**
- One doc source of truth for auth + routes
- OpenAPI or equivalent route table matches runtime
- no ambiguous “canonical header” language left in docs

---

### Phase 1 — Make sweep evidence replay-grade (P0)
**Owner:** Lenny  
**Support:** Macklemore

**Objective**
Turn memU health sweeps into structured ARUGULA evidence instead of ad hoc notes.

**Actions**
- Standardize one sweep artifact schema per run:
  - route/path
  - method
  - header mode used
  - status
  - request_id
  - latency_ms
  - payload_hash when applicable
  - regression_class (`auth`, `route`, `schema`, `rate_limit`, `5xx`, `noop`)
- Write each sweep into ARUGULA evidence under the memU project rather than only daily memory notes.
- Split “expected degradation” from “new regression” so ARUGULA does not overreact to known broken legacy paths.
- Tag repeated identical findings as NOOP and suppress promotion/escalation unless the contract changed.

**Dependencies**
- Phase 0 contract freeze
- stable evidence bundle format in ARUGULA

**Risks**
- If Phase 1 starts before contract freeze, evidence will stay noisy and non-comparable.
- Missing payload hashes will weaken dedupe and replayability.

**Exit criteria**
- two consecutive sweeps produce comparable evidence tuples
- known-issue vs new-regression labeling is deterministic
- ARUGULA can ingest sweep output without manual cleanup

---

### Phase 2 — Fix transport and error semantics (P0/P1)
**Owner:** Macklemore  
**Support:** Lenny

**Objective**
Eliminate misleading failure modes that poison ARUGULA scoring.

**Actions**
- Normalize auth failures to clean 401s.
- Normalize validation failures to 4xx, not wrapped 500s.
- Normalize rate-limit failures to explicit 429s with retry guidance when possible.
- Keep request IDs on all non-2xx responses.
- Confirm health/search/recent/openapi endpoints do not emit silent schema drift.

**Dependencies**
- deployment access
- route/auth contract from Phase 0

**Risks**
- Hidden proxy behavior may still wrap responses.
- Rate-limit fixes may expose upstream quota issues that require provider fallback work.

**Exit criteria**
- no known 500 path for bad embedding dimensions or auth/header mismatch
- 429 behavior is observable rather than masked
- sweep evidence shows regression class directly from HTTP semantics

---

### Phase 3 — Run the first bounded ARUGULA mutation loop (P1)
**Owner:** Rosie for hypothesis framing, Macklemore for implementation, Lenny for verification

**Objective**
Use clean sweep evidence to choose one memU mutation and evaluate it properly.

**Candidate first mutations**
Choose **one only**:
1. retrieval fusion weights
2. salience threshold tuning
3. text-query fallback / search contract hardening
4. writeback dedupe rule

**Recommended first mutation**
Start with **text-query fallback + search contract hardening** because the sweep history shows contract instability is blocking trustworthy retrieval-quality measurement.

**Actions**
- define experiment id, scorecard, guardrails, rollback rule
- replay against benchmark set
- capture before/after on:
  - retrieval usefulness uplift
  - irrelevant recall rate
  - missed critical memory rate
  - latency
  - token cost per useful retrieval

**Dependencies**
- Phase 1 evidence normalization
- benchmark set and judged queries

**Risks**
- jumping to retrieval tuning before contract stability will create fake “wins” caused by infrastructure noise
- multiple simultaneous mutations will invalidate conclusions

**Exit criteria**
- one replay scorecard with explicit sample count
- one retain/reject decision with provenance
- rollback reference recorded

---

### Phase 4 — Shadow rollout + cross-agent operating cadence (P1)
**Owner:** Macklemore  
**Support:** Winnie (operator-facing impact), Lenny (regression gate)

**Objective**
Move from replay to controlled shadow use without destabilizing shared memory.

**Actions**
- run shadow retrieval only for internal agent workflows first
- compare baseline vs candidate retrieval paths side-by-side
- only promote after clean canary approval metadata exists
- feed retained wins back into backlog/defaults

**Dependencies**
- successful Phase 3 replay decision
- approval path for any canary/prod promotion

**Risks**
- shared memory pollution from premature writeback changes
- operator trust loss if stale/irrelevant recall worsens during shadow

**Exit criteria**
- shadow evidence demonstrates stable guardrails
- promotion request carries approval metadata per governance rules

---

## Merge and delivery discipline for this work

### Worktrees
- Every memU or ARUGULA change happens in a dedicated git worktree.
- Branch naming:
  - `mack/memu-contract-freeze`
  - `lenny/memu-sweep-evidence-gate`
  - `rosie/memu-hypothesis-001`
- No edits on `main` and no shared working directory for parallel tasks.

### Pull / commit / push cadence
- Start every task with `git pull --rebase`.
- Commit each logical unit separately:
  - contract/doc updates
  - sweep artifact/schema updates
  - transport/error normalization
  - experiment wiring
- Commit message format:
  - `[macklemore] fix: normalize memu auth semantics`
  - `[lenny] test: add memu sweep evidence bundle gate`
- Push at the end of each verified unit, not only at the end of the whole phase.

### Regression gates before merge
No PR merges unless all of the following pass:
- memU smoke test hits canonical health/search paths successfully
- request_id present on failure paths sampled in test matrix
- documented auth header behavior matches runtime behavior
- ARUGULA memU replay evidence renders cleanly
- no unexplained new 5xx/429 burst in the last 24h sweep window
- docs updated in the same PR as runtime contract changes

### Review routing
- Macklemore PRs on infra/runtime changes: reviewed by Lenny
- Lenny PRs on sweep/test/evidence logic: reviewed by Macklemore
- Rosie hypothesis/scorecard changes: reviewed by Lenny for measurement discipline

---

## NATS communication contract for the memU loop

Use ARUGULA’s documented subjects only.

### Required subjects for this work
- `arugula.signal.memu.telemetry`
- `arugula.signal.memu.incident`
- `arugula.hypothesis.memu.proposed`
- `arugula.mutation.memu.proposed`
- `arugula.mutation.memu.accepted`
- `arugula.run.memu.started`
- `arugula.run.memu.completed`
- `arugula.score.memu.computed`
- `arugula.rollback.memu.requested`
- `arugula.rollback.memu.completed`
- `arugula.memory.write.memu`
- `arugula.ledger.append.memu`
- `arugula.backlog.append.memu`

### Messaging rules
- Sweeps publish **telemetry** for routine evidence and **incident** only for real regressions.
- Mutation acceptance, promotion, and rollback events must carry approval metadata where required.
- Do not publish wildcard subjects.
- Use NATS events to announce phase boundaries, but treat the git repo + evidence artifacts as source of truth.

### Minimal event sequence per experiment
1. `arugula.hypothesis.memu.proposed`
2. `arugula.mutation.memu.proposed`
3. `arugula.run.memu.started`
4. `arugula.signal.memu.telemetry` (sweep + replay evidence)
5. `arugula.score.memu.computed`
6. either:
   - reject and record backlog follow-up, or
   - `arugula.mutation.memu.accepted` with approval metadata for next rung

---

## Immediate next actions
1. **Macklemore:** freeze auth/route contract and align `memory-system.md` vs `memu.md` vs `MEMU_CONTRACT.md`.
2. **Lenny:** add a single normalized sweep artifact format and gate repeated NOOP sweeps.
3. **Rosie:** define memU hypothesis `MU-002` focused on search contract hardening before retrieval-tuning experiments.
4. **Team:** do not start non-memu ARUGULA expansion until memU satisfies the existing expansion gate.

## Success definition
This plan succeeds when memU is no longer “health-check green but operationally ambiguous,” and ARUGULA can make one bounded memU improvement decision from stable, replayable evidence rather than from drift, noise, or conflicting docs.
