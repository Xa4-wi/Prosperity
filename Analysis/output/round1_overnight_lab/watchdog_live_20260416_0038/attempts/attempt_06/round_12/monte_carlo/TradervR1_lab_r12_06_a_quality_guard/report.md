# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_06_a_quality_guard`
- Bots: TradervR1_lab_r12_06_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_06_a_quality_guard

- Combined total PnL: `289283.0000`
- Day -1: `96028.0000`
- Day -2: `96071.0000`
- Day 0: `97184.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_06_a_quality_guard

- Overall samples: `6` | mean `126523.75` | p10 `-14789.25` | cvar10 `-26251.0` | std `125033.8482`
- Profile `all`: count `6`, mean `126523.75`, p10 `-14789.25`, cvar10 `-26251.0`
- Profile `plausible`: count `6`, mean `126523.75`, p10 `-14789.25`, cvar10 `-26251.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52734.5`, p10 `-10453.9`, cvar10 `-26251.0`
- `bootstrap_path`: count `2`, mean `39626.75`, p10 `5263.35`, cvar10 `-3327.5`
- `original_noise`: count `2`, mean `287210.0`, p10 `286590.4`, cvar10 `286435.5`

## Comparison

- Primary: `TradervR1_lab_r12_06_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `872.3333`
- Median delta: `1750.5`
- P10 delta: `-1028.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-1028.75`, p10 delta `-1560.15`, win rate `0.0`
- `bootstrap_path`: mean delta `1895.25`, p10 delta `1860.25`, win rate `1.0`
- `original_noise`: mean delta `1750.5`, p10 delta `1730.5`, win rate `1.0`

- Profile `all`: mean delta `872.3333`, p10 delta `-1028.75`, win rate `0.6667`
- Profile `plausible`: mean delta `872.3333`, p10 delta `-1028.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

