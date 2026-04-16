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

- Overall samples: `6` | mean `127914.0833` | p10 `-14478.5` | cvar10 `-29010.0` | std `125713.6793`
- Profile `all`: count `6`, mean `127914.0833`, p10 `-14478.5`, cvar10 `-29010.0`
- Profile `plausible`: count `6`, mean `127914.0833`, p10 `-14478.5`, cvar10 `-29010.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52269.75`, p10 `-12754.05`, cvar10 `-29010.0`
- `bootstrap_path`: count `2`, mean `42388.5`, p10 `8520.1`, cvar10 `53.0`
- `original_noise`: count `2`, mean `289084.0`, p10 `288432.8`, cvar10 `288270.0`

## Comparison

- Primary: `TradervR1_lab_r07_05_a_quality_guard_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2262.6667`
- Median delta: `3624.5`
- P10 delta: `-1493.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1493.5`, p10 delta `-3860.3`, win rate `0.5`
- `bootstrap_path`: mean delta `4657.0`, p10 delta `4197.0`, win rate `1.0`
- `original_noise`: mean delta `3624.5`, p10 delta `3572.9`, win rate `1.0`

- Profile `all`: mean delta `2262.6667`, p10 delta `-1493.5`, win rate `0.8333`
- Profile `plausible`: mean delta `2262.6667`, p10 delta `-1493.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

