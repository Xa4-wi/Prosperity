# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r08_07_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard

- Combined total PnL: `290663.5000`
- Day -1: `96374.0000`
- Day -2: `96669.5000`
- Day 0: `97620.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard

- Overall samples: `6` | mean `129972.1667` | p10 `-11687.75` | cvar10 `-21687.0` | std `124534.4688`
- Profile `all`: count `6`, mean `129972.1667`, p10 `-11687.75`, cvar10 `-21687.0`
- Profile `plausible`: count `6`, mean `129972.1667`, p10 `-11687.75`, cvar10 `-21687.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `59988.25`, p10 `-5351.95`, cvar10 `-21687.0`
- `bootstrap_path`: count `2`, mean `41118.25`, p10 `6872.85`, cvar10 `-1688.5`
- `original_noise`: count `2`, mean `288810.0`, p10 `288004.8`, cvar10 `287803.5`

## Comparison

- Primary: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4320.75`
- Median delta: `3386.75`
- P10 delta: `2982.25`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `6225.0`, p10 delta `3541.8`, win rate `1.0`
- `bootstrap_path`: mean delta `3386.75`, p10 delta `3303.75`, win rate `1.0`
- `original_noise`: mean delta `3350.5`, p10 delta `3144.9`, win rate `1.0`

- Profile `all`: mean delta `4320.75`, p10 delta `2982.25`, win rate `1.0`
- Profile `plausible`: mean delta `4320.75`, p10 delta `2982.25`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

