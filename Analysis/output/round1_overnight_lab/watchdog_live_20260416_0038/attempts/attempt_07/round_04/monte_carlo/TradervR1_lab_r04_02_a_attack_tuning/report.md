# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_02_a_attack_tuning`
- Bots: TradervR1_lab_r04_02_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_02_a_attack_tuning

- Combined total PnL: `288531.0000`
- Day -1: `95742.0000`
- Day -2: `95845.0000`
- Day 0: `96944.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_02_a_attack_tuning

- Overall samples: `6` | mean `126210.3333` | p10 `-17171.0` | cvar10 `-30823.0` | std `125756.5148`
- Profile `all`: count `6`, mean `126210.3333`, p10 `-17171.0`, cvar10 `-30823.0`
- Profile `plausible`: count `6`, mean `126210.3333`, p10 `-17171.0`, cvar10 `-30823.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53170.0`, p10 `-14024.4`, cvar10 `-30823.0`
- `bootstrap_path`: count `2`, mean `39098.0`, p10 `5004.4`, cvar10 `-3519.0`
- `original_noise`: count `2`, mean `286363.0`, p10 `285672.6`, cvar10 `285500.0`

## Comparison

- Primary: `TradervR1_lab_r04_02_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `558.9167`
- Median delta: `1045.0`
- P10 delta: `-2737.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-593.25`, p10 delta `-5130.65`, win rate `0.5`
- `bootstrap_path`: mean delta `1366.5`, p10 delta `1131.7`, win rate `1.0`
- `original_noise`: mean delta `903.5`, p10 delta `812.7`, win rate `1.0`

- Profile `all`: mean delta `558.9167`, p10 delta `-2737.5`, win rate `0.8333`
- Profile `plausible`: mean delta `558.9167`, p10 delta `-2737.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

