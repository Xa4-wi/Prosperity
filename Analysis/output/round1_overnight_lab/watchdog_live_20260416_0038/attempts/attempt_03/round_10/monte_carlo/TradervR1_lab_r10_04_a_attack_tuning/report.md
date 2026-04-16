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

- Combined total PnL: `288784.0000`
- Day -1: `95822.0000`
- Day -2: `96030.0000`
- Day 0: `96932.0000`

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

- Overall samples: `6` | mean `124980.5833` | p10 `-20433.75` | cvar10 `-37039.0` | std `127104.0616`
- Profile `all`: count `6`, mean `124980.5833`, p10 `-20433.75`, cvar10 `-37039.0`
- Profile `plausible`: count `6`, mean `124980.5833`, p10 `-20433.75`, cvar10 `-37039.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49610.25`, p10 `-19709.15`, cvar10 `-37039.0`
- `bootstrap_path`: count `2`, mean `38961.25`, p10 `4729.45`, cvar10 `-3828.5`
- `original_noise`: count `2`, mean `286370.25`, p10 `285732.85`, cvar10 `285573.5`

## Comparison

- Primary: `TradervR1_lab_r10_04_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-670.8333`
- Median delta: `1033.5`
- P10 delta: `-5808.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4153.0`, p10 delta `-10815.4`, win rate `0.5`
- `bootstrap_path`: mean delta `1229.75`, p10 delta `1133.15`, win rate `1.0`
- `original_noise`: mean delta `910.75`, p10 delta `872.95`, win rate `1.0`

- Profile `all`: mean delta `-670.8333`, p10 delta `-5808.75`, win rate `0.8333`
- Profile `plausible`: mean delta `-670.8333`, p10 delta `-5808.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

