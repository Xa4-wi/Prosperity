# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_07_p_carry_defense_a_quality_guard`
- Bots: TradervR1_lab_r07_07_p_carry_defense_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_07_p_carry_defense_a_quality_guard

- Combined total PnL: `290153.5000`
- Day -1: `96259.0000`
- Day -2: `96440.5000`
- Day 0: `97454.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_07_p_carry_defense_a_quality_guard

- Overall samples: `6` | mean `127599.5` | p10 `-14715.25` | cvar10 `-27222.0` | std `125593.5534`
- Profile `all`: count `6`, mean `127599.5`, p10 `-14715.25`, cvar10 `-27222.0`
- Profile `plausible`: count `6`, mean `127599.5`, p10 `-14715.25`, cvar10 `-27222.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53886.75`, p10 `-11000.25`, cvar10 `-27222.0`
- `bootstrap_path`: count `2`, mean `40408.25`, p10 `6314.85`, cvar10 `-2208.5`
- `original_noise`: count `2`, mean `288503.5`, p10 `287982.3`, cvar10 `287852.0`

## Comparison

- Primary: `TradervR1_lab_r07_07_p_carry_defense_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1948.0833`
- Median delta: `2928.5`
- P10 delta: `-140.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `123.5`, p10 delta `-2106.5`, win rate `0.5`
- `bootstrap_path`: mean delta `2676.75`, p10 delta `2441.75`, win rate `1.0`
- `original_noise`: mean delta `3044.0`, p10 delta `2965.6`, win rate `1.0`

- Profile `all`: mean delta `1948.0833`, p10 delta `-140.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1948.0833`, p10 delta `-140.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

