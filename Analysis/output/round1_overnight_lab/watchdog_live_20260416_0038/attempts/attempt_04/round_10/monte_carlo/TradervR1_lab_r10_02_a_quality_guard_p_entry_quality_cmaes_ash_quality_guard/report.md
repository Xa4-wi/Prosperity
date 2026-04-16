# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_02_a_quality_guard_p_entry_quality_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r10_02_a_quality_guard_p_entry_quality_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_02_a_quality_guard_p_entry_quality_best

- Combined total PnL: `290107.5000`
- Day -1: `96227.0000`
- Day -2: `96424.5000`
- Day 0: `97456.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_02_a_quality_guard_p_entry_quality_best

- Overall samples: `6` | mean `128040.4167` | p10 `-11981.25` | cvar10 `-21752.0` | std `124318.8424`
- Profile `all`: count `6`, mean `128040.4167`, p10 `-11981.25`, cvar10 `-21752.0`
- Profile `plausible`: count `6`, mean `128040.4167`, p10 `-11981.25`, cvar10 `-21752.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55433.75`, p10 `-6314.85`, cvar10 `-21752.0`
- `bootstrap_path`: count `2`, mean `40498.25`, p10 `6331.25`, cvar10 `-2210.5`
- `original_noise`: count `2`, mean `288189.25`, p10 `287456.65`, cvar10 `287273.5`

## Comparison

- Primary: `TradervR1_lab_r10_02_a_quality_guard_p_entry_quality_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2389.0`
- Median delta: `2685.5`
- P10 delta: `1549.25`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1670.5`, p10 delta `762.1`, win rate `1.0`
- `bootstrap_path`: mean delta `2766.75`, p10 delta `2605.35`, win rate `1.0`
- `original_noise`: mean delta `2729.75`, p10 delta `2596.75`, win rate `1.0`

- Profile `all`: mean delta `2389.0`, p10 delta `1549.25`, win rate `1.0`
- Profile `plausible`: mean delta `2389.0`, p10 delta `1549.25`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

