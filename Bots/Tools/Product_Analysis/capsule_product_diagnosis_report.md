# Capsule Product Diagnosis Report

- Root scanned: `/mnt/data`
- Price files: 6
- Trade files: 8
- Competitive intel reference: `/mnt/data/COMPETITIVE_INTEL.md`

## Product Table

| Product | Primary Archetype | Secondary | Mean Mid | Mean Spread | Trend SNR | Trend R² | Anchor | One-Sided |
|---|---|---|---:|---:|---:|---:|---:|---:|
| ASH_COATED_OSMIUM | anchored_market_maker | local_fair_microstructure, bot_driven_overlay | 10000.5 | 16.20 | 2.25 | 0.058 | 10000 (1000) | 0.077 |
| INTARIAN_PEPPER_ROOT | trending_drift_carry | local_fair_microstructure, bot_driven_overlay | 12002.0 | 13.58 | 784.36 | 1.000 | 12000 (1000) | 0.076 |

## ASH_COATED_OSMIUM

### Classification

- Primary archetype: **anchored_market_maker**
- Secondary archetypes: local_fair_microstructure, bot_driven_overlay, mean_reverting_ou
- Rounds seen: [1, 2]
- Days seen: [-2, -1, 0, 1]

### Metrics

- Valid rows / total rows: **55352 / 60000**
- Trade rows: **2660**
- Mean mid: **10000.53**
- Mid std on valid rows: **4.737**
- Mean spread: **16.205**
- Avg top-of-book depth: **28.37**
- One-sided row ratio: **0.077**
- Trend SNR: **2.247**
- Trend R²: **0.0575**
- Mean daily slope: **-0.00000193**
- Trend-residual vs next-return corr: **-0.211**
- Rolling-deviation vs next-return corr: **-0.381**
- Imbalance vs next-return corr: **0.594**
- Anchor candidate: **10000** (step 1000, strength 0.526)

### Trade Pattern Clues

- Common trade sizes: [(5, 474), (6, 468), (4, 381), (3, 360), (2, 359), (8, 179)]
- Sizes often hitting new daily highs/lows: [(6, 17), (2, 12), (3, 10), (4, 6), (5, 5), (10, 5)]
- Recurring large-trade timestamps: [(90200, 3), (122000, 3), (155300, 3), (177700, 3), (185900, 3), (192900, 3), (200300, 3), (208900, 3)]

### Strategy Directions

- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Use wall/stable mid, microprice, imbalance, and short-horizon local fair.
- Quote conditionally on book health; avoid trusting sparse visible touch.
- Research passive-fill markout and side-specific reentry.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `anchored_market_maker`: 3.079
- `local_fair_microstructure`: 2.877
- `bot_driven_overlay`: 2.400
- `mean_reverting_ou`: 1.895
- `slow_random_walk`: 1.647
- `trending_drift_carry`: 1.229

## INTARIAN_PEPPER_ROOT

### Classification

- Primary archetype: **trending_drift_carry**
- Secondary archetypes: local_fair_microstructure, bot_driven_overlay, slow_random_walk
- Rounds seen: [1, 2]
- Days seen: [-2, -1, 0, 1]

### Metrics

- Valid rows / total rows: **55412 / 60000**
- Trade rows: **2007**
- Mean mid: **12001.97**
- Mid std on valid rows: **999.631**
- Mean spread: **13.585**
- Avg top-of-book depth: **23.12**
- One-sided row ratio: **0.076**
- Trend SNR: **784.358**
- Trend R²: **1.0000**
- Mean daily slope: **0.00100002**
- Trend-residual vs next-return corr: **-0.702**
- Rolling-deviation vs next-return corr: **-0.305**
- Imbalance vs next-return corr: **0.568**
- Anchor candidate: **12000** (step 1000, strength 0.020)

### Trade Pattern Clues

- Common trade sizes: [(3, 420), (6, 399), (5, 381), (7, 378), (4, 342), (8, 86)]
- Sizes often hitting new daily highs/lows: [(6, 165), (7, 153), (5, 149), (3, 146), (4, 140), (8, 23)]

### Strategy Directions

- Use a schedule/catch-up carry engine, not plain market making.
- Track drift line, buy cheap dips vs expected drift, avoid chasing rich moves.
- Keep a protected core position and trim only late / clearly rich states.
- Use wall/stable mid, microprice, imbalance, and short-horizon local fair.
- Quote conditionally on book health; avoid trusting sparse visible touch.
- Research passive-fill markout and side-specific reentry.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `trending_drift_carry`: 11.000
- `local_fair_microstructure`: 2.774
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 1.960
- `mean_reverting_ou`: 1.358
- `anchored_market_maker`: 0.280

## Notes

- Advice rules were selected to align with Competitive Intelligence themes: Take → Clear → Make, wall/stable mid over raw mid, O-U for mean reversion, Black–Scholes + smile for option families, and bot-detection overlays.
