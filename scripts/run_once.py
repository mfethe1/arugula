#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_project_specific(project: str, pending: dict) -> str | None:
    runner_map = {
        'trading': (ROOT / 'scripts' / 'trading_autoresearch.py', ['--output', pending['artifactPath']]),
        'memu': (
            ROOT / 'scripts' / 'memu_autoresearch.py',
            [
                '--output', pending['artifactPath'],
                '--objective', pending['objective'],
                '--success-metric', pending['successMetric'],
            ],
        ),
    }

    runner_info = runner_map.get(project)
    if runner_info is None:
        return None

    runner, extra_args = runner_info
    if not runner.exists():
        return None

    artifact = ROOT / pending['artifactPath']
    artifact.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ['python3', str(runner), *extra_args],
        check=True,
        cwd=str(ROOT),
    )
    return str(artifact)


def main():
    parser = argparse.ArgumentParser(description='Run one lightweight ARUGULA pass for a project')
    parser.add_argument('--project', required=True)
    args = parser.parse_args()

    project_dir = ROOT / 'projects' / args.project
    queue_path = project_dir / 'queue.json'
    queue = json.loads(queue_path.read_text())
    pending = next((i for i in queue['items'] if i['status'] == 'pending'), None)
    if not pending:
        print('no pending items')
        return

    pending['status'] = 'running'
    pending['updatedAt'] = now_iso()
    queue_path.write_text(json.dumps(queue, indent=2) + '\n')

    artifact_path = run_project_specific(args.project, pending)
    if artifact_path is None:
        artifact = ROOT / pending['artifactPath']
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            f"# {pending['objective']}\n\n"
            f"project: {args.project}\n"
            f"metric: {pending['successMetric']}\n"
            f"status: seeded analysis packet\n"
            f"generated_at: {now_iso()}\n\n"
            "## next steps\n"
            "- collect current baseline\n"
            "- define exact canary and rollback rule\n"
            "- split into implementation-ready tasks\n"
        )
        artifact_path = str(artifact)

    pending['status'] = 'completed'
    pending['updatedAt'] = now_iso()
    pending['notes'] = (pending.get('notes', '') + ' | run_once generated baseline packet').strip(' |')
    queue_path.write_text(json.dumps(queue, indent=2) + '\n')

    ledger = project_dir / 'experiments.tsv'
    with ledger.open('a', encoding='utf-8') as f:
        f.write('\t'.join([
            pending['id'], pending['createdAt'], pending['updatedAt'], pending['status'], pending['priority'],
            pending['objective'], pending['successMetric'], pending['artifactPath'], pending['owner'], pending['sourceReport'], pending.get('notes', '')
        ]) + '\n')

    print(artifact_path)


if __name__ == '__main__':
    main()
