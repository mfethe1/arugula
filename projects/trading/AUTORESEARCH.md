# Trading AUTORESEARCH Charter

## System objective
Improve risk-adjusted decision quality while measuring orchestration quality separately.

## First experiment track
- regime weighting
- thesis breaker escalation
- sizing logic
- data-loop normalization from paper-trading + execution logs

## Evidence sources to wire into the loop
- `../trading-agents/paper_trading/SESSION-*.json` for signal -> analysis -> approval -> execution outcomes
- `../trading/logs/*.json` for live scanner / rebalance artifacts
- `../trading/market-research/*.md` for macro and discretionary context snapshots
- `../trading/experiments/*.json` for factor and flow experiments

## Immediate bounded experiments
1. Build a baseline scorecard from recent paper-trading sessions so specialist vs orchestration quality is measurable.
2. Split rejection reasons into regime / sizing / structure / reward-risk buckets and score them separately.
3. Replay a regime-aware weighting mutation against the same normalized session dataset before promoting anything.

## Primary metric
- risk_adjusted_return_composite

## Guardrails
- max_drawdown
- concentration
- turnover
- slippage
- regime_mismatch_rate

## Initial promotion mode
replay
