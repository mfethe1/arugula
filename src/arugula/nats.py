from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ledger import append_jsonl
from .policy import validate_payload, validate_subject


class NatsBus:
    """Minimal local stand-in for NATS-backed publication.

    This writes every published event to a local ledger so the system is runnable
    immediately. A real NATS transport can replace this without changing the CLI
    contract.

    Safety guardrails:
    - subjects must come from the documented ARUGULA subject map
    - wildcard subjects are rejected
    - approval-bearing subjects must include approval metadata
    - each event gets a provenance envelope for replay and audit
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.events_path = root / 'runs' / 'events.jsonl'

    def _git_commit(self) -> str | None:
        try:
            result = subprocess.run(
                ['git', '-C', str(self.root), 'rev-parse', 'HEAD'],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
        commit = result.stdout.strip()
        return commit or None

    def _envelope(self, subject: str, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        project = payload.get('project')
        return {
            'event_id': str(uuid.uuid4()),
            'recorded_at': now,
            'subject': subject,
            'project': project,
            'payload': payload,
            'provenance': {
                'transport': 'local-ledger',
                'schema_version': 'arugula.event.v1',
                'recorded_at': now,
                'repo_root': str(self.root),
                'git_commit': self._git_commit(),
            },
        }

    def publish(self, subject: str, payload: dict[str, Any]) -> dict[str, Any]:
        validate_subject(subject)
        validate_payload(subject, payload)
        event = self._envelope(subject, payload)
        append_jsonl(self.events_path, event)
        return event

    def publish_json(self, subject: str, payload: dict[str, Any]) -> str:
        event = self.publish(subject, payload)
        return json.dumps(event, indent=2)
