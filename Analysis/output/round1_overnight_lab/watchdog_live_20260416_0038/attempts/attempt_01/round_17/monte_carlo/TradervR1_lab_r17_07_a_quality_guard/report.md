# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_07_a_quality_guard`
- Bots: TradervR1_lab_r17_07_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_07_a_quality_guard

- Combined total PnL: `286507.5000`
- Day -1: `95216.0000`
- Day -2: `95193.5000`
- Day 0: `96098.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_07_a_quality_guard

- Overall samples: `6` | mean `122949.0` | p10 `-19769.0` | cvar10 `-33375.0` | std `126019.0151`
- Profile `all`: count `6`, mean `122949.0`, p10 `-19769.0`, cvar10 `-33375.0`
- Profile `plausible`: count `6`, mean `122949.0`, p10 `-19769.0`, cvar10 `-33375.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `47251.5`, p10 `-17249.7`, cvar10 `-33375.0`
- `bootstrap_path`: count `2`, mean `36923.5`, p10 `2454.3`, cvar10 `-6163.0`
- `original_noise`: count `2`, mean `284672.0`, p10 `284123.2`, cvar10 `283986.0`

## Comparison

- Primary: `TradervR1_lab_r17_07_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2702.4167`
- Median delta: `-917.5`
- P10 delta: `-6511.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-6511.75`, p10 delta `-8355.95`, win rate `0.0`
- `bootstrap_path`: mean delta `-808.0`, p10 delta `-948.8`, win rate `0.0`
- `original_noise`: mean delta `-787.5`, p10 delta `-838.3`, win rate `0.0`

- Profile `all`: mean delta `-2702.4167`, p10 delta `-6511.75`, win rate `0.0`
- Profile `plausible`: mean delta `-2702.4167`, p10 delta `-6511.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

