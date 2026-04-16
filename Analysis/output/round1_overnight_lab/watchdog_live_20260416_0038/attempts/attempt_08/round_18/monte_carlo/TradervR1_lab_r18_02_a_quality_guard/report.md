# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_02_a_quality_guard`
- Bots: TradervR1_lab_r18_02_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_02_a_quality_guard

- Combined total PnL: `289359.5000`
- Day -1: `96187.0000`
- Day -2: `96071.5000`
- Day 0: `97101.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_02_a_quality_guard

- Overall samples: `6` | mean `124090.25` | p10 `-20635.0` | cvar10 `-38352.0` | std `127634.8969`
- Profile `all`: count `6`, mean `124090.25`, p10 `-20635.0`, cvar10 `-38352.0`
- Profile `plausible`: count `6`, mean `124090.25`, p10 `-20635.0`, cvar10 `-38352.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `44909.5`, p10 `-21699.7`, cvar10 `-38352.0`
- `bootstrap_path`: count `2`, mean `39758.5`, p10 `5617.3`, cvar10 `-2918.0`
- `original_noise`: count `2`, mean `287602.75`, p10 `287056.15`, cvar10 `286919.5`

## Comparison

- Primary: `TradervR1_lab_r18_02_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1561.1667`
- Median delta: `1935.0`
- P10 delta: `-8853.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-8853.75`, p10 delta `-12805.95`, win rate `0.0`
- `bootstrap_path`: mean delta `2027.0`, p10 delta `1839.8`, win rate `1.0`
- `original_noise`: mean delta `2143.25`, p10 delta `2090.25`, win rate `1.0`

- Profile `all`: mean delta `-1561.1667`, p10 delta `-8853.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-1561.1667`, p10 delta `-8853.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

