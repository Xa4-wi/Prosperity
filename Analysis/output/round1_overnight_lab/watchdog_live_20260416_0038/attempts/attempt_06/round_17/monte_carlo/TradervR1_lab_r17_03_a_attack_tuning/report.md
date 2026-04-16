# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_03_a_attack_tuning`
- Bots: TradervR1_lab_r17_03_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_03_a_attack_tuning

- Combined total PnL: `289742.5000`
- Day -1: `96126.0000`
- Day -2: `96285.5000`
- Day 0: `97331.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_03_a_attack_tuning

- Overall samples: `6` | mean `126135.25` | p10 `-15759.0` | cvar10 `-28668.0` | std `125491.1003`
- Profile `all`: count `6`, mean `126135.25`, p10 `-15759.0`, cvar10 `-28668.0`
- Profile `plausible`: count `6`, mean `126135.25`, p10 `-15759.0`, cvar10 `-28668.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51264.75`, p10 `-12681.45`, cvar10 `-28668.0`
- `bootstrap_path`: count `2`, mean `39829.5`, p10 `5685.9`, cvar10 `-2850.0`
- `original_noise`: count `2`, mean `287311.5`, p10 `286432.7`, cvar10 `286213.0`

## Comparison

- Primary: `TradervR1_lab_r17_03_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `483.8333`
- Median delta: `1685.0`
- P10 delta: `-2498.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2498.5`, p10 delta `-3787.7`, win rate `0.0`
- `bootstrap_path`: mean delta `2098.0`, p10 delta `1913.2`, win rate `1.0`
- `original_noise`: mean delta `1852.0`, p10 delta `1572.8`, win rate `1.0`

- Profile `all`: mean delta `483.8333`, p10 delta `-2498.5`, win rate `0.6667`
- Profile `plausible`: mean delta `483.8333`, p10 delta `-2498.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

