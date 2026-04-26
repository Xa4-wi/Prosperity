# Capsule Product Diagnosis Report

- Root scanned: `Data/ROUND_4`
- Price files: 3
- Trade files: 3
- Competitive intel reference: `/Users/xavierwinkelmann/Prosperity/Bots/Research/COMPETITIVE_INTEL.md`

## Product Table

| Product | Primary Archetype | Secondary | Mean Mid | Mean Spread | Trend SNR | Trend R² | Anchor | One-Sided |
|---|---|---|---:|---:|---:|---:|---:|---:|
| HYDROGEL_PACK | anchored_market_maker | bot_driven_overlay, trending_drift_carry | 9994.7 | 15.73 | 0.77 | 0.351 | 10000 (1000) | 0.000 |
| VELVETFRUIT_EXTRACT | bot_driven_overlay | anchored_market_maker, slow_random_walk | 5247.6 | 4.98 | 2.17 | 0.012 | 5250 (250) | 0.000 |
| VEV_4000 | option_family | anchored_market_maker, bot_driven_overlay | 1247.7 | 20.75 | 2.16 | 0.012 | 1250 (250) | 0.000 |
| VEV_4500 | option_family | anchored_market_maker, basket_or_etf_candidate | 747.7 | 15.79 | 2.17 | 0.012 | 750 (250) | 0.000 |
| VEV_5000 | option_family | anchored_market_maker, slow_random_walk | 251.1 | 5.96 | 2.15 | 0.011 | 250 (250) | 0.000 |
| VEV_5100 | option_family | slow_random_walk, anchored_market_maker | 160.9 | 4.17 | 2.14 | 0.013 | 160 (10) | 0.000 |
| VEV_5200 | option_family | bot_driven_overlay, slow_random_walk | 89.0 | 2.76 | 2.14 | 0.032 | 90 (10) | 0.000 |
| VEV_5300 | option_family | bot_driven_overlay, slow_random_walk | 41.2 | 1.97 | 2.21 | 0.071 | 40 (10) | 0.000 |
| VEV_5400 | option_family | bot_driven_overlay, slow_random_walk | 12.6 | 1.30 | 2.43 | 0.149 | 10 (10) | 0.000 |
| VEV_5500 | option_family | bot_driven_overlay, slow_random_walk | 4.7 | 1.11 | 2.45 | 0.231 | 0 (1000) | 0.000 |
| VEV_6000 | option_family | anchored_market_maker, bot_driven_overlay | 0.5 | 1.00 | n/a | n/a | 0 (1000) | 0.000 |
| VEV_6500 | option_family | anchored_market_maker, bot_driven_overlay | 0.5 | 1.00 | n/a | n/a | 0 (1000) | 0.000 |

## HYDROGEL_PACK

### Classification

- Primary archetype: **anchored_market_maker**
- Secondary archetypes: bot_driven_overlay, trending_drift_carry, slow_random_walk
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1022**
- Mean mid: **9994.65**
- Mid std on valid rows: **34.623**
- Mean spread: **15.728**
- Avg top-of-book depth: **24.83**
- One-sided row ratio: **0.000**
- Trend SNR: **0.768**
- Trend R²: **0.3506**
- Mean daily slope: **0.00002051**
- Trend-residual vs next-return corr: **-0.040**
- Rolling-deviation vs next-return corr: **-0.031**
- Imbalance vs next-return corr: **0.299**
- Anchor candidate: **10000** (step 1000, strength 0.320)

### Trade Pattern Clues

- Common trade sizes: [(6, 214), (3, 211), (2, 202), (4, 200), (5, 195)]
- Sizes often hitting new daily highs/lows: [(4, 19), (3, 18), (6, 13), (5, 11), (2, 9)]

### Strategy Directions

- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `anchored_market_maker`: 2.461
- `bot_driven_overlay`: 2.400
- `trending_drift_carry`: 2.071
- `slow_random_walk`: 2.059
- `local_fair_microstructure`: 1.197
- `mean_reverting_ou`: 0.682

## VELVETFRUIT_EXTRACT

### Classification

