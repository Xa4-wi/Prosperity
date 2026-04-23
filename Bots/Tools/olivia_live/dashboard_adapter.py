from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from olivia_common import write_json
    from olivia_live.detector import OliviaRuntimeDetector
    from olivia_live.signal_state import ProductRuntimeConfig, UsageMode
    from olivia_research.score_candidates import load_features
else:
    try:
        from ..olivia_common import write_json
        from .detector import OliviaRuntimeDetector
        from .signal_state import ProductRuntimeConfig, UsageMode
        from ..olivia_research.score_candidates import load_features
    except ImportError:
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from olivia_common import write_json
        from olivia_live.detector import OliviaRuntimeDetector
        from olivia_live.signal_state import ProductRuntimeConfig, UsageMode
        from olivia_research.score_candidates import load_features


def histogram(values: list[float], bins: int = 16) -> list[dict]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        return [{"start": lo - 0.5, "end": hi + 0.5, "count": len(values)}]
    width = (hi - lo) / bins
    counts = [0 for _ in range(bins)]
    for value in values:
        index = min(bins - 1, max(0, int((value - lo) / width)))
        counts[index] += 1
    return [
        {"start": lo + width * idx, "end": lo + width * (idx + 1), "count": counts[idx]}
        for idx in range(bins)
    ]


def build_configs(validated: list[dict]) -> dict[str, ProductRuntimeConfig]:
    configs: dict[str, ProductRuntimeConfig] = {}
    for item in validated:
        configs[item["product"]] = ProductRuntimeConfig(
            product=item["product"],
            lot_cluster=int(item["lot_cluster"]["center"]),
            lot_cluster_min=int(item["lot_cluster"]["min"]),
            lot_cluster_max=int(item["lot_cluster"]["max"]),
            mode=UsageMode(item["recommended_mode"]),
            entry_confidence=float(item["entry_confidence"]),
            exit_confidence=float(item["exit_confidence"]),
            max_persistence=int(item["max_persistence"]),
            basket_bias_weight=float(item.get("basket_bias_weight", 0.0)),
        )
    return configs


