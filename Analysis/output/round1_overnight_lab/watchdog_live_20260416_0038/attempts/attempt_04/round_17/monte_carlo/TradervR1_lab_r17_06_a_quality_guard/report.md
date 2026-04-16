# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_06_a_quality_guard`
- Bots: TradervR1_lab_r17_06_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_06_a_quality_guard

- Combined total PnL: `287401.0000`
- Day -1: `95281.0000`
- Day -2: `95479.0000`
- Day 0: `96641.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_06_a_quality_guard

- Overall samples: `6` | mean `123572.6667` | p10 `-17903.25` | cvar10 `-31134.0` | std `125577.8881`
- Profile `all`: count `6`, mean `123572.6667`, p10 `-17903.25`, cvar10 `-31134.0`
- Profile `plausible`: count `6`, mean `123572.6667`, p10 `-17903.25`, cvar10 `-31134.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47147.0`, p10 `-15477.8`, cvar10 `-31134.0`
- `bootstrap_path`: count `2`, mean `38114.75`, p10 `3884.95`, cvar10 `-4672.5`
- `original_noise`: count `2`, mean `285456.25`, p10 `284878.45`, cvar10 `284734.0`

## Comparison

- Primary: `TradervR1_lab_r17_06_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2078.75`
- Median delta: `-3.25`
- P10 delta: `-6616.25`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-6616.25`, p10 delta `-6648.45`, win rate `0.0`
- `bootstrap_path`: mean delta `383.25`, p10 delta `284.65`, win rate `1.0`
- `original_noise`: mean delta `-3.25`, p10 delta `-25.05`, win rate `0.5`

- Profile `all`: mean delta `-2078.75`, p10 delta `-6616.25`, win rate `0.5`
- Profile `plausible`: mean delta `-2078.75`, p10 delta `-6616.25`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

