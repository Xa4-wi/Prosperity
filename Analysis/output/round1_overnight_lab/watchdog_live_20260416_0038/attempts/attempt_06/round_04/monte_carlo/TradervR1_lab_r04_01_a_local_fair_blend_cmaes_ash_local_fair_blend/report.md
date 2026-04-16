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

- Combined total PnL: `291614.5000`
- Day -1: `96913.0000`
- Day -2: `96966.5000`
- Day 0: `97735.0000`

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

- Overall samples: `6` | mean `130271.8333` | p10 `-11466.25` | cvar10 `-23232.0` | std `124672.9762`
- Profile `all`: count `6`, mean `130271.8333`, p10 `-11466.25`, cvar10 `-23232.0`
- Profile `plausible`: count `6`, mean `130271.8333`, p10 `-11466.25`, cvar10 `-23232.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `58067.0`, p10 `-6972.2`, cvar10 `-23232.0`
- `bootstrap_path`: count `2`, mean `43163.25`, p10 `8872.25`, cvar10 `299.5`
- `original_noise`: count `2`, mean `289585.25`, p10 `288778.65`, cvar10 `288577.0`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4620.4167`
- Median delta: `4884.75`
- P10 delta: `2596.5`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `4303.75`, p10 delta `1921.55`, win rate `1.0`
- `bootstrap_path`: mean delta `5431.75`, p10 delta `5394.35`, win rate `1.0`
- `original_noise`: mean delta `4125.75`, p10 delta `3918.75`, win rate `1.0`

- Profile `all`: mean delta `4620.4167`, p10 delta `2596.5`, win rate `1.0`
- Profile `plausible`: mean delta `4620.4167`, p10 delta `2596.5`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

