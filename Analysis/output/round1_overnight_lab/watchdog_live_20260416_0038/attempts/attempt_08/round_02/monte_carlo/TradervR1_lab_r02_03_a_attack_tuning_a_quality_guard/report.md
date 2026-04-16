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

- Combined total PnL: `290150.5000`
- Day -1: `96267.0000`
- Day -2: `96408.5000`
- Day 0: `97475.0000`

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

- Overall samples: `6` | mean `125394.0833` | p10 `-17881.25` | cvar10 `-33291.0` | std `126627.225`
- Profile `all`: count `6`, mean `125394.0833`, p10 `-17881.25`, cvar10 `-33291.0`
- Profile `plausible`: count `6`, mean `125394.0833`, p10 `-17881.25`, cvar10 `-33291.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47650.0`, p10 `-17102.8`, cvar10 `-33291.0`
- `bootstrap_path`: count `2`, mean `40495.25`, p10 `6121.85`, cvar10 `-2471.5`
- `original_noise`: count `2`, mean `288037.0`, p10 `287197.0`, cvar10 `286987.0`

## Comparison

- Primary: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-257.3333`
- Median delta: `2492.25`
- P10 delta: `-6113.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-6113.25`, p10 delta `-8209.05`, win rate `0.0`
- `bootstrap_path`: mean delta `2763.75`, p10 delta `2718.75`, win rate `1.0`
- `original_noise`: mean delta `2577.5`, p10 delta `2337.1`, win rate `1.0`

- Profile `all`: mean delta `-257.3333`, p10 delta `-6113.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-257.3333`, p10 delta `-6113.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

