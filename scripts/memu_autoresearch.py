#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://api-production-86f5.up.railway.app"
DEFAULT_API_KEY_FILE = Path("/home/michael-fethe/.openclaw/secrets/memu_api_key")


@dataclass
class ProbeResult:
    method: str
    path: str
    ok: bool
    status: int | None
    latency_ms: float
    payload: dict[str, Any] | list[Any] | str | None
    error: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_api_key(explicit: str | None, api_key_file: Path | None) -> str:
    if explicit:
        return explicit.strip()
    env_key = os.getenv("MEMU_API_KEY") or os.getenv("JIRAFLOW_API_KEY")
    if env_key:
        return env_key.strip()
    if api_key_file and api_key_file.exists():
        return api_key_file.read_text(encoding="utf-8").strip()
    raise SystemExit(
        "memU API key not found. Set MEMU_API_KEY/JIRAFLOW_API_KEY or provide --api-key-file."
    )


def _decode_response(body: bytes) -> dict[str, Any] | list[Any] | str | None:
    if not body:
        return None
    text = body.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def call_json(
    *,
    base_url: str,
    api_key: str,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    timeout: int = 20,
) -> ProbeResult:
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urlencode(query, doseq=True)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "x-api-key": api_key,
            "content-type": "application/json",
            "accept": "application/json",
        },
    )

    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = _decode_response(response.read())
            return ProbeResult(
                method=method,
                path=path,
                ok=True,
                status=response.status,
                latency_ms=(time.perf_counter() - started) * 1000,
                payload=payload,
            )
    except HTTPError as exc:
        payload = _decode_response(exc.read())
        return ProbeResult(
            method=method,
            path=path,
            ok=False,
            status=exc.code,
            latency_ms=(time.perf_counter() - started) * 1000,
            payload=payload,
            error=f"HTTP {exc.code}",
        )
    except URLError as exc:
        return ProbeResult(
            method=method,
            path=path,
            ok=False,
            status=None,
            latency_ms=(time.perf_counter() - started) * 1000,
            payload=None,
            error=str(exc.reason),
        )


def format_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def extract_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        results = payload.get("results") or payload.get("memories") or []
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]
    return []


def build_recommendations(objective: str, recall_found: bool, duplicate_count: int) -> list[str]:
    recommendations: list[str] = []
    if duplicate_count >= 2:
        recommendations.append(
            "Formation is currently append-only for identical payloads. Add duplicate suppression or content hashing before promotion."
        )
    else:
        recommendations.append(
            "Duplicate formation did not reproduce in this probe. Keep a canary around exact-content replays to confirm dedupe durability."
        )

    if recall_found:
        recommendations.append(
            "Write-to-read recall succeeded immediately. Track this as the minimum production proof gate before shipping retrieval changes."
        )
    else:
        recommendations.append(
            "Immediate recall failed. Treat retrieval quality as red until exact-write probes are returned reliably."
        )

    objective_lc = objective.lower()
    if "handoff" in objective_lc or "continuity" in objective_lc:
        recommendations.append(
            "Use memU metadata as the handoff packet contract now (source, agent, tags, run_id, handoff_target) and add retrieval filters around those fields."
        )
    elif "retrieval" in objective_lc or "read" in objective_lc:
        recommendations.append(
            "Next experiment should tune ranking/filters without regressing exact-write recall or latency."
        )
    elif "duplicate" in objective_lc or "stale" in objective_lc or "formation" in objective_lc:
        recommendations.append(
            "Prioritize pre-insert duplicate checks and stale-memory consolidation before touching ranking weights."
        )
    else:
        recommendations.append(
            "Keep the next loop small: one mutation surface, the same production probe packet, and explicit rollback thresholds."
        )

    return recommendations


