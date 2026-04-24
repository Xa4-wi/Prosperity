# Capsule Product Diagnosis Report

- Root scanned: `Data/ROUND_3`
- Price files: 3
- Trade files: 3
- Competitive intel reference: `/Users/xavierwinkelmann/Prosperity/Bots/Research/COMPETITIVE_INTEL.md`

## Product Table

| Product | Primary Archetype | Secondary | Mean Mid | Mean Spread | Trend SNR | Trend R² | Anchor | One-Sided |
|---|---|---|---:|---:|---:|---:|---:|---:|
| HYDROGEL_PACK | anchored_market_maker | bot_driven_overlay, slow_random_walk | 9990.8 | 15.72 | 1.27 | 0.254 | 10000 (1000) | 0.000 |
| VELVETFRUIT_EXTRACT | bot_driven_overlay | anchored_market_maker, slow_random_walk | 5250.1 | 4.99 | 1.18 | 0.039 | 5250 (250) | 0.000 |
| VEV_4000 | option_family | anchored_market_maker, bot_driven_overlay | 1250.1 | 20.81 | 1.17 | 0.039 | 1250 (250) | 0.000 |
| VEV_4500 | option_family | anchored_market_maker, basket_or_etf_candidate | 750.1 | 15.85 | 1.19 | 0.039 | 750 (250) | 0.000 |
| VEV_5000 | option_family | anchored_market_maker, slow_random_walk | 255.0 | 6.04 | 1.18 | 0.032 | 250 (250) | 0.000 |
| VEV_5100 | option_family | anchored_market_maker, slow_random_walk | 166.8 | 4.30 | 1.10 | 0.028 | 170 (10) | 0.000 |
| VEV_5200 | option_family | anchored_market_maker, slow_random_walk | 95.5 | 2.89 | 0.97 | 0.037 | 100 (100) | 0.000 |
| VEV_5300 | option_family | bot_driven_overlay, anchored_market_maker | 46.8 | 2.11 | 0.95 | 0.045 | 50 (50) | 0.000 |
| VEV_5400 | option_family | bot_driven_overlay, slow_random_walk | 16.0 | 1.38 | 1.26 | 0.117 | 20 (10) | 0.000 |
| VEV_5500 | option_family | bot_driven_overlay, slow_random_walk | 6.6 | 1.15 | 0.69 | 0.159 | 10 (10) | 0.000 |
| VEV_6000 | option_family | anchored_market_maker, bot_driven_overlay | 0.5 | 1.00 | n/a | n/a | 0 (1000) | 0.000 |
| VEV_6500 | option_family | anchored_market_maker, bot_driven_overlay | 0.5 | 1.00 | n/a | n/a | 0 (1000) | 0.000 |

## HYDROGEL_PACK

### Classification

- Primary archetype: **anchored_market_maker**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, trending_drift_carry
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1010**
- Mean mid: **9990.81**
- Mid std on valid rows: **31.935**
- Mean spread: **15.721**
- Avg top-of-book depth: **24.80**
- One-sided row ratio: **0.000**
- Trend SNR: **1.267**
- Trend R²: **0.2542**
- Mean daily slope: **0.00005552**
- Trend-residual vs next-return corr: **-0.040**
- Rolling-deviation vs next-return corr: **-0.031**
- Imbalance vs next-return corr: **0.299**
- Anchor candidate: **10000** (step 1000, strength 0.338)

### Trade Pattern Clues

- Common trade sizes: [(5, 212), (6, 205), (4, 202), (3, 198), (2, 193)]
- Sizes often hitting new daily highs/lows: [(4, 17), (3, 15), (6, 12), (5, 12), (2, 10)]

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

- `anchored_market_maker`: 2.515
- `bot_driven_overlay`: 2.400
- `slow_random_walk`: 2.023
- `trending_drift_carry`: 1.794
- `local_fair_microstructure`: 1.196
- `mean_reverting_ou`: 0.684

## VELVETFRUIT_EXTRACT

### Classification

- Primary archetype: **bot_driven_overlay**
- Secondary archetypes: anchored_market_maker, slow_random_walk, trending_drift_carry
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1372**
- Mean mid: **5250.10**
- Mid std on valid rows: **15.630**
- Mean spread: **4.988**
- Avg top-of-book depth: **75.63**
- One-sided row ratio: **0.000**
- Trend SNR: **1.179**
- Trend R²: **0.0393**
- Mean daily slope: **0.00000465**
- Trend-residual vs next-return corr: **-0.036**
- Rolling-deviation vs next-return corr: **-0.031**
- Imbalance vs next-return corr: **0.281**
- Anchor candidate: **5250** (step 250, strength 0.260)

### Trade Pattern Clues

