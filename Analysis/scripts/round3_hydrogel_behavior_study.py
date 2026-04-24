from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


PRODUCT = "HYDROGEL_PACK"
ANCHOR = 10000.0
BUCKETS = 20


@dataclass
class HydroRow:
    day: int
    timestamp: int
    mid: float
    bid1: Optional[float]
    bidv1: float
    ask1: Optional[float]
    askv1: float
    top_depth: float
    top3_depth: float
    spread: float
    imbalance: float
    micro_gap: float
    anchor_gap: float
    progress: float


def opt_float(value: str) -> Optional[float]:
    if value == "" or value is None:
        return None
    return float(value)


def correlation(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    if len(xs) < 10 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    var_x = sum(x * x for x in dx)
    var_y = sum(y * y for y in dy)
    if var_x <= 1e-12 or var_y <= 1e-12:
        return None
    cov = sum(x * y for x, y in zip(dx, dy))
    return cov / math.sqrt(var_x * var_y)


def mean_or_none(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def load_rows(data_root: Path) -> Dict[int, List[HydroRow]]:
    rows_by_day: Dict[int, List[HydroRow]] = {}
    for csv_path in sorted(data_root.glob("prices_round_3_day_*.csv")):
        rows: List[HydroRow] = []
        with csv_path.open() as handle:
            reader = csv.DictReader(handle, delimiter=";")
            for raw in reader:
                if raw["product"] != PRODUCT:
                    continue

                bid1 = opt_float(raw["bid_price_1"])
                ask1 = opt_float(raw["ask_price_1"])
                bidv1 = opt_float(raw["bid_volume_1"]) or 0.0
                askv1 = abs(opt_float(raw["ask_volume_1"]) or 0.0)
                top_depth = bidv1 + askv1

                top3_depth = 0.0
                for idx in (1, 2, 3):
                    top3_depth += opt_float(raw[f"bid_volume_{idx}"]) or 0.0
                    top3_depth += abs(opt_float(raw[f"ask_volume_{idx}"]) or 0.0)

                mid = float(raw["mid_price"])
                spread = 1.0
                if bid1 is not None and ask1 is not None:
                    spread = ask1 - bid1

                if bid1 is not None and ask1 is not None and top_depth > 0.0:
                    micro = ((ask1 * bidv1) + (bid1 * askv1)) / top_depth
                else:
                    micro = mid

                imbalance = 0.0
                if top_depth > 0.0:
                    imbalance = (bidv1 - askv1) / top_depth

                ts = int(raw["timestamp"])
                rows.append(
                    HydroRow(
                        day=int(raw["day"]),
                        timestamp=ts,
                        mid=mid,
                        bid1=bid1,
                        bidv1=bidv1,
                        ask1=ask1,
                        askv1=askv1,
                        top_depth=top_depth,
                        top3_depth=top3_depth,
                        spread=spread,
                        imbalance=imbalance,
                        micro_gap=micro - mid,
                        anchor_gap=ANCHOR - mid,
                        progress=ts / 999900.0,
                    )
                )
        if rows:
            rows_by_day[rows[0].day] = rows
    if not rows_by_day:
        raise ValueError(f"No {PRODUCT} rows found in {data_root}")
    return rows_by_day


def horizon_correlations(rows_by_day: Dict[int, List[HydroRow]], horizon: int) -> Dict[str, Optional[float]]:
    micro_x: List[float] = []
    imb_x: List[float] = []
    anchor_x: List[float] = []
    future_y: List[float] = []
    for rows in rows_by_day.values():
        mids = [row.mid for row in rows]
        for idx in range(len(rows) - horizon):
            future_move = mids[idx + horizon] - mids[idx]
            row = rows[idx]
            micro_x.append(row.micro_gap)
            imb_x.append(row.imbalance)
            anchor_x.append(row.anchor_gap)
            future_y.append(future_move)
    return {
        "micro_corr": correlation(micro_x, future_y),
        "imbalance_corr": correlation(imb_x, future_y),
        "anchor_corr": correlation(anchor_x, future_y),
    }


def phase_horizon_summary(
    rows_by_day: Dict[int, List[HydroRow]], horizon: int
) -> Dict[str, Dict[str, Optional[float]]]:
    windows = {
        "early": (0.0, 0.25),
        "mid": (0.25, 0.75),
        "late": (0.75, 1.0),
    }
    out: Dict[str, Dict[str, Optional[float]]] = {}
    for name, (lo, hi) in windows.items():
        micro_x: List[float] = []
        imb_x: List[float] = []
        anchor_x: List[float] = []
        future_y: List[float] = []
        for rows in rows_by_day.values():
            mids = [row.mid for row in rows]
            for idx in range(len(rows) - horizon):
                row = rows[idx]
                if not (lo <= row.progress < hi):
                    continue
                future_move = mids[idx + horizon] - mids[idx]
                micro_x.append(row.micro_gap)
                imb_x.append(row.imbalance)
                anchor_x.append(row.anchor_gap)
                future_y.append(future_move)
        out[name] = {
            "avg_future_move": mean_or_none(future_y),
            "micro_corr": correlation(micro_x, future_y),
            "imbalance_corr": correlation(imb_x, future_y),
            "anchor_corr": correlation(anchor_x, future_y),
        }
    return out


def bucket_returns(rows_by_day: Dict[int, List[HydroRow]]) -> Dict[str, object]:
    day_buckets: Dict[int, List[float]] = {}
    for day, rows in rows_by_day.items():
        mids = [row.mid for row in rows]
        bucket_size = len(rows) // BUCKETS
        series: List[float] = []
        for bucket in range(BUCKETS):
            lo = bucket * bucket_size
            hi = (bucket + 1) * bucket_size if bucket < BUCKETS - 1 else len(rows) - 1
            series.append(mids[hi] - mids[lo])
        day_buckets[day] = series

    aggregate: List[Dict[str, object]] = []
    for bucket in range(BUCKETS):
        values = [day_buckets[day][bucket] for day in sorted(day_buckets)]
        aggregate.append(
            {
                "bucket": bucket,
                "window": f"{bucket * 5}-{(bucket + 1) * 5}%",
                "avg_return": sum(values) / len(values),
                "positive_days": sum(value > 0 for value in values),
                "negative_days": sum(value < 0 for value in values),
                "day_values": values,
            }
        )
    return {"daily": day_buckets, "aggregate": aggregate}


def phase_profile(rows_by_day: Dict[int, List[HydroRow]]) -> Dict[str, object]:
    per_day: Dict[int, Dict[str, object]] = {}
    for day, rows in rows_by_day.items():
        n = len(rows)
        lows = min(rows, key=lambda row: row.mid)
        highs = max(rows, key=lambda row: row.mid)

        late_rows = [row for row in rows if row.progress >= 0.60]
        late_high = max(late_rows, key=lambda row: row.mid)
        post_75 = [row for row in rows if row.progress >= 0.75]
        post_75_high = max(post_75, key=lambda row: row.mid)

        def first_mid_at(progress_cut: float) -> float:
            for row in rows:
                if row.progress >= progress_cut:
                    return row.mid
            return rows[-1].mid

        p75 = first_mid_at(0.75)
        p80 = first_mid_at(0.80)
        p90 = first_mid_at(0.90)
        per_day[day] = {
            "start_mid": rows[0].mid,
            "end_mid": rows[-1].mid,
            "min_mid": lows.mid,
            "min_ts": lows.timestamp,
            "max_mid": highs.mid,
            "max_ts": highs.timestamp,
            "late_high_mid": late_high.mid,
            "late_high_ts": late_high.timestamp,
            "post_75_high_mid": post_75_high.mid,
            "post_75_high_ts": post_75_high.timestamp,
            "move_75_to_80": p80 - p75,
            "move_80_to_90": p90 - p80,
            "move_90_to_end": rows[-1].mid - p90,
            "move_75_to_end": rows[-1].mid - p75,
        }
    return per_day


def late_anchor_edges(rows_by_day: Dict[int, List[HydroRow]], horizon: int) -> Dict[int, Dict[str, Optional[float]]]:
    out: Dict[int, Dict[str, Optional[float]]] = {}
    for day, rows in rows_by_day.items():
        mids = [row.mid for row in rows]
        above: List[float] = []
        below: List[float] = []
        for idx in range(len(rows) - horizon):
            row = rows[idx]
            if row.progress < 0.75:
                continue
            if abs(row.mid - ANCHOR) < 25.0:
                continue
            future_move = mids[idx + horizon] - mids[idx]
            if row.mid > ANCHOR:
                above.append(future_move)
            else:
                below.append(future_move)
        out[day] = {
            "above_anchor_count": len(above),
            "above_anchor_avg_fwd": mean_or_none(above),
            "below_anchor_count": len(below),
            "below_anchor_avg_fwd": mean_or_none(below),
        }
    return out


def phase_liquidity(rows_by_day: Dict[int, List[HydroRow]]) -> Dict[str, Dict[str, float]]:
    windows = {
        "early": (0.0, 0.25),
        "mid": (0.25, 0.75),
        "late": (0.75, 1.0),
    }
    out: Dict[str, Dict[str, float]] = {}
    for name, (lo, hi) in windows.items():
        spreads: List[float] = []
        top_depths: List[float] = []
        top3_depths: List[float] = []
        for rows in rows_by_day.values():
            for row in rows:
                if lo <= row.progress < hi:
                    spreads.append(row.spread)
                    top_depths.append(row.top_depth)
                    top3_depths.append(row.top3_depth)
        out[name] = {
            "spread_mean": sum(spreads) / len(spreads),
            "top_depth_mean": sum(top_depths) / len(top_depths),
            "top3_depth_mean": sum(top3_depths) / len(top3_depths),
        }
    return out


def load_oracle_summary(or_path: Path) -> Optional[dict]:
    if not or_path.exists():
        return None
    return json.loads(or_path.read_text())


def build_summary(data_root: Path, oracle_path: Path) -> Dict[str, object]:
    rows_by_day = load_rows(data_root)
    summary = {
        "product": PRODUCT,
        "oracle": load_oracle_summary(oracle_path),
        "horizon_correlations": {
            str(h): horizon_correlations(rows_by_day, h) for h in (1, 5, 20, 50)
        },
        "phase_horizon_summary": {
            str(h): phase_horizon_summary(rows_by_day, h) for h in (5, 20, 50)
        },
        "bucket_returns": bucket_returns(rows_by_day),
        "phase_profile": phase_profile(rows_by_day),
        "late_anchor_edges_20": late_anchor_edges(rows_by_day, 20),
        "late_anchor_edges_50": late_anchor_edges(rows_by_day, 50),
        "phase_liquidity": phase_liquidity(rows_by_day),
    }
    return summary


def fmt(value: Optional[float], digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def render_markdown(summary: Dict[str, object]) -> str:
    lines: List[str] = [
        "# Round 3 Hydrogel Behavior Study",
        "",
        "This pass re-checks the raw Hydrogel CSVs to answer a narrower question:",
        "what is the product actually doing, and which signals are useful for the next Hydrogel improvements?",
        "",
    ]

    oracle = summary.get("oracle")
    if oracle:
        class_totals = oracle["class_totals"]
        lines.extend(
            [
                "## Oracle Read",
                "",
                f"- `two_flip`: `{class_totals['two_flip']:.0f}`",
                f"- `one_flip`: `{class_totals['one_flip']:.0f}`",
                f"- `anchored_mean_reverter`: `{class_totals['anchored_mean_reverter']:.0f}`",
                f"- `hold`: `{class_totals['hold']:.0f}`",
                f"- `local_fair_mm`: `{class_totals['local_fair_mm']:.0f}`",
                "",
                "Interpretation: Hydrogel is still much closer to an anchored phase/regime product than to a local-fair MM product.",
                "",
            ]
        )

    lines.extend(
        [
            "## Signal Read",
            "",
            "Short-horizon local-book predictors work, but they decay fast. Longer-horizon anchor pull is stronger, especially late in the day.",
            "",
            "| Horizon | Micro Corr | Imbalance Corr | Anchor Corr |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for horizon, values in summary["horizon_correlations"].items():
        lines.append(
            f"| `{horizon}` | `{fmt(values['micro_corr'], 3)}` | `{fmt(values['imbalance_corr'], 3)}` | `{fmt(values['anchor_corr'], 3)}` |"
        )

    lines.extend(
        [
            "",
            "Useful interpretation:",
            "- `1-5` bars: use micro / imbalance for entry timing and re-entry confirmation.",
            "- `20-50` bars: anchor gap matters more than microstructure.",
            "- That means Hydrogel should not use the same signal for entry and hold.",
            "",
            "## Phase Windows",
            "",
            "The most useful repeated buckets are below.",
            "",
            "| Window | Avg Return | Sign Agreement | Day Values |",
            "| --- | ---: | ---: | --- |",
        ]
    )

    for bucket in summary["bucket_returns"]["aggregate"]:
        pos = int(bucket["positive_days"])
        neg = int(bucket["negative_days"])
        avg = float(bucket["avg_return"])
        if pos in (0, 3) or neg in (0, 3) or abs(avg) >= 15.0:
            day_vals = ", ".join(f"{value:.1f}" for value in bucket["day_values"])
            lines.append(
                f"| `{bucket['window']}` | `{avg:.1f}` | `{pos}/3 pos` | `{day_vals}` |"
            )

    lines.extend(
        [
            "",
            "Most actionable phase findings:",
            "- `10-15%` is a consistent rebound window.",
            "- `20-25%` is consistently weak.",
            "- `55-60%` is a consistent positive window.",
            "- `75-80%` is the strongest reliable late fade window across all three days.",
            "- After `80%`, the path splits: fade can continue or rebound, so that window needs confirmation rather than a blind short.",
            "",
            "## Late-Window Anchor Edge",
            "",
            "Late in the day, being far above or below the anchor has a clear directional meaning.",
            "",
            "| Day | 20-bar Fwd if `mid > 10025` | 20-bar Fwd if `mid < 9975` | 50-bar Fwd if `mid > 10025` | 50-bar Fwd if `mid < 9975` |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    late20 = summary["late_anchor_edges_20"]
    late50 = summary["late_anchor_edges_50"]
    for day in sorted(late20):
        lines.append(
            f"| `{day}` | `{fmt(late20[day]['above_anchor_avg_fwd'], 2)}` | `{fmt(late20[day]['below_anchor_avg_fwd'], 2)}` | `{fmt(late50[day]['above_anchor_avg_fwd'], 2)}` | `{fmt(late50[day]['below_anchor_avg_fwd'], 2)}` |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- Late Hydrogel above `10025` has negative forward return on every day.",
            "- Late Hydrogel below `9975` has positive forward return whenever that state appears.",
            "- So a late long held far above anchor is dangerous even if the regime score still looks acceptable.",
            "",
            "## Liquidity Check",
            "",
            "| Phase | Mean Spread | Mean Top Depth | Mean Top-3 Depth |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for phase, vals in summary["phase_liquidity"].items():
        lines.append(
            f"| `{phase}` | `{vals['spread_mean']:.2f}` | `{vals['top_depth_mean']:.2f}` | `{vals['top3_depth_mean']:.2f}` |"
        )

    lines.extend(
        [
            "",
            "Interpretation: the late problem is not caused by worse visible liquidity. Spread and depth stay almost unchanged.",
            "",
            "## Daily Shape",
            "",
            "| Day | Global Min | Global Max | Late High After 60% | Post-75 Move |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for day, vals in sorted(summary["phase_profile"].items()):
        lines.append(
            f"| `{day}` | `{vals['min_mid']:.1f} @ {vals['min_ts']}` | `{vals['max_mid']:.1f} @ {vals['max_ts']}` | `{vals['late_high_mid']:.1f} @ {vals['late_high_ts']}` | `{vals['move_75_to_end']:.1f}` |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- Day `0`: short -> long -> short style.",
            "- Day `1`: long -> short -> long style, but still has an initial `75-80%` fade.",
            "- Day `2`: short -> long -> short style with the second flip around `72%`.",
            "",
            "## Best Next Hydrogel Improvements",
            "",
            "1. Build a late-phase trigger around `75-80%` day progress. That is the cleanest stable timing signal in the raw data.",
            "2. Use micro / imbalance only for entry and re-entry confirmation. They are strong at `1-5` bars but not a hold signal.",
            "3. Use anchor distance as a stronger hold/exit control. A late long above `10025` is structurally dangerous.",
            "4. Do not blindly short after `80%`. The initial fade is reliable, but post-fade continuation is not stable across all days.",
            "5. A better state machine is likely:",
            "`EARLY_SHOCK -> MID_RECOVERY / BUILD -> LATE_FADE_TRIGGER -> {CLEAR_LONG or SMALL_SHORT if reconfirmed}`",
            "",
            "Short version: the next Hydrogel edge is probably not more generic risk control. It is a better late-day state transition that respects both the consistent `75-80%` fade and the fact that the post-fade branch is not always the same.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 3 Hydrogel behavior study")
    parser.add_argument("--data-root", type=Path, default=Path("Data/ROUND_3"))
    parser.add_argument(
        "--oracle-summary",
        type=Path,
        default=Path("Analysis/output/round3_hydrogel_oracle_study/summary.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("Analysis/output/round3_hydrogel_behavior_study"),
    )
    args = parser.parse_args()

    summary = build_summary(args.data_root, args.oracle_summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "report.md"
    summary_path = args.output_dir / "summary.json"
    report_path.write_text(render_markdown(summary))
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps({"report": str(report_path.resolve()), "summary": str(summary_path.resolve())}, indent=2))


if __name__ == "__main__":
    main()
