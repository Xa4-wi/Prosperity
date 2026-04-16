# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_05_p_carry_defense`
- Bots: TradervR1_lab_r18_05_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_05_p_carry_defense

- Combined total PnL: `289265.0000`
- Day -1: `96012.0000`
- Day -2: `96071.0000`
- Day 0: `97182.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_05_p_carry_defense

- Overall samples: `6` | mean `125202.5` | p10 `-18108.75` | cvar10 `-32897.0` | std `126454.9062`
- Profile `all`: count `6`, mean `125202.5`, p10 `-18108.75`, cvar10 `-32897.0`
- Profile `plausible`: count `6`, mean `125202.5`, p10 `-18108.75`, cvar10 `-32897.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48588.0`, p10 `-16600.0`, cvar10 `-32897.0`
- `bootstrap_path`: count `2`, mean `39653.25`, p10 `5274.25`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287366.25`, p10 `286833.25`, cvar10 `286700.0`

## Comparison

- Primary: `TradervR1_lab_r18_05_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-448.9167`
- Median delta: `1841.0`
- P10 delta: `-5175.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5175.25`, p10 delta `-7706.25`, win rate `0.0`
- `bootstrap_path`: mean delta `1921.75`, p10 delta `1871.15`, win rate `1.0`
- `original_noise`: mean delta `1906.75`, p10 delta `1840.15`, win rate `1.0`

- Profile `all`: mean delta `-448.9167`, p10 delta `-5175.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-448.9167`, p10 delta `-5175.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

