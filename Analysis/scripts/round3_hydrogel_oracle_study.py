from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


PRODUCT = "HYDROGEL_PACK"
ANCHOR = 10000.0


@dataclass
class HydroRow:
    day: int
    timestamp: int
    bid1: Optional[float]
    bidv1: Optional[float]
    bid2: Optional[float]
    bidv2: Optional[float]
    bid3: Optional[float]
    bidv3: Optional[float]
    ask1: Optional[float]
    askv1: Optional[float]
    ask2: Optional[float]
    askv2: Optional[float]
    ask3: Optional[float]
    askv3: Optional[float]
    mid: float


def opt_float(value: str) -> Optional[float]:
    if value == "" or value is None:
        return None
    return float(value)


def top_levels(row: HydroRow, side: str) -> List[Tuple[float, float]]:
    if side == "bid":
        levels = [
            (row.bid1, row.bidv1),
            (row.bid2, row.bidv2),
            (row.bid3, row.bidv3),
        ]
    else:
        levels = [
            (row.ask1, row.askv1),
            (row.ask2, row.askv2),
            (row.ask3, row.askv3),
        ]
    return [(float(px), float(vol)) for px, vol in levels if px is not None and vol is not None]


def wall_mid(row: HydroRow) -> float:
    bids = top_levels(row, "bid")
    asks = top_levels(row, "ask")
    if not bids or not asks:
        return row.mid
    wall_bid = max(bids, key=lambda x: (x[1], x[0]))[0]
    wall_ask = min(asks, key=lambda x: (x[1], -x[0]))[0]
    if wall_bid >= wall_ask:
        return row.mid
    return 0.5 * (wall_bid + wall_ask)


def thick_mid(row: HydroRow) -> float:
    bids = top_levels(row, "bid")
    asks = top_levels(row, "ask")
    if not bids or not asks:
        return row.mid
    bid_vol = sum(vol for _, vol in bids)
    ask_vol = sum(abs(vol) for _, vol in asks)
    if bid_vol <= 0.0 or ask_vol <= 0.0:
        return row.mid
    thick_bid = sum(px * vol for px, vol in bids) / bid_vol
    thick_ask = sum(px * abs(vol) for px, vol in asks) / ask_vol
    if thick_bid >= thick_ask:
        return row.mid
    return 0.5 * (thick_bid + thick_ask)


def stable_mid(row: HydroRow) -> float:
    return (row.mid + wall_mid(row) + thick_mid(row)) / 3.0


def spread(row: HydroRow) -> float:
    if row.bid1 is None or row.ask1 is None:
        return 1.0
    return max(1.0, float(row.ask1) - float(row.bid1))


def load_hydro_rows(data_root: Path) -> Dict[int, List[HydroRow]]:
    rows_by_day: Dict[int, List[HydroRow]] = {}
    for csv_path in sorted(data_root.glob("prices_round_3_day_*.csv")):
        with csv_path.open() as handle:
            reader = csv.DictReader(handle, delimiter=";")
            hydro_rows: List[HydroRow] = []
            for raw in reader:
                if raw["product"] != PRODUCT:
                    continue
                hydro_rows.append(
                    HydroRow(
                        day=int(raw["day"]),
                        timestamp=int(raw["timestamp"]),
                        bid1=opt_float(raw["bid_price_1"]),
                        bidv1=opt_float(raw["bid_volume_1"]),
                        bid2=opt_float(raw["bid_price_2"]),
                        bidv2=opt_float(raw["bid_volume_2"]),
                        bid3=opt_float(raw["bid_price_3"]),
                        bidv3=opt_float(raw["bid_volume_3"]),
                        ask1=opt_float(raw["ask_price_1"]),
                        askv1=opt_float(raw["ask_volume_1"]),
                        ask2=opt_float(raw["ask_price_2"]),
                        askv2=opt_float(raw["ask_volume_2"]),
                        ask3=opt_float(raw["ask_price_3"]),
                        askv3=opt_float(raw["ask_volume_3"]),
                        mid=float(raw["mid_price"]),
                    )
                )
        if hydro_rows:
            rows_by_day[hydro_rows[0].day] = hydro_rows
    if not rows_by_day:
        raise ValueError(f"No {PRODUCT} rows found in {data_root}")
    return rows_by_day


