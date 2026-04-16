# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r05_03_a_local_fair_blend`
- Bots: TradervR1_lab_r05_03_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r05_03_a_local_fair_blend

- Combined total PnL: `291478.0000`
- Day -1: `96892.0000`
- Day -2: `96966.0000`
- Day 0: `97620.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r05_03_a_local_fair_blend

- Overall samples: `6` | mean `128200.9167` | p10 `-14717.0` | cvar10 `-29263.0` | std `125935.13`
- Profile `all`: count `6`, mean `128200.9167`, p10 `-14717.0`, cvar10 `-29263.0`
- Profile `plausible`: count `6`, mean `128200.9167`, p10 `-14717.0`, cvar10 `-29263.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52826.75`, p10 `-12845.05`, cvar10 `-29263.0`
- `bootstrap_path`: count `2`, mean `42382.5`, p10 `8339.7`, cvar10 `-171.0`
- `original_noise`: count `2`, mean `289393.5`, p10 `288934.7`, cvar10 `288820.0`

## Comparison

- Primary: `TradervR1_lab_r05_03_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2549.5`
- Median delta: `3934.0`
- P10 delta: `-936.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-936.5`, p10 delta `-3951.3`, win rate `0.5`
- `bootstrap_path`: mean delta `4651.0`, p10 delta `4365.4`, win rate `1.0`
- `original_noise`: mean delta `3934.0`, p10 delta `3793.2`, win rate `1.0`

- Profile `all`: mean delta `2549.5`, p10 delta `-936.5`, win rate `0.8333`
- Profile `plausible`: mean delta `2549.5`, p10 delta `-936.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