- Primary archetype: **bot_driven_overlay**
- Secondary archetypes: anchored_market_maker, slow_random_walk, local_fair_microstructure
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1381**
- Mean mid: **5247.65**
- Mid std on valid rows: **18.077**
- Mean spread: **4.982**
- Avg top-of-book depth: **75.54**
- One-sided row ratio: **0.000**
- Trend SNR: **2.165**
- Trend R²: **0.0125**
- Mean daily slope: **-0.00000024**
- Trend-residual vs next-return corr: **-0.035**
- Rolling-deviation vs next-return corr: **-0.029**
- Imbalance vs next-return corr: **0.281**
- Anchor candidate: **5250** (step 250, strength 0.248)

### Trade Pattern Clues

- Common trade sizes: [(8, 225), (6, 225), (5, 223), (7, 209), (4, 207), (3, 195)]
- Sizes often hitting new daily highs/lows: [(5, 16), (6, 15), (3, 14), (8, 14), (7, 9), (4, 4)]
- Recurring large-trade timestamps: [(10400, 1), (44900, 1), (99400, 1), (109000, 1), (112600, 1), (132600, 1), (156200, 1), (157400, 1)]

### Strategy Directions

- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `bot_driven_overlay`: 2.400
- `anchored_market_maker`: 2.245
- `slow_random_walk`: 2.203
- `local_fair_microstructure`: 1.123
- `trending_drift_carry`: 1.092
- `mean_reverting_ou`: 0.662

## VEV_4000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, local_fair_microstructure
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **442**
- Mean mid: **1247.66**
- Mid std on valid rows: **18.101**
- Mean spread: **20.753**
- Avg top-of-book depth: **21.83**
- One-sided row ratio: **0.000**
- Trend SNR: **2.161**
- Trend R²: **0.0125**
- Mean daily slope: **-0.00000024**
- Trend-residual vs next-return corr: **-0.044**
- Rolling-deviation vs next-return corr: **-0.060**
- Imbalance vs next-return corr: **0.494**
- Anchor candidate: **1250** (step 250, strength 0.430)
- Option family: **VEV**, strike **4000**

### Trade Pattern Clues

