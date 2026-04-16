# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_01_a_local_fair_blend`
- Bots: TradervR1_lab_r04_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_01_a_local_fair_blend

- Combined total PnL: `292417.5000`
- Day -1: `97129.0000`
- Day -2: `97253.5000`
- Day 0: `98035.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_01_a_local_fair_blend

- Overall samples: `6` | mean `128660.75` | p10 `-14088.75` | cvar10 `-29398.0` | std `126035.6966`
- Profile `all`: count `6`, mean `128660.75`, p10 `-14088.75`, cvar10 `-29398.0`
- Profile `plausible`: count `6`, mean `128660.75`, p10 `-14088.75`, cvar10 `-29398.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52143.0`, p10 `-13089.8`, cvar10 `-29398.0`
- `bootstrap_path`: count `2`, mean `43575.25`, p10 `9691.45`, cvar10 `1220.5`
- `original_noise`: count `2`, mean `290264.0`, p10 `289129.2`, cvar10 `288845.5`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `3009.3333`
- Median delta: `4711.75`
- P10 delta: `-1620.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1620.25`, p10 delta `-4196.05`, win rate `0.5`
- `bootstrap_path`: mean delta `5843.75`, p10 delta `5399.15`, win rate `1.0`
- `original_noise`: mean delta `4804.5`, p10 delta `4269.3`, win rate `1.0`

- Profile `all`: mean delta `3009.3333`, p10 delta `-1620.25`, win rate `0.8333`
- Profile `plausible`: mean delta `3009.3333`, p10 delta `-1620.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

