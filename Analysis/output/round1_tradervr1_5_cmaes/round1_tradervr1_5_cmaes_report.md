# TradervR1_5 Round 1 Focused CMA-ES CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/TraderFactory/configs/round1/tradervr1_5_cmaes.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_5.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_tradervr1_5_cmaes/bots/TradervR1_5_best.py`
- Total evaluations: `16`

## Baseline Replay

- Day -2: `81809.5000`
- Day -1: `84382.0000`
- Day 0: `82635.0000`

## Best Candidate

- Objective: `89319.4002`
- Average score: `89881.0000`
- Regression penalty: `0.0000`
- Imbalance penalty: `560.4000`
- Drift penalty: `1.1998`

- Day -2: `89067.0000`
- Day -1: `90939.0000`
- Day 0: `89637.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| ASH_BASE_EDGE | 7.500000 | 7.093185 | -5.42% |
| ASH_IMBALANCE_FAIR_WEIGHT | 3.400000 | 3.486671 | +2.55% |
| ASH_INVENTORY_SKEW | 0.080000 | 0.094027 | +17.53% |
| DRIFT_PER_TIMESTAMP | 0.001000 | 0.001023 | +2.34% |
| RESIDUAL_ALPHA | 0.100000 | 0.105057 | +5.06% |
| BASE_CARRY | 12.000000 | 12.290586 | +2.42% |
| EARLY_LONG_BIAS | 30.000000 | 31.995576 | +6.65% |
| EDGE_TARGET_SCALE | 12.000000 | 11.928238 | -0.60% |
| ZSCORE_SELL_PENALTY | 8.000000 | 9.033857 | +12.92% |
| INVENTORY_SKEW | 0.078000 | 0.083039 | +6.46% |
| BASE_TAKE_EDGE | 1.000000 | 1.072419 | +7.24% |
| BASE_QUOTE_EDGE | 2.400000 | 2.424259 | +1.01% |
| BULLISH_IMBALANCE | 0.050000 | 0.037330 | -25.34% |
| OVEREXTENSION_Z | 1.050000 | 1.165084 | +10.96% |
| LOOKAHEAD_BONUS | 4.500000 | 4.052068 | -9.95% |
| PASSIVE_SELL_BUFFER | 8.000000 | 7.825292 | -2.18% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 88390.1204 | 89268.6667 | 88390.1204 | 89268.6667 | 0.066611 |
| 2 | 89075.8616 | 89648.8333 | 89075.8616 | 89648.8333 | 0.065198 |
| 3 | 89319.4002 | 89881.0000 | 89319.4002 | 89881.0000 | 0.065273 |
