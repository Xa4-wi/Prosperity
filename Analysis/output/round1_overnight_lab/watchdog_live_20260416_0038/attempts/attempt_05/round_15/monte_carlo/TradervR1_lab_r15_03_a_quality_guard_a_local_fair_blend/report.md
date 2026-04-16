# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_03_a_quality_guard_a_local_fair_blend`
- Bots: TradervR1_lab_r15_03_a_quality_guard_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_03_a_quality_guard_a_local_fair_blend

- Combined total PnL: `289715.5000`
- Day -1: `96527.0000`
- Day -2: `96074.5000`
- Day 0: `97114.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_03_a_quality_guard_a_local_fair_blend

- Overall samples: `6` | mean `125371.5` | p10 `-18417.25` | cvar10 `-32938.0` | std `126629.4005`
- Profile `all`: count `6`, mean `125371.5`, p10 `-18417.25`, cvar10 `-32938.0`
- Profile `plausible`: count `6`, mean `125371.5`, p10 `-18417.25`, cvar10 `-32938.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49160.75`, p10 `-16518.25`, cvar10 `-32938.0`
- `bootstrap_path`: count `2`, mean `39430.25`, p10 `4768.85`, cvar10 `-3896.5`
- `original_noise`: count `2`, mean `287523.5`, p10 `287046.7`, cvar10 `286927.5`

## Comparison

- Primary: `TradervR1_lab_r15_03_a_quality_guard_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-279.9167`
- Median delta: `1596.5`
- P10 delta: `-4602.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4602.5`, p10 delta `-7624.5`, win rate `0.0`
- `bootstrap_path`: mean delta `1698.75`, p10 delta `1365.75`, win rate `1.0`
- `original_noise`: mean delta `2064.0`, p10 delta `1941.2`, win rate `1.0`

- Profile `all`: mean delta `-279.9167`, p10 delta `-4602.5`, win rate `0.6667`
- Profile `plausible`: mean delta `-279.9167`, p10 delta `-4602.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

