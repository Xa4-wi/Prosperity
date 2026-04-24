#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


EPS = 1e-9


@dataclass
class Sample:
    label: str
    local_metrics_path: Path
    official_log_path: Path
    local_total: float
    local_by_product: Dict[str, float]
    online_total: float
    online_by_product: Dict[str, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Round 3 calibration layer from official submission logs and local "
            "backtest metrics, then score candidate runs with calibrated product weights."
        )
    )
    parser.add_argument(
        "--sample",
        action="append",
        nargs=3,
        metavar=("LABEL", "LOCAL_METRICS_JSON", "OFFICIAL_LOG"),
        required=True,
        help="Labeled bot sample with both a local backtest metrics.json and an official portal .log file.",
    )
    parser.add_argument(
        "--candidate",
        action="append",
        nargs=2,
        metavar=("LABEL", "LOCAL_METRICS_JSON"),
        help="Optional candidate run to score with the calibrated weights. Defaults to the samples themselves.",
    )
    parser.add_argument("--out-md", default="", help="Optional markdown report output path.")
    parser.add_argument("--out-json", default="", help="Optional JSON summary output path.")
    return parser.parse_args()


def parse_local_metrics(path: Path) -> tuple[float, Dict[str, float]]:
    obj = json.loads(path.read_text())
    by_product = obj.get("final_pnl_by_product") or obj.get("pnl_by_product")
    if not isinstance(by_product, dict):
        raise ValueError(f"Unsupported metrics format: {path}")
    total = obj.get("final_pnl_total")
    if total is None:
        total = float(sum(float(v) for v in by_product.values()))
    return float(total), {str(k): float(v) for k, v in by_product.items()}


def parse_official_log(path: Path) -> tuple[float, Dict[str, float]]:
    obj = json.loads(path.read_text())
    activities = obj.get("activitiesLog")
    if not isinstance(activities, str) or not activities.strip():
        raise ValueError(f"Official log missing activitiesLog: {path}")
    rows = csv.DictReader(io.StringIO(activities), delimiter=";")
    by_product: Dict[str, float] = {}
    for row in rows:
        product = row["product"]
        by_product[product] = float(row["profit_and_loss"])
    return float(sum(by_product.values())), by_product


def load_samples(sample_specs: Sequence[Sequence[str]]) -> List[Sample]:
    samples: List[Sample] = []
    for label, metrics_path, log_path in sample_specs:
        metrics = Path(metrics_path).resolve()
        official = Path(log_path).resolve()
        local_total, local_by_product = parse_local_metrics(metrics)
        online_total, online_by_product = parse_official_log(official)
        samples.append(
            Sample(
                label=label,
                local_metrics_path=metrics,
                official_log_path=official,
                local_total=local_total,
                local_by_product=local_by_product,
                online_total=online_total,
                online_by_product=online_by_product,
            )
        )
    return samples


def sign(x: float) -> int:
    if x > EPS:
        return 1
    if x < -EPS:
        return -1
    return 0


def all_products(samples: Iterable[Sample]) -> List[str]:
    products = set()
    for sample in samples:
        products.update(sample.local_by_product)
        products.update(sample.online_by_product)
    return sorted(products)


def build_product_stats(samples: Sequence[Sample]) -> Dict[str, dict]:
    products = all_products(samples)
    stats: Dict[str, dict] = {}
    for product in products:
        informative = 0
        agree = 0
        mismatch = 0
        neutral = 0
        local_abs_deltas: List[float] = []
        online_abs_deltas: List[float] = []
        pair_rows: List[dict] = []

        for left, right in combinations(samples, 2):
            local_delta = right.local_by_product.get(product, 0.0) - left.local_by_product.get(product, 0.0)
            online_delta = right.online_by_product.get(product, 0.0) - left.online_by_product.get(product, 0.0)
            s_local = sign(local_delta)
            s_online = sign(online_delta)
            local_abs_deltas.append(abs(local_delta))
            online_abs_deltas.append(abs(online_delta))

            if s_local == 0 and s_online == 0:
                neutral += 1
                relation = "neutral"
            elif s_local == 0 or s_online == 0:
                informative += 1
                mismatch += 1
                relation = "flat_mismatch"
            elif s_local == s_online:
                informative += 1
                agree += 1
                relation = "agree"
            else:
                informative += 1
                mismatch += 1
                relation = "mismatch"

            pair_rows.append(
                {
                    "left": left.label,
                    "right": right.label,
                    "local_delta": local_delta,
                    "online_delta": online_delta,
                    "relation": relation,
                }
            )

        agreement_rate = 0.0 if informative == 0 else agree / informative
        local_signal = max(local_abs_deltas, default=0.0)
        online_signal = max(online_abs_deltas, default=0.0)

        if informative == 0:
            class_label = "unproven"
            score_weight = 0.0
        elif agreement_rate >= 0.999:
            class_label = "trustworthy"
            score_weight = 1.0
        elif agreement_rate >= 0.5:
            class_label = "mixed"
            score_weight = 0.35
        else:
            class_label = "misleading"
            score_weight = 0.0

        stats[product] = {
            "informative_pairs": informative,
            "agree_pairs": agree,
            "mismatch_pairs": mismatch,
            "neutral_pairs": neutral,
            "agreement_rate": agreement_rate,
            "local_max_abs_delta": local_signal,
            "online_max_abs_delta": online_signal,
            "class": class_label,
            "score_weight": score_weight,
            "pairs": pair_rows,
        }
    return stats


