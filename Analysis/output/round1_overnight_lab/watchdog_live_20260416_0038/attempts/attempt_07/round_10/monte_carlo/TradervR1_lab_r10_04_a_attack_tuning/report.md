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

- Combined total PnL: `289549.0000`
- Day -1: `96137.0000`
- Day -2: `96309.0000`
- Day 0: `97103.0000`

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

- Overall samples: `6` | mean `125993.5` | p10 `-16756.25` | cvar10 `-30519.0` | std `125998.1214`
- Profile `all`: count `6`, mean `125993.5`, p10 `-16756.25`, cvar10 `-30519.0`
- Profile `plausible`: count `6`, mean `125993.5`, p10 `-16756.25`, cvar10 `-30519.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50499.5`, p10 `-14315.3`, cvar10 `-30519.0`
- `bootstrap_path`: count `2`, mean `39899.75`, p10 `5585.15`, cvar10 `-2993.5`
- `original_noise`: count `2`, mean `287581.25`, p10 `286925.05`, cvar10 `286761.0`

## Comparison

- Primary: `TradervR1_lab_r10_04_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `342.0833`
- Median delta: `2101.0`
- P10 delta: `-3263.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-3263.75`, p10 delta `-5421.55`, win rate `0.0`
- `bootstrap_path`: mean delta `2168.25`, p10 delta `2154.45`, win rate `1.0`
- `original_noise`: mean delta `2121.75`, p10 delta `2065.15`, win rate `1.0`

- Profile `all`: mean delta `342.0833`, p10 delta `-3263.75`, win rate `0.6667`
- Profile `plausible`: mean delta `342.0833`, p10 delta `-3263.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

