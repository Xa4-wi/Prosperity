# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_08_a_quality_guard`
- Bots: TradervR1_lab_r16_08_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_08_a_quality_guard

- Combined total PnL: `289550.5000`
- Day -1: `96115.0000`
- Day -2: `96159.5000`
- Day 0: `97276.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_08_a_quality_guard

- Overall samples: `6` | mean `125664.3333` | p10 `-18380.0` | cvar10 `-34208.0` | std `126668.5896`
- Profile `all`: count `6`, mean `125664.3333`, p10 `-18380.0`, cvar10 `-34208.0`
- Profile `plausible`: count `6`, mean `125664.3333`, p10 `-18380.0`, cvar10 `-34208.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49544.75`, p10 `-17457.45`, cvar10 `-34208.0`
- `bootstrap_path`: count `2`, mean `39995.0`, p10 `5957.4`, cvar10 `-2552.0`
- `original_noise`: count `2`, mean `287453.25`, p10 `286675.45`, cvar10 `286481.0`

## Comparison

- Primary: `TradervR1_lab_r16_08_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `12.9167`
- Median delta: `1835.5`
- P10 delta: `-4218.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4218.5`, p10 delta `-8563.7`, win rate `0.5`
- `bootstrap_path`: mean delta `2263.5`, p10 delta `1972.7`, win rate `1.0`
- `original_noise`: mean delta `1993.75`, p10 delta `1815.55`, win rate `1.0`

- Profile `all`: mean delta `12.9167`, p10 delta `-4218.5`, win rate `0.8333`
- Profile `plausible`: mean delta `12.9167`, p10 delta `-4218.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

