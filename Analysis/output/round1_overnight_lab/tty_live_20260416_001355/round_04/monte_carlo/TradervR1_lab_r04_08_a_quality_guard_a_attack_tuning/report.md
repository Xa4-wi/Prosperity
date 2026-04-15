# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning`
- Bots: TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning

- Combined total PnL: `290905.0000`
- Day -1: `96504.0000`
- Day -2: `96784.0000`
- Day 0: `97617.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning

- Overall samples: `6` | mean `129781.6667` | p10 `-9235.5` | cvar10 `-17442.0` | std `123531.1226`
- Profile `all`: count `6`, mean `129781.6667`, p10 `-9235.5`, cvar10 `-17442.0`
- Profile `plausible`: count `6`, mean `129781.6667`, p10 `-9235.5`, cvar10 `-17442.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `58929.75`, p10 `-2167.65`, cvar10 `-17442.0`
- `bootstrap_path`: count `2`, mean `41498.0`, p10 `7476.4`, cvar10 `-1029.0`
- `original_noise`: count `2`, mean `288917.25`, p10 `288356.65`, cvar10 `288216.5`

## Comparison

- Primary: `TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4130.25`
- Median delta: `3457.75`
- P10 delta: `3300.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `5166.5`, p10 delta `3606.9`, win rate `1.0`
- `bootstrap_path`: mean delta `3766.5`, p10 delta `3459.7`, win rate `1.0`
- `original_noise`: mean delta `3457.75`, p10 delta `3418.75`, win rate `1.0`

- Profile `all`: mean delta `4130.25`, p10 delta `3300.0`, win rate `1.0`
- Profile `plausible`: mean delta `4130.25`, p10 delta `3300.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

