# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_05_a_quality_guard`
- Bots: TradervR1_lab_r08_05_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_05_a_quality_guard

- Combined total PnL: `290556.0000`
- Day -1: `96418.0000`
- Day -2: `96540.0000`
- Day 0: `97598.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_05_a_quality_guard

- Overall samples: `6` | mean `128677.5833` | p10 `-9115.25` | cvar10 `-16288.0` | std `123200.9213`
- Profile `all`: count `6`, mean `128677.5833`, p10 `-9115.25`, cvar10 `-16288.0`
- Profile `plausible`: count `6`, mean `128677.5833`, p10 `-9115.25`, cvar10 `-16288.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56940.0`, p10 `-1642.4`, cvar10 `-16288.0`
- `bootstrap_path`: count `2`, mean `40801.25`, p10 `6606.25`, cvar10 `-1942.5`
- `original_noise`: count `2`, mean `288291.5`, p10 `287532.7`, cvar10 `287343.0`

## Comparison

- Primary: `TradervR1_lab_r08_05_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `3026.1667`
- Median delta: `2967.0`
- P10 delta: `358.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `3176.75`, p10 delta `-897.85`, win rate `0.5`
- `bootstrap_path`: mean delta `3069.75`, p10 delta `2936.35`, win rate `1.0`
- `original_noise`: mean delta `2832.0`, p10 delta `2672.8`, win rate `1.0`

- Profile `all`: mean delta `3026.1667`, p10 delta `358.25`, win rate `0.8333`
- Profile `plausible`: mean delta `3026.1667`, p10 delta `358.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

