from __future__ import annotations

from pathlib import Path

from .manifests import ensure_foundation


TEMPLATES = {
    "templates/projects/manifest.json": '''{
  "project": "replace-me",
  "title": "Replace Me",
  "priority": 1,
  "objective": "Describe the system objective.",
  "primary_metric": "replace_primary_metric",
  "guardrails": [
    "guardrail_one",
    "guardrail_two"
  ],
  "evaluation_window": "replay batch 01",
  "promotion_ladder": ["replay", "shadow", "canary", "production"],
  "mutation_targets": [
    "prompt_or_policy_target"
  ],
  "evidence_sources": [
    "telemetry",
    "human review"
  ],
  "approval_mode": "no autonomous promotion beyond replay without explicit review artifact",
  "rollback_rule": "revert if the primary metric fails to improve or any guardrail regresses materially"
}
''',
    "templates/experiments/experiment.yaml": '''experiment_id: replace-exp-001
project: replace-me
title: Replace with bounded experiment title
mutation_target: replace-target
primary_metric: replace_primary_metric
guardrails:
  - guardrail_one
  - guardrail_two
evaluation_window: replay batch 01
promotion_mode: replay
verify_command: python -m arugula render-board
rollback_rule: revert if the primary metric fails to improve or any guardrail regresses materially
notes: Keep mutation scope narrow and evidence-backed.
''',
    "templates/evidence/evidence-bundle.json": '''{
  "project": "replace-me",
  "experiment_id": "replace-exp-001",
  "kind": "benchmark_report",
  "uri": "artifacts/example.txt",
  "note": "Short human-readable evidence note",
  "metadata": {
    "source": "benchmark"
  }
}
''',
}


def install_templates(root: Path) -> list[str]:
    ensure_foundation(root)
    written: list[str] = []
    for rel, content in TEMPLATES.items():
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(rel)
    return written
