from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from backtester import (
    MonteCarloBacktester,
    build_fill_profile,
    discover_official_logs,
    load_round3_market_data,
    write_summary,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = REPO_ROOT / "Data" / "ROUND_3"
DEFAULT_LOGS_DIR = REPO_ROOT / "Bots" / "Round3"
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent / "output"


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monte Carlo backtester for Prosperity Round 3 bots with fill calibration from official logs."
    )
    parser.add_argument(
        "bot",
        help="Path to the Round 3 bot file to test, for example Bots/Round3/TradervR3_45.py",
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET),
        help=f"Directory holding prices_round_3_day_*.csv and trades_round_3_day_*.csv (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--days",
        nargs="*",
        type=int,
        default=None,
        help="Subset of day numbers to run, e.g. --days 0 1 2",
    )
    parser.add_argument(
        "--sims",
        type=int,
        default=64,
        help="Number of Monte Carlo execution paths to simulate (default: 64)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=28,
        help="Base RNG seed for the simulation family (default: 28)",
    )
    parser.add_argument(
        "--tick-step",
        type=int,
        default=1,
        help="Use every nth timestamp from the CSVs (default: 1)",
    )
    parser.add_argument(
        "--carry-state",
        action="store_true",
        help="Carry position and traderData across selected days instead of resetting per day.",
    )
    parser.add_argument(
        "--logs-dir",
        default=str(DEFAULT_LOGS_DIR),
        help=f"Directory containing official Round 3 logs used for fill calibration (default: {DEFAULT_LOGS_DIR})",
    )
    parser.add_argument(
        "--official-log",
        default=None,
        help="Optional specific official log to compare the Monte Carlo mean against.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Where to write summary.json/report.md/paths.csv. Defaults to a timestamped folder under the tool output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bot_path = (REPO_ROOT / args.bot).resolve() if not Path(args.bot).is_absolute() else Path(args.bot).resolve()
    dataset_dir = (REPO_ROOT / args.dataset).resolve() if not Path(args.dataset).is_absolute() else Path(args.dataset).resolve()
    logs_dir = (REPO_ROOT / args.logs_dir).resolve() if not Path(args.logs_dir).is_absolute() else Path(args.logs_dir).resolve()

    if not bot_path.exists():
        raise FileNotFoundError(f"Bot not found: {bot_path}")
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    if not logs_dir.exists():
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")

    official_log = None
    if args.official_log:
        official_log = (
            (REPO_ROOT / args.official_log).resolve()
            if not Path(args.official_log).is_absolute()
            else Path(args.official_log).resolve()
        )
        if not official_log.exists():
            raise FileNotFoundError(f"Official log not found: {official_log}")

    market = load_round3_market_data(
        dataset_dir=dataset_dir,
        days=args.days,
        tick_step=args.tick_step,
    )
    log_paths = discover_official_logs(logs_dir)
    fill_profile = build_fill_profile(log_paths, market)
    backtester = MonteCarloBacktester(market=market, fill_profile=fill_profile)
    run_days = args.days if args.days is not None else market.days
    summary = backtester.run(
        bot_path=bot_path,
        days=run_days,
        simulations=args.sims,
        base_seed=args.seed,
        carry_state=args.carry_state,
        compare_log=official_log,
    )

    if args.output_dir:
        output_dir = (
            (REPO_ROOT / args.output_dir).resolve()
            if not Path(args.output_dir).is_absolute()
            else Path(args.output_dir).resolve()
        )
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_ROOT / f"{bot_path.stem}_{timestamp}"
    write_summary(output_dir, summary)

    print(f"Bot: {display_path(bot_path)}")
    print(f"Dataset: {display_path(dataset_dir)}")
    print(f"Calibrated from logs: {len(log_paths)}")
    print(f"Days: {run_days}")
    print(f"Simulations: {args.sims}")
    print(f"Mean total PnL: {summary.mean_total:.2f}")
    print(f"Median total PnL: {summary.median_total:.2f}")
    print(f"P05 / P95: {summary.p05_total:.2f} / {summary.p95_total:.2f}")
    if summary.compared_log:
        print(f"Official total: {summary.compared_log['total_pnl']:.2f}")
        print(f"Official - MC mean: {summary.compared_log['delta_vs_mc_mean']:.2f}")
    print(f"Output: {display_path(output_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
