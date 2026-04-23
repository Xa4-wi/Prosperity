from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from olivia_common import (
        CandidateScore,
        QuantityCluster,
        TradeFeature,
        score_candidate_clusters,
        scores_to_rows,
        write_csv_rows,
        write_json,
    )
else:
    try:
        from ..olivia_common import (
            CandidateScore,
            QuantityCluster,
            TradeFeature,
            score_candidate_clusters,
            scores_to_rows,
            write_csv_rows,
            write_json,
        )
    except ImportError:
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from olivia_common import (
            CandidateScore,
            QuantityCluster,
            TradeFeature,
            score_candidate_clusters,
            scores_to_rows,
            write_csv_rows,
            write_json,
        )


def _parse_float(value: str) -> float | None:
    if value == "" or value is None:
        return None
    return float(value)


def _parse_int(value: str) -> int | None:
    if value == "" or value is None:
        return None
    return int(float(value))


def load_features(path: Path) -> list[TradeFeature]:
    features: list[TradeFeature] = []
    with path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            markouts = {
                key.removeprefix("markout_"): _parse_float(value)
                for key, value in row.items()
                if key.startswith("markout_")
            }
            features.append(
                TradeFeature(
                    day=int(row["day"]),
                    timestamp=int(row["timestamp"]),
                    product=row["product"],
                    buyer=row["buyer"],
                    seller=row["seller"],
                    price=float(row["price"]),
                    quantity=int(row["quantity"]),
                    inferred_side=row["inferred_side"],
                    best_bid=_parse_float(row["best_bid"]),
                    best_ask=_parse_float(row["best_ask"]),
                    mid_price=_parse_float(row["mid_price"]),
                    distance_to_mid=_parse_float(row["distance_to_mid"]),
                    distance_to_best_bid=_parse_float(row["distance_to_best_bid"]),
                    distance_to_best_ask=_parse_float(row["distance_to_best_ask"]),
                    is_new_daily_low_trade=row["is_new_daily_low_trade"] == "True",
                    is_new_daily_high_trade=row["is_new_daily_high_trade"] == "True",
                    markouts=markouts,
                    persistence_bars=int(row["persistence_bars"]),
                    cluster_center=_parse_int(row.get("cluster_center")),
                    cluster_min=_parse_int(row.get("cluster_min")),
                    cluster_max=_parse_int(row.get("cluster_max")),
                )
            )
    return features


def load_clusters(path: Path) -> dict[str, list[QuantityCluster]]:
    payload = json.loads(path.read_text())
    clusters_by_product: dict[str, list[QuantityCluster]] = {}
    for product, clusters in payload.items():
        clusters_by_product[product] = [QuantityCluster(**cluster) for cluster in clusters]
    return clusters_by_product


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score Olivia-style candidate clusters from discovery artifacts.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Discovery output directory.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Where score artifacts should be written.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir or input_dir
    features = load_features(input_dir / "trade_features.csv")
    clusters_by_product = load_clusters(input_dir / "quantity_clusters.json")
    scores: list[CandidateScore] = score_candidate_clusters(features, clusters_by_product)

    write_csv_rows(output_dir / "candidate_scores.csv", scores_to_rows(scores))
    write_json(output_dir / "candidate_scores.json", [score.to_row() for score in scores])
    print(f"Wrote candidate scores to {output_dir}")


if __name__ == "__main__":
    main()
