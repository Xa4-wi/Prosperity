from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from olivia_common import (
        TradeFeature,
        extremum_side_match,
        load_price_series,
        write_json,
    )
    from olivia_research.score_candidates import load_features
else:
    try:
        from ..olivia_common import (
            TradeFeature,
            extremum_side_match,
            load_price_series,
            write_json,
        )
        from .score_candidates import load_features
    except ImportError:
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from olivia_common import (
            TradeFeature,
            extremum_side_match,
            load_price_series,
            write_json,
        )
        from olivia_research.score_candidates import load_features


def load_scores(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def proxy_follow_pnl(
    features: list[TradeFeature],
    price_series_by_key,
    cluster_center: int,
    max_persistence_bars: int,
) -> float:
    grouped_features: dict[tuple[int, str], list[TradeFeature]] = defaultdict(list)
    for feature in features:
        if feature.cluster_center == cluster_center and extremum_side_match(feature):
            grouped_features[(feature.day, feature.product)].append(feature)

    total_pnl = 0.0
    for key, event_features in grouped_features.items():
        series = price_series_by_key.get(key)
        if series is None or not series.snapshots:
            continue
        events = sorted(event_features, key=lambda feature: feature.timestamp)
        current_signal = 0
        signal_expiry = -1
        event_index = 0
        previous_mid = None
        for snapshot in series.snapshots:
            while event_index < len(events) and events[event_index].timestamp <= snapshot.timestamp:
                event = events[event_index]
                if event.inferred_side == "BUY":
                    current_signal = 1
                    signal_expiry = event.timestamp + max_persistence_bars * 100
                elif event.inferred_side == "SELL":
                    current_signal = -1
                    signal_expiry = event.timestamp + max_persistence_bars * 100
                event_index += 1
            if snapshot.timestamp > signal_expiry:
                current_signal = 0
            if previous_mid is not None and snapshot.mid_price is not None:
                total_pnl += current_signal * (snapshot.mid_price - previous_mid)
            if snapshot.mid_price is not None:
                previous_mid = snapshot.mid_price
    return total_pnl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate per-product Olivia-style candidates and build recommendations.")
    parser.add_argument("--data-root", type=Path, default=Path("Data"), help="Root data directory.")
    parser.add_argument("--round-dir", type=str, required=True, help="Round directory inside data root.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory with discovery and score artifacts.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for validation artifacts.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir or input_dir
    features = load_features(input_dir / "trade_features.csv")
    scores = load_scores(input_dir / "candidate_scores.json")
    price_series_by_key = load_price_series(args.data_root, args.round_dir)

    best_by_product: dict[str, dict] = {}
    for score in scores:
        product = score["product"]
        current = best_by_product.get(product)
        if current is None or score["candidate_score"] > current["candidate_score"]:
            best_by_product[product] = score

    validations: list[dict] = []
    report_lines = ["# Olivia-style Product Validation", ""]
    for product, score in sorted(best_by_product.items()):
        cluster_center = int(score["cluster_center"])
        max_persistence_bars = max(1, int(round(float(score["avg_signal_persistence_bars"]) / 100.0)))
        product_features = [feature for feature in features if feature.product == product]
        signal_proxy_pnl = proxy_follow_pnl(
            product_features,
            price_series_by_key,
            cluster_center=cluster_center,
            max_persistence_bars=max_persistence_bars,
        )
        validation = {
            **score,
            "signal_proxy_pnl": signal_proxy_pnl,
            "entry_confidence": round(min(0.95, 0.45 + 0.40 * float(score["directional_correctness"])), 3),
            "exit_confidence": round(max(0.20, 0.55 - 0.25 * float(score["directional_correctness"])), 3),
            "max_persistence": int(max(200, round(float(score["avg_signal_persistence_bars"]) / 100.0) * 100)),
            "lot_cluster": {
                "center": cluster_center,
                "min": int(score["cluster_min"]),
                "max": int(score["cluster_max"]),
            },
        }
        validations.append(validation)
        report_lines.extend(
            [
                f"## {product}",
                f"- Candidate lot cluster: `{score['cluster_min']}-{score['cluster_max']}` (center `{cluster_center}`)",
                f"- Buy-at-lows precision: `{float(score['buy_at_lows_precision']):.3f}`",
                f"- Sell-at-highs precision: `{float(score['sell_at_highs_precision']):.3f}`",
                f"- Directional correctness: `{float(score['directional_correctness']):.3f}`",
                f"- Avg signal persistence: `{float(score['avg_signal_persistence_bars']):.1f}` bars",
                f"- Candidate score: `{float(score['candidate_score']):.3f}`",
                f"- Recommended runtime mode: `{score['recommended_mode']}`",
                f"- Follow-signal PnL proxy: `{signal_proxy_pnl:.2f}`",
                "",
            ]
        )

    write_json(output_dir / "validated_products.json", validations)
    (output_dir / "validated_products_report.md").write_text("\n".join(report_lines))
    print(f"Wrote validation artifacts to {output_dir}")


if __name__ == "__main__":
    main()
