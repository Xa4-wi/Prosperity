# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard_cmaes_ash_local_fair_blend`
- Bots: TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard_best

- Combined total PnL: `286790.0000`
- Day -1: `95335.0000`
- Day -2: `95350.0000`
- Day 0: `96105.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard_best

- Overall samples: `6` | mean `123626.9167` | p10 `-18576.25` | cvar10 `-30285.0` | std `125566.974`
- Profile `all`: count `6`, mean `123626.9167`, p10 `-18576.25`, cvar10 `-30285.0`
- Profile `plausible`: count `6`, mean `123626.9167`, p10 `-18576.25`, cvar10 `-30285.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49612.5`, p10 `-14305.5`, cvar10 `-30285.0`
- `bootstrap_path`: count `2`, mean `36500.75`, p10 `1806.15`, cvar10 `-6867.5`
- `original_noise`: count `2`, mean `284767.5`, p10 `283824.7`, cvar10 `283589.0`

## Comparison

- Primary: `TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2024.5`
- Median delta: `-1404.75`
- P10 delta: `-4150.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-4150.75`, p10 delta `-5411.75`, win rate `0.0`
- `bootstrap_path`: mean delta `-1230.75`, p10 delta `-1596.95`, win rate `0.0`
- `original_noise`: mean delta `-692.0`, p10 delta `-1035.2`, win rate `0.0`

- Profile `all`: mean delta `-2024.5`, p10 delta `-4150.75`, win rate `0.0`
- Profile `plausible`: mean delta `-2024.5`, p10 delta `-4150.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