def build_payload(features, validated: list[dict]) -> dict:
    configs = build_configs(validated)
    detector = OliviaRuntimeDetector(configs)
    validated_by_product = {item["product"]: item for item in validated}

    grouped_features: dict[str, list] = defaultdict(list)
    for feature in features:
        if feature.product in configs:
            grouped_features[feature.product].append(feature)
    for product in grouped_features:
        grouped_features[product].sort(key=lambda item: (item.day, item.timestamp))

    payload = {"products": {}}
    for product, product_features in sorted(grouped_features.items()):
        config = configs[product]
        validated_item = validated_by_product[product]
        detector.reset_day(product)
        last_day = None
        trade_points = []
        candidate_points = []
        confidence_points = []
        low_points = []
        high_points = []
        markout_values = []
        for feature in product_features:
            if last_day is None or feature.day != last_day:
                detector.reset_day(product)
                last_day = feature.day
            state = detector.on_trade(
                product=product,
                timestamp=feature.timestamp,
                price=feature.price,
                quantity=feature.quantity,
                buyer=feature.buyer,
                seller=feature.seller,
                prev_best_bid=feature.best_bid,
                prev_best_ask=feature.best_ask,
                prev_mid=feature.mid_price,
            )
            x = int(feature.day * 1_000_000 + feature.timestamp)
            trade_points.append({"x": x, "y": feature.price, "side": feature.inferred_side})
            low_points.append({"x": x, "y": state.day_low_trade})
            high_points.append({"x": x, "y": state.day_high_trade})
            confidence_points.append({"x": x, "y": round(state.confidence, 4), "signal": state.signal_state.value})
            if config.quantity_in_cluster(feature.quantity):
                candidate_points.append(
                    {
                        "x": x,
                        "y": feature.price,
                        "side": feature.inferred_side,
                        "newLow": feature.is_new_daily_low_trade,
                        "newHigh": feature.is_new_daily_high_trade,
                        "quantity": feature.quantity,
                    }
                )
                markout = feature.markouts.get("20")
                if markout is not None:
                    markout_values.append(markout)
        payload["products"][product] = {
            "summary": {
                "recommendedMode": validated_item["recommended_mode"],
                "candidateScore": round(float(validated_item["candidate_score"]), 4),
                "directionalCorrectness": round(float(validated_item["directional_correctness"]), 4),
                "buyAtLowsPrecision": round(float(validated_item["buy_at_lows_precision"]), 4),
                "sellAtHighsPrecision": round(float(validated_item["sell_at_highs_precision"]), 4),
                "avgPersistenceBars": round(float(validated_item["avg_signal_persistence_bars"]), 1),
                "signalProxyPnl": round(float(validated_item["signal_proxy_pnl"]), 2),
                "lotCluster": validated_item["lot_cluster"],
            },
            "series": {
                "trades": trade_points,
                "candidates": candidate_points,
                "dayLow": low_points,
                "dayHigh": high_points,
                "confidence": confidence_points,
            },
            "histograms": {
                "markout20": histogram(markout_values),
            },
        }
    return payload


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Olivia Detector Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f7f7f7; color: #111; }
    h1, h2 { margin: 0 0 12px; }
    .row { display: flex; gap: 16px; flex-wrap: wrap; }
    .card { background: white; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 16px; }
    .summary { display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
    .metric { background: #fafafa; border-radius: 8px; padding: 10px; }
    .label { font-size: 12px; color: #666; margin-bottom: 4px; }
    .value { font-size: 18px; font-weight: 700; }
    select { padding: 8px 10px; font-size: 14px; margin-bottom: 16px; }
    svg { width: 100%; height: 280px; background: #fff; border: 1px solid #e5e5e5; border-radius: 8px; }
    .chart-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; }
    .note { color: #666; font-size: 13px; margin-top: 8px; }
    .legend { display: flex; gap: 12px; font-size: 12px; color: #444; margin: 8px 0 0; flex-wrap: wrap; }
    .legend span::before { content: ""; display: inline-block; width: 10px; height: 10px; margin-right: 6px; border-radius: 999px; vertical-align: middle; }
    .trades::before { background: #111; }
    .candidates::before { background: #0a7; }
    .lows::before { background: #1565c0; }
    .highs::before { background: #c62828; }
    .confidence::before { background: #6a1b9a; }
    table { width: 100%; border-collapse: collapse; }
    td, th { text-align: left; padding: 8px; border-bottom: 1px solid #eee; font-size: 13px; }
  </style>
</head>
<body>
  <h1>Olivia Detector Dashboard</h1>
  <p class="note">Offline discovery, runtime confidence replay, and per-product candidate review.</p>
  <label for="productSelect">Product</label><br />
  <select id="productSelect"></select>
  <div id="summary" class="summary"></div>
  <div class="row">
    <div class="card" style="flex: 2 1 720px;">
      <div class="chart-title">Trade price, daily extremes, and candidate prints</div>
      <svg id="priceChart"></svg>
      <div class="legend">
        <span class="trades">all trades</span>
        <span class="candidates">cluster trades</span>
        <span class="lows">running daily low</span>
        <span class="highs">running daily high</span>
      </div>
    </div>
    <div class="card" style="flex: 1 1 360px;">
      <div class="chart-title">Runtime confidence</div>
      <svg id="confidenceChart"></svg>
      <div class="legend"><span class="confidence">confidence</span></div>
    </div>
  </div>
  <div class="row" style="margin-top: 16px;">
    <div class="card" style="flex: 1 1 360px;">
      <div class="chart-title">Candidate markout histogram (20 bars)</div>
      <svg id="histChart"></svg>
    </div>
    <div class="card" style="flex: 1 1 360px;">
      <div class="chart-title">Runtime usage</div>
      <table id="usageTable"></table>
    </div>
  </div>
<script>
const DATA = __DATA__;

function setText(el, text) { el.textContent = text; }

function scalePoints(points, width, height, padding=24) {
  if (!points.length) return [];
  const xs = points.map(p => p.x);
  const ys = points.map(p => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const xSpan = (maxX - minX) || 1;
  const ySpan = (maxY - minY) || 1;
  return points.map(p => ({
    ...p,
    sx: padding + ((p.x - minX) / xSpan) * (width - padding * 2),
    sy: height - padding - ((p.y - minY) / ySpan) * (height - padding * 2),
  }));
}

function clearSvg(svg) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
}

function linePath(points) {
  return points.map((p, idx) => `${idx === 0 ? "M" : "L"} ${p.sx.toFixed(2)} ${p.sy.toFixed(2)}`).join(" ");
}

function drawPriceChart(product) {
  const svg = document.getElementById("priceChart");
  clearSvg(svg);
  const width = svg.clientWidth || 720;
  const height = svg.clientHeight || 280;
  const series = DATA.products[product].series;
  const all = scalePoints(series.trades, width, height);
  const lows = scalePoints(series.dayLow, width, height);
  const highs = scalePoints(series.dayHigh, width, height);
  const candidates = scalePoints(series.candidates, width, height);
  [
    { points: all, color: "#222", width: 1.5 },
    { points: lows, color: "#1565c0", width: 1.5 },
    { points: highs, color: "#c62828", width: 1.5 },
  ].forEach(item => {
    if (!item.points.length) return;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", linePath(item.points));
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", item.color);
    path.setAttribute("stroke-width", item.width);
    svg.appendChild(path);
  });
  candidates.forEach(point => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", point.sx);
    circle.setAttribute("cy", point.sy);
    circle.setAttribute("r", 3.5);
    circle.setAttribute("fill", point.side === "BUY" ? "#0a7" : "#f57c00");
    svg.appendChild(circle);
  });
}

function drawConfidenceChart(product) {
  const svg = document.getElementById("confidenceChart");
  clearSvg(svg);
  const width = svg.clientWidth || 360;
  const height = svg.clientHeight || 280;
  const points = scalePoints(DATA.products[product].series.confidence, width, height);
  if (!points.length) return;
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", linePath(points));
  path.setAttribute("fill", "none");
  path.setAttribute("stroke", "#6a1b9a");
  path.setAttribute("stroke-width", "2");
  svg.appendChild(path);
}

function drawHistogram(product) {
  const svg = document.getElementById("histChart");
  clearSvg(svg);
  const width = svg.clientWidth || 360;
  const height = svg.clientHeight || 280;
  const bins = DATA.products[product].histograms.markout20 || [];
  if (!bins.length) return;
  const maxCount = Math.max(...bins.map(b => b.count), 1);
  const barWidth = Math.max(10, (width - 32) / bins.length);
  bins.forEach((bin, idx) => {
    const barHeight = ((height - 40) * bin.count) / maxCount;
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", 16 + idx * barWidth);
    rect.setAttribute("y", height - 20 - barHeight);
    rect.setAttribute("width", Math.max(6, barWidth - 3));
    rect.setAttribute("height", barHeight);
    rect.setAttribute("fill", "#00897b");
    svg.appendChild(rect);
  });
}

function renderSummary(product) {
  const summary = DATA.products[product].summary;
  const container = document.getElementById("summary");
  container.innerHTML = "";
  [
    ["Mode", summary.recommendedMode],
    ["Lot cluster", `${summary.lotCluster.min}-${summary.lotCluster.max}`],
    ["Candidate score", summary.candidateScore],
    ["Directional correctness", summary.directionalCorrectness],
    ["Buy-at-lows precision", summary.buyAtLowsPrecision],
    ["Sell-at-highs precision", summary.sellAtHighsPrecision],
    ["Avg persistence (bars)", summary.avgPersistenceBars],
    ["Signal PnL proxy", summary.signalProxyPnl],
  ].forEach(([label, value]) => {
    const metric = document.createElement("div");
    metric.className = "metric";
    metric.innerHTML = `<div class="label">${label}</div><div class="value">${value}</div>`;
    container.appendChild(metric);
  });
}

function renderUsage(product) {
  const summary = DATA.products[product].summary;
  const table = document.getElementById("usageTable");
  table.innerHTML = `
    <tr><th>Field</th><th>Value</th></tr>
    <tr><td>Runtime mode</td><td>${summary.recommendedMode}</td></tr>
    <tr><td>Lot cluster</td><td>${summary.lotCluster.center} (${summary.lotCluster.min}-${summary.lotCluster.max})</td></tr>
    <tr><td>Use case</td><td>${summary.recommendedMode === "FULL_FOLLOW" ? "Replace baseline on signal" : summary.recommendedMode === "FOLLOW_AFTER_TRIGGER" ? "Keep baseline until trigger" : summary.recommendedMode === "BIAS_ONLY" ? "Use as regime/basket bias" : "Ignore"}</td></tr>
    <tr><td>Interpretation</td><td>Treat this as a per-product regime engine with confidence and invalidation, not a one-shot trigger.</td></tr>
  `;
}

function renderProduct(product) {
  renderSummary(product);
  drawPriceChart(product);
  drawConfidenceChart(product);
  drawHistogram(product);
  renderUsage(product);
}

const selector = document.getElementById("productSelect");
Object.keys(DATA.products).forEach(product => {
  const option = document.createElement("option");
  option.value = product;
  option.textContent = product;
  selector.appendChild(option);
});
selector.addEventListener("change", () => renderProduct(selector.value));
if (selector.options.length) {
  selector.value = selector.options[0].value;
  renderProduct(selector.value);
}
</script>
</body>
</html>"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a standalone dashboard from Olivia-style discovery artifacts.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory with trade_features.csv and validated_products.json.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for dashboard artifacts.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir or (input_dir / "dashboard")
    output_dir.mkdir(parents=True, exist_ok=True)

    features = load_features(input_dir / "trade_features.csv")
    validated = json.loads((input_dir / "validated_products.json").read_text())
    payload = build_payload(features, validated)

    write_json(output_dir / "dashboard_data.json", payload)
    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(payload))
    (output_dir / "index.html").write_text(html)
    print(f"Wrote dashboard to {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
