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

- Combined total PnL: `288806.0000`
- Day -1: `95894.0000`
- Day -2: `95830.0000`
- Day 0: `97082.0000`

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

- Overall samples: `6` | mean `126105.5` | p10 `-18470.5` | cvar10 `-34005.0` | std `126521.5647`
- Profile `all`: count `6`, mean `126105.5`, p10 `-18470.5`, cvar10 `-34005.0`
- Profile `plausible`: count `6`, mean `126105.5`, p10 `-18470.5`, cvar10 `-34005.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51859.75`, p10 `-16832.05`, cvar10 `-34005.0`
- `bootstrap_path`: count `2`, mean `39590.5`, p10 `5569.3`, cvar10 `-2936.0`
- `original_noise`: count `2`, mean `286866.25`, p10 `286264.85`, cvar10 `286114.5`

## Comparison

- Primary: `TradervR1_lab_r04_07_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `454.0833`
- Median delta: `1442.0`
- P10 delta: `-4021.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1903.5`, p10 delta `-7938.3`, win rate `0.5`
- `bootstrap_path`: mean delta `1859.0`, p10 delta `1551.8`, win rate `1.0`
- `original_noise`: mean delta `1406.75`, p10 delta `1404.95`, win rate `1.0`

- Profile `all`: mean delta `454.0833`, p10 delta `-4021.25`, win rate `0.8333`
- Profile `plausible`: mean delta `454.0833`, p10 delta `-4021.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

