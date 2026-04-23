from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from olivia_common import (
        DEFAULT_MARKOUT_BARS,
        assign_quantity_clusters,
        build_trade_features,
        clusters_to_payload,
        ensure_dir,
        features_to_rows,
        write_csv_rows,
        write_json,
    )
else:
    from ..olivia_common import (
        DEFAULT_MARKOUT_BARS,
        assign_quantity_clusters,
        build_trade_features,
        clusters_to_payload,
        ensure_dir,
        features_to_rows,
        write_csv_rows,
        write_json,
    )


def parse_markout_bars(value: str) -> tuple[int, ...]:
    if not value:
        return DEFAULT_MARKOUT_BARS
    return tuple(sorted(int(part.strip()) for part in value.split(",") if part.strip()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover Olivia-style candidate lot clusters from historical round data.")
    parser.add_argument("--data-root", type=Path, default=Path("Data"), help="Root data directory.")
    parser.add_argument("--round-dir", type=str, required=True, help="Round directory inside data root, e.g. ROUND_2.")
    parser.add_argument("--output-dir", type=Path, default=Path("Bots/Tools/output/olivia_discovery"), help="Directory for discovery artifacts.")
    parser.add_argument("--markout-bars", type=str, default="5,20,50", help="Comma-separated future horizons in bars.")
    parser.add_argument("--lot-tolerance", type=int, default=1, help="Tolerance when clustering repeated lot sizes.")
    parser.add_argument("--min-occurrences", type=int, default=3, help="Minimum occurrences for a lot-size cluster.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = ensure_dir(args.output_dir)
    markout_bars = parse_markout_bars(args.markout_bars)

    features = build_trade_features(args.data_root, args.round_dir, markout_bars=markout_bars)
    clusters_by_product = assign_quantity_clusters(
        features,
        tolerance=args.lot_tolerance,
        min_occurrences=args.min_occurrences,
    )

    write_csv_rows(output_dir / "trade_features.csv", features_to_rows(features))
    write_json(output_dir / "quantity_clusters.json", clusters_to_payload(clusters_by_product))
    write_json(
        output_dir / "discovery_summary.json",
        {
            "round_dir": args.round_dir,
            "markout_bars": list(markout_bars),
            "lot_tolerance": args.lot_tolerance,
            "min_occurrences": args.min_occurrences,
            "feature_count": len(features),
            "products": sorted(clusters_by_product.keys()),
        },
    )
    print(f"Wrote discovery artifacts to {output_dir}")


if __name__ == "__main__":
    main()
