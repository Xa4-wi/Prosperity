# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Bots: TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Combined total PnL: `290153.5000`
- Day -1: `96251.0000`
- Day -2: `96406.5000`
- Day 0: `97496.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Overall samples: `6` | mean `126051.1667` | p10 `-19621.25` | cvar10 `-36771.0` | std `127566.0915`
- Profile `all`: count `6`, mean `126051.1667`, p10 `-19621.25`, cvar10 `-36771.0`
- Profile `plausible`: count `6`, mean `126051.1667`, p10 `-19621.25`, cvar10 `-36771.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49166.75`, p10 `-19583.45`, cvar10 `-36771.0`
- `bootstrap_path`: count `2`, mean `40570.25`, p10 `6136.85`, cvar10 `-2471.5`
- `original_noise`: count `2`, mean `288416.5`, p10 `287732.1`, cvar10 `287561.0`

## Comparison

- Primary: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `399.75`
- Median delta: `2910.5`
- P10 delta: `-4752.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4596.5`, p10 delta `-10689.7`, win rate `0.5`
- `bootstrap_path`: mean delta `2838.75`, p10 delta `2733.75`, win rate `1.0`
- `original_noise`: mean delta `2957.0`, p10 delta `2872.2`, win rate `1.0`

- Profile `all`: mean delta `399.75`, p10 delta `-4752.75`, win rate `0.8333`
- Profile `plausible`: mean delta `399.75`, p10 delta `-4752.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

