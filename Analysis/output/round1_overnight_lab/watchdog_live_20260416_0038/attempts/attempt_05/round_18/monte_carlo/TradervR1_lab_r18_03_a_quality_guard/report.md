# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_03_a_quality_guard`
- Bots: TradervR1_lab_r18_03_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_03_a_quality_guard

- Combined total PnL: `289884.0000`
- Day -1: `96445.0000`
- Day -2: `96260.0000`
- Day 0: `97179.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_03_a_quality_guard

- Overall samples: `6` | mean `126736.5833` | p10 `-15224.75` | cvar10 `-27536.0` | std `125327.9367`
- Profile `all`: count `6`, mean `126736.5833`, p10 `-15224.75`, cvar10 `-27536.0`
- Profile `plausible`: count `6`, mean `126736.5833`, p10 `-15224.75`, cvar10 `-27536.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52684.5`, p10 `-11491.9`, cvar10 `-27536.0`
- `bootstrap_path`: count `2`, mean `40041.25`, p10 `5677.45`, cvar10 `-2913.5`
- `original_noise`: count `2`, mean `287484.0`, p10 `286567.6`, cvar10 `286338.5`

## Comparison

- Primary: `TradervR1_lab_r18_03_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1085.1667`
- Median delta: `1947.0`
- P10 delta: `-1078.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1078.75`, p10 delta `-2598.15`, win rate `0.5`
- `bootstrap_path`: mean delta `2309.75`, p10 delta `2274.35`, win rate `1.0`
- `original_noise`: mean delta `2024.5`, p10 delta `1707.7`, win rate `1.0`

- Profile `all`: mean delta `1085.1667`, p10 delta `-1078.75`, win rate `0.8333`
- Profile `plausible`: mean delta `1085.1667`, p10 delta `-1078.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

