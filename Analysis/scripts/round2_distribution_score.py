#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUND2BT_ROOT = REPO_ROOT / "Round2Backtester"
if str(ROUND2BT_ROOT) not in sys.path:
    sys.path.insert(0, str(ROUND2BT_ROOT))

from round2_backtester.datamodel_bridge import resolve_bot_path
from round2_backtester.replay import BacktestConfig, run_compare_backtest


DEFAULT_DATA_ROOT = REPO_ROOT / "Data" / "ROUND_2"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "Analysis" / "output" / "round2_distribution_score"


def summarize(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "mean": statistics.mean(values),
        "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "min": ordered[0],
        "max": ordered[-1],
        "p25": ordered[max(0, int(0.25 * (len(ordered) - 1)))],
        "p10": ordered[max(0, int(0.10 * (len(ordered) - 1)))],
    }


def robust_score(stats: dict[str, float], lam: float) -> float:
    return stats["mean"] - lam * stats["std"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Round 2 bots by repeated-run distribution.")
    parser.add_argument("bots", nargs="+", help="Bot paths or names.")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--queue-model", choices=("conservative", "touch_join"), default="conservative")
    parser.add_argument("--access-seed", type=int, default=7)
    parser.add_argument("--access-seeds", type=int, default=7)
    parser.add_argument("--extra-quote-ratio", type=float, default=0.25)
    parser.add_argument("--markout-horizon", type=int, default=5)
    parser.add_argument("--lambda-std", type=float, default=0.5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for bot in args.bots:
        bot_path = resolve_bot_path(bot)
        output_dir = output_root / bot_path.stem
        cfg = BacktestConfig(
            bot_path=bot_path,
            data_root=Path(args.data_root).resolve(),
            output_dir=output_dir,
            day=None,
            mode="compare",
            queue_model=args.queue_model,
            access_seed=args.access_seed,
            access_seeds=args.access_seeds,
            extra_quote_ratio=args.extra_quote_ratio,
            markout_horizon_steps=args.markout_horizon,
        )
        summary = run_compare_backtest(cfg)
        access_totals = [float(run["total_pnl"]) for run in summary["access_runs"]]
        access_stats = summarize(access_totals)
        delta_stats = summarize([float(v) for v in summary["delta_access_values"]])
        entry = {
            "bot": str(bot_path),
            "bot_name": bot_path.stem,
            "baseline_no_access_pnl": float(summary["baseline_no_access_pnl"]),
            "access_total_stats": access_stats,
            "delta_stats": delta_stats,
            "access_total_robust_score": robust_score(access_stats, args.lambda_std),
            "delta_robust_score": robust_score(delta_stats, args.lambda_std),
            "summary_path": str((output_dir / "compare_summary.json").resolve()),
        }
        results.append(entry)

    results.sort(key=lambda item: item["access_total_robust_score"], reverse=True)

    json_path = output_root / "distribution_score.json"
    json_path.write_text(json.dumps(results, indent=2) + "\n")

    lines: list[str] = []
    lines.append("# Round 2 Distribution Score")
    lines.append("")
    lines.append(f"Queue model: `{args.queue_model}`")
    lines.append(f"Access seeds: `{args.access_seed}` to `{args.access_seed + args.access_seeds - 1}`")
    lines.append(f"Robust score: `mean - {args.lambda_std:.2f} * std`")
    lines.append("")
    for row in results:
        total = row["access_total_stats"]
        delta = row["delta_stats"]
        lines.append(f"## `{row['bot_name']}`")
        lines.append("")
        lines.append(f"- baseline no-access: `{row['baseline_no_access_pnl']:.1f}`")
        lines.append(f"- access total mean/std: `{total['mean']:.1f} / {total['std']:.1f}`")
        lines.append(f"- access total p25/p10: `{total['p25']:.1f} / {total['p10']:.1f}`")
        lines.append(f"- access total robust score: `{row['access_total_robust_score']:.1f}`")
        lines.append(f"- access delta mean/std: `{delta['mean']:.1f} / {delta['std']:.1f}`")
        lines.append(f"- access delta p25/p10: `{delta['p25']:.1f} / {delta['p10']:.1f}`")
        lines.append(f"- access delta robust score: `{row['delta_robust_score']:.1f}`")
        lines.append(f"- summary: [{row['bot_name']} summary]({row['summary_path']})")
        lines.append("")

    md_path = output_root / "distribution_score.md"
    md_path.write_text("\n".join(lines) + "\n")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
