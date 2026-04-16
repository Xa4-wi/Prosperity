# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_01_a_local_fair_blend`
- Bots: TradervR1_lab_r15_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_01_a_local_fair_blend

- Combined total PnL: `289269.5000`
- Day -1: `96060.0000`
- Day -2: `96151.5000`
- Day 0: `97058.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_01_a_local_fair_blend

- Overall samples: `6` | mean `127331.6667` | p10 `-11970.0` | cvar10 `-20515.0` | std `123787.4372`
- Profile `all`: count `6`, mean `127331.6667`, p10 `-11970.0`, cvar10 `-20515.0`
- Profile `plausible`: count `6`, mean `127331.6667`, p10 `-11970.0`, cvar10 `-20515.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55520.75`, p10 `-5307.85`, cvar10 `-20515.0`
- `bootstrap_path`: count `2`, mean `39528.5`, p10 `5165.7`, cvar10 `-3425.0`
- `original_noise`: count `2`, mean `286945.75`, p10 `286280.75`, cvar10 `286114.5`

## Comparison

- Primary: `TradervR1_lab_r15_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1680.25`
- Median delta: `1661.0`
- P10 delta: `438.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `1757.5`, p10 delta `-70.9`, win rate `0.5`
- `bootstrap_path`: mean delta `1797.0`, p10 delta `1762.6`, win rate `1.0`
- `original_noise`: mean delta `1486.25`, p10 delta `1420.85`, win rate `1.0`

- Profile `all`: mean delta `1680.25`, p10 delta `438.25`, win rate `0.8333`
- Profile `plausible`: mean delta `1680.25`, p10 delta `438.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

