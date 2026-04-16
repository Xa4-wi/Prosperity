# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning`
- Bots: TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning

- Combined total PnL: `289881.0000`
- Day -1: `96274.0000`
- Day -2: `96340.0000`
- Day 0: `97267.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning

- Overall samples: `6` | mean `128130.9167` | p10 `-11469.25` | cvar10 `-20486.0` | std `123971.8632`
- Profile `all`: count `6`, mean `128130.9167`, p10 `-11469.25`, cvar10 `-20486.0`
- Profile `plausible`: count `6`, mean `128130.9167`, p10 `-11469.25`, cvar10 `-20486.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56298.5`, p10 `-5129.1`, cvar10 `-20486.0`
- `bootstrap_path`: count `2`, mean `40260.75`, p10 `6090.15`, cvar10 `-2452.5`
- `original_noise`: count `2`, mean `287833.5`, p10 `287113.5`, cvar10 `286933.5`

## Comparison

- Primary: `TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2479.5`
- Median delta: `2428.25`
- P10 delta: `1611.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `2535.25`, p10 delta `1305.85`, win rate `1.0`
- `bootstrap_path`: mean delta `2529.25`, p10 delta `2371.45`, win rate `1.0`
- `original_noise`: mean delta `2374.0`, p10 delta `2253.6`, win rate `1.0`

- Profile `all`: mean delta `2479.5`, p10 delta `1611.0`, win rate `1.0`
- Profile `plausible`: mean delta `2479.5`, p10 delta `1611.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

