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

- Overall samples: `6` | mean `121796.5` | p10 `-21036.5` | cvar10 `-35906.0` | std `126093.5461`
- Profile `all`: count `6`, mean `121796.5`, p10 `-21036.5`, cvar10 `-35906.0`
- Profile `plausible`: count `6`, mean `121796.5`, p10 `-21036.5`, cvar10 `-35906.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `45197.25`, p10 `-19685.35`, cvar10 `-35906.0`
- `bootstrap_path`: count `2`, mean `36630.0`, p10 `2392.4`, cvar10 `-6167.0`
- `original_noise`: count `2`, mean `283562.25`, p10 `283001.65`, cvar10 `282861.5`

## Comparison

- Primary: `TradervR1_lab_r10_07_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-3854.9167`
- Median delta: `-1897.25`
- P10 delta: `-8566.0`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-8566.0`, p10 delta `-10791.6`, win rate `0.0`
- `bootstrap_path`: mean delta `-1101.5`, p10 delta `-1192.3`, win rate `0.0`
- `original_noise`: mean delta `-1897.25`, p10 delta `-1936.25`, win rate `0.0`

- Profile `all`: mean delta `-3854.9167`, p10 delta `-8566.0`, win rate `0.0`
- Profile `plausible`: mean delta `-3854.9167`, p10 delta `-8566.0`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

