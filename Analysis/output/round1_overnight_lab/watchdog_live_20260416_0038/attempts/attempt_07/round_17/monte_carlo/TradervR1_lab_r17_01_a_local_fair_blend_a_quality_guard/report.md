# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard`
- Bots: TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard

- Combined total PnL: `289681.0000`
- Day -1: `96095.0000`
- Day -2: `96120.0000`
- Day 0: `97466.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard

- Overall samples: `6` | mean `126986.4167` | p10 `-17057.25` | cvar10 `-32418.0` | std `126222.1729`
- Profile `all`: count `6`, mean `126986.4167`, p10 `-17057.25`, cvar10 `-32418.0`
- Profile `plausible`: count `6`, mean `126986.4167`, p10 `-17057.25`, cvar10 `-32418.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52796.75`, p10 `-15375.05`, cvar10 `-32418.0`
- `bootstrap_path`: count `2`, mean `40616.75`, p10 `6766.15`, cvar10 `-1696.5`
- `original_noise`: count `2`, mean `287545.75`, p10 `286737.55`, cvar10 `286535.5`

## Comparison

- Primary: `TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1335.0`
- Median delta: `2317.5`
- P10 delta: `-3017.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-966.5`, p10 delta `-6481.3`, win rate `0.5`
- `bootstrap_path`: mean delta `2885.25`, p10 delta `2407.45`, win rate `1.0`
- `original_noise`: mean delta `2086.25`, p10 delta `1877.65`, win rate `1.0`

- Profile `all`: mean delta `1335.0`, p10 delta `-3017.25`, win rate `0.8333`
- Profile `plausible`: mean delta `1335.0`, p10 delta `-3017.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

