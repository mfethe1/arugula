# ARUGULA Governance Guardrails

This file defines the minimum governance posture for autonomous experimentation.

## Approval boundaries
- `replay` may be proposed and executed automatically when guardrails are present.
- `shadow` may run automatically only when it cannot mutate user-visible state.
- `canary`, `production`, and `default pattern` promotion require an explicit approval record with actor identity.
- Rollback requests/completions are also control-plane actions and must carry approval metadata so emergency changes still leave an audit trail.

### Approval metadata shape
```json
{
  "approval": {
    "state": "approved",
    "actor": "michael" 
  }
}
```

## Provenance requirements
Every control-plane event should be replayable and attributable. Event envelopes must capture at least:
- stable `event_id`
- `recorded_at`
- published subject
- repo commit/reference used to generate the event
- transport type
- project scope

## NATS subject safety
- Publish only subjects from `subjects/nats-subjects.md`.
- Reject wildcard publishes and unknown projects.
- Treat `promote.*` and `rollback.*` as privileged subjects.

## Secret handling assumptions
- ARUGULA should store secret *references* or names, not raw credential material, inside experiments, event logs, or evidence bundles.
- Run artifacts under `runs/` and `artifacts/` are assumed readable by operators; they must not become secret dumps.
- If an experiment depends on credentials, declare the dependency in `secret_inputs` and resolve it out-of-band.

## Tenant isolation placeholder policy
- Until per-tenant execution boundaries exist, experiments must declare `tenant_scope` explicitly.
- Shared-control-plane experiments need an extra review because replay artifacts and evidence can otherwise mix tenants.
- Absence of tenant scope should be treated as a governance failure, not as "single tenant by default".

## Dangerous autopromotion risk
The biggest failure mode here is a loop that begins to treat its own score improvements as authority to promote itself. Prevent that by keeping these boundaries hard:
- improvement evidence is not approval
- proposal acceptance is not rollout approval
- canary success is not permission for production or default-pattern promotion
- default-pattern promotion must reference a human or policy approval artifact

## Rollback safety
- Every experiment must define a concrete rollback rule before execution.
- Promotion decisions should reference the rollback path or commit/version being reverted to.
- Rollback completion should produce its own event rather than silently editing state.
