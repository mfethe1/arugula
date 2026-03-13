# memU AUTORESEARCH Charter

## System objective
Improve retrieval usefulness and reduce irrelevant or stale memory resurfacing.

## First experiment track
- retrieval fusion weights
- salience thresholds
- chunking policy
- writeback rules

## Primary metric
- retrieval_usefulness_uplift

## Guardrails
- irrelevant_recall_rate
- missed_critical_memory_rate
- stale_fact_resurfacing_rate
- duplicate_growth_rate
- latency
- token_cost_per_useful_retrieval

## Initial promotion mode
replay
