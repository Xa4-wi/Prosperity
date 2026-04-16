# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_01_a_quality_guard`
- Bots: TradervR1_lab_r12_01_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_01_a_quality_guard

- Combined total PnL: `287535.0000`
- Day -1: `95532.0000`
- Day -2: `95499.0000`
- Day 0: `96504.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_01_a_quality_guard

- Overall samples: `6` | mean `123179.6667` | p10 `-19489.25` | cvar10 `-34005.0` | std `126180.1017`
- Profile `all`: count `6`, mean `123179.6667`, p10 `-19489.25`, cvar10 `-34005.0`
- Profile `plausible`: count `6`, mean `123179.6667`, p10 `-19489.25`, cvar10 `-34005.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `46233.0`, p10 `-17957.4`, cvar10 `-34005.0`
- `bootstrap_path`: count `2`, mean `37957.75`, p10 `3612.75`, cvar10 `-4973.5`
- `original_noise`: count `2`, mean `285348.25`, p10 `284627.65`, cvar10 `284447.5`

## Comparison

- Primary: `TradervR1_lab_r12_01_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2471.75`
- Median delta: `-111.25`
- P10 delta: `-7530.25`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-7530.25`, p10 delta `-9063.65`, win rate `0.0`
- `bootstrap_path`: mean delta `226.25`, p10 delta `209.65`, win rate `1.0`
- `original_noise`: mean delta `-111.25`, p10 delta `-232.25`, win rate `0.5`

- Profile `all`: mean delta `-2471.75`, p10 delta `-7530.25`, win rate `0.5`
- Profile `plausible`: mean delta `-2471.75`, p10 delta `-7530.25`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

