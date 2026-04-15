# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning`
- Bots: TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning

- Combined total PnL: `289288.0000`
- Day -1: `96020.0000`
- Day -2: `96073.0000`
- Day 0: `97195.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning

- Overall samples: `6` | mean `125996.0` | p10 `-16852.75` | cvar10 `-31715.0` | std `125806.9698`
- Profile `all`: count `6`, mean `125996.0`, p10 `-16852.75`, cvar10 `-31715.0`
- Profile `plausible`: count `6`, mean `125996.0`, p10 `-16852.75`, cvar10 `-31715.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50540.0`, p10 `-15264.0`, cvar10 `-31715.0`
- `bootstrap_path`: count `2`, mean `40496.25`, p10 `6506.85`, cvar10 `-1990.5`
- `original_noise`: count `2`, mean `286951.75`, p10 `286330.35`, cvar10 `286175.0`

## Comparison

- Primary: `TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `344.5833`
- Median delta: `1492.25`
- P10 delta: `-3223.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3223.25`, p10 delta `-6370.25`, win rate `0.5`
- `bootstrap_path`: mean delta `2764.75`, p10 delta `2425.75`, win rate `1.0`
- `original_noise`: mean delta `1492.25`, p10 delta `1470.45`, win rate `1.0`

- Profile `all`: mean delta `344.5833`, p10 delta `-3223.25`, win rate `0.8333`
- Profile `plausible`: mean delta `344.5833`, p10 delta `-3223.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

