# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_01_a_local_fair_blend`
- Bots: TradervR1_lab_r17_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_01_a_local_fair_blend

- Combined total PnL: `288578.5000`
- Day -1: `95829.0000`
- Day -2: `95824.5000`
- Day 0: `96925.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_01_a_local_fair_blend

- Overall samples: `6` | mean `125849.5` | p10 `-13599.5` | cvar10 `-24309.0` | std `124234.144`
- Profile `all`: count `6`, mean `125849.5`, p10 `-13599.5`, cvar10 `-24309.0`
- Profile `plausible`: count `6`, mean `125849.5`, p10 `-13599.5`, cvar10 `-24309.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51413.25`, p10 `-9164.55`, cvar10 `-24309.0`
- `bootstrap_path`: count `2`, mean `39690.5`, p10 `5626.1`, cvar10 `-2890.0`
- `original_noise`: count `2`, mean `286444.75`, p10 `285910.15`, cvar10 `285776.5`

## Comparison

- Primary: `TradervR1_lab_r17_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `198.0833`
- Median delta: `985.25`
- P10 delta: `-2350.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2350.0`, p10 delta `-4429.2`, win rate `0.5`
- `bootstrap_path`: mean delta `1959.0`, p10 delta `1695.0`, win rate `1.0`
- `original_noise`: mean delta `985.25`, p10 delta `920.25`, win rate `1.0`

- Profile `all`: mean delta `198.0833`, p10 delta `-2350.0`, win rate `0.8333`
- Profile `plausible`: mean delta `198.0833`, p10 delta `-2350.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

