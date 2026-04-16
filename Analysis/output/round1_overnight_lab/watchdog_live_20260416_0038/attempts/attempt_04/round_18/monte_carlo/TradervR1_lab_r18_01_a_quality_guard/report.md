# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_01_a_quality_guard`
- Bots: TradervR1_lab_r18_01_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_01_a_quality_guard

- Combined total PnL: `287548.0000`
- Day -1: `95532.0000`
- Day -2: `95499.0000`
- Day 0: `96517.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_01_a_quality_guard

- Overall samples: `6` | mean `124684.8333` | p10 `-16709.75` | cvar10 `-28580.0` | std `125153.3857`
- Profile `all`: count `6`, mean `124684.8333`, p10 `-16709.75`, cvar10 `-28580.0`
- Profile `plausible`: count `6`, mean `124684.8333`, p10 `-16709.75`, cvar10 `-28580.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50502.75`, p10 `-12763.45`, cvar10 `-28580.0`
- `bootstrap_path`: count `2`, mean `37987.75`, p10 `3725.95`, cvar10 `-4839.5`
- `original_noise`: count `2`, mean `285564.0`, p10 `285068.8`, cvar10 `284945.0`

## Comparison

- Primary: `TradervR1_lab_r18_01_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-966.5833`
- Median delta: `73.5`
- P10 delta: `-3260.5`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-3260.5`, p10 delta `-3869.7`, win rate `0.0`
- `bootstrap_path`: mean delta `256.25`, p10 delta `189.65`, win rate `1.0`
- `original_noise`: mean delta `104.5`, p10 delta `0.1`, win rate `0.5`

- Profile `all`: mean delta `-966.5833`, p10 delta `-3260.5`, win rate `0.5`
- Profile `plausible`: mean delta `-966.5833`, p10 delta `-3260.5`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

