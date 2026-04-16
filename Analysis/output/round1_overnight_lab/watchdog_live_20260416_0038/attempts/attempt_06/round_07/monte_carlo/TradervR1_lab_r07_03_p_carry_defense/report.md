# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_03_p_carry_defense`
- Bots: TradervR1_lab_r07_03_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_03_p_carry_defense

- Combined total PnL: `289303.0000`
- Day -1: `96028.0000`
- Day -2: `96096.0000`
- Day 0: `97179.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_03_p_carry_defense

- Overall samples: `6` | mean `125839.6667` | p10 `-18330.25` | cvar10 `-33340.0` | std `126490.2841`
- Profile `all`: count `6`, mean `125839.6667`, p10 `-18330.25`, cvar10 `-33340.0`
- Profile `plausible`: count `6`, mean `125839.6667`, p10 `-18330.25`, cvar10 `-33340.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50913.25`, p10 `-16489.35`, cvar10 `-33340.0`
- `bootstrap_path`: count `2`, mean `39521.25`, p10 `5247.85`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287084.5`, p10 `286456.1`, cvar10 `286299.0`

## Comparison

- Primary: `TradervR1_lab_r07_03_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `188.25`
- Median delta: `1691.0`
- P10 delta: `-3596.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2850.0`, p10 delta `-7595.6`, win rate `0.5`
- `bootstrap_path`: mean delta `1789.75`, p10 delta `1734.75`, win rate `1.0`
- `original_noise`: mean delta `1625.0`, p10 delta `1596.2`, win rate `1.0`

- Profile `all`: mean delta `188.25`, p10 delta `-3596.5`, win rate `0.8333`
- Profile `plausible`: mean delta `188.25`, p10 delta `-3596.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

