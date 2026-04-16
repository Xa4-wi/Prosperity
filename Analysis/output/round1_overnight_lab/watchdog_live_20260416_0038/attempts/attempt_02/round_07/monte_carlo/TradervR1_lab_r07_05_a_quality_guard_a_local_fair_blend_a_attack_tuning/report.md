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

- Overall samples: `6` | mean `126620.5833` | p10 `-17111.5` | cvar10 `-34276.0` | std `126638.521`
- Profile `all`: count `6`, mean `126620.5833`, p10 `-17111.5`, cvar10 `-34276.0`
- Profile `plausible`: count `6`, mean `126620.5833`, p10 `-17111.5`, cvar10 `-34276.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48782.75`, p10 `-17664.25`, cvar10 `-34276.0`
- `bootstrap_path`: count `2`, mean `42388.5`, p10 `8520.1`, cvar10 `53.0`
- `original_noise`: count `2`, mean `288690.5`, p10 `288145.3`, cvar10 `288009.0`

## Comparison

- Primary: `TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `969.1667`
- Median delta: `3231.0`
- P10 delta: `-4980.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4980.5`, p10 delta `-8770.5`, win rate `0.0`
- `bootstrap_path`: mean delta `4657.0`, p10 delta `4197.0`, win rate `1.0`
- `original_noise`: mean delta `3231.0`, p10 delta `3176.6`, win rate `1.0`

- Profile `all`: mean delta `969.1667`, p10 delta `-4980.5`, win rate `0.6667`
- Profile `plausible`: mean delta `969.1667`, p10 delta `-4980.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

