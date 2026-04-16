# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality`
- Bots: TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality

- Combined total PnL: `288976.5000`
- Day -1: `96076.0000`
- Day -2: `95915.5000`
- Day 0: `96985.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality

- Overall samples: `6` | mean `124560.9167` | p10 `-19657.25` | cvar10 `-36071.0` | std `126932.9156`
- Profile `all`: count `6`, mean `124560.9167`, p10 `-19657.25`, cvar10 `-36071.0`
- Profile `plausible`: count `6`, mean `124560.9167`, p10 `-19657.25`, cvar10 `-36071.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `46951.0`, p10 `-19466.6`, cvar10 `-36071.0`
- `bootstrap_path`: count `2`, mean `39756.75`, p10 `5356.55`, cvar10 `-3243.5`
- `original_noise`: count `2`, mean `286975.0`, p10 `286241.4`, cvar10 `286058.0`

## Comparison

- Primary: `TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1090.5`
- Median delta: `1515.5`
- P10 delta: `-6812.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-6812.25`, p10 delta `-10572.85`, win rate `0.0`
- `bootstrap_path`: mean delta `2025.25`, p10 delta `1953.45`, win rate `1.0`
- `original_noise`: mean delta `1515.5`, p10 delta `1381.5`, win rate `1.0`

- Profile `all`: mean delta `-1090.5`, p10 delta `-6812.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-1090.5`, p10 delta `-6812.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

