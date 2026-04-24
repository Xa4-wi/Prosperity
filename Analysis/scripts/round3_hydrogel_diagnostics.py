from __future__ import annotations

import argparse
import json
from bisect import bisect_right
from pathlib import Path
from typing import Dict, List, Tuple


PRODUCT = "HYDROGEL_PACK"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def parse_log(log_path: Path) -> Tuple[List[dict], List[dict]]:
    payload = json.loads(log_path.read_text())
    activity_lines = payload["activitiesLog"].splitlines()
    header = activity_lines[0].split(";")
    idx = {name: i for i, name in enumerate(header)}

    activity_rows: List[dict] = []
    for line in activity_lines[1:]:
        parts = line.split(";")
        if len(parts) <= idx["profit_and_loss"]:
            continue
        if parts[idx["product"]] != PRODUCT:
            continue
        activity_rows.append(
            {
                "day": int(parts[idx["day"]]),
                "timestamp": int(parts[idx["timestamp"]]),
                "mid": float(parts[idx["mid_price"]]),
                "pnl": float(parts[idx["profit_and_loss"]]),
            }
        )

    trade_rows: List[dict] = []
    for trade in payload["tradeHistory"]:
        if trade["symbol"] != PRODUCT:
            continue
        qty = int(trade["quantity"])
        if trade["buyer"] == "SUBMISSION":
            signed_qty = qty
        elif trade["seller"] == "SUBMISSION":
            signed_qty = -qty
        else:
            continue
        trade_rows.append(
            {
                "timestamp": int(trade["timestamp"]),
                "price": float(trade["price"]),
                "qty": signed_qty,
            }
        )

    trade_rows.sort(key=lambda row: row["timestamp"])
    return activity_rows, trade_rows


def attach_positions(activity_rows: List[dict], trade_rows: List[dict]) -> None:
    running_pos = 0
    trade_idx = 0
    for row in activity_rows:
        while trade_idx < len(trade_rows) and trade_rows[trade_idx]["timestamp"] <= row["timestamp"]:
            running_pos += trade_rows[trade_idx]["qty"]
            trade_idx += 1
        row["position"] = running_pos


def inventory_bucket(abs_pos: int) -> str:
    if abs_pos < 50:
        return "|pos| < 50"
    if abs_pos < 120:
        return "50 <= |pos| < 120"
    return "|pos| >= 120"


def inventory_tables(activity_rows: List[dict]) -> Dict[str, Dict[str, float]]:
    pnl_by_bucket = {"|pos| < 50": 0.0, "50 <= |pos| < 120": 0.0, "|pos| >= 120": 0.0}
    time_by_bucket = {"|pos| < 50": 0.0, "50 <= |pos| < 120": 0.0, "|pos| >= 120": 0.0}

    for left, right in zip(activity_rows, activity_rows[1:]):
        bucket = inventory_bucket(abs(int(left["position"])))
        pnl_by_bucket[bucket] += float(right["pnl"]) - float(left["pnl"])
        time_by_bucket[bucket] += float(right["timestamp"]) - float(left["timestamp"])

    return {"pnl": pnl_by_bucket, "time": time_by_bucket}


def quarter_stats(activity_rows: List[dict]) -> List[dict]:
    max_ts = max(row["timestamp"] for row in activity_rows)
    result: List[dict] = []
    quarter_bounds = [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.0)]
    for lo, hi in quarter_bounds:
        bucket_rows = [
            row
            for row in activity_rows
            if lo <= row["timestamp"] / max_ts < (hi if hi < 1.0 else 1.000001)
        ]
        if not bucket_rows:
            continue
        avg_abs_pos = sum(abs(int(row["position"])) for row in bucket_rows) / len(bucket_rows)
        result.append(
            {
                "window": f"{int(lo * 100)}-{int(hi * 100)}%",
                "pnl_delta": float(bucket_rows[-1]["pnl"]) - float(bucket_rows[0]["pnl"]),
                "avg_abs_pos": avg_abs_pos,
                "max_abs_pos": max(abs(int(row["position"])) for row in bucket_rows),
                "start_pos": int(bucket_rows[0]["position"]),
                "end_pos": int(bucket_rows[-1]["position"]),
            }
        )
    return result


