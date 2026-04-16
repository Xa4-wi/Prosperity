# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_08_p_carry_defense_a_quality_guard_cmaes_pepper_carry_defense`
- Bots: TradervR1_lab_r08_08_p_carry_defense_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_08_p_carry_defense_a_quality_guard_best

- Combined total PnL: `288095.0000`
- Day -1: `95581.0000`
- Day -2: `95775.0000`
- Day 0: `96739.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_08_p_carry_defense_a_quality_guard_best

- Overall samples: `6` | mean `125253.25` | p10 `-14649.5` | cvar10 `-24666.0` | std `124471.8367`
- Profile `all`: count `6`, mean `125253.25`, p10 `-14649.5`, cvar10 `-24666.0`
- Profile `plausible`: count `6`, mean `125253.25`, p10 `-14649.5`, cvar10 `-24666.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51530.0`, p10 `-9426.8`, cvar10 `-24666.0`
- `bootstrap_path`: count `2`, mean `38258.0`, p10 `3945.2`, cvar10 `-4633.0`
- `original_noise`: count `2`, mean `285971.75`, p10 `285395.55`, cvar10 `285251.5`

## Comparison

- Primary: `TradervR1_lab_r08_08_p_carry_defense_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-398.1667`
- Median delta: `495.0`
- P10 delta: `-2233.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2233.25`, p10 delta `-3933.45`, win rate `0.0`
- `bootstrap_path`: mean delta `526.5`, p10 delta `510.9`, win rate `1.0`
- `original_noise`: mean delta `512.25`, p10 delta `488.85`, win rate `1.0`

- Profile `all`: mean delta `-398.1667`, p10 delta `-2233.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-398.1667`, p10 delta `-2233.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

