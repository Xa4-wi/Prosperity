from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build_payload(summary: dict[str, Any]) -> dict[str, Any]:
    product_rows = []
    products = summary.get("products", {})
    for name, product in sorted(products.items()):
        product_rows.append(
            {
                "product": name,
                "primary_archetype": product.get("primary_archetype"),
                "secondary_archetypes": product.get("secondary_archetypes", []),
                "mean_mid": product.get("mean_mid"),
                "mean_spread": product.get("mean_spread"),
                "trend_snr": product.get("trend_snr"),
                "trend_r2": product.get("trend_r2"),
                "anchor_candidate": product.get("anchor_candidate"),
                "anchor_step": product.get("anchor_step"),
                "anchor_strength": product.get("anchor_strength"),
                "one_sided_ratio": product.get("one_sided_ratio"),
                "n_price_rows": product.get("n_price_rows"),
                "n_valid_rows": product.get("n_valid_rows"),
                "n_trade_rows": product.get("n_trade_rows"),
                "avg_top_depth": product.get("avg_top_depth"),
                "imbalance_next_corr": product.get("imbalance_next_corr"),
                "trend_resid_next_corr": product.get("trend_resid_next_corr"),
                "rolling_dev_next_corr": product.get("rolling_dev_next_corr"),
                "common_trade_sizes": product.get("common_trade_sizes", []),
                "daily_extrema_size_hits": product.get("daily_extrema_size_hits", []),
                "recurring_large_trade_timestamps": product.get("recurring_large_trade_timestamps", []),
                "archetype_scores": product.get("archetype_scores", {}),
                "recommended_approaches": product.get("recommended_approaches", []),
                "warnings": product.get("warnings", []),
                "days_seen": product.get("days_seen", []),
                "rounds_seen": product.get("rounds_seen", []),
                "conversion_feature_columns": product.get("conversion_feature_columns", []),
                "basket_candidate_with": product.get("basket_candidate_with", []),
                "option_family": product.get("option_family"),
                "strike": product.get("strike"),
            }
        )
    return {
        "generated_at": summary.get("generated_at"),
        "root": summary.get("root"),
        "intel_md": summary.get("intel_md"),
        "notes": summary.get("notes", []),
        "price_files": summary.get("price_files", []),
        "trade_files": summary.get("trade_files", []),
        "products": product_rows,
    }


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Capsule Product Diagnosis Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f7f7f7; color: #111; }
    h1,h2,h3 { margin: 0 0 10px; }
    .muted { color: #666; }
    .summary-grid, .metric-grid { display: grid; gap: 12px; }
    .summary-grid { grid-template-columns: repeat(4, minmax(180px,1fr)); margin: 16px 0 24px; }
    .metric-grid { grid-template-columns: repeat(4, minmax(160px,1fr)); margin: 14px 0 18px; }
    .card { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .metric { background: #fafafa; border-radius: 8px; padding: 10px; }
    .label { font-size: 12px; color: #666; margin-bottom: 4px; }
    .value { font-size: 18px; font-weight: 700; }
    select { padding: 8px 10px; font-size: 14px; margin: 10px 0 16px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; vertical-align: top; }
    .layout { display: grid; grid-template-columns: 1.1fr 1fr; gap: 16px; }
    .bars { display: grid; gap: 8px; }
    .bar-row { display: grid; grid-template-columns: 180px 1fr 60px; gap: 10px; align-items: center; }
    .bar-shell { height: 14px; background: #ececec; border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, #1976d2, #43a047); }
    ul { margin: 8px 0 0 18px; }
    .warning { color: #b71c1c; }
    .chip { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #edf4ff; color: #0d47a1; font-size: 12px; margin: 2px 6px 2px 0; }
  </style>
</head>
<body>
  <h1>Capsule Product Diagnosis Dashboard</h1>
  <p class="muted">Interactive view over the diagnosis report and summary. Useful for reviewing archetypes, warnings, and strategy directions product by product.</p>

  <div class="summary-grid">
    <div class="metric"><div class="label">Root</div><div class="value" style="font-size:13px" id="root"></div></div>
    <div class="metric"><div class="label">Generated</div><div class="value" style="font-size:13px" id="generated"></div></div>
    <div class="metric"><div class="label">Price files</div><div class="value" id="priceCount"></div></div>
    <div class="metric"><div class="label">Trade files</div><div class="value" id="tradeCount"></div></div>
  </div>

  <label for="productSelect">Product</label><br />
  <select id="productSelect"></select>

  <div class="card" style="margin-bottom:16px;">
    <h2 id="productName"></h2>
    <div id="chips" style="margin-top:6px;"></div>
    <div class="metric-grid" id="metrics"></div>
  </div>

  <div class="layout">
    <div class="card">
      <h3>Archetype Scores</h3>
      <div id="archetypeBars" class="bars"></div>
    </div>
    <div class="card">
      <h3>Trade Pattern Clues</h3>
      <div id="tradePatterns"></div>
    </div>
  </div>

  <div class="layout" style="margin-top:16px;">
    <div class="card">
      <h3>Recommended Approaches</h3>
      <ul id="approaches"></ul>
    </div>
    <div class="card">
      <h3>Warnings</h3>
      <ul id="warnings"></ul>
    </div>
  </div>

  <div class="card" style="margin-top:16px;">
    <h3>All Products</h3>
    <table id="productTable"></table>
  </div>

<script>
const DATA = __DATA__;

function fmt(value, digits=3) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  if (typeof value === "number") return value.toFixed(digits);
  return String(value);
}

function setSummary() {
  document.getElementById("root").textContent = DATA.root || "n/a";
  document.getElementById("generated").textContent = DATA.generated_at || "n/a";
  document.getElementById("priceCount").textContent = DATA.price_files.length;
  document.getElementById("tradeCount").textContent = DATA.trade_files.length;
}

function renderTable() {
  const rows = DATA.products.map(p => `
    <tr>
      <td>${p.product}</td>
      <td>${p.primary_archetype}</td>
      <td>${(p.secondary_archetypes || []).join(", ")}</td>
      <td>${fmt(p.mean_mid, 2)}</td>
      <td>${fmt(p.mean_spread, 2)}</td>
      <td>${fmt(p.trend_snr, 2)}</td>
      <td>${fmt(p.one_sided_ratio, 3)}</td>
    </tr>`).join("");
  document.getElementById("productTable").innerHTML = `
    <tr><th>Product</th><th>Primary</th><th>Secondary</th><th>Mean mid</th><th>Mean spread</th><th>Trend SNR</th><th>One-sided</th></tr>
    ${rows}
  `;
}

function renderProduct(productName) {
  const p = DATA.products.find(x => x.product === productName);
  if (!p) return;
  document.getElementById("productName").textContent = p.product;
  document.getElementById("chips").innerHTML = `
    <span class="chip">primary: ${p.primary_archetype}</span>
    ${(p.secondary_archetypes || []).map(x => `<span class="chip">${x}</span>`).join("")}
  `;
  const metricRows = [
    ["Rounds seen", (p.rounds_seen || []).join(", ") || "n/a"],
    ["Days seen", (p.days_seen || []).join(", ") || "n/a"],
    ["Valid / total rows", `${p.n_valid_rows} / ${p.n_price_rows}`],
    ["Trade rows", p.n_trade_rows],
    ["Mean mid", fmt(p.mean_mid, 2)],
    ["Mean spread", fmt(p.mean_spread, 3)],
    ["Top depth", fmt(p.avg_top_depth, 2)],
    ["Trend SNR", fmt(p.trend_snr, 3)],
    ["Trend R²", fmt(p.trend_r2, 4)],
    ["One-sided ratio", fmt(p.one_sided_ratio, 3)],
    ["Imbalance corr", fmt(p.imbalance_next_corr, 3)],
    ["Residual/next corr", fmt(p.trend_resid_next_corr, 3)],
    ["Rolling dev corr", fmt(p.rolling_dev_next_corr, 3)],
    ["Anchor", p.anchor_candidate !== null ? `${p.anchor_candidate} (${p.anchor_step})` : "n/a"],
  ];
  document.getElementById("metrics").innerHTML = metricRows.map(([label, value]) => `
    <div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>
  `).join("");

  const scores = Object.entries(p.archetype_scores || {});
  const maxScore = Math.max(1, ...scores.map(([,v]) => v));
  document.getElementById("archetypeBars").innerHTML = scores.map(([name, value]) => `
    <div class="bar-row">
      <div>${name}</div>
      <div class="bar-shell"><div class="bar-fill" style="width:${(value / maxScore) * 100}%"></div></div>
      <div>${fmt(value, 3)}</div>
    </div>
  `).join("");

  const tradePatterns = [];
  if ((p.common_trade_sizes || []).length) tradePatterns.push(`<div><strong>Common trade sizes:</strong> ${JSON.stringify(p.common_trade_sizes.slice(0, 6))}</div>`);
  if ((p.daily_extrema_size_hits || []).length) tradePatterns.push(`<div><strong>Extrema size hits:</strong> ${JSON.stringify(p.daily_extrema_size_hits.slice(0, 6))}</div>`);
  if ((p.recurring_large_trade_timestamps || []).length) tradePatterns.push(`<div><strong>Recurring large-trade timestamps:</strong> ${JSON.stringify(p.recurring_large_trade_timestamps.slice(0, 8))}</div>`);
  if ((p.conversion_feature_columns || []).length) tradePatterns.push(`<div><strong>Conversion columns:</strong> ${(p.conversion_feature_columns || []).join(", ")}</div>`);
  if ((p.basket_candidate_with || []).length) tradePatterns.push(`<div><strong>Basket candidates:</strong> ${(p.basket_candidate_with || []).join(", ")}</div>`);
  if (p.option_family) tradePatterns.push(`<div><strong>Option family:</strong> ${p.option_family} strike ${p.strike}</div>`);
  document.getElementById("tradePatterns").innerHTML = tradePatterns.join("") || "<div class='muted'>No special pattern clues recorded.</div>";

  document.getElementById("approaches").innerHTML = (p.recommended_approaches || []).map(x => `<li>${x}</li>`).join("") || "<li class='muted'>No strategy suggestions.</li>";
  document.getElementById("warnings").innerHTML = (p.warnings || []).map(x => `<li class="warning">${x}</li>`).join("") || "<li class='muted'>No warnings.</li>";
}

setSummary();
renderTable();
const select = document.getElementById("productSelect");
for (const p of DATA.products) {
  const opt = document.createElement("option");
  opt.value = p.product;
  opt.textContent = p.product;
  select.appendChild(opt);
}
select.addEventListener("change", () => renderProduct(select.value));
if (DATA.products.length) {
  select.value = DATA.products[0].product;
  renderProduct(select.value);
}
</script>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a standalone HTML dashboard from capsule diagnosis JSON.")
    parser.add_argument("--summary-json", type=Path, required=True, help="Path to capsule_product_diagnosis_summary.json")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for dashboard assets")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = load_summary(args.summary_json)
    payload = build_payload(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "dashboard_data.json").write_text(json.dumps(payload, indent=2))
    (args.output_dir / "index.html").write_text(HTML_TEMPLATE.replace("__DATA__", json.dumps(payload)))
    print(f"Wrote dashboard to {args.output_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
