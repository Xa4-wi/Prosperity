# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend_best

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

### TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend_best

- Overall samples: `6` | mean `124133.1667` | p10 `-21035.25` | cvar10 `-37646.0` | std `127464.5869`
- Profile `all`: count `6`, mean `124133.1667`, p10 `-21035.25`, cvar10 `-37646.0`
- Profile `plausible`: count `6`, mean `124133.1667`, p10 `-21035.25`, cvar10 `-37646.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `46997.0`, p10 `-20717.4`, cvar10 `-37646.0`
- `bootstrap_path`: count `2`, mean `38604.25`, p10 `4181.25`, cvar10 `-4424.5`
- `original_noise`: count `2`, mean `286798.25`, p10 `286158.85`, cvar10 `285999.0`

## Comparison

- Primary: `TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1518.25`
- Median delta: `872.75`
- P10 delta: `-6766.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-6766.25`, p10 delta `-11823.65`, win rate `0.0`
- `bootstrap_path`: mean delta `872.75`, p10 delta `778.15`, win rate `1.0`
- `original_noise`: mean delta `1338.75`, p10 delta `1298.95`, win rate `1.0`

- Profile `all`: mean delta `-1518.25`, p10 delta `-6766.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-1518.25`, p10 delta `-6766.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