- Common trade sizes: [(1, 154), (3, 146), (2, 142)]
- Sizes often hitting new daily highs/lows: [(2, 18), (3, 16), (1, 14)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `anchored_market_maker`: 2.791
- `bot_driven_overlay`: 2.400
- `local_fair_microstructure`: 1.975
- `slow_random_walk`: 1.839
- `trending_drift_carry`: 1.091
- `mean_reverting_ou`: 0.753

## VEV_4500

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, basket_or_etf_candidate, slow_random_walk
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **3**
- Mean mid: **747.66**
- Mid std on valid rows: **18.092**
- Mean spread: **15.794**
- Avg top-of-book depth: **17.90**
- One-sided row ratio: **0.000**
- Trend SNR: **2.173**
- Trend R²: **0.0125**
- Mean daily slope: **-0.00000024**
- Trend-residual vs next-return corr: **-0.039**
- Rolling-deviation vs next-return corr: **-0.043**
- Imbalance vs next-return corr: **0.412**
- Anchor candidate: **750** (step 250, strength 0.401)
- Option family: **VEV**, strike **4500**
- Basket-like correlation cluster: **VEV_4000, VEV_5000**

### Trade Pattern Clues

- Common trade sizes: [(1, 1), (2, 1), (3, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2), (2, 2), (3, 1)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.

### Archetype Scores

- `option_family`: 4.000
- `anchored_market_maker`: 2.704
- `basket_or_etf_candidate`: 2.000
- `slow_random_walk`: 1.898
- `local_fair_microstructure`: 1.648
- `trending_drift_carry`: 1.092
- `mean_reverting_ou`: 0.704

## VEV_5000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, slow_random_walk, basket_or_etf_candidate
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **3**
- Mean mid: **251.14**
- Mid std on valid rows: **17.455**
- Mean spread: **5.964**
- Avg top-of-book depth: **31.21**
- One-sided row ratio: **0.000**
- Trend SNR: **2.152**
- Trend R²: **0.0106**
- Mean daily slope: **-0.00000171**
- Trend-residual vs next-return corr: **-0.032**
- Rolling-deviation vs next-return corr: **-0.019**
- Imbalance vs next-return corr: **0.212**
- Anchor candidate: **250** (step 250, strength 0.279)
- Option family: **VEV**, strike **5000**
- Basket-like correlation cluster: **VEV_4500, VEV_5100**

### Trade Pattern Clues

- Common trade sizes: [(1, 1), (2, 1), (3, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2), (2, 2), (3, 1)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.

### Archetype Scores

- `option_family`: 4.000
- `anchored_market_maker`: 2.337
- `slow_random_walk`: 2.142
- `basket_or_etf_candidate`: 2.000
- `trending_drift_carry`: 1.086
- `local_fair_microstructure`: 0.848
- `mean_reverting_ou`: 0.634

## VEV_5100

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: slow_random_walk, anchored_market_maker, trending_drift_carry
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **3**
- Mean mid: **160.86**
- Mid std on valid rows: **16.127**
- Mean spread: **4.174**
- Avg top-of-book depth: **39.12**
- One-sided row ratio: **0.000**
- Trend SNR: **2.140**
- Trend R²: **0.0131**
- Mean daily slope: **-0.00000399**
- Trend-residual vs next-return corr: **-0.032**
- Rolling-deviation vs next-return corr: **-0.017**
- Imbalance vs next-return corr: **0.230**
- Anchor candidate: **160** (step 10, strength 0.227)
- Option family: **VEV**, strike **5100**

### Trade Pattern Clues

- Common trade sizes: [(1, 1), (2, 1), (3, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2), (2, 2), (3, 1)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Avoid raw mid; use wall mid, maker-mid, or filtered VWAP touch.
- Look for stale market-makers and short-horizon filtered fair.
- Keep thresholds simple and robust; dynamic z-score windows overfit easily.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.

### Archetype Scores

- `option_family`: 4.000
- `slow_random_walk`: 2.247
- `anchored_market_maker`: 2.180
- `trending_drift_carry`: 1.093
- `local_fair_microstructure`: 0.920
- `mean_reverting_ou`: 0.630

## VEV_5200

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **47**
- Mean mid: **88.99**
- Mid std on valid rows: **13.347**
- Mean spread: **2.758**
- Avg top-of-book depth: **45.62**
- One-sided row ratio: **0.000**
- Trend SNR: **2.140**
- Trend R²: **0.0319**
- Mean daily slope: **-0.00000584**
- Trend-residual vs next-return corr: **-0.033**
- Rolling-deviation vs next-return corr: **-0.022**
- Imbalance vs next-return corr: **0.256**
- Anchor candidate: **90** (step 10, strength 0.193)
- Option family: **VEV**, strike **5200**

### Trade Pattern Clues

- Common trade sizes: [(2, 14), (5, 14), (4, 9), (3, 9), (1, 1)]
- Sizes often hitting new daily highs/lows: [(3, 6), (4, 5), (2, 5), (5, 4), (1, 1)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 2.314
- `anchored_market_maker`: 2.079
- `trending_drift_carry`: 1.149
- `local_fair_microstructure`: 1.023
- `mean_reverting_ou`: 0.645

## VEV_5300

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **164**
- Mean mid: **41.18**
- Mid std on valid rows: **9.143**
- Mean spread: **1.973**
- Avg top-of-book depth: **41.05**
- One-sided row ratio: **0.000**
- Trend SNR: **2.210**
- Trend R²: **0.0705**
- Mean daily slope: **-0.00000491**
- Trend-residual vs next-return corr: **-0.040**
- Rolling-deviation vs next-return corr: **-0.042**
- Imbalance vs next-return corr: **0.302**
- Anchor candidate: **40** (step 10, strength 0.181)
- Option family: **VEV**, strike **5300**

### Trade Pattern Clues

- Common trade sizes: [(2, 53), (4, 41), (5, 35), (3, 34), (1, 1)]
- Sizes often hitting new daily highs/lows: [(3, 11), (4, 9), (2, 7), (5, 6)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 2.338
- `anchored_market_maker`: 2.043
- `trending_drift_carry`: 1.267
- `local_fair_microstructure`: 1.209
- `mean_reverting_ou`: 0.703

## VEV_5400

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **276**
- Mean mid: **12.63**
- Mid std on valid rows: **4.149**
- Mean spread: **1.304**
- Avg top-of-book depth: **43.78**
- One-sided row ratio: **0.000**
- Trend SNR: **2.425**
- Trend R²: **0.1487**
- Mean daily slope: **-0.00000374**
- Trend-residual vs next-return corr: **-0.049**
- Rolling-deviation vs next-return corr: **-0.069**
- Imbalance vs next-return corr: **0.269**
- Anchor candidate: **10** (step 10, strength 0.224)
- Option family: **VEV**, strike **5400**

### Trade Pattern Clues

- Common trade sizes: [(2, 79), (4, 72), (5, 69), (3, 56)]
- Sizes often hitting new daily highs/lows: [(3, 10), (2, 9), (4, 9), (5, 7)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 2.252
- `anchored_market_maker`: 2.172
- `trending_drift_carry`: 1.507
- `local_fair_microstructure`: 1.077
- `mean_reverting_ou`: 0.784

## VEV_5500

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **306**
- Mean mid: **4.71**
- Mid std on valid rows: **2.205**
- Mean spread: **1.109**
- Avg top-of-book depth: **44.56**
- One-sided row ratio: **0.000**
- Trend SNR: **2.449**
- Trend R²: **0.2312**
- Mean daily slope: **-0.00000207**
- Trend-residual vs next-return corr: **-0.072**
- Rolling-deviation vs next-return corr: **-0.118**
- Imbalance vs next-return corr: **0.272**
- Anchor candidate: **0** (step 1000, strength 0.190)
- Option family: **VEV**, strike **5500**

### Trade Pattern Clues

- Common trade sizes: [(2, 87), (4, 80), (5, 79), (3, 60)]
- Sizes often hitting new daily highs/lows: [(4, 10), (2, 5), (3, 5), (5, 2)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.
- Check daily-extrema trades for Olivia-like or other informed-bot signatures.
- Use bot behavior as an overlay on top of the base product model.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 2.320
- `anchored_market_maker`: 2.069
- `trending_drift_carry`: 1.755
- `local_fair_microstructure`: 1.089
- `mean_reverting_ou`: 0.954

## VEV_6000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, slow_random_walk
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **317**
- Mean mid: **0.50**
- Mid std on valid rows: **0.000**
- Mean spread: **1.000**
- Avg top-of-book depth: **44.97**
- One-sided row ratio: **0.000**
- Trend SNR: **n/a**
- Trend R²: **n/a**
- Mean daily slope: **n/a**
- Trend-residual vs next-return corr: **n/a**
- Rolling-deviation vs next-return corr: **n/a**
- Imbalance vs next-return corr: **n/a**
- Anchor candidate: **0** (step 1000, strength 0.767)
- Option family: **VEV**, strike **6000**

### Trade Pattern Clues

- Common trade sizes: [(2, 90), (4, 82), (5, 81), (3, 64)]
- Sizes often hitting new daily highs/lows: [(3, 4), (2, 2)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `anchored_market_maker`: 2.800
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 0.467

## VEV_6500

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, slow_random_walk
- Rounds seen: [4]
- Days seen: [1, 2, 3]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **317**
- Mean mid: **0.50**
- Mid std on valid rows: **0.000**
- Mean spread: **1.000**
- Avg top-of-book depth: **30.99**
- One-sided row ratio: **0.000**
- Trend SNR: **n/a**
- Trend R²: **n/a**
- Mean daily slope: **n/a**
- Trend-residual vs next-return corr: **n/a**
- Rolling-deviation vs next-return corr: **n/a**
- Imbalance vs next-return corr: **n/a**
- Anchor candidate: **0** (step 1000, strength 0.767)
- Option family: **VEV**, strike **6500**

### Trade Pattern Clues

- Common trade sizes: [(2, 90), (4, 82), (5, 81), (3, 64)]
- Sizes often hitting new daily highs/lows: [(3, 4), (2, 2)]

### Strategy Directions

- Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.
- Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.
- Do not use flat volatility unless validated very strongly.
- Use Take → Clear → Make every tick.
- Build fair from anchor + wall/stable mid; skew quotes by inventory.
- Add toxicity / markout-aware quoting and a near-zero-EV recycler.
- Profile first; do not tune on raw website randomness.
- Prefer robust plateaus over sharp parameter peaks.
- Keep state in traderData / serialized memory, not class variables.

### Warnings

- Do not use flat-vol Black–Scholes without validating an IV smile.
- Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.

### Archetype Scores

- `option_family`: 4.000
- `anchored_market_maker`: 2.800
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 0.467

## Notes

- Advice rules were selected to align with Competitive Intelligence themes: Take → Clear → Make, wall/stable mid over raw mid, O-U for mean reversion, Black–Scholes + smile for option families, and bot-detection overlays.
