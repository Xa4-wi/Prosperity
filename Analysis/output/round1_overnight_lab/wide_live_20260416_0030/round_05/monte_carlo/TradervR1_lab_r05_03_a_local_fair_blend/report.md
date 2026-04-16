# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r05_03_a_local_fair_blend`
- Bots: TradervR1_lab_r05_03_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r05_03_a_local_fair_blend

- Combined total PnL: `291861.5000`
- Day -1: `96894.0000`
- Day -2: `97098.5000`
- Day 0: `97869.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r05_03_a_local_fair_blend

- Overall samples: `6` | mean `130170.1667` | p10 `-9229.75` | cvar10 `-19457.0` | std `123819.3022`
- Profile `all`: count `6`, mean `130170.1667`, p10 `-9229.75`, cvar10 `-19457.0`
- Profile `plausible`: count `6`, mean `130170.1667`, p10 `-9229.75`, cvar10 `-19457.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `57340.75`, p10 `-4097.45`, cvar10 `-19457.0`
- `bootstrap_path`: count `2`, mean `43420.25`, p10 `9482.05`, cvar10 `997.5`
- `original_noise`: count `2`, mean `289749.5`, p10 `289016.7`, cvar10 `288833.5`

## Comparison

- Primary: `TradervR1_lab_r05_03_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `4518.75`
- Median delta: `4778.75`
- P10 delta: `3088.75`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `3577.5`, p10 delta `2358.7`, win rate `1.0`
- `bootstrap_path`: mean delta `5688.75`, p10 delta `5298.55`, win rate `1.0`
- `original_noise`: mean delta `4290.0`, p10 delta `4156.8`, win rate `1.0`

- Profile `all`: mean delta `4518.75`, p10 delta `3088.75`, win rate `1.0`
- Profile `plausible`: mean delta `4518.75`, p10 delta `3088.75`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

