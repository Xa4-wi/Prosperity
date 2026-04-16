# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning`
- Bots: TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning

- Combined total PnL: `289574.5000`
- Day -1: `96047.0000`
- Day -2: `96359.5000`
- Day 0: `97168.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning

- Overall samples: `6` | mean `126739.0833` | p10 `-14753.75` | cvar10 `-26877.0` | std `125190.3238`
- Profile `all`: count `6`, mean `126739.0833`, p10 `-14753.75`, cvar10 `-26877.0`
- Profile `plausible`: count `6`, mean `126739.0833`, p10 `-14753.75`, cvar10 `-26877.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52585.0`, p10 `-10984.6`, cvar10 `-26877.0`
- `bootstrap_path`: count `2`, mean `40056.25`, p10 `5906.85`, cvar10 `-2630.5`
- `original_noise`: count `2`, mean `287576.0`, p10 `287194.0`, cvar10 `287098.5`

## Comparison

- Primary: `TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1087.6667`
- Median delta: `1972.75`
- P10 delta: `-1178.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-1178.25`, p10 delta `-2090.85`, win rate `0.0`
- `bootstrap_path`: mean delta `2324.75`, p10 delta `2145.75`, win rate `1.0`
- `original_noise`: mean delta `2116.5`, p10 delta `1898.9`, win rate `1.0`

- Profile `all`: mean delta `1087.6667`, p10 delta `-1178.25`, win rate `0.6667`
- Profile `plausible`: mean delta `1087.6667`, p10 delta `-1178.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

