# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_07_a_local_fair_blend`
- Bots: TradervR1_lab_r10_07_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_07_a_local_fair_blend

- Combined total PnL: `285589.0000`
- Day -1: `94727.0000`
- Day -2: `94817.0000`
- Day 0: `96045.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_07_a_local_fair_blend

- Overall samples: `6` | mean `122233.4167` | p10 `-20889.5` | cvar10 `-35612.0` | std `126085.3248`
- Profile `all`: count `6`, mean `122233.4167`, p10 `-20889.5`, cvar10 `-35612.0`
- Profile `plausible`: count `6`, mean `122233.4167`, p10 `-20889.5`, cvar10 `-35612.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `46421.5`, p10 `-19205.3`, cvar10 `-35612.0`
- `bootstrap_path`: count `2`, mean `36630.0`, p10 `2392.4`, cvar10 `-6167.0`
- `original_noise`: count `2`, mean `283648.75`, p10 `282791.75`, cvar10 `282577.5`

## Comparison

- Primary: `TradervR1_lab_r10_07_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-3418.0`
- Median delta: `-1810.75`
- P10 delta: `-7341.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-7341.75`, p10 delta `-10311.55`, win rate `0.0`
- `bootstrap_path`: mean delta `-1101.5`, p10 delta `-1192.3`, win rate `0.0`
- `original_noise`: mean delta `-1810.75`, p10 delta `-2068.15`, win rate `0.0`

- Profile `all`: mean delta `-3418.0`, p10 delta `-7341.75`, win rate `0.0`
- Profile `plausible`: mean delta `-3418.0`, p10 delta `-7341.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