- Common trade sizes: [(8, 233), (7, 224), (5, 223), (6, 212), (3, 190), (4, 189)]
- Sizes often hitting new daily highs/lows: [(6, 14), (8, 14), (5, 13), (3, 12), (4, 5), (7, 3)]
- Recurring large-trade timestamps: [(547100, 2), (882600, 2), (10400, 1), (44900, 1), (105600, 1), (109000, 1), (112600, 1), (132600, 1)]

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
- `anchored_market_maker`: 2.280
- `slow_random_walk`: 2.180
- `trending_drift_carry`: 1.147
- `local_fair_microstructure`: 1.123
- `mean_reverting_ou`: 0.670

## VEV_4000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, local_fair_microstructure
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **464**
- Mean mid: **1250.11**
- Mid std on valid rows: **15.647**
- Mean spread: **20.813**
- Avg top-of-book depth: **21.84**
- One-sided row ratio: **0.000**
- Trend SNR: **1.168**
- Trend R²: **0.0394**
- Mean daily slope: **0.00000466**
- Trend-residual vs next-return corr: **-0.046**
- Rolling-deviation vs next-return corr: **-0.060**
- Imbalance vs next-return corr: **0.483**
- Anchor candidate: **1250** (step 250, strength 0.439)
- Option family: **VEV**, strike **4000**

### Trade Pattern Clues

- Common trade sizes: [(2, 160), (3, 158), (1, 146)]
- Sizes often hitting new daily highs/lows: [(1, 15), (2, 14), (3, 14)]

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
- `anchored_market_maker`: 2.816
- `bot_driven_overlay`: 2.400
- `local_fair_microstructure`: 1.931
- `slow_random_walk`: 1.823
- `trending_drift_carry`: 1.147
- `mean_reverting_ou`: 0.757

## VEV_4500

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, basket_or_etf_candidate, slow_random_walk
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1**
- Mean mid: **750.11**
- Mid std on valid rows: **15.640**
- Mean spread: **15.853**
- Avg top-of-book depth: **17.90**
- One-sided row ratio: **0.000**
- Trend SNR: **1.188**
- Trend R²: **0.0394**
- Mean daily slope: **0.00000466**
- Trend-residual vs next-return corr: **-0.040**
- Rolling-deviation vs next-return corr: **-0.044**
- Imbalance vs next-return corr: **0.401**
- Anchor candidate: **750** (step 250, strength 0.406)
- Option family: **VEV**, strike **4500**
- Basket-like correlation cluster: **VEV_4000, VEV_5000**

### Trade Pattern Clues

- Common trade sizes: [(1, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2)]

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
- `anchored_market_maker`: 2.719
- `basket_or_etf_candidate`: 2.000
- `slow_random_walk`: 1.888
- `local_fair_microstructure`: 1.605
- `trending_drift_carry`: 1.148
- `mean_reverting_ou`: 0.708

## VEV_5000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, slow_random_walk, basket_or_etf_candidate
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1**
- Mean mid: **255.02**
- Mid std on valid rows: **14.375**
- Mean spread: **6.043**
- Avg top-of-book depth: **30.81**
- One-sided row ratio: **0.000**
- Trend SNR: **1.177**
- Trend R²: **0.0324**
- Mean daily slope: **0.00000285**
- Trend-residual vs next-return corr: **-0.033**
- Rolling-deviation vs next-return corr: **-0.021**
- Imbalance vs next-return corr: **0.214**
- Anchor candidate: **250** (step 250, strength 0.306)
- Option family: **VEV**, strike **5000**
- Basket-like correlation cluster: **VEV_4500, VEV_5100**

### Trade Pattern Clues

- Common trade sizes: [(1, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2)]

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
- `anchored_market_maker`: 2.419
- `slow_random_walk`: 2.087
- `basket_or_etf_candidate`: 2.000
- `trending_drift_carry`: 1.127
- `local_fair_microstructure`: 0.855
- `mean_reverting_ou`: 0.641

## VEV_5100

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, slow_random_walk, trending_drift_carry
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **1**
- Mean mid: **166.81**
- Mid std on valid rows: **12.742**
- Mean spread: **4.296**
- Avg top-of-book depth: **38.60**
- One-sided row ratio: **0.000**
- Trend SNR: **1.098**
- Trend R²: **0.0276**
- Mean daily slope: **0.00000065**
- Trend-residual vs next-return corr: **-0.032**
- Rolling-deviation vs next-return corr: **-0.020**
- Imbalance vs next-return corr: **0.227**
- Anchor candidate: **170** (step 10, strength 0.249)
- Option family: **VEV**, strike **5100**

### Trade Pattern Clues

- Common trade sizes: [(1, 1)]
- Sizes often hitting new daily highs/lows: [(1, 2)]

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
- `anchored_market_maker`: 2.248
- `slow_random_walk`: 2.201
- `trending_drift_carry`: 1.110
- `local_fair_microstructure`: 0.908
- `mean_reverting_ou`: 0.635

## VEV_5200

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, slow_random_walk, bot_driven_overlay
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **18**
- Mean mid: **95.55**
- Mid std on valid rows: **9.664**
- Mean spread: **2.888**
- Avg top-of-book depth: **45.07**
- One-sided row ratio: **0.000**
- Trend SNR: **0.970**
- Trend R²: **0.0372**
- Mean daily slope: **-0.00000172**
- Trend-residual vs next-return corr: **-0.034**
- Rolling-deviation vs next-return corr: **-0.028**
- Imbalance vs next-return corr: **0.285**
- Anchor candidate: **100** (step 100, strength 0.249)
- Option family: **VEV**, strike **5200**

