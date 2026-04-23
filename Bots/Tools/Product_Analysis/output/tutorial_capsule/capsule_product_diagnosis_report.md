# Capsule Product Diagnosis Report

- Root scanned: `Data/Tutorial`
- Price files: 2
- Trade files: 2
- Competitive intel reference: `/Users/xavierwinkelmann/Prosperity/Bots/Research/COMPETITIVE_INTEL.md`

## Product Table

| Product | Primary Archetype | Secondary | Mean Mid | Mean Spread | Trend SNR | Trend R² | Anchor | One-Sided |
|---|---|---|---:|---:|---:|---:|---:|---:|
| EMERALDS | mean_reverting_ou | anchored_market_maker, local_fair_microstructure | 10000.0 | 15.74 | 0.00 | 0.000 | 10000 (1000) | 0.000 |
| TOMATOES | slow_random_walk | anchored_market_maker, bot_driven_overlay | 4992.8 | 13.02 | 3.63 | 0.477 | 5000 (1000) | 0.000 |

## EMERALDS

### Classification

- Primary archetype: **mean_reverting_ou**
- Secondary archetypes: anchored_market_maker, local_fair_microstructure, slow_random_walk
- Rounds seen: [0]
- Days seen: [-2, -1]

### Metrics

- Valid rows / total rows: **20000 / 20000**
- Trade rows: **399**
- Mean mid: **10000.00**
- Mid std on valid rows: **0.723**
- Mean spread: **15.738**
- Avg top-of-book depth: **24.92**
- One-sided row ratio: **0.000**
- Trend SNR: **0.000**
- Trend R²: **0.0000**
- Mean daily slope: **-0.00000001**
- Trend-residual vs next-return corr: **-0.701**
- Rolling-deviation vs next-return corr: **-0.699**
- Imbalance vs next-return corr: **0.631**
- Anchor candidate: **10000** (step 1000, strength 0.575)

### Trade Pattern Clues

- Common trade sizes: [(6, 85), (5, 74), (4, 63), (3, 60), (7, 59), (8, 58)]
- Sizes often hitting new daily highs/lows: [(7, 2), (8, 2), (5, 1), (3, 1)]

### Strategy Directions

- Fit an Ornstein–Uhlenbeck style fair: theta, mu, sigma from history.
- Fade deviations from fair, preferably using zero-cross exits.
- Do not regress on raw prices; use deviations / returns instead.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Archetype Scores

- `mean_reverting_ou`: 3.999
- `anchored_market_maker`: 3.225
- `local_fair_microstructure`: 2.522
- `slow_random_walk`: 1.550
- `trending_drift_carry`: 1.000
- `bot_driven_overlay`: 0.800

## TOMATOES

### Classification

- Primary archetype: **slow_random_walk**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, trending_drift_carry
- Rounds seen: [0]
- Days seen: [-2, -1]

### Metrics

- Valid rows / total rows: **20000 / 20000**
- Trade rows: **820**
- Mean mid: **4992.76**
- Mid std on valid rows: **19.747**
- Mean spread: **13.020**
- Avg top-of-book depth: **14.89**
- One-sided row ratio: **0.000**
- Trend SNR: **3.627**
- Trend R²: **0.4769**
- Mean daily slope: **-0.00001334**
- Trend-residual vs next-return corr: **-0.080**
- Rolling-deviation vs next-return corr: **-0.143**
- Imbalance vs next-return corr: **0.326**
- Anchor candidate: **5000** (step 1000, strength 0.389)

### Trade Pattern Clues

- Common trade sizes: [(3, 210), (2, 209), (4, 202), (5, 197), (6, 2)]
- Sizes often hitting new daily highs/lows: [(2, 17), (5, 15), (3, 10), (4, 9)]

### Strategy Directions

- Avoid raw mid; use wall mid, maker-mid, or filtered VWAP touch.
- Look for stale market-makers and short-horizon filtered fair.
- Keep thresholds simple and robust; dynamic z-score windows overfit easily.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `slow_random_walk`: 2.723
- `anchored_market_maker`: 2.666
- `bot_driven_overlay`: 2.400
- `trending_drift_carry`: 1.521
- `local_fair_microstructure`: 1.303
- `mean_reverting_ou`: 1.026

## Notes

- Advice rules were selected to align with Competitive Intelligence themes: Take → Clear → Make, wall/stable mid over raw mid, O-U for mean reversion, Black–Scholes + smile for option families, and bot-detection overlays.
