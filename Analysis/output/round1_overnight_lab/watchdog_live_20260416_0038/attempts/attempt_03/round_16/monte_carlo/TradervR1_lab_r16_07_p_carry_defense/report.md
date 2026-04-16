# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_07_p_carry_defense`
- Bots: TradervR1_lab_r16_07_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_07_p_carry_defense

- Combined total PnL: `289276.0000`
- Day -1: `96028.0000`
- Day -2: `96071.0000`
- Day 0: `97177.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_07_p_carry_defense

- Overall samples: `6` | mean `127563.0` | p10 `-12803.25` | cvar10 `-22286.0` | std `124361.325`
- Profile `all`: count `6`, mean `127563.0`, p10 `-12803.25`, cvar10 `-22286.0`
- Profile `plausible`: count `6`, mean `127563.0`, p10 `-12803.25`, cvar10 `-22286.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55540.5`, p10 `-6720.7`, cvar10 `-22286.0`
- `bootstrap_path`: count `2`, mean `39655.25`, p10 `5274.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287493.25`, p10 `286853.05`, cvar10 `286693.0`

## Comparison

- Primary: `TradervR1_lab_r16_07_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1911.5833`
- Median delta: `1986.0`
- P10 delta: `1570.5`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1777.25`, p10 delta `1381.45`, win rate `1.0`
- `bootstrap_path`: mean delta `1923.75`, p10 delta `1871.55`, win rate `1.0`
- `original_noise`: mean delta `2033.75`, p10 delta `1993.15`, win rate `1.0`

- Profile `all`: mean delta `1911.5833`, p10 delta `1570.5`, win rate `1.0`
- Profile `plausible`: mean delta `1911.5833`, p10 delta `1570.5`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

