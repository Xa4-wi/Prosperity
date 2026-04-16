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

- Overall samples: `6` | mean `125998.0` | p10 `-16297.5` | cvar10 `-29599.0` | std `125580.7619`
- Profile `all`: count `6`, mean `125998.0`, p10 `-16297.5`, cvar10 `-29599.0`
- Profile `plausible`: count `6`, mean `125998.0`, p10 `-16297.5`, cvar10 `-29599.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51300.5`, p10 `-13419.1`, cvar10 `-29599.0`
- `bootstrap_path`: count `2`, mean `39709.5`, p10 `5545.1`, cvar10 `-2996.0`
- `original_noise`: count `2`, mean `286984.0`, p10 `286114.8`, cvar10 `285897.5`

## Comparison

- Primary: `TradervR1_lab_r04_07_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `346.5833`
- Median delta: `1480.25`
- P10 delta: `-2462.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2462.75`, p10 delta `-4525.35`, win rate `0.5`
- `bootstrap_path`: mean delta `1978.0`, p10 delta `1814.0`, win rate `1.0`
- `original_noise`: mean delta `1524.5`, p10 delta `1254.9`, win rate `1.0`

- Profile `all`: mean delta `346.5833`, p10 delta `-2462.75`, win rate `0.8333`
- Profile `plausible`: mean delta `346.5833`, p10 delta `-2462.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

