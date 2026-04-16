# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_01_a_quality_guard_p_carry_defense`
- Bots: TradervR1_lab_r09_01_a_quality_guard_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_01_a_quality_guard_p_carry_defense

- Combined total PnL: `288154.0000`
- Day -1: `95843.0000`
- Day -2: `95846.0000`
- Day 0: `96465.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_01_a_quality_guard_p_carry_defense

- Overall samples: `6` | mean `124317.75` | p10 `-19574.0` | cvar10 `-35170.0` | std `126712.0572`
- Profile `all`: count `6`, mean `124317.75`, p10 `-19574.0`, cvar10 `-35170.0`
- Profile `plausible`: count `6`, mean `124317.75`, p10 `-19574.0`, cvar10 `-35170.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47901.75`, p10 `-18555.65`, cvar10 `-35170.0`
- `bootstrap_path`: count `2`, mean `38651.0`, p10 `4547.8`, cvar10 `-3978.0`
- `original_noise`: count `2`, mean `286400.5`, p10 `285743.7`, cvar10 `285579.5`

## Comparison

- Primary: `TradervR1_lab_r09_01_a_quality_guard_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1333.6667`
- Median delta: `753.75`
- P10 delta: `-5861.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5861.5`, p10 delta `-9661.9`, win rate `0.0`
- `bootstrap_path`: mean delta `919.5`, p10 delta `694.3`, win rate `1.0`
- `original_noise`: mean delta `941.0`, p10 delta `883.8`, win rate `1.0`

- Profile `all`: mean delta `-1333.6667`, p10 delta `-5861.5`, win rate `0.6667`
- Profile `plausible`: mean delta `-1333.6667`, p10 delta `-5861.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

