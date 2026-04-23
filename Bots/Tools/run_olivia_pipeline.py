from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Olivia-style discovery pipeline end to end.")
    parser.add_argument("--data-root", type=Path, default=Path("Data"), help="Root data directory.")
    parser.add_argument("--round-dir", type=str, required=True, help="Round directory, e.g. ROUND_2.")
    parser.add_argument("--output-dir", type=Path, default=Path("Bots/Tools/output/olivia_pipeline"), help="Pipeline output directory.")
    parser.add_argument("--markout-bars", type=str, default="5,20,50", help="Comma-separated markout horizons.")
    parser.add_argument("--lot-tolerance", type=int, default=1, help="Lot cluster tolerance.")
    parser.add_argument("--min-occurrences", type=int, default=3, help="Minimum repetitions for a lot cluster.")
    return parser


def run_step(script: Path, *args: str) -> None:
    cmd = [sys.executable, str(script), *args]
    subprocess.run(cmd, check=True)


def main() -> None:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    run_step(
        ROOT / "olivia_research" / "discover_candidates.py",
        "--data-root", str(args.data_root),
        "--round-dir", args.round_dir,
        "--output-dir", str(args.output_dir),
        "--markout-bars", args.markout_bars,
        "--lot-tolerance", str(args.lot_tolerance),
        "--min-occurrences", str(args.min_occurrences),
    )
    run_step(
        ROOT / "olivia_research" / "score_candidates.py",
        "--input-dir", str(args.output_dir),
        "--output-dir", str(args.output_dir),
    )
    run_step(
        ROOT / "olivia_research" / "validate_products.py",
        "--data-root", str(args.data_root),
        "--round-dir", args.round_dir,
        "--input-dir", str(args.output_dir),
        "--output-dir", str(args.output_dir),
    )
    run_step(
        ROOT / "olivia_research" / "generate_runtime_config.py",
        "--input", str(args.output_dir / "validated_products.json"),
        "--output", str(args.output_dir / "runtime_config.json"),
    )
    run_step(
        ROOT / "olivia_live" / "dashboard_adapter.py",
        "--input-dir", str(args.output_dir),
        "--output-dir", str(args.output_dir / "dashboard"),
    )
    print(f"Olivia pipeline finished. Artifacts in {args.output_dir}")


if __name__ == "__main__":
    main()