def first_hit_markouts(activity_rows: List[dict], thresholds: Tuple[int, ...] = (150, 180, 200)) -> List[dict]:
    result: List[dict] = []
    for threshold in thresholds:
        episodes: List[Tuple[int, float]] = []
        in_episode = False
        for idx, row in enumerate(activity_rows[:-20]):
            pos = int(row["position"])
            if abs(pos) >= threshold and not in_episode:
                future_mid = float(activity_rows[idx + 20]["mid"])
                episodes.append((pos, future_mid - float(row["mid"])))
                in_episode = True
            elif abs(pos) < threshold:
                in_episode = False

        long_markouts = [markout for pos, markout in episodes if pos > 0]
        short_markouts = [markout for pos, markout in episodes if pos < 0]
        result.append(
            {
                "threshold": threshold,
                "episodes": len(episodes),
                "long_count": len(long_markouts),
                "short_count": len(short_markouts),
                "long_markout_20bars": sum(long_markouts) / len(long_markouts) if long_markouts else None,
                "short_markout_20bars": sum(short_markouts) / len(short_markouts) if short_markouts else None,
            }
        )
    return result


def same_side_stretch_markouts(
    activity_rows: List[dict], trade_rows: List[dict], thresholds: Tuple[int, ...] = (120, 150)
) -> List[dict]:
    activity_ts = [row["timestamp"] for row in activity_rows]
    activity_mid = [float(row["mid"]) for row in activity_rows]

    running_pos = 0
    result: List[dict] = []
    for threshold in thresholds:
        buy_markouts: List[float] = []
        sell_markouts: List[float] = []
        running_pos = 0
        for trade in trade_rows:
            qty = int(trade["qty"])
            pos_before = running_pos
            running_pos += qty
            future_idx = bisect_right(activity_ts, int(trade["timestamp"]) + 2000) - 1
            if future_idx < 0:
                continue
            future_mid = activity_mid[future_idx]
            if qty > 0 and pos_before >= threshold:
                buy_markouts.append(future_mid - float(trade["price"]))
            elif qty < 0 and pos_before <= -threshold:
                sell_markouts.append(float(trade["price"]) - future_mid)

        result.append(
            {
                "threshold": threshold,
                "same_side_buy_fill_count": len(buy_markouts),
                "same_side_buy_markout_20bars": sum(buy_markouts) / len(buy_markouts) if buy_markouts else None,
                "same_side_sell_fill_count": len(sell_markouts),
                "same_side_sell_markout_20bars": sum(sell_markouts) / len(sell_markouts) if sell_markouts else None,
            }
        )
    return result


def build_summary(log_path: Path) -> Dict[str, object]:
    activity_rows, trade_rows = parse_log(log_path)
    if not activity_rows:
        raise ValueError(f"No {PRODUCT} rows found in {log_path}")
    attach_positions(activity_rows, trade_rows)

    final_position = int(activity_rows[-1]["position"])
    max_abs_position = max(abs(int(row["position"])) for row in activity_rows)
    time_ge_150 = 0
    time_ge_200 = 0
    for left, right in zip(activity_rows, activity_rows[1:]):
        dt = int(right["timestamp"]) - int(left["timestamp"])
        if abs(int(left["position"])) >= 150:
            time_ge_150 += dt
        if abs(int(left["position"])) >= 200:
            time_ge_200 += dt

    summary = {
        "log_path": str(log_path),
        "product": PRODUCT,
        "final_pnl": float(activity_rows[-1]["pnl"]),
        "min_pnl": min(float(row["pnl"]) for row in activity_rows),
        "max_pnl": max(float(row["pnl"]) for row in activity_rows),
        "final_position": final_position,
        "max_abs_position": max_abs_position,
        "time_abs_pos_ge_150": time_ge_150,
        "time_abs_pos_ge_200": time_ge_200,
        "inventory_tables": inventory_tables(activity_rows),
        "quarter_stats": quarter_stats(activity_rows),
        "first_hit_markouts": first_hit_markouts(activity_rows),
        "same_side_stretch_markouts": same_side_stretch_markouts(activity_rows, trade_rows),
    }

    summary["interpretation"] = {
        "classification_note": "Hydrogel still behaves like an anchored local-fair inventory trader, not a drift product.",
        "main_risk_note": (
            "The worst hidden-data behavior is same-side accumulation while already stretched and then carrying "
            "near-full inventory too late into the session."
        ),
        "execution_note": (
            "Same-side fills while stretched have strongly negative 20-bar markout, which argues for earlier "
            "same-side blocking, harder late-session clearing, and smaller stretched quote size before any fair rewrite."
        ),
    }
    return summary


