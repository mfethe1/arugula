# ARUGULA

**Adaptive Research, Governance, Utility, Learning, and Autonomy**

ARUGULA is the control plane for self-improving product systems.

It generalizes the autoresearch pattern into an enterprise-grade evolution engine:

- observe real-world signals
- propose bounded mutations
- route specialist agents over NATS
- evaluate against scorecards
- keep or revert
- promote wins into backlog, product defaults, or production workflows

## Initial targets
- BuildBid
- rareagent.work
- Fermware
- Investment / stock trading
- memU

## Core principles
- Score specialists and orchestration separately
- Mutate one important variable at a time
- Use real outcomes whenever possible
- Keep full provenance for every decision
- Promote through replay -> shadow -> canary -> production

## Repo layout
- `docs/` architecture, scorecards, rollout model
- `schemas/` shared JSON contracts
- `subjects/` NATS subject map
- `projects/` project-specific manifests and scorecards
- `src/arugula/` control-plane code
- `runs/` local run artifacts (gitignored except templates)

## Near-term mission
1. Establish the shared experiment and scorecard model.
2. Wire NATS subjects for proposal, scoring, promotion, and rollback flows.
3. Stand up project manifests for the five active systems.
4. Run the first bounded mutations in low-risk modes.

## First implementation targets
- BuildBid: missing-scope + dependency-error reduction
- rareagent.work: completion reliability + lower rework
- Fermware: deviation detection + audit completeness
- trading: orchestration-vs-specialist scoring split + paper-trading baseline ingestion
- memU: retrieval usefulness uplift

## Trading quick start
Build the baseline scorecard from existing paper-trading sessions:

```bash
PYTHONPATH=src python3 -m arugula.cli --root . build-trading-baseline \
  --source-dir ../trading-agents/paper_trading \
  --experiment-id trading-exp-002
```

This writes a normalized replay dataset and a week-0 scorecard under `artifacts/trading/` so regime/sizing/escalation mutations can be compared against a real baseline instead of intuition.
