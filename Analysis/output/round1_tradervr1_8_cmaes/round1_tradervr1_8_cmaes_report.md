# TradervR1_8 Round 1 Focused CMA-ES CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/TraderFactory/configs/round1/tradervr1_8_cmaes.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_8.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_tradervr1_8_cmaes/bots/TradervR1_8_best.py`
- Total evaluations: `16`

## Baseline Replay

- Day -2: `89067.0000`
- Day -1: `90939.0000`
- Day 0: `89637.0000`

## Best Candidate

- Objective: `90115.4209`
- Average score: `90132.0000`
- Regression penalty: `0.0000`
- Imbalance penalty: `16.2000`
- Drift penalty: `0.3791`

- Day -2: `89314.0000`
- Day -1: `91183.0000`
- Day 0: `89899.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| ASH_BASE_EDGE | 7.093185 | 6.963193 | -1.83% |
| ASH_IMBALANCE_FAIR_WEIGHT | 3.486671 | 3.425625 | -1.75% |
| ASH_INVENTORY_SKEW | 0.094027 | 0.096267 | +2.38% |
| DRIFT_PER_TIMESTAMP | 0.001023 | 0.001019 | -0.46% |
| RESIDUAL_ALPHA | 0.105057 | 0.104585 | -0.45% |
| EARLY_LONG_BIAS | 31.995576 | 31.467842 | -1.65% |
| ZSCORE_SELL_PENALTY | 9.033857 | 9.052129 | +0.20% |
| INVENTORY_SKEW | 0.083039 | 0.081772 | -1.53% |
| BASE_TAKE_EDGE | 1.072419 | 1.087131 | +1.37% |
| BASE_QUOTE_EDGE | 2.424259 | 2.459784 | +1.47% |
| BULLISH_IMBALANCE | 0.037330 | 0.035670 | -4.45% |
| OVEREXTENSION_Z | 1.165084 | 1.185474 | +1.75% |
| LOOKAHEAD_BONUS | 4.052068 | 4.086796 | +0.86% |
| PASSIVE_SELL_BUFFER | 7.825292 | 7.810083 | -0.19% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 89888.4172 | 90029.0000 | 89888.4172 | 90029.0000 | 0.046770 |
| 2 | 90074.0792 | 90147.8333 | 90074.0792 | 90147.8333 | 0.045369 |
| 3 | 90115.4209 | 90132.0000 | 90115.4209 | 90132.0000 | 0.043445 |
