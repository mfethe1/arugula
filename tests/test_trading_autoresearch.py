import json
from pathlib import Path

from arugula.trading_autoresearch import build_trading_baseline


def _write_session(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_build_trading_baseline_creates_dataset_and_scorecard(tmp_path: Path) -> None:
    source = tmp_path / "paper_trading"
    source.mkdir()

    _write_session(
        source / "SESSION-1.json",
        {
            "session_id": "s1",
            "signals": [{}, {}],
            "analysis": [{"ticker": "QQQ"}, {"ticker": "SPY"}],
            "approved": [
                {"ticker": "QQQ", "risk_reward_ratio": 2.0, "conviction": 0.8}
            ],
            "rejected": [
                {"ticker": "SPY", "reasons": ["R/R ratio 1.1 below minimum 1.5"]}
            ],
            "executed": [{"ticker": "QQQ"}],
        },
    )
    _write_session(
        source / "SESSION-2.json",
        {
            "session_id": "s2",
            "signals": [{}],
            "analysis": [{"ticker": "IWM"}],
            "approved": [],
            "rejected": [
                {"ticker": "IWM", "reasons": ["Conviction below threshold"]}
            ],
            "executed": [],
        },
    )

    result = build_trading_baseline(tmp_path, source_dir=str(source))

    assert result.sessions == 2
    assert result.total_signals == 3
    assert result.total_analysis == 3
    assert result.total_approved == 1
    assert result.total_rejected == 2
    assert result.total_executed == 1

    dataset = json.loads((tmp_path / result.dataset_path).read_text(encoding="utf-8"))
    assert dataset["aggregates"]["avg_approved_rr"] == 2.0
    assert dataset["aggregates"]["top_rejection_reasons"][0][0] in {
        "Conviction below threshold",
        "R/R ratio 1.1 below minimum 1.5",
    }

    scorecard = json.loads((tmp_path / result.scorecard_path).read_text(encoding="utf-8"))
    assert scorecard["project"] == "trading"
    assert len(scorecard["records"]) == 3
    assert scorecard["records"][0]["agent_id"] == "specialist-scouts"
