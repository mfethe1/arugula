from __future__ import annotations

from pathlib import Path

from .ledger import append_jsonl
from .manifests import ensure_foundation, list_project_manifests
from .templates import install_templates


def bootstrap(root: Path) -> None:
    ensure_foundation(root)
    written = install_templates(root)

    for project_key, meta in list_project_manifests(root):
        append_jsonl(
            root / "runs" / "boot.jsonl",
            {
                "kind": "project_bootstrap",
                "project": project_key,
                "title": meta.get("title", project_key),
                "primary_metric": meta.get("primary_metric", "unknown"),
                "promotion_ladder": meta.get("promotion_ladder", []),
            },
        )

    append_jsonl(
        root / "runs" / "boot.jsonl",
        {
            "kind": "foundation_templates",
            "written": written,
        },
    )
