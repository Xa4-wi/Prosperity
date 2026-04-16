# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard

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

### TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard

- Overall samples: `6` | mean `121525.9167` | p10 `-25295.25` | cvar10 `-43723.0` | std `128348.5111`
- Profile `all`: count `6`, mean `121525.9167`, p10 `-25295.25`, cvar10 `-43723.0`
- Profile `plausible`: count `6`, mean `121525.9167`, p10 `-25295.25`, cvar10 `-43723.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `43410.5`, p10 `-26296.3`, cvar10 `-43723.0`
- `bootstrap_path`: count `2`, mean `36500.75`, p10 `1806.15`, cvar10 `-6867.5`
- `original_noise`: count `2`, mean `284666.5`, p10 `283941.3`, cvar10 `283760.0`

## Comparison

- Primary: `TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-4125.5`
- Median delta: `-1245.25`
- P10 delta: `-10426.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-10352.75`, p10 delta `-17402.55`, win rate `0.0`
- `bootstrap_path`: mean delta `-1230.75`, p10 delta `-1596.95`, win rate `0.0`
- `original_noise`: mean delta `-793.0`, p10 delta `-918.6`, win rate `0.0`

- Profile `all`: mean delta `-4125.5`, p10 delta `-10426.75`, win rate `0.0`
- Profile `plausible`: mean delta `-4125.5`, p10 delta `-10426.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

