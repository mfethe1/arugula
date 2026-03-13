from __future__ import annotations

from pathlib import Path

from .ledger import append_jsonl
from .projects import PROJECTS


def bootstrap(root: Path) -> None:
    (root / "runs").mkdir(parents=True, exist_ok=True)
    (root / "artifacts").mkdir(parents=True, exist_ok=True)
    (root / "runs" / ".gitkeep").touch(exist_ok=True)
    (root / "artifacts" / ".gitkeep").touch(exist_ok=True)

    for project_key, meta in PROJECTS.items():
        append_jsonl(
            root / "runs" / "boot.jsonl",
            {
                "kind": "project_bootstrap",
                "project": project_key,
                "title": meta["title"],
                "primary_metric": meta["primary_metric"],
                "promotion_mode": meta["promotion_mode"],
            },
        )
