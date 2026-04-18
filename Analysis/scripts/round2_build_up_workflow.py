from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[2]
BOT_DIR = ROOT / "Bots" / "Round2"
RUN_ROOT = ROOT / "TraderFactory" / "generated" / "runs" / "deterministic" / "rust"
OUTPUT_DIR = ROOT / "Analysis" / "output" / "round2_build_up_workflow"
DATA_ROOT = ROOT / "Data" / "ROUND_2"
CLI = [
    str(ROOT / ".venv-traderfactory" / "bin" / "python"),
    "-m",
    "trader_factory.cli",
    "deterministic",
]
DAYS = (-1, 0, 1)


@dataclass(frozen=True)
class StageSpec:
    key: str
    title: str
    bot_path: Path
    category: str
    parent_key: Optional[str]
    notes: str


STAGES: List[StageSpec] = [
    StageSpec(
        key="R2_12",
        title="Structural base rewrite",
        bot_path=BOT_DIR / "TradervR2_12.py",
        category="plan",
        parent_key=None,
        notes="Clean restart baseline.",
    ),
    StageSpec(
        key="R2_13",
        title="Pepper restoration",
        bot_path=BOT_DIR / "TradervR2_13.py",
        category="support",
        parent_key="R2_12",
        notes="Preparatory step outside the formal plan; restores the stronger Pepper engine.",
    ),
    StageSpec(
        key="R2_14",
        title="Step 1 - conviction",
        bot_path=BOT_DIR / "TradervR2_14.py",
        category="plan",
        parent_key="R2_13",
        notes="Adds conviction-only Osmium layer.",
    ),
    StageSpec(
        key="R2_15",
        title="Step 2 - toxicity smoothing",
        bot_path=BOT_DIR / "TradervR2_15.py",
        category="plan",
        parent_key="R2_13",
        notes="Light side-specific toxicity smoothing.",
    ),
    StageSpec(
        key="R2_16",
        title="Step 3 - reentry / neutral drip",
        bot_path=BOT_DIR / "TradervR2_16.py",
        category="plan",
        parent_key="R2_15",
        notes="Side-specific re-entry and neutral drip on top of toxicity.",
    ),
    StageSpec(
        key="R2_17",
        title="Step 4 - passive-only markout",
        bot_path=BOT_DIR / "TradervR2_17.py",
        category="plan",
        parent_key="R2_16",
        notes="Passive-only markout memory on top of re-entry.",
    ),
    StageSpec(
        key="R2_18",
        title="Exploratory - alpha split heavy",
        bot_path=BOT_DIR / "TradervR2_18.py",
        category="exploratory",
        parent_key="R2_17",
        notes="Aggressive take/quote alpha split experiment; not part of the main plan.",
    ),
    StageSpec(
        key="R2_19",
        title="Exploratory - alpha split light",
        bot_path=BOT_DIR / "TradervR2_19.py",
        category="exploratory",
        parent_key="R2_17",
        notes="Lighter take/quote alpha split experiment; not part of the main plan.",
    ),
    StageSpec(
        key="R2_18_recycler",
        title="Step 5 - recycler",
        bot_path=BOT_DIR / "TradervR2_18_recycler.py",
        category="plan_missing",
        parent_key="R2_17",
        notes="Planned but not implemented yet.",
    ),
    StageSpec(
        key="R2_19_accessaware",
        title="Step 6 - access-aware extension",
        bot_path=BOT_DIR / "TradervR2_19_accessaware.py",
        category="plan_missing",
        parent_key="R2_18_recycler",
        notes="Planned but not implemented yet.",
    ),
    StageSpec(
        key="R2_20_multisweep",
        title="Step 7 - multi-level sweep",
        bot_path=BOT_DIR / "TradervR2_20_multisweep.py",
        category="plan_missing",
        parent_key="R2_19_accessaware",
        notes="Optional later stage; not implemented yet.",
    ),
]


def run_dir_for(bot_path: Path, day: int) -> Path:
    return RUN_ROOT / f"{bot_path.stem}_day_{day}"


def metrics_path_for(bot_path: Path, day: int) -> Path:
    return run_dir_for(bot_path, day) / "metrics.json"


