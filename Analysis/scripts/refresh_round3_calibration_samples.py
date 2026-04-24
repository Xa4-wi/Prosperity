#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = REPO_ROOT / "Bots" / "Round3"
RUNS_ROOT = REPO_ROOT / "ProsperityRustBacktester" / "runs"
OUTPUT_PATH = LOG_ROOT / "round3_calibration_samples.json"


def main() -> int:
    latest_by_trader: dict[str, Path] = {}
    for metrics_path in RUNS_ROOT.glob("**/metrics.json"):
        try:
            obj = json.loads(metrics_path.read_text())
        except Exception:
            continue
        trader_path = str(obj.get("trader_path", ""))
        if not trader_path.startswith("Bots/Round3/TradervR3_"):
            continue
        prev = latest_by_trader.get(trader_path)
        if prev is None or metrics_path.stat().st_mtime > prev.stat().st_mtime:
            latest_by_trader[trader_path] = metrics_path

    rows = []
    for log_path in sorted(LOG_ROOT.glob("TradervR3_*.log")):
        trader_path = f"Bots/Round3/{log_path.stem}.py"
        metrics_path = latest_by_trader.get(trader_path)
        if metrics_path is None:
            continue
        rows.append(
            {
                "label": log_path.stem.replace("Traderv", ""),
                "local_metrics_path": str(metrics_path.relative_to(REPO_ROOT)),
                "official_log_path": str(log_path.relative_to(REPO_ROOT)),
            }
        )

    OUTPUT_PATH.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {len(rows)} samples to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
