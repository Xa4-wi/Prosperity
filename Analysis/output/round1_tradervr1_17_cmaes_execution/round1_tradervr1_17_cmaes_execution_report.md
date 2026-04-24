# TradervR1_17 Round 1 Pepper Execution CMA-ES CMA-ES Report

- Config: `TraderFactory/configs/round1/tradervr1_17_cmaes_execution.json`
- Source bot: `Bots/Round1/TradervR1_17.py`
- Best bot: `Analysis/output/round1_tradervr1_17_cmaes_execution/bots/TradervR1_17_best.py`
- Total evaluations: `16`

## Baseline Replay

- Day -2: `94833.0000`
- Day -1: `95520.0000`
- Day 0: `94199.0000`

## Best Candidate

- Objective: `94850.6667`
- Average score: `94850.6667`
- Regression penalty: `0.0000`
- Imbalance penalty: `0.0000`
- Drift penalty: `0.0000`

- Day -2: `94833.0000`
- Day -1: `95520.0000`
- Day 0: `94199.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| IPR_RESIDUAL_ALPHA | 0.100000 | 0.100000 | +0.00% |
| IPR_SHORT_MID_ALPHA | 0.180000 | 0.180000 | +0.00% |
| IPR_LONG_MID_ALPHA | 0.050000 | 0.050000 | +0.00% |
| IPR_LOOKAHEAD_BONUS | 4.884903 | 4.884903 | +0.00% |
| IPR_ZSCORE_BUY_BONUS | 10.000000 | 10.000000 | +0.00% |
| IPR_ZSCORE_SELL_PENALTY | 6.000000 | 6.000000 | +0.00% |
| IPR_INVENTORY_SKEW | 0.078000 | 0.078000 | +0.00% |
| IPR_BASE_QUOTE_EDGE | 5.000000 | 5.000000 | +0.00% |
| IPR_PASSIVE_FRONT_SIZE | 9.000000 | 9.000000 | +0.00% |
| IPR_PASSIVE_SELL_BUFFER | 6.000000 | 6.000000 | +0.00% |
| IPR_OVEREXTENSION_Z | 1.050000 | 1.050000 | +0.00% |
| IPR_BULLISH_IMBALANCE | 0.050000 | 0.050000 | +0.00% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 94830.7898 | 94894.6667 | 94850.6667 | 94850.6667 | 0.043377 |
| 2 | 94667.6761 | 94938.0000 | 94850.6667 | 94850.6667 | 0.042751 |
| 3 | 94830.3136 | 94894.6667 | 94850.6667 | 94850.6667 | 0.044433 |
