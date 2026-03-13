from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ledger import append_jsonl


class NatsBus:
    """Minimal local stand-in for NATS-backed publication.

    This writes every published event to a local ledger so the system is runnable
    immediately. A real NATS transport can replace this without changing the CLI
    contract.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.events_path = root / "runs" / "events.jsonl"

    def publish(self, subject: str, payload: dict[str, Any]) -> None:
        append_jsonl(self.events_path, {"subject": subject, "payload": payload})

    def publish_json(self, subject: str, payload: dict[str, Any]) -> str:
        self.publish(subject, payload)
        return json.dumps({"subject": subject, "payload": payload}, indent=2)
