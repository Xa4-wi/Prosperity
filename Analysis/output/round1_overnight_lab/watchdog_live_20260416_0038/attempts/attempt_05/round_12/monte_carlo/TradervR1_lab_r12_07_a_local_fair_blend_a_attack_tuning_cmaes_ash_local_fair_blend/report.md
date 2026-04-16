# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend`
- Bots: TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_best

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

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_best

- Overall samples: `6` | mean `125758.1667` | p10 `-17701.75` | cvar10 `-32773.0` | std `126293.262`
- Profile `all`: count `6`, mean `125758.1667`, p10 `-17701.75`, cvar10 `-32773.0`
- Profile `plausible`: count `6`, mean `125758.1667`, p10 `-17701.75`, cvar10 `-32773.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49927.5`, p10 `-16232.9`, cvar10 `-32773.0`
- `bootstrap_path`: count `2`, mean `40056.25`, p10 `5906.85`, cvar10 `-2630.5`
- `original_noise`: count `2`, mean `287290.75`, p10 `286698.15`, cvar10 `286550.0`

## Comparison

- Primary: `TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `106.75`
- Median delta: `1831.25`
- P10 delta: `-3835.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3835.75`, p10 delta `-7339.15`, win rate `0.5`
- `bootstrap_path`: mean delta `2324.75`, p10 delta `2145.75`, win rate `1.0`
- `original_noise`: mean delta `1831.25`, p10 delta `1824.25`, win rate `1.0`

- Profile `all`: mean delta `106.75`, p10 delta `-3835.75`, win rate `0.8333`
- Profile `plausible`: mean delta `106.75`, p10 delta `-3835.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

