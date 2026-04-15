# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_03_a_quality_guard_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r06_03_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_03_a_quality_guard_best

- Combined total PnL: `290148.5000`
- Day -1: `96242.0000`
- Day -2: `96459.5000`
- Day 0: `97447.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_03_a_quality_guard_best

- Overall samples: `6` | mean `126438.6667` | p10 `-16387.75` | cvar10 `-30567.0` | std `126074.5939`
- Profile `all`: count `6`, mean `126438.6667`, p10 `-16387.75`, cvar10 `-30567.0`
- Profile `plausible`: count `6`, mean `126438.6667`, p10 `-16387.75`, cvar10 `-30567.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50750.75`, p10 `-14303.45`, cvar10 `-30567.0`
- `bootstrap_path`: count `2`, mean `40475.75`, p10 `6328.35`, cvar10 `-2208.5`
- `original_noise`: count `2`, mean `288089.5`, p10 `287463.5`, cvar10 `287307.0`

## Comparison

- Primary: `TradervR1_lab_r06_03_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `787.25`
- Median delta: `2557.5`
- P10 delta: `-3012.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-3012.5`, p10 delta `-5409.7`, win rate `0.0`
- `bootstrap_path`: mean delta `2744.25`, p10 delta `2563.25`, win rate `1.0`
- `original_noise`: mean delta `2630.0`, p10 delta `2603.6`, win rate `1.0`

- Profile `all`: mean delta `787.25`, p10 delta `-3012.5`, win rate `0.6667`
- Profile `plausible`: mean delta `787.25`, p10 delta `-3012.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

