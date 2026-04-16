# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Bots: TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality.py, TradervR1_34_1.py

## Families

- `original_noise`: Original historical path with very mild execution-noise perturbations.
- `bootstrap_path`: Block-bootstrap of the historical path with no fill perturbation.
- `bootstrap_balanced`: Block-bootstrap with calibrated mild-to-moderate execution degradation.

## Baseline Replay

### TradervR1_34_1

- Combined total PnL: `287305.5000`
- Day -1: `95486.0000`
- Day -2: `95526.5000`
- Day 0: `96293.0000`

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Combined total PnL: `290141.0000`
- Day -1: `96192.0000`
- Day -2: `96390.0000`
- Day 0: `97559.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Overall samples: `6` | mean `127030.8333` | p10 `-13869.5` | cvar10 `-25751.0` | std `124873.2726`
- Profile `all`: count `6`, mean `127030.8333`, p10 `-13869.5`, cvar10 `-25751.0`
- Profile `plausible`: count `6`, mean `127030.8333`, p10 `-13869.5`, cvar10 `-25751.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53039.75`, p10 `-9992.85`, cvar10 `-25751.0`
- `bootstrap_path`: count `2`, mean `40411.5`, p10 `6491.9`, cvar10 `-1988.0`
- `original_noise`: count `2`, mean `287641.25`, p10 `286838.25`, cvar10 `286637.5`

## Comparison

- Primary: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1379.4167`
- Median delta: `2048.25`
- P10 delta: `-723.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-723.5`, p10 delta `-1099.1`, win rate `0.0`
- `bootstrap_path`: mean delta `2680.0`, p10 delta `2271.2`, win rate `1.0`
- `original_noise`: mean delta `2181.75`, p10 delta `1978.35`, win rate `1.0`

- Profile `all`: mean delta `1379.4167`, p10 delta `-723.5`, win rate `0.6667`
- Profile `plausible`: mean delta `1379.4167`, p10 delta `-723.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

