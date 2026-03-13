# ARUGULA Architecture

## Mission
Create a reusable evolution control plane for enterprise AI systems.

ARUGULA is not a single agent. It is a governed system for improving multi-agent and product workflows through measured mutation.

## Control-plane layers

### 1. Signal layer
Collect evidence from:
- product telemetry
- errors and incidents
- human overrides
- customer usage
- market outcomes
- backlog churn
- support pain points
- memory retrieval quality

### 2. Specialist layer
Project-specific agents produce diagnoses or proposals.
Examples:
- BuildBid: scope extractor, trade estimator, anomaly detector
- rareagent.work: task decomposer, executor, verifier, safety checker
- Fermware: deviation detector, SOP compliance checker, yield predictor
- trading: macro, sector, risk, execution, synthesis
- memU: intake scorer, deduper, retriever, fusion orchestrator

### 3. Orchestration layer
Responsibilities:
- merge proposals
- de-conflict changes
- choose one mutation per experiment
- assign confidence
- route to replay/shadow/canary/prod

### 4. Evaluation layer
Each experiment must define:
- primary metric
- guardrails
- minimum sample size
- evaluation window
- keep/revert rule

### 5. Promotion layer
Promotion ladder:
1. design
2. replay
3. shadow
4. canary
5. production
6. default pattern

### 6. Provenance + memory layer
Everything is logged with:
- evidence bundle
- mutation target
- score delta
- commit / rollback reference
- project and agent version
- approval state

## Runtime model
ARUGULA uses NATS as the event backbone.

### Main subjects
- `arugula.signal.<project>`
- `arugula.hypothesis.<project>`
- `arugula.mutation.<project>.proposed`
- `arugula.mutation.<project>.accepted`
- `arugula.run.<project>.started`
- `arugula.run.<project>.completed`
- `arugula.score.<project>`
- `arugula.promote.<project>`
- `arugula.rollback.<project>`
- `arugula.memory.write.<project>`

## Core system objects
- System
- Agent
- Layer
- Experiment
- Mutation
- Run
- Scorecard
- PromotionDecision
- RollbackDecision
- EvidenceBundle

## Enterprise requirements
- RBAC and policy gates
- auditability
- replayability
- canary promotion
- human signoff where needed
- per-tenant isolation
- real observability
- deterministic score calculations where required

## Design constraints
- mutate one important variable at a time
- score specialists and orchestrators separately
- prefer real outcomes over synthetic outcomes
- no silent promotion to production
- no improvement claim without evidence