### Trade Pattern Clues

- Common trade sizes: [(5, 6), (2, 5), (4, 4), (3, 2), (1, 1)]
- Sizes often hitting new daily highs/lows: [(5, 6), (4, 4), (2, 3), (3, 2), (1, 1)]

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
- `anchored_market_maker`: 2.246
- `slow_random_walk`: 2.203
- `bot_driven_overlay`: 1.600
- `local_fair_microstructure`: 1.142
- `trending_drift_carry`: 1.136
- `mean_reverting_ou`: 0.659

## VEV_5300

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, anchored_market_maker, slow_random_walk
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **121**
- Mean mid: **46.76**
- Mid std on valid rows: **6.228**
- Mean spread: **2.107**
- Avg top-of-book depth: **40.53**
- One-sided row ratio: **0.000**
- Trend SNR: **0.945**
- Trend R²: **0.0451**
- Mean daily slope: **-0.00000196**
- Trend-residual vs next-return corr: **-0.041**
- Rolling-deviation vs next-return corr: **-0.045**
- Imbalance vs next-return corr: **0.353**
- Anchor candidate: **50** (step 50, strength 0.278)
- Option family: **VEV**, strike **5300**

### Trade Pattern Clues

- Common trade sizes: [(4, 36), (2, 33), (5, 28), (3, 23), (1, 1)]
- Sizes often hitting new daily highs/lows: [(4, 11), (5, 4), (2, 4), (3, 3)]

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
- `anchored_market_maker`: 2.335
- `slow_random_walk`: 2.143
- `local_fair_microstructure`: 1.413
- `trending_drift_carry`: 1.159
- `mean_reverting_ou`: 0.714

## VEV_5400

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **225**
- Mean mid: **15.95**
- Mid std on valid rows: **3.429**
- Mean spread: **1.381**
- Avg top-of-book depth: **43.48**
- One-sided row ratio: **0.000**
- Trend SNR: **1.258**
- Trend R²: **0.1173**
- Mean daily slope: **-0.00000335**
- Trend-residual vs next-return corr: **-0.049**
- Rolling-deviation vs next-return corr: **-0.064**
- Imbalance vs next-return corr: **0.273**
- Anchor candidate: **20** (step 10, strength 0.214)
- Option family: **VEV**, strike **5400**

### Trade Pattern Clues

- Common trade sizes: [(2, 62), (4, 60), (5, 57), (3, 46)]
- Sizes often hitting new daily highs/lows: [(2, 9), (5, 8), (4, 8), (3, 6)]

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
- `slow_random_walk`: 2.271
- `anchored_market_maker`: 2.143
- `trending_drift_carry`: 1.383
- `local_fair_microstructure`: 1.092
- `mean_reverting_ou`: 0.776

## VEV_5500

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: bot_driven_overlay, slow_random_walk, anchored_market_maker
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **267**
- Mean mid: **6.64**
- Mid std on valid rows: **1.739**
- Mean spread: **1.150**
- Avg top-of-book depth: **44.35**
- One-sided row ratio: **0.000**
- Trend SNR: **0.689**
- Trend R²: **0.1595**
- Mean daily slope: **-0.00000130**
- Trend-residual vs next-return corr: **-0.073**
- Rolling-deviation vs next-return corr: **-0.115**
- Imbalance vs next-return corr: **0.287**
- Anchor candidate: **10** (step 10, strength 0.208)
- Option family: **VEV**, strike **5500**

### Trade Pattern Clues

- Common trade sizes: [(2, 73), (4, 73), (5, 68), (3, 53)]
- Sizes often hitting new daily highs/lows: [(4, 8), (3, 5), (5, 5), (2, 5)]

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
- `slow_random_walk`: 2.284
- `anchored_market_maker`: 2.124
- `trending_drift_carry`: 1.496
- `local_fair_microstructure`: 1.148
- `mean_reverting_ou`: 0.950

## VEV_6000

### Classification

- Primary archetype: **option_family**
- Secondary archetypes: anchored_market_maker, bot_driven_overlay, slow_random_walk
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **284**
- Mean mid: **0.50**
- Mid std on valid rows: **0.000**
- Mean spread: **1.000**
- Avg top-of-book depth: **44.96**
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

- Common trade sizes: [(4, 78), (2, 76), (5, 74), (3, 56)]
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
- Rounds seen: [3]
- Days seen: [0, 1, 2]

### Metrics

- Valid rows / total rows: **30000 / 30000**
- Trade rows: **284**
- Mean mid: **0.50**
- Mid std on valid rows: **0.000**
- Mean spread: **1.000**
- Avg top-of-book depth: **30.96**
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

- Common trade sizes: [(4, 78), (2, 76), (5, 74), (3, 56)]
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
