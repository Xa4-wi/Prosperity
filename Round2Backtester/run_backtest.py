#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from round2_backtester.datamodel_bridge import REPO_ROOT, resolve_bot_path
from round2_backtester.dashboard_server import serve_dashboard
from round2_backtester.loaders import load_any
from round2_backtester.replay import BacktestConfig, run_compare_backtest, run_single_backtest


DEFAULT_DATA_ROOT = REPO_ROOT / "Data" / "ROUND_2"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "Round2Backtester" / "output"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Round 2 backtester and artifact loader.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest = subparsers.add_parser("backtest", help="Run the Round 2 backtester on a bot.")
    backtest.add_argument("bot", help="Bot filename or path, e.g. Trader.py or Bots/Round1/TradervR1_110.py")
    backtest.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT), help="Directory containing Round 2 CSV files.")
    backtest.add_argument("--output", default="", help="Output directory. Defaults to Round2Backtester/output/<bot_name>/")
    backtest.add_argument("--day", type=int, default=None, help="Optional single-day filter.")
    backtest.add_argument(
        "--mode",
        choices=("no_access", "access", "compare"),
        default="compare",
        help="Replay only the public book, only the augmented book, or compare both.",
    )
    backtest.add_argument(
        "--queue-model",
        choices=("conservative", "touch_join"),
        default="conservative",
        help="Passive fill model.",
    )
    backtest.add_argument("--access-seed", type=int, default=7, help="Base seed for access-mode quote generation.")
    backtest.add_argument("--access-seeds", type=int, default=5, help="Number of access seeds when mode=compare.")
    backtest.add_argument("--extra-quote-ratio", type=float, default=0.25, help="Base probability of adding access quotes.")
    backtest.add_argument("--markout-horizon", type=int, default=5, help="Future-step horizon for fill markout diagnostics.")

    inspect = subparsers.add_parser("inspect", help="Parse a CSV, run JSON, or raw submission log.")
    inspect.add_argument("path", help="Artifact path to inspect.")
    inspect.add_argument("--output", default="", help="Optional JSON output file for the parsed summary.")

    dashboard = subparsers.add_parser("dashboard", help="Serve the dashboard UI for saved backtest outputs.")
    dashboard.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory containing saved run folders. Defaults to Round2Backtester/output/",
    )
    dashboard.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    dashboard.add_argument("--port", type=int, default=8022, help="Port to bind.")
    return parser


def _default_output(bot_path: Path) -> Path:
    return DEFAULT_OUTPUT_ROOT / bot_path.stem


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "inspect":
        artifact = load_any(args.path)
        payload = {
            "kind": artifact.kind,
            "source_path": str(artifact.source_path),
            "metadata": artifact.metadata,
            "counts": artifact.counts(),
        }
        text = json.dumps(payload, indent=2)
        print(text)
        if args.output:
            Path(args.output).resolve().write_text(text + "\n")
        return 0

    if args.command == "dashboard":
        serve_dashboard(Path(args.output_root).resolve(), host=args.host, port=args.port)
        return 0

    bot_path = resolve_bot_path(args.bot)
    output_dir = Path(args.output).resolve() if args.output else _default_output(bot_path)
    config = BacktestConfig(
        bot_path=bot_path,
        data_root=Path(args.data_root).resolve(),
        output_dir=output_dir,
        day=args.day,
        mode=args.mode,
        queue_model=args.queue_model,
        access_seed=args.access_seed,
        access_seeds=args.access_seeds,
        extra_quote_ratio=args.extra_quote_ratio,
        markout_horizon_steps=args.markout_horizon,
    )

    if args.mode == "compare":
        summary = run_compare_backtest(config)
        print(json.dumps(summary, indent=2))
        return 0

    payload = run_single_backtest(config)
    print(json.dumps(payload["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
