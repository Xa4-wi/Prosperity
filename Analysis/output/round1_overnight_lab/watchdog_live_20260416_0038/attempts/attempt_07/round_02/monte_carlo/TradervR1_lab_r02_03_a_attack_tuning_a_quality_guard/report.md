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

- Combined total PnL: `290370.0000`
- Day -1: `96307.0000`
- Day -2: `96498.0000`
- Day 0: `97565.0000`

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

- Overall samples: `6` | mean `127641.25` | p10 `-15152.25` | cvar10 `-28256.0` | std `125803.8753`
- Profile `all`: count `6`, mean `127641.25`, p10 `-15152.25`, cvar10 `-28256.0`
- Profile `plausible`: count `6`, mean `127641.25`, p10 `-15152.25`, cvar10 `-28256.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53605.25`, p10 `-11883.75`, cvar10 `-28256.0`
- `bootstrap_path`: count `2`, mean `40707.75`, p10 `6502.75`, cvar10 `-2048.5`
- `original_noise`: count `2`, mean `288610.75`, p10 `288022.15`, cvar10 `287875.0`

## Comparison

- Primary: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1989.8333`
- Median delta: `3134.0`
- P10 delta: `-438.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-158.0`, p10 delta `-2990.0`, win rate `0.5`
- `bootstrap_path`: mean delta `2976.25`, p10 delta `2852.85`, win rate `1.0`
- `original_noise`: mean delta `3151.25`, p10 delta `3140.25`, win rate `1.0`

- Profile `all`: mean delta `1989.8333`, p10 delta `-438.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1989.8333`, p10 delta `-438.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

