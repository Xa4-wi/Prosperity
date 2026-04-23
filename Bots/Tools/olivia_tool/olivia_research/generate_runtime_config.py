from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate runtime config for the Olivia-style live detector.")
    parser.add_argument("--input", type=Path, required=True, help="validated_products.json path")
    parser.add_argument("--output", type=Path, default=Path("Bots/Tools/olivia_tool/output/olivia_runtime_config.json"), help="Runtime config JSON output.")
    parser.add_argument("--min-mode", type=str, default="BIAS_ONLY", choices=["IGNORE", "BIAS_ONLY", "FOLLOW_AFTER_TRIGGER", "FULL_FOLLOW"], help="Minimum mode to include in runtime config.")
    return parser


MODE_ORDER = {
    "IGNORE": 0,
    "BIAS_ONLY": 1,
    "FOLLOW_AFTER_TRIGGER": 2,
    "FULL_FOLLOW": 3,
}


def main() -> None:
    args = build_parser().parse_args()
    validated = json.loads(args.input.read_text())
    min_mode_rank = MODE_ORDER[args.min_mode]

    config: dict[str, dict] = {}
    for item in validated:
        mode = item["recommended_mode"]
        if MODE_ORDER[mode] < min_mode_rank:
            continue
        config[item["product"]] = {
            "lot_cluster": int(item["lot_cluster"]["center"]),
            "lot_cluster_min": int(item["lot_cluster"]["min"]),
            "lot_cluster_max": int(item["lot_cluster"]["max"]),
            "mode": mode,
            "entry_confidence": float(item["entry_confidence"]),
            "exit_confidence": float(item["exit_confidence"]),
            "max_persistence": int(item["max_persistence"]),
            "basket_bias_weight": round(min(0.75, max(0.15, float(item["directional_correctness"]) * 0.5)), 3),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2, sort_keys=True))
    print(f"Wrote runtime config to {args.output}")


if __name__ == "__main__":
    main()
