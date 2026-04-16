# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_01_p_carry_defense`
- Bots: TradervR1_lab_r15_01_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_01_p_carry_defense

- Combined total PnL: `288951.0000`
- Day -1: `95917.0000`
- Day -2: `95973.0000`
- Day 0: `97061.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_01_p_carry_defense

- Overall samples: `6` | mean `126176.9167` | p10 `-14856.25` | cvar10 `-26109.0` | std `124829.9206`
- Profile `all`: count `6`, mean `126176.9167`, p10 `-14856.25`, cvar10 `-26109.0`
- Profile `plausible`: count `6`, mean `126176.9167`, p10 `-14856.25`, cvar10 `-26109.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52925.75`, p10 `-10302.05`, cvar10 `-26109.0`
- `bootstrap_path`: count `2`, mean `39042.25`, p10 `4925.65`, cvar10 `-3603.5`
- `original_noise`: count `2`, mean `286562.75`, p10 `285955.35`, cvar10 `285803.5`

## Comparison

- Primary: `TradervR1_lab_r15_01_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `525.5`
- Median delta: `1069.75`
- P10 delta: `-837.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-837.5`, p10 delta `-1408.3`, win rate `0.0`
- `bootstrap_path`: mean delta `1310.75`, p10 delta `1098.95`, win rate `1.0`
- `original_noise`: mean delta `1103.25`, p10 delta `1095.45`, win rate `1.0`

- Profile `all`: mean delta `525.5`, p10 delta `-837.5`, win rate `0.6667`
- Profile `plausible`: mean delta `525.5`, p10 delta `-837.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

