from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


SUMMARY_FILE = "summary.json"
COMPARE_FILE = "compare_summary.json"
DIAGNOSTICS_FILE = "diagnostics.json"
STEP_LOG_FILE = "step_log.csv"
PRODUCT_LOG_FILE = "product_steps.csv"
FILLS_FILE = "fills.csv"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _parse_scalar(value: str) -> Any:
    text = value.strip()
    if text == "":
        return None
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if re.fullmatch(r"-?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    try:
        return float(text)
    except ValueError:
        return text


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open() as handle:
        reader = csv.DictReader(handle)
        return [{key: _parse_scalar(value) for key, value in row.items()} for row in reader]


def _is_single_run_dir(path: Path) -> bool:
    return (path / SUMMARY_FILE).is_file()


def _is_compare_run_dir(path: Path) -> bool:
    return (path / COMPARE_FILE).is_file()


def _run_mtime_ms(path: Path) -> int:
    candidate_files = [path / COMPARE_FILE, path / SUMMARY_FILE]
    for file_path in candidate_files:
        if file_path.exists():
            return int(file_path.stat().st_mtime_ns // 1_000_000)
    return int(path.stat().st_mtime_ns // 1_000_000)


def _points_from_rows(rows: list[dict[str, Any]], x_key: str, y_key: str) -> list[dict[str, float]]:
    points = []
    for row in rows:
        x_value = row.get(x_key)
        y_value = row.get(y_key)
        if x_value is None or y_value is None:
            continue
        try:
            points.append({"x": float(x_value), "y": float(y_value)})
        except (TypeError, ValueError):
            continue
    return points


def _scatter_points(rows: list[dict[str, Any]], x_key: str, y_key: str) -> list[dict[str, float]]:
    points = []
    for row in rows:
        x_value = row.get(x_key)
        y_value = row.get(y_key)
        if x_value is None or y_value is None:
            continue
        try:
            points.append({"x": float(x_value), "y": float(y_value)})
        except (TypeError, ValueError):
            continue
    return points


def _downsample_points(points: list[dict[str, float]], max_points: int = 800) -> list[dict[str, float]]:
    if len(points) <= max_points:
        return points
    stride = max(1, len(points) // max_points)
    reduced = points[::stride]
    if reduced[-1] != points[-1]:
        reduced.append(points[-1])
    return reduced


def _histogram(values: list[float], bins: int = 24) -> dict[str, Any]:
    if not values:
        return {"bins": [], "min": None, "max": None}
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        return {
            "bins": [{"start": lo - 0.5, "end": hi + 0.5, "count": len(values)}],
            "min": lo,
            "max": hi,
        }
    width = (hi - lo) / bins
    counts = [0 for _ in range(bins)]
    for value in values:
        index = min(bins - 1, int((value - lo) / width))
        counts[index] += 1
    return {
        "bins": [
            {"start": lo + width * idx, "end": lo + width * (idx + 1), "count": counts[idx]}
            for idx in range(bins)
        ],
        "min": lo,
        "max": hi,
    }


def _counter_items(counter: Counter[str]) -> list[dict[str, Any]]:
    return [{"label": label, "value": value} for label, value in sorted(counter.items())]


def _drawdown_points(points: list[dict[str, float]]) -> list[dict[str, float]]:
    peak = float("-inf")
    drawdowns = []
    for point in points:
        peak = max(peak, point["y"])
        drawdowns.append({"x": point["x"], "y": peak - point["y"]})
    return drawdowns


def _collect_run_dirs(root: Path) -> list[Path]:
    root = root.resolve()
    if _is_single_run_dir(root) or _is_compare_run_dir(root):
        return [root]
    candidates = [
        child.resolve()
        for child in root.iterdir()
        if child.is_dir() and (_is_single_run_dir(child) or _is_compare_run_dir(child))
    ]
    candidates.sort(key=_run_mtime_ms, reverse=True)
    return candidates


def _short_bot_name(bot_path: str | None) -> str | None:
    if not bot_path:
        return None
    return Path(bot_path).name


def _single_run_card(path: Path) -> dict[str, Any]:
    summary = _read_json(path / SUMMARY_FILE)
    return {
        "name": path.name,
        "kind": "single",
        "mtimeMs": _run_mtime_ms(path),
        "botPath": summary.get("bot_path"),
        "botName": _short_bot_name(summary.get("bot_path")),
        "mode": summary.get("mode"),
        "queueModel": summary.get("queue_model"),
        "totalPnl": summary.get("total_pnl"),
        "fills": summary.get("total_fills"),
        "steps": summary.get("steps"),
    }


def _compare_run_card(path: Path) -> dict[str, Any]:
    summary = _read_json(path / COMPARE_FILE)
    return {
        "name": path.name,
        "kind": "compare",
        "mtimeMs": _run_mtime_ms(path),
        "botPath": summary.get("bot_path"),
        "botName": _short_bot_name(summary.get("bot_path")),
        "queueModel": summary.get("queue_model"),
        "baselineNoAccessPnl": summary.get("baseline_no_access_pnl"),
        "deltaAccessMean": summary.get("delta_access_mean"),
        "deltaAccessMedian": summary.get("delta_access_median"),
        "accessRunCount": len(summary.get("access_runs", [])),
    }


def collect_runs(root: Path) -> list[dict[str, Any]]:
    runs = []
    for path in _collect_run_dirs(root):
        if _is_compare_run_dir(path):
            runs.append(_compare_run_card(path))
        else:
            runs.append(_single_run_card(path))
    return runs


def _resolve_run_dir(root: Path, run_name: str) -> Path:
    root = root.resolve()
    if (_is_single_run_dir(root) or _is_compare_run_dir(root)) and root.name == run_name:
        return root
    candidate = (root / run_name).resolve()
    if candidate.parent != root or not candidate.is_dir():
        raise FileNotFoundError(f"Run not found: {run_name}")
    return candidate


def _build_product_payload(
    product: str,
    product_rows: list[dict[str, Any]],
    fill_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    product_rows = sorted(product_rows, key=lambda row: row.get("step_index", 0))
    fill_rows = sorted(fill_rows, key=lambda row: row.get("step_index", 0))
    spread_values = [float(row["spread"]) for row in product_rows if row.get("spread") is not None]
    signal_values = [float(row["signal_proxy"]) for row in product_rows if row.get("signal_proxy") is not None]
    imbalance_values = [float(row["imbalance"]) for row in product_rows if row.get("imbalance") is not None]
    access_level_values = [float(row["access_added_levels"]) for row in product_rows if row.get("access_added_levels") is not None]
    markout_values = [float(row["markout"]) for row in fill_rows if row.get("markout") is not None]
    residual_values = [float(row["residual_to_trend"]) for row in fill_rows if row.get("residual_to_trend") is not None]
    buy_fills = [row for row in fill_rows if row.get("side") == "BUY"]
    sell_fills = [row for row in fill_rows if row.get("side") == "SELL"]
    fill_type_counter = Counter(str(row.get("fill_type")) for row in fill_rows if row.get("fill_type"))
    agreement_counter = Counter(str(row.get("agreement_state")) for row in fill_rows if row.get("agreement_state"))
    side_counter = Counter(str(row.get("side")) for row in fill_rows if row.get("side"))

    return {
        "name": product,
        "summary": {
            "fillCount": len(fill_rows),
            "buyCount": len(buy_fills),
            "sellCount": len(sell_fills),
            "finalPnl": product_rows[-1].get("product_pnl") if product_rows else None,
            "finalPosition": product_rows[-1].get("position") if product_rows else None,
            "meanSpread": round(mean(spread_values), 4) if spread_values else None,
            "meanSignal": round(mean(signal_values), 4) if signal_values else None,
            "meanImbalance": round(mean(imbalance_values), 4) if imbalance_values else None,
            "meanMarkout": round(mean(markout_values), 4) if markout_values else None,
        },
        "charts": {
            "pnl": _downsample_points(_points_from_rows(product_rows, "step_index", "product_pnl")),
            "position": _downsample_points(_points_from_rows(product_rows, "step_index", "position")),
            "signal": _downsample_points(_points_from_rows(product_rows, "step_index", "signal_proxy")),
            "imbalance": _downsample_points(_points_from_rows(product_rows, "step_index", "imbalance")),
            "accessLevels": _downsample_points(_points_from_rows(product_rows, "step_index", "access_added_levels")),
            "midPrice": _downsample_points(_points_from_rows(product_rows, "step_index", "mid_price")),
            "buyFills": _scatter_points(buy_fills, "step_index", "price"),
            "sellFills": _scatter_points(sell_fills, "step_index", "price"),
            "spreadHistogram": _histogram(spread_values),
            "signalHistogram": _histogram(signal_values),
            "imbalanceHistogram": _histogram(imbalance_values),
            "markoutHistogram": _histogram(markout_values),
            "residualHistogram": _histogram(residual_values),
            "fillTypes": _counter_items(fill_type_counter),
            "agreementStates": _counter_items(agreement_counter),
            "sideMix": _counter_items(side_counter),
        },
    }


def build_single_run_payload(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    summary = _read_json(run_dir / SUMMARY_FILE)
    diagnostics = _read_json(run_dir / DIAGNOSTICS_FILE) if (run_dir / DIAGNOSTICS_FILE).exists() else {}
    step_rows = _read_csv(run_dir / STEP_LOG_FILE) if (run_dir / STEP_LOG_FILE).exists() else []
    product_rows = _read_csv(run_dir / PRODUCT_LOG_FILE) if (run_dir / PRODUCT_LOG_FILE).exists() else []
    fill_rows = _read_csv(run_dir / FILLS_FILE) if (run_dir / FILLS_FILE).exists() else []

    products = sorted({row.get("product") for row in product_rows if row.get("product")})
    product_payloads = {}
    for product in products:
        product_payloads[product] = _build_product_payload(
            product,
            [row for row in product_rows if row.get("product") == product],
            [row for row in fill_rows if row.get("product") == product],
        )

    markout_values = [float(row["markout"]) for row in fill_rows if row.get("markout") is not None]
    residual_values = [float(row["residual_to_trend"]) for row in fill_rows if row.get("residual_to_trend") is not None]
    micro_gap_values = [float(row["micro_gap"]) for row in fill_rows if row.get("micro_gap") is not None]
    imbalance_values = [float(row["imbalance"]) for row in product_rows if row.get("imbalance") is not None]
    fill_type_counter = Counter(str(row.get("fill_type")) for row in fill_rows if row.get("fill_type"))
    access_counter = Counter(str(row.get("access_source")) for row in fill_rows if row.get("access_source"))
    book_origin_counter = Counter(str(row.get("book_origin")) for row in fill_rows if row.get("book_origin"))
    side_counter = Counter(str(row.get("side")) for row in fill_rows if row.get("side"))
    toxicity_counter = Counter(str(row.get("toxicity_bucket")) for row in fill_rows if row.get("toxicity_bucket"))
    conviction_counter = Counter(str(row.get("conviction_bucket")) for row in fill_rows if row.get("conviction_bucket"))
    agreement_counter = Counter(str(row.get("agreement_state")) for row in fill_rows if row.get("agreement_state"))
    spread_bucket_counter = Counter(str(row.get("spread_bucket")) for row in fill_rows if row.get("spread_bucket"))
    total_pnl_points = _points_from_rows(step_rows, "step_index", "total_pnl")

    product_execution: list[dict[str, Any]] = []
    for product, product_payload in sorted(product_payloads.items()):
        summary_block = product_payload.get("summary", {})
        product_fill_rows = [row for row in fill_rows if row.get("product") == product]
        product_markouts = [float(row["markout"]) for row in product_fill_rows if row.get("markout") is not None]
        product_execution.append(
            {
                "product": product,
                "final_pnl": summary_block.get("finalPnl"),
                "fills": summary_block.get("fillCount"),
                "buy_fills": summary_block.get("buyCount"),
                "sell_fills": summary_block.get("sellCount"),
                "final_position": summary_block.get("finalPosition"),
                "mean_markout": round(mean(product_markouts), 4) if product_markouts else None,
            }
        )

    payload = {
        "kind": "single",
        "name": run_dir.name,
        "path": str(run_dir),
        "mtimeMs": _run_mtime_ms(run_dir),
        "summary": summary,
        "charts": {
            "totalPnl": _downsample_points(total_pnl_points),
            "drawdown": _downsample_points(_drawdown_points(total_pnl_points)),
            "activity": [
                {
                    "label": "Submitted Orders",
                    "points": _downsample_points(_points_from_rows(step_rows, "step_index", "submitted_orders")),
                },
                {
                    "label": "Fills",
                    "points": _downsample_points(_points_from_rows(step_rows, "step_index", "fills")),
                },
                {
                    "label": "Pending Orders",
                    "points": _downsample_points(_points_from_rows(step_rows, "step_index", "pending_orders_next_step")),
                },
            ],
            "markoutAll": _histogram(markout_values),
            "residualAll": _histogram(residual_values),
            "microGapAll": _histogram(micro_gap_values),
            "imbalanceAll": _histogram(imbalance_values),
            "fillTypes": _counter_items(fill_type_counter),
            "accessSources": _counter_items(access_counter),
            "bookOrigins": _counter_items(book_origin_counter),
            "sideMix": _counter_items(side_counter),
            "toxicityBuckets": _counter_items(toxicity_counter),
            "convictionBuckets": _counter_items(conviction_counter),
            "agreementStates": _counter_items(agreement_counter),
            "spreadBuckets": _counter_items(spread_bucket_counter),
        },
        "products": product_payloads,
        "diagnostics": diagnostics,
        "tables": {
            "osmiumBuckets": [
                {
                    "bucket": key,
                    **value,
                }
                for key, value in sorted(diagnostics.get("osmium_buckets", {}).items())
            ],
            "plateauWindows": diagnostics.get("plateau_windows", []),
            "pepper": diagnostics.get("pepper", {}),
            "productExecution": product_execution,
        },
    }
    return payload


def _aggregate_access_series(run_dir: Path, child_names: list[str]) -> dict[str, Any]:
    baseline_step_rows = _read_csv(run_dir / "no_access" / STEP_LOG_FILE)
    baseline_series = _downsample_points(_points_from_rows(baseline_step_rows, "step_index", "total_pnl"))
    per_step_access: dict[int, list[float]] = defaultdict(list)
    for child_name in child_names:
        child_steps = _read_csv(run_dir / child_name / STEP_LOG_FILE)
        for row in child_steps:
            step_index = row.get("step_index")
            total_pnl = row.get("total_pnl")
            if step_index is None or total_pnl is None:
                continue
            per_step_access[int(step_index)].append(float(total_pnl))
    envelope = []
    for step_index in sorted(per_step_access):
        values = per_step_access[step_index]
        envelope.append(
            {
                "x": float(step_index),
                "mean": mean(values),
                "min": min(values),
                "max": max(values),
            }
        )
    return {
        "baseline": baseline_series,
        "accessEnvelope": _downsample_points([{"x": item["x"], "y": item["mean"]} for item in envelope]),
        "accessBand": _downsample_points(
            [{"x": item["x"], "min": item["min"], "max": item["max"]} for item in envelope]
        ),
    }


def build_compare_run_payload(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    summary = _read_json(run_dir / COMPARE_FILE)
    child_dirs = [
        child.name
        for child in sorted(run_dir.iterdir())
        if child.is_dir() and _is_single_run_dir(child)
    ]
    access_child_names = [name for name in child_dirs if name.startswith("access_seed_")]
    baseline_summary = _read_json(run_dir / "no_access" / SUMMARY_FILE) if (run_dir / "no_access" / SUMMARY_FILE).exists() else {}

    access_pnls = [float(item.get("total_pnl", 0.0)) for item in summary.get("access_runs", [])]
    delta_values = [float(value) for value in summary.get("delta_access_values", [])]

    per_product_delta_items = []
    baseline_per_product = baseline_summary.get("per_product_pnl", {})
    if access_child_names and baseline_per_product:
        product_values: dict[str, list[float]] = defaultdict(list)
        for child_name in access_child_names:
            child_summary = _read_json(run_dir / child_name / SUMMARY_FILE)
            for product, value in child_summary.get("per_product_pnl", {}).items():
                if product not in baseline_per_product:
                    continue
                product_values[product].append(float(value) - float(baseline_per_product[product]))
        for product, values in sorted(product_values.items()):
            per_product_delta_items.append(
                {
                    "label": product,
                    "mean": round(mean(values), 4) if values else 0.0,
                    "min": round(min(values), 4) if values else 0.0,
                    "max": round(max(values), 4) if values else 0.0,
                }
            )

    aggregate_series = _aggregate_access_series(run_dir, access_child_names) if access_child_names else {
        "baseline": [],
        "accessEnvelope": [],
        "accessBand": [],
    }

    return {
        "kind": "compare",
        "name": run_dir.name,
        "path": str(run_dir),
        "mtimeMs": _run_mtime_ms(run_dir),
        "summary": summary,
        "children": [
            {
                "name": child_name,
                "kind": "single",
                "summary": _read_json(run_dir / child_name / SUMMARY_FILE),
            }
            for child_name in child_dirs
        ],
        "charts": {
            "deltaHistogram": _histogram(delta_values),
            "accessPnlHistogram": _histogram(access_pnls),
            "perSeedTotals": [
                {
                    "label": f"seed {item.get('access_seed')}",
                    "value": item.get("total_pnl"),
                    "delta": round(float(item.get("total_pnl", 0.0)) - float(summary.get("baseline_no_access_pnl", 0.0)), 4),
                }
                for item in summary.get("access_runs", [])
            ],
            "perProductDelta": per_product_delta_items,
            "aggregateSeries": aggregate_series,
        },
        "defaultChild": "no_access" if "no_access" in child_dirs else (child_dirs[0] if child_dirs else None),
    }


def build_run_payload(root: Path, run_name: str, child: str | None = None) -> dict[str, Any]:
    run_dir = _resolve_run_dir(root, run_name)
    if child:
        child_dir = (run_dir / child).resolve()
        if child_dir.parent != run_dir or not _is_single_run_dir(child_dir):
            raise FileNotFoundError(f"Child run not found: {child}")
        return build_single_run_payload(child_dir)
    if _is_compare_run_dir(run_dir):
        return build_compare_run_payload(run_dir)
    if _is_single_run_dir(run_dir):
        return build_single_run_payload(run_dir)
    raise FileNotFoundError(f"Run data not found in {run_dir}")
