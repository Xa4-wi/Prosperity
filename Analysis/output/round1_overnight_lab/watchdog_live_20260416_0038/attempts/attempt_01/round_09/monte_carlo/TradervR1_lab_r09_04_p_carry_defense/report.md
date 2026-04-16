# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_04_p_carry_defense`
- Bots: TradervR1_lab_r09_04_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_04_p_carry_defense

- Combined total PnL: `288957.0000`
- Day -1: `95881.0000`
- Day -2: `95990.0000`
- Day 0: `97086.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_04_p_carry_defense

- Overall samples: `6` | mean `124734.3333` | p10 `-20326.25` | cvar10 `-37050.0` | std `127178.961`
- Profile `all`: count `6`, mean `124734.3333`, p10 `-20326.25`, cvar10 `-37050.0`
- Profile `plausible`: count `6`, mean `124734.3333`, p10 `-20326.25`, cvar10 `-37050.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48339.5`, p10 `-19972.1`, cvar10 `-37050.0`
- `bootstrap_path`: count `2`, mean `39137.75`, p10 `4945.55`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286725.75`, p10 `285847.95`, cvar10 `285628.5`

## Comparison

- Primary: `TradervR1_lab_r09_04_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-917.0833`
- Median delta: `1406.25`
- P10 delta: `-5786.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-5423.75`, p10 delta `-11078.35`, win rate `0.5`
- `bootstrap_path`: mean delta `1406.25`, p10 delta `1270.05`, win rate `1.0`
- `original_noise`: mean delta `1266.25`, p10 delta `988.05`, win rate `1.0`

- Profile `all`: mean delta `-917.0833`, p10 delta `-5786.75`, win rate `0.8333`
- Profile `plausible`: mean delta `-917.0833`, p10 delta `-5786.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

