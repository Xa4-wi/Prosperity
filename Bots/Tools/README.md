# Bots Tools

This folder contains standalone research and runtime tools that support bot development outside the main trader files.

## Olivia-style detector toolkit

The Olivia toolkit is split into:

- `olivia_research/`
  - offline discovery and scoring on historical round data
- `olivia_live/`
  - stateful runtime detector, signal state, product policy, and dashboard adapter

## Folder layout

```text
Bots/Tools/
  olivia_common.py
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
python3 Bots/Tools/run_olivia_pipeline.py \
  --data-root Data \
  --round-dir ROUND_2 \
  --output-dir Bots/Tools/output/olivia_round2
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
python3 Bots/Tools/olivia_research/discover_candidates.py --data-root Data --round-dir ROUND_2 --output-dir Bots/Tools/output/olivia_round2
python3 Bots/Tools/olivia_research/score_candidates.py --input-dir Bots/Tools/output/olivia_round2
python3 Bots/Tools/olivia_research/validate_products.py --data-root Data --round-dir ROUND_2 --input-dir Bots/Tools/output/olivia_round2
python3 Bots/Tools/olivia_research/generate_runtime_config.py --input Bots/Tools/output/olivia_round2/validated_products.json --output Bots/Tools/output/olivia_round2/runtime_config.json
python3 Bots/Tools/olivia_live/dashboard_adapter.py --input-dir Bots/Tools/output/olivia_round2 --output-dir Bots/Tools/output/olivia_round2/dashboard
```

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
