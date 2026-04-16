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

- Combined total PnL: `292417.5000`
- Day -1: `97129.0000`
- Day -2: `97253.5000`
- Day 0: `98035.0000`

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

- Overall samples: `6` | mean `129032.1667` | p10 `-14496.75` | cvar10 `-30214.0` | std `126132.9661`
- Profile `all`: count `6`, mean `129032.1667`, p10 `-14496.75`, cvar10 `-30214.0`
- Profile `plausible`: count `6`, mean `129032.1667`, p10 `-14496.75`, cvar10 `-30214.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53500.0`, p10 `-13471.2`, cvar10 `-30214.0`
- `bootstrap_path`: count `2`, mean `43575.25`, p10 `9691.45`, cvar10 `1220.5`
- `original_noise`: count `2`, mean `290021.25`, p10 `289167.45`, cvar10 `288954.0`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `3380.75`
- Median delta: `5004.5`
- P10 delta: `-706.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-263.25`, p10 delta `-4577.45`, win rate `0.5`
- `bootstrap_path`: mean delta `5843.75`, p10 delta `5399.15`, win rate `1.0`
- `original_noise`: mean delta `4561.75`, p10 delta `4307.55`, win rate `1.0`

- Profile `all`: mean delta `3380.75`, p10 delta `-706.0`, win rate `0.8333`
- Profile `plausible`: mean delta `3380.75`, p10 delta `-706.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

