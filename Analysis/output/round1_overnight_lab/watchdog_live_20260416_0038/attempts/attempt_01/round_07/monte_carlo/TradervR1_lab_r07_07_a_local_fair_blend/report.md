# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_07_a_local_fair_blend`
- Bots: TradervR1_lab_r07_07_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_07_a_local_fair_blend

- Combined total PnL: `289804.0000`
- Day -1: `96274.0000`
- Day -2: `96280.0000`
- Day 0: `97250.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_07_a_local_fair_blend

- Overall samples: `6` | mean `127572.9167` | p10 `-12021.5` | cvar10 `-21259.0` | std `124049.5766`
- Profile `all`: count `6`, mean `127572.9167`, p10 `-12021.5`, cvar10 `-21259.0`
- Profile `plausible`: count `6`, mean `127572.9167`, p10 `-12021.5`, cvar10 `-21259.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `54824.5`, p10 `-6042.3`, cvar10 `-21259.0`
- `bootstrap_path`: count `2`, mean `40292.5`, p10 `5831.3`, cvar10 `-2784.0`
- `original_noise`: count `2`, mean `287601.75`, p10 `286733.55`, cvar10 `286516.5`

## Comparison

- Primary: `TradervR1_lab_r07_07_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1921.5`
- Median delta: `2436.5`
- P10 delta: `315.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `1061.25`, p10 delta `-728.95`, win rate `0.5`
- `bootstrap_path`: mean delta `2561.0`, p10 delta `2428.2`, win rate `1.0`
- `original_noise`: mean delta `2142.25`, p10 delta `1873.65`, win rate `1.0`

- Profile `all`: mean delta `1921.5`, p10 delta `315.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1921.5`, p10 delta `315.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

