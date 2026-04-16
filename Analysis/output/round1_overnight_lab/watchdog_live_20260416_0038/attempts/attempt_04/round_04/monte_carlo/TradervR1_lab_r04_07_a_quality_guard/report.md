# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_07_a_quality_guard`
- Bots: TradervR1_lab_r04_07_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_07_a_quality_guard

- Combined total PnL: `289278.5000`
- Day -1: `96082.0000`
- Day -2: `95999.5000`
- Day 0: `97197.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_07_a_quality_guard

- Overall samples: `6` | mean `126227.6667` | p10 `-15103.5` | cvar10 `-27211.0` | std `125024.4644`
- Profile `all`: count `6`, mean `126227.6667`, p10 `-15103.5`, cvar10 `-27211.0`
- Profile `plausible`: count `6`, mean `126227.6667`, p10 `-15103.5`, cvar10 `-27211.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52129.0`, p10 `-11343.0`, cvar10 `-27211.0`
- `bootstrap_path`: count `2`, mean `39709.5`, p10 `5545.1`, cvar10 `-2996.0`
- `original_noise`: count `2`, mean `286844.5`, p10 `286051.7`, cvar10 `285853.5`

## Comparison

- Primary: `TradervR1_lab_r04_07_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `576.25`
- Median delta: `1385.0`
- P10 delta: `-1634.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-1634.25`, p10 delta `-2449.25`, win rate `0.0`
- `bootstrap_path`: mean delta `1978.0`, p10 delta `1814.0`, win rate `1.0`
- `original_noise`: mean delta `1385.0`, p10 delta `1191.8`, win rate `1.0`

- Profile `all`: mean delta `576.25`, p10 delta `-1634.25`, win rate `0.6667`
- Profile `plausible`: mean delta `576.25`, p10 delta `-1634.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

