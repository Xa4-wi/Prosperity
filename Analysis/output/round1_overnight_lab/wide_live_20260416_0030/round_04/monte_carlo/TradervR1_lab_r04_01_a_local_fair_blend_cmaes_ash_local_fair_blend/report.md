# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend`
- Bots: TradervR1_lab_r04_01_a_local_fair_blend_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_01_a_local_fair_blend_best

- Combined total PnL: `292445.5000`
- Day -1: `97159.0000`
- Day -2: `97249.5000`
- Day 0: `98037.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_01_a_local_fair_blend_best

- Overall samples: `6` | mean `129875.0` | p10 `-12050.75` | cvar10 `-25322.0` | std `125377.7148`
- Profile `all`: count `6`, mean `129875.0`, p10 `-12050.75`, cvar10 `-25322.0`
- Profile `plausible`: count `6`, mean `129875.0`, p10 `-12050.75`, cvar10 `-25322.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55258.75`, p10 `-9205.85`, cvar10 `-25322.0`
- `bootstrap_path`: count `2`, mean `43668.75`, p10 `9710.15`, cvar10 `1220.5`
- `original_noise`: count `2`, mean `290697.5`, p10 `290065.5`, cvar10 `289907.5`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4223.5833`
- Median delta: `5238.0`
- P10 delta: `1495.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `1495.5`, p10 delta `-312.1`, win rate `0.5`
- `bootstrap_path`: mean delta `5937.25`, p10 delta `5567.45`, win rate `1.0`
- `original_noise`: mean delta `5238.0`, p10 delta `5205.6`, win rate `1.0`

- Profile `all`: mean delta `4223.5833`, p10 delta `1495.5`, win rate `0.8333`
- Profile `plausible`: mean delta `4223.5833`, p10 delta `1495.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

