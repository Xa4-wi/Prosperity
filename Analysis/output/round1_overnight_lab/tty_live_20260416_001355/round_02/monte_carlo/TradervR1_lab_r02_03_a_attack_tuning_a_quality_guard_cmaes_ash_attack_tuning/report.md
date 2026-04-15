# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_cmaes_ash_attack_tuning`
- Bots: TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best

- Combined total PnL: `290538.5000`
- Day -1: `96444.0000`
- Day -2: `96660.5000`
- Day 0: `97434.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best

- Overall samples: `6` | mean `127153.4167` | p10 `-15952.5` | cvar10 `-30377.0` | std `126133.9887`
- Profile `all`: count `6`, mean `127153.4167`, p10 `-15952.5`, cvar10 `-30377.0`
- Profile `plausible`: count `6`, mean `127153.4167`, p10 `-15952.5`, cvar10 `-30377.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51741.5`, p10 `-13953.3`, cvar10 `-30377.0`
- `bootstrap_path`: count `2`, mean `41088.5`, p10 `6995.3`, cvar10 `-1528.0`
- `original_noise`: count `2`, mean `288630.25`, p10 `287896.85`, cvar10 `287713.5`

## Comparison

- Primary: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1502.0`
- Median delta: `3033.25`
- P10 delta: `-2021.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2021.75`, p10 delta `-5059.55`, win rate `0.5`
- `bootstrap_path`: mean delta `3357.0`, p10 delta `3121.8`, win rate `1.0`
- `original_noise`: mean delta `3170.75`, p10 delta `3036.95`, win rate `1.0`

- Profile `all`: mean delta `1502.0`, p10 delta `-2021.75`, win rate `0.8333`
- Profile `plausible`: mean delta `1502.0`, p10 delta `-2021.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

