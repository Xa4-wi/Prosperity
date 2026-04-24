#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = REPO_ROOT / "Data" / "ROUND_3"
DEFAULT_SAMPLES = REPO_ROOT / "Bots" / "Round3" / "round3_calibration_samples.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "Analysis" / "output" / "round3_calibrated_backtests"
DEFAULT_TARGET_DIR = Path("/tmp/rust_backtester_target_r3_calibrated")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Round 3 Rust backtester, then immediately score the result with the "
            "official-log calibration layer so raw and calibrated rankings are shown together."
        )
    )
    parser.add_argument("bot", help="Bot filename or absolute/relative path.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Round 3 dataset directory.")
    parser.add_argument(
        "--samples",
        default=str(DEFAULT_SAMPLES),
        help="JSON file containing labeled calibration samples.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where calibrated reports should be written.",
    )
    parser.add_argument(
        "--skip-backtest",
        action="store_true",
        help="Skip the Rust replay and only run calibration on --metrics.",
    )
    parser.add_argument(
        "--metrics",
        default="",
        help="Optional metrics.json path when using --skip-backtest, or to override the detected run output.",
    )
    return parser.parse_args()


def load_calibration_module():
    module_path = REPO_ROOT / "Analysis" / "scripts" / "round3_backtest_calibration.py"
    spec = importlib.util.spec_from_file_location("round3_backtest_calibration", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load calibration module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.load_samples, module.build_product_stats, module.score_candidate, module.render_markdown


def load_sample_specs(path: Path) -> List[List[str]]:
    obj = json.loads(path.read_text())
    specs = []
    for row in obj:
        specs.append(
            [
                str(row["label"]),
                str((REPO_ROOT / row["local_metrics_path"]).resolve()),
                str((REPO_ROOT / row["official_log_path"]).resolve()),
            ]
        )
    return specs


def resolve_bot_path(bot_arg: str) -> Path:
    candidate = Path(bot_arg)
    if candidate.exists():
        return candidate.resolve()
    alt = (REPO_ROOT / bot_arg).resolve()
    if alt.exists():
        return alt
    raise FileNotFoundError(f"Bot not found: {bot_arg}")


def choose_python_for_pyo3() -> str:
    preferred = REPO_ROOT / ".venv-traderfactory" / "bin" / "python3.12"
    if preferred.exists():
        return str(preferred)
    return sys.executable


def run_local_backtest(bot_path: Path, dataset: Path) -> tuple[Path, str]:
    runs_root = REPO_ROOT / "ProsperityRustBacktester" / "runs"
    before_metrics = set(runs_root.glob("backtest-*/metrics.json"))
    cmd = [
        "./scripts/cargo_local.sh",
        "run",
        "--",
        "--trader",
        str(bot_path),
        "--dataset",
        str(dataset),
        "--products",
        "full",
        "--persist",
        "--carry",
    ]
    env = os.environ.copy()
    env["PYO3_PYTHON"] = choose_python_for_pyo3()
    env["CARGO_TARGET_DIR"] = str(DEFAULT_TARGET_DIR)
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT / "ProsperityRustBacktester",
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = proc.stdout
    after_metrics = set(runs_root.glob("backtest-*/metrics.json"))
    new_metrics = sorted(after_metrics - before_metrics, key=lambda path: path.stat().st_mtime)
    if new_metrics:
        return new_metrics[-1].resolve(), stdout

    run_dir = None
    for line in stdout.splitlines():
        if "RUN_DIR" in line:
            run_dir = line.rsplit(None, 1)[-1].strip()
    if run_dir is not None:
        metrics_path = (REPO_ROOT / "ProsperityRustBacktester" / run_dir / "metrics.json").resolve()
        if metrics_path.exists():
            return metrics_path, stdout

    latest_metrics = sorted(after_metrics, key=lambda path: path.stat().st_mtime)
    if latest_metrics:
        return latest_metrics[-1].resolve(), stdout

    raise FileNotFoundError("metrics.json not found after local backtest run")


def write_outputs(
    output_root: Path,
    bot_label: str,
    metrics_path: Path,
    raw_stdout: str,
    markdown: str,
    payload: Dict[str, Any],
) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = output_root / f"{bot_label}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "raw_backtest_stdout.txt").write_text(raw_stdout)
    (out_dir / "calibrated_report.md").write_text(markdown + "\n")
    (out_dir / "calibrated_summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out_dir / "candidate_metrics_path.txt").write_text(str(metrics_path) + "\n")
    return out_dir


def main() -> int:
    args = parse_args()
    load_samples, build_product_stats, score_candidate, render_markdown = load_calibration_module()

    sample_specs = load_sample_specs(Path(args.samples).resolve())
    samples = load_samples(sample_specs)
    product_stats = build_product_stats(samples)

    raw_stdout = ""
    if args.skip_backtest:
        if not args.metrics:
            raise ValueError("--skip-backtest requires --metrics")
        metrics_path = Path(args.metrics).resolve()
        bot_path = resolve_bot_path(args.bot)
    else:
        bot_path = resolve_bot_path(args.bot)
        metrics_path, raw_stdout = run_local_backtest(bot_path, Path(args.dataset).resolve())

    candidate = score_candidate(bot_path.stem, metrics_path, product_stats)
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
    markdown = render_markdown(samples, product_stats, [candidate])
    out_dir = write_outputs(Path(args.output_root).resolve(), bot_path.stem, metrics_path, raw_stdout, markdown, payload)

    print(f"bot: {bot_path.name}")
    print(f"metrics: {metrics_path}")
    print(f"raw_local_total: {candidate['raw_total']:.2f}")
    print(f"calibrated_total: {candidate['calibrated_total']:.2f}")
    print(f"output_dir: {out_dir}")
    print("")
    print("Top product contributions:")
    ranked = sorted(
        candidate["by_product"].items(),
        key=lambda item: abs(float(item[1]["calibrated_contribution"])),
        reverse=True,
    )
    for product, row in ranked[:8]:
        print(
            f"- {product}: local={float(row['local_pnl']):.2f}, "
            f"weight={float(row['weight']):.2f}, calibrated={float(row['calibrated_contribution']):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
