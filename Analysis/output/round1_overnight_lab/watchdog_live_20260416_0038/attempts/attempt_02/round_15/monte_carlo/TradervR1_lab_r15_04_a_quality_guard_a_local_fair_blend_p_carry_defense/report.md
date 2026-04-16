# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense`
- Bots: TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense

- Combined total PnL: `288627.0000`
- Day -1: `96015.0000`
- Day -2: `95892.0000`
- Day 0: `96720.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense

- Overall samples: `6` | mean `126483.8333` | p10 `-16137.75` | cvar10 `-30015.0` | std `125548.1482`
- Profile `all`: count `6`, mean `126483.8333`, p10 `-16137.75`, cvar10 `-30015.0`
- Profile `plausible`: count `6`, mean `126483.8333`, p10 `-16137.75`, cvar10 `-30015.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52246.5`, p10 `-13562.7`, cvar10 `-30015.0`
- `bootstrap_path`: count `2`, mean `40215.75`, p10 `6234.75`, cvar10 `-2260.5`
- `original_noise`: count `2`, mean `286989.25`, p10 `286438.65`, cvar10 `286301.0`

## Comparison

- Primary: `TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `832.4167`
- Median delta: `1820.5`
- P10 delta: `-1994.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1516.75`, p10 delta `-4668.95`, win rate `0.5`
- `bootstrap_path`: mean delta `2484.25`, p10 delta `2136.85`, win rate `1.0`
- `original_noise`: mean delta `1529.75`, p10 delta `1480.75`, win rate `1.0`

- Profile `all`: mean delta `832.4167`, p10 delta `-1994.25`, win rate `0.8333`
- Profile `plausible`: mean delta `832.4167`, p10 delta `-1994.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

