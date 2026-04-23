from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "Data"
DEFAULT_INTEL = REPO_ROOT / "Bots" / "Research" / "COMPETITIVE_INTEL.md"
DEFAULT_OUTPUT_ROOT = TOOL_DIR / "output"
DEFAULT_LOG_ROOT = TOOL_DIR / "logs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the product diagnoser end-to-end and build a dashboard.")
    parser.add_argument("--root", type=Path, default=DEFAULT_DATA_ROOT, help="Directory to scan for CSV files.")
    parser.add_argument("--intel-md", type=Path, default=DEFAULT_INTEL, help="Competitive intel markdown file.")
    parser.add_argument("--run-name", type=str, default=None, help="Optional stable run name.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Where run outputs should be stored.")
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT, help="Where run logs should be stored.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_name = args.run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = args.output_root / run_name
    dashboard_dir = run_dir / "dashboard"
    args.log_root.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    report_md = run_dir / "capsule_product_diagnosis_report.md"
    summary_json = run_dir / "capsule_product_diagnosis_summary.json"
    log_path = args.log_root / f"{run_name}.log"

    diag_cmd = [
        sys.executable,
        str(TOOL_DIR / "capsule_product_diagnoser.py"),
        "--root", str(args.root),
        "--intel-md", str(args.intel_md),
        "--out-md", str(report_md),
        "--out-json", str(summary_json),
    ]
    dash_cmd = [
        sys.executable,
        str(TOOL_DIR / "build_dashboard.py"),
        "--summary-json", str(summary_json),
        "--output-dir", str(dashboard_dir),
    ]

    with log_path.open("w") as handle:
        handle.write(f"run_name={run_name}\n")
        handle.write(f"root={args.root}\n")
        handle.write(f"intel_md={args.intel_md}\n")
        handle.write(f"report_md={report_md}\n")
        handle.write(f"summary_json={summary_json}\n")
        handle.write(f"dashboard_dir={dashboard_dir}\n\n")

        handle.write(">>> Diagnoser command\n")
        handle.write(" ".join(diag_cmd) + "\n")
        subprocess.run(diag_cmd, check=True, cwd=REPO_ROOT, stdout=handle, stderr=handle)

        handle.write("\n>>> Dashboard command\n")
        handle.write(" ".join(dash_cmd) + "\n")
        subprocess.run(dash_cmd, check=True, cwd=REPO_ROOT, stdout=handle, stderr=handle)

    latest_dir = args.output_root / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    (latest_dir / "LATEST_RUN.txt").write_text(run_name)

    print(f"Run complete: {run_name}")
    print(f"Report: {report_md}")
    print(f"Summary: {summary_json}")
    print(f"Dashboard: {dashboard_dir / 'index.html'}")
    print(f"Log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