def evaluate_target_path(rows: Sequence[HydroRow], targets: Sequence[int]) -> float:
    if len(rows) != len(targets):
        raise ValueError("rows and targets must match")
    if len(rows) < 2:
        return 0.0
    pnl = 0.0
    pos_prev = 0
    for idx, row in enumerate(rows[:-1]):
        pos = int(targets[idx])
        pnl -= abs(pos - pos_prev) * 0.5 * spread(row)
        pnl += pos * (rows[idx + 1].mid - row.mid)
        pos_prev = pos
    return float(pnl)


def constant_target(rows: Sequence[HydroRow], target: int) -> List[int]:
    return [target] * len(rows)


def best_hold(rows: Sequence[HydroRow], size: int = 200) -> Dict[str, object]:
    long_pnl = evaluate_target_path(rows, constant_target(rows, size))
    short_pnl = evaluate_target_path(rows, constant_target(rows, -size))
    if long_pnl >= short_pnl:
        return {"pattern": "all_day_long", "size": size, "pnl": long_pnl}
    return {"pattern": "all_day_short", "size": size, "pnl": short_pnl}


def best_one_flip(rows: Sequence[HydroRow], size: int = 200) -> Dict[str, object]:
    best: Optional[Dict[str, object]] = None
    n = len(rows)
    start_mid = rows[0].mid
    end_mid = rows[-1].mid
    open_cost = size * 0.5 * spread(rows[0])
    for first_sign, label in ((1, "long_short"), (-1, "short_long")):
        const = first_sign * size * (-start_mid - end_mid) - open_cost
        for flip_idx in range(1, n - 1):
            pnl = (
                first_sign * size * (2.0 * rows[flip_idx].mid)
                + const
                - size * spread(rows[flip_idx])
            )
            if best is None or pnl > float(best["pnl"]):
                best = {
                    "pattern": label,
                    "size": size,
                    "flip_idx": flip_idx,
                    "flip_timestamp": rows[flip_idx].timestamp,
                    "pnl": float(pnl),
                }
    assert best is not None
    return best


def best_two_flip(rows: Sequence[HydroRow], size: int = 200) -> Dict[str, object]:
    best: Optional[Dict[str, object]] = None
    n = len(rows)
    start_mid = rows[0].mid
    end_mid = rows[-1].mid
    open_cost = size * 0.5 * spread(rows[0])
    patterns = [
        (1, "long_short_long"),
        (-1, "short_long_short"),
    ]
    for sign_a, label in patterns:
        # PnL = sign_a*Q*(2m_i - 2m_j + m_end - m_start) - open - Q*(spread_i + spread_j)
        # For each j, track the best admissible i < j.
        best_prefix_value = None
        best_prefix_idx = None
        const = sign_a * size * (end_mid - start_mid) - open_cost
        for second_flip in range(2, n - 1):
            candidate_idx = second_flip - 1
            candidate_value = sign_a * size * (2.0 * rows[candidate_idx].mid) - size * spread(rows[candidate_idx])
            if best_prefix_value is None or candidate_value > best_prefix_value:
                best_prefix_value = candidate_value
                best_prefix_idx = candidate_idx

            assert best_prefix_value is not None
            assert best_prefix_idx is not None
            pnl = (
                best_prefix_value
                + sign_a * size * (-2.0 * rows[second_flip].mid)
                - size * spread(rows[second_flip])
                + const
            )
            if best is None or pnl > float(best["pnl"]):
                best = {
                    "pattern": label,
                    "size": size,
                    "first_flip_idx": best_prefix_idx,
                    "first_flip_timestamp": rows[best_prefix_idx].timestamp,
                    "second_flip_idx": second_flip,
                    "second_flip_timestamp": rows[second_flip].timestamp,
                    "pnl": float(pnl),
                }
    assert best is not None
    return best


def anchored_mean_reverter(rows: Sequence[HydroRow]) -> Dict[str, object]:
    best: Optional[Dict[str, object]] = None
    for size in (60, 100, 140, 200):
        for entry in range(4, 61, 2):
            exit_th = max(1.0, 0.5 * entry)
            targets: List[int] = []
            current = 0
            for row in rows:
                gap = row.mid - ANCHOR
                if gap >= entry:
                    current = -size
                elif gap <= -entry:
                    current = size
                elif abs(gap) <= exit_th:
                    current = 0
                targets.append(current)
            pnl = evaluate_target_path(rows, targets)
            if best is None or pnl > float(best["pnl"]):
                best = {
                    "pattern": "anchored_mean_reverter",
                    "size": size,
                    "entry_threshold": entry,
                    "exit_threshold": exit_th,
                    "pnl": pnl,
                }
    assert best is not None
    return best


