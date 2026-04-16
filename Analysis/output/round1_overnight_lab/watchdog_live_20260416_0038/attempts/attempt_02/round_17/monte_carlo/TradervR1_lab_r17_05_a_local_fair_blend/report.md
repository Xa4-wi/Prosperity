# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_05_a_local_fair_blend`
- Bots: TradervR1_lab_r17_05_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_05_a_local_fair_blend

- Combined total PnL: `290027.5000`
- Day -1: `96207.0000`
- Day -2: `96442.5000`
- Day 0: `97378.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_05_a_local_fair_blend

- Overall samples: `6` | mean `127837.9167` | p10 `-10023.25` | cvar10 `-17899.0` | std `123456.7325`
- Profile `all`: count `6`, mean `127837.9167`, p10 `-10023.25`, cvar10 `-17899.0`
- Profile `plausible`: count `6`, mean `127837.9167`, p10 `-10023.25`, cvar10 `-17899.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55109.25`, p10 `-3297.35`, cvar10 `-17899.0`
- `bootstrap_path`: count `2`, mean `40411.75`, p10 `6364.35`, cvar10 `-2147.5`
- `original_noise`: count `2`, mean `287992.75`, p10 `287261.35`, cvar10 `287078.5`

## Comparison

- Primary: `TradervR1_lab_r17_05_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2186.5`
- Median delta: `2533.25`
- P10 delta: `-819.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `1346.0`, p10 delta `-2904.4`, win rate `0.5`
- `bootstrap_path`: mean delta `2680.25`, p10 delta `2399.25`, win rate `1.0`
- `original_noise`: mean delta `2533.25`, p10 delta `2401.45`, win rate `1.0`

- Profile `all`: mean delta `2186.5`, p10 delta `-819.0`, win rate `0.8333`
- Profile `plausible`: mean delta `2186.5`, p10 delta `-819.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

