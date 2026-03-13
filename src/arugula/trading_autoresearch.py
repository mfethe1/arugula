from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import attach_evidence
from .ledger import append_jsonl
from .nats import NatsBus


@dataclass
class TradingBaselineResult:
    sessions: int
    total_signals: int
    total_analysis: int
    total_approved: int
    total_rejected: int
    total_executed: int
    scorecard_path: str
    dataset_path: str


DEFAULT_PAPER_TRADING_DIR = Path("../trading-agents/paper_trading")


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_session(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _paper_trading_dir(root: Path, source_dir: str | None) -> Path:
    if source_dir:
        path = Path(source_dir)
        return path if path.is_absolute() else (root / path).resolve()
    return (root / DEFAULT_PAPER_TRADING_DIR).resolve()


def _infer_rr(item: dict[str, Any]) -> float | None:
    explicit = _safe_float(item.get("risk_reward_ratio"))
    if explicit is not None:
        return explicit
    entry = _safe_float(item.get("entry_target"))
    stop = _safe_float(item.get("stop_loss"))
    target = _safe_float(item.get("profit_target"))
    if entry is None or stop is None or target is None:
        return None
    risk = abs(entry - stop)
    reward = abs(target - entry)
    if risk <= 0:
        return None
    return reward / risk


def _session_summary(session: dict[str, Any], session_path: Path) -> dict[str, Any]:
    approved = session.get("approved", [])
    rejected = session.get("rejected", [])
    analysis = session.get("analysis", [])
    executed = session.get("executed", [])

    approved_rr = [rr for rr in (_infer_rr(item) for item in approved) if rr is not None]
    approved_conviction = [
        c
        for c in (_safe_float(item.get("conviction")) for item in approved)
        if c is not None
    ]

    rejection_reasons: dict[str, int] = {}
    for item in rejected:
        for reason in item.get("reasons", []):
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    return {
        "session_id": session.get("session_id", session_path.stem),
        "source_file": str(session_path),
        "started_at": session.get("started_at"),
        "signals": len(session.get("signals", [])),
        "analysis": len(analysis),
        "approved": len(approved),
        "rejected": len(rejected),
        "executed": len(executed),
        "approval_rate": (len(approved) / len(analysis)) if analysis else 0.0,
        "execution_rate": (len(executed) / len(approved)) if approved else 0.0,
        "avg_approved_rr": _mean(approved_rr),
        "avg_approved_conviction": _mean(approved_conviction),
        "rejection_reasons": rejection_reasons,
    }


def build_trading_baseline(
    root: Path,
    *,
    experiment_id: str = "trading-exp-002",
    source_dir: str | None = None,
) -> TradingBaselineResult:
    source = _paper_trading_dir(root, source_dir)
    session_paths = sorted(source.glob("SESSION-*.json"))
    if not session_paths:
        raise FileNotFoundError(f"no paper-trading sessions found in {source}")

    sessions = [_load_session(path) for path in session_paths]
    summaries = [_session_summary(session, path) for session, path in zip(sessions, session_paths)]

    total_signals = sum(item["signals"] for item in summaries)
    total_analysis = sum(item["analysis"] for item in summaries)
    total_approved = sum(item["approved"] for item in summaries)
    total_rejected = sum(item["rejected"] for item in summaries)
    total_executed = sum(item["executed"] for item in summaries)

    avg_approval_rate = _mean([item["approval_rate"] for item in summaries])
    avg_execution_rate = _mean([item["execution_rate"] for item in summaries])
    avg_approved_rr = _mean([item["avg_approved_rr"] for item in summaries if item["approved"] > 0])
    avg_approved_conviction = _mean([
        item["avg_approved_conviction"] for item in summaries if item["approved"] > 0
    ])

    rejection_totals: dict[str, int] = {}
    for item in summaries:
        for reason, count in item["rejection_reasons"].items():
            rejection_totals[reason] = rejection_totals.get(reason, 0) + count

    dataset = {
        "project": "trading",
        "experiment_id": experiment_id,
        "source_dir": str(source),
        "sessions": summaries,
        "aggregates": {
            "sessions": len(summaries),
            "total_signals": total_signals,
            "total_analysis": total_analysis,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "total_executed": total_executed,
            "avg_approval_rate": avg_approval_rate,
            "avg_execution_rate": avg_execution_rate,
            "avg_approved_rr": avg_approved_rr,
            "avg_approved_conviction": avg_approved_conviction,
            "top_rejection_reasons": sorted(
                rejection_totals.items(), key=lambda item: (-item[1], item[0])
            )[:10],
        },
    }

    dataset_path = root / "artifacts" / "trading" / "replay" / "paper-trading-baseline.json"
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    scorecard = {
        "project": "trading",
        "window": "paper-trading-baseline-week0",
        "score_function": "risk_adjusted_return_composite_proxy",
        "records": [
            {
                "agent_id": "specialist-scouts",
                "layer": "specialist",
                "primary_score": round(avg_approved_conviction, 4),
                "samples": total_analysis,
                "weight": 1.0,
                "secondary_scores": {
                    "approval_rate": round(avg_approval_rate, 4),
                    "avg_approved_rr": round(avg_approved_rr, 4),
                    "total_signals": total_signals,
                },
                "notes": "Baseline specialist quality from paper-trading analysis/approval outcomes.",
            },
            {
                "agent_id": "risk-gate",
                "layer": "orchestrator",
                "primary_score": round(avg_execution_rate, 4),
                "samples": total_approved,
                "weight": 1.0,
                "secondary_scores": {
                    "rejection_rate": round((total_rejected / total_analysis), 4) if total_analysis else 0.0,
                    "top_rejection_reasons": dict(dataset["aggregates"]["top_rejection_reasons"][:5]),
                },
                "notes": "How often approved ideas made it through the review/execution gate.",
            },
            {
                "agent_id": "trading-orchestrator",
                "layer": "evaluation",
                "primary_score": round((_mean([avg_approval_rate, avg_execution_rate, min(avg_approved_rr / 2.0, 1.0)])), 4),
                "samples": len(summaries),
                "weight": 1.0,
                "secondary_scores": {
                    "approval_rate": round(avg_approval_rate, 4),
                    "execution_rate": round(avg_execution_rate, 4),
                    "avg_approved_rr": round(avg_approved_rr, 4),
                    "total_executed": total_executed,
                },
                "notes": "Week-0 proxy baseline before real PnL-linked scorecards are wired in.",
            },
        ],
    }

    scorecard_path = root / "artifacts" / "trading" / "scorecards" / "TR-week0-baseline.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(scorecard, indent=2) + "\n", encoding="utf-8")

    bus = NatsBus(root)
    bus.publish(
        "arugula.signal.trading.outcome",
        {
            "project": "trading",
            "experiment_id": experiment_id,
            "sessions": len(summaries),
            "total_analysis": total_analysis,
            "total_approved": total_approved,
            "total_executed": total_executed,
            "scorecard_path": str(scorecard_path.relative_to(root)),
            "dataset_path": str(dataset_path.relative_to(root)),
        },
    )
    append_jsonl(
        root / "runs" / "score-trading.jsonl",
        {
            "project": "trading",
            "agent_id": "paper-trading-baseline-builder",
            "layer": "evaluation",
            "primary_score": scorecard["records"][-1]["primary_score"],
            "samples": len(summaries),
            "weight": 1.0,
            "secondary_scores": scorecard["records"][-1]["secondary_scores"],
            "notes": "Generated baseline scorecard from paper-trading sessions.",
        },
    )
    attach_evidence(
        root,
        project="trading",
        experiment_id=experiment_id,
        kind="baseline_dataset",
        uri=str(dataset_path.relative_to(root)),
        note="Normalized paper-trading sessions for replay/scoring.",
    )
    attach_evidence(
        root,
        project="trading",
        experiment_id=experiment_id,
        kind="scorecard",
        uri=str(scorecard_path.relative_to(root)),
        note="Baseline trading scorecard generated from recent paper-trading sessions.",
    )

    return TradingBaselineResult(
        sessions=len(summaries),
        total_signals=total_signals,
        total_analysis=total_analysis,
        total_approved=total_approved,
        total_rejected=total_rejected,
        total_executed=total_executed,
        scorecard_path=str(scorecard_path.relative_to(root)),
        dataset_path=str(dataset_path.relative_to(root)),
    )
