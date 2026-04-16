# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_01_p_carry_defense`
- Bots: TradervR1_lab_r14_01_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_01_p_carry_defense

- Combined total PnL: `287283.5000`
- Day -1: `95491.0000`
- Day -2: `95517.5000`
- Day 0: `96275.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_01_p_carry_defense

- Overall samples: `6` | mean `124238.1667` | p10 `-16708.0` | cvar10 `-28237.0` | std `124971.9576`
- Profile `all`: count `6`, mean `124238.1667`, p10 `-16708.0`, cvar10 `-28237.0`
- Profile `plausible`: count `6`, mean `124238.1667`, p10 `-16708.0`, cvar10 `-28237.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49822.5`, p10 `-12625.1`, cvar10 `-28237.0`
- `bootstrap_path`: count `2`, mean `37727.5`, p10 `3402.3`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285164.5`, p10 `284521.7`, cvar10 `284361.0`

## Comparison

- Primary: `TradervR1_lab_r14_01_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1413.25`
- Median delta: `-295.0`
- P10 delta: `-3940.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-3940.75`, p10 delta `-4150.15`, win rate `0.0`
- `bootstrap_path`: mean delta `-4.0`, p10 delta `-7.2`, win rate `0.0`
- `original_noise`: mean delta `-295.0`, p10 delta `-338.2`, win rate `0.0`

- Profile `all`: mean delta `-1413.25`, p10 delta `-3940.75`, win rate `0.0`
- Profile `plausible`: mean delta `-1413.25`, p10 delta `-3940.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