def submission_log_path_for(bot_path: Path, day: int) -> Path:
    return run_dir_for(bot_path, day) / "submission.log"


def should_rerun(bot_path: Path, day: int, force: bool) -> bool:
    if force:
        return True
    metrics_path = metrics_path_for(bot_path, day)
    if not metrics_path.exists():
        return True
    return metrics_path.stat().st_mtime < bot_path.stat().st_mtime


def run_deterministic(bot_path: Path, day: int, rerun: bool) -> Path:
    run_dir = run_dir_for(bot_path, day)
    if not should_rerun(bot_path, day, rerun):
        return run_dir

    cmd = [
        *CLI,
        str(bot_path.relative_to(ROOT)),
        "--day",
        str(day),
        "--data-root",
        str(DATA_ROOT.relative_to(ROOT)),
        "--dataset-tag",
        "round_2",
        "--engine",
        "rust",
    ]
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    tf_path = str((ROOT / "TraderFactory").resolve())
    env["PYTHONPATH"] = (
        f"{tf_path}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else tf_path
    )
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)
    return run_dir


def parse_activities_log(activities_log: str) -> Dict[str, List[Dict[str, float]]]:
    rows_by_symbol: Dict[str, List[Dict[str, float]]] = {}
    if not activities_log:
        return rows_by_symbol

    reader = csv.DictReader(activities_log.splitlines(), delimiter=";")
    for row in reader:
        symbol = row.get("product")
        if not symbol:
            continue
        timestamp = int(row["timestamp"])
        pnl = float(row["profit_and_loss"])
        rows_by_symbol.setdefault(symbol, []).append({"timestamp": timestamp, "pnl": pnl})
    return rows_by_symbol


