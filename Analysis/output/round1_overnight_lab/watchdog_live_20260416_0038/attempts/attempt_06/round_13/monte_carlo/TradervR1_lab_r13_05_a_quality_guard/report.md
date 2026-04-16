# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r13_05_a_quality_guard`
- Bots: TradervR1_lab_r13_05_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r13_05_a_quality_guard

- Combined total PnL: `289032.0000`
- Day -1: `95917.0000`
- Day -2: `96015.0000`
- Day 0: `97100.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r13_05_a_quality_guard

- Overall samples: `6` | mean `125231.25` | p10 `-18703.75` | cvar10 `-33884.0` | std `126525.1608`
- Profile `all`: count `6`, mean `125231.25`, p10 `-18703.75`, cvar10 `-33884.0`
- Profile `plausible`: count `6`, mean `125231.25`, p10 `-18703.75`, cvar10 `-33884.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49757.0`, p10 `-17155.8`, cvar10 `-33884.0`
- `bootstrap_path`: count `2`, mean `39145.25`, p10 `5010.25`, cvar10 `-3523.5`
- `original_noise`: count `2`, mean `286791.5`, p10 `286207.1`, cvar10 `286061.0`

## Comparison

- Primary: `TradervR1_lab_r13_05_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-420.1667`
- Median delta: `1313.25`
- P10 delta: `-4077.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4006.25`, p10 delta `-8262.05`, win rate `0.5`
- `bootstrap_path`: mean delta `1413.75`, p10 delta `1220.35`, win rate `1.0`
- `original_noise`: mean delta `1332.0`, p10 delta `1316.8`, win rate `1.0`

- Profile `all`: mean delta `-420.1667`, p10 delta `-4077.0`, win rate `0.8333`
- Profile `plausible`: mean delta `-420.1667`, p10 delta `-4077.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

