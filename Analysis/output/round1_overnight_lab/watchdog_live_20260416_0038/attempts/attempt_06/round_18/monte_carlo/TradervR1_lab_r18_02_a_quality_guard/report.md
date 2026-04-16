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

- Combined total PnL: `290132.5000`
- Day -1: `96259.0000`
- Day -2: `96513.5000`
- Day 0: `97360.0000`

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

- Overall samples: `6` | mean `126757.4167` | p10 `-15756.25` | cvar10 `-28873.0` | std `125706.3367`
- Profile `all`: count `6`, mean `126757.4167`, p10 `-15756.25`, cvar10 `-28873.0`
- Profile `plausible`: count `6`, mean `126757.4167`, p10 `-15756.25`, cvar10 `-28873.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52188.5`, p10 `-12660.7`, cvar10 `-28873.0`
- `bootstrap_path`: count `2`, mean `40237.75`, p10 `5935.95`, cvar10 `-2639.5`
- `original_noise`: count `2`, mean `287846.0`, p10 `287000.8`, cvar10 `286789.5`

## Comparison

- Primary: `TradervR1_lab_r18_02_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1106.0`
- Median delta: `2276.25`
- P10 delta: `-1574.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1574.75`, p10 delta `-3766.95`, win rate `0.5`
- `bootstrap_path`: mean delta `2506.25`, p10 delta `2479.65`, win rate `1.0`
- `original_noise`: mean delta `2386.5`, p10 delta `2140.9`, win rate `1.0`

- Profile `all`: mean delta `1106.0`, p10 delta `-1574.75`, win rate `0.8333`
- Profile `plausible`: mean delta `1106.0`, p10 delta `-1574.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

