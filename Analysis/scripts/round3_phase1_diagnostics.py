from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


PRODUCTS = ["HYDROGEL_PACK", "VELVETFRUIT_EXTRACT"]
TIME_BUCKETS = 6


def top_levels(row: pd.Series, side: str) -> List[tuple[float, float]]:
    levels: List[tuple[float, float]] = []
    for idx in (1, 2, 3):
        px = row.get(f"{side}_price_{idx}")
        vol = row.get(f"{side}_volume_{idx}")
        if pd.notna(px) and pd.notna(vol):
            levels.append((float(px), float(vol)))
    return levels


def compute_row_features(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        bid_levels = top_levels(row, "bid")
        ask_levels = top_levels(row, "ask")
        raw_mid = float(row["mid_price"]) if pd.notna(row["mid_price"]) else math.nan
        bb = bid_levels[0][0] if bid_levels else math.nan
        ba = ask_levels[0][0] if ask_levels else math.nan
        spread = ba - bb if bid_levels and ask_levels else math.nan

        wall_bid = max(bid_levels, key=lambda x: (x[1], x[0]))[0] if bid_levels else math.nan
        wall_ask = min(ask_levels, key=lambda x: (x[1], -x[0]))[0] if ask_levels else math.nan
        wall_mid = 0.5 * (wall_bid + wall_ask) if bid_levels and ask_levels and wall_bid < wall_ask else raw_mid

        bid_vol = sum(vol for _, vol in bid_levels)
        ask_vol = sum(abs(vol) for _, vol in ask_levels)
        thick_bid = sum(px * vol for px, vol in bid_levels) / bid_vol if bid_vol > 0 else math.nan
        thick_ask = sum(px * abs(vol) for px, vol in ask_levels) / ask_vol if ask_vol > 0 else math.nan
        thick_mid = 0.5 * (thick_bid + thick_ask) if pd.notna(thick_bid) and pd.notna(thick_ask) and thick_bid < thick_ask else raw_mid

        top_bid_vol = bid_levels[0][1] if bid_levels else 0.0
        top_ask_vol = abs(ask_levels[0][1]) if ask_levels else 0.0
        total_top = top_bid_vol + top_ask_vol
        micro = ((ba * top_bid_vol) + (bb * top_ask_vol)) / total_top if total_top > 0 and bid_levels and ask_levels else raw_mid
        imbalance = (top_bid_vol - top_ask_vol) / total_top if total_top > 0 else 0.0
        stable = np.nanmean([raw_mid, wall_mid, thick_mid])

        top_depth = total_top
        top3_depth = bid_vol + ask_vol

        rows.append(
            {
                "day": int(row["day"]),
                "timestamp": int(row["timestamp"]),
                "product": row["product"],
                "raw_mid": raw_mid,
                "spread": spread,
                "wall_mid": wall_mid,
                "thick_mid": thick_mid,
                "stable_mid": stable,
                "micro": micro,
                "micro_gap": micro - raw_mid if pd.notna(micro) and pd.notna(raw_mid) else math.nan,
                "stable_gap": stable - raw_mid if pd.notna(stable) and pd.notna(raw_mid) else math.nan,
                "imbalance": imbalance,
                "top_depth": top_depth,
                "top3_depth": top3_depth,
            }
        )

    feat = pd.DataFrame(rows)
    feat["next_mid"] = feat.groupby(["product", "day"])["raw_mid"].shift(-1)
    feat["next_move"] = feat["next_mid"] - feat["raw_mid"]
    feat["mid_ret"] = feat["next_move"] / feat["raw_mid"]
    feat["prev_mid"] = feat.groupby(["product", "day"])["raw_mid"].shift(1)
    feat["abs_mid_move"] = (feat["raw_mid"] - feat["prev_mid"]).abs()
    feat["progress"] = feat["timestamp"] / feat.groupby("day")["timestamp"].transform("max")
    feat["bucket"] = np.minimum((feat["progress"] * TIME_BUCKETS).astype(int), TIME_BUCKETS - 1)
    return feat


def safe_corr(a: pd.Series, b: pd.Series) -> float | None:
    mask = a.notna() & b.notna()
    if mask.sum() < 10:
        return None
    return float(a[mask].corr(b[mask]))


def drift_snr(mid: pd.Series) -> float | None:
    diff = mid.diff().dropna()
    if len(diff) < 20 or diff.std(ddof=1) <= 1e-12:
        return None
    return float(diff.mean() / diff.std(ddof=1) * math.sqrt(len(diff)))


def ar1_half_life(mid: pd.Series) -> float | None:
    clean = mid.dropna()
    if len(clean) < 50:
        return None
    x = clean.values
    x_lag = x[:-1]
    x_now = x[1:]
    x_lag_c = x_lag - x_lag.mean()
    x_now_c = x_now - x_now.mean()
    denom = float(np.dot(x_lag_c, x_lag_c))
    if abs(denom) <= 1e-12:
        return None
    phi = float(np.dot(x_lag_c, x_now_c) / denom)
    if not (0.0 < phi < 1.0):
        return None
    return float(math.log(0.5) / math.log(phi))


def classify_product(metrics: Dict[str, float | None]) -> Dict[str, str]:
    drift = metrics.get("drift_snr")
    mr_half = metrics.get("mean_reversion_half_life")
    micro_corr = metrics.get("micro_gap_corr")
    imb_corr = metrics.get("imbalance_corr")
    stable_gap_std = metrics.get("stable_gap_std")
    spread_mean = metrics.get("spread_mean")
    mean_mid = metrics.get("mean_mid")
    anchor_dist = metrics.get("anchor_dist")

    anchor_candidate = "none"
    if mean_mid is not None and anchor_dist is not None:
        if anchor_dist <= max(8.0, 0.0015 * mean_mid):
            anchor_candidate = "strong"
        elif anchor_dist <= max(18.0, 0.0035 * mean_mid):
            anchor_candidate = "moderate"
        else:
            anchor_candidate = "weak"

    micro_ok = micro_corr is not None and abs(micro_corr) >= 0.08
    imb_ok = imb_corr is not None and abs(imb_corr) >= 0.08
    drift_ok = drift is not None and abs(drift) >= 1.6
    mr_ok = mr_half is not None and mr_half <= 250.0
    stable_ok = stable_gap_std is not None and stable_gap_std <= max(1.2, 0.15 * (spread_mean or 1.0))

    if anchor_candidate == "strong" and (micro_ok or imb_ok):
        primary = "anchored_local_fair_mm"
    elif anchor_candidate in {"strong", "moderate"} and stable_ok:
        primary = "anchored_market_maker"
    elif mr_ok:
        primary = "mean_reverting_candidate"
    elif drift_ok:
        primary = "drift_candidate"
    elif micro_ok or imb_ok:
        primary = "local_fair_microstructure"
    else:
        primary = "mixed_low_conviction"

    notes = []
    if drift_ok:
        notes.append("directional drift is materially present")
    else:
        notes.append("drift signal is weak")
    if mr_ok:
        notes.append("there is usable mean-reversion structure")
    else:
        notes.append("mean-reversion is not strong enough to be the base model")
    if micro_ok or imb_ok:
        notes.append("short-horizon local book state contains predictive information")
    else:
        notes.append("local book predictors are weak")
    if anchor_candidate in {"strong", "moderate"}:
        notes.append(f"the product stays near a {anchor_candidate} anchor")
    else:
        notes.append("the product does not sit tightly on a useful anchor")

    return {
        "primary_classification": primary,
        "anchor_strength": anchor_candidate,
        "execution_style": (
            "Take -> Clear -> Make around a robust stable/wall fair"
            if primary in {"anchored_local_fair_mm", "anchored_market_maker", "local_fair_microstructure"}
            else "safer quoting until product classification is improved further"
        ),
        "notes": "; ".join(notes),
    }


def product_summary(feat: pd.DataFrame, product: str) -> Dict[str, object]:
    sub = feat[feat["product"] == product].copy()
    mean_mid = float(sub["raw_mid"].mean())
    anchor = 10000.0 if product == "HYDROGEL_PACK" else 5250.0
    bucket_vol = (
        sub.groupby("bucket")["mid_ret"]
        .apply(lambda s: float(s.dropna().std(ddof=0) * math.sqrt(len(s.dropna()))) if len(s.dropna()) > 1 else 0.0)
        .to_dict()
    )

    metrics: Dict[str, float | None] = {
        "mean_mid": mean_mid,
        "spread_mean": float(sub["spread"].mean()),
        "spread_std": float(sub["spread"].std(ddof=0)),
        "top_depth_mean": float(sub["top_depth"].mean()),
        "top3_depth_mean": float(sub["top3_depth"].mean()),
        "drift_snr": drift_snr(sub["raw_mid"]),
        "mean_reversion_half_life": ar1_half_life(sub["raw_mid"]),
        "micro_gap_corr": safe_corr(sub["micro_gap"], sub["next_move"]),
        "imbalance_corr": safe_corr(sub["imbalance"], sub["next_move"]),
        "stable_gap_corr": safe_corr(sub["stable_gap"], sub["next_move"]),
        "stable_gap_std": float(sub["stable_gap"].dropna().std(ddof=0)),
        "stable_gap_abs_mean": float(sub["stable_gap"].dropna().abs().mean()),
        "anchor_dist": float(abs(mean_mid - anchor)),
    }

    daily = []
    for day, day_sub in sub.groupby("day"):
        daily.append(
            {
                "day": int(day),
                "drift_snr": drift_snr(day_sub["raw_mid"]),
                "mean_reversion_half_life": ar1_half_life(day_sub["raw_mid"]),
                "micro_gap_corr": safe_corr(day_sub["micro_gap"], day_sub["next_move"]),
                "imbalance_corr": safe_corr(day_sub["imbalance"], day_sub["next_move"]),
                "volatility": float(day_sub["mid_ret"].dropna().std(ddof=0) * math.sqrt(len(day_sub["mid_ret"].dropna())))
                if len(day_sub["mid_ret"].dropna()) > 1
                else None,
            }
        )

    classification = classify_product(metrics)
    return {
        "product": product,
        "anchor_reference": anchor,
        "metrics": metrics,
        "daily_metrics": daily,
        "bucket_realized_volatility": {str(int(k)): float(v) for k, v in bucket_vol.items()},
        **classification,
    }


def render_markdown(results: List[Dict[str, object]], out_path: Path) -> None:
    lines = [
        "# Round 3 Phase 1 Diagnostics",
        "",
        "Base bot under review: [TradervR3_7.py](Bots/Round3/TradervR3_7.py)",
        "",
        "This report is the Phase 1 hard-classification pass for the two delta-1 products.",
        "",
    ]
    for result in results:
        metrics = result["metrics"]
        lines.extend(
            [
                f"## {result['product']}",
                "",
                f"- Primary classification: **{result['primary_classification']}**",
                f"- Anchor reference: `{result['anchor_reference']}`",
                f"- Anchor strength: **{result['anchor_strength']}**",
                f"- Recommended execution style: {result['execution_style']}",
                f"- Interpretation: {result['notes']}",
                "",
                "### Core metrics",
                "",
                f"- Mean mid: `{metrics['mean_mid']:.3f}`",
                f"- Mean spread: `{metrics['spread_mean']:.3f}`",
                f"- Mean top depth: `{metrics['top_depth_mean']:.3f}`",
                f"- Mean top-3 depth: `{metrics['top3_depth_mean']:.3f}`",
                f"- Drift SNR: `{metrics['drift_snr']:.3f}`" if metrics["drift_snr"] is not None else "- Drift SNR: `n/a`",
                (
                    f"- Mean-reversion half-life: `{metrics['mean_reversion_half_life']:.1f}` bars"
                    if metrics["mean_reversion_half_life"] is not None
                    else "- Mean-reversion half-life: `n/a`"
                ),
                f"- Corr(next move, micro gap): `{metrics['micro_gap_corr']:.3f}`" if metrics["micro_gap_corr"] is not None else "- Corr(next move, micro gap): `n/a`",
                f"- Corr(next move, imbalance): `{metrics['imbalance_corr']:.3f}`" if metrics["imbalance_corr"] is not None else "- Corr(next move, imbalance): `n/a`",
                f"- Corr(next move, stable gap): `{metrics['stable_gap_corr']:.3f}`" if metrics["stable_gap_corr"] is not None else "- Corr(next move, stable gap): `n/a`",
                f"- Std(stable mid - raw mid): `{metrics['stable_gap_std']:.4f}`",
                f"- Mean |stable mid - raw mid|: `{metrics['stable_gap_abs_mean']:.4f}`",
                "",
                "### Realized volatility by time bucket",
                "",
            ]
        )
        for bucket, value in result["bucket_realized_volatility"].items():
            lines.append(f"- Bucket `{bucket}`: `{value:.6f}`")
        lines.extend(["", "### Daily metrics", ""])
        for day_metrics in result["daily_metrics"]:
            parts = [f"day `{day_metrics['day']}`"]
            drift = day_metrics["drift_snr"]
            half = day_metrics["mean_reversion_half_life"]
            micro = day_metrics["micro_gap_corr"]
            imb = day_metrics["imbalance_corr"]
            vol = day_metrics["volatility"]
            parts.append(f"drift `{drift:.3f}`" if drift is not None else "drift `n/a`")
            parts.append(f"half-life `{half:.1f}`" if half is not None else "half-life `n/a`")
            parts.append(f"micro corr `{micro:.3f}`" if micro is not None else "micro corr `n/a`")
            parts.append(f"imb corr `{imb:.3f}`" if imb is not None else "imb corr `n/a`")
            parts.append(f"vol `{vol:.6f}`" if vol is not None else "vol `n/a`")
            lines.append(f"- {', '.join(parts)}")
        lines.append("")

    lines.extend(
        [
            "## Phase 1 Takeaways",
            "",
            "- `HYDROGEL_PACK` should only remain strongly anchor-driven if the classification stays anchored after this harder pass.",
            "- `VELVETFRUIT_EXTRACT` must be judged not just on direct alpha, but on how reliable it is as the voucher hedge anchor.",
            "- The next implementation change should be fair-family adjustments only, not new voucher alpha.",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 3 Phase 1 diagnostics for Hydrogel and Velvet.")
    parser.add_argument("--root", default="Data/ROUND_3")
    parser.add_argument("--out-dir", default="Analysis/output/round3_phase1_diagnostics")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    price_files = sorted(root.glob("prices_round_3_day_*.csv"))
    if not price_files:
        raise SystemExit(f"No Round 3 price files found under {root}")

    price_df = pd.concat([pd.read_csv(path, sep=";") for path in price_files], ignore_index=True)
    price_df = price_df[price_df["product"].isin(PRODUCTS)].copy()
    feat = compute_row_features(price_df)

    results = [product_summary(feat, product) for product in PRODUCTS]

    report_path = out_dir / "report.md"
    summary_path = out_dir / "summary.json"
    render_markdown(results, report_path)
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Wrote {report_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
