from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bootstrap import bootstrap
from .delivery import render_delivery_board
from .evidence import attach_evidence
from .ledger import append_jsonl
from .manifests import list_project_manifests, load_manifest, project_manifest_path, resolve_experiment_path
from .nats import NatsBus
from .projects import PROJECTS
from .replay import run_replay
from .templates import install_templates


def cmd_init(root: Path) -> None:
    bootstrap(root)
    print(f"initialized ARUGULA at {root}")


def cmd_list_projects(root: Path) -> None:
    manifests = list_project_manifests(root)
    if manifests:
        for key, meta in manifests:
            print(f"{key}\t{meta.get('title', key)}\t{meta.get('primary_metric', 'unknown')}")
        return
    for key, meta in PROJECTS.items():
        print(f"{key}\t{meta['title']}\t{meta['primary_metric']}")


def _project_meta(root: Path, project: str) -> dict:
    if project not in PROJECTS and not (root / "projects" / project).exists():
        raise SystemExit(f"unknown project: {project}")
    try:
        return load_manifest(project_manifest_path(root, project))
    except FileNotFoundError:
        return {"project": project, **PROJECTS[project]}


def cmd_propose(project: str, title: str, mutation_target: str, root: Path, experiment: str = "") -> None:
    meta = _project_meta(root, project)
    bus = NatsBus(root)
    payload = {
        "project": project,
        "title": title,
        "mutation_target": mutation_target,
        "primary_metric": meta["primary_metric"],
        "promotion_mode": meta.get("promotion_mode", (meta.get("promotion_ladder") or ["replay"])[0]),
    }
    if experiment:
        payload["experiment_path"] = str(resolve_experiment_path(root, project, experiment).relative_to(root))
    print(bus.publish_json(f"arugula.mutation.{project}.proposed", payload))


def cmd_start(project: str, experiment: str, root: Path) -> None:
    meta = _project_meta(root, project)
    manifest_path = resolve_experiment_path(root, project, experiment)
    manifest = load_manifest(manifest_path)
    bus = NatsBus(root)
    payload = {
        "project": project,
        "experiment": manifest["experiment_id"],
        "status": "started",
        "manifest_path": str(manifest_path.relative_to(root)),
        "primary_metric": meta["primary_metric"],
    }
    print(bus.publish_json(f"arugula.run.{project}.started", payload))


def cmd_score(project: str, score: float, component: str, layer: str, samples: int, root: Path, note: str = "") -> None:
    _project_meta(root, project)
    payload = {
        "project": project,
        "agent_id": component,
        "layer": layer,
        "primary_score": score,
        "samples": samples,
        "weight": 1.0,
        "notes": note,
    }
    append_jsonl(root / "runs" / f"score-{project}.jsonl", payload)
    print(f"scored {project}:{component}")


def cmd_attach_evidence(project: str, experiment: str, kind: str, uri: str, root: Path, note: str = "") -> None:
    manifest = load_manifest(resolve_experiment_path(root, project, experiment))
    payload = attach_evidence(
        root,
        project=project,
        experiment_id=manifest["experiment_id"],
        kind=kind,
        uri=uri,
        note=note,
    )
    print(json.dumps(payload, indent=2))


def cmd_replay(project: str, experiment: str, root: Path, verify: str, timeout: int) -> None:
    result = run_replay(root, project, experiment, verify=verify, timeout=timeout)
    print(json.dumps(result.__dict__, indent=2))


def cmd_render_board(root: Path) -> None:
    board = render_delivery_board(root)
    print(json.dumps(board, indent=2))


def cmd_install_templates(root: Path) -> None:
    written = install_templates(root)
    print(json.dumps({"written": written}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="ARUGULA evolution control plane")
    parser.add_argument("--root", default=".", help="Repo root")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    lp = sub.add_parser("list-projects")
    lp.set_defaults(_needs_root=True)
    sub.add_parser("install-templates")

    p = sub.add_parser("propose")
    p.add_argument("project")
    p.add_argument("title")
    p.add_argument("mutation_target")
    p.add_argument("--experiment", default="")

    s = sub.add_parser("start")
    s.add_argument("project")
    s.add_argument("experiment")

    sc = sub.add_parser("score")
    sc.add_argument("project")
    sc.add_argument("component")
    sc.add_argument("layer")
    sc.add_argument("score", type=float)
    sc.add_argument("samples", type=int)
    sc.add_argument("--note", default="")

    ev = sub.add_parser("attach-evidence")
    ev.add_argument("project")
    ev.add_argument("experiment")
    ev.add_argument("kind")
    ev.add_argument("uri")
    ev.add_argument("--note", default="")

    rp = sub.add_parser("replay")
    rp.add_argument("project")
    rp.add_argument("experiment")
    rp.add_argument("--verify", default="")
    rp.add_argument("--timeout", type=int, default=600)

    sub.add_parser("render-board")

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.cmd == "init":
        cmd_init(root)
    elif args.cmd == "list-projects":
        cmd_list_projects(root)
    elif args.cmd == "install-templates":
        cmd_install_templates(root)
    elif args.cmd == "propose":
        cmd_propose(args.project, args.title, args.mutation_target, root, experiment=args.experiment)
    elif args.cmd == "start":
        cmd_start(args.project, args.experiment, root)
    elif args.cmd == "score":
        cmd_score(args.project, args.score, args.component, args.layer, args.samples, root, note=args.note)
    elif args.cmd == "attach-evidence":
        cmd_attach_evidence(args.project, args.experiment, args.kind, args.uri, root, note=args.note)
    elif args.cmd == "replay":
        cmd_replay(args.project, args.experiment, root, verify=args.verify, timeout=args.timeout)
    elif args.cmd == "render-board":
        cmd_render_board(root)


if __name__ == "__main__":
    main()
