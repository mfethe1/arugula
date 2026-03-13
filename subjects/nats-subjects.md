# NATS Subject Map

## Global
- `arugula.control.heartbeat`
- `arugula.control.health`
- `arugula.control.policy`

## Per-project subjects
Replace `<project>` with `buildbid`, `rareagent`, `fermware`, `trading`, or `memu`.

### Signals
- `arugula.signal.<project>.telemetry`
- `arugula.signal.<project>.incident`
- `arugula.signal.<project>.feedback`
- `arugula.signal.<project>.outcome`

### Evolution workflow
- `arugula.hypothesis.<project>.proposed`
- `arugula.mutation.<project>.proposed`
- `arugula.mutation.<project>.accepted`
- `arugula.run.<project>.started`
- `arugula.run.<project>.completed`
- `arugula.score.<project>.computed`
- `arugula.promote.<project>.requested`
- `arugula.promote.<project>.approved`
- `arugula.rollback.<project>.requested`
- `arugula.rollback.<project>.completed`

### Persistence
- `arugula.memory.write.<project>`
- `arugula.ledger.append.<project>`
- `arugula.backlog.append.<project>`
