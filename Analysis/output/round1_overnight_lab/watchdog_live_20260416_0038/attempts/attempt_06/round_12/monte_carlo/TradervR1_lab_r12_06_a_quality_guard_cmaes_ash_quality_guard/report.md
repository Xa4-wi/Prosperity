# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_06_a_quality_guard_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r12_06_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_06_a_quality_guard_best

- Combined total PnL: `289283.0000`
- Day -1: `96028.0000`
- Day -2: `96071.0000`
- Day 0: `97184.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_06_a_quality_guard_best

- Overall samples: `6` | mean `126661.1667` | p10 `-13781.75` | cvar10 `-24236.0` | std `124776.9847`
- Profile `all`: count `6`, mean `126661.1667`, p10 `-13781.75`, cvar10 `-24236.0`
- Profile `plausible`: count `6`, mean `126661.1667`, p10 `-13781.75`, cvar10 `-24236.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52768.75`, p10 `-8835.05`, cvar10 `-24236.0`
- `bootstrap_path`: count `2`, mean `39626.75`, p10 `5263.35`, cvar10 `-3327.5`
- `original_noise`: count `2`, mean `287588.0`, p10 `286987.2`, cvar10 `286837.0`

## Comparison

- Primary: `TradervR1_lab_r12_06_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1009.75`
- Median delta: `1895.25`
- P10 delta: `-994.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-994.5`, p10 delta `-2047.7`, win rate `0.5`
- `bootstrap_path`: mean delta `1895.25`, p10 delta `1860.25`, win rate `1.0`
- `original_noise`: mean delta `2128.5`, p10 delta `2127.3`, win rate `1.0`

- Profile `all`: mean delta `1009.75`, p10 delta `-994.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1009.75`, p10 delta `-994.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

