# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_03_a_attack_tuning_cmaes_ash_attack_tuning`
- Bots: TradervR1_lab_r06_03_a_attack_tuning_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_03_a_attack_tuning_best

- Combined total PnL: `288842.0000`
- Day -1: `95934.0000`
- Day -2: `95935.0000`
- Day 0: `96973.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_03_a_attack_tuning_best

- Overall samples: `6` | mean `124840.5` | p10 `-17639.25` | cvar10 `-31640.0` | std `126020.615`
- Profile `all`: count `6`, mean `124840.5`, p10 `-17639.25`, cvar10 `-31640.0`
- Profile `plausible`: count `6`, mean `124840.5`, p10 `-17639.25`, cvar10 `-31640.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48666.0`, p10 `-15578.8`, cvar10 `-31640.0`
- `bootstrap_path`: count `2`, mean `39106.75`, p10 `4910.55`, cvar10 `-3638.5`
- `original_noise`: count `2`, mean `286748.75`, p10 `286337.35`, cvar10 `286234.5`

## Comparison

- Primary: `TradervR1_lab_r06_03_a_attack_tuning_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-810.9167`
- Median delta: `1132.0`
- P10 delta: `-5097.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5097.25`, p10 delta `-6685.05`, win rate `0.0`
- `bootstrap_path`: mean delta `1375.25`, p10 delta `1243.05`, win rate `1.0`
- `original_noise`: mean delta `1289.25`, p10 delta `1101.05`, win rate `1.0`

- Profile `all`: mean delta `-810.9167`, p10 delta `-5097.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-810.9167`, p10 delta `-5097.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

