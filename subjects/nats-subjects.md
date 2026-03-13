# NATS Subject Map

## Global
- `arugula.control.heartbeat`
- `arugula.control.health`
- `arugula.control.policy`

## Subject safety rules
- Only documented literal subjects are valid. Wildcards (`*`, `>`) are for subscriptions, never for published events.
- `<project>` must be one of: `buildbid`, `rareagent`, `fermware`, `trading`, `memu`.
- Promotion and rollback subjects are control-plane actions, not observations; they require explicit approval metadata.
- Production/default-pattern promotion must never be emitted from speculative or self-modifying loops without a separate approved decision record.

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
- `arugula.mutation.<project>.accepted` *(requires approval metadata)*
- `arugula.run.<project>.started`
- `arugula.run.<project>.completed`
- `arugula.score.<project>.computed`
- `arugula.promote.<project>.requested` *(requires approval metadata)*
- `arugula.promote.<project>.approved` *(requires approval metadata)*
- `arugula.rollback.<project>.requested` *(requires approval metadata)*
- `arugula.rollback.<project>.completed` *(requires approval metadata)*

### Persistence
- `arugula.memory.write.<project>`
- `arugula.ledger.append.<project>`
- `arugula.backlog.append.<project>`
