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

- Combined total PnL: `287081.0000`
- Day -1: `95368.0000`
- Day -2: `95530.0000`
- Day 0: `96183.0000`

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

- Overall samples: `6` | mean `123007.6667` | p10 `-20264.0` | cvar10 `-36649.0` | std `126450.6614`
- Profile `all`: count `6`, mean `123007.6667`, p10 `-20264.0`, cvar10 `-36649.0`
- Profile `plausible`: count `6`, mean `123007.6667`, p10 `-20264.0`, cvar10 `-36649.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `45298.75`, p10 `-20259.45`, cvar10 `-36649.0`
- `bootstrap_path`: count `2`, mean `38591.0`, p10 `4615.0`, cvar10 `-3879.0`
- `original_noise`: count `2`, mean `285133.25`, p10 `284503.05`, cvar10 `284345.5`

## Comparison

- Primary: `TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2643.75`
- Median delta: `-326.25`
- P10 delta: `-8464.5`
- Win rate: `0.3333`

- `bootstrap_balanced`: mean delta `-8464.5`, p10 delta `-11365.7`, win rate `0.0`
- `bootstrap_path`: mean delta `859.5`, p10 delta `507.1`, win rate `1.0`
- `original_noise`: mean delta `-326.25`, p10 delta `-356.85`, win rate `0.0`

- Profile `all`: mean delta `-2643.75`, p10 delta `-8464.5`, win rate `0.3333`
- Profile `plausible`: mean delta `-2643.75`, p10 delta `-8464.5`, win rate `0.3333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

