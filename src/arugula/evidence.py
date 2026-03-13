from __future__ import annotations

from pathlib import Path
from typing import Any

from .ledger import append_jsonl


def attach_evidence(
    root: Path,
    *,
    project: str,
    experiment_id: str,
    kind: str,
    uri: str,
    note: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "project": project,
        "experiment_id": experiment_id,
        "kind": kind,
        "uri": uri,
        "note": note,
        "metadata": metadata or {},
    }
    append_jsonl(root / "runs" / "evidence" / f"{project}.jsonl", record)
    append_jsonl(root / "runs" / "events.jsonl", {"subject": f"arugula.evidence.{project}.attached", "payload": record})
    return record
