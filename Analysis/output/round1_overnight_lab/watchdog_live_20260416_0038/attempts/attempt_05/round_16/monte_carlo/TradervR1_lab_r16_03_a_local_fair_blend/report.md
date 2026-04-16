# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_03_a_local_fair_blend`
- Bots: TradervR1_lab_r16_03_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_03_a_local_fair_blend

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

### TradervR1_lab_r16_03_a_local_fair_blend

- Overall samples: `6` | mean `125877.6667` | p10 `-13830.0` | cvar10 `-22766.0` | std `124266.6972`
- Profile `all`: count `6`, mean `125877.6667`, p10 `-13830.0`, cvar10 `-22766.0`
- Profile `plausible`: count `6`, mean `125877.6667`, p10 `-13830.0`, cvar10 `-22766.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53439.5`, p10 `-7524.9`, cvar10 `-22766.0`
- `bootstrap_path`: count `2`, mean `37982.5`, p10 `3681.3`, cvar10 `-4894.0`
- `original_noise`: count `2`, mean `286211.0`, p10 `285285.8`, cvar10 `285054.5`

## Comparison

- Primary: `TradervR1_lab_r16_03_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `226.25`
- Median delta: `314.75`
- P10 delta: `-1111.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-323.75`, p10 delta `-2016.35`, win rate `0.5`
- `bootstrap_path`: mean delta `251.0`, p10 delta `223.8`, win rate `1.0`
- `original_noise`: mean delta `751.5`, p10 delta `425.9`, win rate `1.0`

- Profile `all`: mean delta `226.25`, p10 delta `-1111.25`, win rate `0.8333`
- Profile `plausible`: mean delta `226.25`, p10 delta `-1111.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

