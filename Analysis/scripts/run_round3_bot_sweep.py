#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLES = REPO_ROOT / "Bots" / "Round3" / "round3_calibration_samples.json"
DEFAULT_DATASET = REPO_ROOT / "Data" / "ROUND_3"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "Analysis" / "output" / "round3_all_bots_sweep"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Round 3 Rust backtester across a bot family, then rank the results "
            "with the calibrated official-log selector."
        )
    )
    parser.add_argument(
        "--bot",
        action="append",
        default=[],
        help=(
            "Bot filename or path. Can be passed multiple times. "
            "If omitted, all Bots/Round3/TradervR3_*.py files are used."
        ),
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET),
        help="Round 3 dataset directory.",
    )
    parser.add_argument(
        "--samples",
        default=str(DEFAULT_SAMPLES),
        help="Calibration sample JSON file.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where sweep outputs should be written.",
    )
    return parser.parse_args()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bot_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"TradervR3_(\d+)", path.name)
    if match:
        return int(match.group(1)), path.name
    return 10**9, path.name


def discover_bots(bot_args: Sequence[str]) -> List[Path]:
    if bot_args:
        bots = []
        for bot_arg in bot_args:
            candidate = Path(bot_arg)
            if candidate.exists():
                bots.append(candidate.resolve())
                continue
            alt = (REPO_ROOT / bot_arg).resolve()
            if alt.exists():
                bots.append(alt)
                continue
            raise FileNotFoundError(f"Bot not found: {bot_arg}")
        return sorted(dict.fromkeys(bots), key=bot_sort_key)

    default_bots = sorted((REPO_ROOT / "Bots" / "Round3").glob("TradervR3_*.py"), key=bot_sort_key)
    if not default_bots:
        raise FileNotFoundError("No Round 3 bots found under Bots/Round3")
    return default_bots


def top_products(candidate: Dict[str, Any], limit: int = 6) -> List[Dict[str, Any]]:
    ranked = sorted(
        candidate["by_product"].items(),
        key=lambda item: abs(float(item[1]["calibrated_contribution"])),
        reverse=True,
    )
    rows: List[Dict[str, Any]] = []
    for product, row in ranked[:limit]:
        rows.append(
            {
                "product": product,
                "local_pnl": float(row["local_pnl"]),
                "weight": float(row["weight"]),
                "calibrated_contribution": float(row["calibrated_contribution"]),
            }
        )
    return rows


def render_report(
    samples: Sequence[Any],
    product_stats: Dict[str, dict],
    results: Sequence[Dict[str, Any]],
) -> str:
    lines: List[str] = []
    lines.append("# Round 3 Bot Sweep")
    lines.append("")
    lines.append("This report reruns the Round 3 bots through the Rust backtester and ranks them with the official-log calibration layer.")
    lines.append("")
    lines.append("## Calibration Samples")
    lines.append("")
    lines.append("| Label | Local total | Official total |")
    lines.append("|---|---:|---:|")
    for sample in samples:
        lines.append(f"| {sample.label} | {sample.local_total:.2f} | {sample.online_total:.2f} |")
    lines.append("")
    lines.append("## Product Reliability")
    lines.append("")
    lines.append("| Product | Class | Weight | Agreement |")
    lines.append("|---|---|---:|---:|")
    for product, stat in sorted(product_stats.items()):
        lines.append(
            f"| {product} | {stat['class']} | {float(stat['score_weight']):.2f} | {float(stat['agreement_rate']):.2f} |"
        )
    lines.append("")
    lines.append("## Bot Ranking")
    lines.append("")
    lines.append("| Rank | Bot | Raw local total | Calibrated total |")
    lines.append("|---:|---|---:|---:|")
    ranked_results = sorted(results, key=lambda item: float(item["calibrated_total"]), reverse=True)
    for rank, row in enumerate(ranked_results, start=1):
        lines.append(
            f"| {rank} | {row['bot']} | {float(row['raw_total']):.2f} | {float(row['calibrated_total']):.2f} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- The calibrated total is a selector, not a hidden-book reconstruction.")
    lines.append("- If raw and calibrated rankings disagree, prefer the calibrated ordering until more official logs arrive.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    wrapper = load_module(
        "run_round3_calibrated_backtest_module",
        REPO_ROOT / "Analysis" / "scripts" / "run_round3_calibrated_backtest.py",
    )
    calibration = load_module(
        "round3_backtest_calibration_module",
        REPO_ROOT / "Analysis" / "scripts" / "round3_backtest_calibration.py",
    )

    bots = discover_bots(args.bot)
    sample_specs = wrapper.load_sample_specs(Path(args.samples).resolve())
    samples = calibration.load_samples(sample_specs)
    product_stats = calibration.build_product_stats(samples)

    calibrated_runs_root = output_root / "calibrated_runs"
    calibrated_runs_root.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    for bot_path in bots:
        metrics_path, raw_stdout = wrapper.run_local_backtest(bot_path, Path(args.dataset).resolve())
        candidate = calibration.score_candidate(bot_path.stem, metrics_path, product_stats)
        payload = {
            "candidate": candidate,
            "samples": [
                {
                    "label": sample.label,
                    "local_total": sample.local_total,
                    "online_total": sample.online_total,
                    "local_metrics_path": str(sample.local_metrics_path),
                    "official_log_path": str(sample.official_log_path),
                }
                for sample in samples
            ],
            "product_stats": product_stats,
        }
        markdown = calibration.render_markdown(samples, product_stats, [candidate])
        out_dir = wrapper.write_outputs(
            calibrated_runs_root,
            bot_path.stem,
            metrics_path,
            raw_stdout,
            markdown,
            payload,
        )
        results.append(
            {
                "bot": bot_path.name,
                "metrics_path": str(metrics_path),
                "raw_total": float(candidate["raw_total"]),
                "calibrated_total": float(candidate["calibrated_total"]),
                "output_dir": str(out_dir),
                "top_products": top_products(candidate),
            }
        )
        print(f"[done] {bot_path.name}: raw={candidate['raw_total']:.2f}, calibrated={candidate['calibrated_total']:.2f}")

    summary_path = output_root / "summary.json"
    report_path = output_root / "report.md"
    summary_path.write_text(json.dumps(results, indent=2) + "\n")
    report_path.write_text(render_report(samples, product_stats, results))

    print("")
    print(f"summary: {summary_path}")
    print(f"report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
