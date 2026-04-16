# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_02_a_local_fair_blend`
- Bots: TradervR1_lab_r16_02_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_02_a_local_fair_blend

- Combined total PnL: `288402.5000`
- Day -1: `95812.0000`
- Day -2: `95779.5000`
- Day 0: `96811.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_02_a_local_fair_blend

- Overall samples: `6` | mean `124829.1667` | p10 `-14962.0` | cvar10 `-25030.0` | std `124584.2484`
- Profile `all`: count `6`, mean `124829.1667`, p10 `-14962.0`, cvar10 `-25030.0`
- Profile `plausible`: count `6`, mean `124829.1667`, p10 `-14962.0`, cvar10 `-25030.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50577.5`, p10 `-9908.5`, cvar10 `-25030.0`
- `bootstrap_path`: count `2`, mean `37982.5`, p10 `3681.3`, cvar10 `-4894.0`
- `original_noise`: count `2`, mean `285927.5`, p10 `285367.5`, cvar10 `285227.5`

## Comparison

- Primary: `TradervR1_lab_r16_02_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-822.25`
- Median delta: `251.0`
- P10 delta: `-3185.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-3185.75`, p10 delta `-5356.75`, win rate `0.0`
- `bootstrap_path`: mean delta `251.0`, p10 delta `223.8`, win rate `1.0`
- `original_noise`: mean delta `468.0`, p10 delta `428.4`, win rate `1.0`

- Profile `all`: mean delta `-822.25`, p10 delta `-3185.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-822.25`, p10 delta `-3185.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

