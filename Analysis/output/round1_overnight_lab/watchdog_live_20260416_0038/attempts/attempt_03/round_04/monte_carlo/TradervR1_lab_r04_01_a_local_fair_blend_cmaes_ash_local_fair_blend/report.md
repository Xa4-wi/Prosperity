# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend`
- Bots: TradervR1_lab_r04_01_a_local_fair_blend_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_01_a_local_fair_blend_best

- Combined total PnL: `291845.0000`
- Day -1: `96977.0000`
- Day -2: `97104.0000`
- Day 0: `97764.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_01_a_local_fair_blend_best

- Overall samples: `6` | mean `129890.0833` | p10 `-9536.0` | cvar10 `-19406.0` | std `124067.4675`
- Profile `all`: count `6`, mean `129890.0833`, p10 `-9536.0`, cvar10 `-19406.0`
- Profile `plausible`: count `6`, mean `129890.0833`, p10 `-9536.0`, cvar10 `-19406.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56632.5`, p10 `-4198.3`, cvar10 `-19406.0`
- `bootstrap_path`: count `2`, mean `42972.0`, p10 `8861.6`, cvar10 `334.0`
- `original_noise`: count `2`, mean `290065.75`, p10 `289403.15`, cvar10 `289237.5`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4238.6667`
- Median delta: `4826.5`
- P10 delta: `2557.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `2869.25`, p10 delta `1043.05`, win rate `1.0`
- `bootstrap_path`: mean delta `5240.5`, p10 delta `5022.5`, win rate `1.0`
- `original_noise`: mean delta `4606.25`, p10 delta `4543.25`, win rate `1.0`

- Profile `all`: mean delta `4238.6667`, p10 delta `2557.0`, win rate `1.0`
- Profile `plausible`: mean delta `4238.6667`, p10 delta `2557.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

