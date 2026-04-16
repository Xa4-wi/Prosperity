# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_01_a_local_fair_blend`
- Bots: TradervR1_lab_r10_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_01_a_local_fair_blend

- Combined total PnL: `287575.5000`
- Day -1: `95564.0000`
- Day -2: `95588.5000`
- Day 0: `96423.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_01_a_local_fair_blend

- Overall samples: `6` | mean `125425.25` | p10 `-14178.0` | cvar10 `-23035.0` | std `124158.3162`
- Profile `all`: count `6`, mean `125425.25`, p10 `-14178.0`, cvar10 `-23035.0`
- Profile `plausible`: count `6`, mean `125425.25`, p10 `-14178.0`, cvar10 `-23035.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52592.75`, p10 `-7909.45`, cvar10 `-23035.0`
- `bootstrap_path`: count `2`, mean `37955.5`, p10 `3334.3`, cvar10 `-5321.0`
- `original_noise`: count `2`, mean `285727.5`, p10 `284885.1`, cvar10 `284674.5`

## Comparison

- Primary: `TradervR1_lab_r10_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-226.1667`
- Median delta: `268.0`
- P10 delta: `-2003.0`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-1170.5`, p10 delta `-3325.3`, win rate `0.5`
- `bootstrap_path`: mean delta `224.0`, p10 delta `-68.8`, win rate `0.5`
- `original_noise`: mean delta `268.0`, p10 delta `25.2`, win rate `0.5`

- Profile `all`: mean delta `-226.1667`, p10 delta `-2003.0`, win rate `0.5`
- Profile `plausible`: mean delta `-226.1667`, p10 delta `-2003.0`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

