#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUND2BT_ROOT = REPO_ROOT / "Round2Backtester"
if str(ROUND2BT_ROOT) not in sys.path:
    sys.path.insert(0, str(ROUND2BT_ROOT))

from round2_backtester.replay import BacktestConfig, run_compare_backtest


BASE_BOT = REPO_ROOT / "Bots" / "Round2" / "TradervR2_27_researchBase.py"
REFERENCE_BOT = REPO_ROOT / "Bots" / "Round2" / "TradervR2_26.py"
VARIANT_DIR = REPO_ROOT / "Bots" / "Round2" / "research_variants"
OUTPUT_ROOT = REPO_ROOT / "Analysis" / "output" / "round2_robustness_workflow"
DATA_ROOT = REPO_ROOT / "Data" / "ROUND_2"


IDEA_MATRIX: list[dict[str, Any]] = [
    {
        "idea": "1_book_health",
        "variants": [
            {
                "name": "TradervR2_28_bookHealth_mild.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "BOOK_HEALTH_LOW": 0.42,
                    "BOOK_HEALTH_MED": 0.64,
                    "BOOK_HEALTH_SIGNAL_DAMP_LOW": 0.84,
                    "BOOK_HEALTH_SIGNAL_DAMP_MED": 0.93,
                    "BOOK_HEALTH_EDGE_PENALTY_LOW": 0.10,
                    "BOOK_HEALTH_EDGE_PENALTY_MED": 0.04,
                    "BOOK_HEALTH_JOIN_PENALTY_LOW": 0.22,
                    "BOOK_HEALTH_JOIN_PENALTY_MED": 0.10,
                    "BOOK_HEALTH_SIZE_MULT_LOW": 0.90,
                    "BOOK_HEALTH_SIZE_MULT_MED": 0.96,
                    "ACCESS_BOOK_HEALTH_MIN": 0.58,
                },
            },
            {
                "name": "TradervR2_28_bookHealth_strong.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "BOOK_HEALTH_LOW": 0.46,
                    "BOOK_HEALTH_MED": 0.68,
                    "BOOK_HEALTH_SIGNAL_DAMP_LOW": 0.76,
                    "BOOK_HEALTH_SIGNAL_DAMP_MED": 0.88,
                    "BOOK_HEALTH_EDGE_PENALTY_LOW": 0.18,
                    "BOOK_HEALTH_EDGE_PENALTY_MED": 0.08,
                    "BOOK_HEALTH_JOIN_PENALTY_LOW": 0.36,
                    "BOOK_HEALTH_JOIN_PENALTY_MED": 0.16,
                    "BOOK_HEALTH_SIZE_MULT_LOW": 0.80,
                    "BOOK_HEALTH_SIZE_MULT_MED": 0.92,
                    "ACCESS_BOOK_HEALTH_MIN": 0.66,
                },
            },
        ],
    },
    {
        "idea": "2_fair_robustness",
        "variants": [
            {
                "name": "TradervR2_28_fair_anchorGuard.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "FAIR_STYLE": "anchor_guard",
                    "LOW_HEALTH_ANCHOR_WEIGHT": 0.66,
                    "LOW_HEALTH_STABLE_WEIGHT": 0.34,
                },
            },
            {
                "name": "TradervR2_28_fair_medianGuard.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "FAIR_STYLE": "median_guard",
                },
            },
            {
                "name": "TradervR2_28_fair_thinTopIgnore.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "FAIR_STYLE": "thin_top_ignore",
                    "THIN_TOP_RATIO": 0.70,
                },
            },
        ],
    },
    {
        "idea": "3_vacuum_recovery",
        "variants": [
            {
                "name": "TradervR2_28_vacuumRecovery_cooldown.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "REFILL_STICKY_TICKS": 3,
                    "VACUUM_RECOVERY_STABLE_BARS": 4,
                },
            },
            {
                "name": "TradervR2_28_vacuumRecovery_stableBars.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "REFILL_STICKY_TICKS": 4,
                    "VACUUM_RECOVERY_STABLE_BARS": 5,
                    "REFILL_EDGE_BONUS": 0.06,
                    "REFILL_JOIN_BONUS": 0.06,
                },
            },
        ],
    },
    {
        "idea": "4_side_starvation",
        "variants": [
            {
                "name": "TradervR2_28_starvation_priority.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "STARVATION_BARS": 5,
                    "STARVATION_SIGNAL_MIN": 0.08,
                    "STARVATION_BOOK_HEALTH_MIN": 0.58,
                    "STARVATION_EXTRA_CAP": 0.35,
                    "STARVATION_JOIN_BONUS": 0.12,
                },
            },
            {
                "name": "TradervR2_28_starvation_strong.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "STARVATION_BARS": 4,
                    "STARVATION_SIGNAL_MIN": 0.06,
                    "STARVATION_BOOK_HEALTH_MIN": 0.62,
                    "STARVATION_EXTRA_CAP": 0.42,
                    "STARVATION_JOIN_BONUS": 0.16,
                },
            },
        ],
    },
    {
        "idea": "5_markout_passive",
        "variants": [
            {
                "name": "TradervR2_28_markout_bucketedLight.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "MARKOUT_EDGE_PENALTY": 0.10,
                    "MARKOUT_SIZE_PENALTY": 0.05,
                    "MARKOUT_LOW_HEALTH_FACTOR": 1.15,
                    "MARKOUT_WIDE_SPREAD_FACTOR": 1.08,
                },
            },
            {
                "name": "TradervR2_28_markout_bucketedStrong.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "MARKOUT_EDGE_PENALTY": 0.14,
                    "MARKOUT_SIZE_PENALTY": 0.09,
                    "MARKOUT_LOW_HEALTH_FACTOR": 1.35,
                    "MARKOUT_WIDE_SPREAD_FACTOR": 1.18,
                },
            },
        ],
    },
    {
        "idea": "6_terminal_risk",
        "variants": [
            {
                "name": "TradervR2_28_terminalRisk_soft.py",
                "ash": {
                    "TERMINAL_RISK_ENABLE": True,
                    "TERMINAL_RISK_START": 0.84,
                    "TERMINAL_RISK_POS": 18,
                    "TERMINAL_RISK_SIGNAL_MAX": 0.10,
                    "TERMINAL_RISK_CONVICTION_MAX": 0.55,
                    "TERMINAL_RISK_EDGE_BONUS": 0.10,
                    "TERMINAL_RISK_JOIN_BONUS": 0.04,
                    "TERMINAL_RISK_FRONT_BONUS": 1,
                    "TERMINAL_RISK_OPPOSITE_EDGE_PENALTY": 0.12,
                },
            },
            {
                "name": "TradervR2_28_terminalRisk_asymmetric.py",
                "ash": {
                    "TERMINAL_RISK_ENABLE": True,
                    "TERMINAL_RISK_START": 0.78,
                    "TERMINAL_RISK_HARD_START": 0.92,
                    "TERMINAL_RISK_POS": 14,
                    "TERMINAL_RISK_SIGNAL_MAX": 0.16,
                    "TERMINAL_RISK_CONVICTION_MAX": 0.65,
                    "TERMINAL_RISK_EDGE_BONUS": 0.16,
                    "TERMINAL_RISK_JOIN_BONUS": 0.08,
                    "TERMINAL_RISK_FRONT_BONUS": 2,
                    "TERMINAL_RISK_OPPOSITE_EDGE_PENALTY": 0.18,
                },
            },
        ],
    },
    {
        "idea": "7_access_safe",
        "variants": [
            {
                "name": "TradervR2_28_accessGate_highHealth.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "ACCESS_BOOK_HEALTH_MIN": 0.68,
                    "ACCESS_SIGNAL_MIN": 0.24,
                    "ACCESS_CONVICTION_MIN": 0.48,
                },
            },
            {
                "name": "TradervR2_28_accessGate_highHealthHighConv.py",
                "ash": {
                    "BOOK_HEALTH_ENABLE": True,
                    "ACCESS_BOOK_HEALTH_MIN": 0.76,
                    "ACCESS_SIGNAL_MIN": 0.28,
                    "ACCESS_CONVICTION_MIN": 0.62,
                    "ACCESS_MAGNET_MIN": 1.00,
                },
            },
        ],
    },
    {
        "idea": "10_pepper_robustness",
        "variants": [
            {
                "name": "TradervR2_28_pepper_cheapEarly.py",
                "ipr": {
                    "CHEAP_ACCUM_END": 0.60,
                    "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.55,
                    "CHEAP_ACCUM_FRONT_SIZE_BONUS": 2,
                    "CHEAP_ACCUM_Z_RELAX": -0.65,
                },
            },
            {
                "name": "TradervR2_28_pepper_lateTrim.py",
                "ipr": {
                    "LATE_TRIM_START": 0.84,
                    "LATE_TRIM_RELIEF": 0.16,
                    "EXIT_SELL_RELIEF": 0.22,
                },
            },
        ],
    },
]