def local_fair_mr(rows: Sequence[HydroRow]) -> Dict[str, object]:
    best: Optional[Dict[str, object]] = None
    stable_vals = [stable_mid(row) for row in rows]
    for size in (40, 80, 120, 160, 200):
        for entry_tenths in range(2, 21):
            entry = 0.1 * entry_tenths
            exit_th = max(0.05, 0.5 * entry)
            targets: List[int] = []
            current = 0
            for row, fair in zip(rows, stable_vals):
                gap = row.mid - fair
                if gap >= entry:
                    current = -size
                elif gap <= -entry:
                    current = size
                elif abs(gap) <= exit_th:
                    current = 0
                targets.append(current)
            pnl = evaluate_target_path(rows, targets)
            if best is None or pnl > float(best["pnl"]):
                best = {
                    "pattern": "local_fair_mean_reverter",
                    "size": size,
                    "entry_threshold": entry,
                    "exit_threshold": exit_th,
                    "pnl": pnl,
                }
    assert best is not None
    return best


def phase_profile(rows_by_day: Dict[int, List[HydroRow]], buckets: int = 12) -> Dict[str, object]:
    bucket_returns: Dict[int, List[float]] = {idx: [] for idx in range(buckets)}
    for rows in rows_by_day.values():
        max_ts = max(row.timestamp for row in rows)
        for left, right in zip(rows, rows[1:]):
            progress = left.timestamp / max_ts if max_ts > 0 else 0.0
            bucket = min(buckets - 1, int(progress * buckets))
            bucket_returns[bucket].append(right.mid - left.mid)

    avg_returns = {idx: mean(vals) if vals else 0.0 for idx, vals in bucket_returns.items()}
    sign_agreement = {
        idx: (sum(1 for value in vals if value > 0) / len(vals) if vals else 0.0)
        for idx, vals in bucket_returns.items()
    }
    cumulative = {}
    running = 0.0
    for idx in range(buckets):
        running += avg_returns[idx]
        cumulative[idx] = running
    return {
        "avg_bucket_return": avg_returns,
        "positive_sign_agreement": sign_agreement,
        "cumulative_mean_return": cumulative,
    }


def classify_winner(class_totals: Dict[str, float]) -> str:
    best_name = max(class_totals, key=class_totals.get)
    best_val = class_totals[best_name]
    sorted_vals = sorted(class_totals.values(), reverse=True)
    runner_up = sorted_vals[1] if len(sorted_vals) > 1 else 0.0
    edge = best_val - runner_up
    if best_name in {"one_flip", "two_flip"} and edge > 0.10 * max(1.0, abs(best_val)):
        return "Hydrogel ceiling looks regime / phase driven."
    if best_name == "local_fair_mm":
        return "Hydrogel ceiling looks more like moving-fair / local-fair trading."
    if best_name == "anchored_mean_reverter":
        return "Hydrogel ceiling still supports an anchored mean-reversion thesis."
    return "Hydrogel ceiling is mixed; no single class dominates strongly."


def run_study(data_root: Path) -> Dict[str, object]:
    rows_by_day = load_hydro_rows(data_root)
    daily_results: Dict[int, Dict[str, object]] = {}
    class_totals = {
        "hold": 0.0,
        "one_flip": 0.0,
        "two_flip": 0.0,
        "anchored_mean_reverter": 0.0,
        "local_fair_mm": 0.0,
    }

    for day, rows in sorted(rows_by_day.items()):
        hold = best_hold(rows)
        one_flip = best_one_flip(rows)
        two_flip = best_two_flip(rows)
        anchored = anchored_mean_reverter(rows)
        local_fair = local_fair_mr(rows)

        day_summary = {
            "hold": hold,
            "one_flip": one_flip,
            "two_flip": two_flip,
            "anchored_mean_reverter": anchored,
            "local_fair_mm": local_fair,
        }
        daily_results[day] = day_summary
        class_totals["hold"] += float(hold["pnl"])
        class_totals["one_flip"] += float(one_flip["pnl"])
        class_totals["two_flip"] += float(two_flip["pnl"])
        class_totals["anchored_mean_reverter"] += float(anchored["pnl"])
        class_totals["local_fair_mm"] += float(local_fair["pnl"])

    profile = phase_profile(rows_by_day)
    return {
        "product": PRODUCT,
        "anchor_reference": ANCHOR,
        "daily": daily_results,
        "class_totals": class_totals,
        "phase_profile": profile,
        "interpretation": classify_winner(class_totals),
    }


