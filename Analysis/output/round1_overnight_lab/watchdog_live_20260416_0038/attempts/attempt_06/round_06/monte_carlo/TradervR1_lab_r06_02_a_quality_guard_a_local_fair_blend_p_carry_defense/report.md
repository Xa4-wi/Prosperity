# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense`
- Bots: TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense

- Combined total PnL: `288094.0000`
- Day -1: `95654.0000`
- Day -2: `95703.0000`
- Day 0: `96737.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense

- Overall samples: `6` | mean `123872.75` | p10 `-20553.75` | cvar10 `-35537.0` | std `126966.0167`
- Profile `all`: count `6`, mean `123872.75`, p10 `-20553.75`, cvar10 `-35537.0`
- Profile `plausible`: count `6`, mean `123872.75`, p10 `-20553.75`, cvar10 `-35537.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47823.75`, p10 `-18864.85`, cvar10 `-35537.0`
- `bootstrap_path`: count `2`, mean `37665.75`, p10 `3076.75`, cvar10 `-5570.5`
- `original_noise`: count `2`, mean `286128.75`, p10 `285502.15`, cvar10 `285345.5`

## Comparison

- Primary: `TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1778.6667`
- Median delta: `-65.75`
- P10 delta: `-5939.5`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-5939.5`, p10 delta `-9971.1`, win rate `0.0`
- `bootstrap_path`: mean delta `-65.75`, p10 delta `-326.35`, win rate `0.5`
- `original_noise`: mean delta `669.25`, p10 delta `642.25`, win rate `1.0`

- Profile `all`: mean delta `-1778.6667`, p10 delta `-5939.5`, win rate `0.5`
- Profile `plausible`: mean delta `-1778.6667`, p10 delta `-5939.5`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