def build_report(base_url: str, objective: str, success_metric: str, api_key: str) -> str:
    run_id = f"arugula-memu-{uuid.uuid4().hex[:12]}"
    timestamp = now_iso()

    health = call_json(base_url=base_url, api_key=api_key, method="GET", path="/api/v1/memu/health")

    recall_content = f"ARUGULA memU recall probe {run_id}"
    recall_metadata = {
        "source": "arugula",
        "agent": "ARUGULA",
        "tags": ["arugula", "autoresearch", "recall-probe", run_id],
        "ts": timestamp,
        "run_id": run_id,
    }
    recall_upsert = call_json(
        base_url=base_url,
        api_key=api_key,
        method="POST",
        path="/api/v1/memu/upsert",
        body={"content": recall_content, "metadata": recall_metadata},
    )
    recall_search = call_json(
        base_url=base_url,
        api_key=api_key,
        method="POST",
        path="/api/v1/memu/search",
        body={"query": recall_content, "k": 5},
    )

    duplicate_content = f"ARUGULA memU duplicate probe {run_id}"
    duplicate_metadata = {
        "source": "arugula",
        "agent": "ARUGULA",
        "tags": ["arugula", "autoresearch", "duplicate-probe", run_id],
        "ts": timestamp,
        "run_id": run_id,
    }
    duplicate_upsert_1 = call_json(
        base_url=base_url,
        api_key=api_key,
        method="POST",
        path="/api/v1/memu/upsert",
        body={"content": duplicate_content, "metadata": duplicate_metadata},
    )
    duplicate_upsert_2 = call_json(
        base_url=base_url,
        api_key=api_key,
        method="POST",
        path="/api/v1/memu/upsert",
        body={"content": duplicate_content, "metadata": duplicate_metadata},
    )
    duplicate_search = call_json(
        base_url=base_url,
        api_key=api_key,
        method="POST",
        path="/api/v1/memu/search",
        body={"query": duplicate_content, "k": 10},
    )

    recall_results = extract_results(recall_search.payload)
    duplicate_results = extract_results(duplicate_search.payload)

    recall_upsert_id = recall_upsert.payload.get("id") if isinstance(recall_upsert.payload, dict) else None
    recall_found = any(item.get("id") == recall_upsert_id for item in recall_results)
    recall_rank = next((idx + 1 for idx, item in enumerate(recall_results) if item.get("id") == recall_upsert_id), None)

    duplicate_ids = []
    for probe in (duplicate_upsert_1, duplicate_upsert_2):
        if isinstance(probe.payload, dict) and probe.payload.get("id") is not None:
            duplicate_ids.append(probe.payload["id"])
    exact_duplicate_results = [item for item in duplicate_results if item.get("content") == duplicate_content]
    duplicate_count = len(exact_duplicate_results)

    overall_ok = all(
        probe.ok
        for probe in [
            health,
            recall_upsert,
            recall_search,
            duplicate_upsert_1,
            duplicate_upsert_2,
            duplicate_search,
        ]
    )

    lines: list[str] = []
    lines.append(f"# {objective}")
    lines.append("")
    lines.append(f"project: memu")
    lines.append(f"metric: {success_metric}")
    lines.append(f"status: {'baseline captured against production memU contract' if overall_ok else 'baseline probe failed'}")
    lines.append(f"generated_at: {timestamp}")
    lines.append(f"base_url: {base_url}")
    lines.append(f"run_id: {run_id}")
    lines.append("")
    lines.append("## baseline summary")
    lines.append(f"- health_ok: {health.ok}")
    lines.append(f"- write_read_recall_ok: {recall_found}")
    lines.append(f"- recall_rank: {recall_rank if recall_rank is not None else 'not_found'}")
    lines.append(f"- duplicate_ids_written: {len(duplicate_ids)}")
    lines.append(f"- duplicate_results_found: {duplicate_count}")
    lines.append(f"- duplicate_formation_detected: {duplicate_count >= 2}")
    if isinstance(health.payload, dict) and health.payload.get("total_memories") is not None:
        lines.append(f"- total_memories_reported: {health.payload.get('total_memories')}")
    lines.append("")
    lines.append("## contract probes")
    for label, probe in [
        ("health", health),
        ("recall_upsert", recall_upsert),
        ("recall_search", recall_search),
        ("duplicate_upsert_1", duplicate_upsert_1),
        ("duplicate_upsert_2", duplicate_upsert_2),
        ("duplicate_search", duplicate_search),
    ]:
        lines.append(
            f"- {label}: ok={probe.ok}, status={probe.status}, latency_ms={probe.latency_ms:.1f}, path={probe.path}"
        )
        if probe.error:
            lines.append(f"  - error: {probe.error}")
    lines.append("")
    lines.append("## observations")
    if health.ok:
        lines.append(
            f"- Production health endpoint responded with {format_json(health.payload)}"
        )
    else:
        lines.append("- Production health endpoint did not satisfy the contract.")
    if recall_upsert.ok:
        lines.append(
            f"- Unique recall probe was written with id={recall_upsert_id}; exact query returned {len(recall_results)} result(s)."
        )
    else:
        lines.append("- Recall probe write failed, so write-to-read validation is incomplete.")
    if recall_found:
        lines.append(
            f"- Exact write-to-read recall succeeded immediately at rank {recall_rank}."
        )
    else:
        lines.append("- Exact write-to-read recall did not return the freshly written memory.")
    if duplicate_upsert_1.ok and duplicate_upsert_2.ok:
        lines.append(
            f"- Two identical writes produced ids {duplicate_ids}; subsequent search surfaced {duplicate_count} exact duplicate result(s)."
        )
    else:
        lines.append("- Duplicate formation probe could not complete both writes.")
    if duplicate_count >= 2:
        lines.append(
            "- Duplicate formation is reproducible under the current contract; the store is not deduping exact repeated content on write."
        )
    else:
        lines.append("- Duplicate formation was not observed in this run.")
    lines.append("")
    lines.append("## raw payload snapshots")
    lines.append("### health")
    lines.append("```json")
    lines.append(format_json(health.payload))
    lines.append("```")
    lines.append("")
    lines.append("### recall_search")
    lines.append("```json")
    lines.append(format_json(recall_search.payload))
    lines.append("```")
    lines.append("")
    lines.append("### duplicate_search")
    lines.append("```json")
    lines.append(format_json(duplicate_search.payload))
    lines.append("```")
    lines.append("")
    lines.append("## next steps")
    for item in build_recommendations(objective, recall_found, duplicate_count):
        lines.append(f"- {item}")
    lines.append("- Keep this exact probe packet as the production proof gate for future memU ARUGULA runs.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a production memU baseline probe for ARUGULA")
    parser.add_argument("--output", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--success-metric", required=True)
    parser.add_argument("--base-url", default=os.getenv("MEMU_BASE_URL") or DEFAULT_BASE_URL)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--api-key-file", default=str(DEFAULT_API_KEY_FILE))
    args = parser.parse_args()

    api_key_file = Path(args.api_key_file) if args.api_key_file else None
    api_key = load_api_key(args.api_key, api_key_file)
    report = build_report(
        base_url=args.base_url,
        objective=args.objective,
        success_metric=args.success_metric,
        api_key=api_key,
    )

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + ("" if report.endswith("\n") else "\n"), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
