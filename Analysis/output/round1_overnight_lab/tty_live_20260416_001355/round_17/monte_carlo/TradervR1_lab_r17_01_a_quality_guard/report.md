# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_01_a_quality_guard`
- Bots: TradervR1_lab_r17_01_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_01_a_quality_guard

- Combined total PnL: `288970.0000`
- Day -1: `95897.0000`
- Day -2: `95973.0000`
- Day 0: `97100.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_01_a_quality_guard

- Overall samples: `6` | mean `125700.8333` | p10 `-16354.75` | cvar10 `-29107.0` | std `125652.2059`
- Profile `all`: count `6`, mean `125700.8333`, p10 `-16354.75`, cvar10 `-29107.0`
- Profile `plausible`: count `6`, mean `125700.8333`, p10 `-16354.75`, cvar10 `-29107.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50929.5`, p10 `-13099.7`, cvar10 `-29107.0`
- `bootstrap_path`: count `2`, mean `39090.75`, p10 `4936.15`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `287082.25`, p10 `286342.45`, cvar10 `286157.5`

## Comparison

- Primary: `TradervR1_lab_r17_01_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `49.4167`
- Median delta: `1294.75`
- P10 delta: `-2833.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2833.75`, p10 delta `-4205.95`, win rate `0.0`
- `bootstrap_path`: mean delta `1359.25`, p10 delta `1185.45`, win rate `1.0`
- `original_noise`: mean delta `1622.75`, p10 delta `1482.55`, win rate `1.0`

- Profile `all`: mean delta `49.4167`, p10 delta `-2833.75`, win rate `0.6667`
- Profile `plausible`: mean delta `49.4167`, p10 delta `-2833.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

