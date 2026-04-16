# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_04_p_carry_defense_cmaes_pepper_carry_defense`
- Bots: TradervR1_lab_r18_04_p_carry_defense_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_04_p_carry_defense_best

- Combined total PnL: `289304.0000`
- Day -1: `96018.0000`
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

### TradervR1_lab_r18_04_p_carry_defense_best

- Overall samples: `6` | mean `124657.1667` | p10 `-20452.25` | cvar10 `-37584.0` | std `127309.9802`
- Profile `all`: count `6`, mean `124657.1667`, p10 `-20452.25`, cvar10 `-37584.0`
- Profile `plausible`: count `6`, mean `124657.1667`, p10 `-20452.25`, cvar10 `-37584.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47259.25`, p10 `-20615.35`, cvar10 `-37584.0`
- `bootstrap_path`: count `2`, mean `39684.25`, p10 `5280.45`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287028.0`, p10 `286415.6`, cvar10 `286262.5`

## Comparison

- Primary: `TradervR1_lab_r18_04_p_carry_defense_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-994.25`
- Median delta: `1568.5`
- P10 delta: `-6504.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-6504.0`, p10 delta `-11721.6`, win rate `0.5`
- `bootstrap_path`: mean delta `1952.75`, p10 delta `1877.35`, win rate `1.0`
- `original_noise`: mean delta `1568.5`, p10 delta `1555.7`, win rate `1.0`

- Profile `all`: mean delta `-994.25`, p10 delta `-6504.0`, win rate `0.8333`
- Profile `plausible`: mean delta `-994.25`, p10 delta `-6504.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

