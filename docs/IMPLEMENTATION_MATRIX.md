# Implementation Matrix

## BuildBid
### Objective
Improve estimate reliability and reduce embarrassing misses.

### Primary score
- estimate accuracy delta vs reviewed target or actuals

### Guardrails
- missing scope rate
- dependency error rate
- duplicate item rate
- hallucinated line items
- time to first usable estimate
- human edit distance

### First bounded mutations
- trade dependency rules
- scope-gap detection rules
- confidence ranking in synthesis

### Initial promotion mode
- replay -> shadow on historical bid packages

## rareagent.work
### Objective
Increase task completion reliability while lowering supervision burden.

### Primary score
- accepted task completion rate

### Guardrails
- rework rate
- scope violation rate
- unverifiable completion rate
- unsafe action attempts
- token/cost overhead

### First bounded mutations
- task decomposition prompt
- verification checklist
- completion criteria

### Initial promotion mode
- replay -> canary on internal tasks

## Fermware
### Objective
Improve deviation detection, batch record quality, and operator usefulness.

### Primary score
- deviation detection quality + audit completeness composite

### Guardrails
- false alarms
- missed deviations
- operator friction
- record completion lag
- override rate

### First bounded mutations
- anomaly thresholds
- SOP reminder timing
- release-readiness summary format

### Initial promotion mode
- replay only until validation data is available

## trading
### Objective
Improve risk-adjusted decision quality and orchestration quality separately.

### Primary score
- risk-adjusted return composite (Sharpe / drawdown penalty)

### Guardrails
- max drawdown
- concentration
- turnover
- slippage
- regime mismatch

### First bounded mutations
- evidence weighting by regime
- sizing rule
- thesis breaker escalation rule

### Initial promotion mode
- replay -> paper trading -> shadow live

## memU
### Objective
Increase downstream usefulness of memory retrieval.

### Primary score
- task success uplift from retrieved context

### Guardrails
- irrelevant recall rate
- missed critical memory rate
- duplicate growth
- stale fact resurfacing
- latency
- token cost per useful retrieval

### First bounded mutations
- retrieval fusion weights
- salience thresholds
- chunking policy
- writeback rules

### Initial promotion mode
- benchmark replay -> shadow retrieval -> controlled rollout
