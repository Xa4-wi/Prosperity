# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_cmaes_pepper_entry_quality`
- Bots: TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best

- Combined total PnL: `291848.0000`
- Day -1: `96904.0000`
- Day -2: `97101.0000`
- Day 0: `97843.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best

- Overall samples: `6` | mean `129184.0833` | p10 `-11638.0` | cvar10 `-23586.0` | std `124849.3693`
- Profile `all`: count `6`, mean `129184.0833`, p10 `-11638.0`, cvar10 `-23586.0`
- Profile `plausible`: count `6`, mean `129184.0833`, p10 `-11638.0`, cvar10 `-23586.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `54946.25`, p10 `-7879.55`, cvar10 `-23586.0`
- `bootstrap_path`: count `2`, mean `42761.0`, p10 `8800.2`, cvar10 `310.0`
- `original_noise`: count `2`, mean `289845.0`, p10 `289247.4`, cvar10 `289098.0`

## Comparison

- Primary: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `3532.6667`
- Median delta: `4385.5`
- P10 delta: `1183.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1183.0`, p10 delta `1014.2`, win rate `1.0`
- `bootstrap_path`: mean delta `5029.5`, p10 delta `4661.9`, win rate `1.0`
- `original_noise`: mean delta `4385.5`, p10 delta `4383.5`, win rate `1.0`

- Profile `all`: mean delta `3532.6667`, p10 delta `1183.0`, win rate `1.0`
- Profile `plausible`: mean delta `3532.6667`, p10 delta `1183.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