def score_candidate(label: str, metrics_path: Path, product_stats: Dict[str, dict]) -> dict:
    local_total, by_product = parse_local_metrics(metrics_path)
    weighted_contribs = {}
    calibrated_total = 0.0
    for product, pnl in by_product.items():
        weight = float(product_stats.get(product, {}).get("score_weight", 0.0))
        contrib = pnl * weight
        weighted_contribs[product] = {
            "local_pnl": pnl,
            "weight": weight,
            "calibrated_contribution": contrib,
        }
        calibrated_total += contrib
    return {
        "label": label,
        "metrics_path": str(metrics_path),
        "raw_total": local_total,
        "calibrated_total": calibrated_total,
        "by_product": weighted_contribs,
    }


def render_markdown(samples: Sequence[Sample], product_stats: Dict[str, dict], candidates: Sequence[dict]) -> str:
    lines: List[str] = []
    lines.append("# Round 3 Backtest Calibration")
    lines.append("")
    lines.append("This report compares local public-data backtests against official submission logs and builds a calibrated selection score.")
    lines.append("")
    lines.append("## Samples")
    lines.append("")
    lines.append("| Label | Local total | Official total |")
    lines.append("|---|---:|---:|")
    for sample in samples:
        lines.append(f"| {sample.label} | {sample.local_total:.2f} | {sample.online_total:.2f} |")

    lines.append("")
    lines.append("## Product Reliability")
    lines.append("")
    lines.append("| Product | Class | Weight | Agreement | Notes |")
    lines.append("|---|---|---:|---:|---|")
    for product, stat in sorted(product_stats.items()):
        note = ""
        if stat["class"] == "trustworthy":
            note = "Local sign matched official sign on all informative pairs."
        elif stat["class"] == "misleading":
            note = "Local deltas pointed the wrong way; ignore in calibrated ranking."
        elif stat["class"] == "mixed":
            note = "Some signal, but not stable enough to trust fully."
        else:
            note = "Not enough evidence yet."
        lines.append(
            f"| {product} | {stat['class']} | {stat['score_weight']:.2f} | {stat['agreement_rate']:.2f} | {note} |"
        )

    lines.append("")
    lines.append("## Candidate Scores")
    lines.append("")
    lines.append("| Label | Raw local total | Calibrated total |")
    lines.append("|---|---:|---:|")
    for candidate in sorted(candidates, key=lambda item: item["calibrated_total"], reverse=True):
        lines.append(f"| {candidate['label']} | {candidate['raw_total']:.2f} | {candidate['calibrated_total']:.2f} |")

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- The calibrated score is a selector, not a hidden-book simulator.")
    lines.append("- Products labeled `misleading` are currently downweighted to zero because the local replay ranked them the wrong way versus official logs.")
    lines.append("- As more official logs arrive, these weights should be recomputed rather than hardcoded.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    samples = load_samples(args.sample)
    product_stats = build_product_stats(samples)

    candidate_specs = args.candidate or [[sample.label, str(sample.local_metrics_path)] for sample in samples]
    candidates = [
        score_candidate(label, Path(metrics_path).resolve(), product_stats)
        for label, metrics_path in candidate_specs
    ]

    payload = {
        "samples": [
            {
                "label": sample.label,
                "local_metrics_path": str(sample.local_metrics_path),
                "official_log_path": str(sample.official_log_path),
                "local_total": sample.local_total,
                "online_total": sample.online_total,
                "local_by_product": sample.local_by_product,
                "online_by_product": sample.online_by_product,
            }
            for sample in samples
        ],
        "product_stats": product_stats,
        "candidates": candidates,
    }
    markdown = render_markdown(samples, product_stats, candidates)

    print(markdown)
    if args.out_md:
        out_md = Path(args.out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(markdown + "\n")
    if args.out_json:
        out_json = Path(args.out_json).resolve()
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
