from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .manifests import list_project_manifests


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def render_delivery_board(root: Path) -> dict[str, Any]:
    projects = []
    for project, manifest in list_project_manifests(root):
        replay_rows = _read_jsonl(root / "runs" / "replay" / f"{project}.jsonl")
        evidence_rows = _read_jsonl(root / "runs" / "evidence" / f"{project}.jsonl")
        latest_replay = replay_rows[-1] if replay_rows else None
        projects.append(
            {
                "project": project,
                "title": manifest.get("title", project),
                "objective": manifest.get("objective", ""),
                "primary_metric": manifest.get("primary_metric", ""),
                "promotion_ladder": manifest.get("promotion_ladder", []),
                "latest_replay": latest_replay,
                "evidence_count": len(evidence_rows),
            }
        )

    board = {"projects": projects}
    out_dir = root / "artifacts" / "delivery"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")

    lines = ["# ARUGULA Delivery Board", ""]
    for item in projects:
        latest = item["latest_replay"] or {}
        status = latest.get("status", "pending")
        replay_id = latest.get("replay_id", "—")
        lines.extend(
            [
                f"## {item['title']} ({item['project']})",
                f"- Objective: {item['objective'] or 'n/a'}",
                f"- Primary metric: {item['primary_metric'] or 'n/a'}",
                f"- Promotion ladder: {', '.join(item['promotion_ladder']) or 'n/a'}",
                f"- Latest replay: {status} ({replay_id})",
                f"- Evidence bundles: {item['evidence_count']}",
                "",
            ]
        )
    (out_dir / "board.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return board