def render_markdown(summary: Dict[str, object]) -> str:
    inv = summary["inventory_tables"]
    lines = [
        "# Round 3 Hydrogel Diagnostics",
        "",
        f"Source log: [{Path(str(summary['log_path'])).name}]({str(Path(summary['log_path']).resolve())})",
        "",
        "This report follows the Hydrogel build-order manual:",
        "",
        "```text",
        "Measure -> classify -> tune risk shape -> tune execution -> only then redesign fair/model",
        "```",
        "",
        "## Headline Read",
        "",
        f"- Final PnL: `{summary['final_pnl']}`",
        f"- Min / max PnL: `{summary['min_pnl']} / {summary['max_pnl']}`",
        f"- Final position: `{summary['final_position']}`",
        f"- Max |position|: `{summary['max_abs_position']}`",
        f"- Time with `|pos| >= 150`: `{summary['time_abs_pos_ge_150']}`",
        f"- Time with `|pos| >= 200`: `{summary['time_abs_pos_ge_200']}`",
        "",
        f"- Classification note: {summary['interpretation']['classification_note']}",
        f"- Main risk note: {summary['interpretation']['main_risk_note']}",
        f"- Execution note: {summary['interpretation']['execution_note']}",
        "",
        "## Inventory Bucket PnL",
        "",
    ]

    for bucket in ("|pos| < 50", "50 <= |pos| < 120", "|pos| >= 120"):
        lines.append(f"- `{bucket}`: pnl `{inv['pnl'][bucket]}`, time `{inv['time'][bucket]}`")

    lines.extend(["", "## Session Quarter Stats", ""])
    for row in summary["quarter_stats"]:
        lines.append(
            f"- `{row['window']}`: pnl delta `{row['pnl_delta']}`, avg |pos| `{row['avg_abs_pos']:.2f}`, "
            f"max |pos| `{row['max_abs_pos']}`, start `{row['start_pos']}`, end `{row['end_pos']}`"
        )

    lines.extend(["", "## First-Hit Markouts", ""])
    for row in summary["first_hit_markouts"]:
        lines.append(
            f"- `|pos| >= {row['threshold']}`: episodes `{row['episodes']}`, "
            f"long count `{row['long_count']}`, short count `{row['short_count']}`, "
            f"long 20-bar markout `{row['long_markout_20bars']}`, short 20-bar markout `{row['short_markout_20bars']}`"
        )

    lines.extend(["", "## Same-Side Fill Quality While Stretched", ""])
    for row in summary["same_side_stretch_markouts"]:
        lines.append(
            f"- threshold `{row['threshold']}`: buy fills `{row['same_side_buy_fill_count']}`, "
            f"buy 20-bar markout `{row['same_side_buy_markout_20bars']}`, "
            f"sell fills `{row['same_side_sell_fill_count']}`, "
            f"sell 20-bar markout `{row['same_side_sell_markout_20bars']}`"
        )

    lines.extend(
        [
            "",
            "## Phase B / C Implications",
            "",
            "- Keep the current fair family for now. The measurement still looks like anchored local-fair MM.",
            "- Tighten same-side blocking earlier, because stretched same-side fills are adverse on hidden data.",
            "- Shrink late-session Hydrogel exposure harder. The bot is still carrying near-full inventory too late.",
            "- Make clear behavior more proactive before `|pos|` reaches the worst tail, especially during sign-flip episodes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("Analysis/output/round3_hydrogel_diagnostics"))
    args = parser.parse_args()

    summary = build_summary(args.log_path)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    out_json = out_dir / "summary.json"
    out_md = out_dir / "report.md"
    out_json.write_text(json.dumps(summary, indent=2))
    out_md.write_text(render_markdown(summary))
    print(f"summary: {out_json}")
    print(f"report: {out_md}")


if __name__ == "__main__":
    main()
