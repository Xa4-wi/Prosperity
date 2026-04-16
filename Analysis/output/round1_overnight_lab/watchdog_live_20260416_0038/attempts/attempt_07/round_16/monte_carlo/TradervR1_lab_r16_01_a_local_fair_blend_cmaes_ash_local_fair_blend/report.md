# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_01_a_local_fair_blend_cmaes_ash_local_fair_blend`
- Bots: TradervR1_lab_r16_01_a_local_fair_blend_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_01_a_local_fair_blend_best

- Combined total PnL: `290020.0000`
- Day -1: `96221.0000`
- Day -2: `96404.0000`
- Day 0: `97395.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_01_a_local_fair_blend_best

- Overall samples: `6` | mean `128573.25` | p10 `-11370.25` | cvar10 `-21052.0` | std `124047.7416`
- Profile `all`: count `6`, mean `128573.25`, p10 `-11370.25`, cvar10 `-21052.0`
- Profile `plausible`: count `6`, mean `128573.25`, p10 `-11370.25`, cvar10 `-21052.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56511.75`, p10 `-5539.25`, cvar10 `-21052.0`
- `bootstrap_path`: count `2`, mean `41050.25`, p10 `6859.25`, cvar10 `-1688.5`
- `original_noise`: count `2`, mean `288157.75`, p10 `287625.55`, cvar10 `287492.5`

## Comparison

- Primary: `TradervR1_lab_r16_01_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2921.8333`
- Median delta: `2964.75`
- P10 delta: `2302.5`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `2748.5`, p10 delta `2142.5`, win rate `1.0`
- `bootstrap_path`: mean delta `3318.75`, p10 delta `3181.35`, win rate `1.0`
- `original_noise`: mean delta `2698.25`, p10 delta `2630.85`, win rate `1.0`

- Profile `all`: mean delta `2921.8333`, p10 delta `2302.5`, win rate `1.0`
- Profile `plausible`: mean delta `2921.8333`, p10 delta `2302.5`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

