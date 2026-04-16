# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning`
- Bots: TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning

- Combined total PnL: `290844.5000`
- Day -1: `96603.0000`
- Day -2: `96622.5000`
- Day 0: `97619.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning

- Overall samples: `6` | mean `128368.25` | p10 `-13876.0` | cvar10 `-27805.0` | std `125463.8819`
- Profile `all`: count `6`, mean `128368.25`, p10 `-13876.0`, cvar10 `-27805.0`
- Profile `plausible`: count `6`, mean `128368.25`, p10 `-13876.0`, cvar10 `-27805.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53660.0`, p10 `-11512.0`, cvar10 `-27805.0`
- `bootstrap_path`: count `2`, mean `42388.5`, p10 `8520.1`, cvar10 `53.0`
- `original_noise`: count `2`, mean `289056.25`, p10 `288662.05`, cvar10 `288563.5`

## Comparison

- Primary: `TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2716.8333`
- Median delta: `3596.75`
- P10 delta: `-103.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-103.25`, p10 delta `-2618.25`, win rate `0.5`
- `bootstrap_path`: mean delta `4657.0`, p10 delta `4197.0`, win rate `1.0`
- `original_noise`: mean delta `3596.75`, p10 delta `3391.35`, win rate `1.0`

- Profile `all`: mean delta `2716.8333`, p10 delta `-103.25`, win rate `0.8333`
- Profile `plausible`: mean delta `2716.8333`, p10 delta `-103.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

