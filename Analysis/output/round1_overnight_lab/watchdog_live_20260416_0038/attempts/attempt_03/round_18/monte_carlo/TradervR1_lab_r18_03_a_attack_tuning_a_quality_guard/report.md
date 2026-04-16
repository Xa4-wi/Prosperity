# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_03_a_attack_tuning_a_quality_guard`
- Bots: TradervR1_lab_r18_03_a_attack_tuning_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_03_a_attack_tuning_a_quality_guard

- Combined total PnL: `289194.5000`
- Day -1: `96149.0000`
- Day -2: `96197.5000`
- Day 0: `96848.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_03_a_attack_tuning_a_quality_guard

- Overall samples: `6` | mean `124995.0833` | p10 `-20637.75` | cvar10 `-38127.0` | std `127507.935`
- Profile `all`: count `6`, mean `124995.0833`, p10 `-20637.75`, cvar10 `-38127.0`
- Profile `plausible`: count `6`, mean `124995.0833`, p10 `-20637.75`, cvar10 `-38127.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47997.25`, p10 `-20902.15`, cvar10 `-38127.0`
- `bootstrap_path`: count `2`, mean `39753.75`, p10 `5431.95`, cvar10 `-3148.5`
- `original_noise`: count `2`, mean `287234.25`, p10 `286650.45`, cvar10 `286504.5`

## Comparison

- Primary: `TradervR1_lab_r18_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-656.3333`
- Median delta: `1904.25`
- P10 delta: `-5907.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-5766.0`, p10 delta `-12008.4`, win rate `0.5`
- `bootstrap_path`: mean delta `2022.25`, p10 delta `2015.65`, win rate `1.0`
- `original_noise`: mean delta `1774.75`, p10 delta `1758.95`, win rate `1.0`

- Profile `all`: mean delta `-656.3333`, p10 delta `-5907.0`, win rate `0.8333`
- Profile `plausible`: mean delta `-656.3333`, p10 delta `-5907.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

