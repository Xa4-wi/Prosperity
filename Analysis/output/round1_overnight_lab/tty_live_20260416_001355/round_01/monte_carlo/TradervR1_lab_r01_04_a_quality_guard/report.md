# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r01_04_a_quality_guard`
- Bots: TradervR1_lab_r01_04_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r01_04_a_quality_guard

- Combined total PnL: `288075.0000`
- Day -1: `95581.0000`
- Day -2: `95750.0000`
- Day 0: `96744.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r01_04_a_quality_guard

- Overall samples: `6` | mean `124988.75` | p10 `-18102.5` | cvar10 `-31734.0` | std `125946.5006`
- Profile `all`: count `6`, mean `124988.75`, p10 `-18102.5`, cvar10 `-31734.0`
- Profile `plausible`: count `6`, mean `124988.75`, p10 `-18102.5`, cvar10 `-31734.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50453.25`, p10 `-15296.55`, cvar10 `-31734.0`
- `bootstrap_path`: count `2`, mean `38449.5`, p10 `4113.1`, cvar10 `-4471.0`
- `original_noise`: count `2`, mean `286063.5`, p10 `285266.7`, cvar10 `285067.5`

## Comparison

- Primary: `TradervR1_lab_r01_04_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-662.6667`
- Median delta: `632.0`
- P10 delta: `-3409.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3310.0`, p10 delta `-6402.8`, win rate `0.5`
- `bootstrap_path`: mean delta `718.0`, p10 delta `710.0`, win rate `1.0`
- `original_noise`: mean delta `604.0`, p10 delta `406.8`, win rate `1.0`

- Profile `all`: mean delta `-662.6667`, p10 delta `-3409.25`, win rate `0.8333`
- Profile `plausible`: mean delta `-662.6667`, p10 delta `-3409.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

