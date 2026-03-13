from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .evidence import attach_evidence
from .ledger import append_jsonl
from .manifests import load_manifest, resolve_experiment_path
from .nats import NatsBus


@dataclass
class ReplayResult:
    project: str
    experiment_id: str
    experiment_path: str
    status: str
    verify_command: str
    verify_exit_code: int | None
    verify_stdout: str
    verify_stderr: str
    replay_id: str


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_verify(command: str, cwd: Path, timeout: int) -> subprocess.CompletedProcess[str] | None:
    if not command:
        return None
    try:
        return subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=stdout,
            stderr=(stderr + f"\n[timeout] command exceeded {timeout}s").strip(),
        )


def run_replay(root: Path, project: str, experiment: str, verify: str = "", timeout: int = 600) -> ReplayResult:
    path = resolve_experiment_path(root, project, experiment)
    manifest = load_manifest(path)
    experiment_id = manifest["experiment_id"]
    verify_command = verify or str(manifest.get("verify_command", "")).strip()
    replay_id = f"{project}-{experiment_id}-{_ts()}"

    bus = NatsBus(root)
    bus.publish(
        f"arugula.run.{project}.started",
        {
            "project": project,
            "experiment_id": experiment_id,
            "replay_id": replay_id,
            "mode": "replay",
            "manifest_path": str(path.relative_to(root)),
        },
    )

    verify_res = _run_verify(verify_command, root, timeout) if verify_command else None
    status = "completed" if (verify_res is None or verify_res.returncode == 0) else "failed"

    result = ReplayResult(
        project=project,
        experiment_id=experiment_id,
        experiment_path=str(path.relative_to(root)),
        status=status,
        verify_command=verify_command,
        verify_exit_code=None if verify_res is None else verify_res.returncode,
        verify_stdout="" if verify_res is None else verify_res.stdout[-12000:],
        verify_stderr="" if verify_res is None else verify_res.stderr[-8000:],
        replay_id=replay_id,
    )

    append_jsonl(
        root / "runs" / "replay" / f"{project}.jsonl",
        result.__dict__,
    )
    append_jsonl(
        root / "runs" / f"score-{project}.jsonl",
        {
            "project": project,
            "agent_id": "replay-runner",
            "layer": "evaluation",
            "primary_score": 1.0 if status == "completed" else 0.0,
            "samples": 1,
            "weight": 1.0,
            "secondary_scores": {
                "verify_exit_code": result.verify_exit_code,
            },
            "notes": f"Replay result for {experiment_id}",
        },
    )
    attach_evidence(
        root,
        project=project,
        experiment_id=experiment_id,
        kind="replay_log",
        uri=f"runs/replay/{project}.jsonl",
        note=f"Replay {status} for {experiment_id}",
        metadata={"replay_id": replay_id, "verify_exit_code": result.verify_exit_code},
    )
    bus.publish(
        f"arugula.run.{project}.completed",
        {
            "project": project,
            "experiment_id": experiment_id,
            "replay_id": replay_id,
            "status": status,
            "verify_exit_code": result.verify_exit_code,
        },
    )
    return result
