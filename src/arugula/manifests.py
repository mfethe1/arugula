from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - fallback when dependency is unavailable
    yaml = None


PROJECTS_DIR = "projects"
TEMPLATES_DIR = "templates"


def ensure_foundation(root: Path) -> None:
    for rel in [
        "runs",
        "artifacts",
        "artifacts/delivery",
        "runs/evidence",
        "runs/replay",
        "templates/projects",
        "templates/experiments",
        "templates/evidence",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)

    for rel in ["runs/.gitkeep", "artifacts/.gitkeep"]:
        (root / rel).touch(exist_ok=True)


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to load YAML manifests. Install project dependencies first."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object manifest in {path}")
    return data


def load_manifest(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix in {".yaml", ".yml", ".md"}:
        return _load_yaml(path)
    raise ValueError(f"unsupported manifest format: {path}")


def dump_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError(
                "PyYAML is required to write YAML manifests. Install project dependencies first."
            )
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return
    raise ValueError(f"unsupported manifest format: {path}")


def project_dir(root: Path, project: str) -> Path:
    return root / PROJECTS_DIR / project


def project_manifest_path(root: Path, project: str) -> Path:
    candidate = project_dir(root, project) / "manifest.json"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"missing project manifest: {candidate}")


def experiment_dir(root: Path, project: str) -> Path:
    return project_dir(root, project) / "experiments"


def resolve_experiment_path(root: Path, project: str, experiment: str) -> Path:
    provided = Path(experiment)
    if provided.exists():
        return provided.resolve()

    base = experiment_dir(root, project)
    for ext in (".yaml", ".yml", ".json"):
        candidate = base / f"{experiment}{ext}"
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"could not resolve experiment '{experiment}' for project '{project}'")


def list_project_manifests(root: Path) -> list[tuple[str, dict[str, Any]]]:
    projects_root = root / PROJECTS_DIR
    items: list[tuple[str, dict[str, Any]]] = []
    if not projects_root.exists():
        return items
    for path in sorted(projects_root.glob("*/manifest.json")):
        items.append((path.parent.name, load_manifest(path)))
    return items
