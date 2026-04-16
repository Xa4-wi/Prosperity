# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_04_p_carry_defense`
- Bots: TradervR1_lab_r15_04_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_04_p_carry_defense

- Combined total PnL: `289032.5000`
- Day -1: `96029.0000`
- Day -2: `96130.5000`
- Day 0: `96873.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_04_p_carry_defense

- Overall samples: `6` | mean `127296.25` | p10 `-12543.5` | cvar10 `-21851.0` | std `124140.8527`
- Profile `all`: count `6`, mean `127296.25`, p10 `-12543.5`, cvar10 `-21851.0`
- Profile `plausible`: count `6`, mean `127296.25`, p10 `-12543.5`, cvar10 `-21851.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55150.5`, p10 `-6450.7`, cvar10 `-21851.0`
- `bootstrap_path`: count `2`, mean `39543.0`, p10 `5319.8`, cvar10 `-3236.0`
- `original_noise`: count `2`, mean `287195.25`, p10 `286797.05`, cvar10 `286697.5`

## Comparison

- Primary: `TradervR1_lab_r15_04_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1644.8333`
- Median delta: `1811.5`
- P10 delta: `775.75`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1387.25`, p10 delta `331.45`, win rate `1.0`
- `bootstrap_path`: mean delta `1811.5`, p10 delta `1706.3`, win rate `1.0`
- `original_noise`: mean delta `1735.75`, p10 delta `1534.35`, win rate `1.0`

- Profile `all`: mean delta `1644.8333`, p10 delta `775.75`, win rate `1.0`
- Profile `plausible`: mean delta `1644.8333`, p10 delta `775.75`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

