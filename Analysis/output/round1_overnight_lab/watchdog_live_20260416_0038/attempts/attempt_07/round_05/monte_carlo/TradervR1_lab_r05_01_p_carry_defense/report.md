# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r05_01_p_carry_defense`
- Bots: TradervR1_lab_r05_01_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r05_01_p_carry_defense

- Combined total PnL: `289306.0000`
- Day -1: `96020.0000`
- Day -2: `96088.0000`
- Day 0: `97198.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r05_01_p_carry_defense

- Overall samples: `6` | mean `125479.6667` | p10 `-16541.25` | cvar10 `-29762.0` | std `125781.8254`
- Profile `all`: count `6`, mean `125479.6667`, p10 `-16541.25`, cvar10 `-29762.0`
- Profile `plausible`: count `6`, mean `125479.6667`, p10 `-16541.25`, cvar10 `-29762.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49411.5`, p10 `-13927.3`, cvar10 `-29762.0`
- `bootstrap_path`: count `2`, mean `39690.25`, p10 `5281.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287337.25`, p10 `286636.25`, cvar10 `286461.0`

## Comparison

- Primary: `TradervR1_lab_r05_01_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-171.75`
- Median delta: `1804.75`
- P10 delta: `-4351.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4351.75`, p10 delta `-5033.55`, win rate `0.0`
- `bootstrap_path`: mean delta `1958.75`, p10 delta `1878.55`, win rate `1.0`
- `original_noise`: mean delta `1877.75`, p10 delta `1776.35`, win rate `1.0`

- Profile `all`: mean delta `-171.75`, p10 delta `-4351.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-171.75`, p10 delta `-4351.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

