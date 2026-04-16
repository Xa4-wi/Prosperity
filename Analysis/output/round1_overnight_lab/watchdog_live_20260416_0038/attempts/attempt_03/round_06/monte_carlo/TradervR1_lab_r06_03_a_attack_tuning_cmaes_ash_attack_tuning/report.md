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

- Combined total PnL: `288894.5000`
- Day -1: `95885.0000`
- Day -2: `95917.5000`
- Day 0: `97092.0000`

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

- Overall samples: `6` | mean `125755.5` | p10 `-16303.0` | cvar10 `-29363.0` | std `125678.3097`
- Profile `all`: count `6`, mean `125755.5`, p10 `-16303.0`, cvar10 `-29363.0`
- Profile `plausible`: count `6`, mean `125755.5`, p10 `-16303.0`, cvar10 `-29363.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50774.75`, p10 `-13335.45`, cvar10 `-29363.0`
- `bootstrap_path`: count `2`, mean `39313.5`, p10 `5268.3`, cvar10 `-3243.0`
- `original_noise`: count `2`, mean `287178.25`, p10 `286697.25`, cvar10 `286577.0`

## Comparison

- Primary: `TradervR1_lab_r06_03_a_attack_tuning_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `104.0833`
- Median delta: `1399.25`
- P10 delta: `-2988.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2988.5`, p10 delta `-4441.7`, win rate `0.0`
- `bootstrap_path`: mean delta `1582.0`, p10 delta `1298.8`, win rate `1.0`
- `original_noise`: mean delta `1718.75`, p10 delta `1600.15`, win rate `1.0`

- Profile `all`: mean delta `104.0833`, p10 delta `-2988.5`, win rate `0.6667`
- Profile `plausible`: mean delta `104.0833`, p10 delta `-2988.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

