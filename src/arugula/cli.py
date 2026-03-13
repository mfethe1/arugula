from __future__ import annotations

import argparse
from pathlib import Path

from .bootstrap import bootstrap
from .ledger import append_jsonl
from .nats import NatsBus
from .projects import PROJECTS


def cmd_init(root: Path) -> None:
    bootstrap(root)
    print(f"initialized ARUGULA at {root}")


def cmd_list_projects() -> None:
    for key, meta in PROJECTS.items():
        print(f"{key}	{meta['title']}	{meta['primary_metric']}")


def cmd_propose(project: str, title: str, mutation_target: str, root: Path) -> None:
    if project not in PROJECTS:
        raise SystemExit(f"unknown project: {project}")
    bus = NatsBus(root)
    payload = {
        'project': project,
        'title': title,
        'mutation_target': mutation_target,
        'primary_metric': PROJECTS[project]['primary_metric'],
        'promotion_mode': PROJECTS[project]['promotion_mode'],
    }
    print(bus.publish_json(f'arugula.mutation.{project}.proposed', payload))


def cmd_start(project: str, experiment: str, root: Path) -> None:
    if project not in PROJECTS:
        raise SystemExit(f"unknown project: {project}")
    bus = NatsBus(root)
    payload = {'project': project, 'experiment': experiment, 'status': 'started'}
    print(bus.publish_json(f'arugula.run.{project}.started', payload))


def cmd_score(project: str, score: float, component: str, layer: str, samples: int, root: Path) -> None:
    if project not in PROJECTS:
        raise SystemExit(f"unknown project: {project}")
    payload = {
        'project': project,
        'agent_id': component,
        'layer': layer,
        'primary_score': score,
        'samples': samples,
        'weight': 1.0,
    }
    append_jsonl(root / 'runs' / f'score-{project}.jsonl', payload)
    print(f"scored {project}:{component}")


def main() -> None:
    parser = argparse.ArgumentParser(description='ARUGULA evolution control plane')
    parser.add_argument('--root', default='.', help='Repo root')
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('init')
    sub.add_parser('list-projects')

    p = sub.add_parser('propose')
    p.add_argument('project')
    p.add_argument('title')
    p.add_argument('mutation_target')

    s = sub.add_parser('start')
    s.add_argument('project')
    s.add_argument('experiment')

    sc = sub.add_parser('score')
    sc.add_argument('project')
    sc.add_argument('component')
    sc.add_argument('layer')
    sc.add_argument('score', type=float)
    sc.add_argument('samples', type=int)

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.cmd == 'init':
        cmd_init(root)
    elif args.cmd == 'list-projects':
        cmd_list_projects()
    elif args.cmd == 'propose':
        cmd_propose(args.project, args.title, args.mutation_target, root)
    elif args.cmd == 'start':
        cmd_start(args.project, args.experiment, root)
    elif args.cmd == 'score':
        cmd_score(args.project, args.score, args.component, args.layer, args.samples, root)


if __name__ == '__main__':
    main()
