# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_04_a_attack_tuning`
- Bots: TradervR1_lab_r10_04_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_04_a_attack_tuning

- Combined total PnL: `287828.0000`
- Day -1: `95642.0000`
- Day -2: `95679.0000`
- Day 0: `96507.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_04_a_attack_tuning

- Overall samples: `6` | mean `124076.9167` | p10 `-18549.75` | cvar10 `-32522.0` | std `126191.1311`
- Profile `all`: count `6`, mean `124076.9167`, p10 `-18549.75`, cvar10 `-32522.0`
- Profile `plausible`: count `6`, mean `124076.9167`, p10 `-18549.75`, cvar10 `-32522.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47504.75`, p10 `-16516.65`, cvar10 `-32522.0`
- `bootstrap_path`: count `2`, mean `38418.75`, p10 `4021.75`, cvar10 `-4577.5`
- `original_noise`: count `2`, mean `286307.25`, p10 `285835.85`, cvar10 `285718.0`

## Comparison

- Primary: `TradervR1_lab_r10_04_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1574.5`
- Median delta: `644.5`
- P10 delta: `-6258.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-6258.5`, p10 delta `-7622.9`, win rate `0.0`
- `bootstrap_path`: mean delta `687.25`, p10 delta `618.65`, win rate `1.0`
- `original_noise`: mean delta `847.75`, p10 delta `719.55`, win rate `1.0`

- Profile `all`: mean delta `-1574.5`, p10 delta `-6258.5`, win rate `0.6667`
- Profile `plausible`: mean delta `-1574.5`, p10 delta `-6258.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