def plateau_stats(points: Iterable[Dict[str, float]]) -> Dict[str, int]:
    points_list = list(points)
    if len(points_list) < 2:
        return {
            "longest_flat_bars": 0,
            "longest_flat_timestamps": 0,
            "plateau_count_ge_10": 0,
        }

    longest_flat_bars = 0
    plateau_count_ge_10 = 0
    current_flat = 0

    prev_pnl = points_list[0]["pnl"]
    for point in points_list[1:]:
        if point["pnl"] == prev_pnl:
            current_flat += 1
        else:
            if current_flat >= 10:
                plateau_count_ge_10 += 1
            longest_flat_bars = max(longest_flat_bars, current_flat)
            current_flat = 0
        prev_pnl = point["pnl"]

    if current_flat >= 10:
        plateau_count_ge_10 += 1
    longest_flat_bars = max(longest_flat_bars, current_flat)
    return {
        "longest_flat_bars": longest_flat_bars,
        "longest_flat_timestamps": longest_flat_bars * 100,
        "plateau_count_ge_10": plateau_count_ge_10,
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def analyze_stage(stage: StageSpec, rerun: bool) -> dict:
    result = {
        "key": stage.key,
        "title": stage.title,
        "category": stage.category,
        "bot_path": str(stage.bot_path.relative_to(ROOT)),
        "exists": stage.bot_path.exists(),
        "parent_key": stage.parent_key,
        "notes": stage.notes,
    }

    if not stage.bot_path.exists():
        return result

    day_results = []
    totals = {"ASH_COATED_OSMIUM": 0.0, "INTARIAN_PEPPER_ROOT": 0.0}
    total_pnl = 0.0
    plateau_summary = {
        "ASH_COATED_OSMIUM": {"longest_flat_bars": 0, "longest_flat_timestamps": 0, "plateau_count_ge_10": 0},
        "INTARIAN_PEPPER_ROOT": {"longest_flat_bars": 0, "longest_flat_timestamps": 0, "plateau_count_ge_10": 0},
    }

    for day in DAYS:
        run_dir = run_deterministic(stage.bot_path, day, rerun)
        metrics = load_json(run_dir / "metrics.json")
        submission = load_json(run_dir / "submission.log")
        activity_rows = parse_activities_log(submission.get("activitiesLog", ""))

        per_day_plateaus = {}
        for symbol, points in activity_rows.items():
            stats = plateau_stats(points)
            per_day_plateaus[symbol] = stats
            plateau_summary[symbol]["longest_flat_bars"] = max(
                plateau_summary[symbol]["longest_flat_bars"], stats["longest_flat_bars"]
            )
            plateau_summary[symbol]["longest_flat_timestamps"] = max(
                plateau_summary[symbol]["longest_flat_timestamps"], stats["longest_flat_timestamps"]
            )
            plateau_summary[symbol]["plateau_count_ge_10"] += stats["plateau_count_ge_10"]

        total_pnl += float(metrics["final_pnl_total"])
        for product, pnl in metrics["final_pnl_by_product"].items():
            totals[product] = totals.get(product, 0.0) + float(pnl)

        day_results.append(
            {
                "day": day,
                "total_pnl": float(metrics["final_pnl_total"]),
                "pnl_by_product": {k: float(v) for k, v in metrics["final_pnl_by_product"].items()},
                "own_trade_count": int(metrics.get("own_trade_count", 0)),
                "plateaus": per_day_plateaus,
                "run_dir": str(run_dir.relative_to(ROOT)),
            }
        )

    result["three_day_total"] = total_pnl
    result["split"] = totals
    result["day_results"] = day_results
    result["plateaus"] = plateau_summary
    result["supported_metrics"] = {
        "total_pnl": True,
        "product_split": True,
        "own_trade_count": True,
        "plateau_stats": True,
        "final_positions": False,
        "osmium_take_fills": False,
        "osmium_passive_fills": False,
        "toxic_flips": False,
        "reentry_events": False,
        "average_passive_markout": False,
    }
    return result


def render_table(rows: List[List[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    formatted = []
    for idx, row in enumerate(rows):
        line = "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"
        formatted.append(line)
        if idx == 0:
            formatted.append("| " + " | ".join("-" * widths[i] for i in range(len(widths))) + " |")
    return "\n".join(formatted)


def build_report(results: Dict[str, dict]) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    existing = [results[s.key] for s in STAGES if results[s.key].get("exists")]
    best_existing = max(existing, key=lambda item: item.get("three_day_total", float("-inf"))) if existing else None

    lines: List[str] = []
    lines.append("# Round 2 Build-Up Workflow Report")
    lines.append("")
    lines.append(f"Generated at: `{timestamp}`")
    lines.append("")
    lines.append("This report tracks the clean Round 2 rebuild path from the staged build-up plan, replays the available bots, and marks missing future steps so the workflow stays easy to supervise.")
    lines.append("")

    if best_existing:
        lines.append("## Current Best")
        lines.append("")
        lines.append(
            f"- Best tested branch: [`{best_existing['key']}`]({(ROOT / best_existing['bot_path']).as_posix()})"
        )
        lines.append(f"- Three-day total: `{best_existing['three_day_total']:.1f}`")
        lines.append(
            f"- Split: Ash `{best_existing['split'].get('ASH_COATED_OSMIUM', 0.0):.1f}`, Pepper `{best_existing['split'].get('INTARIAN_PEPPER_ROOT', 0.0):.1f}`"
        )
        lines.append("")

    plan_rows = [["Stage", "Bot", "Status", "Three-day total", "Delta vs parent", "Ash", "Pepper", "Ash max plateau"]]
    for stage in STAGES:
        result = results[stage.key]
        if not result.get("exists"):
            plan_rows.append(
                [stage.key, stage.bot_path.name, "missing", "-", "-", "-", "-", "-"]
            )
            continue
        parent_total = None
        if stage.parent_key and results.get(stage.parent_key, {}).get("exists"):
            parent_total = results[stage.parent_key].get("three_day_total")
        delta = (
            f"{result['three_day_total'] - parent_total:+.1f}"
            if parent_total is not None
            else "-"
        )
        ash_plateau = result["plateaus"].get("ASH_COATED_OSMIUM", {}).get("longest_flat_bars", 0)
        status = "tested"
        if stage.category == "exploratory":
            status = "exploratory"
        elif stage.category == "support":
            status = "support"
        plan_rows.append(
            [
                stage.key,
                stage.bot_path.name,
                status,
                f"{result['three_day_total']:.1f}",
                delta,
                f"{result['split'].get('ASH_COATED_OSMIUM', 0.0):.1f}",
                f"{result['split'].get('INTARIAN_PEPPER_ROOT', 0.0):.1f}",
                str(ash_plateau),
            ]
        )

    lines.append("## Stage Board")
    lines.append("")
    lines.append(render_table(plan_rows))
    lines.append("")

    lines.append("## Supported Metrics")
    lines.append("")
    lines.append("The deterministic replay artifacts currently support:")
    lines.append("- total PnL")
    lines.append("- product PnL split")
    lines.append("- total own trade count")
    lines.append("- plateau stats inferred from `activitiesLog`")
    lines.append("")
    lines.append("The workflow marks these as unavailable unless future bots emit diagnostics or the replay artifact format changes:")
    lines.append("- final positions")
    lines.append("- Osmium take/passive fill split")
    lines.append("- toxic level flips")
    lines.append("- reentry event count")
    lines.append("- average passive markout")
    lines.append("")

    lines.append("## Per-Stage Notes")
    lines.append("")
    for stage in STAGES:
        result = results[stage.key]
        lines.append(f"### {stage.key} — {stage.title}")
        lines.append("")
        lines.append(f"- File: `{stage.bot_path.relative_to(ROOT)}`")
        lines.append(f"- Notes: {stage.notes}")
        if not result.get("exists"):
            lines.append("- Status: missing")
            lines.append("")
            continue
        lines.append(f"- Three-day total: `{result['three_day_total']:.1f}`")
        lines.append(
            f"- Split: Ash `{result['split'].get('ASH_COATED_OSMIUM', 0.0):.1f}`, Pepper `{result['split'].get('INTARIAN_PEPPER_ROOT', 0.0):.1f}`"
        )
        if stage.parent_key and results.get(stage.parent_key, {}).get("exists"):
            parent_total = results[stage.parent_key]["three_day_total"]
            lines.append(f"- Delta vs `{stage.parent_key}`: `{result['three_day_total'] - parent_total:+.1f}`")
        ash_plateau = result["plateaus"].get("ASH_COATED_OSMIUM", {})
        pepper_plateau = result["plateaus"].get("INTARIAN_PEPPER_ROOT", {})
        lines.append(
            f"- Max Ash flat plateau: `{ash_plateau.get('longest_flat_bars', 0)}` bars (`{ash_plateau.get('longest_flat_timestamps', 0)}` timestamps)"
        )
        lines.append(
            f"- Max Pepper flat plateau: `{pepper_plateau.get('longest_flat_bars', 0)}` bars (`{pepper_plateau.get('longest_flat_timestamps', 0)}` timestamps)"
        )
        lines.append("- Day breakdown:")
        for day_result in result["day_results"]:
            lines.append(
                f"  - day `{day_result['day']}`: total `{day_result['total_pnl']:.1f}`, "
                f"Ash `{day_result['pnl_by_product'].get('ASH_COATED_OSMIUM', 0.0):.1f}`, "
                f"Pepper `{day_result['pnl_by_product'].get('INTARIAN_PEPPER_ROOT', 0.0):.1f}`, "
                f"own trades `{day_result['own_trade_count']}`"
            )
        lines.append("")

    missing = [stage for stage in STAGES if not results[stage.key].get("exists")]
    lines.append("## Next Gaps")
    lines.append("")
    if missing:
        for stage in missing:
            lines.append(f"- `{stage.key}` is still missing: {stage.title}")
    else:
        lines.append("- No missing stages in the registered workflow.")
    lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and summarize the Round 2 build-up workflow.")
    parser.add_argument("--rerun", action="store_true", help="Force rerunning deterministic replays.")
    parser.add_argument(
        "--include-missing",
        action="store_true",
        help="Keep missing future stages in the output (default: yes).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: Dict[str, dict] = {}
    for stage in STAGES:
        results[stage.key] = analyze_stage(stage, rerun=args.rerun)

    report = build_report(results)
    report_path = OUTPUT_DIR / "round2_build_up_workflow_report.md"
    json_path = OUTPUT_DIR / "round2_build_up_workflow_report.json"
    report_path.write_text(report)
    json_path.write_text(json.dumps(results, indent=2))

    print(f"Wrote report: {report_path}")
    print(f"Wrote JSON:   {json_path}")


if __name__ == "__main__":
    main()
