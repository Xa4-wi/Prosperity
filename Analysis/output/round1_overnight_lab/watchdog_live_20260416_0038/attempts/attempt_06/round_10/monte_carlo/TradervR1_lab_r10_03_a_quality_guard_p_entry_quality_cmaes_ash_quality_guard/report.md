# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_03_a_quality_guard_p_entry_quality_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r10_03_a_quality_guard_p_entry_quality_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_03_a_quality_guard_p_entry_quality_best

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

### TradervR1_lab_r10_03_a_quality_guard_p_entry_quality_best

- Overall samples: `6` | mean `127701.6667` | p10 `-16654.25` | cvar10 `-31098.0` | std `126296.1395`
- Profile `all`: count `6`, mean `127701.6667`, p10 `-16654.25`, cvar10 `-31098.0`
- Profile `plausible`: count `6`, mean `127701.6667`, p10 `-16654.25`, cvar10 `-31098.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `54472.75`, p10 `-13983.85`, cvar10 `-31098.0`
- `bootstrap_path`: count `2`, mean `40498.25`, p10 `6331.25`, cvar10 `-2210.5`
- `original_noise`: count `2`, mean `288134.0`, p10 `287688.4`, cvar10 `287577.0`

## Comparison

- Primary: `TradervR1_lab_r10_03_a_quality_guard_p_entry_quality_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2050.25`
- Median delta: `2716.0`
- P10 delta: `-2029.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `709.5`, p10 delta `-5090.1`, win rate `0.5`
- `bootstrap_path`: mean delta `2766.75`, p10 delta `2605.35`, win rate `1.0`
- `original_noise`: mean delta `2674.5`, p10 delta `2520.5`, win rate `1.0`

- Profile `all`: mean delta `2050.25`, p10 delta `-2029.0`, win rate `0.8333`
- Profile `plausible`: mean delta `2050.25`, p10 delta `-2029.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

