# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend`
- Bots: TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend

- Combined total PnL: `288703.0000`
- Day -1: `96108.0000`
- Day -2: `95867.0000`
- Day 0: `96728.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend

- Overall samples: `6` | mean `124564.5833` | p10 `-18697.25` | cvar10 `-32970.0` | std `126483.6824`
- Profile `all`: count `6`, mean `124564.5833`, p10 `-18697.25`, cvar10 `-32970.0`
- Profile `plausible`: count `6`, mean `124564.5833`, p10 `-18697.25`, cvar10 `-32970.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48250.75`, p10 `-16725.85`, cvar10 `-32970.0`
- `bootstrap_path`: count `2`, mean `38604.25`, p10 `4181.25`, cvar10 `-4424.5`
- `original_noise`: count `2`, mean `286838.75`, p10 `286483.75`, cvar10 `286395.0`

## Comparison

- Primary: `TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1086.8333`
- Median delta: `872.75`
- P10 delta: `-5512.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5512.5`, p10 delta `-7832.1`, win rate `0.0`
- `bootstrap_path`: mean delta `872.75`, p10 delta `778.15`, win rate `1.0`
- `original_noise`: mean delta `1379.25`, p10 delta `1134.65`, win rate `1.0`

- Profile `all`: mean delta `-1086.8333`, p10 delta `-5512.5`, win rate `0.6667`
- Profile `plausible`: mean delta `-1086.8333`, p10 delta `-5512.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

