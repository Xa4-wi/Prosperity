# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r05_02_a_quality_guard`
- Bots: TradervR1_lab_r05_02_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r05_02_a_quality_guard

- Combined total PnL: `290529.5000`
- Day -1: `96432.0000`
- Day -2: `96724.5000`
- Day 0: `97373.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r05_02_a_quality_guard

- Overall samples: `6` | mean `126922.9167` | p10 `-17697.25` | cvar10 `-33755.0` | std `126971.4597`
- Profile `all`: count `6`, mean `126922.9167`, p10 `-17697.25`, cvar10 `-33755.0`
- Profile `plausible`: count `6`, mean `126922.9167`, p10 `-17697.25`, cvar10 `-33755.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50891.25`, p10 `-16825.75`, cvar10 `-33755.0`
- `bootstrap_path`: count `2`, mean `41027.25`, p10 `6893.85`, cvar10 `-1639.5`
- `original_noise`: count `2`, mean `288850.25`, p10 `288299.25`, cvar10 `288161.5`

## Comparison

- Primary: `TradervR1_lab_r05_02_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1271.5`
- Median delta: `3390.75`
- P10 delta: `-3072.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2872.0`, p10 delta `-7932.0`, win rate `0.5`
- `bootstrap_path`: mean delta `3295.75`, p10 delta `3100.75`, win rate `1.0`
- `original_noise`: mean delta `3390.75`, p10 delta `3342.15`, win rate `1.0`

- Profile `all`: mean delta `1271.5`, p10 delta `-3072.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1271.5`, p10 delta `-3072.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

