# Olivia Detector Toolkit

This folder contains the Olivia-style discovery and runtime detection toolkit as a self-contained tool inside [Bots/Tools](/Users/xavierwinkelmann/Prosperity/Bots/Tools).

The toolkit is split into:

- `olivia_research/`
  - offline discovery and scoring on historical round data
- `olivia_live/`
  - stateful runtime detector, signal state, product policy, and dashboard adapter

## Folder layout

```text
Bots/Tools/olivia_tool/
  README.md
  olivia_common.py
  output/
  run_olivia_pipeline.py
  olivia_research/
    discover_candidates.py
    score_candidates.py
    validate_products.py
    generate_runtime_config.py
  olivia_live/
    signal_state.py
    detector.py
    product_policy.py
    dashboard_adapter.py
```

## Typical workflow

### 1. Run the full pipeline

```bash
python3 Bots/Tools/olivia_tool/run_olivia_pipeline.py \
  --data-root Data \
  --round-dir ROUND_2 \
  --output-dir Bots/Tools/olivia_tool/output/olivia_round2
```

This produces:

- `trade_features.csv`
- `quantity_clusters.json`
- `candidate_scores.csv`
- `validated_products.json`
- `runtime_config.json`
- `dashboard/index.html`

### 2. Run the stages manually if you want finer control

```bash
python3 Bots/Tools/olivia_tool/olivia_research/discover_candidates.py --data-root Data --round-dir ROUND_2 --output-dir Bots/Tools/olivia_tool/output/olivia_round2
python3 Bots/Tools/olivia_tool/olivia_research/score_candidates.py --input-dir Bots/Tools/olivia_tool/output/olivia_round2
python3 Bots/Tools/olivia_tool/olivia_research/validate_products.py --data-root Data --round-dir ROUND_2 --input-dir Bots/Tools/olivia_tool/output/olivia_round2
python3 Bots/Tools/olivia_tool/olivia_research/generate_runtime_config.py --input Bots/Tools/olivia_tool/output/olivia_round2/validated_products.json --output Bots/Tools/olivia_tool/output/olivia_round2/runtime_config.json
python3 Bots/Tools/olivia_tool/olivia_live/dashboard_adapter.py --input-dir Bots/Tools/olivia_tool/output/olivia_round2 --output-dir Bots/Tools/olivia_tool/output/olivia_round2/dashboard
```

### 3. Start a local HTML server for the dashboard

Once the dashboard files exist, you can serve them locally:

```bash
python3 -m http.server 8033 --directory Bots/Tools/olivia_tool/output/olivia_round2/dashboard
```

Then open:

- `http://127.0.0.1:8033`

Notes:

- If you used a different output folder, replace `Bots/Tools/olivia_tool/output/olivia_round2/dashboard` with that dashboard path.
- If port `8033` is already taken, choose another port such as `8040`.
- Stop the local server with `Ctrl+C`.

Direct file fallback:

- you can also open [index.html](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool/output/olivia_round2_smoke/dashboard/index.html) directly, but the local server is usually the cleaner option for browser inspection.

## What each stage does

### `discover_candidates.py`

Builds per-trade features:
- inferred side
- new daily low/high flags from executed trade prices
- distance to bid/ask/mid
- future markouts
- persistence
- repeated lot-size cluster membership

### `score_candidates.py`

Scores candidate lot clusters by:
- extremum hit rate
- directional correctness
- persistence
- cross-day repeatability
- cross-product repeatability

### `validate_products.py`

Chooses the strongest candidate per product and assigns:
- `FULL_FOLLOW`
- `FOLLOW_AFTER_TRIGGER`
- `BIAS_ONLY`
- `IGNORE`

It also builds a simple signal-follow PnL proxy.

### `generate_runtime_config.py`

Turns the validated research output into a runtime JSON config that the live detector can consume.

### `dashboard_adapter.py`

Builds a self-contained HTML dashboard showing:
- trade prices
- running daily lows/highs
- candidate cluster trades
- runtime confidence over time
- markout histogram
- per-product recommended mode

## Runtime integration

The live detector is intentionally separate from the research layer.

Use:
- `olivia_live/signal_state.py`
- `olivia_live/detector.py`
- `olivia_live/product_policy.py`

inside a trader if an insider-style pattern appears in a future round.
