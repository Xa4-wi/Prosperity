# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning_best

- Combined total PnL: `290905.0000`
- Day -1: `96504.0000`
- Day -2: `96784.0000`
- Day 0: `97617.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning_best

- Overall samples: `6` | mean `126726.5` | p10 `-17068.5` | cvar10 `-33108.0` | std `126584.6406`
- Profile `all`: count `6`, mean `126726.5`, p10 `-17068.5`, cvar10 `-33108.0`
- Profile `plausible`: count `6`, mean `126726.5`, p10 `-17068.5`, cvar10 `-33108.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50082.5`, p10 `-16469.9`, cvar10 `-33108.0`
- `bootstrap_path`: count `2`, mean `41498.0`, p10 `7476.4`, cvar10 `-1029.0`
- `original_noise`: count `2`, mean `288599.0`, p10 `287839.0`, cvar10 `287649.0`

## Comparison

- Primary: `TradervR1_lab_r04_08_a_quality_guard_a_attack_tuning_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1075.0833`
- Median delta: `3139.5`
- P10 delta: `-3680.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3680.75`, p10 delta `-7576.15`, win rate `0.5`
- `bootstrap_path`: mean delta `3766.5`, p10 delta `3459.7`, win rate `1.0`
- `original_noise`: mean delta `3139.5`, p10 delta `2979.1`, win rate `1.0`

- Profile `all`: mean delta `1075.0833`, p10 delta `-3680.75`, win rate `0.8333`
- Profile `plausible`: mean delta `1075.0833`, p10 delta `-3680.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

