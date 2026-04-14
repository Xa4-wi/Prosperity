# TradervR1_1 Round 1 Focused CMA-ES CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/TraderFactory/configs/round1/tradervr1_1_cmaes.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_1.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_tradervr1_1_cmaes/bots/TradervR1_1_best.py`
- Total evaluations: `9`

## Baseline Replay

- Day -2: `29712.0000`
- Day -1: `30710.0000`
- Day 0: `28785.0000`

## Best Candidate

- Objective: `74624.6979`
- Average score: `75887.8333`
- Regression penalty: `0.0000`
- Imbalance penalty: `1262.7000`
- Drift penalty: `0.4355`

- Day -2: `74472.5000`
- Day -1: `77509.0000`
- Day 0: `75682.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| ASH_DEFAULT_EDGE | 8.000000 | 7.946659 | -0.67% |
| ASH_INVENTORY_SKEW | 0.090000 | 0.081970 | -8.92% |
| DRIFT_PER_TIMESTAMP | 0.001000 | 0.001140 | +14.02% |
| RESIDUAL_ALPHA | 0.100000 | 0.110626 | +10.63% |
| BASE_CARRY | 8.000000 | 8.243888 | +3.05% |
| EDGE_TARGET_SCALE | 10.000000 | 9.653408 | -3.47% |
| ZSCORE_BUY_BONUS | 10.000000 | 9.696484 | -3.04% |
| ZSCORE_SELL_PENALTY | 12.000000 | 10.372821 | -13.56% |
| INVENTORY_SKEW | 0.100000 | 0.103532 | +3.53% |
| BASE_TAKE_EDGE | 1.200000 | 1.242362 | +3.53% |
| BASE_QUOTE_EDGE | 3.000000 | 3.066146 | +2.20% |
| BULLISH_IMBALANCE | 0.080000 | 0.071731 | -10.34% |
| OVEREXTENSION_Z | 0.950000 | 0.912142 | -3.99% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 74409.3603 | 75676.3333 | 74409.3603 | 75676.3333 | 0.078727 |
| 2 | 74624.6979 | 75887.8333 | 74624.6979 | 75887.8333 | 0.075657 |