def replace_param(text: str, dict_name: str, key: str, value: Any) -> str:
    if dict_name == "ash":
        start_token = "DEFAULT_ASH_PARAMS = {"
        end_token = "\n\n\nDEFAULT_IPR_PARAMS = {"
    else:
        start_token = "DEFAULT_IPR_PARAMS = {"
        end_token = "\n\n\ndef clamp"
    start = text.index(start_token)
    end = text.index(end_token, start)
    section = text[start:end]
    pattern = re.compile(rf'("{re.escape(key)}":\s*)([^,\n]+)(,)')
    if not pattern.search(section):
        raise ValueError(f"Could not find {dict_name} key {key}")
    section = pattern.sub(lambda m: f"{m.group(1)}{repr(value)}{m.group(3)}", section, count=1)
    return text[:start] + section + text[end:]


def generate_variant(base_text: str, variant: dict[str, Any]) -> Path:
    text = base_text
    for key, value in variant.get("ash", {}).items():
        text = replace_param(text, "ash", key, value)
    for key, value in variant.get("ipr", {}).items():
        text = replace_param(text, "ipr", key, value)
    path = VARIANT_DIR / variant["name"]
    path.write_text(text)
    return path


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


def classify_plateaus(product_steps_path: Path, plateau_min: int = 8) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    with product_steps_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["product"] != "ASH_COATED_OSMIUM" or row["mode"] != "no_access":
                continue
            rows.append(
                {
                    "timestamp": int(row["timestamp"]),
                    "pnl": float(row["product_pnl"]),
                    "fills": int(row["fills"]),
                    "submitted": int(row["submitted_orders"]),
                    "position": int(row["position"]),
                    "spread": float(row["spread"]),
                    "signal": float(row["signal_proxy"]),
                    "tox": row["toxicity_bucket"],
                    "agree": row["agreement_state"],
                }
            )

    plateaus: list[list[dict[str, Any]]] = []
    start = 0
    while start < len(rows):
        end = start
        base_pnl = rows[start]["pnl"]
        while end + 1 < len(rows) and abs(rows[end + 1]["pnl"] - base_pnl) < 1e-9:
            end += 1
        if end - start + 1 >= plateau_min:
            plateaus.append(rows[start : end + 1])
        start = end + 1

    counts = Counter()
    longest = 0
    for plateau in plateaus:
        longest = max(longest, len(plateau))
        avg_spread = statistics.mean(r["spread"] for r in plateau)
        avg_signal = statistics.mean(abs(r["signal"]) for r in plateau)
        avg_submitted = statistics.mean(r["submitted"] for r in plateau)
        avg_pos = statistics.mean(abs(r["position"]) for r in plateau)
        high_tox_frac = sum(r["tox"] == "high" for r in plateau) / len(plateau)
        neutral_frac = sum(r["agree"] == "neutral" for r in plateau) / len(plateau)

        if avg_pos >= 55:
            label = "inventory_blocked"
        elif high_tox_frac >= 0.50 and avg_submitted <= 2.0:
            label = "stale_toxicity"
        elif avg_spread >= 18.0 and high_tox_frac >= 0.35:
            label = "market_dry"
        elif avg_signal < 0.45 or neutral_frac >= 0.50:
            label = "signal_neutral"
        else:
            label = "self_throttled"
        counts[label] += 1

    return {
        "plateau_count": len(plateaus),
        "longest_plateau": longest,
        "class_counts": dict(counts),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Round 2 robustness idea workflow.")
    parser.add_argument("--access-seed", type=int, default=7)
    parser.add_argument("--access-seeds", type=int, default=3)
    parser.add_argument("--queue-model", choices=("conservative", "touch_join"), default="conservative")
    parser.add_argument("--lambda-std", type=float, default=0.5)
    parser.add_argument("--skip-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    base_text = BASE_BOT.read_text()
    generated: list[dict[str, Any]] = []

    for idea in IDEA_MATRIX:
        for variant in idea["variants"]:
            path = generate_variant(base_text, variant)
            generated.append({"idea": idea["idea"], "name": path.stem, "path": path})

    bots_to_run = [
        {"idea": "reference", "name": REFERENCE_BOT.stem, "path": REFERENCE_BOT},
        {"idea": "research_base", "name": BASE_BOT.stem, "path": BASE_BOT},
        *generated,
    ]

    results: list[dict[str, Any]] = []
    if not args.skip_run:
        for bot in bots_to_run:
            out_dir = OUTPUT_ROOT / bot["name"]
            cfg = BacktestConfig(
                bot_path=bot["path"],
                data_root=DATA_ROOT,
                output_dir=out_dir,
                day=None,
                mode="compare",
                queue_model=args.queue_model,
                access_seed=args.access_seed,
                access_seeds=args.access_seeds,
                extra_quote_ratio=0.25,
                markout_horizon_steps=5,
            )
            summary = run_compare_backtest(cfg)
            access_totals = [float(run["total_pnl"]) for run in summary["access_runs"]]
            delta_vals = [float(v) for v in summary["delta_access_values"]]
            access_stats = summarize(access_totals)
            delta_stats = summarize(delta_vals)
            plateau_stats = classify_plateaus(out_dir / "no_access" / "product_steps.csv")
            results.append(
                {
                    "idea": bot["idea"],
                    "bot_name": bot["name"],
                    "bot_path": str(bot["path"]),
                    "baseline_no_access_pnl": float(summary["baseline_no_access_pnl"]),
                    "access_total_stats": access_stats,
                    "delta_stats": delta_stats,
                    "access_total_robust_score": robust_score(access_stats, args.lambda_std),
                    "delta_robust_score": robust_score(delta_stats, args.lambda_std),
                    "plateau_stats": plateau_stats,
                    "summary_path": str((out_dir / "compare_summary.json").resolve()),
                }
            )

    results.sort(key=lambda item: item["access_total_robust_score"], reverse=True)
    (OUTPUT_ROOT / "workflow_results.json").write_text(json.dumps(results, indent=2) + "\n")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        grouped[row["idea"]].append(row)

    lines: list[str] = []
    lines.append("# Round 2 Robustness Workflow")
    lines.append("")
    lines.append(f"Base research file: [{BASE_BOT.name}]({BASE_BOT})")
    lines.append(f"Reference bot: [{REFERENCE_BOT.name}]({REFERENCE_BOT})")
    lines.append("")
    lines.append(f"Queue model: `{args.queue_model}`")
    lines.append(f"Access seeds: `{args.access_seed}` to `{args.access_seed + args.access_seeds - 1}`")
    lines.append(f"Robust score: `mean - {args.lambda_std:.2f} * std`")
    lines.append("")

    if results:
        lines.append("## Overall Ranking")
        lines.append("")
        for row in results[:10]:
            lines.append(
                f"- `{row['bot_name']}`: robust `{row['access_total_robust_score']:.1f}`, "
                f"mean `{row['access_total_stats']['mean']:.1f}`, p25 `{row['access_total_stats']['p25']:.1f}`, "
                f"longest plateau `{row['plateau_stats']['longest_plateau']}`"
            )
        lines.append("")

    for idea_name in ["reference", "research_base"] + [item["idea"] for item in IDEA_MATRIX]:
        if idea_name not in grouped:
            continue
        lines.append(f"## `{idea_name}`")
        lines.append("")
        for row in grouped[idea_name]:
            plateau = row["plateau_stats"]
            lines.append(f"### `{row['bot_name']}`")
            lines.append("")
            lines.append(f"- baseline no-access: `{row['baseline_no_access_pnl']:.1f}`")
            lines.append(
                f"- access mean/std/p25: `{row['access_total_stats']['mean']:.1f} / "
                f"{row['access_total_stats']['std']:.1f} / {row['access_total_stats']['p25']:.1f}`"
            )
            lines.append(f"- access robust score: `{row['access_total_robust_score']:.1f}`")
            lines.append(
                f"- plateau count / longest: `{plateau['plateau_count']} / {plateau['longest_plateau']}`"
            )
            lines.append(f"- plateau classes: `{plateau['class_counts']}`")
            lines.append(f"- summary: [{row['bot_name']} compare]({row['summary_path']})")
            lines.append("")

    lines.append("## Plateau Classification Heuristic")
    lines.append("")
    lines.append("The plateau labels are heuristic and come from `no_access/product_steps.csv` on Ash:")
    lines.append("- `market_dry`: wide-ish, toxic, low-opportunity windows")
    lines.append("- `self_throttled`: book looked tradable but the bot stayed too quiet")
    lines.append("- `inventory_blocked`: position was already stretched")
    lines.append("- `signal_neutral`: no strong directional edge")
    lines.append("- `stale_toxicity`: toxic memory likely outlived the raw state")
    lines.append("")

    (OUTPUT_ROOT / "workflow_report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(results[:10], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
