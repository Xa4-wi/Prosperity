# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r13_07_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r13_07_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r13_07_p_entry_quality_a_quality_guard

- Combined total PnL: `287999.0000`
- Day -1: `95581.0000`
- Day -2: `95674.0000`
- Day 0: `96744.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r13_07_p_entry_quality_a_quality_guard

- Overall samples: `6` | mean `125327.4167` | p10 `-16798.5` | cvar10 `-29389.0` | std `125450.9052`
- Profile `all`: count `6`, mean `125327.4167`, p10 `-16798.5`, cvar10 `-29389.0`
- Profile `plausible`: count `6`, mean `125327.4167`, p10 `-16798.5`, cvar10 `-29389.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51232.0`, p10 `-13264.8`, cvar10 `-29389.0`
- `bootstrap_path`: count `2`, mean `38587.0`, p10 `4351.0`, cvar10 `-4208.0`
- `original_noise`: count `2`, mean `286163.25`, p10 `285635.45`, cvar10 `285503.5`

## Comparison

- Primary: `TradervR1_lab_r13_07_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-324.0`
- Median delta: `677.0`
- P10 delta: `-2531.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2531.25`, p10 delta `-4371.05`, win rate `0.0`
- `bootstrap_path`: mean delta `855.5`, p10 delta `763.1`, win rate `1.0`
- `original_noise`: mean delta `703.75`, p10 delta `631.95`, win rate `1.0`

- Profile `all`: mean delta `-324.0`, p10 delta `-2531.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-324.0`, p10 delta `-2531.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

