# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_cmaes_ash_attack_tuning`
- Bots: TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_best

- Combined total PnL: `289263.0000`
- Day -1: `96008.0000`
- Day -2: `96044.0000`
- Day 0: `97211.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_best

- Overall samples: `6` | mean `128024.5` | p10 `-10856.75` | cvar10 `-18530.0` | std `123481.7678`
- Profile `all`: count `6`, mean `128024.5`, p10 `-10856.75`, cvar10 `-18530.0`
- Profile `plausible`: count `6`, mean `128024.5`, p10 `-10856.75`, cvar10 `-18530.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `57177.5`, p10 `-3388.5`, cvar10 `-18530.0`
- `bootstrap_path`: count `2`, mean `39661.25`, p10 `5385.45`, cvar10 `-3183.5`
- `original_noise`: count `2`, mean `287234.75`, p10 `286576.15`, cvar10 `286411.5`

## Comparison

- Primary: `TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2373.0833`
- Median delta: `1856.5`
- P10 delta: `1251.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `3414.25`, p10 delta `1323.25`, win rate `1.0`
- `bootstrap_path`: mean delta `1929.75`, p10 delta `1877.15`, win rate `1.0`
- `original_noise`: mean delta `1775.25`, p10 delta `1716.25`, win rate `1.0`

- Profile `all`: mean delta `2373.0833`, p10 delta `1251.0`, win rate `1.0`
- Profile `plausible`: mean delta `2373.0833`, p10 delta `1251.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

