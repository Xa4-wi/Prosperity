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

- Combined total PnL: `289688.5000`
- Day -1: `96150.0000`
- Day -2: `96329.5000`
- Day 0: `97209.0000`

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

- Overall samples: `6` | mean `126695.25` | p10 `-15555.5` | cvar10 `-28445.0` | std `125602.6475`
- Profile `all`: count `6`, mean `126695.25`, p10 `-15555.5`, cvar10 `-28445.0`
- Profile `plausible`: count `6`, mean `126695.25`, p10 `-15555.5`, cvar10 `-28445.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52055.25`, p10 `-12344.95`, cvar10 `-28445.0`
- `bootstrap_path`: count `2`, mean `40218.5`, p10 `5910.9`, cvar10 `-2666.0`
- `original_noise`: count `2`, mean `287812.0`, p10 `287124.0`, cvar10 `286952.0`

## Comparison

- Primary: `TradervR1_lab_r07_07_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1043.8333`
- Median delta: `2351.5`
- P10 delta: `-1708.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1708.0`, p10 delta `-3451.2`, win rate `0.5`
- `bootstrap_path`: mean delta `2487.0`, p10 delta `2466.2`, win rate `1.0`
- `original_noise`: mean delta `2352.5`, p10 delta `2264.1`, win rate `1.0`

- Profile `all`: mean delta `1043.8333`, p10 delta `-1708.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1043.8333`, p10 delta `-1708.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