def render_markdown(summary: Dict[str, object]) -> str:
    lines = [
        "# Round 3 Hydrogel Oracle Study",
        "",
        "This study compares Hydrogel strategy classes, not bot parameter tweaks.",
        "",
        "Classes tested:",
        "- all-day hold",
        "- one-flip trend strategy",
        "- two-flip trend strategy",
        "- anchored mean reverter around `10000`",
        "- local-fair mean reverter around a moving stable fair",
        "",
        "## Aggregate Class Totals",
        "",
    ]
    class_totals = summary["class_totals"]
    for name, value in sorted(class_totals.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- `{name}`: `{value:.2f}`")
    lines.extend(["", f"Interpretation: {summary['interpretation']}", ""])

    lines.append("## Daily Best Results")
    lines.append("")
    for day, result in summary["daily"].items():
        lines.append(f"### Day {day}")
        lines.append("")
        for key in ("hold", "one_flip", "two_flip", "anchored_mean_reverter", "local_fair_mm"):
            lines.append(f"- `{key}`: `{json.dumps(result[key], sort_keys=True)}`")
        lines.append("")

    lines.extend(["## Phase Profile", ""])
    for bucket, value in summary["phase_profile"]["avg_bucket_return"].items():
        agreement = summary["phase_profile"]["positive_sign_agreement"][bucket]
        cumulative = summary["phase_profile"]["cumulative_mean_return"][bucket]
        lines.append(
            f"- bucket `{bucket}`: avg return `{value:.4f}`, positive sign agreement `{agreement:.3f}`, cumulative mean return `{cumulative:.4f}`"
        )

    lines.extend(
        [
            "",
            "## Next-Step Read",
            "",
            "- If `one_flip` or `two_flip` dominates, Hydrogel should move toward regime / phase detection.",
            "- If `local_fair_mm` dominates, Hydrogel should stay in the moving-fair family and we should retune fair/execution, not build a regime trader.",
            "- If `anchored_mean_reverter` dominates, the current anchor thesis is still competitive and only the execution shape is wrong.",
        ]
    )
    return "\n".join(lines) + "\n"


def save_phase_plot(summary: Dict[str, object], out_path: Path) -> None:
    if plt is None:
        return
    profile = summary["phase_profile"]
    buckets = sorted(profile["avg_bucket_return"])
    avg_returns = [profile["avg_bucket_return"][idx] for idx in buckets]
    cumulative = [profile["cumulative_mean_return"][idx] for idx in buckets]
    sign_agreement = [profile["positive_sign_agreement"][idx] for idx in buckets]

    fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax[0].plot(buckets, avg_returns, marker="o", label="Avg Bucket Return")
    ax[0].plot(buckets, cumulative, marker="s", label="Cumulative Mean Return")
    ax[0].axhline(0.0, color="black", linewidth=0.8)
    ax[0].legend()
    ax[0].set_title("Hydrogel Phase Profile")
    ax[0].set_ylabel("Ticks")

    ax[1].bar(buckets, sign_agreement, color="#5a7")
    ax[1].axhline(0.5, color="black", linewidth=0.8, linestyle="--")
    ax[1].set_ylim(0.0, 1.0)
    ax[1].set_ylabel("Positive Sign Agreement")
    ax[1].set_xlabel("Normalized Timestamp Bucket")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("Data/ROUND_3"))
    parser.add_argument("--out-dir", type=Path, default=Path("Analysis/output/round3_hydrogel_oracle_study"))
    args = parser.parse_args()

    summary = run_study(args.data_root)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.out_dir / "report.md"
    summary_path = args.out_dir / "summary.json"
    report_path.write_text(render_markdown(summary))
    summary_path.write_text(json.dumps(summary, indent=2))
    save_phase_plot(summary, args.out_dir / "phase_profile.png")

    print(f"report: {report_path}")
    print(f"summary: {summary_path}")
    if (args.out_dir / 'phase_profile.png').exists():
        print(f"plot: {args.out_dir / 'phase_profile.png'}")


if __name__ == "__main__":
    main()
